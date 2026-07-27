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

# session34 §1 속성 선별 (전 품목 공통 적용)
_ATTR_MAP: dict[str, str] = {
    "Beginning Stocks":      "BEGINNING_STOCKS",
    "Production":            "PRODUCTION",
    "Imports":               "IMPORTS",
    "Exports":               "EXPORTS",
    "Ending Stocks":         "ENDING_STOCKS",
    "Domestic Consumption":  "DOMESTIC_USE",
    "Crush":                 "CRUSH",
    "Food Use Dom. Cons.":   "FOOD_USE",
    "Industrial Dom. Cons.": "INDUSTRIAL_USE",
    "Feed Waste Dom. Cons.": "FEED_USE",
    "SME":                   "SME",
    "Total Supply":          "TOTAL_SUPPLY",
    "Total Distribution":    "TOTAL_DISTRIBUTION",
}

# 파일명(stem lower) → 지표 인픽스 (대두 3종 하위호환 유지, 그 외 자동 파생)
_COMMODITY_INFIX: dict[str, str] = {
    "oil, soybean":     "SBO",
    "oilseed, soybean": "SOY",
    "meal, soybean":    "SBM",
}


def _infix_for(stem: str) -> tuple[str, str]:
    """파일명 → (infix, type). type ∈ {oil, meal, oilseed}. 신규 품목 자동 파생."""
    key = stem.strip().lower()
    ptype = key.split(",")[0].strip()          # oil / meal / oilseed
    if key in _COMMODITY_INFIX:
        return _COMMODITY_INFIX[key], ptype
    # 예: 'oil, palm' → OIL_PALM · 'meal, rapeseed' → MEAL_RAPESEED
    return re.sub(r"[^a-z0-9]+", "_", key).strip("_").upper(), ptype

_MY_COL_RE = re.compile(r"^(\d{4})/\d{2,4}$")


def _my_to_date(col: str) -> date | None:
    m = _MY_COL_RE.match(str(col).strip())
    return date(int(m.group(1)), 10, 1) if m else None


def parse_psd_file(xlsx_path: Path) -> pd.DataFrame:
    if "(local)" in xlsx_path.stem.lower():
        print(f"  [건너뜀] Local 파일 제외(D-012): {xlsx_path.name}")
        return pd.DataFrame()
    infix, ptype = _infix_for(xlsx_path.stem)

    df = pd.read_excel(xlsx_path, header=0, engine="openpyxl")
    df.columns = [str(c).strip() for c in df.columns]
    if "Attribute" not in df.columns or "Country" not in df.columns:
        print(f"  [경고] {xlsx_path.name}: 예상 컬럼(Attribute/Country) 없음")
        return pd.DataFrame()

    df["Attribute"] = df["Attribute"].ffill()      # 병합셀 forward-fill
    my_cols = [c for c in df.columns if _MY_COL_RE.match(str(c).strip())]
    if not my_cols:
        print(f"  [경고] {xlsx_path.name}: 마케팅연도 컬럼 없음")
        return pd.DataFrame()

    base = {
        "source_name": "USDA_FAS_PSD_XLSX",
        "unit":        "1000MT",
        "ingested_at": pd.Timestamp.now("UTC"),
        "note":        xlsx_path.name,
    }
    records: list[dict] = []
    attrs_present = set(df["Attribute"].astype(str).str.strip())
    # oilseed에 'Crush' 속성 부재 시 Domestic Consumption을 압착 프록시로
    crush_proxy = (ptype == "oilseed" and "Crush" not in attrs_present)

    for attr, code in _ATTR_MAP.items():
        sub = df[df["Attribute"].astype(str).str.strip() == attr]
        if sub.empty:
            continue
        emit_code = "CRUSH" if (crush_proxy and attr == "Domestic Consumption") else code
        for col in my_cols:
            price_date = _my_to_date(col)
            if price_date is None:
                continue
            world = pd.to_numeric(sub[col], errors="coerce").dropna().sum()  # 국가 합산
            if world > 0:
                records.append({**base, "price_date": price_date,
                                "indicator_code": f"PSD_{infix}_{emit_code}",
                                "value": float(world)})

    # STU 파생 (오일·오일시드): Ending Stocks / (Total Supply|Domestic Use) × 100
    df_rec = pd.DataFrame(records)
    if not df_rec.empty:
        piv = df_rec.pivot_table(index="price_date", columns="indicator_code",
                                 values="value", aggfunc="first")
        for dt, row in piv.iterrows():
            es = row.get(f"PSD_{infix}_ENDING_STOCKS")
            du = row.get(f"PSD_{infix}_TOTAL_SUPPLY") or row.get(f"PSD_{infix}_DOMESTIC_USE")
            if pd.notna(es) and du and du > 0:
                records.append({**base, "price_date": dt, "unit": "percent",
                                "indicator_code": f"PSD_{infix}_STU",
                                "value": round(es / du * 100, 2)})

    return pd.DataFrame(records)


def run(psd_dir: Path = PSD_DIR, output_dir: Path = OUTPUT_DIR) -> None:
    # 전체 PSD xlsx 자동 탐색(Local 제외) — 신규 품목 업로드 시 자동 반영(session34 §1)
    target_files = [f for f in sorted(psd_dir.glob("*.xlsx"))
                    if "(local)" not in f.stem.lower()]
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
