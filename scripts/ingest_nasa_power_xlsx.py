#!/usr/bin/env python3
"""
NASA POWER Agroclimatology 히스토리 xlsx 수집·정형화 (WBS 1.1.47 · A-066)

배경: 조정자가 주요 생산국 3대 산지의 9개년(2017~2025) 농업기상 데이터를 수동 업로드.
      (NASA POWER Single Point · Standard · Monthly · community=AG — 선별 파라미터)

입력: data/raw/NASA Power/Agroclimatology/{Country}/*.xlsx
      (폴백: data/raw/*Agr*climatology*.xlsx — 재정리 전)
      파일명: '{YYYY}~{YYYY}_{Region}_Agroclimatology Dataset(s).xlsx' (Agri/Agro·단복수 허용)
      시트: '{YYYY}년' · 메타 5행 후 [PARAMETER | Jan..Dec | Avg] 와이드 표

출력: data/raw/nasa_power_agroclimatology_historical.parquet (롱포맷)
      price_date, region, country, role(grow/crush), indicator_code({PARAM}_{Region}),
      parameter, value, source_name, ingested_at

의존성: pandas >= 2.0 · openpyxl
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

NASA_ROOT = Path("data/raw/NASA Power/Agroclimatology")
RAW_ROOT  = Path("data/raw")
OUT_PATH  = Path("data/raw/nasa_power_agroclimatology_historical.parquet")

# 지역 → (국가, 역할) — 조정자 명세 (grow=재배·crush=압착 산지)
REGION_META: dict[str, tuple[str, str]] = {
    "Illinois":        ("United States", "grow_crush"),
    "Iowa":            ("United States", "grow_crush"),
    "Indiana":         ("United States", "grow"),
    "MatoGrosso":      ("Brazil",        "grow_crush"),
    "Parana":          ("Brazil",        "grow_crush"),
    "MatoGrossodoSul": ("Brazil",        "grow"),
    "Cordoba":         ("Argentina",     "grow"),
    "SantaFe":         ("Argentina",     "crush"),
    "Buenos Aires":    ("Argentina",     "grow"),
    "Heilongjiang":    ("China",         "grow"),
    "Shandong":        ("China",         "crush"),
    "Jiangsu":         ("China",         "crush"),
}

_MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
           "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
_YEAR_RE = re.compile(r"(\d{4})")


def _region_from_name(stem: str) -> str | None:
    parts = stem.split("_")
    return parts[1].strip() if len(parts) > 1 else None


def _slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")


def parse_nasa_file(path: Path) -> pd.DataFrame:
    region = _region_from_name(path.stem)
    if region is None or region not in REGION_META:
        # 공백 제거 매칭 재시도 (예: 'Buenos Aires')
        region = next((r for r in REGION_META if _slug(r).lower() in _slug(path.stem).lower()), None)
    if region is None:
        print(f"  [건너뜀] 지역 미매칭: {path.name}")
        return pd.DataFrame()
    country, role = REGION_META[region]

    try:
        xl = pd.ExcelFile(path)
    except Exception as e:
        print(f"  [오류] 열기 실패 {path.name}: {e}")
        return pd.DataFrame()

    records: list[dict] = []
    for sheet in xl.sheet_names:
        ym = _YEAR_RE.search(str(sheet))
        if not ym:
            continue
        year = int(ym.group(1))
        raw = xl.parse(sheet, header=None)
        # 헤더 행 탐지: 0열이 'PARAMETER'
        hdr = None
        for i in range(min(12, len(raw))):
            if str(raw.iloc[i, 0]).strip().upper() == "PARAMETER":
                hdr = i
                break
        if hdr is None:
            continue
        month_cols = {}
        for c in range(1, raw.shape[1]):
            key = str(raw.iloc[hdr, c]).strip().lower()[:3]
            if key in _MONTHS:
                month_cols[c] = _MONTHS[key]
        for r in range(hdr + 1, len(raw)):
            param = str(raw.iloc[r, 0]).strip()
            if not param or param.lower() == "nan":
                continue
            for c, month in month_cols.items():
                val = pd.to_numeric(raw.iloc[r, c], errors="coerce")
                if pd.isna(val) or float(val) <= -999:
                    continue
                records.append({
                    "price_date":     pd.Timestamp(year=year, month=month, day=1),
                    "region":         region,
                    "country":        country,
                    "role":           role,
                    "parameter":      param,
                    "indicator_code": f"{param}_{_slug(region)}",
                    "value":          float(val),
                    "source_name":    "NASA_POWER_xlsx",
                    "ingested_at":    pd.Timestamp.now("UTC"),
                })
    return pd.DataFrame(records)


def _iter_files() -> list[Path]:
    if NASA_ROOT.exists():
        files = sorted(NASA_ROOT.rglob("*.xlsx"))
        if files:
            return files
    return sorted(p for p in RAW_ROOT.glob("*.xlsx")
                  if re.search(r"agr[io]climatology", p.name, re.IGNORECASE))


def run() -> None:
    files = _iter_files()
    if not files:
        print("[경고] NASA POWER xlsx 없음.")
        return
    print(f"[C-03] NASA POWER Agroclimatology {len(files)}개 파일 정형화...")
    frames = []
    for f in files:
        df = parse_nasa_file(f)
        if not df.empty:
            frames.append(df)
            print(f"  [OK] {f.name}: {len(df):,}행 ({df['parameter'].nunique()}파라미터)")
    if not frames:
        print("[경고] 정형화 데이터 없음.")
        return
    combined = pd.concat(frames, ignore_index=True).sort_values(
        ["country", "region", "price_date", "parameter"]).reset_index(drop=True)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(OUT_PATH, index=False)
    print(f"\n[완료] → {OUT_PATH}")
    print(f"  총 {len(combined):,}행 · {combined['region'].nunique()}지역 · "
          f"{combined['parameter'].nunique()}파라미터 · "
          f"{combined['price_date'].min().date()}~{combined['price_date'].max().date()}")
    for country, g in combined.groupby("country"):
        print(f"  - {country}: {sorted(g['region'].unique())}")


if __name__ == "__main__":
    run()
