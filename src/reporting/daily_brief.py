"""G1 일별 브리프 렌더러 — 목업 v2(A-225·A-227) 구조의 실데이터 결선.

조정자 승인(2026-08-28) 후 실통합. 설계 원칙:
  - 7블록: E1 신뢰 스트립 → 한눈 요약(KPI) → 가격 추세·핵심 변인 → 금일 경보 →
    공급 경로 → 지표 스냅샷 → 언론·매체 → 주목 일정 → 부록(전문 기관)
  - 각 블록 4단 요약([현황]→[요인]→[전망]→[유의·권고]) — 규칙 기반 문장(LLM 미사용)
  - 차트·스파크라인·경로 모식도는 **서버측 SVG 생성**(JS 의존 0 — PDF 변환·CI 렌더 안전)
  - 토글(산출 근거·온톨로지 연결)은 순수 HTML <details> — 스크립트 0
  - 결측은 "미수집" 정직 표기(위장 금지) — 블록 단위 우아한 강등
  - 참고 범위 명칭·한계 캡션 상시(A-191) · HITL 고지(CLAUDE.md §6)
"""
from __future__ import annotations

import html as _html
import os
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SIGNALS_CSV = Path("data/processed/unstructured_daily_signals.csv")
LB_PER_MT = 2204.62262            # USc/lb → $/MT 환산 (×22.0462)

# WASDE 발표 예정일 (USDA 공표 일정 — 확정 시 갱신)
WASDE_SCHEDULE = [date(2026, 9, 11), date(2026, 10, 9), date(2026, 11, 10), date(2026, 12, 10)]
POLICY_MILESTONES = [
    (date(2027, 1, 1), "아르헨 수출세 월별 인하 개시", "Decree 423/2026 · 24%→15% 경로"),
]
LEADTIME_DAYS = 50                # CIF 한국 리드타임 상단(40~50일) 보수 적용

# 변인 코드 → 한국어 표시명 (미등재 코드는 원 코드 노출)
VAR_LABELS: dict[str, str] = {
    "CBOT_BO_CLOSE": "CBOT 대두유(ZL) 종가",
    "TE_BDI": "BDI 해상운임지수", "BDI": "BDI 해상운임지수", "BDI_ZSCORE": "BDI 해상운임지수",
    "DEXBZUS": "브라질 헤알 환율(BRL/USD)", "DEXCHUS": "위안 환율(CNY/USD)",
    "DEXKOUS": "원/달러 환율", "VIXCLS": "VIX 변동성",
    "GPR_NORMALIZED": "지정학 위험(GPR 정규화)", "GPR": "지정학 위험(GPR)",
    "ENSO_ONI": "ENSO ONI(엘니뇨 지수)", "ONI": "ENSO ONI(엘니뇨 지수)",
    "CPO_SBO_SPREAD": "대두유−팜유 가격 차이", "WASDE_SBO_STU": "WASDE 재고사용비율",
    "TE_PALM_OIL": "CPO 팜유(TE)", "TE_SOYBEANS": "CBOT 대두(TE)",
    "FEDFUNDS": "미 기준금리", "CPIAUCSL": "미 CPI",
}

# 변인 키워드 → 기사 매칭 (별점) — 규칙 기반(Phase B에서 LLM 매핑 검토)
_DRIVER_KEYWORDS: dict[str, list[str]] = {
    "RVO": ["rvo", "rin", "biodiesel", "renewable diesel", "biofuel", "epa",
            "바이오디젤", "바이오연료", "재생디젤"],
    "BIODIESEL": ["biodiesel", "biofuel", "b40", "b50", "바이오디젤", "바이오연료"],
    "CPO": ["palm", "mpob", "팜유", "올레인"],
    "PALM": ["palm", "mpob", "팜유"],
    "BDI": ["freight", "shipping", "bdi", "운임", "해운"],
    "DEXBZUS": ["brazil", "real", "브라질", "헤알"],
    "BRL": ["brazil", "real", "브라질", "헤알"],
    "ARG": ["argentin", "export tax", "아르헨", "수출세", "rosario", "로사리오"],
    "EXPORT_TAX": ["argentin", "export tax", "수출세"],
    "ONI": ["el nino", "la nina", "enso", "drought", "엘니뇨", "라니냐", "가뭄"],
    "ENSO": ["el nino", "la nina", "enso", "drought", "엘니뇨", "라니냐", "가뭄"],
    "WASDE": ["wasde", "usda"],
    "STU": ["wasde", "stocks", "재고"],
    "HORMUZ": ["hormuz", "strait", "호르무즈", "해협"],
    "VIX": ["volatility", "vix", "변동성"],
    "CBOT": ["soybean oil", "soyoil", "cbot", "대두유"],
}

# 일별 비정형 지표 → 온톨로지 체인 (signal_tag_mapping·CE evidence 기반 정적 렌더 —
# 실검증 상태는 ontology.yaml이 원천, 여기서는 표시용 최소 사본)
_ONTOLOGY_CHAINS: dict[str, list[str]] = {
    "BIODIESEL_MANDATE_NEWS": ["기사", "신호: 바이오연료 수요", "CE-022 (검증됨)",
                               "바이오연료 의무량", "SBO 수요 ▲", "가격 상방"],
    "ARG_EXPORT_TAX_NEWS": ["기사", "신호: 수출세 경로", "CE-003 (검증됨)",
                            "아르헨 수출 물량", "공급 회복", "가격 하방"],
    "INDIA_DUTY_NEWS": ["기사", "신호: 수입관세", "CE-004 (후보)",
                        "인도 수입 수요", "수요 변동", "방향 조건부"],
    "HORMUZ_THREAT_LEVEL": ["AIS·프록시 관측", "해협 위험 지수", "CE-013 (검증됨)",
                            "운임·전쟁보험료", "도착가 잔차층", "참고 범위 폭"],
    "SUEZ_RED_SEA_RISK": ["관측", "해협 위험 지수", "CE-014 (검증됨)",
                          "우회 항로(+12~15일)", "운임 상승", "도착가 상방"],
    "US_CHINA_TARIFF_STATUS": ["기사", "신호: 무역 정책", "CE-009 (검증됨)",
                               "미중 교역 흐름", "대두 수급 재편", "방향 조건부"],
}


# ── 데이터 추출 헬퍼 ──────────────────────────────────────────────────────────

def _dated_series(frames: dict[str, pd.DataFrame], codes: list[str]) -> pd.DataFrame:
    """indicator_code 우선순위 목록에서 (date, value) 시계열 추출 — 일자 중복은 최신 유지."""
    for code in codes:
        parts = []
        for df in frames.values():
            if "indicator_code" not in df.columns or "value" not in df.columns:
                continue
            sub = df[df["indicator_code"] == code]
            if not sub.empty and "price_date" in sub.columns:
                parts.append(sub[["price_date", "value"]])
        if not parts:
            continue
        merged = pd.concat(parts, ignore_index=True)
        merged["price_date"] = pd.to_datetime(merged["price_date"], errors="coerce")
        merged["value"] = pd.to_numeric(merged["value"], errors="coerce")
        merged = (merged.dropna().sort_values("price_date")
                  .drop_duplicates("price_date", keep="last").reset_index(drop=True))
        if not merged.empty:
            return merged
    return pd.DataFrame(columns=["price_date", "value"])


def _pct(a: float, b: float) -> float | None:
    return (a / b - 1.0) * 100.0 if b else None


def _z90(vals: pd.Series) -> float | None:
    if len(vals) < 30:
        return None
    win = vals.tail(90)
    sd = win.std()
    return float((vals.iloc[-1] - win.mean()) / sd) if sd and sd > 0 else None


@dataclass
class CloseKpi:
    close: float
    chg_abs: float | None
    chg_pct: float | None
    wk_pct: float | None
    z90: float | None
    last_date: date
    series: pd.DataFrame          # 최근 90관측 (date, value)


def _kpi_close(frames: dict[str, pd.DataFrame]) -> CloseKpi | None:
    s = _dated_series(frames, ["CBOT_BO_CLOSE"])
    if len(s) < 2:
        return None
    v = s["value"]
    close = float(v.iloc[-1])
    prev = float(v.iloc[-2])
    wk = float(v.iloc[-6]) if len(v) >= 6 else None
    return CloseKpi(
        close=close, chg_abs=close - prev, chg_pct=_pct(close, prev),
        wk_pct=_pct(close, wk) if wk else None, z90=_z90(v),
        last_date=s["price_date"].iloc[-1].date(), series=s.tail(90).reset_index(drop=True))


