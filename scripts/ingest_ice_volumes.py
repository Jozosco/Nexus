#!/usr/bin/env python3
"""
ICE 월별 거래량(Monthly Volumes) 수집·정형화 (WBS 1.1.45 · A-063)

입력: data/raw/ICE/Reports/Monthly Volumes/{U.S.,E.U.}/*.xlsx
      - U.S. : ICE Futures U.S.  (Financial·Agricultural·Energy) — Futures / Options
      - E.U. : ICE F&O Europe    (Oil·Energy)                   — Futures&Options
      파일명: 'YYYY_Monthly Volume(s) {Futures|Options|Futures&Options}.xlsx'  (단·복수 허용)
      시트명: 'YYYY년' · 다단 헤더(0행=상품군, 1행=세부상품), 2행~=월별 값

출력: data/raw/ice_monthly_volumes.parquet (롱포맷)
      price_date(월초), year, market(US/EU), contract_type, product_group, product,
      volume, indicator_code, source_name, ingested_at

성격: 가격이 아닌 '거래량(유동성·참여도)' — G1 보조 / G2 변동성 레이어 입력 (핵심 인과 변수 아님).

의존성: pandas >= 2.0 · openpyxl
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ICE_ROOT = Path("data/raw/ICE/Reports/Monthly Volumes")
OUT_PATH = Path("data/raw/ice_monthly_volumes.parquet")

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}
_YEAR_RE = re.compile(r"(\d{4})")


def _contract_type(name: str) -> str:
    low = name.lower()
    if "futures&options" in low or "futures & options" in low:
        return "Futures&Options"
    if "option" in low:
        return "Options"
    if "future" in low:
        return "Futures"
    return "Unknown"


def _slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", str(text)).strip("_").upper()


def parse_ice_file(path: Path, market: str) -> pd.DataFrame:
    """단일 ICE xlsx → 롱포맷(월×상품×거래량)."""
    contract = _contract_type(path.stem)
    try:
        xl = pd.ExcelFile(path)
    except Exception as e:
        print(f"  [오류] 열기 실패 {path.name}: {e}")
        return pd.DataFrame()

    records: list[dict] = []
    for sheet in xl.sheet_names:
        ym = _YEAR_RE.search(str(sheet))
        year = int(ym.group(1)) if ym else None
        raw = xl.parse(sheet, header=None)
        if raw.empty:
            continue
        # 헤더 행 탐지: 0열이 'Month'인 행
        hdr_idx = None
        for i in range(min(6, len(raw))):
            if str(raw.iloc[i, 0]).strip().lower() == "month":
                hdr_idx = i
                break
        if hdr_idx is None:
            continue
        group_row = raw.iloc[hdr_idx - 1].ffill() if hdr_idx >= 1 else raw.iloc[hdr_idx]
        prod_row = raw.iloc[hdr_idx]
        data = raw.iloc[hdr_idx + 1:]

        for _, row in data.iterrows():
            month_name = str(row.iloc[0]).strip().lower()
            month = _MONTHS.get(month_name)
            if month is None or year is None:
                continue
            price_date = pd.Timestamp(year=year, month=month, day=1)
            for col in range(1, raw.shape[1]):
                product = str(prod_row.iloc[col]).strip()
                if not product or product.lower() in ("nan", "month"):
                    continue
                val = pd.to_numeric(row.iloc[col], errors="coerce")
                if pd.isna(val):
                    continue
                group = str(group_row.iloc[col]).strip()
                group = "" if group.lower() == "nan" else group
                records.append({
                    "price_date":    price_date,
                    "year":          year,
                    "market":        market,
                    "contract_type": contract,
                    "product_group": group or "Monthly Totals",
                    "product":       product.replace("*", "").strip(),
                    "volume":        float(val),
                    "indicator_code": f"ICE_{market}_{_slug(product)}_{_slug(contract)}",
                    "source_name":   "ICE_MonthlyVolumes_xlsx",
                    "ingested_at":   pd.Timestamp.now("UTC"),
                })

    return pd.DataFrame(records)


def run() -> None:
    if not ICE_ROOT.exists():
        print(f"[경고] {ICE_ROOT} 없음.")
        return
    markets = {"U.S.": "US", "E.U.": "EU"}
    frames = []
    for folder, market in markets.items():
        files = sorted((ICE_ROOT / folder).glob("*.xlsx"))
        if not files:
            print(f"[정보] {folder} — 파일 없음.")
            continue
        print(f"[C-03] ICE {market}: {len(files)}개 파일 파싱...")
        for f in files:
            df = parse_ice_file(f, market)
            if not df.empty:
                frames.append(df)
                print(f"  [OK] {f.name}: {len(df):,}행")

    if not frames:
        print("[경고] 정형화된 ICE 데이터 없음.")
        return

    combined = pd.concat(frames, ignore_index=True).sort_values(
        ["market", "contract_type", "price_date", "product"]).reset_index(drop=True)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(OUT_PATH, index=False)

    print(f"\n[완료] → {OUT_PATH}")
    print(f"  총 {len(combined):,}행 · 지표 {combined['indicator_code'].nunique()}종 "
          f"· 기간 {combined['price_date'].min().date()}~{combined['price_date'].max().date()}")
    for (mkt, ct), g in combined.groupby(["market", "contract_type"]):
        print(f"  - {mkt}/{ct}: {g['product'].nunique()}개 상품, {len(g):,}행")


if __name__ == "__main__":
    run()
