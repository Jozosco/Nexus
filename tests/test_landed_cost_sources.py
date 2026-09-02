"""도착가 밴드 원천 합집합 회귀 테스트 (A-245 — 런 #87 실측 결함)."""
from __future__ import annotations

import pandas as pd

from src.forecasting.landed_cost import _bulk_monthly, combine_customs_sources


def _rows(months, country, kg=200_000, usd=250_000):
    return pd.DataFrame({
        "price_date": pd.to_datetime(months), "imp_usd": usd, "imp_kg": kg, "country": country,
    })


def test_union_keeps_history_and_prefers_api_months():
    """API 당년 7개월 + GW 2010~ 히스토리 → 공통 월이 0건이 아니라 전 기간이 남는다."""
    api = _bulk_monthly([_rows(pd.date_range("2026-01-01", periods=7, freq="MS"), "아르헨티나")])
    gw = _bulk_monthly([_rows(pd.date_range("2024-01-01", periods=30, freq="MS"), "Argentina")])
    combined, label = combine_customs_sources(api, gw)
    months = combined["price_date"].nunique()
    assert months == 30 + 7 - 6        # 2026-01~06 겹침은 API만 남음(이중 합산 없음)
    assert "API 당년 7개월" in label and "GW" in label
    overlap = combined[combined["price_date"] == pd.Timestamp("2026-03-01")]
    assert overlap["country"].tolist() == ["아르헨티나"]


def test_gw_only_when_api_absent():
    gw = _bulk_monthly([_rows(pd.date_range("2025-01-01", periods=12, freq="MS"), "U.S.A")])
    combined, label = combine_customs_sources(_bulk_monthly([]), gw)
    assert len(combined) == 12 and "GW 업로드본" in label


def test_bulk_floor_and_month_normalisation():
    """벌크 하한 미만은 제외되고 월중 일자는 월초로 정규화된다."""
    small = _rows(["2025-05-20"], "Brazil", kg=50_000)
    big = _rows(["2025-05-20"], "Brazil", kg=150_000)
    tbl = _bulk_monthly([small, big])
    assert len(tbl) == 1 and tbl["price_date"].iloc[0] == pd.Timestamp("2025-05-01")
