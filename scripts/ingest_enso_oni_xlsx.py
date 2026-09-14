"""승인자 업로드 ENSO ONI 1950~2026(NOAA PSL · Niño3.4 SST 5°N–5°S, 170°W–120°W) → parquet (2026-09-14 · A-266).

입력: data/raw/1950~2026.xlsx — 10년 시트 '1950s'~'2020s', 열 Year | Month | Index(°C 편차, 월 단위).
코드: ENSO_ONI — API 수집 계열(NOAA CPC oni.ascii.txt → 코드 ONI)과 **분리**한다. 같은 코드에 두 vintage
      (PSL 기준기간 이동평균 vs CPC)를 섞으면 마트 (지표, event_time) 값충돌로 하드 실패한다(D-033).
      소비자(준비도·유사 시기·신뢰도·브리프 스냅샷)는 이미 ENSO_ONI 후보를 본다.
규약: price_date = 해당 월 1일(업로드본이 이미 달력월) · enso_phase(≥0.5 El Niño / ≤−0.5 La Niña / Neutral) ·
      ±5 물리 가드(A-179) · 미래 빈 행 제거. 원본 xlsx는 읽기 전용(A-184).
출력: data/raw/enso_oni_historical.parquet
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

_sys_root = Path(__file__).resolve().parents[1]
if str(_sys_root) not in sys.path:
    sys.path.insert(0, str(_sys_root))
from src.pipeline.asof import attach_asof  # noqa: E402

SRC_PATH = Path("data/raw/1950~2026.xlsx")
OUT_PATH = Path("data/raw/enso_oni_historical.parquet")
INDICATOR = "ENSO_ONI"
SOURCE_NAME = "NOAA_PSL_upload"
PHYSICAL_ABS_MAX = 5.0


def _phase(v: float) -> str:
    if v >= 0.5:
        return "El Niño"
    if v <= -0.5:
        return "La Niña"
    return "Neutral"


def parse_workbook(path: Path = SRC_PATH) -> pd.DataFrame:
    xl = pd.ExcelFile(path)
    frames = []
    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        if not {"Year", "Month", "Index"}.issubset(df.columns):
            print(f"  [건너뜀] {sheet}: Year/Month/Index 열 없음")
            continue
        sub = pd.DataFrame({
            "year": pd.to_numeric(df["Year"], errors="coerce"),
            "month": pd.to_numeric(df["Month"], errors="coerce"),
            "value": pd.to_numeric(df["Index"], errors="coerce"),
        }).dropna()
        frames.append(sub)
    if not frames:
        raise SystemExit(f"[오류] {path}: 유효 시트 없음")
    out = pd.concat(frames, ignore_index=True)
    bad = out["value"].abs() > PHYSICAL_ABS_MAX
    if bad.any():
        print(f"[경고] 물리 범위(±{PHYSICAL_ABS_MAX}) 밖 {int(bad.sum())}건 제외 — 단위/열 혼입 의심")
        out = out[~bad]
    out["price_date"] = pd.to_datetime(dict(year=out["year"].astype(int), month=out["month"].astype(int), day=1))
    out = out.sort_values("price_date").drop_duplicates("price_date", keep="last")
    out["indicator_code"] = INDICATOR
    out["unit"] = "°C anomaly"
    out["enso_phase"] = out["value"].map(_phase)
    out["region"] = "Niño3.4 (5N-5S, 170W-120W)"
    out["source_name"] = SOURCE_NAME
    out["note"] = "승인자 업로드 NOAA PSL ONI 1950~ — CPC 계열(ONI)과 별도 vintage, 코드 분리"
    out["ingested_at"] = pd.Timestamp.now("UTC")
    return out[["price_date", "indicator_code", "value", "unit", "enso_phase", "region",
                "source_name", "note", "ingested_at"]].reset_index(drop=True)


def run() -> None:
    if not SRC_PATH.is_file():
        print(f"[경고] {SRC_PATH} 없음 — 건너뜀")
        return
    df = parse_workbook(SRC_PATH)
    df = attach_asof(df, source="CLIMATE")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_PATH, index=False)
    print(f"[완료] {INDICATOR} {len(df):,}개월 {df['price_date'].min().date()}~{df['price_date'].max().date()} "
          f"· 최신 {df['value'].iloc[-1]:+.2f}({df['enso_phase'].iloc[-1]}) → {OUT_PATH}")


if __name__ == "__main__":
    run()
