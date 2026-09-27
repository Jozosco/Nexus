"""주요 변동일 원인 분해 — 교차시장 동반 변동 + 날짜가 확인된 사건 달력 (A-289 · 2026-09-27 승인자 지적 대응).

승인자 지적: 네 변동일에 같은 '당시 신호'(바이오디젤 의무혼합 요약)가 붙어 원인 분석이 비어 있었다.
원인은 두 층으로 나눠 제시한다.

1) 정량 층 — 그날 대두유 변동 중 관련 시장(에너지·대두·팜유·타 식물성유) 동반 변동으로 설명되는 몫과
   대두유 고유 잔차. 계수는 **그 날짜 이전 250거래일**만으로 추정(사후 정보 불사용). 잔차가 평소 잔차 표준편차의
   1.5배 이상이면 '대두유 고유 재료 가능성'으로 표시한다. 동반 변동은 원인 후보이지 인과 증명이 아니다
   (카놀라·팜유는 같은 식물성유 충격에 함께 반응하는 동행 지표 — '공통 식물성유 요인'으로 묶어 서술).
2) 사건 층 — `config/market_event_calendar.yaml`에 **날짜와 출처가 확인된** 사건만 등재하고, 변동일 ±1영업일 안의
   사건을 붙인다. 확인되지 않은 사건은 넣지 않는다(정직 강등: '확인된 사건 없음').
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

CALENDAR_PATH = Path("config/market_event_calendar.yaml")
BETA_WINDOW = 250
RESID_FLAG_SIGMA = 1.5

# 요인 → (원시 계열 후보 코드, 화면 라벨, 묶음)
FACTORS: list[tuple[str, list[str], str, str]] = [
    ("energy", ["TE_HEATING_OIL", "HEATING_OIL"], "난방유(경유 계열)", "에너지"),
    ("soy", ["TE_SOYBEANS", "CBOT_SOYBEANS"], "대두", "대두 복합체"),
    ("palm", ["TE_PALM_OIL", "CPO_MYR_MT"], "팜유", "경쟁 식물성유"),
    ("canola", ["TE_CANOLA"], "카놀라", "경쟁 식물성유"),
]
# 설명용 참고 시장(회귀에는 넣지 않고 동반 변동만 표시) — 공선성 큰 계열은 회귀에서 제외
REFERENCE_MARKETS: list[tuple[list[str], str]] = [
    (["TE_BRENT_CRUDE_OIL"], "브렌트유"), (["TE_GASOLINE"], "휘발유"),
    (["TE_CORN"], "옥수수"), (["TE_WHEAT"], "밀"), (["TE_BDI", "BDI"], "해상운임(BDI)"),
]


@dataclass
class Attribution:
    date: pd.Timestamp
    move_pct: float
    contributions: dict[str, float] = field(default_factory=dict)      # 라벨 → %p
    same_day: dict[str, float] = field(default_factory=dict)            # 라벨 → 그날 변동률(%)
    explained: float = float("nan")
    residual: float = float("nan")
    resid_sigma: float = float("nan")
    r2: float = float("nan")
    verdict: str = ""
    events: list[dict] = field(default_factory=list)
    note: str = ""


def _series(frames: dict[str, pd.DataFrame], codes: list[str]) -> pd.Series:
    from src.reporting.daily_brief import _dated_series
    s = _dated_series(frames, codes)
    if s.empty:
        return pd.Series(dtype=float)
    return s.set_index("price_date")["value"].astype(float)


def load_event_calendar(path: Path = CALENDAR_PATH) -> list[dict]:
    try:
        import yaml
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return list(data.get("events") or [])
    except Exception:                                          # noqa: BLE001 — 비치명(달력 없으면 사건 층 생략)
        return []


def events_near(d: pd.Timestamp, events: list[dict], bdays: int = 1) -> list[dict]:
    out = []
    for e in events:
        try:
            ed = pd.Timestamp(e["date"])
        except Exception:                                      # noqa: BLE001
            continue
        lo, hi = sorted([ed.date(), d.date()])
        if abs(int(np.busday_count(lo, hi))) <= bdays:
            out.append(e)
    return sorted(out, key=lambda e: (e.get("label", "") != "CONFIRMED", str(e.get("date"))))


def attribute_move(frames: dict[str, pd.DataFrame], d: pd.Timestamp, move_pct: float,
                   events: list[dict] | None = None) -> Attribution:
    """변동일 d의 대두유 변동을 교차시장 요인과 대두유 고유 잔차로 분해(계수는 d 이전 250거래일만)."""
    d = pd.Timestamp(d).normalize()
    att = Attribution(date=d, move_pct=float(move_pct))
    zl = _series(frames, ["CBOT_BO_CLOSE"])
    cols: dict[str, pd.Series] = {}
    labels: dict[str, str] = {}
    for key, codes, label, _grp in FACTORS:
        s = _series(frames, codes)
        if len(s) > BETA_WINDOW // 2:
            cols[key] = s
            labels[key] = label
    if zl.empty or not cols:
        att.note = "원시 계열 부족 — 분해 생략"
        att.events = events_near(d, events or [])
        return att
    df = pd.DataFrame({"ZL": zl, **cols}).sort_index()
    df = df[df.index.dayofweek < 5].ffill(limit=3)
    r = np.log(df).diff() * 100.0
    hist = r.loc[: d - pd.Timedelta(days=1)].dropna().tail(BETA_WINDOW)
    keys = list(cols)
    if len(hist) < 60 or d not in r.index:
        att.note = "분해 표본 부족 또는 그날 관측 없음"
        att.events = events_near(d, events or [])
        return att
    A = np.column_stack([np.ones(len(hist))] + [hist[k].values for k in keys])
    beta, *_ = np.linalg.lstsq(A, hist["ZL"].values, rcond=None)
    fitted = A @ beta
    resid_sd = float(np.std(hist["ZL"].values - fitted, ddof=1))
    att.r2 = float(1 - np.var(hist["ZL"].values - fitted) / np.var(hist["ZL"].values))
    x = r.loc[d].copy()
    # 자료 이상 검사(표시 전용 품질 점검): 그날 변동이 평소의 3배 이상이고 다음 관측에서 같은 크기로 되돌아가면
    # 원천 값 오류로 보고 분해에서 제외(예: 2026-08-28 팜유 −3.9% → 9/1 +7.2% → 9/2 −6.8% — 보도 종가와 불일치)
    suspects = []
    for k in keys:
        sd = hist[k].std()
        after = r[k].loc[r.index > d].dropna()
        after = after[after != 0]                              # 결측을 앞값으로 채운 0 변동은 건너뜀
        if pd.notna(x.get(k)) and sd > 0 and abs(x[k]) > 2.5 * sd and len(after) and \
                abs(after.iloc[0]) > 2.5 * sd and np.sign(after.iloc[0]) != np.sign(x[k]):
            suspects.append(labels[k])
            x[k] = 0.0
    if suspects:
        att.note = f"자료 이상 의심으로 분해에서 제외: {', '.join(suspects)}(급변 직후 같은 크기로 되돌림 — 원천 값 재확인 필요)"
    for i, k in enumerate(keys):
        if pd.notna(x.get(k)):
            att.contributions[labels[k]] = float(beta[i + 1] * x[k])
            if labels[k] not in suspects:
                att.same_day[labels[k]] = float(np.expm1(x[k] / 100.0) * 100.0)
    for codes, label in REFERENCE_MARKETS:
        s = _series(frames, codes)
        if len(s) > 2 and d in s.index:
            prev = s[s.index < d]
            if len(prev):
                att.same_day[label] = float((s.loc[d] / prev.iloc[-1] - 1) * 100.0)
    att.explained = float(sum(att.contributions.values()))
    att.residual = att.move_pct - att.explained
    att.resid_sigma = abs(att.residual) / resid_sd if resid_sd > 0 else float("nan")
    energy = att.same_day.get("난방유(경유 계열)", 0.0)
    brent = att.same_day.get("브렌트유", 0.0)
    if att.resid_sigma >= RESID_FLAG_SIGMA:
        att.verdict = "대두유 고유 재료 가능성 — 관련 시장으로 설명되지 않는 몫이 큼"
    elif abs(energy) >= 3 or abs(brent) >= 3:
        att.verdict = "에너지 시장 충격 동반 — 바이오연료 경제성 경로로 대두유에 전이된 날로 보임"
    elif abs(att.explained) >= abs(att.move_pct) * 0.6:
        att.verdict = "식물성유·곡물 시장 전반의 동반 변동"
    else:
        att.verdict = "뚜렷한 동반 시장 없음 — 원인 미확정"
    att.events = events_near(d, events or [])
    return att


def render_attribution_items(att: Attribution) -> list[str]:
    """변동일 카드용 <li> 목록(HTML 이스케이프는 호출측 _esc 사용을 전제로 텍스트만 반환)."""
    items: list[str] = []
    if att.same_day:
        top = sorted(att.same_day.items(), key=lambda kv: -abs(kv[1]))[:6]
        items.append("같은 날 관련 시장: " + " · ".join(f"{k} {v:+.1f}%" for k, v in top))
    if att.contributions and att.explained == att.explained:
        contrib = " · ".join(f"{k} {v:+.2f}%p" for k, v in sorted(att.contributions.items(), key=lambda kv: -abs(kv[1])))
        items.append(f"변동 분해: 관련 시장 동반 변동으로 {att.explained:+.2f}%p({contrib}) · 대두유 고유 {att.residual:+.2f}%p"
                     f"(평소의 {att.resid_sigma:.1f}배)")
    if att.verdict:
        items.append(f"판정: {att.verdict}")
    for e in att.events[:3]:
        src = e.get("source", "")
        lab = {"CONFIRMED": "확인", "INFERENCE": "추정"}.get(str(e.get("label", "")), str(e.get("label", "")))
        after = pd.Timestamp(e["date"]) > att.date
        head = "변동일 이후 발표(원인 아님 — 선반영 여부 미확인)" if after else f"확인된 사건({lab})"
        items.append(f"{head}·{str(e.get('date'))[5:]}: {e.get('title_ko', '')} — {src}")
    if not [e for e in att.events if pd.Timestamp(e["date"]) <= att.date]:
        items.append("날짜가 확인된 사건 없음(사건 달력 기준) — 위 분해만으로 판단")
    if att.note:
        items.append(att.note)
    return items
