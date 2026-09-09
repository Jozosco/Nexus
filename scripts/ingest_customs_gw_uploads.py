#!/usr/bin/env python3
"""관세청 GW 업로드 원본(승인자 수동 업로드 xlsx) → 롱포맷 parquet (A-247).

배경: 업로드본 172파일(16 HS 품목군 · 10자리 하위 코드 · 국가별 · 17 연도 시트)이 저장소에
있으나 일별 분석에 기여하는 파서가 없었다 — `ingest_customs_gw_xlsx.py`는 API 수집기(6자리·
국가 10 고정·`_API.xlsx` 작성 전용), `verify_customs_gw.py`는 검증 전용, `landed_cost`는
1507.10 2폴더만 직독. 이 스크립트가 **업로드본 전체**를 하나의 롱포맷으로 정규화한다.

규약:
  - 원본 xlsx는 읽기 전용(A-184 원본 불가침). `_API.xlsx`·`.partial.xlsx`는 제외(API 소관).
  - 통합본(`16years…`)은 country=WORLD로 별도 보존(국가 합산과 혼입 금지 — 검증 참조용).
  - 시트 구조: 연도 시트 × 월행 × [무역수지·수출액·수출량·수입액·수입량](헤더행 '무역수지' 탐지).
  - 미완결 월(당해 연도 현재 월 이후)은 물리 제약으로 제거(A-122 GATS 동일 원리).
  - 지표코드: KCS_{HS}_{METRIC}_{국가코드} — HS는 10자리(하위 폴더) 또는 6자리(루트 파일).
  - as-of 5필드는 attach_asof(source="CUSTOMS_")가 부여(D-023 — 확정치 개정은 vintage).

출력: data/raw/customs_gw_uploads_historical.parquet + stdout 요약(품목×국가×월 수).
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

import pandas as pd

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from src.pipeline.asof import attach_asof  # noqa: E402

GW_ROOT = Path("data/raw/관세청/Import Export Performance by Commodity and Country(GW)")
OUT = Path("data/raw/customs_gw_uploads_historical.parquet")

_MONTH_RE = re.compile(r"(\d{1,2})\s*월")
_HS6_RE = re.compile(r"(\d{4})\.(\d{2})")          # 'Palm Oil (1511.90)' · '1507.10'
_SUB_RE = re.compile(r"\(\.(\d{4})\)")             # 'Palm Olein (.1000)'
_METRICS = ("BAL_USD", "EXP_USD", "EXP_KG", "IMP_USD", "IMP_KG")   # 열 1~5 순서
_UNITS = {"BAL_USD": "USD", "EXP_USD": "USD", "EXP_KG": "kg", "IMP_USD": "USD", "IMP_KG": "kg"}
COUNTRY_CODES = {
    "u.s.a": "US", "usa": "US", "united states": "US", "argentina": "AR", "brazil": "BR",
    "china": "CN", "indonesia": "ID", "malaysia": "MY", "netherlands": "NL", "spain": "ES",
    "paraguay": "PY", "vietnam": "VN", "australia": "AU", "austrailia": "AU",   # 업로드 오타 흡수
    "germany": "DE", "united arab emirates": "AE", "canada": "CA", "ukraine": "UA",
    "hungary": "HU", "turkey": "TR", "turkiye": "TR", "türkiye": "TR", "singapore": "SG",
}


def _hs_from_path(path: Path) -> tuple[str, int, str, str]:
    """경로 → (hs_code, hs_level, commodity_folder, use_label)."""
    parts = path.relative_to(GW_ROOT).parts[:-1]
    hs6 = sub = ""
    commodity = parts[0] if parts else ""
    use_label = ""
    for part in parts:
        m6 = _HS6_RE.search(part)
        if m6 and not hs6:
            hs6 = m6.group(1) + m6.group(2)
        ms = _SUB_RE.search(part)
        if ms:
            sub = ms.group(1)
            use_label = _SUB_RE.sub("", part).strip()
    if not hs6:
        raise ValueError(f"[오류] HS 6자리를 경로에서 찾지 못함: {path}")
    return (hs6 + sub, 10 if sub else 6, commodity, use_label)


def _country_code(stem: str) -> str:
    if stem.lower().startswith("16years"):
        return "WORLD"
    return COUNTRY_CODES.get(stem.strip().lower(), re.sub(r"[^A-Za-z]", "", stem).upper()[:8])


def _file_kind(path: Path) -> str:
    """'xlsx' | 'drm' | 'unknown' — 매직 바이트 판별(A-051·A-085 DRM 래퍼 전례)."""
    head = path.read_bytes()[:16]
    if head[:2] == b"PK":
        return "xlsx"
    if head.startswith(b"<DOCUMEN"):
        return "drm"
    return "unknown"


def _parse_file(path: Path, today: date) -> pd.DataFrame:
    recs: list[dict] = []
    try:
        xl = pd.ExcelFile(path)
    except Exception as e:  # noqa: BLE001
        print(f"  [경고] {path.name} 읽기 실패: {type(e).__name__}: {e}")
        return pd.DataFrame()
    for sheet in xl.sheet_names:
        ym = re.search(r"(\d{4})", str(sheet))
        if not ym:
            continue
        year = int(ym.group(1))
        raw = xl.parse(sheet, header=None)
        hdr = next((i for i in range(min(6, len(raw)))
                    if raw.iloc[i].astype(str).str.contains("무역수지").any()), None)
        if hdr is None:
            continue
        for r in range(hdr + 1, len(raw)):
            mm = _MONTH_RE.search(str(raw.iloc[r, 0]))
            if not mm:
                continue
            month = int(mm.group(1))
            if not 1 <= month <= 12:
                continue
            if (year, month) >= (today.year, today.month):   # 미완결 월 제거(A-122 원리)
                continue
            vals = [pd.to_numeric(raw.iloc[r, c], errors="coerce") for c in range(1, 6)]
            if all(pd.isna(v) for v in vals):
                continue
            for metric, v in zip(_METRICS, vals):
                if pd.isna(v):
                    continue
                recs.append({"year": year, "month": month, "metric": metric, "value": float(v)})
    return pd.DataFrame(recs)


def run(today: date | None = None) -> pd.DataFrame:
    today = today or date.today()
    files = sorted(p for p in GW_ROOT.rglob("*.xlsx")
                   if not p.stem.endswith("_API") and ".partial" not in p.name)
    if not files:
        raise SystemExit(f"[오류] 관세청 GW 업로드본 없음 — {GW_ROOT}")
    frames: list[pd.DataFrame] = []
    skipped: list[str] = []
    drm_or_bad: list[str] = []
    empty_templates: list[str] = []
    for f in files:
        try:
            hs, level, commodity, use_label = _hs_from_path(f)
        except ValueError as e:
            skipped.append(f"{f.name}: {e}")
            continue
        cc = _country_code(f.stem)
        kind = _file_kind(f)
        if kind != "xlsx":
            label = "DRM 래퍼(<DOCUMENT SAFER> — 해제 후 재업로드 필요)" if kind == "drm" else "형식 불명"
            drm_or_bad.append(f"{f.relative_to(GW_ROOT)}: {label}")
            continue
        df = _parse_file(f, today)
        if df.empty:
            empty_templates.append(str(f.relative_to(GW_ROOT)))   # A-075 사전 템플릿(값 0개)
            continue
        df["price_date"] = pd.to_datetime(dict(year=df["year"], month=df["month"], day=1))
        df["indicator_code"] = "KCS_" + hs + "_" + df["metric"] + "_" + cc
        df["unit"] = df["metric"].map(_UNITS)
        df["hs_code"] = hs
        df["hs_level"] = level
        df["country"] = cc
        df["country_name"] = f.stem
        df["commodity"] = commodity
        df["use_label"] = use_label
        df["source_name"] = "KoreaCustoms_GW_upload"
        df["note"] = f"[관세청 GW 업로드본] {commodity} / {use_label or 'HS6 루트'} / {f.stem}"
        frames.append(df.drop(columns=["year", "month", "metric"]))
    if not frames:
        raise SystemExit("[오류] 관세청 GW 업로드본 파싱 결과 0행 — 시트 구조 확인 필요")
    out = pd.concat(frames, ignore_index=True)
    dup = out.duplicated(subset=["indicator_code", "price_date"]).sum()
    if dup:
        raise SystemExit(f"[오류] 지표코드 충돌 {dup}건 — 동일 (HS,국가,월)이 복수 파일에 존재(D-033 원칙: 자동 선택 금지)")
    out["ingested_at"] = pd.Timestamp.now("UTC")
    out = attach_asof(out, source="CUSTOMS_")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT, index=False)

    # 요약
    print(f"[완료] 관세청 GW 업로드본 {len(files)}파일 → {len(out):,}행 · 지표 {out['indicator_code'].nunique():,}종 "
          f"· {out['price_date'].min().date()}~{out['price_date'].max().date()} → {OUT}")
    summ = (out[out["country"] != "WORLD"]
            .groupby(["commodity", "hs_code"])
            .agg(countries=("country", lambda s: ",".join(sorted(set(s)))),
                 months=("price_date", "nunique"))
            .reset_index())
    with pd.option_context("display.max_rows", 100, "display.width", 200):
        print(summ.to_string(index=False))
    if drm_or_bad:
        print(f"[경고] 판독 불가 {len(drm_or_bad)}건(재업로드 필요):")
        for x in drm_or_bad:
            print(f"    · {x}")
    if empty_templates:
        print(f"[정보] 빈 템플릿(값 없음) {len(empty_templates)}건 — 데이터 아님(A-075 사전 생성분): "
              + " | ".join(Path(x).parent.name + "/" + Path(x).name for x in empty_templates[:12]))
    if skipped:
        print(f"[정보] 건너뜀 {len(skipped)}건: " + " | ".join(skipped[:10]))
    return out


if __name__ == "__main__":
    run()
