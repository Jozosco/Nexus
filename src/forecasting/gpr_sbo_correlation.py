"""
GPR × SBO 상관관계 분석 — WBS 1.4.1
지정학 리스크 지수(GPR/AIS/GeoIntel)와 CBOT 대두유 선물 가격의 롤링 상관관계 분석.

참조: Shadowbroker 지정학 인텔리전스 패턴 (github.com/BigBodyCobain/Shadowbroker)
분석 목적: 리스크 경보 발령 시 SBO 가격에 대한 선행 신호 여부 식별

수집 대상:
  GPR 지수       — data/raw/geopolitical_indices_*.parquet (indicator_code=GPR)
  AIS 해협 리스크 — data/raw/ais_strait_risk_*.parquet (SBO_STRAIT_RISK_COMPOSITE)
  GeoIntel 복합  — data/raw/geointel_*.parquet (GEOINTEL_RISK_COMPOSITE)
  CBOT SBO 선물  — data/raw/commodity_data_*.parquet (indicator_code=CBOT_SBO_FUTURES)

분석 방법:
  롤링 피어슨 상관 (7일/30일/90일 창)
  경보 조건: 30일 창 r ≥ 0.60 (CLAUDE.md §1 대두유 스코프)
  리드-랙 교차상관 (±30일, Granger 인과관계 근사)

출력: reports/pipeline/gpr_sbo_correlation_{today}.html
"""

from __future__ import annotations

import glob
import os
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

OUTPUT_DIR = "reports/pipeline"
DATA_DIR   = "data/raw"

CORRELATION_ALERT_THRESHOLD = 0.60
ROLLING_WINDOWS = [7, 30, 90]
LAG_RANGE       = 30

GPR_SIGNALS: dict[str, str] = {
    "GPR":                     "GPR 종합 지수",
    "GPR_REALTIME":            "GPR 실시간",
    "HORMUZ_THREAT_LEVEL":     "호르무즈 위협 수준",
    "SBO_STRAIT_RISK_COMPOSITE": "AIS 해협 복합 리스크",
    "GEOINTEL_RISK_COMPOSITE": "GeoIntel 복합 지수",
    "SEISMIC_PANAMA_CANAL_MAG": "파나마 지진 강도",
    "SEISMIC_HORMUZ_MAG":      "호르무즈 지진 강도",
    "SEISMIC_MALACCA_MAG":     "말라카 지진 강도",
}

SBO_SIGNAL = "CBOT_SBO_FUTURES"


def _load_parquets(pattern: str) -> pd.DataFrame:
    """data/raw/에서 패턴에 맞는 모든 parquet 파일을 하나의 DataFrame으로 합산."""
    files = sorted(glob.glob(os.path.join(DATA_DIR, pattern)))
    if not files:
        return pd.DataFrame()
    frames = []
    for f in files:
        try:
            frames.append(pd.read_parquet(f))
        except Exception as e:
            print(f"[경고] parquet 로드 실패 ({f}): {e}")
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _pivot_to_daily(df: pd.DataFrame, signal_codes: list[str]) -> pd.DataFrame:
    """indicator_code 기준으로 wide 포맷 변환 (price_date × signal)."""
    if df.empty:
        return pd.DataFrame()
    df = df[df["indicator_code"].isin(signal_codes)].copy()
    df["price_date"] = pd.to_datetime(df["price_date"]).dt.normalize()
    daily = (
        df.groupby(["price_date", "indicator_code"])["value"]
        .mean()
        .reset_index()
        .pivot(index="price_date", columns="indicator_code", values="value")
    )
    return daily.sort_index()


def _load_all_signals() -> pd.DataFrame:
    """GPR/AIS/GeoIntel/SBO 신호를 하나의 daily wide DataFrame으로 반환."""
    sources = [
        ("geopolitical_indices_*.parquet", list(GPR_SIGNALS.keys())),
        ("ais_strait_risk_*.parquet",      ["SBO_STRAIT_RISK_COMPOSITE"]),
        ("geointel_*.parquet",             ["GEOINTEL_RISK_COMPOSITE",
                                            "SEISMIC_PANAMA_CANAL_MAG",
                                            "SEISMIC_HORMUZ_MAG",
                                            "SEISMIC_MALACCA_MAG"]),
        ("commodity_data_*.parquet",       [SBO_SIGNAL]),
    ]
    pivot_frames = []
    for pattern, codes in sources:
        raw = _load_parquets(pattern)
        pv  = _pivot_to_daily(raw, codes)
        if not pv.empty:
            pivot_frames.append(pv)

    if not pivot_frames:
        return pd.DataFrame()

    combined = pivot_frames[0]
    for f in pivot_frames[1:]:
        combined = combined.join(f, how="outer")
    return combined.sort_index()


