#!/usr/bin/env python3
"""
4축 조달 대안 엔진 v0 — G2 운영 현실화 계층 (D-041 · WBS G2-OPS)

무엇을 만드는가:
    도착가 밴드(landed_cost.py)를 실무자의 **현실적 대안 4축**으로 번역한다.
    ①시점(지금 vs 2·4주 대기) ②커버리지(레짐별 권장 개월) ③Incoterms(CFR vs FOB+스팟)
    ④대체유지(팜·유채·해바라기 스프레드). 각 축에 정량 델타($/MT)와 온톨로지
    인과엣지(CE-ID) 근거를 병기한다.

파라미터 (competitive_differentiation §3c — 시뮬레이션 필요 파라미터 5종):
    리드타임 · 계약유형 · 가격고정 방식 · 커버리지 개월수 · 대체 전환 임계.
    ⚠️ **사내 실값(실제 계약 유형·커버리지·재고·소요량)은 런타임 입력 전용 — 저장 금지.**
    본 모듈·저장소·보고서에 사내 수치를 기록하지 않는다(D-021: 내부 데이터 전면 미사용).
    기본값은 전부 공개 문서 근거(§3c 보도 사례 · 04_supply_chain_analyst.md:115-121).

⚠️ HITL: 본 산출물은 Buy/Hold 지시가 아니다. 조건별 기대비용 차이의 **참고 정보**이며
    모든 조달 결정은 CLAUDE.md §6 HITL 게이트(인간 승인)를 통과해야 한다(§3d 주의 동일).

사용:
    python -m src.forecasting.procurement_alternatives              # 보고서 생성
    python -m src.forecasting.procurement_alternatives --self-test  # 자체검증
    python -m src.forecasting.procurement_alternatives --coverage-months 2.0   # 런타임 입력

산출: reports/market/procurement_alternatives_{date}.md
의존성: pandas · pyarrow (landed_cost 경유)
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd

from src.forecasting.landed_cost import (
    BDI_Z_SURGE,
    BDI_Z_WATCH,
    LandedCostResult,
    REPORT_DIR,
    TE_PARQUET,
    build_landed_band,
    load_cbot_usd_mt,
)

# ── 상수 ─────────────────────────────────────────────────────────────────────
WAIT_WEEKS = (2, 4)                     # ①시점 축 — 대기 시나리오(주)
Z_WINDOW_DAYS = 90                      # 대체유지 z-score 창(관측일)
Z_MIN_PERIODS = 30
CPO_SBO_THRESHOLD_USD_MT = 175.0        # CE-015 대체압력 임계 — SBO−CPO(대두유 고평가 폭) 기준
                                        # (GPT 교차검증 정정: CPO−SBO 표기는 방향 역전이었음)
SUBSTITUTE_CODES = {                    # feature mart / TE parquet 지표코드
    "팜유(CPO)": "TE_PALM_OIL",
    "유채유": "TE_RAPESEED",
    "해바라기유": "TE_SUNFLOWER_OIL",
}
# 운임 레짐 → 권장 커버리지 개월 (§3c: 평시 1~2 → 위기 3~6, 2021~22 보도 실증)
COVERAGE_BY_REGIME: dict[str, tuple[float, float]] = {
    "평시": (1.0, 2.0),
    "경계": (2.0, 3.0),
    "급등": (3.0, 6.0),
}


@dataclass
class ProcurementConfig:
    """§3c 파라미터 5종 — 사내 실값은 런타임 입력 전용(저장 금지 · D-021).

    기본값 근거(전부 공개 자료):
      lead_time_days: 남미→한국 40~45일·미국 걸프 45~50일
        (.claude/skills/phase1/04_supply_chain_analyst.md:115-121 — ontology
         supply_chain.routes와 동일 원천)
      contract_type · price_fixing: §3c 표 유형 구분(spot/term · flat/basis+fixation)
      coverage_months: 평시 1~2개월(§3c 커버리지 행)
      substitution_threshold_usd_mt: CE-015 CPO-SBO $175/MT
    """
    lead_time_min_days: int = 40
    lead_time_max_days: int = 50
    contract_type: str = "spot"                  # spot | term
    price_fixing: str = "flat"                   # flat | basis_futures
    coverage_months: float = 1.5                 # 현재 커버리지(개월) — 사내 실값 런타임 입력
    substitution_threshold_usd_mt: float = CPO_SBO_THRESHOLD_USD_MT


@dataclass
class Axis:
    """대안 축 하나 — 신호·정량 델타·인과 근거."""
    name: str
    signal: str                # 현재 관측 신호
    delta: str                 # 정량 델타 ($/MT)
    guidance: str              # 참고 방향 (지시 아님)
    causal_refs: str           # ontology causal_edges ID 인용


# ── 축별 산출 ────────────────────────────────────────────────────────────────
def axis_timing(r: LandedCostResult) -> Axis:
    """①시점 — 지금 매입 vs 2·4주 대기: 도착가 밴드의 꼬리 비대칭으로 비교.

    v0 가정: G2 모델 전이라 기대 경로는 무추세(P50 유지). 대기의 손익은 밴드
    비대칭으로 근사 — 상방 리스크(P90−P50) vs 하방 기회(P50−P10).
    리드타임(§3c) 때문에 '지금'도 도착은 40~50일 후 — 대기는 그 위에 가산된다.
    """
    up_risk = r.band_p90 - r.band_p50
    down_opp = r.band_p50 - r.band_p10
    asym = up_risk - down_opp
    tilt = "상방 꼬리 우세(대기 리스크 큼)" if asym > 0 else "하방 꼬리 우세(대기 여지 있음)"
    return Axis(
        name="①시점 (지금 vs 2·4주 대기)",
        signal=f"도착가 P50 {r.band_p50:,.0f} $/MT · 밴드 [{r.band_p10:,.0f}, "
               f"{r.band_p90:,.0f}] · 무추세 가정(G2 모델 전)",
        delta=f"상방 리스크 +{up_risk:,.0f} vs 하방 기회 −{down_opp:,.0f} $/MT "
              f"(비대칭 {asym:+,.0f} → {tilt})",
        guidance=f"대기 {WAIT_WEEKS[0]}·{WAIT_WEEKS[1]}주 시 기대비용은 P50 유지 가정 — "
                 "비대칭 부호가 대기 손익의 방향 신호",
        causal_refs="CE-001(45Z 상방) · CE-021(BRL 약세 하방) · CE-008(WASDE 이벤트 단기)")


def axis_coverage(r: LandedCostResult, cfg: ProcurementConfig) -> Axis:
    """②커버리지 — 운임 레짐(z-score)별 권장 선매입 개월(§3c 2021~22 실증 범위)."""
    lo, hi = COVERAGE_BY_REGIME[r.scenario]
    ext = max(0.0, lo - cfg.coverage_months)
    up_protect = r.band_p90 - r.band_p50
    z_label = f"{r.bdi_z:+.2f}" if r.bdi_z is not None else "미확보"
    return Axis(
        name="②커버리지 (선매입 개월수)",
        signal=f"운임 레짐 **{r.scenario}** (BDI z={z_label}) → 권장 {lo:.0f}~{hi:.0f}개월 "
               f"(현재 입력값 {cfg.coverage_months:.1f}개월)",
        delta=f"1개월 연장 시 단위 물량당 선확정 {r.band_p50:,.0f} $/MT · "
              f"상방 보호 기대 최대 +{up_protect:,.0f} $/MT (권장 하한까지 부족 {ext:.1f}개월)",
        guidance="레짐 악화(경계→급등) 시 커버리지 연장이 §3c 실수요자 대응 1순위였음(2021~22)",
        causal_refs="CE-010(해협→운임→CIF) · CE-016(BDI→수출 채산성) · CE-006(라니냐 공급)")


def axis_incoterms(r: LandedCostResult, cfg: ProcurementConfig) -> Axis:
    """③Incoterms — §3d 판정 로직 이식: BDI z 레짐별 CFR 유지 vs FOB+스팟 비교."""
    freight_exposure = r.basis.p90 - r.basis.p50          # 운임 급등 시 추가 노출 근사
    if r.bdi_z is not None and r.bdi_z > BDI_Z_SURGE:
        judgement = ("급등 레짐: **기존 CFR term 유지**(운임 상승분 매도인 고정) · "
                     "신규 계약은 CFR 호가 프리미엄 vs FOB+스팟 실측 비교")
    elif r.bdi_z is not None and r.bdi_z > BDI_Z_WATCH:
        judgement = "경계 레짐: CFR 유지 + FOB 견적 병행 수집(급등 대비 협상 준비)"
    else:
        judgement = ("평시 레짐: FOB+운임 직접 계약 검토 — basis·운임 각층 최저가 조합 "
                     "절감 여지(§3d 평시 복귀 분기)")
    return Axis(
        name="③Incoterms (CFR 유지 vs FOB+스팟)",
        signal=f"운임 레짐 {r.scenario} · 임계 z>{BDI_Z_WATCH:.0f} 경계 / "
               f"z>{BDI_Z_SURGE:.0f} 급등 (§3d)",
        delta=f"내재층 P90−P50 = +{freight_exposure:,.0f} $/MT — 급등 레짐 전환 시 "
              f"신규 CFR 호가에 가산될 운임 프리미엄 근사 (계약유형 입력: {cfg.contract_type} · "
              f"가격고정 입력: {cfg.price_fixing})",
        guidance=judgement + " — BCAA 실측(§5 유료 승인) 전 BDI 프록시 판정임",
        causal_refs="CE-010(호르무즈·말라카) · CE-013(수에즈 우회 선복) — "
                    "ontology supply_chain.routes 전파 구조")


def _rolling_z_last(s: pd.Series) -> float | None:
    if len(s) < Z_MIN_PERIODS:
        return None
    mean = s.rolling(Z_WINDOW_DAYS, min_periods=Z_MIN_PERIODS).mean()
    std = s.rolling(Z_WINDOW_DAYS, min_periods=Z_MIN_PERIODS).std()
    z = ((s - mean) / std.where(std > 0)).dropna()
    return float(z.iloc[-1]) if len(z) else None


def axis_substitutes(cfg: ProcurementConfig) -> tuple[Axis, list[dict]]:
    """④대체유지 — TE 팜·유채·해바라기 vs CBOT 스프레드 현황·임계.

    USD/MT 스프레드는 D8 단위 정규화(converted=True) 행에서만 산출한다 —
    FX 미확보 시 자체 통화 z-score(무차원 상대 모멘텀)로 대체하고 상태를 명시한다
    (왜곡 금지: 미확보 환율로 임의 환산하지 않음, D4·D8 원칙).
    """
    cbot_daily, _, _ = load_cbot_usd_mt()
    cbot_z = _rolling_z_last(cbot_daily)
    rows: list[dict] = []
    spread_available = False
    if TE_PARQUET.exists():
        te = pd.read_parquet(TE_PARQUET)
        for label, code in SUBSTITUTE_CODES.items():
            sub = te[te["indicator_code"] == code].sort_values("price_date")
            if sub.empty:
                rows.append({"대체유지": label, "상태": "❓ 미수집", "z격차": "—",
                             "스프레드": "—", "최종관측": "—"})
                continue
            s = sub.set_index(pd.to_datetime(sub["price_date"]))["value"].astype(float)
            sub_z = _rolling_z_last(s)
            conv = sub[sub["converted"].fillna(False)]
            if len(conv):
                spread_available = True
                usd = conv.set_index(pd.to_datetime(conv["price_date"]))["value_usd_mt"]
                common = pd.concat([usd.resample("MS").mean(),
                                    cbot_daily.resample("MS").mean()], axis=1).dropna()
                spread_txt = (f"{common.iloc[-1, 0] - common.iloc[-1, 1]:+,.0f} $/MT"
                              if len(common) else "공통 월 없음")
            else:
                spread_txt = "환산 미확보(FX parquet 부재 — CI 재실행 시 산출)"
            gap = (f"{sub_z - cbot_z:+.2f}" if sub_z is not None and cbot_z is not None
                   else "표본 부족")
            rows.append({"대체유지": label,
                         "상태": f"단위 {sub.iloc[-1]['unit']}",
                         "z격차": gap, "스프레드": spread_txt,
                         "최종관측": str(s.index[-1].date())})
    spread_note = ("USD/MT 스프레드 산출 가능" if spread_available
                   else "USD/MT 스프레드 전량 환산 대기(D8 FX 미확보) — z격차(무차원)로 대체")
    axis = Axis(
        name="④대체유지 (팜·유채·해바라기 스프레드)",
        signal=f"CBOT 90일 z={cbot_z:+.2f} 대비 대체유지 z격차 관측 · {spread_note}",
        delta=f"전환 임계: SBO−CPO 스프레드 > {cfg.substitution_threshold_usd_mt:,.0f} $/MT "
              f"(SBO가 팜유 대비 임계 이상 고평가 시 배합 전환 검토 — GPT 교차검증 부호 정정)"
              "(CE-015 — 통계 검증 대기) · 관세청 대체유 9품목 실측 CIF는 GW 확장수집 "
              "완료 후 병행(A-161: 현재 템플릿만 존재)",
        guidance="z격차 음수(대체유가 SBO보다 약세)가 지속되면 배합 전환 검토 신호 — "
                 "실제 전환은 품질 규격(§3b)·정제 설비 제약 확인 필요",
        causal_refs="CE-015(CPO 대체압력) · CE-002(B40→스프레드 축소) · CE-014(해바라기 차단)")
    return axis, rows


# ── 보고서 ───────────────────────────────────────────────────────────────────
HITL_NOTICE = """## ⚠️ HITL 고지 (필수)

