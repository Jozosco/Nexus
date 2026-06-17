#!/usr/bin/env python3
"""
USDA FAS PS&D Excel 수집 스크립트 (WBS 1.1.41 변형)

입력: data/raw/USDA/FAS/PSD/*.xlsx
출력: data/raw/psd_historical.parquet

포함 파일:
  ✅ Oil, Soybean.xlsx    — 대두유 공급/수요 밸런스 (국제 무역 포함)
  ✅ Oilseed, Soybean.xlsx — 대두 원료 공급/수요 (선행 지표)
  ✅ Meal, Soybean.xlsx   — 대두박 (압착 마진 계산용)
  ❌ Oil, Soybean (Local).xlsx — 제외 (D-012: 수공업 생산·무역 비포함)

마케팅연도 처리:
  "2023" → price_date = 2023-10-01 (10월 1일 = 마케팅연도 시작)
  참조: c01_p101_psd_local_vs_standard_2026_06_17.md

수집 지표:
  PSD_SBO_PRODUCTION        : 대두유 글로벌 생산량 (1,000 MT)
  PSD_SBO_EXPORTS           : 대두유 글로벌 수출량 (1,000 MT)
  PSD_SBO_IMPORTS           : 대두유 글로벌 수입량 (1,000 MT)
  PSD_SBO_ENDING_STOCKS     : 대두유 기말재고 (1,000 MT)
  PSD_SBO_TOTAL_USE         : 대두유 총소비 (1,000 MT)
  PSD_SBO_STU               : 재고사용비율 (%)
  PSD_SOY_PRODUCTION        : 대두 글로벌 생산량 (100만 MT)
  PSD_SOY_CRUSH             : 대두 압착량 (100만 MT)
  PSD_SBM_PRODUCTION        : 대두박 글로벌 생산량 (1,000 MT) [마진 계산용]
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

PSD_DIR    = Path("data/raw/USDA/FAS/PSD")
OUTPUT_DIR = Path("data/raw")

PSD_FILES_TO_INGEST: list[str] = [
    "Oil, Soybean.xlsx",       # 대두유 S&D 밸런스 (국제 무역 포함) ✅
    "Oilseed, Soybean.xlsx",   # 대두 원료 S&D (선행 지표) ✅
    "Meal, Soybean.xlsx",      # 대두박 (압착 마진 계산용) ✅
    # "Oil, Soybean (Local).xlsx"  # D-012 결정: 제외
]

_INDICATOR_MAP: dict[str, dict[str, str]] = {
    "oil, soybean": {
        "Production":       "PSD_SBO_PRODUCTION",
        "MY Exports":       "PSD_SBO_EXPORTS",
        "MY Imports":       "PSD_SBO_IMPORTS",
        "Ending Stocks":    "PSD_SBO_ENDING_STOCKS",
        "Total Dom. Cons.": "PSD_SBO_TOTAL_USE",
    },
    "oilseed, soybean": {
        "Production":       "PSD_SOY_PRODUCTION",
        "Crush":            "PSD_SOY_CRUSH",
        "MY Exports":       "PSD_SOY_EXPORTS",
        "Ending Stocks":    "PSD_SOY_ENDING_STOCKS",
    },
    "meal, soybean": {
        "Production":       "PSD_SBM_PRODUCTION",
        "MY Exports":       "PSD_SBM_EXPORTS",
        "Ending Stocks":    "PSD_SBM_ENDING_STOCKS",
    },
}


def _marketing_year_to_date(year_str: str) -> date | None:
    """마케팅연도 → price_date 변환: '2023' → 2023-10-01."""
    try:
        y = int(str(year_str).strip().split("/")[0].split("-")[0])
        if 2000 <= y <= 2040:
            return date(y, 10, 1)
    except (ValueError, IndexError):
        pass
    return None


def parse_psd_file(xlsx_path: Path) -> pd.DataFrame:
    """PS&D Excel 파일 → 마케팅연도별 정규화 DataFrame."""
    commodity_key = xlsx_path.stem.lower()
    indicator_map = _INDICATOR_MAP.get(commodity_key)
    if indicator_map is None:
        print(f"  [건너뜀] 매핑 없는 파일: {xlsx_path.name}")
        return pd.DataFrame()

    try:
        df = pd.read_excel(xlsx_path, engine="openpyxl", index_col=0)
    except Exception as e:
        raise RuntimeError(f"[오류] PS&D Excel 로드 실패: {xlsx_path}: {e}") from e

    # PS&D 형식: 행 = 지표명, 열 = 마케팅연도 (또는 전치 가능)
    # 우선 열이 연도인지 확인
    year_cols: list[tuple[int, str]] = []
    for col in df.columns:
        pd_date = _marketing_year_to_date(str(col))
        if pd_date is not None:
            year_cols.append((col, pd_date))

    if not year_cols:
        # 전치 시도: 행=연도, 열=지표
        df = df.T
        for col in df.columns:
            pd_date = _marketing_year_to_date(str(col))
            if pd_date is not None:
                year_cols.append((col, pd_date))

    records: list[dict] = []
    base = {
        "source_name": "USDA_FAS_PSD_XLSX",
        "unit":        "1000MT",
        "ingested_at": pd.Timestamp.utcnow(),
        "note":        xlsx_path.name,
    }

    for col, price_date in year_cols:
        for row_key, indicator_code in indicator_map.items():
            # 행 이름 근사 매칭
            matched_idx = None
            for idx in df.index:
                if row_key.lower() in str(idx).lower():
                    matched_idx = idx
                    break
            if matched_idx is None:
                continue
            v = pd.to_numeric(df.loc[matched_idx, col], errors="coerce")
            if pd.notna(v):
                records.append({**base, "price_date": price_date,
                                 "indicator_code": indicator_code, "value": float(v)})

    # STU 파생 계산 (대두유 파일)
    if commodity_key == "oil, soybean":
        prod_map: dict[date, float] = {}
        use_map:  dict[date, float] = {}
        stk_map:  dict[date, float] = {}
        for rec in records:
            if rec["indicator_code"] == "PSD_SBO_PRODUCTION":
                prod_map[rec["price_date"]] = rec["value"]
            elif rec["indicator_code"] == "PSD_SBO_TOTAL_USE":
                use_map[rec["price_date"]] = rec["value"]
            elif rec["indicator_code"] == "PSD_SBO_ENDING_STOCKS":
                stk_map[rec["price_date"]] = rec["value"]
        for dt in set(use_map) & set(stk_map):
            total_use = use_map[dt]
            if total_use and total_use > 0:
                stu = round(stk_map[dt] / total_use * 100, 2)
                records.append({**base, "price_date": dt,
                                 "indicator_code": "PSD_SBO_STU",
                                 "value": stu, "unit": "percent"})

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
            all_frames.append(df)
            print(f"    → {len(df)}건 추출")
        except Exception as e:
            print(f"    [오류] {f.name}: {e}")

    if not all_frames:
        print("[오류] 추출된 데이터 없음.")
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