def _reference_range_usclb(close_hist: pd.Series, horizon: int = 60
                           ) -> tuple[float, float, float] | None:
    """기준 가격층 — 과거 60거래일 수익률 분포 분위를 최근 종가에 적용 (참고 범위)."""
    v = close_hist.dropna()
    if len(v) < horizon + 60:
        return None
    rets = v.pct_change(periods=horizon).dropna()
    if len(rets) < 30:
        return None
    last = float(v.iloc[-1])
    q10, q50, q90 = (float(rets.quantile(q)) for q in (0.10, 0.50, 0.90))
    return (last * (1 + q10), last * (1 + q50), last * (1 + q90))


def _landed_band() -> tuple[float, float, float] | None:
    """참고 도착가 범위($/MT) — landed_cost 산출과 직접 연동. 실패 시 None(정직 강등)."""
    try:
        from src.forecasting.landed_cost import build_landed_band
        r = build_landed_band()
        return (float(r.band_p10), float(r.band_p50), float(r.band_p90))
    except Exception as e:                                    # noqa: BLE001 — 비치명 강등
        print(f"[정보] 참고 도착가 범위 산출 불가(비치명): {type(e).__name__}: {e}")
        return None


def _load_signals(days: int = 3) -> pd.DataFrame:
    """일별 비정형 신호 아카이브(A-181)에서 최근 N일 로드."""
    if not SIGNALS_CSV.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(SIGNALS_CSV)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        cutoff = pd.Timestamp(date.today() - timedelta(days=days))
        return df[df["date"] >= cutoff].sort_values("date", ascending=False)
    except Exception as e:                                    # noqa: BLE001
        print(f"[경고] 일별 신호 아카이브 로드 실패(비치명): {e}")
        return pd.DataFrame()


_URL_RE = re.compile(r"https?://[^\s\"'<>\)\]]+")


def _first_url(text: str) -> str | None:
    m = _URL_RE.search(str(text))
    return m.group(0).rstrip(".,;") if m else None


def _match_articles(var_code: str, signals: pd.DataFrame) -> list[dict]:
    """변인 코드 ↔ 최근 기사 키워드 매칭 — 별점 재료."""
    kws: list[str] = []
    up = var_code.upper()
    for key, words in _DRIVER_KEYWORDS.items():
        if key in up:
            kws.extend(words)
    if not kws or signals.empty:
        return []
    out = []
    for _, row in signals.iterrows():
        blob = f"{row.get('indicator', '')} {row.get('note', '')}".lower()
        hits = sum(1 for w in kws if w in blob)
        if hits:
            out.append({"hits": hits, "note": str(row.get("note", ""))[:160],
                        "indicator": row.get("indicator", ""),
                        "source": row.get("source_name", ""),
                        "url": _first_url(row.get("note", ""))})
    return sorted(out, key=lambda d: -d["hits"])[:3]


# ── SVG 생성 (서버측 — JS 0) ─────────────────────────────────────────────────

_INFLECTION_MARKS = "①②③④⑤"


def _inflection_points(kpi: CloseKpi, top_n: int = 4) -> list[dict]:
    """표시 구간(최근 90관측) 내 |일간 변화율| 상위 급변일 검출 — 사실 기술 전용 (W-C).

    기준: 표시 구간 일간 변화율 표준편차의 1.5배(최소 1.0%) 이상인 날 중 상위 top_n.
    """
    v = kpi.series["value"].astype(float)
    ret = v.pct_change() * 100.0
    if ret.notna().sum() < 20:
        return []
    sd = float(ret.std())
    if not sd or sd <= 0:
        return []
    thr = max(1.5 * sd, 1.0)
    cand = ret[ret.abs() >= thr]
    picks = sorted(cand.abs().sort_values(ascending=False).head(top_n).index)
    out = []
    for k, i in enumerate(picks):
        out.append({"i": int(i), "no": _INFLECTION_MARKS[k],
                    "date": kpi.series["price_date"].iloc[int(i)],
                    "chg": float(ret.iloc[int(i)]), "close": float(v.iloc[int(i)])})
    return out


def _signals_around(center: pd.Timestamp, window_days: int = 2) -> pd.DataFrame:
    """일별 신호 아카이브에서 특정일 ±window 신호 로드 — 아카이브 밖 날짜는 빈 결과."""
    if not SIGNALS_CSV.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(SIGNALS_CSV)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        lo = center - pd.Timedelta(days=window_days)
        hi = center + pd.Timedelta(days=window_days)
        return df[(df["date"] >= lo) & (df["date"] <= hi)].sort_values("date")
    except Exception as e:                                    # noqa: BLE001 — 비치명
        print(f"[경고] 신호 아카이브 구간 조회 실패(비치명): {e}")
        return pd.DataFrame()


def _svg_price_chart(kpi: CloseKpi, rng: tuple[float, float, float] | None,
                     horizon: int = 60, marks: list[dict] | None = None) -> str:
    s = kpi.series
    hist = s["value"].tolist()
    n = len(hist)
    fwd = 20                                            # 팬 표시 해상도(전망 60거래일 축약)
    W, H, padL, padR, padT, padB = 560, 260, 44, 40, 14, 34
    total = n + fwd - 1
    if rng:
        p10e, p50e, p90e = rng
        lo = min(min(hist), p10e) * 0.985
        hi = max(max(hist), p90e) * 1.015
    else:
        lo, hi = min(hist) * 0.985, max(hist) * 1.015

    def x(i: float) -> float:
        return padL + (W - padL - padR) * i / total

    def y(v: float) -> float:
        return padT + (H - padT - padB) * (1 - (v - lo) / (hi - lo))

    grid = []
    step = max(round((hi - lo) / 5, 1), 0.5)
    g = np.arange(np.ceil(lo / step) * step, hi, step)
    for v in g:
        grid.append(f'<line x1="{padL}" x2="{W - padR}" y1="{y(v):.1f}" y2="{y(v):.1f}" '
                    f'stroke="var(--line)" stroke-width="1"/>'
                    f'<text x="{padL - 6}" y="{y(v) + 4:.1f}" font-size="10" '
                    f'fill="var(--ink3)" text-anchor="end">{v:.1f}</text>')
    line = " ".join(f"{'M' if i == 0 else 'L'}{x(i):.1f} {y(v):.1f}" for i, v in enumerate(hist))
    start_lbl = s["price_date"].iloc[0].strftime("%m-%d")
    today_lbl = kpi.last_date.strftime("%m-%d")
    end_date = np.busday_offset(kpi.last_date, horizon, roll="forward")
    end_lbl = pd.Timestamp(end_date).strftime("%m-%d")
    parts = ["".join(grid),
             f'<line x1="{x(n - 1):.1f}" x2="{x(n - 1):.1f}" y1="{padT}" y2="{H - padB}" '
             f'stroke="var(--ink3)" stroke-width="1" stroke-dasharray="3 3"/>']
    if rng:
        last = hist[-1]
        p10e, p50e, p90e = rng
        p10s, p50s, p90s = [], [], []
        for k in range(fwd):
            t = k / (fwd - 1)
            tw = t ** 0.5
            p50s.append(last + (p50e - last) * t)
            p10s.append(last + (p10e - last) * tw)
            p90s.append(last + (p90e - last) * tw)
        band = f"M{x(n - 1):.1f} {y(p10s[0]):.1f}"
        for i in range(1, fwd):
            band += f" L{x(n - 1 + i):.1f} {y(p10s[i]):.1f}"
        for i in range(fwd - 1, -1, -1):
            band += f" L{x(n - 1 + i):.1f} {y(p90s[i]):.1f}"
        band += " Z"
        p50path = " ".join(f"{'M' if i == 0 else 'L'}{x(n - 1 + i):.1f} {y(v):.1f}"
                           for i, v in enumerate(p50s))
        parts.append(f'<path d="{band}" fill="var(--band2)"/>')
        parts.append(f'<path d="{p50path}" fill="none" stroke="var(--accent)" '
                     f'stroke-width="2" stroke-dasharray="5 4"/>')
        parts.append(f'<text x="{x(total) + 2:.1f}" y="{y(p90e) + 3:.1f}" font-size="10" '
                     f'fill="var(--ink3)">{p90e:.2f}</text>'
                     f'<text x="{x(total) + 2:.1f}" y="{y(p50e) + 3:.1f}" font-size="10" '
                     f'fill="var(--accent)" font-weight="700">{p50e:.2f}</text>'
                     f'<text x="{x(total) + 2:.1f}" y="{y(p10e) + 3:.1f}" font-size="10" '
                     f'fill="var(--ink3)">{p10e:.2f}</text>')
        parts.append(f'<text x="{x(n - 1 + fwd / 2):.1f}" y="{padT + 10}" font-size="10" '
                     f'fill="var(--ink3)" text-anchor="middle">전망 약 90일({horizon}거래일)</text>')
    parts.append(f'<path d="{line}" fill="none" stroke="var(--accent)" stroke-width="2"/>')
    # W-C: 급변일 마커 — 번호는 아래 '주요 변동일' 목록과 1:1 대응
    for k, m in enumerate(marks or []):
        mi = m["i"]
        if not (0 <= mi < n):
            continue
        col = "var(--up)" if m["chg"] > 0 else "var(--down)"
        mx, my = x(mi), y(hist[mi])
        ly_off = -10 if (k % 2 == 0) else 18
        parts.append(
            f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="4.5" fill="{col}" '
            f'stroke="var(--surface)" stroke-width="1.5"/>'
            f'<text x="{mx:.1f}" y="{my + ly_off:.1f}" font-size="11" font-weight="700" '
            f'fill="{col}" text-anchor="middle">{m["no"]}</text>')
    parts.append(f'<text x="{x(0):.1f}" y="{H - 8}" font-size="10" fill="var(--ink3)">{start_lbl}</text>'
                 f'<text x="{x(n - 1):.1f}" y="{H - 8}" font-size="10" fill="var(--ink3)" '
                 f'text-anchor="middle">{today_lbl} (기준일)</text>'
                 f'<text x="{x(total):.1f}" y="{H - 8}" font-size="10" fill="var(--ink3)" '
                 f'text-anchor="end">{end_lbl}</text>')
    return (f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto;display:block" '
            f'role="img" aria-label="CBOT ZL 종가 추이와 {horizon}거래일 참고 범위">'
            + "".join(parts) + "</svg>")


