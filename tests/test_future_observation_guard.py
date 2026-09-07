"""관측 계열 미래 행 제거 · DQ_EXPECTED 선택 표식 회귀 테스트 (A-246)."""
from __future__ import annotations

from datetime import date

import pandas as pd

from src.pipeline.asof import drop_future_observations


def _df(dates, code="BDI"):
    return pd.DataFrame({"price_date": pd.to_datetime(dates), "value": 1.0, "indicator_code": code})


def test_future_rows_dropped_and_past_kept():
    today = date(2026, 9, 7)
    df = pd.concat([_df(["2026-09-05", "2026-09-07"]), _df(["2026-09-08", "2026-10-06"], "CPO_USD_MT")])
    out = drop_future_observations(df, "t", today=today)
    assert len(out) == 2 and out["price_date"].max() == pd.Timestamp(today)


def test_no_future_rows_is_noop():
    df = _df(["2026-09-01", "2026-09-02"])
    out = drop_future_observations(df, "t", today=date(2026, 9, 7))
    assert len(out) == 2


def test_missing_price_date_column_passthrough():
    df = pd.DataFrame({"value": [1, 2]})
    assert drop_future_observations(df, "t", today=date(2026, 9, 7)).equals(df)


def test_dq_expected_optional_marker_parsing():
    env = "economic_indicators,crop_data?,commodity_data"
    parsed = [(p.rstrip("?"), p.endswith("?")) for p in env.split(",")]
    assert parsed == [("economic_indicators", False), ("crop_data", True), ("commodity_data", False)]
