"""유사국면 참조 모듈 단위 테스트 (W1 Stage 1 — 계획 승인 검증 항목)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.forecasting.analogue_g1 import (
    ANALOGUE_QUANTILE_BINS,
    EXCLUDE_RECENT_TRADING_DAYS,
    MIN_ANALOGUE_EPISODES,
    build_analogue_context,
    dedup_episodes,
    find_analogue_days_quantile,
    format_result_line,
    render_analogue_md,
    summarize_forward,
)

_FORBIDDEN = ("예상", "전망 확률", "매수 유리", "대기 유리")


@pytest.fixture
def synth_analysis() -> pd.DataFrame:
    """합성 mart analysis — z와 전방수익률을 수작업 대조 가능하게 구성."""
    rng = np.random.default_rng(11)
    idx = pd.bdate_range("2014-01-01", periods=1600)
    z = pd.Series(np.sin(np.arange(1600) / 35) + rng.normal(0, 0.25, 1600), index=idx)
    ret = pd.Series(rng.normal(0.005, 0.04, 1600), index=idx)
    return pd.DataFrame({"VARX__z90": z, "target_ret5": ret,
                         "target_ret20": ret, "target_ret60": ret})


def test_forward_return_matches_manual(synth_analysis: pd.DataFrame) -> None:
    """전방 수익률 집계가 수작업 계산과 일치."""
    days = synth_analysis.index[[100, 200, 300, 400, 500, 600, 700, 800]]
    n, n_up, n_down, p10, p50, p90, years = summarize_forward(
        synth_analysis, pd.DatetimeIndex(days), 20)
    manual = np.expm1(synth_analysis.loc[days, "target_ret20"]) * 100
    assert n == 8
    assert n_up == int((manual > 0).sum())
    assert p50 == pytest.approx(float(manual.quantile(0.5)))


def test_leak_guard_excludes_recent(synth_analysis: pd.DataFrame) -> None:
    """직전 60거래일은 유사일 후보에서 제외 — 위반 0건."""
    days, _ = find_analogue_days_quantile(synth_analysis["VARX__z90"])
    cutoff = synth_analysis.index[-EXCLUDE_RECENT_TRADING_DAYS - 1]
    assert len(days) > 0
    assert days.max() <= cutoff


def test_dedup_gap_enforced(synth_analysis: pd.DataFrame) -> None:
    """에피소드 간 최소 거래일 간격 보장."""
    days = synth_analysis.index[:100]                 # 연속 100일
    kept = dedup_episodes(pd.DatetimeIndex(days), synth_analysis.index, 20)
    pos = {d: i for i, d in enumerate(synth_analysis.index)}
    gaps = np.diff([pos[d] for d in kept])
    assert (gaps >= 20).all()


def test_small_sample_degrades_honestly(synth_analysis: pd.DataFrame) -> None:
    """표본 부족 시 guard_note 강등(수치 미산출)."""
    tiny = synth_analysis.iloc[:50]
    res = build_analogue_context(["VARX"], [], analysis=tiny)
    assert res and all(r.guard_note for r in res)
    for r in res:
        assert "보류" in format_result_line(r)


def test_render_contract_a191(synth_analysis: pd.DataFrame) -> None:
    """렌더 계약 — 필수 캡션 존재·금지어 부재 (A-191)."""
    res = build_analogue_context(["VARX"], [], analysis=synth_analysis)
    md = "\n".join(render_analogue_md(res))
    assert "과거 관측의 요약이며 향후 전망·확률 주장이 아님" in md
    for w in _FORBIDDEN:
        assert w not in md
    assert "통계 검정 없음" in md


def test_relax_ladder_marked(synth_analysis: pd.DataFrame) -> None:
    """완화 사다리 사용 시 relax_step=1 표기(사전 등록 1단만)."""
    res = build_analogue_context(["VARX"], [], analysis=synth_analysis)
    ok = [r for r in res if not r.guard_note]
    assert ok, "정상 산출이 최소 1건 있어야 함"
    for r in ok:
        assert r.relax_step in (0, 1)
        if r.relax_step == 1:
            assert "오분위 완화" in format_result_line(r)


def test_unresolvable_variable_degrades(synth_analysis: pd.DataFrame) -> None:
    """mart에 없는 변수는 z-컬럼 미해석 강등."""
    res = build_analogue_context(["NO_SUCH_VAR"], [], analysis=synth_analysis)
    assert res and all("미해석" in r.guard_note for r in res)
