#!/usr/bin/env python3
"""핵심 용어 사전집 xlsx ← entities.yaml · ontology.yaml 동기화 (문서 산출물 도구).

정본은 `src/semantic/entities.yaml`(용어)·`src/semantic/ontology.yaml`(관계 유형)이며, 이 스크립트는
승인자 열람용 사전집 `data/raw/비정형 분석용_핵심 용어 사전집_v1.0.xlsx`를 정본에 맞춰 갱신한다.
- 용어사전: 기존 용어는 YAML 기반 셀만 값이 다를 때 덮어쓰고(셀 단위 로그), xlsx 전용 열
  (대분류_EN·중분류_EN·소분류·엔터티유형)은 비어 있을 때만 채운다. 신규 용어는 2행 서식을 복사해 추가.
- 분류체계·관계사전·출처·코드목록: 누락 행만 추가(기존 행 무변경).
- 요약: 버전 v1.1·기준일·수식 범위($500)·시장구조·기업 집계 행 보강. 병합 범위는 건드리지 않음.
- 멱등: 2회차 실행은 변경 0건. `--check`는 변경이 있으면 종료코드 1(CI 게이트용).

openpyxl 사용 근거: 파이프라인이 아닌 열람용 문서 산출물(scripts/build_weekly_wbs.py와 동일 허용).
"""
from __future__ import annotations

import argparse
import copy
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import openpyxl
import yaml
from openpyxl.cell.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_XLSX = ROOT / "data" / "raw" / "비정형 분석용_핵심 용어 사전집_v1.0.xlsx"
DEFAULT_ENTITIES = ROOT / "src" / "semantic" / "entities.yaml"
DEFAULT_ONTOLOGY = ROOT / "src" / "semantic" / "ontology.yaml"

SHEET_TERMS = "용어사전"
SHEET_SUMMARY = "요약"
SHEET_TAXONOMY = "분류체계"
SHEET_RELATIONS = "관계사전"
SHEET_SOURCES = "출처"
SHEET_CODES = "코드목록"

SUMMARY_VERSION_OLD = "v1.0"
SUMMARY_VERSION_NEW = "v1.1"
SUMMARY_DATE = "2026-09-13"
TERM_RANGE_END = 500  # 요약 수식의 행 상한 — 용어 증가에 대비한 여유

SYNONYM_SEP = "; "
LIST_SEP = ","

# 용어사전 열 배치 (A:V) — 사전집 v1.0 헤더 순서 고정
COL = {
    "term_id": "A", "category": "B", "category_en": "C", "subcategory": "D",
    "subcategory_en": "E", "subclass": "F", "canonical": "G", "canonical_ko": "H",
    "abbr": "I", "synonyms": "J", "entity_type": "K", "definition": "L",
    "interpretation_rules": "M", "impact_target": "N", "price_direction": "O",
    "unit_range": "P", "alert_criteria": "Q", "priority": "R", "ambiguity_risk": "S",
    "class": "T", "relations": "U", "source_code": "V",
}
# YAML 값이 정본인 열(값이 다르면 덮어씀)
YAML_BACKED = (
    "category", "subcategory", "canonical", "canonical_ko", "abbr", "synonyms",
    "definition", "interpretation_rules", "impact_target", "price_direction",
    "unit_range", "alert_criteria", "priority", "ambiguity_risk", "class",
    "relations", "source_code",
)
# xlsx 전용 열(비어 있을 때만 채움)
XLSX_ONLY = ("category_en", "subcategory_en", "subclass", "entity_type")

