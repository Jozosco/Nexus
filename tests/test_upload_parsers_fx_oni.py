"""승인자 업로드 파서 2종(A-266) — 역수 통일·휴일 이월 제거·코드 분리·as-of 규칙."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from scripts import ingest_enso_oni_xlsx as oni
from scripts import ingest_fx_brl_usd_xlsx as fx
from src.pipeline.asof import attach_asof, revision_status, rule_for


def _write_fx(tmp_path: Path) -> Path:
    p = tmp_path / "fx.xlsx"
    with pd.ExcelWriter(p) as w:
        pd.DataFrame({"Month": [1, 1, 1, 1], "Day": [1, 4, 5, 10],
                      "Price": [0.5, 0.58, 0.60, 0.61], "Open": [0.5, 0.57, 0.59, 0.61],
                      "High": [0.5, 0.585, 0.61, 0.62], "Low": [0.5, 0.565, 0.58, 0.60]}).to_excel(w, sheet_name="2010년", index=False)
        pd.DataFrame({"Month": [1, 1], "Day": [2, 3], "Price": [0.2577, 0.2639], "Open": [0.2577, 0.2578],
                      "High": [0.2577, 0.2643], "Low": [0.2577, 0.2566], "Vol.": ["44.05K", None]}).to_excel(w, sheet_name="2019년", index=False)
    return p


def test_fx_inversion_and_carry_removal(tmp_path):
    df = fx.parse_workbook(_write_fx(tmp_path))
    # 2010-01-01(OHLC 동일 = 휴일 이월)·2010-01-10(일요일) 제거 → 2010-01-04·01-05 + 2019 2행 중 1/2(이월) 제거
    assert set(df["price_date"].dt.strftime("%Y-%m-%d")) == {"2010-01-04", "2010-01-05", "2019-01-03"}
    r = df[df["price_date"] == "2010-01-04"].iloc[0]
    assert abs(r["value"] - 1 / 0.58) < 1e-9 and abs(r["high"] - 1 / 0.565) < 1e-9 and abs(r["low"] - 1 / 0.585) < 1e-9
    assert (df["indicator_code"] == "FX_BRL_USD").all() and (df["unit"] == "BRL/USD").all()
    assert df["volume"].isna().all()                                      # 이월 행(원본 Vol 44.05K)은 제거됨
    assert fx._parse_volume("44.05K") == 44050 and fx._parse_volume("1.2M") == 1_200_000 and fx._parse_volume(None) is None


def test_fx_asof_rule_no_revision():
    r = rule_for("FX_BRL_USD")
    assert r.kind == "immediate" and r.lag_days == 1 and not r.revises
    assert revision_status("FX_BRL_USD") == "n/a"


def test_oni_parser_and_code_separation(tmp_path):
    p = tmp_path / "oni.xlsx"
    with pd.ExcelWriter(p) as w:
        pd.DataFrame({"Year": [2020, 2020, 2026, 2026], "Month": [1, 2, 7, 8],
                      "Index": [0.64, 0.63, 1.8, None]}).to_excel(w, sheet_name="2020s", index=False)
        pd.DataFrame({"Year": [1950], "Month": [1], "Index": [-1.53]}).to_excel(w, sheet_name="1950s", index=False)
    df = oni.parse_workbook(p)
    assert len(df) == 4 and df["price_date"].iloc[0] == pd.Timestamp("1950-01-01")
    assert (df["indicator_code"] == "ENSO_ONI").all()
    assert df["enso_phase"].tolist() == ["La Niña", "El Niño", "El Niño", "El Niño"]
    out = attach_asof(df, source="CLIMATE")
    assert (out["available_at"] >= out["event_time"]).all()
    assert rule_for("ENSO_ONI").revises is False and revision_status("ENSO_ONI") == "n/a"
    assert rule_for("ONI").revises is True                                 # API 계열은 기존 규칙 유지


@pytest.mark.skipif(not Path("data/raw/1950~2026.xlsx").is_file(), reason="업로드 원본 없음")
def test_real_oni_upload_range():
    df = oni.parse_workbook()
    assert df["price_date"].min() == pd.Timestamp("1950-01-01") and df["price_date"].max() == pd.Timestamp("2026-07-01")
    assert len(df) == 919 and df["value"].abs().max() <= 5
