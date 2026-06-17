#!/usr/bin/env python3
"""
USDA FAS GATS 수출/재수출 통계 수집 스크립트 (WBS 1.1.42)

입력: data/raw/USDA/FAS/GATS/*.xlsx
출력: data/raw/gats_historical.parquet

파일 명명 규칙:
  - 수출:   YYYY년 미국 對국가별 수출량.xlsx
  - 재수출: YYYY년 미국 對국가별 재수출량.xlsx
  (2018년 재수출 파일 없음 → 해당 연도 재수출 = 0 처리)

HS 코드: 1507 (대두유, crude + refined)
수집 지표:
  - GATS_US_SBO_EXPORT_TOTAL      : 미국 SBO 전체 수출량 (MT)
  - GATS_US_SBO_EXPORT_KOREA      : 미국 → 한국 수출량 (MT)
  - GATS_US_SBO_EXPORT_CHINA      : 미국 → 중국 수출량 (MT)
  - GATS_US_SBO_REEXPORT_TOTAL    : 미국 재수출 전체 (MT)
  - GATS_US_SBO_DOMESTIC_USE      : 미국 내수 = 총수입 - 재수출 (MT) [Phase B 파생]
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pandas as pd

GATS_DIR   = Path("data/raw/USDA/FAS/GATS")
OUTPUT_DIR = Path("data/raw")

_YEAR_RE = re.compile(r"^(\d{4})년")

# 주요 수출 대상국 코드 (GATS 파일 내 컬럼명 또는 행 식별)
TARGET_COUNTRIES: dict[str, str] = {
    "Korea": "GATS_US_SBO_EXPORT_KOREA",
    "South Korea": "GATS_US_SBO_EXPORT_KOREA",
    "한국": "GATS_US_SBO_EXPORT_KOREA",
    "China": "GATS_US_SBO_EXPORT_CHINA",
    "중국": "GATS_US_SBO_EXPORT_CHINA",
    "India": "GATS_US_SBO_EXPORT_INDIA",
    "인도": "GATS_US_SBO_EXPORT_INDIA",
    "Mexico": "GATS_US_SBO_EXPORT_MEXICO",
    "멕시코": "GATS_US_SBO_EXPORT_MEXICO",
}


def _year_from_filename(filename: str) -> int | None:
    m = _YEAR_RE.match(filename)
    return int(m.group(1)) if m else None


def _is_reexport_file(filename: str) -> bool:
    return "재수출" in filename


def parse_gats_file(xlsx_path: Path) -> pd.DataFrame:
    """GATS Excel 파일 → 월별 정규화 DataFrame."""
    year = _year_from_filename(xlsx_path.name)
    if year is None:
        raise ValueError(f"[오류] 연도 추출 실패: {xlsx_path.name}")

    is_reexport = _is_reexport_file(xlsx_path.name)
    prefix = "GATS_US_SBO_REEXPORT" if is_reexport else "GATS_US_SBO_EXPORT"

    try:
        df = pd.read_excel(xlsx_path, engine="openpyxl", index_col=0)
    except Exception as e:
        raise RuntimeError(f"[오류] GATS Excel 로드 실패: {xlsx_path}: {e}") from e

    # GATS 파일: 행=국가, 열=월(1~12) 또는 연도 합계
    # 열 이름을 월 번호로 정규화
    month_cols: dict[int, str] = {}
    for col in df.columns:
        col_str = str(col).strip()
        if col_str.isdigit() and 1 <= int(col_str) <= 12:
            month_cols[int(col_str)] = col
        else:
            # 월 이름 매핑 시도
            month_map = {
                "jan": 1, "feb": 2, "mar": 3, "apr": 4,
                "may": 5, "jun": 6, "jul": 7, "aug": 8,
                "sep": 9, "oct": 10, "nov": 11, "dec": 12,
            }
            lower = col_str.lower()[:3]
            if lower in month_map:
                month_cols[month_map[lower]] = col

    records: list[dict] = []
    base = {
        "source_name": "USDA_GATS_XLSX",
        "unit":        "MT",
        "ingested_at": pd.Timestamp.utcnow(),
        "note":        xlsx_path.name,
    }

    for month, col in month_cols.items():
        price_date = date(year, month, 1)

        # 전체 합계 행 탐색 (Total / World / 합계)
        total_keywords = ["total", "world", "합계", "전체"]
        total_val: float | None = None
        for idx_val in df.index:
            if any(kw in str(idx_val).lower() for kw in total_keywords):
                v = pd.to_numeric(df.loc[idx_val, col], errors="coerce")
                if pd.notna(v):
                    total_val = float(v)
                    break

        if total_val is not None:
            records.append({
                **base,
                "price_date":     price_date,
                "indicator_code": f"{prefix}_TOTAL",
                "value":          total_val,
            })

        # 국가별 수출량
        for idx_val in df.index:
            idx_str = str(idx_val).strip()
            for country_key, indicator in TARGET_COUNTRIES.items():
                if country_key.lower() in idx_str.lower():
                    v = pd.to_numeric(df.loc[idx_val, col], errors="coerce")
                    if pd.notna(v):
                        ind = indicator if not is_reexport else indicator.replace("EXPORT", "REEXPORT")
                        records.append({
                            **base,
                            "price_date":     price_date,
                            "indicator_code": ind,
                            "value":          float(v),
                        })
                    break

    return pd.DataFrame(records)


def run(gats_dir: Path = GATS_DIR, output_dir: Path = OUTPUT_DIR) -> None:
    xlsx_files = sorted(gats_dir.glob("*.xlsx"))
    if not xlsx_files:
        print(f"[오류] {gats_dir}에 xlsx 파일 없음.")
        return

    print(f"[C-04] GATS Excel {len(xlsx_files)}개 파일 파싱 시작...")
    all_frames: list[pd.DataFrame] = []

    for f in xlsx_files:
        print(f"  처리 중: {f.name}")
        try:
            df = parse_gats_file(f)
            all_frames.append(df)
            print(f"    → {len(df)}건 추출")
        except Exception as e:
            print(f"    [오류] {f.name}: {e}")

    if not all_frames:
        print("[오류] 추출된 데이터 없음.")
        return

    combined = pd.concat(all_frames, ignore_index=True)
    combined = combined.sort_values(["price_date", "indicator_code"]).reset_index(drop=True)

    out_path = output_dir / "gats_historical.parquet"
    output_dir.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(out_path, index=False)

    print(f"\n[완료] {len(combined)}건 → {out_path}")
    print(f"  기간: {combined['price_date'].min()} ~ {combined['price_date'].max()}")


if __name__ == "__main__":
    run()
