#!/usr/bin/env python3
"""
비정형 PDF 요약 생성기 — FAO AMIS · USDA GAIN (WBS 1.1.51 · A-079)

목적(조정자 Req 3): C-04(추출)→P1-05(aspect 신호)→P1-06(엔티티) 체인의 실동작 검증.
각 PDF **옆(동일 폴더)** 에 `{원본파일명}.md` 요약을 생성한다.

요약 구성(에이전트 역할 매핑):
  C-04  : 판독 메타(페이지·문자수)·식용유 관련 섹션 발췌(레이아웃 텍스트)
  P1-05 : aspect 신호 태그(수출규제·수입관세·바이오연료·기상·압착·재고·생산변동·물류)
          + 방향성 힌트(상방/하방 키워드 카운트)
  P1-06 : 정규 엔티티 후보(국가·정책·상품 — src/semantic/entities.yaml 사전 기반)

사용:
  python scripts/summarize_pdfs.py fao          # FAO AMIS 전체
  python scripts/summarize_pdfs.py gain [YYYY]  # GAIN 전체 또는 특정 연도만
의존성: pdfplumber(pypdf 폴백) · PyYAML
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

FAO_DIR  = Path("data/raw/FAO/AMIS")
GAIN_DIR = Path("data/raw/USDA/FAS/GAIN")
ENTITIES_YAML = Path("src/semantic/entities.yaml")

# P1-05 aspect 신호 (p105 스펙 7종 + 물류)
_SIGNALS = {
    r"export\s+tax|export\s+dut|export\s+ban|retencion":            "수출규제",
    r"import\s+tariff|import\s+dut|tariff\s+hike":                  "수입관세",
    r"biodiesel|renewable\s+diesel|\bSAF\b|blend|\bB3[05]\b|\bRFS\b|RVO": "바이오연료수요",
    r"drought|la\s*ni[nñ]a|el\s*ni[nñ]o|excessive\s+rain|heat\s*wave":   "기상이변",
    r"crush(ing)?\b":                                               "압착",
    r"ending\s+stock|carryover|stocks?-to-use|inventor":            "재고",
    r"production\s+(up|down|increase|decrease|revis|forecast)":     "생산변동",
    r"freight|hormuz|red\s+sea|black\s+sea|panama|port\s+congestion": "물류충격",
}
_BULL = r"(surge|rally|increase|rise|tighten|deficit|shortage|hike|higher)"
_BEAR = r"(decline|drop|fall|decrease|surplus|bumper|record\s+crop|lower|cut)"
_VEGOIL_HINT = re.compile(r"(soy(bean)?\s*oil|vegetable\s*oil|palm\s*oil|sun(flower)?\s*oil|rapeseed|canola|oilseed)", re.I)


def _load_entities() -> dict[str, list[str]]:
    """entities.yaml → {canonical: [synonyms...]} 평탄화 (P1-06 사전)."""
    try:
        import yaml
        data = yaml.safe_load(ENTITIES_YAML.read_text(encoding="utf-8"))
    except Exception:
        return {}
    out: dict[str, list[str]] = {}
    for group in (data or {}).values():
        if not isinstance(group, list):
            continue
        for ent in group:
            if isinstance(ent, dict) and ent.get("canonical"):
                out[ent["canonical"]] = [str(s) for s in ent.get("synonyms", [])]
    return out


def _extract_text(pdf: Path, max_pages: int = 25) -> tuple[str, int]:
    try:
        import pdfplumber
        with pdfplumber.open(pdf) as d:
            n = len(d.pages)
            txt = "\n".join(p.extract_text() or "" for p in d.pages[:max_pages])
            return txt, n
    except BaseException:      # pyo3 PanicException 등 비표준 예외 포함 (A-079)
        pass
    try:
        from pypdf import PdfReader
        r = PdfReader(str(pdf))
        return "\n".join(p.extract_text() or "" for p in r.pages[:max_pages]), len(r.pages)
    except Exception:
        return "", 0


def _vegoil_excerpt(text: str, limit: int = 1500) -> str:
    """식용유 관련 문단 우선 발췌 (C-04 — 정보 밀도 우선)."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.strip()) > 60]
    hits = [p for p in paras if _VEGOIL_HINT.search(p)]
    body = "\n\n".join(hits[:6]) if hits else "\n\n".join(paras[:3])
    body = re.sub(r"[ \t]+", " ", body)
    return body[:limit]


def summarize_pdf(pdf: Path, entities: dict[str, list[str]]) -> bool:
    out = pdf.with_suffix(".md")
    text, n_pages = _extract_text(pdf)
    low = text.lower()
    readable = len(text.strip()) > 80

    signals = sorted({tag for pat, tag in _SIGNALS.items() if re.search(pat, low)}) if readable else []
    bull = len(re.findall(_BULL, low)); bear = len(re.findall(_BEAR, low))
    tone = ("상방 우세" if bull > bear * 1.3 else "하방 우세" if bear > bull * 1.3 else "중립/혼재") if readable else "판독불가"

    found_entities = []
    if readable:
        for canonical, syns in entities.items():
            if any(re.search(r"\b" + re.escape(s.lower()) + r"\b", low) for s in syns if len(s) > 2):
                found_entities.append(canonical)

    lines = [
        f"# 요약 — {pdf.name}",
        "",
        f"- **판독(C-04)**: {'✅ 정상' if readable else '🚨 실패(스캔본 가능성)'} · 페이지 {n_pages} · 추출 {len(text.strip()):,}자",
        f"- **신호 태그(P1-05)**: {', '.join(signals) if signals else '—'}",
        f"- **방향성 힌트(P1-05)**: {tone} (상방어 {bull} · 하방어 {bear})",
        f"- **엔티티 후보(P1-06)**: {', '.join(found_entities[:12]) if found_entities else '—'}",
        "",
        "## 식용유 관련 발췌 (원문 그대로 — provenance)",
        "",
        _vegoil_excerpt(text) if readable else "_(텍스트 추출 실패)_",
        "",
        f"---\n*자동 생성: scripts/summarize_pdfs.py · 출처 파일: `{pdf.name}` (동일 폴더)*",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    return readable


def run(target: str, year: str | None = None) -> None:
    entities = _load_entities()
    if target == "fao":
        pdfs = sorted(FAO_DIR.rglob("*.pdf"))
    elif target == "gain":
        base = GAIN_DIR
        pdfs = sorted(base.rglob(f"{year}/**/*.pdf")) if year else sorted(base.rglob("*.pdf"))
    else:
        print("사용법: summarize_pdfs.py [fao|gain] [YYYY]"); return
    print(f"[C-04→P1-05→P1-06] {target} PDF {len(pdfs)}건 요약 생성...")
    ok = fail = 0
    for i, pdf in enumerate(pdfs, 1):
        try:
            if summarize_pdf(pdf, entities):
                ok += 1
            else:
                fail += 1
        except Exception as e:
            fail += 1
            print(f"  [오류] {pdf.name}: {e}")
        if i % 25 == 0:
            print(f"  … {i}/{len(pdfs)}")
    print(f"[완료] 요약 md {ok+fail}건 생성 (판독 정상 {ok} · 실패 {fail}) — 각 PDF 동일 폴더에 저장")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "fao",
        sys.argv[2] if len(sys.argv) > 2 else None)
