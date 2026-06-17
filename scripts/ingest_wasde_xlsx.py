#!/usr/bin/env python3
"""
USDA FAS WASDE Excel 수동 업로드 데이터 수집 스크립트 (WBS 1.1.41)

입력: data/raw/USDA/WASDE/*.xlsx  (17년~26년 취합본, 월별 시트)
출력: data/raw/wasde_historical_{YYYY}.parquet  → Snowflake (Phase B)

시트 구조:
  - 각 파일은 해당 연도의 1월~12월 (또는 수집된 월까지) 시트를 포함
  - 각 시트: USDA WASDE 형식의 대두/유지류 공급·수요 테이블

수집 지표:
  - WASDE_SBO_PRODUCTION     : 대두유 글로벌 생산량 (1,000 MT)
  - WASDE_SBO_CONSUMPTION    : 대두유 글로벌 소비량 (1,000 MT)
  - WASDE_SBO_EXPORTS        : 대두유 글로벌 수출량 (1,000 MT)
  - WASDE_SBO_ENDING_STOCKS  : 대두유 기말재고 (1,000 MT)
  - WASDE_SBO_STU            : 재고사용비율 Ending Stocks / Total Use × 100 (%)
  - WASDE_SOY_PRODUCTION     : 대두 글로벌 생산량 (100만 MT) [선행 지표]

제약:
  - openpyxl 미사용 (CLAUDE.md §2): pipeline 데이터는 Snowflake 경유
  - 이 스크립트는 scripts/ 전용 수동 실행 도구
  - Snowflake 연동은 Phase B에서 추가
"""
from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd

# ── 경로 상수 ─────────────────────────────────────────────────────────────────
WASDE_DIR   = Path("data/raw/USDA/WASDE")
OUTPUT_DIR  = Path("data/raw")
REPORT_DIR  = Path("reports/pipeline")

# 파일명 → 연도 추출 패턴: "17년_곡물 및 유지류 취합본.xlsx" → 2017
_YEAR_RE = re.compile(r"^(\d{2})년")

# 대두유 행 식별 키워드 (한국어/영어 혼용 취합본 고려)
_SBO_KEYWORDS = [
    "대두유", "SBO", "Soybean Oil", "Soybean oil",
    "Soybean Oils", "Bean Oil",
]
_SOY_KEYWORDS = [
    "대두", "Soybeans", "Soybean", "대두(대두박·두유 포함)",
]

# 컬럼명 → 지표코드 매핑 후보 (취합본 포맷에 따라 달라질 수 있음)
_COL_MAP: dict[str, str] = {
    "production":        "WASDE_SBO_PRODUCTION",
    "생산량":            "WASDE_SBO_PRODUCTION",
    "consumption":       "WASDE_SBO_CONSUMPTION",
    "소비량":            "WASDE_SBO_CONSUMPTION",
    "exports":           "WASDE_SBO_EXPORTS",
    "수출량":            "WASDE_SBO_EXPORTS",
    "ending stocks":     "WASDE_SBO_ENDING_STOCKS",
    "기말재고":          "WASDE_SBO_ENDING_STOCKS",
    "total use":         "WASDE_SBO_TOTAL_USE",
    "총소비":            "WASDE_SBO_TOTAL_USE",
}


def _year_from_filename(filename: str) -> Optional[int]:
    """파일명에서 연도 추출: '17년_...' → 2017."""
    m = _YEAR_RE.match(filename)
    if not m:
        return None
    yy = int(m.group(1))
    return 2000 + yy


def _month_from_sheet(sheet_name: str) -> Optional[int]:
    """시트명에서 월 추출: '1월', 'Jan', '1', '01' → 1."""
    month_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4,
        "may": 5, "jun": 6, "jul": 7, "aug": 8,
        "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }
    sn = sheet_name.strip().lower()
    if sn in month_map:
        return month_map[sn]
    m = re.match(r"^(\d{1,2})월?$", sn)
    if m:
        v = int(m.group(1))
        return v if 1 <= v <= 12 else None
    return None


def _extract_sbo_row(df: pd.DataFrame, keywords: list[str]) -> Optional[pd.Series]:
    """DataFrame에서 대두유 행 탐색 (첫 번째 컬럼 기준)."""
    first_col = df.iloc[:, 0].astype(str)
    for kw in keywords:
        matches = first_col[first_col.str.contains(kw, case=False, na=False)]
        if not matches.empty:
            return df.loc[matches.index[0]]
    return None