def _svg_spark(vals: list[float]) -> str:
    if len(vals) < 2:
        return ""
    W, H = 90, 26
    lo, hi = min(vals), max(vals)
    sp = (hi - lo) or 1.0
    pts = " ".join(f"{4 + (W - 8) * i / (len(vals) - 1):.1f},"
                   f"{4 + (H - 8) * (1 - (v - lo) / sp):.1f}" for i, v in enumerate(vals))
    lx, ly = pts.rsplit(" ", 1)[-1].split(",")
    return (f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<polyline points="{pts}" fill="none" stroke="var(--ink3)" stroke-width="1.5"/>'
            f'<circle cx="{lx}" cy="{ly}" r="2.5" fill="var(--accent)"/></svg>')


def _route_status(frames: dict[str, pd.DataFrame]) -> dict[str, str]:
    """해협 상태 — 실지표 연동(1=ok·2=warn·3=crit), 미수집은 unknown."""
    def level(codes: list[str]) -> str:
        s = _dated_series(frames, codes)
        if s.empty:
            return "unknown"
        v = float(s["value"].iloc[-1])
        return "crit" if v >= 3 else ("warn" if v >= 2 else "ok")
    return {"hormuz": level(["HORMUZ_THREAT_LEVEL"]),
            "suez": level(["SUEZ_RED_SEA_RISK"]),
            "panama": "ok", "malacca": "ok",       # 전용 지표 부재 — 복합 지수로 보완
            "composite": _fmt_last(frames, ["SBO_STRAIT_RISK_COMPOSITE"], "{:.0f}")}


def _fmt_last(frames: dict, codes: list[str], fmt: str) -> str:
    s = _dated_series(frames, codes)
    return fmt.format(float(s["value"].iloc[-1])) if not s.empty else "—"


def _svg_route_map(st: dict[str, str]) -> str:
    col = {"ok": "var(--ok)", "warn": "var(--warn)", "crit": "var(--crit)",
           "unknown": "var(--ink3)"}
    P = {"usg": (210, 95), "bra": (300, 185), "arg": (270, 215), "mys": (700, 165),
         "kor": (880, 80), "panama": (235, 140), "suez": (500, 105),
         "hormuz": (585, 115), "malacca": (715, 150)}
    W, H = 1000, 250

    def arc(a, b, bend):
        return (f"M{a[0]} {a[1]} Q{(a[0] + b[0]) / 2:.0f} "
                f"{(a[1] + b[1]) / 2 + bend:.0f} {b[0]} {b[1]}")

    grid = "".join(f'<line x1="{x}" y1="18" x2="{x}" y2="{H - 18}" stroke="var(--line)" '
                   f'stroke-width="1" opacity=".5"/>' for x in range(60, W, 94))
    grid += "".join(f'<line x1="30" y1="{y}" x2="{W - 30}" y2="{y}" stroke="var(--line)" '
                    f'stroke-width="1" opacity=".5"/>' for y in range(40, H - 10, 44))
    routes = "".join(f'<path d="{arc(P[a], P["kor"], b)}" fill="none" stroke="var(--accent)" '
                     f'stroke-width="1.5" stroke-dasharray="6 5" opacity=".55"/>'
                     for a, b in [("usg", -70), ("bra", 55), ("arg", 90), ("mys", 25)])

    def origin(key, label, sub):
        px, py = P[key]
        return (f'<circle cx="{px}" cy="{py}" r="7" fill="var(--accent-soft)" '
                f'stroke="var(--accent)" stroke-width="2"/>'
                f'<text x="{px}" y="{py + 22}" font-size="11" fill="var(--ink2)" '
                f'text-anchor="middle" font-weight="500">{label}</text>'
                f'<text x="{px}" y="{py + 35}" font-size="9.5" fill="var(--ink3)" '
                f'text-anchor="middle">{sub}</text>')

    def choke(key, label, status):
        px, py = P[key]
        return (f'<rect x="{px - 5}" y="{py - 5}" width="10" height="10" '
                f'transform="rotate(45 {px} {py})" fill="{col[status]}"/>'
                f'<text x="{px}" y="{py - 11}" font-size="10" fill="var(--ink2)" '
                f'text-anchor="middle">{label}</text>')

    kx, ky = P["kor"]
    return (f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto;display:block" '
            f'role="img" aria-label="주요 원산지에서 한국까지의 공급 경로 모식도">'
            + grid + routes
            + origin("usg", "미국 멕시코만", "조유·정제유")
            + origin("bra", "브라질", "조유")
            + origin("arg", "아르헨티나", "조유 최대 공급")
            + origin("mys", "말레이·인니", "팜유(대체)")
            + f'<circle cx="{kx}" cy="{ky}" r="9" fill="var(--accent)"/>'
            + f'<text x="{kx}" y="{ky - 16}" font-size="12" fill="var(--ink2)" '
              f'text-anchor="middle" font-weight="700">한국 (평택·인천)</text>'
            + choke("panama", "파나마", st["panama"]) + choke("suez", "수에즈·홍해", st["suez"])
            + choke("hormuz", "호르무즈", st["hormuz"]) + choke("malacca", "말라카", st["malacca"])
            + "</svg>")


# ── 블록 렌더 ────────────────────────────────────────────────────────────────

def _esc(t: object) -> str:
    return _html.escape(str(t), quote=True)


def _chg_html(v: float | None, suffix: str = "%") -> str:
    if v is None:
        return '<span class="chg flat">—</span>'
    cls = "up" if v > 0 else ("down" if v < 0 else "flat")
    arrow = "▲ +" if v > 0 else ("▼ " if v < 0 else "")
    return f'<span class="chg {cls} num">{arrow}{v:.2f}{suffix}</span>'


def _brief_box(items: list[tuple[str, str]]) -> str:
    seg = "".join(
        f'<span class="k{" warn" if k == "유의" else ""}">{k}</span>{_esc(t)} '
        for k, t in items if t)
    return f'<div class="brief">{seg}</div>'


def _stars(n: int) -> str:
    return "★" * max(1, min(3, n))


