"""G1 신뢰도 지표(A-264) — 합성 데이터로 규칙·보류·서술 계약 검증."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.evaluation import g1_reliability as gr


@pytest.fixture(scope="module")
def synthetic() -> tuple[pd.Series, pd.DataFrame]:
    rng = np.random.default_rng(7)
    idx = pd.bdate_range("2010-01-04", "2025-12-31")
    ret = rng.normal(0, 0.012, len(idx))
    close = pd.Series(50 * np.exp(np.cumsum(ret)), index=idx)
    bdi = pd.Series(1500 + np.cumsum(rng.normal(0, 25, len(idx))), index=idx).clip(lower=300)
    noise = pd.Series(rng.normal(0, 1, len(idx)), index=idx)
    levels = pd.DataFrame({"TE_BDI": bdi, "X_NOISE": noise, "X_LEAD": close.shift(-1)})
    return close, levels


def test_reference_range_coverage_near_nominal_on_iid(synthetic):
    close, _ = synthetic
    out = gr.reference_range_diagnosis(close)
    for h in gr.HORIZONS:
        cov = out["horizons"][str(h)]["coverage"]
        assert 0.70 <= cov <= 0.90, f"iid 수익률에서 포함률이 명목 80% 근처여야 함: {h}일 {cov}"
    assert out["label"].startswith("범위 폭 진단")


def test_alert_retro_episode_gap_and_hold(synthetic):
    close, levels = synthetic
    out = gr.alert_rule_retro(levels, close)
    bdi = out["rules"]["해상운임(BDI) 90일 편차 > 2σ"]
    assert bdi["status"] == "산출" and bdi["breach_days"] > 0
    h60 = bdi["horizons"]["60"]
    # 에피소드 간격 ≥ 지평이므로 60일 에피소드 수 ≤ 발화일 수 / 1 이고 5일보다 적어야 함
    assert bdi["horizons"]["5"]["episodes"] >= h60["episodes"]
    assert out["rules"]["대두유−팜유 가격 차이 > 175 $/MT"]["status"].startswith("미평가")
    assert out["label"] == "실발행 아님 — 소급 합성"


def test_alert_retro_holds_when_few_episodes():
    idx = pd.bdate_range("2010-01-04", "2025-12-31")
    close = pd.Series(np.linspace(40, 60, len(idx)), index=idx)
    rare = pd.Series(0.0, index=idx)
    rare.iloc[2000] = 1000.0                       # 단 1회 급등 → 에피소드 1 → 보류
    out = gr.alert_rule_retro(pd.DataFrame({"TE_BDI": rare + 100}), close)
    horizons = out["rules"]["해상운임(BDI) 90일 편차 > 2σ"]["horizons"]
    assert all(v["status"] == "표본 부족 — 보류" for v in horizons.values())


def test_rank_stability_sign_and_rho(synthetic):
    close, levels = synthetic
    target = gr._forward_returns(close)["target_ret20"]
    feats = pd.DataFrame({"A_SIGNAL": target.shift(0) * 3 + np.random.default_rng(1).normal(0, 0.05, len(target)),
                          "B_NOISE": np.random.default_rng(2).normal(0, 1, len(target)),
                          "C_NOISE": np.random.default_rng(3).normal(0, 1, len(target)),
                          "D_NOISE": np.random.default_rng(4).normal(0, 1, len(target))}, index=target.index)
    out = gr.rank_stability(feats, target)
    assert out["status"] == "산출"
    assert out["pearson"]["top_last_fold"][0] == "A_SIGNAL"
    assert -1.0 <= out["pearson"]["mean_spearman"] <= 1.0


def test_ledger_append_dedup_and_mature(tmp_path, synthetic):
    close, _ = synthetic
    path = tmp_path / "ledger.csv"
    alerts = [{"변수": "ENSO_ONI", "현재값": "1.8", "임계값": "±0.5", "상태": "🚨 임계초과"},
              {"변수": "BDI_ZSCORE", "현재값": "0.3", "임계값": "2.0σ", "상태": "✅ 정상"}]
    assert gr.append_alert_ledger(alerts, "2020-03-02 00:00:00", "r1", path) == 1
    assert gr.append_alert_ledger(alerts, "2020-03-02 00:00:00", "r2", path) == 0   # 중복 유지
    filled = gr.mature_alert_ledger(close, path)
    assert filled == 3                                                            # 5/20/60 전부 성숙
    led = pd.read_csv(path)
    assert led["abs_ret60"].notna().all() and led["run_id"].iloc[0] == "r1"
    assert gr.ledger_summary(path)["matured"]["60"] == 1


def test_markdown_contract_and_forbidden_phrases(synthetic):
    close, levels = synthetic
    res = {"generated_at": "2026-09-14T00:00:00+00:00", "mode": "full", "window": [gr.WINDOW_START, gr.WINDOW_END],
           "basis": "합성", "realtime": gr.realtime_metrics(), "ledger": {"rows": 0},
           "historical": {"H1_rank_stability": {"status": "산출 보류", "reason": "x"},
                          "H2_granger_persistence": {"status": "미산출"},
                          "H3_alert_rule_retro": gr.alert_rule_retro(levels, close),
                          "H4_reference_range": gr.reference_range_diagnosis(close),
                          "H5_analogue_discrimination": gr.analogue_discrimination(levels, close, ["TE_BDI"])}}
    md = gr.render_markdown(res)
    assert gr.REQUIRED_CAPTION in md
    for bad in gr.FORBIDDEN_PHRASES:
        assert bad not in md
    assert "R6 데이터 유형별 규칙 재검증" in md
