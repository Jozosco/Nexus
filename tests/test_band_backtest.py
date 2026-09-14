"""G2 밴드 백테스트 기준선(R-038) — 누수 차단·포함률 규약 검증."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.evaluation import band_backtest as bb


def _close(seed: int = 3) -> pd.Series:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2010-01-04", "2025-12-31")
    return pd.Series(50 * np.exp(np.cumsum(rng.normal(0, 0.012, len(idx)))), index=idx)


def test_rolling_band_uses_only_past_returns():
    close = _close()
    logc = np.log(close)
    bands = bb._baseline_bands(logc, 20)
    b2 = bands["B2 롤링 경험 분위(250일)"]
    # t 시점 분위는 t까지의 수익률만 사용: 미래 종가를 바꿔도 t 이전 값은 불변
    logc2 = logc.copy(); logc2.iloc[-100:] += 0.5
    b2b = bb._baseline_bands(logc2, 20)["B2 롤링 경험 분위(250일)"]
    pd.testing.assert_frame_equal(b2.iloc[:-120], b2b.iloc[:-120])


def test_iid_coverage_near_nominal_and_pinball_order():
    res = bb.run_backtest(_close())
    w = res["horizons"]["20"]["B2 롤링 경험 분위(250일)"]["walk_forward"]
    assert 0.70 <= w["coverage_80"] <= 0.90
    assert 0.40 <= w["coverage_50"] <= 0.60
    b1 = res["horizons"]["20"]["B1 최근값"]["walk_forward"]
    assert b1["coverage_80"] == 0.0                      # 폭 0 기준선
    assert w["pinball_p10"] < b1["pinball_p10"]           # 분위 밴드가 점 기준선보다 낫다


def test_markdown_has_no_direction_claims():
    res = bb.run_backtest(_close())
    md = bb.render_markdown(res, "합성")
    for bad in ("적중률", "상승 확률", "예측 정확도"):
        assert bad not in md
    assert "락박스" in md
