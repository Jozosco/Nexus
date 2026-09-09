"""해상 위협 점수 — 규칙·경계·결측·결정론 테스트 (A-250)."""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from src.risk.maritime_threat import (Observation, band_of, compute_maritime_threat, explain_ko,
                                      load_registry, _FORBIDDEN_WORDS)

TODAY = date(2026, 9, 9)


@pytest.fixture(scope="module")
def reg():
    return load_registry()


def _obs(v, d=TODAY):
    return Observation(float(v), d)


def _cp(res, key):
    return next(s for s in res["chokepoints"] if s.key == key)


def test_band_boundaries(reg):
    b = reg["bands"]
    assert band_of(19.99, b) == "ok" and band_of(20, b) == "warn"
    assert band_of(49.99, b) == "warn" and band_of(50, b) == "crit"


def test_clip_at_100_and_component_sum(reg):
    inp = {"HORMUZ_THREAT_LEVEL": _obs(3), "GDELT_EVENT_SCORE": _obs(99), "GEOINTEL_RISK_COMPOSITE": _obs(99),
           "AIS_HORMUZ_RISK": _obs(3)}
    h = _cp(compute_maritime_threat(inp, today=TODAY, registry=reg), "hormuz")
    # critical 40 + 경보 2건 10 + AIS 15 = 65 (급감 보너스는 통항 비율 없이는 0)
    assert h.tier == "critical" and h.score == 65 and h.band == "crit" and not h.partial
    reg2 = dict(reg); reg2["tier_weights"] = {**reg["tier_weights"], "critical": 90}
    assert _cp(compute_maritime_threat(inp, today=TODAY, registry=reg2), "hormuz").score == 100


def test_missing_inputs_are_partial_not_zero(reg):
    h = _cp(compute_maritime_threat({}, today=TODAY, registry=reg), "hormuz")
    assert h.partial and h.components["warnings"].points is None and h.components["ais"].points is None
    assert h.score == reg["tier_weights"][h.tier]          # 구조 등급만 반영, 결측은 0 대입 아님
    assert "미확인" in explain_ko(h)


def test_stale_observation_degrades(reg):
    old = TODAY - timedelta(days=reg["staleness_days"]["signal"] + 1)
    inp = {"HORMUZ_THREAT_LEVEL": _obs(3, old)}
    h = _cp(compute_maritime_threat(inp, today=TODAY, registry=reg), "hormuz")
    assert h.tier_source == "structural" and any("노후" in m for m in h.missing)


def test_monotonic_in_threat_level(reg):
    prev = -1
    for lvl in (1, 2, 3):
        h = _cp(compute_maritime_threat({"HORMUZ_THREAT_LEVEL": _obs(lvl)}, today=TODAY, registry=reg), "hormuz")
        assert h.score >= prev
        prev = h.score


def test_one_signal_one_slot(reg):
    # 승급에 쓴 HORMUZ_THREAT_LEVEL은 경보 원천이 아니어야 함(이중 계상 금지)
    cp = next(c for c in reg["chokepoints"] if c["key"] == "hormuz")
    assert cp["dynamic_upgrade"]["indicator"] not in (cp.get("warning_sources") or {})


def test_ais_baseline_gate_and_anomaly(reg):
    n = reg["ais_baseline_min_days"]
    ser = {"AIS_HORMUZ_TANKER_COUNT": [(TODAY - timedelta(days=n - i), 40.0) for i in range(n)]
           + [(TODAY, 10.0)]}                                   # 통항 25% → 심각도 3 + 급감 조건
    inp = {"HORMUZ_THREAT_LEVEL": _obs(3)}
    h = _cp(compute_maritime_threat(inp, series=ser, today=TODAY, registry=reg), "hormuz")
    assert h.components["ais"].points == reg["caps"]["ais"] and h.components["anomaly"].points == reg["caps"]["anomaly_bonus"]
    short = {"AIS_HORMUZ_TANKER_COUNT": ser["AIS_HORMUZ_TANKER_COUNT"][-5:]}
    h2 = _cp(compute_maritime_threat(inp, series=short, today=TODAY, registry=reg), "hormuz")
    assert h2.components["ais"].points is None                  # 축적 부족 → 미확인(0 아님)


def test_korea_index_is_max_of_direct(reg):
    inp = {"GDELT_EVENT_SCORE": _obs(50), "AIS_MALACCA_RISK": _obs(3), "AIS_PANAMA_RISK": _obs(1)}
    res = compute_maritime_threat(inp, today=TODAY, registry=reg)
    assert res["korea_direct"]["driver"] == "말라카 해협"
    assert res["korea_direct"]["score"] == max(_cp(res, "malacca").score, _cp(res, "panama").score)
    assert res["rule_version"] == reg["rule_version"]


def test_no_forbidden_words_in_output(reg):
    res = compute_maritime_threat({"HORMUZ_THREAT_LEVEL": _obs(3)}, today=TODAY, registry=reg)
    text = res["caption"] + " ".join(explain_ko(s) for s in res["chokepoints"])
    assert not any(w in text for w in _FORBIDDEN_WORDS)
