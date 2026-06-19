#!/usr/bin/env python3
"""
USDA FAS PS&D Excel 수집 스크립트 (WBS 1.1.41 변형)

입력: data/raw/USDA/FAS/PSD/*.xlsx
출력: data/raw/psd_historical.parquet

실제 파일 구조 (A-051):
  컬럼 = [Commodity, Attribute, Country, 2017/2018, ..., 2025/2026, Unit Description]
  - Commodity·Attribute는 forward-fill 필요 (병합셀 → 첫 행만 값, 이하 NaN)
  - World/Total 집계 행 없음 → 국가별 값을 마케팅연도별로 합산해 글로벌 산출
  - 'Crush' attribute 미존재 → Oilseed 'Domestic Consumption'을 압착량 프록시로 사용

포함 파일:
  ✅ Oil, Soybean.xlsx     — 대두유 S&D
  ✅ Oilseed, Soybean.xlsx — 대두 원료 S&D (압착 프록시 포함)
  ✅ Meal, Soybean.xlsx    — 대두박 (압착 마진)
  ❌ Oil, Soybean (Local).xlsx — 제외 (D-012)

마케팅연도 → price_date: '2023/2024' → 2023-10-01 (10월 1일 = MY 시작)
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pandas as pd

PSD_DIR    = Path("data/raw/USDA/FAS/PSD")
OUTPUT_DIR = Path("data/raw")

PSD_FILES_TO_INGEST = ["Oil, Soybean.xlsx", "Oilseed, Soybean.xlsx", "Meal, Soybean.xlsx"]

# (commodity_key) → {Attribute: indicator_code}
_INDICATOR_MAP: dict[str, dict[str, str]] = {
    "oil, soybean": {
        "Production":           "PSD_SBO_PRODUCTION",
        "Exports":              "PSD_SBO_EXPORTS",
        "Imports":              "PSD_SBO_IMPORTS",
        "Ending Stocks":        "PSD_SBO_ENDING_STOCKS",
        "Domestic Consumption": "PSD_SBO_TOTAL_USE",
    },
    "oilseed, soybean": {
        "Production":           "PSD_SOY_PRODUCTION",
        "Domestic Consumption": "PSD_SOY_CRUSH",      # 압착량 프록시
        "Exports":              "PSD_SOY_EXPORTS",
        "Ending Stocks":        "PSD_SOY_ENDING_STOCKS",
    },
    "meal, soybean": {
        "Production":           "PSD_SBM_PRODUCTION",
        "Exports":              "PSD_SBM_EXPORTS",
        "Ending Stocks":        "PSD_SBM_ENDING_STOCKS",
    },
}

_MY_COL_RE = re.compile(r"^(\d{4})/\d{2,4}$")


def _my_to_date(col: str) -> date | None:
    m = _MY_COL_RE.match(str(col).strip())
    return date(int(m.group(1)), 10, 1) if m else None


def parse_psd_file(xlsx_path: Path) -> pd.DataFrame:
    commodity_key = xlsx_path.stem.lower()
    indicator_map = _INDICATOR_MAP.get(commodity_key)
    if indicator_map is None:
        print(f"  [건너뜀] 매핑 없는 파일: {xlsx_path.name}")
        return pd.DataFrame()

    df = pd.read_excel(xlsx_path, header=0, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]
    if "Attribute" not in df.columns or "Country" not in df.columns:
        print(f"  [경고] {xlsx_path.name}: 예상 컬럼(Attribute/Country) 없음")
        return pd.DataFrame()

    # 병합셀 forward-fill
    df["Attribute"] = df["Attribute"].ffill()

    my_cols = [c for c in df.columns if _MY_COL_RE.match(str(c).strip())]
    if not my_cols:
        print(f"  [경고] {xlsx_path.name}: 마케팅연도 컬럼 없음")
        return pd.DataFrame()

    base = {
        "source_name": "USDA_FAS_PSD_XLSX",
        "unit":        "1000MT",
        "ingested_at": pd.Timestamp.utcnow(),
        "note":        xlsx_path.name,
    }
    records: list[dict] = []

    for attr, code in indicator_map.items():
        sub = df[df["Attribute"].astype(str).str.strip() == attr]
        if sub.empty:
            continue
        for col in my_cols:
            price_date = _my_to_date(col)
            if price_date is None:
                continue
            world = pd.to_numeric(sub[col], errors="coerce").dropna().sum()  # 국가 합산
            if world > 0:
                records.append({**base, "price_date": price_date,
                                "indicator_code": code, "value": float(world)})

    # 대두유 STU 파생
    if commodity_key == "oil, soybean":
        df_rec = pd.DataFrame(records)
        if not df_rec.empty:
            piv = df_rec.pivot_table(index="price_date", columns="indicator_code",
                                     values="value", aggfunc="first")
            for dt, row in piv.iterrows():
                es = row.get("PSD_SBO_ENDING_STOCKS")
                tu = row.get("PSD_SBO_TOTAL_USE")
                if pd.notna(es) and pd.notna(tu) and tu > 0:
                    records.append({**base, "price_date": dt, "unit": "percent",
                                    "indicator_code": "PSD_SBO_STU",
                                    "value": round(es / tu * 100, 2)})

    return pd.DataFrame(records)


def run(psd_dir: Path = PSD_DIR, output_dir: Path = OUTPUT_DIR) -> None:
    target_files = [psd_dir / f for f in PSD_FILES_TO_INGEST if (psd_dir / f).exists()]
    missing = [f for f in PSD_FILES_TO_INGEST if not (psd_dir / f).exists()]
    if missing:
        print(f"[경고] 다음 파일 없음: {missing}")
    if not target_files:
        print(f"[오류] {psd_dir}에 대상 파일 없음.")
        return

    print(f"[C-04] PS&D Excel {len(target_files)}개 파일 파싱 시작...")
    all_frames: list[pd.DataFrame] = []
    for f in target_files:
        print(f"  처리 중: {f.name}")
        try:
            df = parse_psd_file(f)
            if not df.empty:
                all_frames.append(df)
            print(f"    → {len(df)}건 추출")
        except Exception as e:
            print(f"    [오류] {f.name}: {e}")

    if not all_frames:
        print("[경고] 추출된 PS&D 레코드 없음 — parquet 미생성.")
        return

    combined = pd.concat(all_frames, ignore_index=True)
    combined = combined.sort_values(["price_date", "indicator_code"]).reset_index(drop=True)

    out_path = output_dir / "psd_historical.parquet"
    output_dir.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(out_path, index=False)

    print(f"\n[완료] {len(combined)}건 → {out_path}")
    print(f"  기간: {combined['price_date'].min()} ~ {combined['price_date'].max()}")
    print(f"  지표: {sorted(combined['indicator_code'].unique())}")


if __name__ == "__main__":
    run()