def _inflection_block(points: list[dict], importance_df: pd.DataFrame) -> str:
    """주요 변동일 목록 — 날짜·변화율·당시 신호·변인 상태·온톨로지 체인 (W-C · R2).

    신호 아카이브(2026-08-17~) 이전 날짜와 분석 데이터 미가용 상황은 정직 강등.
    """
    if not points:
        return ""
    top_codes = ([str(r["변수"]) for _, r in importance_df.head(3).iterrows()]
                 if not importance_df.empty else [])
    analysis = None
    try:
        from src.forecasting.variable_importance_g1 import _load_g1_feature_mart
        analysis, _lv, _t = _load_g1_feature_mart()
    except Exception:                                         # noqa: BLE001 — 비치명
        analysis = None
    try:
        from src.forecasting.analogue_g1 import _resolve_z_column
    except Exception:                                         # noqa: BLE001
        _resolve_z_column = None                              # type: ignore[assignment]

    cards = []
    for p in points:
        d: pd.Timestamp = p["date"]
        chg = p["chg"]
        cls = "up" if chg > 0 else "down"
        arrow = "▲" if chg > 0 else "▼"
        rows: list[str] = [
            f'<li>일간 변화율 <span class="chg {cls} num">{arrow} {chg:+.2f}%</span> · '
            f'종가 <span class="num">{p["close"]:.2f}</span> USc/lb</li>']
        # ① 당시 수집 신호(±2일)
        sig = _signals_around(d)
        if not sig.empty:
            shown = 0
            for _, row in sig.iterrows():
                if shown >= 2:
                    break
                note = str(row.get("note", ""))
                title = _esc(note.split("]")[-1][:90].strip() or row.get("indicator", ""))
                url = _first_url(note)
                head = (f'<a href="{_esc(url)}" target="_blank" rel="noopener">{title}</a>'
                        if url else title)
                rows.append(f'<li>당시 신호: {head} '
                            f'<span class="src">{_esc(row.get("source_name", ""))}</span></li>')
                chain = _ONTOLOGY_CHAINS.get(str(row.get("indicator", "")))
                if chain and shown == 0:
                    rows.append(f'<li>연결 경로: {_esc(" → ".join(chain))}</li>')
                shown += 1
        else:
            rows.append('<li><span class="src">당시 수집 신호 없음(신호 아카이브는 '
                        '2026-08-17부터) — 변인 상태만 표시</span></li>')
        # ② 당시 변인 표준화 지수(분석 데이터 시점 조회)
        z_parts: list[str] = []
        if analysis is not None and _resolve_z_column is not None and top_codes:
            idx = analysis.index[analysis.index <= d]
            if len(idx):
                row_z = analysis.loc[idx[-1]]
                for c in top_codes:
                    zc = _resolve_z_column(analysis.columns, c)
                    if zc is not None and pd.notna(row_z.get(zc)):
                        base = c.split("__")[0]
                        z_parts.append(f'{_esc(VAR_LABELS.get(base, base))} '
                                       f'{float(row_z[zc]):+.1f}')
        if z_parts:
            rows.append(f'<li>당시 상위 변인 표준화 지수(z): {" · ".join(z_parts)}</li>')
        elif analysis is None:
            rows.append('<li><span class="src">변인 상태: 분석 데이터 미가용 — CI 실행에서 '
                        '자동 표시</span></li>')
        cards.append(
            f'<details class="mech"><summary>{p["no"]} {d.strftime("%Y-%m-%d")} '
            f'<span class="chg {cls} num">{arrow} {chg:+.2f}%</span></summary>'
            f'<ul style="margin:6px 0 0 16px;line-height:1.7">{"".join(rows)}</ul></details>')
    return ('<div style="margin-top:8px"><b style="font-size:13px">주요 변동일 '
            f'{len(points)}건</b> <span class="cap">— 차트의 번호 표시와 대응 · 클릭 시 '
            '당시 신호·변인 상태 표시(과거 사실 기술)</span>'
            + "".join(cards) + "</div>")


def _analogue_block(breach: list[dict], importance_df: pd.DataFrame) -> str:
    """과거 유사국면 실측 참조 블록 — 경보 변수 우선, 중요도 상위로 보충.

    A-191: 과거 관측의 요약까지만 — 전망·확률 주장 금지. mart 미가용 시 정직 강등.
    """
    try:
        from src.forecasting.analogue_g1 import (build_analogue_context,
                                                 case_narrative_lines,
                                                 format_result_line)
        alert_codes = [str(a.get("변수", "")) for a in breach]
        top_codes = ([str(r["변수"]) for _, r in importance_df.head(4).iterrows()]
                     if not importance_df.empty else [])
        results = build_analogue_context(alert_codes, top_codes)
    except Exception as e:                                    # noqa: BLE001 — 비치명
        print(f"[정보] 유사국면 블록 생성 불가(비치명): {type(e).__name__}: {e}")
        results = []
    if not results:
        return ('<div class="card sig-item"><p>과거 유사 시기 참조: 분석 데이터 미가용 '
                '또는 대상 변수 부재 — 산출 보류. 실산출은 CI 실행에서 분석 데이터와 함께 '
                '생성됨.</p></div>')
    by_var: dict[str, list] = {}
    for r in results:
        by_var.setdefault(r.var_code, []).append(r)
    cards = []
    for var, rs in list(by_var.items())[:3]:
        z_txt = f"{rs[0].current_z:+.1f}" if rs[0].current_z == rs[0].current_z else "?"
        label = VAR_LABELS.get(var, var)
        lines = "".join(f"<li>{_esc(format_result_line(r))}</li>"
                        for r in sorted(rs, key=lambda x: x.horizon))
        badges = sorted({b for r in rs for b in r.case_badges})
        badge_parts = []
        if badges:
            badge_parts.append(f'<div class="src">겹치는 위기 사례: '
                               f'{_esc(" · ".join(badges))}</div>')
            # W-B(조정자 R1): 배지 클릭 → 왜 유사한가 — 원인→경로→가격 실측→유사점/차이점
            for b in badges:
                narr = case_narrative_lines(b)
                if narr:
                    items = "".join(f"<li>{_esc(t)}</li>" for t in narr)
                    badge_parts.append(
                        f'<details class="mech"><summary>{_esc(b)} — 왜 유사한가 (클릭)'
                        f'</summary><ul style="margin:6px 0 0 16px;line-height:1.7">'
                        f'{items}</ul><div class="cap">과거 사실 기술과 구조 비교까지만 — '
                        f'방향 판단 아님(A-191). 상세·수치는 위기 사례 문서(corrections '
                        f'병독).</div></details>')
        badge_html = "".join(badge_parts)
        cards.append(f"""
    <div class="card sig-item">
      <span class="tag">{_esc(label)} <span style="color:var(--ink3)">현재 z {z_txt}</span></span>
      <ul style="font-size:13px;margin:6px 0 0 18px;line-height:1.8">{lines}</ul>
      {badge_html}</div>""")
    mech = """
    <details class="mech"><summary>산출 방식 (클릭)</summary>
      변수의 90일 표준화 지수(z)가 현재와 같은 구간(십분위)이었던 과거 거래일을 찾아,
      그 날들로부터 약 1주(5거래일)/약 1개월(20거래일)/약 3개월(60거래일) 뒤의
      <b>실측</b> 가격 변화를 집계함(2010~ 전 구간). 유사일 사이에 최소 간격을 두어
      중복 시기를 제거하고, 최근 60거래일은 집계에서 제외함(전방 구간 겹침 방지).
      유사 시기가 8회 미만이면 산출을 보류함. <b>통계 검정 없음 — 기술 서술</b>이며,
      감시 창(90일)은 기준 기간 확정 전 잠정값임.</details>"""
    return (f'<div class="signals">{"".join(cards)}</div>' + mech
            + '<div class="cap" style="margin-top:8px">⚠️ 위 수치는 <b>과거 관측의 '
              '요약이며 향후 전망·확률 주장이 아님</b>(A-191). 유사 상황에서 어떤 변수를 '
              '주시할지 참고하는 자료로만 사용할 것.</div>')


def _snapshot_specs() -> list[dict]:
    return [
        {"label": "CBOT ZL 종가", "codes": ["CBOT_BO_CLOSE"], "src": "CME 정산가", "fmt": "{:,.2f}"},
        {"label": "CPO 팜유", "codes": ["TE_PALM_OIL", "CPO"], "src": "TE/Bursa", "fmt": "{:,.0f}"},
        {"label": "BDI 해상운임지수", "codes": ["TE_BDI", "BDI"], "src": "Baltic", "fmt": "{:,.0f}"},
        {"label": "BRL/USD 환율", "codes": ["DEXBZUS"], "src": "FRED", "fmt": "{:.2f}"},
        {"label": "원/달러 환율", "codes": ["DEXKOUS", "KRW_USD"], "src": "FRED/BOK", "fmt": "{:,.0f}"},
        {"label": "VIX 변동성", "codes": ["VIXCLS"], "src": "CBOE", "fmt": "{:.1f}"},
        {"label": "ENSO ONI", "codes": ["ONI", "ENSO_ONI"], "src": "NOAA", "fmt": "{:+.2f}",
         "monthly": True},
        # D-051·A-229: 대두박(ZM)·대두(ZS) 반입(9/1~) 후 산출 — 그 전까지 예정 표기
        {"label": "압착 마진 (Board Crush)", "codes": ["BOARD_CRUSH_MARGIN"],
         "src": "CBOT ZL·ZM·ZS", "fmt": "{:+.2f}",
         "pending_note": "수집 예정 — 대두박(ZM)·대두(ZS) 반입 후 산출(트레이더가 대두 복합체를 읽는 대표 지표)"},
    ]


