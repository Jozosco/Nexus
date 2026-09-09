"""관측 행 available_at 캡 — 설계 지연(+1일)과 발표 지연 추정의 구분 (A-242·A-254)."""
from __future__ import annotations

import pandas as pd

from src.pipeline.asof import attach_asof


def _row(code: str, event: str, ingested: str) -> pd.DataFrame:
    return pd.DataFrame({"price_date": [pd.Timestamp(event)], "indicator_code": [code],
                         "value": [1.0], "ingested_at": [pd.Timestamp(ingested)]})


def test_esr_estimate_capped_to_ingest_time_morning_run():
    # 주간 관측(기준일 9/4) + 7일 추정 = 9/11 — 오전 수집(9/9 05:52)에서 값을 이미 받았으므로 9/9로 캡
    out = attach_asof(_row("ESR_SBO_EXPORT_KOREA", "2026-09-04", "2026-09-09 05:52"), source="USDA")
    assert out["available_at"].iloc[0] == pd.Timestamp("2026-09-09 05:52")
    assert out["available_at"].iloc[0].date() <= pd.Timestamp("2026-09-09").date()


def test_vix_design_lag_preserved():
    # VIXCLS: 장 마감 후 확정 → 설계상 +1일(M-013) — 수집 시점보다 늦어도 캡하지 않음
    out = attach_asof(_row("VIXCLS", "2026-09-08", "2026-09-08 22:52"), source="FRED")
    assert out["available_at"].iloc[0] == pd.Timestamp("2026-09-09")


def test_forecast_row_capped():
    # 전망 행(event_time > ingested_at)은 수집 시점으로 캡(A-195)
    out = attach_asof(_row("SBO_PRODUCTION_US", "2026-10-01", "2026-09-09 05:52"), source="USDA")
    assert out["available_at"].iloc[0] <= pd.Timestamp("2026-09-09 05:52")
