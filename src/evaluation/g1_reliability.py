"""G1 보고서 신뢰도 지표 — 2단계 검증 (2026-09-14 · A-264).

승인자 요구: G1(약 15개년 과거 데이터로 현재 핵심 변인 식별)·G2(G1 결과 기반 가격 변동 범위)는
①과거 데이터 기반 1차 검증 → ②실시간 수집 데이터 유형별 적용 논리의 2차 검증을 거치므로,
'G1 보고서' 신뢰도를 재는 **구체 지표**가 필요하다.

설계 정본: docs/research_desk/2026-09/g1_report_trust_and_cadence_2026_09_02.md §2(6축)
서술 계약: G1은 예측 모델이 아니다(A-191) — 여기서의 수치는 '예측 정확도'가 아니라
**신뢰 지표**(과거 관측의 요약·과정 무결성)이며 방향 적중률·확률 주장은 산출하지 않는다.

1단계 — 과거 데이터 검증(H)          | 2단계 — 실시간 수집 데이터 검증(R)
  H1 변인 순위 안정성(폴드 간 ρ)      |   R1 입력 정확도(정산가 교차검증)
  H2 인과 검정 재현성(창 간 지속률)    |   R2 시점 정확도(정합 위반·개정 미보존 지표 수)
  H3 경보 규칙 소급 성적(오경보 근사)  |   R3 경보 정합성(보고서 경보 수 = 서명 스탬프)
  H4 참고 범위 폭 진단(포함률·폭)      |   R4 발행 무결성(스탬프 판정 분포·연속 통과일)
  H5 유사 시기 참조 분별력(조건부 폭)  |   R5 수집 채널 실적(비정형 아카이브 도달률·채널)
                                     |   R6 데이터 유형별 규칙 재검증표

입력 우선순위: ① CI 마트(data/gold/feature_mart.parquet — 정산가 정본·전 피처)
             ② 로컬 진단 모드(Databento UTC 종가 CSV + 수동 파케이) — 라벨 '진단(부분)'
산출: data/processed/g1_reliability_latest.json(브리프 신뢰도 스트립 입력) ·
      reports/market/g1_reliability_{date}.md(월별 부록)

실행: python -m src.evaluation.g1_reliability [--mode alert|weekly|monthly|full] [--report-dir DIR]
      alert 모드는 R만(경량), 나머지는 H+R.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

HORIZONS: tuple[int, ...] = (5, 20, 60)
WINDOW_START = "2010-01-01"
WINDOW_END = os.environ.get("ANALYSIS_END_DATE", "2025-12-31")
STRESS_SLICES: dict[str, tuple[str, str]] = {
    "2012 가뭄":   ("2012-01-01", "2012-12-31"),
    "2018 미·중":  ("2018-01-01", "2018-12-31"),
    "2020 팬데믹": ("2020-01-01", "2020-12-31"),
    "2022 러·우":  ("2022-01-01", "2022-12-31"),
    "2025":        ("2025-01-01", "2025-12-31"),
}
RULE_VERSION = "임계 규칙 v2026-08-25"        # D-3 처분(GPR P90 단일 기준) 이후 버전
MIN_EPISODES = 8                               # 미만이면 '표본 부족 — 보류'(analogue와 동일)
TOP_N = 20
N_FOLDS = 5

LATEST_JSON = Path("data/processed/g1_reliability_latest.json")
ALERT_LEDGER = Path("data/processed/g1_alert_ledger.csv")
STAMPS_CSV = Path("data/processed/signed_daily_stamps.csv")
SIGNALS_CSV = Path("data/processed/unstructured_daily_signals.csv")
CONTRACT_YAML = Path("data/gold/feature_contract.yaml")
ALERT_LATEST = Path("reports/pipeline/latest/g1_alert_latest.md")
BRIEF_LATEST = Path("reports/pipeline/latest/g1_daily_brief_latest.html")
DATABENTO_CSV_GLOB = "data/raw/Databento/GLBX.MDP3/ZL_ohlcv-1d_*.csv"
TE_PARQUET = Path("data/raw/te_commodities_historical.parquet")

# 서술 계약(A-191) — 산출 문서에 절대 넣지 않는 표현
FORBIDDEN_PHRASES = ("예측 정확도", "적중률", "상승 확률", "하락 확률", "전망치")
REQUIRED_CAPTION = ("본 지표는 과거 관측의 요약과 과정 무결성의 측정이며 향후 전망·확률 주장이 아님. "
                    "참고 범위 포함률은 범위 폭 진단일 뿐 확률 밴드 주장이 아니므로 의사결정 근거로 쓰지 않음.")


# ─────────────────────────────────────────────────────────────────────────────
# 입력
# ─────────────────────────────────────────────────────────────────────────────
class Inputs:
    """평가 입력 — close(일별 종가), levels(일별 지표 수준), features(피처, 선택), basis 라벨."""

    def __init__(self, close: pd.Series, levels: pd.DataFrame,
                 features: pd.DataFrame | None, basis: str, source: str) -> None:
        self.close = close.sort_index()
        self.levels = levels.sort_index()
        self.features = features
        self.basis = basis
        self.source = source


def _forward_returns(close: pd.Series, horizons: tuple[int, ...] = HORIZONS) -> pd.DataFrame:
    """target_ret{h} = log(close[t+h]/close[t]) — 마트와 동일 정의(유일한 전방참조)."""
    out = {}
    logc = np.log(close.astype(float))
    for h in horizons:
        out[f"target_ret{h}"] = logc.shift(-h) - logc
    return pd.DataFrame(out, index=close.index)


def load_inputs() -> Inputs:
    """① CI 마트 → ② 로컬 진단 모드. 어느 쪽인지 basis에 정직 표기."""
    try:
        from src.forecasting.variable_importance_g1 import _load_g1_feature_mart, G1_TARGET_COL
        analysis, levels, target_label = _load_g1_feature_mart(horizon=20)
        close = levels[G1_TARGET_COL].dropna()
        feats = analysis.drop(columns=[c for c in analysis.columns if c.startswith("target_")])
        levels = levels.drop(columns=[G1_TARGET_COL], errors="ignore")
        return Inputs(close, levels, feats, basis="정본(시카고 정산가 교차검증 계열)",
                      source="data/gold/feature_mart.parquet")
    except Exception as e:                                  # noqa: BLE001 — 진단 모드로 강등
        print(f"[정보] CI 마트 미가용({type(e).__name__}) — 로컬 진단 모드로 산출")
    files = sorted(glob.glob(DATABENTO_CSV_GLOB))
    if not files:
        raise RuntimeError("[오류] 평가 입력 없음 — 마트도 Databento CSV도 없습니다.")
    raw = pd.read_csv(files[-1])
    raw["price_date"] = pd.to_datetime(raw["price_date"], errors="coerce")
    raw = raw.dropna(subset=["price_date", "close"])
    raw = raw[raw["price_date"].dt.weekday < 5]             # A-131: 일요일 저녁 세션 제거
    close = (raw.sort_values(["price_date", "volume"])
                .drop_duplicates("price_date", keep="last")   # 롤일: 거래량 최대 계약(A-111)
                .set_index("price_date")["close"].astype(float))
    levels = pd.DataFrame(index=close.index)
    if TE_PARQUET.is_file():
        te = pd.read_parquet(TE_PARQUET)
        piv = (te.pivot_table(index="price_date", columns="indicator_code", values="value",
                              aggfunc="last").sort_index())
        levels = piv.reindex(close.index, method="ffill")
    return Inputs(close, levels, levels.copy() if not levels.empty else None,
                  basis="진단(부분) — Databento UTC 종가·수동 파케이 26지표", source=files[-1])


def _window(idx: pd.DatetimeIndex) -> pd.Series:
    return (idx >= pd.Timestamp(WINDOW_START)) & (idx <= pd.Timestamp(WINDOW_END))


# ─────────────────────────────────────────────────────────────────────────────
# H1 변인 순위 안정성
# ─────────────────────────────────────────────────────────────────────────────
def _spearman(a: pd.Series, b: pd.Series) -> float:
    j = pd.concat([a, b], axis=1).dropna()
    if len(j) < 3:
        return float("nan")
    return float(j.iloc[:, 0].rank().corr(j.iloc[:, 1].rank()))


def rank_stability(features: pd.DataFrame, target: pd.Series, n_folds: int = N_FOLDS,
                   top_n: int = TOP_N) -> dict[str, Any]:
    """확장 폴드 n개에서 |피어슨 r| 순위를 만들고 인접 폴드 간 Spearman ρ·부호 일치율을 잰다.

    폴드 = 분석창을 n+1 등분한 누적 창(TimeSeriesSplit expanding과 동형). 데이터 과학 관점의
    안정성 정의: 순위가 표본 추가에 흔들리지 않을수록 '현재 핵심 변인' 주장이 견고하다.
    sklearn이 있으면 Elastic Net(고정 α=0.01·l1=0.5, 폴드 내 대치·표준화)으로도 같은 통계를 낸다.
    """
    X = features.copy()
    X = X.loc[:, X.notna().mean() >= 0.60]
    X = X.loc[:, ~X.columns.str.startswith("target_")]
    j = pd.concat([X, target.rename("__y")], axis=1).dropna(subset=["__y"])
    j = j[_window(j.index)]
    if len(j) < 200 or X.shape[1] < 3:
        return {"status": "산출 보류", "reason": f"표본 {len(j)}행·변수 {X.shape[1]}개 — 부족"}
    cuts = np.linspace(len(j) // (n_folds + 1), len(j), n_folds + 1, dtype=int)[1:]
    pearson_ranks: list[pd.Series] = []
    en_ranks: list[pd.Series] = []
    try:
        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import ElasticNet
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        have_sk = True
    except Exception:                                       # noqa: BLE001
        have_sk = False
    for c in cuts:
        sub = j.iloc[:c]
        r = sub.drop(columns="__y").corrwith(sub["__y"])
        pearson_ranks.append(r)
        if have_sk:
            pipe = Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler()),
                             ("m", ElasticNet(alpha=0.01, l1_ratio=0.5, max_iter=5000,
                                               random_state=42))])
            pipe.fit(sub.drop(columns="__y"), sub["__y"])
            en_ranks.append(pd.Series(pipe.named_steps["m"].coef_, index=sub.columns.drop("__y")))

    def _stats(series_list: list[pd.Series]) -> dict[str, Any]:
        rhos, signs = [], []
        for a, b in zip(series_list[:-1], series_list[1:]):
            top = set(a.abs().nlargest(top_n).index) | set(b.abs().nlargest(top_n).index)
            rhos.append(_spearman(a.abs().reindex(list(top)), b.abs().reindex(list(top))))
            tb = b.abs().nlargest(top_n).index
            signs.append(float((np.sign(a.reindex(tb)) == np.sign(b.reindex(tb))).mean()))
        last = series_list[-1]
        return {"adjacent_fold_spearman": [round(x, 3) for x in rhos],
                "mean_spearman": round(float(np.nanmean(rhos)), 3),
                "sign_agreement_top": round(float(np.nanmean(signs)), 3),
                "top_last_fold": [str(v) for v in last.abs().nlargest(10).index]}
    out: dict[str, Any] = {"status": "산출", "n_rows": int(len(j)), "n_features": int(X.shape[1]),
                           "n_folds": n_folds, "pearson": _stats(pearson_ranks)}
    out["elastic_net"] = _stats(en_ranks) if have_sk else {"status": "미산출(sklearn 부재 — CI에서 산출)"}
    return out


# ─────────────────────────────────────────────────────────────────────────────
# H2 인과 검정 재현성
# ─────────────────────────────────────────────────────────────────────────────
def granger_persistence(features: pd.DataFrame, target: pd.Series, top_vars: list[str],
                        max_lag: int = 4, alpha: float = 0.05) -> dict[str, Any]:
    """상위 변인의 Granger 유의(본페로니 α/m)가 전체 창→최근 5년→사건 연도에서 지속되는 비율.

    입력은 1차 차분(수준 비정상성 방어). 유의성은 '지속되는가'만 본다 — 인과 주장 아님(SHAP≠인과).
    """
    try:
        from statsmodels.tsa.stattools import grangercausalitytests
    except Exception:                                       # noqa: BLE001
        return {"status": "미산출(statsmodels 부재)"}
    vars_ = [v for v in top_vars if v in features.columns][:10]
    if not vars_:
        return {"status": "산출 보류", "reason": "상위 변인 없음"}
    y = target.dropna()
    windows = {"전체(2010~2025)": (WINDOW_START, WINDOW_END),
               "최근 5년(2021~2025)": ("2021-01-01", WINDOW_END),
               "사건 연도 합집합": None}
    m = len(vars_)
    res: dict[str, dict[str, bool]] = {}
    for name, w in windows.items():
        res[name] = {}
        for v in vars_:
            x = features[v].astype(float).diff()
            j = pd.concat([y.rename("y"), x.rename("x")], axis=1).dropna()
            if w is None:
                mask = np.zeros(len(j), dtype=bool)
                for s, e in STRESS_SLICES.values():
                    mask |= ((j.index >= pd.Timestamp(s)) & (j.index <= pd.Timestamp(e)))
                j = j[mask]
            else:
                j = j[(j.index >= pd.Timestamp(w[0])) & (j.index <= pd.Timestamp(w[1]))]
            if len(j) < 60:
                res[name][v] = False
                continue
            try:
                g = grangercausalitytests(j[["y", "x"]], maxlag=max_lag, verbose=False)
                p = min(g[k][0]["ssr_ftest"][1] for k in g)
                res[name][v] = bool(p < alpha / m)
            except Exception:                               # noqa: BLE001
                res[name][v] = False
    full_sig = [v for v, ok in res["전체(2010~2025)"].items() if ok]
    persist = [v for v in full_sig if any(res[n].get(v) for n in windows if n != "전체(2010~2025)")]
    return {"status": "산출", "n_vars": m, "alpha_bonferroni": round(alpha / m, 4),
            "significant_full": full_sig,
            "persistence_rate": (round(len(persist) / len(full_sig), 3) if full_sig else None),
            "by_window": {n: sorted(v for v, ok in d.items() if ok) for n, d in res.items()}}


# ─────────────────────────────────────────────────────────────────────────────
# H3 경보 규칙 소급 성적
# ─────────────────────────────────────────────────────────────────────────────
def _z90(s: pd.Series) -> pd.Series:
    s = s.astype(float)
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    capped = s.clip(q1 - 1.5 * iqr, q3 + 1.5 * iqr) if iqr > 0 else s   # D6: z 경로만 캡
    m = capped.rolling(90, min_periods=30).mean()
    sd = capped.rolling(90, min_periods=30).std(ddof=1)
    return (capped - m) / sd


def _episodes(breach: pd.Series, gap: int) -> list[pd.Timestamp]:
    """발화일을 간격≥gap(거래일)로 압축한 에피소드 시작일 — analogue와 같은 규칙."""
    idx = list(breach.index[breach.fillna(False).astype(bool)])
    pos = {d: i for i, d in enumerate(breach.index)}
    out: list[pd.Timestamp] = []
    last = -10 ** 9
    for d in idx:
        if pos[d] - last >= gap:
            out.append(d)
            last = pos[d]
    return out


def _rules(levels: pd.DataFrame) -> dict[str, tuple[pd.Series | None, str]]:
    """평가 가능한 임계 규칙(현행 5종) → (발화 불리언 계열, 정의). 계열 부재는 None."""
    def col(*cands: str) -> pd.Series | None:
        for c in cands:
            if c in levels.columns and levels[c].notna().sum() > 100:
                return levels[c]
        return None
    rules: dict[str, tuple[pd.Series | None, str]] = {}
    bdi = col("TE_BDI", "BDI")
    rules["해상운임(BDI) 90일 편차 > 2σ"] = ((_z90(bdi) > 2.0) if bdi is not None else None,
                                          "IQR 캡·90일 롤링(관측≥30) 표준화 지수 > 2")
    oni = col("ENSO_ONI", "ONI")
    rules["엘니뇨·라니냐 강도 |ONI| ≥ 0.5"] = ((oni.abs() >= 0.5) if oni is not None else None,
                                            "절댓값 0.5°C 이상")
    gpr = col("GPR", "GPR_NORMALIZED")
    if gpr is not None:
        p90 = gpr.rolling(1260, min_periods=250).quantile(0.90).shift(1)   # 과거 전용(P0-2)
        rules["지정학 위험 지수 ≥ 과거 5년 상위 10%"] = ((gpr >= p90), "직전 1,260거래일 P90(t−1까지) 이상")
    else:
        rules["지정학 위험 지수 ≥ 과거 5년 상위 10%"] = (None, "직전 1,260거래일 P90 이상")
    stu = col("WASDE_SBO_STU", "WASDE_STU")
    if stu is not None:
        s = stu.astype(float)
        s = s / 100.0 if s.median() > 1 else s
        rules["재고사용비율 < 10%"] = ((s < 0.10), "세계 대두유 STU < 10% — 실측 5.5~9.4%라 상시 발화(죽은 규칙, P0-3)")
    else:
        rules["재고사용비율 < 10%"] = (None, "세계 대두유 STU < 10%")
    rules["대두유−팜유 가격 차이 > 175 $/MT"] = (None, "환산 파생 계열 미구축(P0-3) — 미평가")
    return rules


def alert_rule_retro(levels: pd.DataFrame, close: pd.Series) -> dict[str, Any]:
    """임계 규칙을 2010~2025에 소급 적용한 '실발행 아님 — 소급 합성' 성적.

    에피소드 뒤 5/20/60거래일 |수익률|이 무조건부 중앙값 이하인 비율 = 오경보 근사율.
    방향 적중률은 산출하지 않는다(A-191). 표본 8회 미만은 보류.
    """
    fwd = _forward_returns(close).abs()
    w = _window(fwd.index)
    out: dict[str, Any] = {"label": "실발행 아님 — 소급 합성", "rule_version": RULE_VERSION,
                           "unconditional_median_abs": {}, "rules": {}}
    for h in HORIZONS:
        out["unconditional_median_abs"][str(h)] = round(float(fwd.loc[w, f"target_ret{h}"].median()), 4)
    for name, (breach, definition) in _rules(levels).items():
        entry: dict[str, Any] = {"definition": definition}
        if breach is None:
            entry["status"] = "미평가(계열 부재)"
            out["rules"][name] = entry
            continue
        b = breach.reindex(close.index).fillna(False).astype(bool)
        b = b[_window(b.index)]
        entry["breach_days"] = int(b.sum())
        entry["breach_share"] = round(float(b.mean()), 3)
        entry["horizons"] = {}
        for h in HORIZONS:
            eps = [d for d in _episodes(b, gap=h) if d in fwd.index]
            vals = fwd.loc[eps, f"target_ret{h}"].dropna()
            unc = out["unconditional_median_abs"][str(h)]
            if len(vals) < MIN_EPISODES:
                entry["horizons"][str(h)] = {"episodes": int(len(vals)), "status": "표본 부족 — 보류"}
                continue
            entry["horizons"][str(h)] = {
                "episodes": int(len(vals)),
                "false_alarm_proxy": round(float((vals <= unc).mean()), 3),
                "median_abs_move": round(float(vals.median()), 4),
                "ratio_vs_unconditional": round(float(vals.median() / unc), 2) if unc else None,
                "status": "산출"}
        entry["status"] = "산출"
        out["rules"][name] = entry
    return out


# ─────────────────────────────────────────────────────────────────────────────
# H4 참고 범위 폭 진단
# ─────────────────────────────────────────────────────────────────────────────
def reference_range_diagnosis(close: pd.Series) -> dict[str, Any]:
    """브리프 참고 범위(직전 h거래일 수익률의 P10~P90을 최근 종가에 적용)의 실측 포함률·폭.

    t 시점 범위는 t까지의 과거 수익률만 쓴다(확장 분위). 포함률은 '범위 폭 진단'이며 확률 밴드
    주장이 아니다 — 월별 부록 한정, 의사결정 근거 금지(신뢰 문서 §2 ④).
    """
    c = close.astype(float)
    out: dict[str, Any] = {"label": "범위 폭 진단(확률 밴드 주장 아님)", "nominal_coverage": 0.80,
                           "horizons": {}}
    for h in HORIZONS:
        r = c.pct_change(h)                      # r[t] = 수익률(t−h→t): t에 확정
        q10 = r.expanding(min_periods=250).quantile(0.10)
        q90 = r.expanding(min_periods=250).quantile(0.90)
        realized = c.shift(-h) / c - 1           # t→t+h 실측
        inside = ((realized >= q10) & (realized <= q90))
        valid = realized.notna() & q10.notna()
        mask = valid & _window(c.index)
        res: dict[str, Any] = {
            "n": int(mask.sum()),
            "coverage": round(float(inside[mask].mean()), 3) if mask.sum() else None,
            "mean_width_pct": round(float(((q90 - q10)[mask]).mean() * 100), 2) if mask.sum() else None,
            "by_slice": {}}
        for name, (s, e) in STRESS_SLICES.items():
            m2 = mask & (c.index >= pd.Timestamp(s)) & (c.index <= pd.Timestamp(e))
            if m2.sum() >= 20:
                res["by_slice"][name] = {"n": int(m2.sum()), "coverage": round(float(inside[m2].mean()), 3)}
        out["horizons"][str(h)] = res
    return out


# ─────────────────────────────────────────────────────────────────────────────
# H5 유사 시기 참조 분별력
# ─────────────────────────────────────────────────────────────────────────────
def analogue_discrimination(levels: pd.DataFrame, close: pd.Series, top_vars: list[str],
                            horizon: int = 20, bins: int = 10) -> dict[str, Any]:
    """변인 90일 표준화 지수 십분위 조건부 실측 분포(IQR)가 무조건부보다 얼마나 좁은가(비율<1 = 분별)."""
    fwd = _forward_returns(close)[f"target_ret{horizon}"]
    w = _window(fwd.index)
    unc_iqr = float(fwd[w].quantile(0.75) - fwd[w].quantile(0.25))
    out: dict[str, Any] = {"horizon": horizon, "unconditional_iqr": round(unc_iqr, 4), "vars": {}}
    for v in top_vars:
        if v not in levels.columns:
            continue
        z = _z90(levels[v]).reindex(fwd.index)
        j = pd.concat([z.rename("z"), fwd.rename("r")], axis=1)[w].dropna()
        if len(j) < 500:
            out["vars"][v] = {"status": "표본 부족 — 보류"}
            continue
        try:
            j["bin"] = pd.qcut(j["z"], bins, labels=False, duplicates="drop")
        except ValueError:
            out["vars"][v] = {"status": "구간 분할 불가"}
            continue
        g = j.groupby("bin")["r"]
        iqr = (g.quantile(0.75) - g.quantile(0.25))
        med = g.median()
        out["vars"][v] = {"status": "산출", "n": int(len(j)),
                          "mean_conditional_iqr_ratio": round(float(iqr.mean() / unc_iqr), 3) if unc_iqr else None,
                          "median_spread_across_bins": round(float(med.max() - med.min()), 4)}
        if len(out["vars"]) >= 3:
            break
    return out


# ─────────────────────────────────────────────────────────────────────────────
# 실시간 R1~R6 (원장·스탬프·아카이브·계약)
# ─────────────────────────────────────────────────────────────────────────────
def _read_csv(p: Path) -> pd.DataFrame:
    return pd.read_csv(p) if p.is_file() else pd.DataFrame()


def realtime_metrics(today: date | None = None) -> dict[str, Any]:
    today = today or date.today()
    out: dict[str, Any] = {}

    # R1 입력 정확도 — 정산가 교차검증 최신 리포트(CI 산출) → 없으면 마지막 확정 실측
    r1 = {"status": "미확인", "source": None}
    reps = sorted(glob.glob("reports/market/session_close_validation_*.md"))
    if reps:
        txt = Path(reps[-1]).read_text(encoding="utf-8", errors="ignore")
        med = re.search(r"중앙값[^0-9]*([0-9.]+)\s*%", txt)
        p99 = re.search(r"P99[^0-9]*([0-9.]+)\s*%", txt)
        r1 = {"status": "산출", "source": reps[-1],
              "median_diff_pct": float(med.group(1)) if med else None,
              "p99_diff_pct": float(p99.group(1)) if p99 else None}
    else:
        r1 = {"status": "마지막 확정 실측(2026-08-13 세션 종가 검증 통과)", "source": "V-001",
              "median_diff_pct": 0.1003, "p99_diff_pct": 1.34, "overlap_days": 3957,
              "over_2pct_share": 0.0038}
    out["R1_input_accuracy"] = r1

    # R2 시점 정확도 — 계약의 개정 미보존 지표 수 + 최근 스탬프 게이트
    r2: dict[str, Any] = {"status": "미확인"}
    if CONTRACT_YAML.is_file():
        try:
            import yaml
            c = yaml.safe_load(CONTRACT_YAML.read_text(encoding="utf-8")) or {}
            feats = c.get("features", {}) or {}
            cont = sum(1 for m in feats.values() if isinstance(m, dict) and m.get("revision_contaminated"))
            r2 = {"status": "산출", "n_features": len(feats), "revision_contaminated": cont,
                  "asof_rule": c.get("asof_rule"), "window": c.get("window")}
        except Exception as e:                              # noqa: BLE001
            r2 = {"status": f"계약 파싱 실패({type(e).__name__})"}
    out["R2_asof_accuracy"] = r2

    # R3·R4 서명 스탬프
    st = _read_csv(STAMPS_CSV)
    r3: dict[str, Any] = {"status": "미확인"}
    r4: dict[str, Any] = {"status": "미확인"}
    if not st.empty:
        st["date"] = pd.to_datetime(st["date"], errors="coerce")
        st = st.sort_values("date")
        last = st.iloc[-1]
        n_alert_md = None
        if ALERT_LATEST.is_file():
            body = ALERT_LATEST.read_text(encoding="utf-8", errors="ignore")
            tbl = body.split("## 🚨")[1].split("##")[0] if "## 🚨" in body else ""
            n_alert_md = sum(1 for ln in tbl.splitlines() if ln.startswith("| ") and "변수" not in ln and "---" not in ln)
        r3 = {"status": "산출", "stamp_date": str(last["date"].date()), "stamp_alerts": int(last["alerts"]),
              "report_alerts": n_alert_md,
              "consistent": (n_alert_md is None) or (int(last["alerts"]) == n_alert_md)}
        verd = st["verdict"].astype(str)
        gate_ok = st["gate"].astype(str).isin(["PASS", "WARNING"])
        streak = 0
        for ok in reversed(gate_ok.tolist()):
            if ok:
                streak += 1
            else:
                break
        r4 = {"status": "산출", "rows": int(len(st)), "from": str(st["date"].min().date()),
              "to": str(st["date"].max().date()),
              "verdicts": {k: int(v) for k, v in verd.str.split(" ").str[0].value_counts().items()},
              "gate_pass_streak_runs": streak,
              "contaminated_note": "8/26~9/1 6행은 경보 열 오염(A-245) — 사실 기록 유지"}
    out["R3_alert_consistency"] = r3
    out["R4_publication_integrity"] = r4

    # R5 수집 채널 실적
    sg = _read_csv(SIGNALS_CSV)
    r5: dict[str, Any] = {"status": "미확인"}
    if not sg.empty:
        sg["date"] = pd.to_datetime(sg["date"], errors="coerce")
        days = sg["date"].dt.normalize().dropna()
        bdays = pd.bdate_range(days.min(), days.max())
        arrived = days.drop_duplicates()
        arrived_b = arrived[arrived.dt.weekday < 5]
        ch = sg["note"].astype(str).str.extract(r"^\[채널: ([^\]·]+?)\s*(?:·|\])")[0]   # A-271: kw 접미 제외
        r5 = {"status": "산출", "rows": int(len(sg)), "indicators": int(sg["indicator"].nunique()),
              "from": str(days.min().date()), "to": str(days.max().date()),
              "bday_arrival_rate": round(float(len(arrived_b) / max(len(bdays), 1)), 3),
              "by_category": {k: int(v) for k, v in sg["category"].value_counts().items()},
              "media_channel_winners": {k: int(v) for k, v in ch.dropna().value_counts().items()},
              "rss_codes": int(sg["indicator"].astype(str).str.startswith("RSS_").sum())}
    out["R5_collection_channels"] = r5

    # R6 데이터 유형별 규칙 재검증표
    rows = []
    te_last = None
    if TE_PARQUET.is_file():
        te = pd.read_parquet(TE_PARQUET, columns=["indicator_code", "price_date"])
        te_last = pd.to_datetime(te.loc[te["indicator_code"] == "TE_BDI", "price_date"]).max()
    brief_date = None
    if BRIEF_LATEST.is_file():
        m = re.search(r"데이터 기준일 (\d{4}-\d{2}-\d{2})", BRIEF_LATEST.read_text(encoding="utf-8", errors="ignore"))
        brief_date = m.group(1) if m else None
    rows.append({"유형": "일별 시세(시카고 정산가·환율)", "과거 규칙": "마감(14:20 ET) 후 당일 확정 · 마감 이후 확정 지표는 +1일",
                 "실시간 관측": f"브리프 데이터 기준일 {brief_date or '미확인'} (발행일 전 거래일)",
                 "판정": "정합" if brief_date else "미확인"})
    rows.append({"유형": "해상운임(BDI)", "과거 규칙": "발틱거래소 13:00 런던 발표 → 당일 즉시",
                 "실시간 관측": f"스냅샷 사본 최신 {te_last.date() if te_last is not None else '미확인'} · 3단 폴백(API→stooq→사본)",
                 "판정": ("정합(≤3영업일)" if te_last is not None and np.busday_count(te_last.date(), today) <= 3 else "지연 확인 필요")})
    rows.append({"유형": "월간 수급 보고서(WASDE·PSD)", "과거 규칙": "발표일 이후 가용(same_month) · 전망 행은 수집 시점 캡",
                 "실시간 관측": "품질 테스트 available_at ≤ 오늘 통과(#99)", "판정": "정합"})
    rows.append({"유형": "산지 기후(ERA5-Land·예보)", "과거 규칙": "재분석 지연 6일 · 예보는 발행일 키(별도 파일)",
                 "실시간 관측": "예보 분리 반영 후 첫 정기 실행에서 판정", "판정": "판정 대기"})
    rows.append({"유형": "비정형(정책·지정학·매체)", "과거 규칙": "수집 시점 가용 · 마감 후 수집분은 +1일",
                 "실시간 관측": (f"아카이브 영업일 도달률 {r5.get('bday_arrival_rate')}" if r5.get("status") == "산출" else "미확인"),
                 "판정": "정합" if (r5.get("bday_arrival_rate") or 0) >= 0.8 else "부분"})
    out["R6_rule_reverification"] = rows
    return out


# ─────────────────────────────────────────────────────────────────────────────
# 경보 원장 (P0-1)
# ─────────────────────────────────────────────────────────────────────────────
LEDGER_COLS = ["date", "variable", "value", "threshold", "status", "rule_version", "run_id",
               "appended_at", "abs_ret5", "abs_ret20", "abs_ret60"]


def append_alert_ledger(alerts: list[dict], run_ts: str, run_id: str,
                        path: Path = ALERT_LEDGER) -> int:
    """G1 경보(🚨) 발행분을 원장에 append — (date, variable) 중복은 기존 유지(A-181 규약)."""
    breach = [a for a in alerts if "🚨" in str(a.get("상태", ""))]
    if not breach:
        return 0
    day = str(run_ts)[:10]
    new = pd.DataFrame([{
        "date": day, "variable": str(a.get("변수")), "value": str(a.get("현재값")),
        "threshold": str(a.get("임계값")), "status": str(a.get("상태")), "rule_version": RULE_VERSION,
        "run_id": str(run_id), "appended_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "abs_ret5": np.nan, "abs_ret20": np.nan, "abs_ret60": np.nan} for a in breach])
    old = _read_csv(path)
    merged = pd.concat([old, new], ignore_index=True) if not old.empty else new
    merged = merged.drop_duplicates(["date", "variable"], keep="first")
    path.parent.mkdir(parents=True, exist_ok=True)
    merged[LEDGER_COLS].to_csv(path, index=False)
    return int(len(merged) - len(old))


def mature_alert_ledger(close: pd.Series, path: Path = ALERT_LEDGER) -> int:
    """성숙(5/20/60거래일 경과)한 경보에 실측 |수익률|을 채운다 — look-ahead 차단(경과분만)."""
    led = _read_csv(path)
    if led.empty:
        return 0
    c = close.sort_index().astype(float)
    logc = np.log(c)
    filled = 0
    for i, row in led.iterrows():
        d = pd.Timestamp(row["date"])
        pos = c.index.searchsorted(d)
        if pos >= len(c):
            continue
        for h in HORIZONS:
            col = f"abs_ret{h}"
            if pd.notna(row.get(col)) or pos + h >= len(c):
                continue
            led.at[i, col] = round(abs(float(logc.iloc[pos + h] - logc.iloc[pos])), 4)
            filled += 1
    if filled:
        led[LEDGER_COLS].to_csv(path, index=False)
    return filled


def ledger_summary(path: Path = ALERT_LEDGER) -> dict[str, Any]:
    led = _read_csv(path)
    if led.empty:
        return {"status": "원장 없음", "rows": 0}
    matured = {str(h): int(led[f"abs_ret{h}"].notna().sum()) for h in HORIZONS}
    return {"status": "산출", "rows": int(len(led)), "from": str(led["date"].min()),
            "to": str(led["date"].max()), "matured": matured,
            "by_variable": {k: int(v) for k, v in led["variable"].value_counts().items()},
            "note": "성숙 경보 8회 미만은 사후 성적 보류(실발행 원장은 2026-09-14 개설)"}


# ─────────────────────────────────────────────────────────────────────────────
# 산출·보고
# ─────────────────────────────────────────────────────────────────────────────
def evaluate(mode: str = "full") -> dict[str, Any]:
    result: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "mode": mode, "window": [WINDOW_START, WINDOW_END], "caption": REQUIRED_CAPTION,
        "realtime": realtime_metrics(), "ledger": ledger_summary()}
    if mode == "alert":
        # A-271: 경량 모드는 직전 정규판(weekly/monthly/full)의 과거 H1~H5를 이월 — 문자열로 덮으면
        #   E1 승격 후 브리프 월별 항목이 다음 금요일까지 사라진다.
        result["historical"] = {"status": "경량 모드 — 주별·월별판에서 산출"}
        try:
            prev = json.loads(LATEST_JSON.read_text(encoding="utf-8")) if LATEST_JSON.is_file() else {}
            ph = prev.get("historical")
            if isinstance(ph, dict) and "H1_rank_stability" in ph:
                result["historical"] = ph
                result["historical_asof"] = prev.get("generated_at")
                result["basis"] = prev.get("basis", "직전 정규판 이월")
                result["source"] = prev.get("source", {})
        except Exception as e:                                  # noqa: BLE001
            result["historical_carry_error"] = f"{type(e).__name__}"
        return result
    inp = load_inputs()
    result["basis"] = inp.basis
    result["source"] = inp.source
    fwd = _forward_returns(inp.close)
    target20 = fwd["target_ret20"]
    hist: dict[str, Any] = {}
    feats = inp.features if inp.features is not None else pd.DataFrame(index=inp.close.index)
    hist["H1_rank_stability"] = rank_stability(feats, target20) if not feats.empty else {"status": "미산출(피처 없음)"}
    top = hist["H1_rank_stability"].get("pearson", {}).get("top_last_fold", []) if hist["H1_rank_stability"].get("status") == "산출" else []
    hist["H2_granger_persistence"] = granger_persistence(feats, target20, top) if top else {"status": "미산출"}
    hist["H3_alert_rule_retro"] = alert_rule_retro(inp.levels, inp.close)
    hist["H4_reference_range"] = reference_range_diagnosis(inp.close)
    hist["H5_analogue_discrimination"] = analogue_discrimination(inp.levels, inp.close, top or ["TE_BDI"])
    result["historical"] = hist
    try:
        result["ledger_matured_now"] = mature_alert_ledger(inp.close)
        result["ledger"] = ledger_summary()
    except Exception as e:                                  # noqa: BLE001
        result["ledger_matured_now"] = f"실패({type(e).__name__})"
    return result


def _label(code: str) -> str:
    try:
        from src.reporting.daily_brief import _label_ko
        return _label_ko(code)
    except Exception:                                       # noqa: BLE001
        return code


def render_markdown(res: dict[str, Any]) -> str:
    L: list[str] = []
    L.append(f"# G1 보고서 신뢰도 지표 — {res['generated_at'][:10]} ({res.get('mode')})")
    L.append("")
    L.append(f"> {REQUIRED_CAPTION}")
    L.append(f"> 입력 기반: **{res.get('basis', '경량 모드')}** · 분석창 {res['window'][0]}~{res['window'][1]}")
    L.append("")
    L.append("## 1단계 — 과거 데이터 검증 (H1~H5)")
    H = res.get("historical", {})
    if H.get("status"):
        L.append(f"- {H['status']}")
    else:
        h1 = H["H1_rank_stability"]
        if h1.get("status") == "산출":
            p = h1["pearson"]
            L.append(f"- **H1 변인 순위 안정성**: 인접 폴드 순위 상관 평균 **{p['mean_spearman']}** "
                     f"(폴드별 {p['adjacent_fold_spearman']}) · 상위 {TOP_N} 부호 일치율 {p['sign_agreement_top']} · "
                     f"표본 {h1['n_rows']:,}행·변수 {h1['n_features']}개")
            en = h1.get("elastic_net", {})
            if en.get("mean_spearman") is not None:
                L.append(f"  - 규제 회귀 기준: 순위 상관 평균 {en['mean_spearman']} · 부호 일치율 {en['sign_agreement_top']}")
            else:
                L.append(f"  - 규제 회귀 기준: {en.get('status', '미산출')}")
            L.append("  - 마지막 폴드 상위 변인: " + ", ".join(_label(v) for v in p["top_last_fold"][:6]))
        else:
            L.append(f"- **H1 변인 순위 안정성**: {h1.get('status')} — {h1.get('reason', '')}")
        h2 = H["H2_granger_persistence"]
        if h2.get("status") == "산출":
            L.append(f"- **H2 인과 검정 재현성**: 전체 창 유의 {len(h2['significant_full'])}/{h2['n_vars']}개 · "
                     f"부분 창 지속률 **{h2['persistence_rate']}** (본페로니 α={h2['alpha_bonferroni']})")
        else:
            L.append(f"- **H2 인과 검정 재현성**: {h2.get('status')}")
        h3 = H["H3_alert_rule_retro"]
        L.append(f"- **H3 경보 규칙 소급 성적** ({h3['label']} · {h3['rule_version']}): "
                 f"무조건부 |변화율| 중앙값 5/20/60일 = "
                 + " / ".join(f"{h3['unconditional_median_abs'][str(h)]*100:.2f}%" for h in HORIZONS))
        L.append("")
        L.append("| 규칙 | 발화일 비중 | 지평 | 에피소드 | 오경보 근사율 | 조건부 중앙 \\|변화율\\| / 무조건부 |")
        L.append("|---|---|---|---|---|---|")
        for name, r in h3["rules"].items():
            if r.get("status") != "산출":
                L.append(f"| {name} | — | — | — | {r.get('status')} | {r['definition']} |")
                continue
            for h in HORIZONS:
                hh = r["horizons"][str(h)]
                if hh.get("status") == "산출":
                    L.append(f"| {name} | {r['breach_share']*100:.1f}% | {h}일 | {hh['episodes']} | "
                             f"{hh['false_alarm_proxy']*100:.0f}% | ×{hh['ratio_vs_unconditional']} |")
                else:
                    L.append(f"| {name} | {r['breach_share']*100:.1f}% | {h}일 | {hh['episodes']} | {hh['status']} | — |")
        L.append("")
        h4 = H["H4_reference_range"]
        L.append(f"- **H4 참고 범위 폭 진단** ({h4['label']} · 명목 {int(h4['nominal_coverage']*100)}%):")
        L.append("")
        L.append("| 지평 | 표본 | 포함률 | 평균 폭 | 스트레스 구간 포함률 |")
        L.append("|---|---|---|---|---|")
        for h in HORIZONS:
            r = h4["horizons"][str(h)]
            sl = " · ".join(f"{k} {v['coverage']*100:.0f}%" for k, v in r["by_slice"].items())
            L.append(f"| {h}일 | {r['n']:,} | {r['coverage']*100:.1f}% | ±{r['mean_width_pct']/2:.1f}% | {sl} |")
        L.append("")
        h5 = H["H5_analogue_discrimination"]
        parts = [f"{_label(v)}: 조건부 폭 비율 {d['mean_conditional_iqr_ratio']}" for v, d in h5["vars"].items()
                 if d.get("status") == "산출"]
        L.append(f"- **H5 유사 시기 참조 분별력**(20일·십분위 조건부 IQR / 무조건부 {h5['unconditional_iqr']}): "
                 + ("; ".join(parts) if parts else "산출 보류(표본 부족)"))
    L.append("")
    L.append("## 2단계 — 실시간 수집 데이터 검증 (R1~R6)")
    R = res["realtime"]
    r1 = R["R1_input_accuracy"]
    L.append(f"- **R1 입력 정확도**: 정산가 교차검증 상대오차 중앙값 {r1.get('median_diff_pct')}% · P99 {r1.get('p99_diff_pct')}% ({r1['status']})")
    r2 = R["R2_asof_accuracy"]
    if r2.get("status") == "산출":
        L.append(f"- **R2 시점 정확도**: 계약 피처 {r2['n_features']}종 중 개정 이력 미보존 {r2['revision_contaminated']}종(투입 제외·면책 자동 삽입) · 규칙 `{r2['asof_rule']}`")
    else:
        L.append(f"- **R2 시점 정확도**: {r2.get('status')}")
    r3 = R["R3_alert_consistency"]
    if r3.get("status") == "산출":
        L.append(f"- **R3 경보 정합성**: 스탬프 {r3['stamp_date']} 경보 {r3['stamp_alerts']}건 ↔ 경보판 {r3['report_alerts']}건 → "
                 f"{'일치' if r3['consistent'] else '불일치'}")
    r4 = R["R4_publication_integrity"]
    if r4.get("status") == "산출":
        L.append(f"- **R4 발행 무결성**: 서명 스탬프 {r4['rows']}행({r4['from']}~{r4['to']}) · 판정 분포 {r4['verdicts']} · "
                 f"게이트 연속 통과 {r4['gate_pass_streak_runs']}회 · {r4['contaminated_note']}")
    r5 = R["R5_collection_channels"]
    if r5.get("status") == "산출":
        L.append(f"- **R5 수집 채널 실적**: 비정형 아카이브 {r5['rows']}행·{r5['indicators']}지표({r5['from']}~{r5['to']}) · "
                 f"영업일 도달률 {r5['bday_arrival_rate']*100:.0f}% · 매체 채널 승자 {r5['media_channel_winners']} · 매체 기사 행 {r5['rss_codes']}")
    L.append("- **R6 데이터 유형별 규칙 재검증**:")
    L.append("")
    L.append("| 데이터 유형 | 과거 데이터에서 확립한 규칙 | 실시간 관측 | 판정 |")
    L.append("|---|---|---|---|")
    for row in R["R6_rule_reverification"]:
        L.append(f"| {row['유형']} | {row['과거 규칙']} | {row['실시간 관측']} | {row['판정']} |")
    L.append("")
    led = res.get("ledger", {})
    L.append(f"- **경보 원장(실발행)**: {led.get('rows', 0)}행 · 성숙 {led.get('matured', {})} · {led.get('note', '')}")
    L.append("")
    L.append("## 판독")
    L.append("- 1단계 수치는 표본을 나눠 다시 세어도 같은 변인이 남는지, 규칙이 과거에 얼마나 헛돌았는지, 참고 범위가 실제 변동을 얼마나 담았는지를 재는 **과정 검증**임.")
    L.append("- 2단계 수치는 지금 들어오는 데이터가 1단계에서 확립한 규칙(발표 시점·주기·임계)대로 처리되는지를 재는 **적용 검증**임. 실발행 경보의 사후 성적은 원장 성숙 8회 이상부터 표기함.")
    md = "\n".join(L) + "\n"
    for bad in FORBIDDEN_PHRASES:
        assert bad not in md, f"[오류] 서술 계약 위반 표현: {bad}"
    return md


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="G1 보고서 신뢰도 지표 산출")
    ap.add_argument("--mode", default=os.environ.get("G1_PUBLISH_MODE", "full"),
                    choices=["alert", "weekly", "monthly", "full"])
    ap.add_argument("--report-dir", default=os.environ.get("G1_REPORT_DIR", "reports/market"))
    ap.add_argument("--json", default=str(LATEST_JSON))
    a = ap.parse_args(argv)
    res = evaluate(a.mode)
    Path(a.json).parent.mkdir(parents=True, exist_ok=True)
    Path(a.json).write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    md = render_markdown(res)
    out = Path(a.report_dir) / f"g1_reliability_{date.today().isoformat()}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"[완료] 신뢰도 지표 → {a.json} · {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