def build_daily_brief(
    frames: dict[str, pd.DataFrame],
    importance_df: pd.DataFrame,
    alerts: list[dict],
    status_df: pd.DataFrame,
    run_ts: str,
    run_id: str,
    target_label: str,
    n_features: int | None = None,
) -> str:
    """일별 브리프 HTML 문자열 생성 — 모든 블록은 결측 시 정직 강등."""
    today = date.today()
    kpi = _kpi_close(frames)
    full_close = _dated_series(frames, ["CBOT_BO_CLOSE"])["value"]
    rng = _reference_range_usclb(full_close) if len(full_close) else None
    band_mt = _landed_band()
    signals = _load_signals()

    breach = [a for a in alerts if "🚨" in str(a.get("상태", ""))]
    watch = [a for a in alerts if "⚠️" in str(a.get("상태", "")) or "❓" in str(a.get("상태", ""))]
    normal_n = len(alerts) - len(breach) - len(watch)

    # 데이터 적시성 (status_df 신선도 플래그)
    fresh_total = len(status_df) if not status_df.empty else 0
    fresh_ok = int(status_df["신선도"].astype(str).str.contains("✅").sum()) \
        if (not status_df.empty and "신선도" in status_df.columns) else 0

    # ── KPI 블록 ──
    kpi_cards = []
    if kpi:
        kpi_cards.append(f"""
    <div class="card kpi"><div class="lbl">CBOT 대두유(ZL) 종가</div>
      <div class="val num">{kpi.close:.2f} <span class="unit">USc/lb</span></div>
      {_chg_html(kpi.chg_pct)}
      <div class="foot num">주간 {f"{kpi.wk_pct:+.1f}%" if kpi.wk_pct is not None else "—"} ·
        90일 z {f"{kpi.z90:+.1f}" if kpi.z90 is not None else "—"} · CME 정산가 기준 · 기준일 {kpi.last_date}</div></div>""")
    else:
        kpi_cards.append('<div class="card kpi"><div class="lbl">CBOT 대두유(ZL) 종가</div>'
                         '<div class="val">미수집</div><div class="foot">CBOT_BO_CLOSE 미발행 — '
                         '목표변수 잡 확인 필요</div></div>')
    if band_mt:
        kpi_cards.append(f"""
    <div class="card kpi"><div class="lbl">참고 도착가 범위 · 약 90일(60거래일)</div>
      <div class="val num">{band_mt[1]:,.2f} <span class="unit">달러/MT</span></div>
      <div class="chg flat num">최소 {band_mt[0]:,.2f} — 최대 {band_mt[2]:,.2f}</div>
      <div class="foot">CIF 한국 · 실측 잔차층 반영 <span class="pill acc">참고 범위</span></div></div>""")
    else:
        kpi_cards.append('<div class="card kpi"><div class="lbl">참고 도착가 범위 · 60거래일</div>'
                         '<div class="val">산출 불가</div><div class="foot">관세청 실측 또는 '
                         'CBOT 층 데이터 부족 — 비치명 강등</div></div>')
    kpi_cards.append(f"""
    <div class="card kpi"><div class="lbl">금일 경보 (유의 사항)</div>
      <div class="val num">{len(breach)}<span class="unit">건</span></div>
      <div class="chg flat">{('<span class="pill warn">🚨 기준 초과</span>' if breach
                              else '<span class="pill ok">서명된 무소식</span>')}</div>
      <div class="foot">기준 초과 {len(breach)} · 관찰 {len(watch)} · 정상 {normal_n}</div></div>""")
    kpi_cards.append(f"""
    <div class="card kpi"><div class="lbl">데이터 적시성</div>
      <div class="val num">{fresh_ok}<span class="unit">/{fresh_total} 항목</span></div>
      <div class="chg flat">{('<span class="pill ok">수집 정상</span>'
                              if fresh_total and fresh_ok >= fresh_total * 0.8
                              else '<span class="pill warn">지연 확인 필요</span>')}</div>
      <div class="foot">신선도 ✅ 비율 기준 (월별 지표의 정기 지연 포함)</div></div>""")

    # ── 한눈 요약 4단 문장 (규칙 기반) ──
    if kpi and kpi.wk_pct is not None:
        if kpi.wk_pct > 0.5:
            trend = f"한 주간 {kpi.wk_pct:+.1f}% 상승했으며"
        elif kpi.wk_pct < -0.5:
            trend = f"한 주간 {kpi.wk_pct:+.1f}% 하락했으며"
        else:
            trend = "한 주간 보합권에서 움직였으며"
        s_now = f"대두유 선물은 {trend}, 종가 {kpi.close:.2f} USc/lb로 마감함."
    else:
        s_now = "목표변수(CBOT ZL) 최신 관측이 부족해 현황 판단을 보류함."
    top2 = importance_df.head(2)
    if not top2.empty:
        names = " · ".join(VAR_LABELS.get(str(r["변수"]), str(r["변수"])) for _, r in top2.iterrows())
        s_factor = f"현재 중요도 상위 변인은 {names}임 (Elastic Net·상관 삼각검증)."
    else:
        s_factor = "변인 중요도 산출이 비어 있어 요인 판단을 보류함."
    s_outlook = (f"향후 약 3개월(60거래일)의 참고 범위는 {rng[0]:.2f}~{rng[2]:.2f} USc/lb"
                 + (f"(도착가 {band_mt[0]:,.2f}~{band_mt[2]:,.2f}달러/MT)" if band_mt else "")
                 + "임. 과거 유사 시기 실측은 전용 항목 참조." if rng
                 else "참고 범위는 데이터 부족으로 산출하지 않음.")
    s_care = (f"금일 기준 초과 {len(breach)}건 — 상세는 '금일 경보' 참조. 조달 결정은 담당자 승인 절차 필수."
              if breach else "금일 기준 초과 없음(서명된 무소식) — 조달 결정은 담당자 승인 절차 필수.")
    summary_top = _brief_box([("현황", s_now), ("요인", s_factor),
                              ("전망", s_outlook), ("유의", s_care)])

    # ── 핵심 변인 Top 5 ──
    drv_rows = []
    top5 = importance_df.head(5)
    max_abs = float(top5["LASSO_계수"].abs().max()) if not top5.empty else 0.0
    for i, (_, row) in enumerate(top5.iterrows(), start=1):
        code = str(row["변수"])
        label = VAR_LABELS.get(code, code)
        r = row.get("피어슨_r")
        coef = row.get("LASSO_계수")
        direction = ('<span class="dir up">상방 ▲</span>' if isinstance(r, float) and r > 0
                     else ('<span class="dir down">하방 ▼</span>' if isinstance(r, float) and r < 0
                           else ""))
        width = int(abs(coef) / max_abs * 100) if (max_abs and isinstance(coef, float)) else 10
        arts = _match_articles(code, signals)
        if arts:
            a0 = arts[0]
            title = _esc(a0["note"].split("]")[-1][:70].strip() or a0["indicator"])
            link = (f'<a href="{_esc(a0["url"])}" target="_blank" rel="noopener">{title}…</a>'
                    if a0["url"] else f"{title}…")
            news = (f'<div class="news"><span class="stars">{_stars(len(arts))}</span> '
                    f'{link} · {_esc(a0["source"])}</div>')
        else:
            news = '<div class="news">관련 기사 매핑 없음</div>'
        drv_rows.append(f"""
      <div class="drv"><span class="rank num">{i}</span><div>
        <span class="name">{_esc(label)}</span>{direction}
        <div class="barrow"><div class="bar" style="width:{max(width, 8)}%"></div>
          <span class="shap num">계수 {coef:+.4f} · r {r:+.3f}</span></div>
        {news}</div></div>""")
    drivers_html = ("".join(drv_rows) if drv_rows
                    else '<p class="cap">변인 중요도 산출 결과가 없습니다 — 미수집.</p>')

    # ── 차트 ──
    if kpi:
        inflections = _inflection_points(kpi)
        chart_svg = _svg_price_chart(kpi, rng, marks=inflections)
        inflection_html = _inflection_block(inflections, importance_df)
        chart_start = kpi.series["price_date"].iloc[0].strftime("%Y-%m-%d")
        chart_cap = (f"실적: {chart_start} ~ {kpi.last_date} ({len(kpi.series)}거래일 · "
                     f"CME 실측) · 참고 범위: 기준일 이후 약 90일(60거래일)")
        rng_fig = (f"""
      <div class="range-figures num">
        <span>범위 중앙(P50) <b>{rng[1]:.2f}</b></span>
        <span>최소(P10) <b>{rng[0]:.2f}</b></span>
        <span>최대(P90) <b>{rng[2]:.2f}</b> USc/lb</span></div>""" if rng else
                   '<div class="range-figures">참고 범위: 데이터 부족으로 미산출</div>')
    else:
        chart_svg = '<p class="cap">목표변수 미수집 — 차트를 생성하지 않음.</p>'
        chart_cap, rng_fig, inflection_html = "", "", ""

    mech = f"""
      <details class="mech"><summary>참고 범위 산출 근거 (클릭)</summary>
        <ol>
          <li><b>가격 원천</b>: CME(CBOT) ZL 선물 — 정산가 교차검증을 거친 종가 계열.</li>
          <li><b>기준 가격층</b>: 과거 60거래일 변동 분포(2010~ 전 구간)의 하위 10%·
            중앙값·상위 10% 지점을 최근 종가에 적용함.</li>
          <li><b>실측 잔차층</b>: 관세청 수입 실적(선적 100톤 이상)의 CIF 단가에서 같은 달
            CBOT 가격을 뺀 차이 — 최근 12개월 분포(운임·프리미엄이 섞인 잔차층).</li>
          <li><b>결합</b>: 두 층을 몬테카를로 방식으로 결합함(2만 회 추출·결과 재현 가능).
            분위 수치의 단순 합산은 통계적으로 부정확하여 쓰지 않음.</li>
          <li><b>한계</b>: 과거 변동이 이중으로 반영될 수 있어 <b>"확률 범위"가 아닌
            "참고 범위"</b>로만 제공함. G2 모델 가동 시 이 층이 교체됨.</li>
        </ol></details>"""

    # ── 경보 블록 ──
    if breach:
        cards = []
        for a in breach:
            code = str(a.get("변수", "?"))
            cards.append(f"""
    <div class="alert"><div class="stripe"></div><div class="body">
      <div class="head">🚨 <span>{_esc(VAR_LABELS.get(code, code))} — {_esc(a.get("설명", ""))}</span>
        <span class="pill warn">기준 초과</span></div>
      <div class="detail num">현재값 {_esc(a.get("현재값", "?"))} · 기준 {_esc(a.get("임계값", "?"))} ·
        신선도 {_esc(a.get("데이터신선도", "?"))}</div></div></div>""")
        alerts_html = "".join(cards)
        s_alert_now = f"{len(alerts)}개 감시 변인 가운데 {len(breach)}건이 주의 기준을 넘어섬."
        s_alert_out = "기준 초과 변인의 지속 여부를 다음 날 브리프에서 다시 점검함."
    else:
        alerts_html = ("""
    <div class="card" style="padding:14px 18px">
      <b style="color:var(--ok)">✔ 서명된 무소식</b> — 감시 변인 전체가 기준 범위 내에 있음.
      침묵이 아니라 검사를 통과한 결과임 (게이트·검증 상태는 상단 신뢰 스트립 참조).</div>""")
        s_alert_now = f"{len(alerts)}개 감시 변인 전체가 기준 범위 안에 있음(미수집 {len(watch)}건 별도)."
        s_alert_out = "이상 징후 없음 — 정기 감시를 지속함."
    summary_alert = _brief_box([
        ("현황", s_alert_now),
        ("요인", "판정 기준은 분포 기반(상위 10%·z 2σ)과 검증된 절대 기준의 이중 체계임."),
        ("전망", s_alert_out),
        ("유의", "미수집 항목은 경보 불가 상태이므로 '정상'과 구분해 표기함.")])

    # ── 과거 유사국면 실측 참조 (D-051 — G1 재정립의 본질 블록) ──
    analogue_html = _analogue_block(breach, importance_df)

    # ── 지표 스냅샷 ──
    snap_rows = []
    for spec in _snapshot_specs():
        s = _dated_series(frames, spec["codes"])
        if s.empty:
            missing = spec.get("pending_note", "미수집")
            snap_rows.append(f'<tr><td>{spec["label"]}<span class="src">{spec["src"]}</span></td>'
                             f'<td colspan="5" style="color:var(--ink3);text-align:left">'
                             f'{missing}</td></tr>')
            continue
        v = s["value"]
        val = spec["fmt"].format(float(v.iloc[-1]))
        d1 = _pct(float(v.iloc[-1]), float(v.iloc[-2])) if len(v) >= 2 else None
        d5 = _pct(float(v.iloc[-1]), float(v.iloc[-6])) if len(v) >= 6 else None
        z = _z90(v)
        z_txt = (f'<span class="z-hot">{z:+.1f}</span>' if (z is not None and abs(z) >= 2)
                 else (f"{z:+.1f}" if z is not None else "—"))
        if spec.get("monthly"):
            d1_txt, d5_txt = '<span style="color:var(--ink3)">월간</span>', "—"
        else:
            d1_txt = _chg_html(d1) if d1 is not None else "—"
            d5_txt = _chg_html(d5) if d5 is not None else "—"
        spark = _svg_spark([float(x) for x in v.tail(8)])
        snap_rows.append(
            f'<tr><td>{spec["label"]}<span class="src">{spec["src"]}</span></td>'
            f'<td class="num">{val}</td><td>{d1_txt}</td><td>{d5_txt}</td>'
            f'<td class="num">{z_txt}</td><td>{spark}</td></tr>')

    # ── 언론·매체 블록 ──
    sig_cards = []
    seen_ind: set[str] = set()
    for _, row in signals.iterrows():
        ind = str(row.get("indicator", ""))
        if ind in seen_ind or len(sig_cards) >= 6:
            continue
        seen_ind.add(ind)
        note = str(row.get("note", ""))
        url = _first_url(note)
        title = _esc(note.split("]")[-1][:110].strip() or ind)
        head = (f'<a href="{_esc(url)}" target="_blank" rel="noopener">{title}</a>'
                if url else title)
        chain = _ONTOLOGY_CHAINS.get(ind)
        chain_html = ""
        if chain:
            nodes = ""
            for j, nname in enumerate(chain):
                cls = "edge" if "CE-" in nname else ("ent" if j in (1, 3) else "")
                nodes += f'<span class="node {cls}">{_esc(nname)}</span>'
                if j < len(chain) - 1:
                    nodes += '<span class="arr">→</span>'
            chain_html = (f'<details class="chain"><summary>온톨로지 연결</summary>'
                          f'<div class="row">{nodes}</div>'
                          f'<div class="meta">시맨틱 레이어 연동: entities.yaml·ontology.yaml v3 '
                          f'(validated 엣지만 변인 분석 반영 · 근거 발췌 보존 S-5)</div></details>')
        sig_cards.append(f"""
    <div class="card sig-item">
      <span class="tag">{_esc(row.get("category", "신호"))}</span>
      <p>{head}</p>
      <div class="src">{_esc(row.get("source_name", ""))} ·
        {pd.Timestamp(row.get("date")).strftime("%m-%d") if pd.notna(row.get("date")) else ""}</div>
      {chain_html}</div>""")
    signals_html = ("".join(sig_cards) if sig_cards else
                    '<div class="card sig-item"><p>최근 3일 내 수집된 언론·매체 신호가 없음 — '
                    '일별 다이제스트 실행 여부 확인 필요.</p></div>')

    # ── 주목해야 할 일정 ──
    cal_items = []
    next_wasde = next((d for d in WASDE_SCHEDULE if d >= today), None)
    if next_wasde:
        cal_items.append((next_wasde, "USDA WASDE 발표",
                          "발표 익영업일 월별 심층판 자동 발행"))
        order_deadline = next_wasde + timedelta(days=6)
        cal_items.append((order_deadline, "차기 선적분 발주 검토 시한",
                          f"CIF 한국 리드타임 {LEADTIME_DAYS}일 역산 기준"))
    for d, what, when in POLICY_MILESTONES:
        if d >= today:
            cal_items.append((d, what, when))
    cal_html = "".join(f"""
    <div class="card cal-item">
      <div class="dday num">D-{(d - today).days}<small>{d.strftime("%m/%d")}</small></div>
      <div><div class="what">{_esc(what)}</div><div class="when">{_esc(when)}</div></div></div>"""
                       for d, what, when in sorted(cal_items)[:4])

    # ── 부록: 전문 기관(RSS 소스별 최신 1건) ──
    appx_cards = []
    if not signals.empty:
        rss = signals[signals["indicator"].astype(str).str.startswith("RSS_")]
        for src, grp in rss.groupby("indicator"):
            row = grp.iloc[0]
            note = str(row.get("note", ""))
            url = _first_url(note)
            title = _esc(note[:130])
            org = str(src).replace("RSS_", "").replace("_", " ").title()
            link = (f'<a href="{_esc(url)}" target="_blank" rel="noopener">원문</a>' if url else "")
            appx_cards.append(f"""
    <div class="card appx-item"><div class="org">{_esc(org)}</div>
      <p>{title}</p><div class="src">{link}</div></div>""")
    appx_html = ("".join(appx_cards[:6]) if appx_cards else
                 '<div class="card appx-item"><p>전문 매체 RSS 수집분이 아직 없음 — 첫 수집 '
                 '이후 기관별 최신 발간물이 이 자리에 표시됨.</p></div>')

    # ── 경로 모식도 ──
    st = _route_status(frames)
    route_svg = _svg_route_map(st)

    # ── E1 신뢰 스트립 ──
    gate = os.environ.get("E1_GATE_STATUS", "").strip() or "미확인(게이트 잡 별도)"
    feat_txt = f"{n_features:,}" if n_features else "—"

    css = _CSS
    breach_pill = (f'🚨 기준 초과 {len(breach)}건' if breach else '서명된 무소식')
    return f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nexus 일일 브리프 — {run_ts[:10]}</title>
