"""일별 브리프 변곡점 연동(W-C)·사례 서사(W-B) 단위 테스트."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.forecasting.analogue_g1 import CASE_PROFILES, case_narrative_lines
from src.reporting.daily_brief import (_inflection_block, _inflection_points,
                                       _kpi_close, _svg_price_chart)


@pytest.fixture
def frames_with_spikes() -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(5)
    dates = pd.bdate_range("2026-04-20", periods=95)
    vals = 66 + np.cumsum(rng.normal(0, 0.3, 95))
    vals[40] = vals[39] * 1.035                       # +3.5% 급등일 주입
    vals[70] = vals[69] * 0.966                       # −3.4% 급락일 주입
    df = pd.DataFrame({"price_date": dates, "indicator_code": "CBOT_BO_CLOSE",
                       "value": vals})
    return {"commodity": df}


def test_inflection_detects_injected_spikes(frames_with_spikes) -> None:
    """주입한 급변일 2건이 검출 목록에 포함."""
    kpi = _kpi_close(frames_with_spikes)
    pts = _inflection_points(kpi)
    assert pts, "변곡점 미검출"
    chgs = [round(p["chg"], 1) for p in pts]
    assert any(c >= 3.0 for c in chgs) and any(c <= -3.0 for c in chgs)
    # 번호는 목록 순서와 1:1
    assert [p["no"] for p in pts] == list("①②③④⑤"[:len(pts)])


def test_inflection_markers_in_svg(frames_with_spikes) -> None:
    """SVG 차트에 변곡점 번호 마커가 렌더됨."""
    kpi = _kpi_close(frames_with_spikes)
    pts = _inflection_points(kpi)
    svg = _svg_price_chart(kpi, None, marks=pts)
    for p in pts:
        assert p["no"] in svg


def test_inflection_block_honest_degradation(frames_with_spikes) -> None:
    """신호 아카이브 밖 날짜·분석 데이터 미가용 시 정직 강등 문구."""
    kpi = _kpi_close(frames_with_spikes)
    pts = _inflection_points(kpi)
    html = _inflection_block(pts, pd.DataFrame())
    assert "주요 변동일" in html
    # 방향 주장 금지(A-191 승계)
    for w in ("매수 유리", "대기 유리", "상승할 것", "하락할 것"):
        assert w not in html


def test_flat_series_no_inflections() -> None:
    """급변 없는 계열은 빈 목록(기준 미달)."""
    dates = pd.bdate_range("2026-04-20", periods=95)
    df = pd.DataFrame({"price_date": dates, "indicator_code": "CBOT_BO_CLOSE",
                       "value": np.linspace(66, 67, 95)})
    kpi = _kpi_close({"c": df})
    assert _inflection_points(kpi) == []


def test_case_profiles_complete() -> None:
    """전 사례 프로파일이 5필드 서사를 반환하고 방향 주장 금지어가 없음."""
    for name in CASE_PROFILES:
        narr = case_narrative_lines(name)
        assert len(narr) == 5
        blob = "\n".join(narr)
        for w in ("예상", "전망 확률", "매수 유리", "대기 유리"):
            assert w not in blob
