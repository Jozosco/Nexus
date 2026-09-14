"""해운 BDI 3순위 폴백 — 저장소 TE xlsx 스냅샷 사본(A-263).

런 #97 유형(TE 409 + stooq 404 → Perplexity BCAA 1행만 저장 → MIN_ROWS 게이트)을 막는 장치.
openai는 이 커넥터가 모듈 수준에서 import하지만 이 테스트 경로에서는 쓰이지 않으므로 stub 처리.
"""
from __future__ import annotations

import sys
import types

import pandas as pd
import pytest

if "openai" not in sys.modules:                       # 로컬 개발 환경 — 폴백 경로만 검증
    _stub = types.ModuleType("openai")
    _stub.OpenAI = object
    sys.modules["openai"] = _stub

from src.pipeline.connectors import shipping_connector as sc  # noqa: E402


def test_te_xlsx_fallback_reconstructs_recent_bdi() -> None:
    df = sc.fetch_bdi_te_xlsx(recent_days=120)
    if df.empty:
        pytest.skip("TE xlsx BDI 사본 없음(sparse checkout 범위 밖)")
    assert (df["indicator_code"] == "BDI").all()
    assert df["source_name"].eq("TradingEconomics_xlsx_snapshot").all()
    assert len(df) >= 10, "최근 120일 사본이 MIN_ROWS(10) 미만"
    assert df["price_date"].is_monotonic_increasing
    assert (df["price_date"] >= pd.Timestamp.now(tz="UTC").tz_localize(None) - pd.Timedelta(days=121)).all()
    assert df["value"].gt(0).all()


def test_te_xlsx_fallback_missing_file_is_nonfatal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sc, "TE_XLSX_BDI_GLOB", "data/raw/__없는_폴더__/*.xlsx")
    assert sc.fetch_bdi_te_xlsx().empty