def _rolling_correlation(wide: pd.DataFrame, window: int) -> pd.DataFrame:
    """SBO 선물 대비 각 GPR 신호의 rolling Pearson 상관계수 반환."""
    if SBO_SIGNAL not in wide.columns:
        return pd.DataFrame()
    result_cols = {}
    for col in wide.columns:
        if col == SBO_SIGNAL:
            continue
        r = wide[col].rolling(window, min_periods=max(3, window // 3)).corr(wide[SBO_SIGNAL])
        result_cols[col] = r
    return pd.DataFrame(result_cols, index=wide.index)


def _detect_alerts(corr_30d: pd.DataFrame) -> list[dict]:
    """30일 창 기준 r ≥ 0.60 경보 목록 반환."""
    alerts = []
    if corr_30d.empty:
        return alerts
    latest = corr_30d.iloc[-1].dropna()
    for signal, r_val in latest.items():
        if abs(r_val) >= CORRELATION_ALERT_THRESHOLD:
            label = GPR_SIGNALS.get(str(signal), str(signal))
            direction = "양의" if r_val > 0 else "음의"
            alerts.append({
                "signal":    str(signal),
                "label":     label,
                "r":         round(float(r_val), 3),
                "direction": direction,
                "message":   (
                    f"[경보] {label} × SBO 선물 {direction} 상관 r={r_val:.3f} "
                    f"(임계값 ±{CORRELATION_ALERT_THRESHOLD}) — 가격 이동 선행 신호 가능성"
                ),
            })
    alerts.sort(key=lambda x: abs(x["r"]), reverse=True)
    return alerts


def _lead_lag_cross_corr(wide: pd.DataFrame, signal: str) -> pd.Series:
    """signal 대비 SBO 선물 가격의 ±LAG_RANGE일 교차상관 반환."""
    if signal not in wide.columns or SBO_SIGNAL not in wide.columns:
        return pd.Series(dtype=float)
    x = wide[signal].dropna()
    y = wide[SBO_SIGNAL].dropna()
    common = x.index.intersection(y.index)
    if len(common) < 10:
        return pd.Series(dtype=float)
    x_c = (x[common] - x[common].mean()) / (x[common].std() + 1e-9)
    y_c = (y[common] - y[common].mean()) / (y[common].std() + 1e-9)
    lags = range(-LAG_RANGE, LAG_RANGE + 1)
    values = []
    for lag in lags:
        if lag >= 0:
            r = float(np.corrcoef(x_c.iloc[:len(x_c)-lag or None],
                                   y_c.iloc[lag:])[0, 1]) if lag < len(x_c) else np.nan
        else:
            r = float(np.corrcoef(x_c.iloc[-lag:],
                                   y_c.iloc[:len(y_c)+lag or None])[0, 1]) if -lag < len(y_c) else np.nan
        values.append(r)
    return pd.Series(values, index=list(lags), name=signal)


def _build_html_report(
    wide: pd.DataFrame,
    corr_frames: dict[int, pd.DataFrame],
    alerts: list[dict],
    lead_lag: dict[str, pd.Series],
) -> str:
    """HTML 보고서 문자열 생성."""
    today_str  = date.today().isoformat()
    data_start = wide.index.min().date().isoformat() if not wide.empty else "N/A"
    data_end   = wide.index.max().date().isoformat() if not wide.empty else "N/A"

    alert_html = _render_alert_table(alerts)
    corr_table  = _render_correlation_table(corr_frames)
    lag_section = _render_lead_lag_section(lead_lag)

    available_signals = [c for c in wide.columns if c != SBO_SIGNAL]
    signal_list = "".join(f"<li><code>{s}</code> — {GPR_SIGNALS.get(s, s)}</li>"
                          for s in available_signals)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>GPR × SBO 상관관계 분석 — {today_str}</title>
<style>
  body {{ font-family: 'Noto Sans KR', sans-serif; margin: 2rem; color: #1a1a2e; background: #f8f9fa; }}
  h1 {{ color: #16213e; border-bottom: 3px solid #e94560; padding-bottom: 0.5rem; }}
  h2 {{ color: #0f3460; margin-top: 2rem; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
  th {{ background: #16213e; color: white; padding: 0.6rem 1rem; text-align: left; }}
  td {{ padding: 0.5rem 1rem; border-bottom: 1px solid #dee2e6; }}
  tr:nth-child(even) td {{ background: #f0f4f8; }}
  .alert-high {{ background: #fff3cd !important; font-weight: bold; }}
  .alert-critical {{ background: #f8d7da !important; font-weight: bold; }}
  .meta {{ color: #666; font-size: 0.9rem; margin-bottom: 1rem; }}
  .no-data {{ color: #999; font-style: italic; padding: 1rem; }}
  pre {{ background: #1a1a2e; color: #a8ff78; padding: 1rem; border-radius: 4px; overflow-x: auto; }}
</style>
</head>
<body>
<h1>GPR × SBO 상관관계 분석 보고서</h1>
<p class="meta">생성일: {today_str} | 데이터 기간: {data_start} ~ {data_end} |
분석 범위: GPR / AIS / GeoIntel × CBOT 대두유 선물</p>

<h2>분석 신호 목록</h2>
<ul>{signal_list if signal_list else '<li class="no-data">수집된 신호 없음</li>'}</ul>

<h2>경보 현황 (30일 창, |r| ≥ {CORRELATION_ALERT_THRESHOLD})</h2>
{alert_html}

<h2>롤링 피어슨 상관계수 최신값</h2>
{corr_table}

<h2>리드-랙 교차상관 (±{LAG_RANGE}일)</h2>
{lag_section}

<hr>
<p class="meta">Project Nexus · WBS 1.4.1 · CLAUDE.md §6 HITL 준수 — 조달 결정은 별도 인간 승인 필요</p>
</body>
</html>"""


def _render_alert_table(alerts: list[dict]) -> str:
    if not alerts:
        return '<p class="no-data">현재 경보 없음 (|r| &lt; 0.60)</p>'
    rows = ""
    for a in alerts:
        cls = "alert-critical" if abs(a["r"]) >= 0.75 else "alert-high"
        rows += (f'<tr class="{cls}"><td>{a["label"]}</td><td>{a["r"]:+.3f}</td>'
                 f'<td>{a["direction"]} 상관</td><td>{a["message"]}</td></tr>\n')
    return (f'<table><tr><th>신호</th><th>r 값</th><th>방향</th><th>경보 내용</th></tr>'
            f'{rows}</table>')


def _render_correlation_table(corr_frames: dict[int, pd.DataFrame]) -> str:
    """7d/30d/90d 창 최신 r 값을 표로 출력."""
    signals = set()
    for cf in corr_frames.values():
        signals.update(cf.columns.tolist())
    if not signals:
        return '<p class="no-data">상관계수 데이터 없음</p>'

    header = "<tr><th>신호</th>" + "".join(f"<th>{w}일 r</th>" for w in ROLLING_WINDOWS) + "</tr>\n"
    rows   = ""
    for sig in sorted(signals):
        label = GPR_SIGNALS.get(sig, sig)
        cells = f"<td>{label}</td>"
        for w in ROLLING_WINDOWS:
            cf = corr_frames.get(w, pd.DataFrame())
            if not cf.empty and sig in cf.columns and not cf[sig].dropna().empty:
                r = cf[sig].dropna().iloc[-1]
                flag = " 🔴" if abs(r) >= 0.75 else (" 🟡" if abs(r) >= 0.60 else "")
                cells += f"<td>{r:+.3f}{flag}</td>"
            else:
                cells += "<td>—</td>"
        rows += f"<tr>{cells}</tr>\n"
    return f"<table>{header}{rows}</table>"


def _render_lead_lag_section(lead_lag: dict[str, pd.Series]) -> str:
    if not lead_lag:
        return '<p class="no-data">리드-랙 데이터 없음 (SBO 선물 parquet 확인 필요)</p>'
    sections = []
    for signal, series in lead_lag.items():
        if series.empty:
            continue
        label    = GPR_SIGNALS.get(signal, signal)
        peak_lag = int(series.abs().idxmax())
        peak_r   = float(series.iloc[series.abs().argmax()])
        direction = "선행" if peak_lag < 0 else ("동행" if peak_lag == 0 else "후행")
        interp    = (f"최대 교차상관: lag={peak_lag:+d}일 r={peak_r:+.3f} "
                     f"→ {label}이(가) SBO 선물에 {abs(peak_lag)}일 {direction}")
        rows = "".join(
            f"<tr><td>{lag:+d}</td><td>{r:+.3f}</td></tr>"
            for lag, r in series.items()
            if abs(r) >= 0.30
        )
        tbl = (f"<table><tr><th>lag(일)</th><th>r</th></tr>{rows}</table>"
               if rows else '<p class="no-data">유의미한 상관(|r|≥0.30) 없음</p>')
        sections.append(f"<h3>{label}</h3><p>{interp}</p>{tbl}")
    return "\n".join(sections) if sections else '<p class="no-data">교차상관 분석 불가</p>'


def run() -> None:
    """GPR × SBO 상관관계 분석 실행 및 HTML 보고서 저장."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y%m%d")

    wide = _load_all_signals()
    if wide.empty:
        print("[경고] GPR×SBO 상관분석: 신호 데이터 없음 — data/raw/ parquet 확인 필요")
        return

    if SBO_SIGNAL not in wide.columns:
        print(f"[경고] SBO 선물 신호({SBO_SIGNAL}) 없음 — commodity_data_*.parquet 확인 필요")

    corr_frames: dict[int, pd.DataFrame] = {}
    for w in ROLLING_WINDOWS:
        corr_frames[w] = _rolling_correlation(wide, w)

    alerts  = _detect_alerts(corr_frames.get(30, pd.DataFrame()))
    for a in alerts:
        print(a["message"])

    risk_signals = [s for s in wide.columns if s != SBO_SIGNAL and s in GPR_SIGNALS]
    lead_lag = {s: _lead_lag_cross_corr(wide, s) for s in risk_signals[:5]}

    html     = _build_html_report(wide, corr_frames, alerts, lead_lag)
    out_path = f"{OUTPUT_DIR}/gpr_sbo_correlation_{today}.html"
    Path(out_path).write_text(html, encoding="utf-8")
    print(f"[완료] GPR×SBO 상관분석 보고서 → {out_path} ({len(wide)}일 데이터, 경보 {len(alerts)}건)")


if __name__ == "__main__":
    run()