CATEGORY_EN: dict[str, str] = {
    "경제·무역": "Economy & Trade",
    "농업·농기상": "Agriculture & Agrometeorology",
    "시장·가격·조달": "Market, Price & Procurement",
    "에너지·바이오연료": "Energy & Biofuel",
    "지정학·안보": "Geopolitics & Security",
    "물류·공급망": "Logistics & Supply Chain",
    "외교·정책·규제": "Diplomacy, Policy & Regulation",
    "데이터·시맨틱·품질": "Data, Semantics & Quality",
    "시장구조·기업": "Market Structure & Firms",
}
# 신규 (대분류, 중분류) → 중분류_EN. 기존 시트의 쌍은 실행 시 시트에서 먼저 읽어 우선한다.
SUBCATEGORY_EN: dict[tuple[str, str], str] = {
    ("시장구조·기업", "트레이딩하우스"): "Trading Houses",
    ("시장구조·기업", "국내 압착·정제"): "Domestic Crushing & Refining",
    ("시장구조·기업", "수입 양하 항만"): "Import Discharge Ports",
    ("시장구조·기업", "해상 병목"): "Maritime Chokepoints",
    ("시장구조·기업", "집중도"): "Concentration Metrics",
    ("시장구조·기업", "집중도 지표"): "Concentration Metrics",
    ("시장구조·기업", "거래 관행"): "Trading Conventions",
    ("데이터·시맨틱·품질", "매체·수집 채널"): "Media & Collection Channels",
    ("농업·농기상", "생산지역"): "Production Regions",
}
# 신규 온톨로지 클래스 → 엔터티유형. 기존 시트의 class→K 쌍은 실행 시 먼저 읽어 우선한다.
CLASS_TO_ENTITY_TYPE: dict[str, str] = {
    "TradingHouse": "Organization",
    "Processor": "Organization",
    "Port": "Port",
    "Chokepoint": "Chokepoint",
    "ConcentrationMetric": "Metric",
    "ContractStandard": "Standard",
    "PricingConvention": "Concept",
    "PriceBenchmark": "Indicator",
    "MediaSource": "DataSource",
    "ProductionRegion": "Region",
    "CollectionChannel": "DataSource",
}

TAXONOMY_NEW_ROW = (
    "시장구조·기업",
    CATEGORY_EN["시장구조·기업"],
    "트레이딩하우스·국내 압착·정제·수입 양하 항만·해상 병목·집중도·거래 관행",
    "기업 실체는 여기, 운임·항로 지표는 물류·공급망",
)

