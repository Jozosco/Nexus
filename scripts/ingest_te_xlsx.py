#!/usr/bin/env python3
"""
Trading Economics 히스토리 xlsx 수집·정형화 (WBS 1.1.44 · A-061)

배경: TE API 실시간 수집이 불안정하여(요청 근거) 조정자가 9개년(2017.01.01~2026.07.01)
      히스토리 xlsx를 수동 업로드함. 본 스크립트가 이를 롱포맷 parquet로 정형화한다.

입력: data/raw/Trading Economics/Markets/Commodities/{Agricultural,Energy,Shipping Indices}/*.xlsx
      (폴백: data/raw/*.xlsx — 재정리 전 상태)
      파일명 규칙: {YYYY}~{YYYY}_{Commodity}[_{Exchange}]_{Units}.xlsx
      시트명: '{YYYY}년' (연도별) · 컬럼: Month, Day, Open, High, Low, Close

출력: data/raw/te_commodities_historical.parquet
      컬럼: price_date, indicator_code, value(=Close), open, high, low,
            commodity, category, unit, exchange, source_name, ingested_at

주의(CLAUDE.md §2): xlsx는 수동 히스토리 백필 예외(USDA 패턴과 동일). 파이프라인 상시
      소스는 아니며 Snowflake 이관 전 1회성 정형화 용도.

의존성: pandas >= 2.0 · openpyxl(읽기 엔진)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

import pandas as pd

TE_ROOT   = Path("data/raw/Trading Economics/Markets/Commodities")
RAW_ROOT  = Path("data/raw")
OUT_PATH  = Path("data/raw/te_commodities_historical.parquet")

# 품목 → 카테고리 (폴더 미존재 시 파일명 기반 분류)
_AGRI = {"canola", "palm oil", "rapeseed", "soybeans", "sunflower oil"}
_SHIP = {"bdi", "containerized freight index", "drewry world container index"}
_INDU = {"di-ammonium", "urea", "dap"}
# 그 외 에너지 (brent, wti, coal, natural gas, gasoline 등)

_YEAR_SHEET_RE = re.compile(r"(\d{4})\s*년")


def _classify(commodity: str, parent: str) -> str:
    """폴더명 우선, 없으면 품목명으로 카테고리 판정."""
    p = parent.lower()
    if "agricultural" in p:
        return "Agricultural"
    if "energy" in p:
        return "Energy"
    if "shipping" in p:
        return "Shipping Indices"
    if "industrial" in p:
        return "Industrial"
    c = commodity.lower()
    if c in _AGRI:
        return "Agricultural"
    if c in _SHIP:
        return "Shipping Indices"
    if c in _INDU:
        return "Industrial"
    return "Energy"


def _parse_filename(stem: str) -> Optional[tuple[str, str, str]]:
    """'{YYYY}~{YYYY}_{Commodity}[_{Exchange}]_{Units}' → (commodity, exchange, unit)."""
    parts = stem.split("_")
    if len(parts) < 3 or "~" not in parts[0]:
        return None
    commodity = parts[1].strip()
    unit = parts[-1].strip()
    exchange = "_".join(parts[2:-1]).strip() if len(parts) > 3 else ""
    return (commodity, exchange, unit)


def _indicator_code(commodity: str) -> str:
    """품목명 → TE_ 접두 스네이크 대문자 지표코드."""
    slug = re.sub(r"[^A-Za-z0-9]+", "_", commodity).strip("_").upper()
    return f"TE_{slug}"


def _iter_te_files() -> list[Path]:
    """TE 폴더 우선, 없으면 루트의 YYYY~YYYY_ xlsx."""
    if TE_ROOT.exists():
        files = sorted(TE_ROOT.rglob("*.xlsx"))
        if files:
            return files
    return sorted(p for p in RAW_ROOT.glob("*.xlsx")
                  if re.match(r"\d{4}~\d{4}_", p.name))


def parse_te_file(path: Path) -> pd.DataFrame:
    """단일 TE xlsx → 롱포맷 DataFrame (연도 시트 전체)."""
    parsed = _parse_filename(path.stem)
    if parsed is None:
        print(f"  [건너뜀] 파일명 규칙 불일치: {path.name}")
        return pd.DataFrame()
    commodity, exchange, unit = parsed
    category = _classify(commodity, path.parent.name)
    code = _indicator_code(commodity)

    try:
        xl = pd.ExcelFile(path)
    except Exception as e:
        print(f"  [오류] 엑셀 열기 실패 {path.name}: {e}")
        return pd.DataFrame()

    rows: list[pd.DataFrame] = []
    for sheet in xl.sheet_names:
        m = _YEAR_SHEET_RE.search(str(sheet))
        if not m:
            continue
        year = int(m.group(1))
        try:
            df = xl.parse(sheet)
        except Exception as e:
            print(f"    [경고] 시트 파싱 실패 {path.name}:{sheet}: {e}")
            continue
        if df.empty or not {"Month", "Day"}.issubset(df.columns):
            continue
        close_col = next((c for c in ("Close", "close", "Price", "value") if c in df.columns), None)
        if close_col is None:
            continue
        sub = df[["Month", "Day"]].copy()
        sub["year"] = year
        sub["price_date"] = pd.to_datetime(
            dict(year=sub["year"], month=sub["Month"], day=sub["Day"]),
            errors="coerce",
        )
        sub["value"] = pd.to_numeric(df[close_col], errors="coerce")
        for col in ("Open", "High", "Low"):
            sub[col.lower()] = pd.to_numeric(df[col], errors="coerce") if col in df.columns else pd.NA
        sub = sub.dropna(subset=["price_date", "value"])
        rows.append(sub[["price_date", "value", "open", "high", "low"]])

    if not rows:
        print(f"  [경고] 유효 데이터 없음: {path.name}")
        return pd.DataFrame()

    out = pd.concat(rows, ignore_index=True)
    out["indicator_code"] = code
    out["commodity"]      = commodity
    out["category"]       = category
    out["unit"]           = unit
    out["exchange"]       = exchange or "N/A"
    out["source_name"]    = "TradingEconomics_history_xlsx"
    out["ingested_at"]    = pd.Timestamp.now("UTC")
    return out.sort_values("price_date").reset_index(drop=True)


def run() -> None:
    files = _iter_te_files()
    if not files:
        print("[경고] TE xlsx 없음 (폴더/루트 모두 비어 있음).")
        return
    print(f"[C-03] Trading Economics {len(files)}개 파일 정형화 중...")
    frames = []
    for f in files:
        df = parse_te_file(f)
        if not df.empty:
            frames.append(df)
            print(f"  [OK] {f.name}: {len(df):,}행 "
                  f"({df['price_date'].min().date()}~{df['price_date'].max().date()})")

    if not frames:
        print("[경고] 정형화된 데이터 없음.")
        return

    combined = pd.concat(frames, ignore_index=True)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(OUT_PATH, index=False)

    print(f"\n[완료] → {OUT_PATH}")
    print(f"  총 {len(combined):,}행 · 지표 {combined['indicator_code'].nunique()}종 "
          f"· 기간 {combined['price_date'].min().date()}~{combined['price_date'].max().date()}")
    by_cat = combined.groupby("category")["indicator_code"].nunique()
    for cat, n in by_cat.items():
        print(f"  - {cat}: {n}종")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 단일 파일 테스트 모드
        out = parse_te_file(Path(sys.argv[1]))
        print(out.head(10).to_string())
        print(f"... 총 {len(out)}행")
    else:
        run()
