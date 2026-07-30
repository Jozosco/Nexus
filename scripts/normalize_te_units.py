#!/usr/bin/env python3
"""
TE 상품가격 단위 정규화 → USD/MT (설계결정 D8 · WBS 1.1.50)

D8(조정자 확정): USD/MT 외 단위는 **해당 일/월 환율**을 적용해 변환한다.
 - 순수 단위 환산(통화 무관): bushel·lb → MT   (즉시 변환 가능)
 - 통화 환산: MYR·EUR·INR·CAD → USD            (FRED 환율 시계열 필요 — economic parquet)
   환율 미확보 시 해당 행은 converted=False로 보존(왜곡 금지, D4 원칙과 일관).

입력: data/raw/te_commodities_historical.parquet
      data/raw/economic_indicators_*.parquet (환율: DEXUSEU·DEXCAUS·DEXINUS·DEXMAUS 등)
출력: data/raw/te_commodities_usd_mt.parquet
      (원본 컬럼 + value_usd_mt · fx_rate · fx_series · converted)

환산 계수 (USDA 표준):
  대두/밀 60 lb/bu → USD/bu × 36.7437 = USD/MT
  옥수수 56 lb/bu → × 39.3683
  설탕 USc/lb → × 22.0462 = USD/MT
  해바라기유 INR/10kg → × 100 = INR/MT → ÷ USDINR
"""
from __future__ import annotations

import glob
from pathlib import Path

import pandas as pd

TE_PARQUET = Path("data/raw/te_commodities_historical.parquet")
OUT_PATH   = Path("data/raw/te_commodities_usd_mt.parquet")

# commodity → (곱셈 계수, 필요 FX FRED 시리즈 또는 None, FX 방향 'multiply'|'divide')
# FX 시리즈 의미: DEXUSEU=USD per EUR(곱), DEXCAUS=CAD per USD(나눗셈),
#                 DEXINUS=INR per USD(나눗셈), DEXMAUS=MYR per USD(나눗셈)
RULES: dict[str, tuple[float, str | None, str]] = {
    "Soybeans":      (36.7437, None, "none"),          # USD/bu → USD/MT
    "Wheat":         (36.7437, None, "none"),
    "Corn":          (39.3683, None, "none"),
    "Sugar":         (22.0462, None, "none"),          # USc/lb → USD/MT
    "Palm Oil":      (1.0, "DEXMAUS", "divide"),       # MYR/MT ÷ (MYR per USD)
    "Rapeseed":      (1.0, "DEXUSEU", "multiply"),     # EUR/ton × (USD per EUR)
    "Canola":        (1.0, "DEXCAUS", "divide"),       # CAD/MT ÷ (CAD per USD)
    "Sunflower Oil": (100.0, "DEXINUS", "divide"),     # INR/10kg×100=INR/MT ÷ (INR per USD)
}


def _load_fx() -> pd.DataFrame:
    """economic parquet에서 환율 시계열 로드 (월평균으로 리샘플)."""
    frames = []
    for f in glob.glob("data/raw/economic_indicators_*.parquet"):
        try:
            df = pd.read_parquet(f)
            if {"indicator_code", "price_date", "value"}.issubset(df.columns):
                frames.append(df[["price_date", "indicator_code", "value"]])
        except Exception:
            continue
    if not frames:
        return pd.DataFrame()
    fx = pd.concat(frames, ignore_index=True).drop_duplicates()
    fx["price_date"] = pd.to_datetime(fx["price_date"])
    fx["ym"] = fx["price_date"].dt.to_period("M")
    return fx.groupby(["ym", "indicator_code"])["value"].mean().reset_index()


def run() -> None:
    if not TE_PARQUET.exists():
        print("[경고] TE parquet 없음 — ingest_te_xlsx.py 먼저 실행")
        return
    te = pd.read_parquet(TE_PARQUET)
    fx = _load_fx()
    fx_map: dict[tuple, float] = {}
    if not fx.empty:
        fx_map = {(r["ym"], r["indicator_code"]): r["value"] for _, r in fx.iterrows()}

    te["ym"] = pd.to_datetime(te["price_date"]).dt.to_period("M")
    vals, rates, series_used, converted = [], [], [], []
    for _, row in te.iterrows():
        rule = RULES.get(str(row.get("commodity", "")))
        if rule is None:
            vals.append(None); rates.append(None); series_used.append(None); converted.append(False)
            continue
        factor, fx_series, mode = rule
        v = row["value"] * factor
        if fx_series is None:
            vals.append(v); rates.append(None); series_used.append(None); converted.append(True)
            continue
        rate = fx_map.get((row["ym"], fx_series))
        if rate is None or rate <= 0:
            vals.append(None); rates.append(None); series_used.append(fx_series); converted.append(False)
            continue
        v = v * rate if mode == "multiply" else v / rate
        vals.append(v); rates.append(rate); series_used.append(fx_series); converted.append(True)

    te["value_usd_mt"] = vals
    te["fx_rate"] = rates
    te["fx_series"] = series_used
    te["converted"] = converted
    te = te.drop(columns=["ym"])
    te.to_parquet(OUT_PATH, index=False)

    n_ok = sum(converted)
    n_fx_missing = sum(1 for c, s in zip(converted, series_used) if not c and s)
    print(f"[완료] → {OUT_PATH}")
    print(f"  변환 성공 {n_ok:,} · 환율 미확보 보류 {n_fx_missing:,} (D4 원칙: 왜곡 금지·보존)")
    if n_fx_missing:
        missing = sorted({s for c, s in zip(converted, series_used) if not c and s})
        print(f"  [정보] 필요 환율 시리즈: {missing} — economic 커넥터(include_api=true) 실행 시 충족")


if __name__ == "__main__":
    run()