# 출처코드 레지스트리: 토큰 → (유형, 제목, 연도, 반영 범위, URL)
_REF = "docs/research_desk/references"
SOURCE_REGISTRY: dict[str, tuple[str, str, str, str, str]] = {
    "Adaptation_2025_traders_geopolitics.pdf": (
        "저장소 원문 PDF",
        "Adaptation of grain traders to geopolitical shocks (Tatarenko & Nabok, 2025)",
        "2025", "트레이더 지정학 적응·하이브리드 가격 공식·흑해 회랑 정량 (CE-013·CE-014 evidence)",
        f"저장소 경로: {_REF}/Adaptation_2025_grain_traders_geopolitical_shocks.pdf"),
    "China_2023_financialized_soybeans_food_regime.pdf": (
        "저장소 원문 PDF",
        "Financialized soybeans and the food regime (Fares, J. Agrarian Change 2023)",
        "2023", "COFCO 금융화·해외 압착 — 중국 구매 신호의 국가·상업 채널 분리 규율",
        f"저장소 경로: {_REF}/China_2023_financialized_soybeans_food_regime.pdf"),
    "Dynamics_2025_AEPP_grain_oilseed_trading_concentration.pdf": (
        "저장소 원문 PDF",
        "Dynamics of grain & oilseed trading concentration (Wilson·Bullock·Dubovoy, AEPP 2025)",
        "2025", "선적 실거래 CR4/HHI 집중도 실측 — 'ABCD 70~90%' 통설 교정·COFCO CNF 1위",
        f"저장소 경로: {_REF}/Dynamics_2025_AEPP_grain_oilseed_trading_concentration.pdf"),
    "MEMORY_A-211": (
        "MEMORY", "MEMORY A-211 — 6차분 통합(VAL 베트남 합작·중국 순수출·한국 압착 원문)",
        "2026", "베트남 채널 승격 근거·중국 정제유 공급 여력·국내 압착 원산지 다변화",
        "저장소 경로: docs/memory_archive/2026-08.md (A-211)"),
    "Ukraine_grain_seed_trade_global_position.pdf": (
        "저장소 원문 PDF",
        "Ukraine grain & oilseed trade global position (Panfilova 외, Scientific Horizons 2025)",
        "2025", "해바라기 취약점=압착+물류(설비 피해·운송비) — CE-013·CE-014 물량·비용 축",
        f"저장소 경로: {_REF}/Ukraine_grain_seed_trade_global_position.pdf"),
    "abcd_trading_structure_2026_08_15.md": (
        "저장소 문서", "ABCD·COFCO·Wilmar 거래구조 조사 (2026-08-15)",
        "2026", "상하류 수직통합·FOSFA/basis 거래 관행·한국 압착·정제 구조·관세청 채널 프로파일",
        "저장소 경로: docs/research_desk/2026-08/abcd_trading_structure_2026_08_15.md"),
    "market_structure_errata_2026_08_19.md": (
        "저장소 문서", "시장구조 브리프 정오표 (2026-08-19)",
        "2026", "Deep Research 교차검증 정오표 — 원자료 재확인 항목·확인 항목",
        "저장소 경로: docs/research_desk/2026-08/market_structure_errata_2026_08_19.md"),
    "ontology_supply_chain_v3.1": (
        "저장소 문서", "ontology.yaml supply_chain 절 (v3.1)",
        "2026", "트레이딩하우스·항만·한국향 루트 리드타임·OPERATED_BY·TRANSITS 관계",
        "저장소 경로: src/semantic/ontology.yaml (supply_chain)"),
    "GH-DIGEST": (
        "저장소 스크립트", "일별 비정형 다이제스트 (scripts/daily_unstructured_digest.py)",
        "2026", "Perplexity 실시간 프록시 7분류·RSS 전문 매체 수집·온톨로지 후보 큐",
        "저장소 경로: scripts/daily_unstructured_digest.py"),
    "media_source_fallback_design_2026_09_13.md": (
        "저장소 문서", "매체 소스 폴백 설계 (2026-09-13)",
        "2026", "매체·수집 채널 엔터티 — 소스 폴백 순서·수집 채널 정의",
        "저장소 경로: docs/research_desk/2026-09/media_source_fallback_design_2026_09_13.md"),
}
SOURCE_UNKNOWN_TYPE = "미등록"

STATUS_CODE_ROWS: tuple[tuple[str, str, str, str], ...] = (
    ("Status", "active", "원 사전집(v1.0) 등재 용어 — 활성 사용", "entities.yaml.status"),
    ("Status", "confirmed", "저장소 문서·원문으로 확인된 신규 용어(승인 완료)", "entities.yaml.status"),
    ("Status", "inference", "추론 기반 신규 용어 — 원문 확인 전(INFERENCE 라벨)", "entities.yaml.status"),
)


@dataclass
class SyncStats:
    """시트별 변경 집계 — 요약 줄과 `--check` 판정에 사용."""

    terms_added: int = 0
    cells_updated: int = 0
    relations_added: int = 0
    sources_added: int = 0
    taxonomy_added: int = 0
    codes_added: int = 0
    summary_changes: int = 0
    log: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return (self.terms_added + self.cells_updated + self.relations_added
                + self.sources_added + self.taxonomy_added + self.codes_added
                + self.summary_changes)

    def summary_line(self, path: Path) -> str:
        return (f"[완료] 용어 +{self.terms_added}·갱신 셀 {self.cells_updated}"
                f"·관계 +{self.relations_added}·출처 +{self.sources_added}"
                f"·분류 +{self.taxonomy_added}·코드 +{self.codes_added} → {path}")


# ── YAML 로드 ─────────────────────────────────────────────────────────────────────