<link rel="stylesheet" media="print" onload="this.media='all'"
 href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@600;700&family=IBM+Plex+Sans+KR:wght@400;500;700&display=swap">
<!-- 폰트 비차단 로드(A-241): 사내망이 fonts.googleapis.com을 차단·지연시켜도 렌더가
     멈추지 않게 비동기 적용 — 실패 시 시스템 폰트(Malgun Gothic 등)로 즉시 표시 -->
<style>{css}</style></head><body>
<div class="page">
<header>
  <div class="masthead"><h1>Nexus 일일 브리프</h1>
    <div class="sub">대두유 조달 신호 데스크 · 핵심 변인과 <b>과거 유사 시기 실측 참조</b> — <b>Preview</b></div></div>
  <div class="dateblock"><strong>{run_ts[:10]}</strong>
    KST 05:30 발행 체계 · 데이터 기준 {kpi.last_date if kpi else "미수집"} CME 마감</div>
</header>
<div class="trust">
  <span class="sig">✔ 서명된 검사</span>
  <span>품질 게이트 <b>{_esc(gate)}</b></span>
  <span>시점 정합 변수 <b>{feat_txt}</b></span>
  <span>분석 타깃 <b>{_esc(target_label)}</b></span>
  <span>런 <b>{_esc(run_id)}</b> · {breach_pill}</span>
