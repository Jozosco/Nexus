#!/usr/bin/env python3
"""
USDA FAS GATS 수출/재수출 통계 수집 스크립트 (WBS 1.1.42)

입력 폴더 (reorganize_fas_files.yml 실행 후):
  data/raw/USDA/FAS/GATS/
    1507.10/   YYYY년 미국 對국가별 수출량.xlsx / 재수출량.xlsx (조대두유)
    1507.90/   YYYY년 미국 對국가별 수출량.xlsx (정제 대두유)
    export_value_top10/  9개년 미국 XX 수출액_상위 10개국.xlsx (USD)

출력:
  data/raw/gats_quantity_historical.parquet  — 월별 수출/재수출 물량 (MT)
  data/raw/gats_value_historical.parquet     — 연간 수출액 (USD)

실제 수출량 파일 구조 (A-052):
  row0 = 월 밴드(January..December, Total) — 각 밴드 3컬럼
  row1 = 하위 헤더 [Value, Qty, Unit Value] (밴드별 반복)
  col0 = Country, col1 = Unit of Measure (1507.90은 col1=Product, col2=Unit)
  → Qty 컬럼이 수출 물량(MT). 'World Total' 행 = 전체.

HS 접두사: 1507.10 → GATS_US_SBO_ , 1507.90 → GATS_US_RSBO_
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pandas as pd

GATS_DIR   = Path("data/raw/USDA/FAS/GATS")
OUTPUT_DIR = Path("data/raw")

_YEAR_RE = re.compile(r"^(\d{4})")

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}

# 행 라벨(국가) → 지표 국가 태그
TARGET_COUNTRIES = {
    "world total": "TOTAL", "world": "TOTAL",
    "korea, south": "KOREA", "south korea": "KOREA", "korea": "KOREA",
    "china": "CHINA", "india": "INDIA", "mexico": "MEXICO",
    "japan": "JAPAN", "colombia": "COLOMBIA", "canada": "CANADA",
}

_VALUE_COMMODITY = {"대두유": "SBO", "대두박": "SBM", "대두": "SOY"}


def _year_from_filename(name: str) -> int | None:
    m = _YEAR_RE.match(name.strip())
    return int(m.group(1)) if m else None


def parse_quantity_file(xlsx_path: Path, hs_prefix: str) -> pd.DataFrame:
    """수출량/재수출량 파일 → 월별 물량(Qty, MT) 정규화."""
    year = _year_from_filename(xlsx_path.name)
    if year is None:
        raise ValueError(f"[오류] 연도 추출 실패: {xlsx_path.name}")
    flow = "REEXPORT" if "재수출" in xlsx_path.name else "EXPORT"

    raw = pd.read_excel(xlsx_path, header=None, engine="openpyxl")
    if raw.shape[0] < 3:
        return pd.DataFrame()

    # 밴드(월/Total) 라벨을 forward-fill 하여 각 컬럼이 속한 밴드 식별
    band = raw.iloc[0].astype(str).where(lambda s: s != "nan").ffill()
    sub  = raw.iloc[1].astype(str)

    # Qty 컬럼만 추출: (밴드 라벨, 컬럼 인덱스)
    qty_cols: list[tuple[str, int]] = []
    for i in range(raw.shape[1]):
        if sub.iat[i].strip().lower() == "qty":
            qty_cols.append((str(band.iat[i]).strip().lower(), i))

    base = {
        "source_name": "USDA_GATS_XLSX",
        "unit":        "MT",
        "ingested_at": pd.Timestamp.utcnow(),
        "note":        xlsx_path.name,
    }
    records: list[dict] = []

    for r in range(2, raw.shape[0]):
        country_raw = str(raw.iat[r, 0]).strip().lower()
        tag = TARGET_COUNTRIES.get(country_raw)
        if tag is None:
            continue
        for band_label, ci in qty_cols:
            month = _MONTHS.get(band_label)
            if month is None:        # 'total' 밴드는 월별 합산이라 생략(중복 방지)
                continue
            qty = pd.to_numeric(raw.iat[r, ci], errors="coerce")
            if pd.notna(qty) and qty != 0:
                records.append({**base, "price_date": date(year, month, 1),
                                "indicator_code": f"{hs_prefix}{flow}_{tag}",
                                "value": float(qty)})

    return pd.DataFrame(records)


def parse_value_file(xlsx_path: Path) -> pd.DataFrame:
    """9개년 수출액 파일 → 연간 총수출액(USD). 행=국가, row1=연도."""
    tag = next((t for kw, t in _VALUE_COMMODITY.items()
                if kw in xlsx_path.name.lower()), None)
    if tag is None:
        print(f"  [건너뜀] 품목 식별 불가: {xlsx_path.name}")
        return pd.DataFrame()

    raw = pd.read_excel(xlsx_path, header=None, engine="openpyxl")
    # 연도 행 탐색 (값이 2000~2040 정수인 행)
    year_row_idx, year_cols = None, {}
    for r in range(min(5, raw.shape[0])):
        cols = {}
        for c in range(raw.shape[1]):
            v = pd.to_numeric(raw.iat[r, c], errors="coerce")
            if pd.notna(v) and 2000 <= v <= 2040:
                cols[c] = int(v)
        if len(cols) >= 3:
            year_row_idx, year_cols = r, cols
            break
    if not year_cols:
        print(f"  [경고] {xlsx_path.name}: 연도 행 없음")
        return pd.DataFrame()

    base = {
        "source_name":    "USDA_GATS_VALUE_XLSX",
        "unit":           "USD",
        "ingested_at":    pd.Timestamp.utcnow(),
        "note":           xlsx_path.name,
        "indicator_code": f"GATS_US_{tag}_EXPORT_VALUE",
    }
    records: list[dict] = []
    for c, yr in year_cols.items():
        col_vals = pd.to_numeric(raw.iloc[year_row_idx + 1:, c], errors="coerce").dropna()
        total = float(col_vals.sum())   # 상위 10개국 합산
        if total > 0:
            records.append({**base, "price_date": date(yr, 10, 1), "value": total})
    return pd.DataFrame(records)


def run(gats_dir: Path = GATS_DIR, output_dir: Path = OUTPUT_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── 수출량 (1507.10 + 1507.90) ──────────────────────────────────────────
    quantity_frames: list[pd.DataFrame] = []
    for hs_sub, prefix in [("1507.10", "GATS_US_SBO_"), ("1507.90", "GATS_US_RSBO_")]:
        sub_dir = gats_dir / hs_sub
        files = sorted(sub_dir.glob("*.xlsx")) if sub_dir.exists() else []
        if not files:
            print(f"[경고] {sub_dir} — xlsx 없음.")
            continue
        print(f"[C-04] GATS {hs_sub}: {len(files)}개 파일 파싱...")
        for f in files:
            print(f"  처리 중: {f.name}")
            try:
                df = parse_quantity_file(f, prefix)
                if not df.empty:
                    quantity_frames.append(df)
                print(f"    → {len(df)}건")
            except Exception as e:
                print(f"    [오류] {f.name}: {e}")

    if quantity_frames:
        qty = pd.concat(quantity_frames, ignore_index=True)
        qty = qty.sort_values(["price_date", "indicator_code"]).reset_index(drop=True)
        qpath = output_dir / "gats_quantity_historical.parquet"
        qty.to_parquet(qpath, index=False)
        print(f"\n[완료] 수출량 {len(qty)}건 → {qpath}")
        print(f"  기간: {qty['price_date'].min()} ~ {qty['price_date'].max()}")
        print(f"  지표: {sorted(qty['indicator_code'].unique())}")
    else:
        print("[경고] 수출량 데이터 없음.")

    # ── 수출액 (export_value_top10) ─────────────────────────────────────────
    vdir = gats_dir / "export_value_top10"
    vfiles = sorted(vdir.glob("*.xlsx")) if vdir.exists() else []
    if not vfiles:
        print(f"[경고] {vdir} — xlsx 없음.")
        return
    print(f"\n[C-04] export_value_top10: {len(vfiles)}개 파일 파싱...")
    value_frames: list[pd.DataFrame] = []
    for f in vfiles:
        print(f"  처리 중: {f.name}")
        try:
            df = parse_value_file(f)
            if not df.empty:
                value_frames.append(df)
            print(f"    → {len(df)}건")
        except Exception as e:
            print(f"    [오류] {f.name}: {e}")

    if value_frames:
        val = pd.concat(value_frames, ignore_index=True)
        val = val.sort_values(["price_date", "indicator_code"]).reset_index(drop=True)
        vpath = output_dir / "gats_value_historical.parquet"
        val.to_parquet(vpath, index=False)
        print(f"\n[완료] 수출액 {len(val)}건 → {vpath}")
        print(f"  지표: {sorted(val['indicator_code'].unique())}")


if __name__ == "__main__":
    run()