def load_terms(entities_path: Path) -> list[dict[str, Any]]:
    """entities.yaml의 최상위 리스트 전부에서 term_id를 가진 레코드를 평탄화한다."""
    data = yaml.safe_load(entities_path.read_text(encoding="utf-8")) or {}
    terms: list[dict[str, Any]] = []
    seen: set[str] = set()
    for key, value in data.items():
        if not isinstance(value, list):
            continue
        for rec in value:
            if not isinstance(rec, dict) or "term_id" not in rec:
                continue
            tid = str(rec["term_id"])
            if tid in seen:
                print(f"[경고] entities.yaml 중복 term_id {tid} (섹션 {key}) — 첫 레코드 유지")
                continue
            seen.add(tid)
            terms.append(rec)
    if not terms:
        raise SystemExit(f"[오류] entities.yaml에서 term_id 레코드를 찾지 못함: {entities_path}")
    return terms


def load_relation_types(ontology_path: Path) -> list[dict[str, Any]]:
    """ontology.yaml relation_types 리스트(code/definition/domain/range/symmetric/…)."""
    data = yaml.safe_load(ontology_path.read_text(encoding="utf-8")) or {}
    rel = data.get("relation_types") or []
    if isinstance(rel, dict):  # 방어: code→dict 형식이면 리스트로 변환
        rel = [{"code": k, **(v or {})} for k, v in rel.items()]
    out = [r for r in rel if isinstance(r, dict) and r.get("code")]
    if not out:
        raise SystemExit(f"[오류] ontology.yaml relation_types 없음: {ontology_path}")
    return out


# ── 값 정규화 ───────────────────────────────────────────────────────────────────────