</div>

<section><div class="sec-h"><h2>한눈 요약</h2><span class="note">전 거래일 마감 기준</span></div>
{summary_top}
<div class="kpis">{"".join(kpi_cards)}</div></section>

<section><div class="sec-h"><h2>가격 추세와 핵심 변인</h2>
  <span class="note">변인 순위: Elastic Net + 상관 삼각검증 (20거래일 지평)</span></div>
<div class="duo">
  <div class="card chartbox">
    <h3>CBOT ZL 종가 추이 + 참고 범위</h3>
    <div class="cap">{chart_cap}</div>
    {chart_svg}
    <div class="legend"><span><i></i>종가 (USc/lb)</span>
      <span><i class="band"></i>참고 범위 P10–P90</span></div>
    {rng_fig}{inflection_html}{mech}
  </div>
  <div class="card drivers"><h3>핵심 변인 Top 5</h3>
    <div class="cap">별점 = 최근 기사와 변인의 연관 매핑 (★~★★★) · 제목 클릭 시 원문</div>
    {drivers_html}</div>
</div></section>

<section><div class="sec-h"><h2>금일 경보 (유의 사항)</h2>
  <span class="note">기준 초과 변인만 표시 — 이상이 없는 날은 서명된 무소식으로 대체함</span></div>
{summary_alert}{alerts_html}</section>

<section><div class="sec-h"><h2>과거 유사 시기 실측 참조</h2>
  <span class="note">현재와 유사했던 과거 연도들의 이후 실측 — 예측이 아닌 참조(A-191)</span></div>
{analogue_html}</section>

<section><div class="sec-h"><h2>글로벌 공급 경로 현황</h2>
  <span class="note">모식도(1단계) — 실지도·AIS 위치 연동은 2단계 로드맵</span></div>
<div class="card mapbox"><h3>주요 원산지 → 한국 항로와 요충 해협</h3>
{route_svg}
<div class="map-legend"><span><span class="dot ok"></span>정상</span>
  <span><span class="dot warn"></span>주의</span>
  <span><span class="dot crit"></span>심각</span>
  <span><span class="dot" style="background:var(--ink3)"></span>미수집</span>
  <span style="margin-left:auto">해협 위험 종합 지수 <b class="num">{st["composite"]}</b>/100</span>
</div></div></section>

<section><div class="sec-h"><h2>지표 스냅샷</h2>
  <span class="note">z = 90일 기준(잠정 — 기준 기간 확정 전 · W0) · 상승 적색/하락 청색</span></div>
<div class="card tablewrap"><table>
  <thead><tr><th>지표</th><th>값</th><th>일간</th><th>주간</th><th>90일 z</th><th>추세</th></tr></thead>
  <tbody>{"".join(snap_rows)}</tbody></table></div></section>

<section><div class="sec-h"><h2>금일 언론·매체로 보는 시장 추세</h2>
  <span class="note">일별 수집 + 전문 매체 — 제목 클릭 시 원문 · 온톨로지 연결로 분석 체계 확인</span></div>
<div class="signals">{signals_html}</div></section>

<section><div class="sec-h"><h2>주목해야 할 일정</h2>
  <span class="note">발표 캘린더 + 조달 리드타임 D-day</span></div>
<div class="cal">{cal_html}</div></section>

<section><div class="sec-h"><h2>부록 — 전문 기관·매체 최신</h2>
  <span class="note">RSS 수집분 기관별 최신 1건 + 원문 링크</span></div>
<div class="appx">{appx_html}</div></section>

<footer>
  <div class="hitl">본 브리프는 판단 지원 정보이며, 조달(구매/보류) 결정은 반드시 담당자
    승인 절차를 거침. 구매/보류 신호와 국면 판정(G3)은 정식판에서 제공 예정. 위기 국면에는
    시나리오와 행동 옵션을 담은 특별 브리프 체계로 전환됨.</div>
  데이터 시점 규율: 모든 입력은 발행 시점 이전에 확정된 값만 사용함 — 장 마감(14:20 ET)
  이후 확정되는 지표는 하루 지연해 반영함. 산출: G1 파이프라인 (Elastic Net + SHAP
  삼각검증 + Granger) · 생성 {run_ts} UTC
