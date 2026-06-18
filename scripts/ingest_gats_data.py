#!/usr/bin/env python3
"""
USDA FAS GATS 수출/재수출 통계 수집 스크립트 (WBS 1.1.42)

입력 폴더 구조 (reorganize_fas_files.yml 실행 후):
  data/raw/USDA/FAS/GATS/
    1507.10/   YYYY년 미국 對국가별 수출량.xlsx (조대두유 수출량)
               YYYY년 미국 對국가별 재수출량.xlsx (조대두유 재수출량)
    1507.90/   YYYY년 미국 對국가별 수출량.xlsx (정제 대두유 수출량)
    export_value_top10/  9개년 미국 XX 수출액_상위 10개국.xlsx (수출액 USD, 대두/대두박/대두유)

출력:
  data/raw/gats_quantity_historical.parquet   — 수출량·재수출량 (MT)
  data/raw/gats_value_historical.parquet      — 수출액 상위 10개국 (USD, 연간)

HS 코드 구분:
  1507.10: 조대두유 (crude)   → 지표 접두사 GATS_US_SBO_
  1507.90: 정제 대두유 (refined) → 지표 접두사 GATS_US_RSBO_

수집 지표 (1507.10):
  GATS_US_SBO_EXPORT_TOTAL      : 전체 수출량 (MT)
  GATS_US_SBO_EXPORT_KOREA      : 미국→한국 수출량 (MT)  ← G1 Phase A 핵심 피처
  GATS_US_SBO_EXPORT_CHINA      : 미국→중국 수출량 (MT)
  GATS_US_SBO_EXPORT_INDIA      : 미국→인도 수출량 (MT)
  GATS_US_SBO_EXPORT_MEXICO     : 미국→멕시코 수출량 (MT)
  GATS_US_SBO_REEXPORT_TOTAL    : 전체 재수출량 (MT)
  GATS_US_SBO_REEXPORT_KOREA    : 미국→한국 재수출량 (MT)

수집 지표 (1507.90):
  GATS_US_RSBO_EXPORT_TOTAL     : 전체 수출량 (MT)
  GATS_US_RSBO_EXPORT_KOREA     : 미국→한국 수출량 (MT)
  GATS_US_RSBO_EXPORT_CHINA     : 미국→중국 수출량 (MT)

수집 지표 (export_value_top10):
  GATS_US_SOY_EXPORT_VALUE      : 대두(HS1201) 수출액 (USD) — 연간, 상위 10개국
  GATS_US_SBM_EXPORT_VALUE      : 대두박(HS2304) 수출액 (USD) — 연간, 상위 10개국
  GATS_US_SBO_EXPORT_VALUE      : 대두유(HS1507) 수출액 (USD) — 연간, 상위 10개국
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pandas as pd

GATS_DIR   = Path("data/raw/USDA/FAS/GATS")
OUTPUT_DIR = Path("data/raw")

_YEAR_RE  = re.compile(r"^(\d{4})년")
_9YR_RE   = re.compile(r"9개년.*수출액", re.IGNORECASE)

TARGET_COUNTRIES: dict[str, str] = {
    "korea":       "KOREA",
    "south korea": "KOREA",
    "한국":        "KOREA",
    "china":       "CHINA",
    "중국":        "CHINA",
    "india":       "INDIA",
    "인도":        "INDIA",
    "mexico":      "MEXICO",
    "멕시코":      "MEXICO",
    "japan":       "JAPAN",
    "일본":        "JAPAN",
    "colombia":    "COLOMBIA",
    "콜롬비아":    "COLOMBIA",
}

_VALUE_COMMODITY_KEYWORDS: dict[str, str] = {
    "대두유": "SBO",
    "soybean oil": "SBO",
    "대두박": "SBM",
    "soybean meal": "SBM",
    "대두":   "SOY",
    "soybean": "SOY",
}


def _year_from_filename(filename: str) -> int | None:
    m = _YEAR_RE.match(filename)
    return int(m.group(1)) if m else None


def _is_reexport_file(filename: str) -> bool:
    return "재수출" in filename


def parse_quantity_file(xlsx_path: Path, hs_prefix: str) -> pd.DataFrame:
    """수출량/재수출량 Excel → 월별 정규화 DataFrame.

    hs_prefix: 'GATS_US_SBO_' (1507.10) 또는 'GATS_US_RSBO_' (1507.90)
    """
    year = _year_from_filename(xlsx_path.name)
    if year is None:
        raise ValueError(f"[오류] 연도 추출 실패: {xlsx_path.name}")

    is_reexport = _is_reexport_file(xlsx_path.name)
    flow_tag = "REEXPORT" if is_reexport else "EXPORT"

    try:
        df = pd.read_excel(xlsx_path, engine="openpyxl", index_col=0)
    except Exception as e:
        raise RuntimeError(f"[오류] GATS Excel 로드 실패: {xlsx_path}: {e}") from e

    month_cols: dict[int, object] = {}
    for col in df.columns:
        col_str = str(col).strip()
        if col_str.isdigit() and 1 <= int(col_str) <= 12:
            month_cols[int(col_str)] = col
        else:
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

        total_val: float | None = None
        for idx_val in df.index:
            if any(kw in str(idx_val).lower() for kw in ["total", "world", "합계", "전체"]):
                v = pd.to_numeric(df.loc[idx_val, col], errors="coerce")
                if pd.notna(v):
                    total_val = float(v)
                    break

        if total_val is not None:
            records.append({
                **base,
                "price_date":     price_date,
                "indicator_code": f"{hs_prefix}{flow_tag}_TOTAL",
                "value":          total_val,
            })

        for idx_val in df.index:
            idx_str = str(idx_val).strip().lower()
            for country_key, country_tag in TARGET_COUNTRIES.items():
                if country_key in idx_str:
                    v = pd.to_numeric(df.loc[idx_val, col], errors="coerce")
                    if pd.notna(v):
                        records.append({
                            **base,
                            "price_date":     price_date,
                            "indicator_code": f"{hs_prefix}{flow_tag}_{country_tag}",
                            "value":          float(v),
                        })
                    break

    return pd.DataFrame(records)


def parse_value_file(xlsx_path: Path) -> pd.DataFrame:
    """9개년 수출액 상위 10개국 Excel → 연간 정규화 DataFrame.

    파일: '9개년 미국 XX 수출액_상위 10개국.xlsx'
    형식: 행=국가, 열=연도 (또는 행=연도, 열=국가)
    단위: USD (수출액)
    """
    commodity_tag: str | None = None
    fname_lower = xlsx_path.name.lower()
    for kw, tag in _VALUE_COMMODITY_KEYWORDS.items():
        if kw in fname_lower:
            commodity_tag = tag
            break
    if commodity_tag is None:
        print(f"  [건너뜀] 품목 식별 불가: {xlsx_path.name}")
        return pd.DataFrame()

    try:
        df = pd.read_excel(xlsx_path, engine="openpyxl", index_col=0)
    except Exception as e:
        raise RuntimeError(f"[오류] 수출액 Excel 로드 실패: {xlsx_path}: {e}") from e

    indicator_code = f"GATS_US_{commodity_tag}_EXPORT_VALUE"

    # 연도 컬럼 탐색 (열=연도)
    year_col_map: list[tuple[object, int]] = []
    for col in df.columns:
        try:
            y = int(str(col).strip().split("/")[0])
            if 2000 <= y <= 2040:
                year_col_map.append((col, y))
        except ValueError:
            pass

    # 전치 시도 (행=연도인 경우)
    if not year_col_map:
        df = df.T
        for col in df.columns:
            try:
                y = int(str(col).strip().split("/")[0])
                if 2000 <= y <= 2040:
                    year_col_map.append((col, y))
            except ValueError:
                pass

    records: list[dict] = []
    base = {
        "source_name":    "USDA_GATS_VALUE_XLSX",
        "unit":           "USD",
        "ingested_at":    pd.Timestamp.utcnow(),
        "note":           xlsx_path.name,
        "indicator_code": indicator_code,
    }

    for col, year in year_col_map:
        price_date = date(year, 10, 1)  # 마케팅연도 시작월

        total_val: float | None = None
        for idx_val in df.index:
            if any(kw in str(idx_val).lower() for kw in ["total", "world", "합계", "전체"]):
                v = pd.to_numeric(df.loc[idx_val, col], errors="coerce")
                if pd.notna(v):
                    total_val = float(v)
                    break

        # 합계 행이 없으면 수치 합산
        if total_val is None:
            series = pd.to_numeric(df[col], errors="coerce").dropna()
            if not series.empty:
                total_val = float(series.sum())

        if total_val is not None and total_val > 0:
            records.append({**base, "price_date": price_date, "value": total_val})

    return pd.DataFrame(records)


def run(gats_dir: Path = GATS_DIR, output_dir: Path = OUTPUT_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── 수출량 파싱 (1507.10 + 1507.90) ─────────────────────────────────────
    quantity_frames: list[pd.DataFrame] = []

    for hs_sub, hs_prefix in [("1507.10", "GATS_US_SBO_"), ("1507.90", "GATS_US_RSBO_")]:
        sub_dir = gats_dir / hs_sub
        xlsx_files = sorted(sub_dir.glob("*.xlsx")) if sub_dir.exists() else []
        if not xlsx_files:
            print(f"[경고] {sub_dir} — xlsx 파일 없음. (파일 업로드 후 재실행)")
            continue

        print(f"[C-04] GATS {hs_sub}: {len(xlsx_files)}개 파일 파싱...")
        for f in xlsx_files:
            print(f"  처리 중: {f.name}")
            try:
                df = parse_quantity_file(f, hs_prefix)
                quantity_frames.append(df)
                print(f"    → {len(df)}건 추출")
            except Exception as e:
                print(f"    [오류] {f.name}: {e}")

    if quantity_frames:
        qty_combined = pd.concat(quantity_frames, ignore_index=True)
        qty_combined = qty_combined.sort_values(["price_date", "indicator_code"]).reset_index(drop=True)
        qty_path = output_dir / "gats_quantity_historical.parquet"
        qty_combined.to_parquet(qty_path, index=False)
        print(f"\n[완료] 수출량: {len(qty_combined)}건 → {qty_path}")
        print(f"  기간: {qty_combined['price_date'].min()} ~ {qty_combined['price_date'].max()}")
        print(f"  지표: {sorted(qty_combined['indicator_code'].unique())}")
    else:
        print("[경고] 수출량 데이터 없음.")

    # ── 수출액 파싱 (export_value_top10) ────────────────────────────────────
    value_dir = gats_dir / "export_value_top10"
    value_files = sorted(value_dir.glob("*.xlsx")) if value_dir.exists() else []

    if not value_files:
        print(f"[경고] {value_dir} — xlsx 파일 없음.")
    else:
        print(f"\n[C-04] GATS export_value_top10: {len(value_files)}개 파일 파싱...")
        value_frames: list[pd.DataFrame] = []
        for f in value_files:
            print(f"  처리 중: {f.name}")
            try:
                df = parse_value_file(f)
                value_frames.append(df)
                print(f"    → {len(df)}건 추출")
            except Exception as e:
                print(f"    [오류] {f.name}: {e}")

        if value_frames:
            val_combined = pd.concat(value_frames, ignore_index=True)
            val_combined = val_combined.sort_values(["price_date", "indicator_code"]).reset_index(drop=True)
            val_path = output_dir / "gats_value_historical.parquet"
            val_combined.to_parquet(val_path, index=False)
            print(f"\n[완료] 수출액: {len(val_combined)}건 → {val_path}")
            print(f"  기간: {val_combined['price_date'].min()} ~ {val_combined['price_date'].max()}")
            print(f"  지표: {sorted(val_combined['indicator_code'].unique())}")


if __name__ == "__main__":
    run()