def _norm(value: Any) -> str | None:
    """비교용 정규화 — 빈 문자열·None은 동일하게 None, 그 외는 공백 제거 문자열."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _join_list(value: Any, sep: str) -> str | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return sep.join(str(v).strip() for v in value if _norm(v)) or None
    return _norm(value)


def term_to_row_values(rec: dict[str, Any]) -> dict[str, str | None]:
    """YAML 레코드 → YAML 기반 열 값(빈 값은 None)."""
    rules = _norm(rec.get("interpretation_rules"))
    note = _norm(rec.get("measurement_note"))
    if note:
        rules = f"{rules} ⋅ 측정 주석: {note}" if rules else f"측정 주석: {note}"
    return {
        "category": _norm(rec.get("category")),
        "subcategory": _norm(rec.get("subcategory")),
        "canonical": _norm(rec.get("canonical")),
        "canonical_ko": _norm(rec.get("canonical_ko")),
        "abbr": _norm(rec.get("abbr")),
        "synonyms": _join_list(rec.get("synonyms"), SYNONYM_SEP),
        "definition": _norm(rec.get("definition")),
        "interpretation_rules": rules,
        "impact_target": _norm(rec.get("impact_target")),
        "price_direction": _norm(rec.get("price_direction")),
        "unit_range": _norm(rec.get("unit_range")),
        "alert_criteria": _norm(rec.get("alert_criteria")),
        "priority": _norm(rec.get("priority")),
        "ambiguity_risk": _norm(rec.get("ambiguity_risk")),
        "class": _norm(rec.get("class")),
        "relations": _join_list(rec.get("relations"), LIST_SEP),
        "source_code": _join_list(rec.get("source_code"), LIST_SEP),
    }


def source_tokens(terms: list[dict[str, Any]]) -> list[str]:
    """전 용어의 source_code를 쉼표 분리해 등장 순서대로 고유 토큰 목록으로 만든다."""
    seen: dict[str, None] = {}
    for rec in terms:
        joined = _join_list(rec.get("source_code"), LIST_SEP) or ""
        for tok in joined.split(LIST_SEP):
            tok = tok.strip()
            if tok:
                seen.setdefault(tok, None)
    return list(seen)


# ── 셀 서식 ─────────────────────────────────────────────────────────────────────────

def _copy_style(src: Cell, dst: Cell) -> None:
    dst.font = copy.copy(src.font)
    dst.alignment = copy.copy(src.alignment)
    dst.border = copy.copy(src.border)
    dst.fill = copy.copy(src.fill)
    dst.number_format = src.number_format


def _append_styled_row(ws: Worksheet, values: list[Any], style_row: int = 2) -> int:
    """마지막 행 다음에 값을 쓰고 style_row 서식을 열별로 복사한다. 새 행 번호 반환."""
    row = _last_data_row(ws) + 1
    for idx, value in enumerate(values, start=1):
        cell = ws.cell(row=row, column=idx, value=value)
        _copy_style(ws.cell(row=style_row, column=idx), cell)
    if ws.row_dimensions[style_row].height:
        ws.row_dimensions[row].height = ws.row_dimensions[style_row].height
    return row


def _last_data_row(ws: Worksheet) -> int:
    """A열 기준 마지막 비어 있지 않은 행(ws.max_row는 서식만 있는 행도 세므로 사용 금지)."""
    for row in range(ws.max_row, 0, -1):
        if _norm(ws.cell(row=row, column=1).value) is not None:
            return row
    return 1


def _col_idx(key: str) -> int:
    return openpyxl.utils.column_index_from_string(COL[key])


# ── 용어사전 ─────────────────────────────────────────────────────────────────────────

def _seed_subcategory_en(ws: Worksheet) -> dict[tuple[str, str], str]:
    seed = dict(SUBCATEGORY_EN)
    for row in range(2, _last_data_row(ws) + 1):
        cat = _norm(ws.cell(row=row, column=_col_idx("category")).value)
        sub = _norm(ws.cell(row=row, column=_col_idx("subcategory")).value)
        en = _norm(ws.cell(row=row, column=_col_idx("subcategory_en")).value)
        if cat and sub and en:
            seed[(cat, sub)] = en  # 시트 기존 값 우선
    return seed


def _seed_entity_type(ws: Worksheet) -> dict[str, str]:
    seed = dict(CLASS_TO_ENTITY_TYPE)
    for row in range(2, _last_data_row(ws) + 1):
        cls = _norm(ws.cell(row=row, column=_col_idx("class")).value)
        et = _norm(ws.cell(row=row, column=_col_idx("entity_type")).value)
        if cls and et and cls not in seed:
            seed[cls] = et  # 클래스당 첫 등장 값 채택
    return seed


def _xlsx_only_defaults(rec: dict[str, Any], values: dict[str, str | None],
                        sub_en: dict[tuple[str, str], str],
                        ent_type: dict[str, str]) -> dict[str, str | None]:
    cat, sub, cls = values["category"], values["subcategory"], values["class"]
    sub_key = (cat or "", sub or "")
    if sub and sub_key not in sub_en:
        print(f"[경고] 중분류_EN 미정의 {sub_key} — 빈 칸 유지 (SUBCATEGORY_EN 보강 필요)")
    return {
        "category_en": CATEGORY_EN.get(cat or ""),
        "subcategory_en": sub_en.get(sub_key),
        "subclass": sub,
        "entity_type": ent_type.get(cls or "", cls),
    }


def sync_terms(ws: Worksheet, terms: list[dict[str, Any]], stats: SyncStats) -> None:
    sub_en = _seed_subcategory_en(ws)
    ent_type = _seed_entity_type(ws)
    index: dict[str, int] = {}
    for row in range(2, _last_data_row(ws) + 1):
        tid = _norm(ws.cell(row=row, column=1).value)
        if tid:
            index[tid] = row

    for rec in terms:
        tid = str(rec["term_id"])
        values = term_to_row_values(rec)
        defaults = _xlsx_only_defaults(rec, values, sub_en, ent_type)
        row = index.get(tid)
        if row is None:
            row_vals: list[Any] = [tid]
            for key in list(COL)[1:]:
                row_vals.append(values.get(key) if key in values else defaults.get(key))
            _append_styled_row(ws, row_vals)
            stats.terms_added += 1
            stats.log.append(f"{tid} 신규 행 추가 ({values['canonical']})")
            continue
        for key in YAML_BACKED:
            cell = ws.cell(row=row, column=_col_idx(key))
            if _norm(cell.value) != values[key]:
                stats.log.append(f"{tid} {COL[key]}: {cell.value!r} → {values[key]!r}")
                cell.value = values[key]
                stats.cells_updated += 1
        for key in XLSX_ONLY:
            cell = ws.cell(row=row, column=_col_idx(key))
            if _norm(cell.value) is None and defaults.get(key):
                stats.log.append(f"{tid} {COL[key]}: (빈 칸) → {defaults[key]!r}")
                cell.value = defaults[key]
                stats.cells_updated += 1


# ── 분류체계 · 관계사전 · 출처 · 코드목록 ─────────────────────────────────────────────

def _col_a_values(ws: Worksheet) -> set[str]:
    return {v for row in range(2, _last_data_row(ws) + 1)
            if (v := _norm(ws.cell(row=row, column=1).value))}


def sync_taxonomy(ws: Worksheet, stats: SyncStats) -> None:
    if TAXONOMY_NEW_ROW[0] not in _col_a_values(ws):
        _append_styled_row(ws, list(TAXONOMY_NEW_ROW))
        stats.taxonomy_added += 1
        stats.log.append(f"분류체계 추가: {TAXONOMY_NEW_ROW[0]}")


def sync_relations(ws: Worksheet, relations: list[dict[str, Any]], stats: SyncStats) -> None:
    existing = _col_a_values(ws)
    for rel in relations:
        code = str(rel["code"])
        if code in existing:
            continue
        _append_styled_row(ws, [
            code, _norm(rel.get("definition")), _norm(rel.get("domain")),
            _norm(rel.get("range")), "Y" if rel.get("symmetric") else "N",
            _norm(rel.get("constraints_example")),
        ])
        existing.add(code)
        stats.relations_added += 1
        stats.log.append(f"관계사전 추가: {code}")


def sync_sources(ws: Worksheet, tokens: list[str], stats: SyncStats) -> None:
    existing = _col_a_values(ws)
    for tok in tokens:
        if tok in existing:
            continue
        entry = SOURCE_REGISTRY.get(tok)
        if entry is None:
            print(f"[경고] 출처코드 미등록 {tok!r} — 스텁 행 추가(유형 {SOURCE_UNKNOWN_TYPE})")
            year = _year_from_token(tok)
            entry = (SOURCE_UNKNOWN_TYPE, tok, year, "", "")
        _append_styled_row(ws, [tok, *entry])
        existing.add(tok)
        stats.sources_added += 1
        stats.log.append(f"출처 추가: {tok}")


def _year_from_token(tok: str) -> str:
    m = re.search(r"(20\d{2})", tok)
    return m.group(1) if m else "2026"


def sync_codes(ws: Worksheet, stats: SyncStats) -> None:
    existing = {(_norm(ws.cell(row=r, column=1).value), _norm(ws.cell(row=r, column=2).value))
                for r in range(2, _last_data_row(ws) + 1)}
    for row_vals in STATUS_CODE_ROWS:
        if (row_vals[0], row_vals[1]) in existing:
            continue
        _append_styled_row(ws, list(row_vals))
        stats.codes_added += 1
        stats.log.append(f"코드목록 추가: {row_vals[0]}/{row_vals[1]}")


# ── 요약 ────────────────────────────────────────────────────────────────────────────

def _set_if_changed(ws: Worksheet, coord: str, new: Any, stats: SyncStats) -> None:
    cell = ws[coord]
    if _norm(cell.value) != _norm(new):
        stats.log.append(f"요약 {coord}: {cell.value!r} → {new!r}")
        cell.value = new
        stats.summary_changes += 1


def sync_summary(ws: Worksheet, stats: SyncStats) -> None:
    title = str(ws["A1"].value or "")
    if SUMMARY_VERSION_OLD in title:
        _set_if_changed(ws, "A1", title.replace(SUMMARY_VERSION_OLD, SUMMARY_VERSION_NEW), stats)
    subtitle = str(ws["A3"].value or "")
    if re.search(r"\d{4}-\d{2}-\d{2}", subtitle):
        _set_if_changed(ws, "A3", re.sub(r"\d{4}-\d{2}-\d{2}", SUMMARY_DATE, subtitle), stats)
    end = TERM_RANGE_END
    _set_if_changed(ws, "B6", f"=COUNTA({SHEET_TERMS}!$A$2:$A${end})", stats)
    _set_if_changed(ws, "B7", f"=COUNTA({SHEET_TAXONOMY}!$A$2:$A${end})", stats)
    for coord in ("B8", "B9"):
        cur = str(ws[coord].value or "")
        if "$153" in cur:
            _set_if_changed(ws, coord, cur.replace("$153", f"${end}"), stats)
    # 대분류별 용어 수 표에 시장구조·기업 행 보강 (D13/E13 서식 복사)
    if _norm(ws["D14"].value) is None:
        _copy_style(ws["D13"], ws["D14"])
        _copy_style(ws["E13"], ws["E14"])
    _set_if_changed(ws, "D14", TAXONOMY_NEW_ROW[0], stats)
    _set_if_changed(ws, "E14", f"=COUNTIF({SHEET_TERMS}!$B$2:$B${end},D14)", stats)


# ── 진입점 ───────────────────────────────────────────────────────────────────────────

def run_sync(xlsx: Path, entities: Path, ontology: Path, *, save: bool) -> SyncStats:
    """전 시트 동기화 실행. save=False면 메모리에서만 변경을 계산한다."""
    for p in (xlsx, entities, ontology):
        if not p.exists():
            raise SystemExit(f"[오류] 입력 파일 없음: {p}")
    terms = load_terms(entities)
    relations = load_relation_types(ontology)
    wb = openpyxl.load_workbook(xlsx)
    missing = [s for s in (SHEET_TERMS, SHEET_SUMMARY, SHEET_TAXONOMY, SHEET_RELATIONS,
                           SHEET_SOURCES, SHEET_CODES) if s not in wb.sheetnames]
    if missing:
        raise SystemExit(f"[오류] 사전집 시트 누락: {missing}")
    stats = SyncStats()
    print(f"[정보] YAML 용어 {len(terms)}건 · 관계 유형 {len(relations)}건 로드")
    sync_terms(wb[SHEET_TERMS], terms, stats)
    sync_taxonomy(wb[SHEET_TAXONOMY], stats)
    sync_relations(wb[SHEET_RELATIONS], relations, stats)
    sync_sources(wb[SHEET_SOURCES], source_tokens(terms), stats)
    sync_codes(wb[SHEET_CODES], stats)
    sync_summary(wb[SHEET_SUMMARY], stats)
    for line in stats.log:
        print(f"[정보] {line}")
    if save and stats.total:
        wb.save(xlsx)
    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="용어 사전집 xlsx ← entities/ontology yaml 동기화")
    parser.add_argument("--xlsx", type=Path, default=DEFAULT_XLSX)
    parser.add_argument("--entities", type=Path, default=DEFAULT_ENTITIES)
    parser.add_argument("--ontology", type=Path, default=DEFAULT_ONTOLOGY)
    parser.add_argument("--dry-run", action="store_true", help="변경 계산만, 저장 안 함")
    parser.add_argument("--check", action="store_true",
                        help="변경이 하나라도 있으면 종료코드 1 (저장 안 함)")
    args = parser.parse_args(argv)

    save = not (args.dry_run or args.check)
    stats = run_sync(args.xlsx, args.entities, args.ontology, save=save)
    mode = "" if save else " (미저장)"
    print(stats.summary_line(args.xlsx) + mode)
    if args.check and stats.total:
        print(f"[경고] --check: 변경 {stats.total}건 — 사전집이 YAML 정본과 불일치")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