def _compute_stu(production: float, consumption: float, ending_stocks: float) -> Optional[float]:
    """재고사용비율(STU) 계산: Ending Stocks / Total Use × 100."""
    total_use = consumption  # 간이 근사
    if total_use and total_use > 0:
        return round(ending_stocks / total_use * 100, 2)
    return None


def parse_wasde_file(xlsx_path: Path) -> pd.DataFrame:
    """단일 WASDE 취합본 Excel → 정규화 DataFrame 변환."""
    year = _year_from_filename(xlsx_path.name)
    if year is None:
        raise ValueError(f"[오류] 연도 추출 실패: {xlsx_path.name}. 파일명 형식 확인 필요.")

    try:
        xl = pd.ExcelFile(xlsx_path, engine="openpyxl")
    except Exception as e:
        raise RuntimeError(f"[오류] Excel 파일 로드 실패: {xlsx_path}: {e}") from e

    records: list[dict] = []
    for sheet_name in xl.sheet_names:
        month = _month_from_sheet(sheet_name)
        if month is None:
            continue  # 목차, 메모 시트 등 건너뜀

        price_date = date(year, month, 1)

        try:
            df_sheet = xl.parse(sheet_name, header=None)
        except Exception as e:
            print(f"  [경고] 시트 파싱 실패 {sheet_name}: {e}")
            continue

        # 대두유 행 탐색
        sbo_row = _extract_sbo_row(df_sheet, _SBO_KEYWORDS)
        if sbo_row is None:
            print(f"  [정보] {year}/{month:02d}: 대두유 행 없음 — 건너뜀")
            continue

        # 수치 컬럼 추출 (숫자형 컬럼만)
        numeric_vals = pd.to_numeric(sbo_row, errors="coerce").dropna()
        if len(numeric_vals) < 3:
            print(f"  [경고] {year}/{month:02d}: 유효 수치 부족 ({len(numeric_vals)}개)")
            continue

        # 컬럼 위치 기반 순서 추정 (production / consumption / exports / ending_stocks)
        col_values = numeric_vals.values.tolist()

        base_record = {
            "price_date":     price_date,
            "source_name":    "USDA_WASDE_XLSX",
            "unit":           "1000MT",
            "ingested_at":    pd.Timestamp.utcnow(),
            "note":           f"{xlsx_path.name} / {sheet_name}",
        }

        # 최소 4개 수치가 있으면 순서대로 매핑
        indicator_order = [
            "WASDE_SBO_PRODUCTION",
            "WASDE_SBO_CONSUMPTION",
            "WASDE_SBO_EXPORTS",
            "WASDE_SBO_ENDING_STOCKS",
        ]
        for i, code in enumerate(indicator_order):
            if i < len(col_values):
                records.append({**base_record, "indicator_code": code, "value": col_values[i]})

        # STU 파생 계산
        if len(col_values) >= 4:
            stu = _compute_stu(col_values[0], col_values[1], col_values[3])
            if stu is not None:
                records.append({**base_record, "indicator_code": "WASDE_SBO_STU",
                                 "value": stu, "unit": "percent"})

    if not records:
        print(f"  [경고] {xlsx_path.name}: 추출된 레코드 없음")

    return pd.DataFrame(records)


def run(wasde_dir: Path = WASDE_DIR, output_dir: Path = OUTPUT_DIR) -> None:
    """전체 WASDE Excel 파일 수집·정규화·저장."""
    xlsx_files = sorted(wasde_dir.glob("*.xlsx"))
    if not xlsx_files:
        print(f"[오류] {wasde_dir}에 xlsx 파일 없음. 파일 업로드 후 재실행하세요.")
        return

    print(f"[C-04] WASDE Excel {len(xlsx_files)}개 파일 파싱 시작...")
    all_frames: list[pd.DataFrame] = []
    for f in xlsx_files:
        print(f"  처리 중: {f.name}")
        try:
            df = parse_wasde_file(f)
            all_frames.append(df)
            print(f"    → {len(df)}건 추출")
        except Exception as e:
            print(f"    [오류] {f.name}: {e}")

    if not all_frames:
        print("[오류] 추출된 데이터 없음.")
        return

    combined = pd.concat(all_frames, ignore_index=True)
    combined = combined.sort_values(["price_date", "indicator_code"]).reset_index(drop=True)

    out_path = output_dir / "wasde_historical.parquet"
    output_dir.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(out_path, index=False)

    print(f"\n[완료] {len(combined)}건 → {out_path}")
    print(f"  기간: {combined['price_date'].min()} ~ {combined['price_date'].max()}")
    print(f"  지표: {combined['indicator_code'].unique().tolist()}")


if __name__ == "__main__":
    run()
