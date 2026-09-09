"""해상 요충 해협 위협 점수 — 규칙 기반 참고 지수 (0~100 · 확률·전망 아님).

설계 원천: World Monitor 공개 방법론(등급 가중 + 경보 + AIS + 급감 보너스, 상한 100 — 편집상 가중치).
규칙 파일: config/chokepoints.yaml (rule_version 동반 · 개정 시 과거 재계산 금지).
규율:
  · 결측 성분은 0이 아닌 None('미확인') — 부분 산출 표기, 결측 제외 후 재정규화 금지 (A-202)
  · 노후 관측(staleness_days 초과)은 결측 취급 · 한 신호는 한 자리(승급에 쓴 신호는 경보 수에서 제외)
  · 보고 계층 파생값 — feature mart 미편입(원자 지표와 공선) · 출력 문구에 확률·전망 어휘 금지 (A-191)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml

REGISTRY_PATH = Path(__file__).resolve().parents[2] / "config" / "chokepoints.yaml"
_FORBIDDEN_WORDS = ("확률", "전망", "예측")
TIER_ORDER = ["normal", "elevated", "high", "critical", "war_zone"]


@dataclass
class Observation:
    value: float
    as_of: date


@dataclass
class Component:
    points: float | None            # None = 미확인(결측·노후)
    note: str
    sources: list[str] = field(default_factory=list)


@dataclass
class ChokepointScore:
    key: str
    name_ko: str
    kind: str
    tier: str
    tier_weight: float
    tier_source: str                # structural | dynamic
    tier_basis: str
    components: dict[str, Component]
    score: int
    band: str                       # ok | warn | crit
    partial: bool
    missing: list[str]
    used_signals: list[str]
    awrp_multiplier: float | None
    route_relevance: dict[str, Any]
    lead_time_impact: dict[str, Any]
    as_of: date


def load_registry(path: Path | None = None) -> dict[str, Any]:
    with open(path or REGISTRY_PATH, encoding="utf-8") as f:
        reg = yaml.safe_load(f)
    for k in ("rule_version", "tier_weights", "bands", "caps", "staleness_days", "chokepoints"):
        if k not in reg:
            raise ValueError(f"[오류] 해협 레지스트리 필수 키 누락: {k}")
    return reg


def band_of(score: float, bands: dict[str, float]) -> str:
    if score < bands["ok_below"]:
        return "ok"
    if score < bands["warn_below"]:
        return "warn"
    return "crit"


def _fresh(obs: Observation | None, today: date, max_days: int) -> tuple[Observation | None, str | None]:
    """관측 신선도 판정 — (유효 관측, 결측 사유)."""
    if obs is None:
        return None, "미수집"
    age = (today - obs.as_of).days
    if age > max_days:
        return None, f"노후({age}일)"
    return obs, None


def _ais_component(cp: dict, inputs: dict[str, Observation], series: dict[str, list[tuple[date, float]]],
                   reg: dict, today: date) -> tuple[Component, float | None]:
    """AIS 성분 — 위험 등급 지표 우선, 없으면 통항 수의 자기 기준(롤링 중앙값) 대비 비율. 반환 (성분, 통항 비율)."""
    caps, stale = reg["caps"], reg["staleness_days"]["ais"]
    risk_code, count_code = cp.get("ais_risk_indicator"), cp.get("ais_count_indicator")
    if not risk_code and not count_code:
        return Component(None, "전용 AIS 지표 없음(DATA GAP)"), None
    ratio: float | None = None
    # ① 통항 수 자기 기준 비율(축적 ≥ min_days일 때만)
    if count_code and count_code in series:
        pts = sorted(series[count_code])
        hist = [v for d, v in pts if d < today - timedelta(days=0)]
        last_d, last_v = pts[-1]
        if (today - last_d).days <= stale and len(hist) >= reg["ais_baseline_min_days"]:
            base = sorted(v for _, v in pts[-reg["ais_baseline_min_days"] - 1:-1])
            med = base[len(base) // 2]
            if med > 0:
                ratio = last_v / med
    # ② 등급 지표
    obs, why = _fresh(inputs.get(risk_code) if risk_code else None, today, stale)
    if obs is not None:
        sev = {1: 0, 2: 2, 3: 3}.get(int(round(obs.value)), 0)
        return Component(min(caps["ais"], caps["ais_unit"] * sev),
                         f"{risk_code}={obs.value:.0f} → 심각도 {sev}", [risk_code]), ratio
    if ratio is not None:
        sev = 0
        for s, thr in sorted(reg["ais_severity_ratio"].items(), key=lambda kv: kv[1]):
            if ratio < thr:
                sev = int(s)
                break
        return Component(min(caps["ais"], caps["ais_unit"] * sev),
                         f"통항 비율 {ratio:.2f}(자기 기준 대비) → 심각도 {sev}", [count_code]), ratio
    if count_code and count_code in series:
        return Component(None, f"통항 수 축적 {len(series[count_code])}일 < 기준 {reg['ais_baseline_min_days']}일"), None
    return Component(None, f"AIS 미수집({why or '미수집'})"), None


def score_chokepoint(cp: dict, inputs: dict[str, Observation], series: dict[str, list[tuple[date, float]]],
                     reg: dict, today: date) -> ChokepointScore:
    tw, caps, stale = reg["tier_weights"], reg["caps"], reg["staleness_days"]
    used: list[str] = []
    missing: list[str] = []
    # ── ① 등급(구조 + 동적 승급) ──
    tier, tier_src, basis = cp["structural_tier"], "structural", cp.get("tier_source", "")
    dyn = cp.get("dynamic_upgrade")
    if dyn:
        obs, why = _fresh(inputs.get(dyn["indicator"]), today, stale["signal"])
        if obs is None:
            missing.append(f"{dyn['indicator']}({why})")
        else:
            mapped = dyn["map"].get(int(round(obs.value)))
            used.append(dyn["indicator"])
            if mapped and TIER_ORDER.index(mapped) > TIER_ORDER.index(tier):
                tier, tier_src = mapped, "dynamic"
                basis = f"{dyn['indicator']}={obs.value:.0f} → {mapped} 승급"
    comps: dict[str, Component] = {}
    comps["tier"] = Component(float(tw[tier]), f"{tier} 등급 가중 {tw[tier]}", [dyn["indicator"]] if (dyn and tier_src == "dynamic") else [])
    # ── ② 경보 성분(독립 원천 수 × unit, cap) — 승급에 쓴 신호 제외 ──
    n, srcs, avail = 0, [], 0
    for code, thr in (cp.get("warning_sources") or {}).items():
        if dyn and code == dyn["indicator"]:
            continue
        obs, why = _fresh(inputs.get(code), today, stale["signal"])
        if obs is None:
            missing.append(f"{code}({why})")
            continue
        avail += 1
        used.append(code)
        if obs.value >= thr:
            n += 1
            srcs.append(f"{code}={obs.value:.0f}≥{thr}")
    if avail == 0:
        comps["warnings"] = Component(None, "경보 원천 전부 미수집")
    else:
        comps["warnings"] = Component(min(caps["warnings"], caps["warning_unit"] * n),
                                      f"경보 {n}건(원천 {avail}종 확인)", srcs)
    # ── ③ AIS 성분 ──
    ais, ratio = _ais_component(cp, inputs, series, reg, today)
    comps["ais"] = ais
    if ais.points is None:
        missing.append(f"AIS({ais.note})")
    else:
        used.extend(ais.sources)
    # ── ④ 급감 보너스 ──
    if ratio is not None and ratio <= reg["anomaly_ratio"] and TIER_ORDER.index(tier) >= TIER_ORDER.index("critical"):
        comps["anomaly"] = Component(float(caps["anomaly_bonus"]), f"통항 ≤{reg['anomaly_ratio']:.0%} + 등급 {tier}")
    else:
        comps["anomaly"] = Component(0.0 if ais.points is not None else None,
                                     "조건 불충족" if ais.points is not None else "AIS 미확인")
    # ── 합산(결측 성분 제외 · 재정규화 없음) ──
    total = sum(c.points for c in comps.values() if c.points is not None)
    score = int(min(100, round(total)))
    partial = any(c.points is None for c in comps.values())
    awrp = None
    if cp.get("awrp_indicator"):
        obs, _ = _fresh(inputs.get(cp["awrp_indicator"]), today, stale["signal"])
        if obs is not None:
            awrp = obs.value
            used.append(cp["awrp_indicator"])
    return ChokepointScore(
        key=cp["key"], name_ko=cp["name_ko"], kind=cp.get("kind", ""), tier=tier, tier_weight=float(tw[tier]),
        tier_source=tier_src, tier_basis=basis, components=comps, score=score, band=band_of(score, reg["bands"]),
        partial=partial, missing=missing, used_signals=used, awrp_multiplier=awrp,
        route_relevance=cp.get("route_relevance") or {}, lead_time_impact=cp.get("lead_time_impact") or {},
        as_of=today)


def compute_maritime_threat(inputs: dict[str, Observation],
                            series: dict[str, list[tuple[date, float]]] | None = None,
                            today: date | None = None, registry: dict | None = None) -> dict[str, Any]:
    """전 해협 점수 + 한국향 지수. 결정론적(동일 입력 → 동일 출력)."""
    reg = registry or load_registry()
    today = today or date.today()
    series = series or {}
    scores = [score_chokepoint(cp, inputs, series, reg, today) for cp in reg["chokepoints"]]
    by_key = {s.key: s for s in scores}
    ki = reg.get("korea_index", {})

    def _idx(keys: list[str]) -> dict[str, Any]:
        sel = [by_key[k] for k in keys if k in by_key]
        if not sel:
            return {"score": None, "band": "unknown", "partial": True, "driver": None}
        top = max(sel, key=lambda s: s.score)
        return {"score": top.score, "band": top.band, "partial": any(s.partial for s in sel),
                "driver": top.name_ko, "keys": keys}

    return {
        "rule_version": reg["rule_version"], "as_of": today.isoformat(),
        "method_source": reg.get("method_source", ""),
        "chokepoints": scores,
        "korea_direct": _idx(ki.get("direct_keys", [])),
        "propagation": _idx(ki.get("propagation_keys", [])),
        "coverage_note": ki.get("coverage_note", ""),
        "caption": ("규칙 기반 편집상 참고 지수(0~100)이며 시장 방향의 판단 근거가 아님 · "
                    "미확인 성분은 0으로 대체하지 않고 부분 산출로 표기함"),
    }


def explain_ko(s: ChokepointScore) -> str:
    """카드 근거 문장 — 성분 분해를 그대로 서술."""
    parts = []
    for k, label in (("tier", "등급"), ("warnings", "경보"), ("ais", "AIS"), ("anomaly", "급감")):
        c = s.components.get(k)
        if c is None:
            continue
        parts.append(f"{label} {'미확인' if c.points is None else f'{c.points:.0f}'}({c.note})")
    tail = f" · 부분 산출(미확인 {len([c for c in s.components.values() if c.points is None])}개 성분)" if s.partial else ""
    return " + ".join(parts) + f" = {s.score}/100{tail}"


def self_test() -> None:
    """결정론·경계·금지어 자체 검증 (A-191 self-test 패턴)."""
    reg = load_registry()
    today = date(2026, 9, 9)
    hi = {"HORMUZ_THREAT_LEVEL": Observation(3, today), "GDELT_EVENT_SCORE": Observation(50, today),
          "GEOINTEL_RISK_COMPOSITE": Observation(60, today), "AIS_HORMUZ_RISK": Observation(3, today)}
    a = compute_maritime_threat(hi, today=today, registry=reg)
    b = compute_maritime_threat(hi, today=today, registry=reg)
    assert [s.score for s in a["chokepoints"]] == [s.score for s in b["chokepoints"]], "결정론 위반"
    h = next(s for s in a["chokepoints"] if s.key == "hormuz")
    assert h.tier == "critical" and h.score == 40 + 10 + 15, h
    empty = compute_maritime_threat({}, today=today, registry=reg)
    assert all(s.partial for s in empty["chokepoints"]), "결측 시 부분 산출 표기 누락"
    text = " ".join(explain_ko(s) for s in a["chokepoints"]) + a["caption"]
    bad = [w for w in _FORBIDDEN_WORDS if re.search(w, text)]
    assert not bad, f"금지어 검출: {bad}"
    print(f"[완료] maritime_threat self-test 통과 — {reg['rule_version']}")


if __name__ == "__main__":
    self_test()