**본 문서는 Buy/Hold 지시가 아님.** 4축 대안은 조건별 기대비용 차이의 참고 정보이며,
실제 Incoterms·계약 선택에는 매도인 협상·항만 사정 등 비가격 요인이 큼(§3d 주의).
모든 조달 의사결정은 **CLAUDE.md §6 HITL 게이트**(Explore→Plan→Validate→Execute,
인간 승인 필수)를 통과해야 하며, AI는 권고만 하고 실행하지 않음."""


def render_md(r: LandedCostResult, axes: list[Axis], sub_rows: list[dict],
              cfg: ProcurementConfig) -> str:
    today = date.today()
    lines = [
        f"# 4축 조달 대안 v0 — {today}",
        "",
        "> G2 운영 현실화 계층(D-041). 도착가 밴드(landed_cost_band 동일 일자 보고서)를",
        "> 실무자 대안 4축으로 번역함. 각 델타는 $/MT 단위 정량값 + 인과엣지(CE-ID) 근거.",
        "",
        "## 4축 요약",
        "",
        "| 축 | 현재 신호 | 정량 델타 ($/MT) | 참고 방향 | 인과 근거 |",
        "|---|---|---|---|---|",
    ]
    for ax in axes:
        lines.append(f"| {ax.name} | {ax.signal} | {ax.delta} | {ax.guidance} "
                     f"| {ax.causal_refs} |")
    lines += [
        "",
        "## ④대체유지 상세",
        "",
        "| 대체유지 | 단위(원계열) | 90일 z격차 (대체유−CBOT) | USD/MT 스프레드 | 최종 관측 |",
        "|---|---|---|---|---|",
    ]
    for row in sub_rows:
        lines.append(f"| {row['대체유지']} | {row['상태']} | {row['z격차']} "
                     f"| {row['스프레드']} | {row['최종관측']} |")
    lines += [
        "",
        "## 입력 파라미터 (§3c 5종 — 사내 실값은 런타임 입력 전용·저장 금지)",
        "",
        "| 파라미터 | 값 | 근거 |",
        "|---|---|---|",
        f"| 물리 리드타임 | {cfg.lead_time_min_days}~{cfg.lead_time_max_days}일 "
        "| 04_supply_chain_analyst.md:115-121 · ontology supply_chain.routes |",
        f"| 계약 유형 | {cfg.contract_type} | §3c (spot/term) — 기본값(사내 실값 아님) |",
        f"| 가격 고정 방식 | {cfg.price_fixing} | §3c (flat/basis+fixation) — 기본값 |",
        f"| 커버리지 개월수 | {cfg.coverage_months:.1f} | §3c 평시 1~2개월 — 기본값 |",
        f"| 대체 전환 임계 | {cfg.substitution_threshold_usd_mt:,.0f} $/MT | CE-015 |",
        "",
        "## 신선도·한계",
        "",
        f"- 도착가 밴드 원천: `reports/market/landed_cost_band_{today}.md` 참조"
        "(CBOT·관세청 CIF·BDI 신선도 각주 동일 적용).",
        "- Incoterms 판정은 BCAA 실측 확보(§5 유료 승인) 전 BDI 프록시 기반임.",
        "- ①시점 축은 무추세 가정 — G2 분위수 모델 산출 후 기대 경로 기반으로 갱신 예정.",
        "",
        HITL_NOTICE,
        "",
    ]
    return "\n".join(lines)


# ── 자체검증 ─────────────────────────────────────────────────────────────────
def self_test(axes: list[Axis], sub_rows: list[dict]) -> list[str]:
    problems: list[str] = []
    if len(axes) != 4:
        problems.append(f"4축 미충족 — {len(axes)}축 생성")
    for ax in axes:
        if not (ax.signal and ax.delta and ax.causal_refs):
            problems.append(f"{ax.name} — 신호/델타/인과 근거 누락")
        if "CE-" not in ax.causal_refs:
            problems.append(f"{ax.name} — 인과엣지 ID 인용 없음")
    if not sub_rows:
        problems.append("④대체유지 상세 행 0건")
    return problems


def _build_config(a: argparse.Namespace) -> ProcurementConfig:
    if a.config:
        raw = json.loads(Path(a.config).read_text(encoding="utf-8"))
        return ProcurementConfig(**raw)
    return ProcurementConfig(
        lead_time_min_days=a.lead_time_min, lead_time_max_days=a.lead_time_max,
        contract_type=a.contract_type, price_fixing=a.price_fixing,
        coverage_months=a.coverage_months,
        substitution_threshold_usd_mt=a.substitution_threshold)


def main() -> int:
    ap = argparse.ArgumentParser(description="4축 조달 대안 엔진 v0 (§3c 파라미터는 런타임 입력)")
    ap.add_argument("--config", help="§3c 파라미터 JSON 경로(사내 실값 — 저장 금지)")
    ap.add_argument("--lead-time-min", type=int, default=40)
    ap.add_argument("--lead-time-max", type=int, default=50)
    ap.add_argument("--contract-type", default="spot", choices=["spot", "term"])
    ap.add_argument("--price-fixing", default="flat", choices=["flat", "basis_futures"])
    ap.add_argument("--coverage-months", type=float, default=1.5)
    ap.add_argument("--substitution-threshold", type=float, default=CPO_SBO_THRESHOLD_USD_MT)
    ap.add_argument("--self-test", action="store_true", help="자체검증만 수행")
    a = ap.parse_args()
    cfg = _build_config(a)

    print("[4축 대안] 도착가 밴드 로드(landed_cost) — 전부 외부 데이터(D-021)")
    r = build_landed_band()
    ax4, sub_rows = axis_substitutes(cfg)
    axes = [axis_timing(r), axis_coverage(r, cfg), axis_incoterms(r, cfg), ax4]
    for ax in axes:
        print(f"  {ax.name}: {ax.delta}")

    problems = self_test(axes, sub_rows)
    for p in problems:
        print(f"  🚨 {p}")
    if problems:
        print("[중단] 자체검증 실패 — 보고서를 저장하지 않습니다.")
        return 1
    print("  ✅ 자체검증 통과 (4축 · 델타 · CE 인용 · 대체유지 상세)")
    if a.self_test:
        return 0

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / f"procurement_alternatives_{date.today()}.md"
    out.write_text(render_md(r, axes, sub_rows, cfg), encoding="utf-8")
    print(f"[완료] 보고서 → {out} (HITL 고지 포함)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
