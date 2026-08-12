#!/usr/bin/env python3
"""
as-of 시점 정합성 필드 부여 — 미래 정보 누수 차단의 단일 진실원천 (D-023)

핵심 규칙(CLAUDE.md §1 · .claude/rules/modeling.md):
    모델의 t일 입력값 = available_at <= t 를 만족하는 가장 최근 값

왜 필요한가 — 누수의 실제 형태:
    WASDE 2026년 8월호는 **8월 12일에 발표**된다. 그런데 `price_date=2026-08-01`로
    저장한 뒤 일별로 forward-fill 하면, 모델은 **8월 1일부터 11일까지** 아직 세상에
    존재하지 않는 값을 보게 된다. 백테스트 성능이 부풀고 실전에서 무너진다.
    관세청 확정치·PSD 연간값·GPR 월간지수 모두 같은 함정을 가진다.

5필드 정의:
    event_time     : 측정 대상 현상이 발생한 시점(관측일). 기존 price_date와 동일한 경우가 많음
    period_end     : 집계 기간의 종료일. 월간·연간 자료에만 존재(일별은 NULL)
    release_time   : 원천이 실제로 공표한 시점
    available_at   : **우리가 최초로 사용 가능했던 시점** — 모델 필터의 기준
    source_vintage : 개정본 식별자. 덮어쓰지 않고 vintage별로 적재

available_at vs release_time:
    보통 같다. 다르는 경우 — 수집 파이프라인이 일 1회만 도는데 발표가 그 이후면
    실제 사용 가능 시점은 다음 수집분이다. 보수적으로 **늦은 쪽**을 택한다.

설계 원칙:
    ① 누수보다 지연이 안전하다 — 불확실하면 available_at을 **늦게** 잡는다.
    ② 규칙은 여기 한 곳에만 둔다 — 커넥터가 각자 추정하면 정합성이 깨진다.
    ③ 원천이 발표일을 제공하면 항상 그것을 우선한다(추정 규칙은 폴백).

사용:
    from src.pipeline.asof import attach_asof
    df = attach_asof(df, source="FRED")                     # 지표별 규칙 자동 적용
    df = attach_asof(df, source="USDA_WASDE", vintage="2026-08")

의존성: pandas
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Callable, Literal

import pandas as pd

# 5필드 정식 명칭 — 스키마·검증·적재가 이 목록을 공유한다
ASOF_FIELDS: list[str] = [
    "event_time", "period_end", "release_time", "available_at", "source_vintage",
]
# 모델 진입 게이트에서 NOT NULL을 강제하는 필드
ASOF_REQUIRED: list[str] = ["event_time", "available_at"]

ReleaseKind = Literal["immediate", "lag_days", "monthly_on_day", "annual_on", "explicit"]


@dataclass(frozen=True)
class ReleaseRule:
    """소스별 발표 규칙.

    kind:
      immediate      — 관측 즉시 공개(일별 시장가격). available_at = event_time (+lag_days)
      lag_days       — 관측 후 N일 뒤 공개(재분석·주간 집계)
      monthly_on_day — 대상월 종료 후 익월 `day`일 공개(월간 통계)
      annual_on      — 대상연도 종료 후 `month`월 `day`일 공개(연간 통계)
      explicit       — 원천이 발표일을 제공 → 호출부가 release_series로 전달
    """
    kind: ReleaseKind
    lag_days: int = 0
    day: int = 1
    month: int = 1
    revises: bool = False          # 개정이 발생하는가(vintage 관리 필요)
    same_month: bool = False       # ← 아래 설명 참조
    note: str = ""

    # same_month가 필요한 이유 — 월간 자료에는 서로 다른 두 의미가 섞여 있다:
    #
    #   ① 보고서-기준(report-dated): price_date = **보고서 자체의 월**
    #      예) WASDE 2026년 8월호는 **8월 12일에 발표**된다.
    #          price_date=2026-08-01 → release=2026-08-12  (같은 달)
    #
    #   ② 기간-기준(period-dated): price_date = **측정 대상 기간**
    #      예) 2026년 8월 CPI는 **9월 중순에 발표**된다.
    #          price_date=2026-08-01 → release=2026-09-13  (익월)
    #
    # 둘을 구분하지 않으면 ①에서 발표일이 한 달 밀려 **모델이 실제로 알 수 있었던 정보를
    # 못 보게 된다**(누수의 반대 방향 오류 — 성능을 부당하게 깎는다).
    # same_month=True가 ①이다.


# ── 소스·지표별 발표 규칙 레지스트리 ─────────────────────────────────────────
# 키는 indicator_code **접두사**(긴 것 우선 매칭) 또는 source_name.
# ⚠️ 확인되지 않은 값은 보수적(늦은) 추정이며 note에 근거·검증 필요 여부를 남긴다.
RELEASE_RULES: dict[str, ReleaseRule] = {
    # ── 일별 시장가격: 관측일 장 마감 후 즉시 이용 가능 ──────────────────────
    "CBOT_BO_":  ReleaseRule("immediate", note="CME 일봉 — 당일 정산 후 공개"),
    "TE_":       ReleaseRule("immediate", note="Trading Economics 시장 시세"),
    "BDI":       ReleaseRule("immediate", note="Baltic Exchange 일별 발표(런던 시간)"),
    "BCAA":      ReleaseRule("immediate"),
    "CPO":       ReleaseRule("immediate"),
    "VIXCLS":    ReleaseRule("immediate"),

    # ── FRED 계열: 시리즈별로 지연이 다르다 ────────────────────────────────
    "DEX":       ReleaseRule("immediate", lag_days=1,
                             note="FRED 일별 환율 — 익영업일 공개. T+2 결제 규약은 별개(M-002)"),
    "FEDFUNDS":  ReleaseRule("monthly_on_day", day=8,
                             note="월평균 실효연방기금금리 — H.15 익월 초 16:15 ET. "
                                  "보수적으로 익월 8일(월말+5영업일)"),
    "CPIAUCSL":  ReleaseRule("monthly_on_day", day=16, revises=True,
                             note="美 CPI — BLS는 익월 10~15일 08:30 ET 발표. 보수적으로 16일 채택. "
                                  "매년 2월 계절조정계수 재산정으로 최근 5년 소급개정 → vintage 필수"),
    "CPI_KOREA": ReleaseRule("monthly_on_day", day=10, revises=True,
                             note="통계청 소비자물가동향 — 익월 초 08:00 KST 발표 + KOSIS DB "
                                  "반영 1~2영업일 → 익월 10일. 5년 주기 기준연도 개편 시 소급 재계산"),
    "PPOILUSDM": ReleaseRule("monthly_on_day", day=15,
                             note="World Bank Pink Sheet 계열 — 익월 중순"),

    # ── 에너지 ─────────────────────────────────────────────────────────────
    "BRENT":     ReleaseRule("immediate", lag_days=1, note="EIA 일별 현물 — 익영업일 반영"),

    # ── USDA: 발표일이 명확히 정해진 대표적 케이스 ──────────────────────────
    "WASDE_":    ReleaseRule("monthly_on_day", day=12, revises=True, same_month=True,
                             note="**보고서-기준**: WASDE 8월호는 8월 9~12일경 12:00 ET 발표. "
                                  "보수적으로 12일. 다음 호에서 직전 추정치가 개정됨 → vintage 필수"),
    "PSD_":      ReleaseRule("monthly_on_day", day=12, revises=True, same_month=True,
                             note="**보고서-기준**: PS&D는 WASDE와 동시 갱신"),
    "NASS_":     ReleaseRule("annual_on", month=1, day=12, revises=True,
                             note="Crop Production Annual Summary(1월) 기준. 품목별 상이 — 검증 필요"),
    "GATS_":     ReleaseRule("monthly_on_day", day=8, revises=True,
                             note="FAS GATS 월간 무역통계 — 익월 초순. 확정치 개정 있음"),
    "ESR_":      ReleaseRule("lag_days", lag_days=7,
                             note="FAS ESR 주간 수출판매 — 대상주 다음 목요일 08:30 ET"),
    "FAOSTAT_":  ReleaseRule("annual_on", month=7, day=1, revises=True,
                             note="FAOSTAT 연간 — 이듬해 중반 공개. 보수적 추정"),

    # ── 무역통계 ───────────────────────────────────────────────────────────
    "CUSTOMS_":  ReleaseRule("monthly_on_day", day=15, revises=True,
                             note="관세청 월간 수출입 — 익월 15일경 잠정치. **확정치 개정 있음** → vintage 필수"),
    "COMTRADE_": ReleaseRule("monthly_on_day", day=45 % 31 or 14, lag_days=45,
                             note="UN Comtrade — 회원국 보고 지연으로 수개월. 보수적 45일"),

    # ── 기후: 재분석 자료는 지연이 본질 ────────────────────────────────────
    "ONI":       ReleaseRule("monthly_on_day", day=10, revises=True,
                             note="NOAA CPC ONI — 익월 초 갱신. 3개월 이동평균이라 후속 개정 있음"),
    "temperature_2m":  ReleaseRule("lag_days", lag_days=6,
                                   note="ERA5-Land 재분석 — 통상 5일 지연. 보수적 6일"),
    "precipitation_":  ReleaseRule("lag_days", lag_days=6, note="동일(ERA5-Land)"),
    "soil_":           ReleaseRule("lag_days", lag_days=6, note="동일(ERA5-Land)"),
    "shortwave_":      ReleaseRule("lag_days", lag_days=6, note="동일(ERA5-Land)"),
    "et0_":            ReleaseRule("lag_days", lag_days=6, note="동일(ERA5-Land)"),
    "sunshine_":       ReleaseRule("lag_days", lag_days=6, note="동일(ERA5-Land)"),
    "NASA_POWER_":     ReleaseRule("lag_days", lag_days=7,
                                   note="NASA POWER — 위성 처리 지연 약 1주"),
    "USDM_":           ReleaseRule("lag_days", lag_days=5,
                                   note="US Drought Monitor — 화요일 관측, 목요일 08:30 ET 공개"),

    # ── 지정학 ─────────────────────────────────────────────────────────────
    "GPR":       ReleaseRule("monthly_on_day", day=5, revises=True,
                             note="Caldara & Iacoviello 월간 지수 — 익월 초 갱신"),
    "GDELT_":    ReleaseRule("immediate", note="GDELT는 15분 단위 갱신 — 사실상 즉시"),
    "SEISMIC_":  ReleaseRule("immediate", note="USGS 실시간"),

    # ── 비정형 파생: 문서 발행일이 곧 이용 가능 시점 ────────────────────────
    "UNSTR_":    ReleaseRule("monthly_on_day", day=20,
                             note="GAIN·FAO 월간 문서를 집계한 파생 지표. 해당 월 문서가 모두 "
                                  "나온 뒤라야 월 집계가 확정되므로 보수적으로 익월 20일"),

    # ── 시장 유동성 ────────────────────────────────────────────────────────
    "ICE_":      ReleaseRule("monthly_on_day", day=5,
                             note="ICE 월별 거래량 리포트 — 익월 초"),
}

# 원천이 발표일을 직접 제공하는 소스(그 필드를 우선 사용)
EXPLICIT_RELEASE_SOURCES: set[str] = {"USDA_WASDE_XLSX", "USDA_FAS_GAIN_PDF", "FAO_AMIS_PDF"}

_DEFAULT_RULE = ReleaseRule(
    "lag_days", lag_days=1,
    note="규칙 미등록 — 보수적 1일 지연 적용. RELEASE_RULES 등재 필요")


def rule_for(indicator_code: str, source_name: str = "") -> ReleaseRule:
    """지표코드(우선) → 소스명 순으로 가장 긴 접두사 규칙을 찾는다."""
    for key in sorted(RELEASE_RULES, key=len, reverse=True):
        if indicator_code.startswith(key) or (source_name and source_name.startswith(key)):
            return RELEASE_RULES[key]
    return _DEFAULT_RULE


def _release_for(ev: pd.Timestamp, rule: ReleaseRule) -> pd.Timestamp:
    """단일 관측의 발표 시점 산출."""
    if pd.isna(ev):
        return pd.NaT
    if rule.kind == "immediate":
        return ev + pd.Timedelta(days=rule.lag_days)
    if rule.kind == "lag_days":
        return ev + pd.Timedelta(days=rule.lag_days)
    if rule.kind == "monthly_on_day":
        if rule.same_month:
            # 보고서-기준: 그 달 `day`일에 발표 (WASDE 8월호 → 8/12)
            base = ev.normalize().replace(day=1)
        else:
            # 기간-기준: 대상월 종료 후 익월 `day`일 발표 (8월 CPI → 9/13)
            base = (ev + pd.offsets.MonthBegin(1)).normalize()
        rel = base + pd.Timedelta(days=min(rule.day, 28) - 1)
        return rel + pd.Timedelta(days=rule.lag_days)
    if rule.kind == "annual_on":
        # 대상연도 종료 후 이듬해 `month`월 `day`일
        return pd.Timestamp(year=ev.year + 1, month=rule.month,
                            day=min(rule.day, 28)) + pd.Timedelta(days=rule.lag_days)
    return ev  # explicit — 호출부가 덮어씀


def _period_end_for(ev: pd.Timestamp, rule: ReleaseRule) -> pd.Timestamp:
    """집계 기간 종료일. 일별 자료는 NaT."""
    if pd.isna(ev):
        return pd.NaT
    if rule.kind == "monthly_on_day":
        return (ev + pd.offsets.MonthEnd(0)).normalize()
    if rule.kind == "annual_on":
        return pd.Timestamp(year=ev.year, month=12, day=31)
    return pd.NaT


def attach_asof(
    df: pd.DataFrame,
    source: str = "",
    *,
    event_col: str = "price_date",
    release_series: pd.Series | None = None,
    vintage: str | None = None,
    ingest_lag_days: int = 0,
) -> pd.DataFrame:
    """DataFrame에 as-of 5필드를 부여한다.

    Args:
        df: `event_col`과 `indicator_code`를 가진 롱포맷 프레임
        source: source_name (규칙 매칭 보조)
        event_col: 관측 시점 컬럼(기본 price_date — **보존되며 삭제하지 않음**)
        release_series: 원천이 발표일을 제공할 때 그 시리즈(최우선 적용)
        vintage: 개정본 식별자. 미지정 시 개정 소스는 수집일(YYYY-MM-DD)로 대체
        ingest_lag_days: 수집 파이프라인 지연(발표를 그날 못 받는 경우)

    Returns:
        5필드가 추가된 사본. 원본은 변경하지 않는다.
    """
    if df is None or df.empty:
        return df
    out = df.copy()
    if event_col not in out.columns:
        raise ValueError(f"[오류] as-of 부여 실패: '{event_col}' 컬럼 없음 "
                         f"(보유 컬럼: {list(out.columns)[:8]})")

    ev = pd.to_datetime(out[event_col], errors="coerce")
    if hasattr(ev.dtype, "tz") and ev.dt.tz is not None:
        ev = ev.dt.tz_localize(None)
    out["event_time"] = ev

    codes = out.get("indicator_code", pd.Series([""] * len(out), index=out.index)).astype(str)
    src = str(source or "")

    # 지표코드가 소수 종류뿐이므로 코드 단위로 규칙을 한 번만 조회한다(행별 조회는 낭비)
    rules = {c: rule_for(c, src) for c in codes.unique()}

    out["period_end"] = [
        _period_end_for(e, rules[c]) for e, c in zip(ev, codes)
    ]
    # 우선순위: ①명시 전달 release_series ②**원천이 이미 제공한 release_time**(FRED ALFRED
    # 등 실측 게시일 — 추정 규칙보다 항상 우선) ③접두사 규칙 추정
    estimated = pd.Series([_release_for(e, rules[c]) for e, c in zip(ev, codes)], index=out.index)
    if release_series is not None:
        rel = pd.to_datetime(release_series, errors="coerce")
        if hasattr(rel.dtype, "tz") and rel.dt.tz is not None:
            rel = rel.dt.tz_localize(None)
        out["release_time"] = pd.Series(rel.values, index=out.index).fillna(estimated)
    elif "release_time" in df.columns:
        existing = pd.to_datetime(out["release_time"], errors="coerce")
        if hasattr(existing.dtype, "tz") and existing.dt.tz is not None:
            existing = existing.dt.tz_localize(None)
        n_kept = int(existing.notna().sum())
        if n_kept:
            print(f"[as-of] 원천 제공 발표일 {n_kept:,}건 보존(추정 규칙 미적용)")
        out["release_time"] = existing.fillna(estimated)
    else:
        out["release_time"] = estimated

    # available_at = release_time + 수집 지연. 누수 방지를 위해 event_time보다 이르지 않게 강제
    avail = pd.to_datetime(out["release_time"]) + pd.Timedelta(days=ingest_lag_days)
    out["available_at"] = avail.where(avail >= out["event_time"], out["event_time"])

    if vintage is not None:
        out["source_vintage"] = str(vintage)
    elif "source_vintage" in df.columns and out["source_vintage"].notna().any():
        pass          # 원천이 준 vintage(ALFRED realtime_start 등)를 그대로 둔다
    else:
        revises = {c for c, r in rules.items() if r.revises}
        today = date.today().isoformat()
        out["source_vintage"] = [today if c in revises else None for c in codes]

    return out


def missing_asof(df: pd.DataFrame) -> list[str]:
    """모델 게이트 위반 항목을 반환한다(빈 리스트 = 통과)."""
    problems: list[str] = []
    for f in ASOF_REQUIRED:
        if f not in df.columns:
            problems.append(f"필수 필드 없음: {f}")
        elif df[f].isna().any():
            problems.append(f"{f} 결측 {int(df[f].isna().sum()):,}건")
    if {"available_at", "event_time"} <= set(df.columns):
        inverted = (pd.to_datetime(df["available_at"]) < pd.to_datetime(df["event_time"])).sum()
        if inverted:
            problems.append(f"available_at < event_time 역전 {int(inverted):,}건")
    return problems
