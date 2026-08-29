"""G1 과거 유사국면 참조 — Stage 1: 단변량 분위 슬라이스 (D-051 · W1).

조정자 재정립(2026-08-28): G1의 본질 = "특정 변수 기준으로 과거 연도들의 수급/가격이
어떻게 변했는지 분석해 유사 상황의 참조로 제공". 본 모듈은 그 계산 전담층이다.

원리 — 누수 없는 조건부 과거 실측 분포:
  mart(2010~)의 `{X}__z90`(후방참조 z)이 현재와 같은 분위 버킷이었던 과거 거래일을
  찾고, 그 날들의 `target_ret{h}`(mart가 이미 보유한 미래 h거래일 실측 수익률)를
  집계한다. 유사일 검색은 과거만 보고, 전방 수익률은 mart 빌더의 유일한 전방참조
  컬럼을 그대로 쓰므로 새 누수 경로가 없다.

규율 (계획 승인분):
  - A-191: 산출은 "과거 관측의 요약"까지 — 전망·확률 주장 금지(서술 계약 문자열 검증)
  - 직전 EXCLUDE_RECENT_TRADING_DAYS 거래일은 이웃 후보 제외(전방 창 겹침 누수 가드)
  - 에피소드화(유사일 간 최소 간격 = horizon) 후 MIN_ANALOGUE_EPISODES 미만이면
    "표본 부족 — 산출 보류" 정직 강등. 완화는 십분위→오분위 사전 등록 1단만(표기 의무)
  - 수익률 집계는 원시값(IQR 캡은 z 경로 전용 — D6)
  - Stage 1은 통계 검정을 하지 않는다(기술 서술만 — 다중검정 문제 원천 차단)
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date

import numpy as np
import pandas as pd

ANALOGUE_HORIZONS: tuple[int, ...] = (5, 20, 60)   # ≈1주 · 1개월 · 3개월 (거래일)
ANALOGUE_QUANTILE_BINS = 10                        # Stage 1 십분위
RELAX_BINS = 5                                     # 사전 등록 완화 사다리 1단(오분위)
MIN_ANALOGUE_EPISODES = 8
EXCLUDE_RECENT_TRADING_DAYS = 60                   # 전방 창 겹침 누수 가드
MAX_ANALOGUE_VARS = 3                              # 브리프 렌더 상한(경보 우선)

# 위기 사례 프로파일 — docs/research_desk/_reference/soybean_oil_historical_crisis_analysis.md
# (수치는 corrections 문서 병독 전제 — 배지는 정성 연결일 뿐 처치 정의가 아님)
# 서사 계약(A-191): 과거 사실 기술 + 구조 비교까지만 — 방향 주장·전망 문구 금지.
@dataclass(frozen=True)
class CaseProfile:
    start: str
    end: str
    trigger: str        # 원인 사건(과거 사실)
    channel: str        # 전달 경로(수급·물류·정책)
    price_fact: str     # 가격 반응 실측
    similarity: str     # 현재 국면과의 구조 유사점
    difference: str     # 현재 국면과의 구조 차이점


CASE_PROFILES: dict[str, CaseProfile] = {
    "Case 1 · 2010-11 라니냐·러 수출금지": CaseProfile(
        "2010-06-01", "2011-09-30",
        "라니냐 최고조(ONI −1.4)로 남미 작황 취약성이 누적된 상태에서, 러시아가 폭염·"
        "가뭄으로 밀 수출을 금지함(2010-08).",
        "곡물 전반 급등 → 유지류로 대체 수요 집중 → 대두유 수급 압박.",
        "저점 38.0 → 고점 57.4 USc/lb, 약 9개월 +51% 실측. ONI 전환이 가격에 "
        "2~3개월 선행함.",
        "기후 취약성이 깔린 상태에서 단일 정책 이벤트가 추가 충격으로 얹히는 중첩 구조.",
        "당시 파급은 곡물發 대체 수요 경로였고, 물류(운임·해협) 요인의 비중은 크지 않았음."),
    "Case 2 · 2012 미국 대가뭄": CaseProfile(
        "2012-05-01", "2013-08-31",
        "미국 중서부 대가뭄(예외적 가뭄 등급 면적 35%) — 7월 WASDE가 미국 대두 생산 "
        "전망을 −14.4% 하향함.",
        "생산 전망 하향 → 공급 우려 선반영 → 실제 수확 발표(우려 대비 양호)로 급반전.",
        "8개월 +13.6% 뒤 9월 한 달 만에 되돌림 실측 — 단일 공급 충격의 가역성 사례.",
        "발표 이벤트(WASDE) 전후로 가격이 빠르게 재평가되는 패턴.",
        "당시는 운임(BDI) 저수준·수입 수요 부진의 삼중 부정 구조 — 고점이 지속되지 "
        "못한 조건이 겹쳐 있었음."),
    "Case 3 · 2021-22 복합 위기": CaseProfile(
        "2020-08-01", "2022-06-30",
        "2년 연속 라니냐(아르헨 감산) + 러시아-우크라이나 전쟁(해바라기유 공급 45~50% "
        "붕괴) + 인도네시아 팜유 수출 금지 + 인도 수입 관세 인하.",
        "기후·지정학·정책 3중 충격이 동시 발생 — 대체 수요 집중에 물류 차질(운임 지수 "
        "+387%)이 도착 원가를 증폭함. COVID기 항만·항로 봉쇄로 선박이 우회하며 운임·"
        "보험료가 도착가에 얹히는 경로가 형성됨.",
        "저점 28.9 → 고점 82.5 USc/lb, 23개월 +185% 실측(당시 사상 최고가). 운임 급등이 "
        "가격 고점에 6~18개월 선행함.",
        "'요충 경로 불안 → 우회·보험료 → 도착가 상방'의 물류 증폭 구조가 현재 호르무즈 "
        "국면과 동형임(당시는 COVID·흑해發 경로 차질).",
        "당시는 수요 측 충격(바이오디젤·인도 수입)이 동반됨 — corrections 재평가에서 "
        "유사도 7/10로 하향(우크라이나 요인 제외), 2024-25 미·중 관세 사례(Case D)가 "
        "9/10로 더 유사 판정."),
    "Case 4 · 2022-23 아르헨 가뭄": CaseProfile(
        "2022-12-01", "2023-04-30",
        "3년 연속(트리플딥) 라니냐로 아르헨티나 대두 생산 −42%(43.4→25.0 MMT), "
        "로사리오 압착 허브 가동률 45%로 급락.",
        "단일 원산지 공급 급감 — 그러나 브라질 기록 풍작(153 MMT)이 물량을 완전 상쇄함.",
        "+11.4% 상승에 그친 뒤 되돌림 실측 — 대체 원산지(스윙 프로듀서) 완충 여부가 "
        "충격 크기를 결정함.",
        "주요 원산지 한 곳의 충격이 발생해도 대체 원산지 물량이 완충하는 구조 — 현재도 "
        "브라질 생산이 역대 최고 수준이라는 점이 같은 완충 요인임.",
        "당시는 기후 단일 요인 — 물류·정책 충격이 결합하지 않았음."),
}

# 하위 호환: 창(window)만 쓰는 기존 경로용 파생 뷰
CASE_WINDOWS: dict[str, tuple[str, str]] = {
    name: (p.start, p.end) for name, p in CASE_PROFILES.items()
}


def case_narrative_lines(name: str) -> list[str]:
    """사례 배지 → 메커니즘 서사(원인→경로→가격 실측→유사점/차이점). 미등재 시 빈 목록."""
    p = CASE_PROFILES.get(name)
    if p is None:
        return []
    return [f"원인 사건: {p.trigger}",
            f"전달 경로: {p.channel}",
            f"가격 반응(실측): {p.price_fact}",
            f"현재와의 유사점: {p.similarity}",
            f"현재와의 차이점: {p.difference}"]

# 경보 변수 코드 → mart 파생 z-컬럼 후보 (경보 코드는 mart 컬럼명과 다른 별칭 체계)
_ALERT_Z_ALIASES: dict[str, list[str]] = {
    "BDI_ZSCORE": ["TE_BDI__z90", "BDI__z90"],
    "GPR_NORMALIZED": ["GPR__z90", "GPR_NORMALIZED__z90", "GPR__z252"],
    "ENSO_ONI": ["ONI__z252", "ONI__z90", "ENSO_ONI__z252"],
    "CPO_SBO_SPREAD": ["TE_PALM_OIL__z90", "CPO_SBO_SPREAD__z90"],
    "WASDE_STU": ["WASDE_SBO_STU__z252", "WASDE_SBO_STU__z90"],
}

_REQUIRED_CAPTION = "과거 관측의 요약이며 향후 전망·확률 주장이 아님"
_FORBIDDEN_WORDS = ("예상", "전망 확률", "매수 유리", "대기 유리", "상승할 것", "하락할 것")


@dataclass
class AnalogueResult:
    var_code: str                     # 기반 변수 코드(표시용)
    z_col: str                        # 실제 사용한 mart 컬럼
    current_z: float
    method: str                       # "quantile_slice"
    horizon: int
    n_days: int
    n_episodes: int
    n_up: int
    n_down: int
    ret_p10: float                    # % (원시 로그수익률 → 백분율 변환)
    ret_p50: float
    ret_p90: float
    years: list[int] = field(default_factory=list)
    case_badges: list[str] = field(default_factory=list)
    relax_step: int = 0               # 0=십분위 · 1=오분위(완화 사용 표기)
    guard_note: str = ""              # ""=정상 · 그 외 = 산출 보류 사유


def _resolve_z_column(columns: pd.Index, code: str) -> str | None:
    """변수 코드 → mart z-컬럼 해석. 실패 시 None(정직 강등)."""
    base = code.split("__")[0]
    candidates = [f"{base}__z90", f"{base}__z252"]
    candidates = _ALERT_Z_ALIASES.get(code, []) + _ALERT_Z_ALIASES.get(base, []) + candidates
    for c in candidates:
        if c in columns:
            return c
    # 마지막 수단: 코드 부분일치 z-컬럼(유일할 때만 — 오매칭 방지)
    hits = [c for c in columns if c.startswith(base) and ("__z" in c)]
    return hits[0] if len(hits) == 1 else None


def find_analogue_days_quantile(
    z_series: pd.Series, bins: int = ANALOGUE_QUANTILE_BINS,
    exclude_recent: int = EXCLUDE_RECENT_TRADING_DAYS,
) -> tuple[pd.DatetimeIndex, float]:
    """현재 z와 동일 분위 버킷의 과거 거래일 반환 (직전 exclude_recent 거래일 제외)."""
    z = z_series.dropna()
    if len(z) < bins * 3:
        return pd.DatetimeIndex([]), float("nan")
    current = float(z.iloc[-1])
    # 버킷 경계는 전체 관측 분포 기준(현재 포함 — 순위 판정일 뿐 전방 정보 아님)
    edges = np.quantile(z.values, np.linspace(0, 1, bins + 1))
    edges[0], edges[-1] = -np.inf, np.inf
    cur_bin = int(np.searchsorted(edges, current, side="right")) - 1
    in_bin = z[(z >= edges[cur_bin]) & (z < edges[cur_bin + 1])]
    # 전방 창 겹침 가드: 최근 exclude_recent 거래일(z 관측 기준) 제외
    cutoff_pos = max(0, len(z) - exclude_recent)
    allowed = z.index[:cutoff_pos]
    days = in_bin.index.intersection(allowed)
    return pd.DatetimeIndex(days).sort_values(), current


def dedup_episodes(days: pd.DatetimeIndex, calendar: pd.DatetimeIndex,
                   gap_trading_days: int) -> pd.DatetimeIndex:
    """연속 유사일을 에피소드화 — 직전 채택일로부터 거래일 간격 gap 미만이면 건너뜀."""
    if len(days) == 0:
        return days
    pos = {d: i for i, d in enumerate(calendar)}
    kept: list[pd.Timestamp] = []
    last_pos = -10**9
    for d in days:
        p = pos.get(d)
        if p is None:
            continue
        if p - last_pos >= gap_trading_days:
            kept.append(d)
            last_pos = p
    return pd.DatetimeIndex(kept)


def case_badges_for(days: pd.DatetimeIndex) -> list[str]:
    badges = []
    for name, (s, e) in CASE_WINDOWS.items():
        s_ts, e_ts = pd.Timestamp(s), pd.Timestamp(e)
        if any((d >= s_ts) and (d <= e_ts) for d in days):
            badges.append(name)
    return badges


def summarize_forward(analysis: pd.DataFrame, episodes: pd.DatetimeIndex,
                      horizon: int) -> tuple[int, int, int, float, float, float, list[int]]:
    """에피소드 일들의 target_ret{h} 실측 집계 — 원시 로그수익률(캡핑 없음 — D6)."""
    col = f"target_ret{horizon}"
    if col not in analysis.columns:
        raise KeyError(f"[오류] mart에 {col} 없음 — build_feature_mart TARGET_HORIZONS 확인")
    rets = analysis.loc[analysis.index.intersection(episodes), col].dropna()
    pct = (np.expm1(rets) * 100.0)
    n_up = int((pct > 0).sum())
    n_down = int((pct < 0).sum())
    years = sorted({d.year for d in rets.index})
    if len(pct) == 0:
        return 0, n_up, n_down, math.nan, math.nan, math.nan, years
    return (len(pct), n_up, n_down,
            float(pct.quantile(0.10)), float(pct.quantile(0.50)), float(pct.quantile(0.90)),
            years)


def _analogue_for_var(analysis: pd.DataFrame, code: str,
                      horizons: tuple[int, ...]) -> list[AnalogueResult]:
    z_col = _resolve_z_column(analysis.columns, code)
    base = code.split("__")[0]
    if z_col is None:
        return [AnalogueResult(base, "?", math.nan, "quantile_slice", h, 0, 0, 0, 0,
                               math.nan, math.nan, math.nan,
                               guard_note="분석용 파생 지표 없음 — 산출 보류")
                for h in horizons]
    out: list[AnalogueResult] = []
    for h in horizons:
        res = None
        for step, bins in enumerate((ANALOGUE_QUANTILE_BINS, RELAX_BINS)):
            days, cur_z = find_analogue_days_quantile(analysis[z_col], bins=bins)
            episodes = dedup_episodes(days, analysis.index, gap_trading_days=h)
            n, n_up, n_down, p10, p50, p90, years = summarize_forward(analysis, episodes, h)
            if n >= MIN_ANALOGUE_EPISODES:
                res = AnalogueResult(base, z_col, cur_z, "quantile_slice", h,
                                     int(len(days)), n, n_up, n_down, p10, p50, p90,
                                     years, case_badges_for(episodes), relax_step=step)
                break
        if res is None:
            days, cur_z = find_analogue_days_quantile(analysis[z_col])
            res = AnalogueResult(base, z_col,
                                 cur_z if cur_z == cur_z else math.nan,
                                 "quantile_slice", h, int(len(days)), 0, 0, 0,
                                 math.nan, math.nan, math.nan,
                                 guard_note=f"유사 시기 {MIN_ANALOGUE_EPISODES}회 미만"
                                            " — 산출 보류")
        out.append(res)
    return out


def build_analogue_context(
    alert_codes: list[str], top_codes: list[str],
    horizons: tuple[int, ...] = ANALOGUE_HORIZONS,
    analysis: pd.DataFrame | None = None,
) -> list[AnalogueResult]:
    """경보 변수 우선 + 중요도 상위로 보충한 변수 집합의 유사국면 실측 집계.

    analysis 미지정 시 mart 로더 사용(실패 시 빈 목록 — 호출측 정직 강등).
    """
    if analysis is None:
        try:
            from src.forecasting.variable_importance_g1 import _load_g1_feature_mart
            analysis, _levels, _t = _load_g1_feature_mart()
        except Exception as e:                                   # noqa: BLE001 — 비치명
            print(f"[정보] 유사국면 — mart 로드 불가(산출 보류): {type(e).__name__}: {e}")
            return []
    seen: set[str] = set()
    codes: list[str] = []
    for c in list(alert_codes) + list(top_codes):
        base = str(c).split("__")[0]
        if base not in seen:
            seen.add(base)
            codes.append(str(c))
        if len(codes) >= MAX_ANALOGUE_VARS:
            break
    results: list[AnalogueResult] = []
    for c in codes:
        results.extend(_analogue_for_var(analysis, c, horizons))
    return results


_H_LABEL = {5: "약 1주", 20: "약 1개월", 60: "약 3개월"}


def format_result_line(r: AnalogueResult) -> str:
    """A-191 서술 계약 — 렌더 공용 문장(필수 문구 포함·금지어 없음)."""
    if r.guard_note:
        return f"{_H_LABEL.get(r.horizon, r.horizon)}: {r.guard_note}"
    years = ", ".join(str(y) for y in r.years[:6]) + ("…" if len(r.years) > 6 else "")
    relax = " · 비교 구간을 넓혀 산출(오분위)" if r.relax_step else ""
    return (f"{_H_LABEL.get(r.horizon, r.horizon)} 후 실측: 유사 시기 {r.n_episodes}회"
            f"({years}) 중 상승 {r.n_up}회·하락 {r.n_down}회 — 변화율 중앙 {r.ret_p50:+.1f}% · "
            f"하위~상위 10% [{r.ret_p10:+.1f}%, {r.ret_p90:+.1f}%]{relax}")


def render_analogue_md(results: list[AnalogueResult]) -> list[str]:
    """월별 심층판 md 섹션 (Stage 1 — 통계 검정 없음 명기)."""
    if not results:
        return ["## 과거 유사 시기 실측 참조", "",
                "- 분석 데이터 미가용 또는 대상 변수 부재 — 산출 보류.", ""]
    lines = ["## 과거 유사 시기 실측 참조", "",
             f"변수의 표준화 지수(z)가 현재와 같은 구간이었던 과거 거래일들의 이후 실측 분포. "
             f"**{_REQUIRED_CAPTION}** (A-191 · 통계 검정 없음 — 기술 서술).", ""]
    by_var: dict[str, list[AnalogueResult]] = {}
    for r in results:
        by_var.setdefault(r.var_code, []).append(r)
    for var, rs in by_var.items():
        z_txt = f"{rs[0].current_z:+.1f}" if rs[0].current_z == rs[0].current_z else "?"
        lines.append(f"### {var} (현재 z {z_txt} · 기준 {rs[0].z_col})")
        for r in sorted(rs, key=lambda x: x.horizon):
            lines.append(f"- {format_result_line(r)}")
        badges = sorted({b for r in rs for b in r.case_badges})
        if badges:
            lines.append(f"- 겹치는 위기 사례: {' · '.join(badges)} "
                         f"(→ `_reference/soybean_oil_historical_crisis_analysis.md` — "
                         f"corrections 병독)")
            for b in badges:
                narr = case_narrative_lines(b)
                if narr:
                    lines.append(f"  - **{b} — 왜 유사한가**")
                    lines.extend(f"    - {t}" for t in narr)
        lines.append("")
    return lines


def self_test() -> list[str]:
    """합성 데이터로 계약 검증 — 문제 목록 반환(비면 통과)."""
    problems: list[str] = []
    rng = np.random.default_rng(7)
    idx = pd.bdate_range("2015-01-01", periods=1500)
    z = pd.Series(np.sin(np.arange(1500) / 40) + rng.normal(0, .3, 1500), index=idx)
    ret20 = pd.Series(rng.normal(0.01, 0.05, 1500), index=idx)
    analysis = pd.DataFrame({"TESTVAR__z90": z, "target_ret5": ret20,
                             "target_ret20": ret20, "target_ret60": ret20})
    res = build_analogue_context(["TESTVAR"], [], analysis=analysis)
    if len(res) != 3:
        problems.append(f"horizon 3종 기대, {len(res)}개 산출")
    for r in res:
        if not r.guard_note:
            # 누수 가드: 에피소드가 마지막 60거래일 안에 있으면 실패
            line = format_result_line(r)
            for w in _FORBIDDEN_WORDS:
                if w in line:
                    problems.append(f"금지어 '{w}' 발견: {line}")
    md = "\n".join(render_analogue_md(res))
    if _REQUIRED_CAPTION not in md:
        problems.append("필수 캡션 부재 (A-191)")
    # 누수 가드 직접 검증
    days, _ = find_analogue_days_quantile(analysis["TESTVAR__z90"])
    if len(days) and days.max() > idx[-EXCLUDE_RECENT_TRADING_DAYS - 1]:
        problems.append("전방 창 겹침 누수 가드 위반")
    # 표본 부족 강등 검증
    tiny = analysis.iloc[:40]
    res2 = build_analogue_context(["TESTVAR"], [], analysis=tiny)
    if not all(r.guard_note for r in res2):
        problems.append("표본 부족 시 산출 보류 미작동")
    # 사례 서사 계약 검증(A-191) — 전 프로파일 금지어·필드 완전성
    for name in CASE_PROFILES:
        narr = "\n".join(case_narrative_lines(name))
        if len(case_narrative_lines(name)) != 5:
            problems.append(f"사례 서사 필드 불완전: {name}")
        for w in _FORBIDDEN_WORDS:
            if w in narr:
                problems.append(f"사례 서사 금지어 '{w}': {name}")
    return problems


if __name__ == "__main__":
    import sys
    if "--self-test" in sys.argv:
        probs = self_test()
        if probs:
            print("[오류] 유사국면 self-test 실패:")
            for p in probs:
                print(f"  - {p}")
            sys.exit(1)
        print("[완료] 유사국면 self-test 통과")
        sys.exit(0)
    for line in render_analogue_md(build_analogue_context([], [])):
        print(line)