</footer>
</div></body></html>"""


_CSS = """
:root{--paper:#F7F8FA;--surface:#FFFFFF;--ink:#182236;--ink2:#5A6478;--ink3:#8B93A5;
--line:#DDE2EA;--accent:#1F4FA8;--accent-soft:#E8EEF9;--up:#C4382E;--down:#1D5FBF;
--warn:#9C6A00;--warn-soft:#FBF3E0;--ok:#1E7A46;--ok-soft:#E7F3EC;--crit:#B3261E;
--band2:rgba(31,79,168,.20)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--paper:#12161F;
--surface:#1A2029;--ink:#E8ECF4;--ink2:#A6AEBF;--ink3:#727B8E;--line:#2A3242;
--accent:#7BA3E8;--accent-soft:#22304A;--up:#E86A5E;--down:#6FA0E8;--warn:#D9A544;
--warn-soft:#33290F;--ok:#5CB985;--ok-soft:#15301F;--crit:#E8756B;
--band2:rgba(123,163,232,.26)}}
:root[data-theme="dark"]{--paper:#12161F;--surface:#1A2029;--ink:#E8ECF4;--ink2:#A6AEBF;
--ink3:#727B8E;--line:#2A3242;--accent:#7BA3E8;--accent-soft:#22304A;--up:#E86A5E;
--down:#6FA0E8;--warn:#D9A544;--warn-soft:#33290F;--ok:#5CB985;--ok-soft:#15301F;
--crit:#E8756B;--band2:rgba(123,163,232,.26)}
*{box-sizing:border-box;margin:0}
body{background:var(--paper);color:var(--ink);
font-family:"IBM Plex Sans KR","Noto Sans CJK KR",-apple-system,"Malgun Gothic",sans-serif;
font-size:15px;line-height:1.65}
.page{max-width:1060px;margin:0 auto;padding:0 24px 72px}
.num{font-variant-numeric:tabular-nums}
a{color:var(--accent)}
header{border-bottom:3px solid var(--ink);padding:34px 0 18px;display:flex;flex-wrap:wrap;
align-items:flex-end;justify-content:space-between;gap:12px}
.masthead h1{font-family:"Noto Serif KR","Noto Serif CJK KR",serif;font-weight:700;
font-size:30px;letter-spacing:-.01em;line-height:1.2}
.masthead .sub{color:var(--ink2);font-size:13px;margin-top:4px}
.dateblock{text-align:right;font-size:13px;color:var(--ink2)}
.dateblock strong{display:block;font-size:17px;color:var(--ink);font-weight:700}
.trust{display:flex;flex-wrap:wrap;gap:8px 22px;align-items:center;background:var(--surface);
border:1px solid var(--line);border-top:none;border-radius:0 0 8px 8px;padding:10px 16px;
font-size:12.5px;color:var(--ink2)}
.trust .sig{font-weight:700;color:var(--ok)}
.trust b{color:var(--ink);font-weight:500}
section{margin-top:34px}
.sec-h{display:flex;align-items:baseline;gap:10px;border-bottom:1px solid var(--line);
padding-bottom:8px;margin-bottom:12px}
.sec-h h2{font-size:16px;font-weight:700}
.sec-h .note{font-size:12px;color:var(--ink3)}
.card{background:var(--surface);border:1px solid var(--line);border-radius:8px}
.brief{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--accent);
border-radius:8px;padding:12px 16px;font-size:13.5px;margin-bottom:14px;line-height:1.75}
.brief .k{display:inline-block;font-size:11px;font-weight:700;color:var(--accent);
background:var(--accent-soft);border-radius:4px;padding:0 6px;margin-right:4px;
letter-spacing:.03em;vertical-align:1px}
.brief .k.warn{color:var(--warn);background:var(--warn-soft)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.kpi{padding:16px 18px}
.kpi .lbl{font-size:12px;color:var(--ink2);letter-spacing:.04em}
.kpi .val{font-size:26px;font-weight:700;margin-top:2px}
.kpi .unit{font-size:13px;font-weight:400;color:var(--ink2)}
.chg{font-size:13px;margin-top:2px;display:inline-block}
.chg.up{color:var(--up)}.chg.down{color:var(--down)}.chg.flat{color:var(--ink2)}
.kpi .foot{font-size:12px;color:var(--ink3);margin-top:6px}
.pill{display:inline-block;font-size:11.5px;font-weight:700;padding:2px 9px;border-radius:99px}
.pill.warn{background:var(--warn-soft);color:var(--warn)}
.pill.ok{background:var(--ok-soft);color:var(--ok)}
.pill.acc{background:var(--accent-soft);color:var(--accent)}
.duo{display:grid;grid-template-columns:minmax(0,3fr) minmax(0,2fr);gap:14px}
@media(max-width:820px){.duo{grid-template-columns:1fr}}
.chartbox{padding:16px 18px 12px}
.chartbox h3,.drivers h3{font-size:14px;font-weight:700;margin-bottom:2px}
.chartbox .cap,.drivers .cap{font-size:12px;color:var(--ink3);margin-bottom:10px}
.legend{display:flex;flex-wrap:wrap;gap:12px 16px;font-size:12px;color:var(--ink2);margin:6px 0 2px}
.legend i{display:inline-block;width:14px;height:3px;border-radius:2px;background:var(--accent);
vertical-align:middle;margin-right:5px}
.legend i.band{height:10px;background:var(--band2)}
svg text{font-family:"IBM Plex Sans KR",sans-serif}
.range-figures{display:flex;flex-wrap:wrap;gap:8px 20px;font-size:12.5px;color:var(--ink2);
margin-top:8px;padding-top:8px;border-top:1px dashed var(--line)}
.range-figures b{color:var(--ink);font-weight:700}
.mech{margin-top:10px;background:var(--paper);border:1px solid var(--line);border-radius:8px;
padding:10px 14px;font-size:12.5px;line-height:1.8;color:var(--ink2)}
.mech summary{cursor:pointer;font-weight:500;color:var(--accent)}
.mech b{color:var(--ink)}.mech ol{padding-left:18px;margin-top:6px}
.drivers{padding:16px 18px}
.drv{display:grid;grid-template-columns:20px minmax(0,1fr);gap:0 10px;padding:9px 0;
border-bottom:1px solid var(--line)}
.drv:last-child{border-bottom:none}
.drv .rank{font-weight:700;color:var(--ink3);font-size:13px;padding-top:1px}
.drv .name{font-weight:500;font-size:13.5px}
.dir{font-size:12px;margin-left:6px}.dir.up{color:var(--up)}.dir.down{color:var(--down)}
.drv .barrow{display:flex;align-items:center;gap:8px;margin-top:4px}
.drv .bar{height:8px;border-radius:2px;background:var(--accent)}
.drv .shap{font-size:11.5px;color:var(--ink2);white-space:nowrap}
.drv .news{font-size:12px;color:var(--ink2);margin-top:4px}
.drv .news .stars{color:var(--warn);letter-spacing:1px}
.alert{display:grid;grid-template-columns:4px minmax(0,1fr);border-radius:8px;overflow:hidden;
border:1px solid var(--line);background:var(--surface);margin-bottom:10px}
.alert .stripe{background:var(--warn)}
.alert .body{padding:14px 18px}
.alert .head{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-weight:700;font-size:14px}
.alert .detail{font-size:13px;color:var(--ink2);margin-top:4px}
.tablewrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:13.5px;min-width:640px}
th{font-size:11.5px;color:var(--ink2);letter-spacing:.05em;font-weight:500;text-align:right;
padding:8px 10px;border-bottom:1px solid var(--line)}
th:first-child{text-align:left}
td{padding:9px 10px;border-bottom:1px solid var(--line);text-align:right}
td:first-child{text-align:left;font-weight:500}
tr:last-child td{border-bottom:none}
td .src{color:var(--ink3);font-size:11.5px;font-weight:400;margin-left:6px}
.z-hot{background:var(--warn-soft);border-radius:4px;padding:1px 6px;color:var(--warn);
font-weight:700}
.mapbox{padding:16px 18px 12px}.mapbox h3{font-size:14px;font-weight:700;margin-bottom:8px}
.map-legend{display:flex;flex-wrap:wrap;gap:12px 18px;font-size:12px;color:var(--ink2);
margin-top:6px}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;vertical-align:-1px;
margin-right:5px}
.dot.ok{background:var(--ok)}.dot.warn{background:var(--warn)}.dot.crit{background:var(--crit)}
.signals{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
.sig-item{padding:13px 16px}
.sig-item .tag{font-size:11.5px;font-weight:700;color:var(--accent);letter-spacing:.03em}
.sig-item p{font-size:13px;margin-top:3px;overflow-wrap:anywhere}
.sig-item .src{font-size:11.5px;color:var(--ink3);margin-top:6px}
.chain{margin-top:10px;background:var(--paper);border:1px solid var(--line);border-radius:8px;
padding:8px 12px;font-size:12px;overflow-x:auto}
.chain summary{cursor:pointer;color:var(--accent);font-weight:500}
.chain .row{display:flex;align-items:center;gap:6px;white-space:nowrap;margin-top:8px}
.chain .node{border:1px solid var(--line);background:var(--surface);border-radius:6px;
padding:3px 9px;font-weight:500}
.chain .node.ent{border-color:var(--accent);color:var(--accent)}
.chain .node.edge{background:var(--accent-soft);color:var(--accent);border-color:transparent;
font-weight:700}
.chain .arr{color:var(--ink3)}
.chain .meta{color:var(--ink3);margin-top:6px;white-space:normal}
.cal{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}
.cal-item{padding:14px 16px;display:flex;gap:14px;align-items:center}
.dday{font-weight:700;font-size:19px;color:var(--accent);min-width:56px;text-align:center;
background:var(--accent-soft);border-radius:8px;padding:8px 4px;line-height:1.15}
.dday small{display:block;font-size:10px;font-weight:500}
.cal-item .what{font-weight:500;font-size:13.5px}
.cal-item .when{font-size:12px;color:var(--ink3)}
.appx{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
.appx-item{padding:13px 16px}
.appx-item .org{font-size:12px;font-weight:700;color:var(--ink2)}
.appx-item p{font-size:13px;margin-top:3px;overflow-wrap:anywhere}
.appx-item .src{font-size:11.5px;margin-top:6px}
footer{margin-top:44px;border-top:1px solid var(--line);padding-top:16px;font-size:12px;
color:var(--ink3);line-height:1.8}
footer .hitl{color:var(--ink2);font-weight:500}
"""
