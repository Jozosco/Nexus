"""지정학·에너지 충격 전후 대두유 가격 반응 — 1차 정량 프로토타입 (M1 사건 연구 + M2 국소투영).

목적: 과거 충격 사건 전후에 **관측된** CBOT 대두유(ZL) 가격 반응을 로컬 데이터만으로 요약한다.
산출은 과거 실측의 기술(記述)까지이며 향후 방향·가능성 주장이 아니다(A-191 서술 계약 —
금지어 검증을 보고서 생성 단계에 내장).

데이터 기반(진단 계열):
  - ZL 일봉 종가: data/raw/Databento/GLBX.MDP3/ZL_ohlcv-1d_*.csv (UTC 일봉 — 정산가 아님,
    D-035·A-156). 주말 세션 행 제거(A-131), 동일 일자 중복은 거래량 최대 행 채택(A-111).
  - TE 일별: data/raw/te_commodities_historical.parquet (롱포맷). Brent·BDI·난방유·팜유.

방법:
  M1 사건 연구 — 사전 고정 사건 목록(전부 과거)마다 사건 직전 종가(t0−1) 기준 t0+h(h=0·1·5·20·60)
    누적 로그수익률, 60거래일 내 최대 상승폭·최대 하락폭, 초기 반응(첫 5거래일 내 절대값 최대
    이동) 이후 사건 전 수준 복귀까지의 거래일 수(상한 120 → '미복귀'). 전 거래일 무조건부 분포
    대비 백분위 순위를 병기.
  M2 국소투영(Jordà) — 충격 프록시(Brent·BDI·난방유 일간 로그변화, 표본 σ로 표준화)에 대한
    ZL 누적 로그수익률 log(P[t+h]/P[t−1])의 OLS 반응계수. 통제: ZL 수익률·충격의 1~5차 시차.
    Newey–West HAC(maxlags=h) 표준오차, 90% 신뢰구간. 대형 충격(>+2σ / <−2σ) 지시변수
    사양으로 비대칭 병기. 표본 2010-06~2025-12(2026 미완결 제외 — M-008)와 2020~2025 별도.

실행:
  python scripts/shock_response_prototype.py            # 실데이터 → reports/market/*.md
  python scripts/shock_response_prototype.py --self-test # 합성 데이터 형상 검증
"""
from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

REPO_ROOT = Path(__file__).resolve().parents[1]
ZL_CSV = REPO_ROOT / "data/raw/Databento/GLBX.MDP3/ZL_ohlcv-1d_2010-06-06_2026-08-12.csv"
TE_PARQUET = REPO_ROOT / "data/raw/te_commodities_historical.parquet"
REPORT_DATE = "2026-09-25"
OUT_MD = REPO_ROOT / f"reports/market/shock_response_prototype_{REPORT_DATE}.md"

DATA_BASIS = "진단 계열 — Databento UTC 종가·TE 일별; 정산가 아님"
CAPTION = "본 수치는 과거 충격 전후에 관측된 반응의 요약이며 향후 방향·확률 주장이 아님."
# 보고서 본문(캡션 제외)에 나타나면 안 되는 어휘 — A-191 서술 계약
FORBIDDEN_TERMS: tuple[str, ...] = ("예측", "전망", "확률", "적중률")

# 충격 프록시 — TE indicator_code → 표시명. 부재 시 [경고] 후 건너뜀.
SHOCK_PROXIES: dict[str, str] = {
    "TE_BRENT_CRUDE_OIL": "Brent",
    "TE_BDI": "BDI",
    "TE_HEATING_OIL": "난방유(디젤 프록시)",
}
# M1에서 ZL과 함께 창 수익률을 병기하는 계열
COMPANION_SERIES: dict[str, str] = {
    "TE_BRENT_CRUDE_OIL": "Brent",
    "TE_BDI": "BDI",
    "TE_PALM_OIL": "팜유",
}

EVENT_WINDOWS: tuple[int, ...] = (0, 1, 5, 20, 60)     # 0 = 첫 거래일 당일
LP_HORIZONS: tuple[int, ...] = (1, 5, 20, 60)
MAX_DRAW_WINDOW = 60
RECOVERY_CAP = 120
INITIAL_REACTION_DAYS = 5                                # 복귀 판정의 '초기 반응' 탐색 창
N_CONTROL_LAGS = 5
LARGE_SHOCK_SIGMA = 2.0
CI_ALPHA = 0.10                                          # 90% 신뢰구간
FFILL_LIMIT = 5                                          # TE → ZL 달력 정렬 시 허용 이월일
SAMPLE_START = pd.Timestamp("2010-06-01")
SAMPLE_END = pd.Timestamp("2025-12-31")                  # 2026 미완결 제외(M-008)
STRESS_START = pd.Timestamp("2020-01-01")
SELF_TEST_DAYS = 1200
SELF_TEST_SEED = 20260925


@dataclass(frozen=True)
class ShockEvent:
    event_date: str     # 사건 발생일(달력일). 첫 거래일은 데이터에서 탐색.
    label: str
    category: str


# 사전 고정 사건 목록 — 전부 과거 사실. 순서 = 발생일순.
EVENTS: tuple[ShockEvent, ...] = (
    ShockEvent("2010-08-05", "러시아 곡물 수출 금지 발표", "농산물 정책"),
    ShockEvent("2016-05-03", "포트 맥머리 산불(캐나다 오일샌드)", "에너지 공급"),
    ShockEvent("2017-08-25", "허리케인 하비 상륙(걸프 정제 마비)", "에너지 공급"),
    ShockEvent("2019-09-14", "아브카이크 사우디 정유시설 피격", "지정학·에너지"),
    ShockEvent("2022-02-24", "러시아의 우크라이나 침공", "지정학"),
    ShockEvent("2023-02-05", "EU 러시아산 석유제품 금수 발효", "에너지 정책"),
    ShockEvent("2023-09-21", "러시아 디젤 수출 금지", "에너지 정책"),
    ShockEvent("2023-11-19", "후티 갤럭시 리더호 나포(홍해)", "지정학·물류"),
    ShockEvent("2024-01-12", "미·영 후티 공습", "지정학·물류"),
    ShockEvent("2025-03-20", "중국 캐나다산 카놀라유 100% 관세", "농산물 정책"),
    ShockEvent("2025-08-12", "중국 캐나다산 카놀라씨 반덤핑 예치금", "농산물 정책"),
)


# ---------------------------------------------------------------------------------------------
# 로더
# ---------------------------------------------------------------------------------------------
def load_zl_close(path: Path = ZL_CSV) -> pd.Series:
    """ZL 일봉 종가 로더 — 주말 행 제거(A-131), 동일 일자 중복은 거래량 최대 행(A-111)."""
    if not path.exists():
        raise FileNotFoundError(f"[오류] ZL 일봉 CSV 없음: {path}")
    df = pd.read_csv(path, usecols=["price_date", "close", "volume"])
    df["price_date"] = pd.to_datetime(df["price_date"], errors="coerce")
    n_raw = len(df)
    df = df.dropna(subset=["price_date", "close"])
    df = df[df["price_date"].dt.weekday < 5]
    df = (df.sort_values(["price_date", "volume"], ascending=[True, False])
            .drop_duplicates("price_date", keep="first"))
    close = df.set_index("price_date")["close"].astype(float).sort_index()
    if close.empty:
        raise ValueError(f"[오류] ZL 종가 0건: {path}")
    if (close <= 0).any():
        raise ValueError("[오류] ZL 종가에 0 이하 값 존재 — 로그수익률 산출 불가")
    print(f"[정보] ZL 종가 {len(close):,}일 로드(원본 {n_raw:,}행) "
          f"{close.index.min().date()}~{close.index.max().date()} USc/lb")
    return close


def load_te_series(codes: tuple[str, ...], path: Path = TE_PARQUET) -> pd.DataFrame:
    """TE 롱포맷 → 요청 코드만 와이드(일자 × 코드). 부재 코드는 [경고] 후 열 생략."""
    if not path.exists():
        raise FileNotFoundError(
            f"[오류] TE parquet 없음: {path} — 먼저 python scripts/ingest_te_xlsx.py 실행")
    df = pd.read_parquet(path, columns=["price_date", "indicator_code", "value"])
    available = set(df["indicator_code"].unique())
    present = [c for c in codes if c in available]
    for c in codes:
        if c not in available:
            print(f"[경고] TE 지표 부재 — 건너뜀: {c}")
    sub = df[df["indicator_code"].isin(present)].copy()
    sub["price_date"] = pd.to_datetime(sub["price_date"])
    sub = sub.dropna(subset=["value"])
    sub = sub[sub["value"] > 0]
    wide = (sub.groupby(["price_date", "indicator_code"])["value"].last()
              .unstack("indicator_code").sort_index())
    for c in present:
        s = wide[c].dropna()
        print(f"[정보] TE {c}: {len(s):,}일 {s.index.min().date()}~{s.index.max().date()}")
    return wide


def build_panel(zl: pd.Series, te: pd.DataFrame) -> pd.DataFrame:
    """ZL 거래일 달력에 TE 계열을 정렬(최대 FFILL_LIMIT일 이월). 공통 구간만 남김."""
    start = max(zl.index.min(), te.index.min()) if not te.empty else zl.index.min()
    end = min(zl.index.max(), te.index.max()) if not te.empty else zl.index.max()
    idx = zl.loc[start:end].index
    panel = pd.DataFrame({"ZL": zl.reindex(idx)})
    if not te.empty:
        aligned = te.reindex(idx.union(te.index)).ffill(limit=FFILL_LIMIT).reindex(idx)
        for c in te.columns:
            panel[c] = aligned[c]
    panel = panel.dropna(subset=["ZL"])
    print(f"[정보] 정렬 패널 {len(panel):,}거래일 {panel.index.min().date()}~"
          f"{panel.index.max().date()} · 열 {list(panel.columns)}")
    return panel


# ---------------------------------------------------------------------------------------------
# M1 사건 연구
# ---------------------------------------------------------------------------------------------
def _window_log_returns(price: pd.Series, h: int) -> pd.Series:
    """전 거래일 t에 대한 log(P[t+h]/P[t−1]) — 사건 창과 동일 길이(h+1일)의 무조건부 분포."""
    logp = np.log(price.to_numpy(dtype=float))
    n = len(logp)
    out = np.full(n, np.nan)
    if n > h + 1:
        out[1:n - h] = logp[1 + h:n] - logp[0:n - h - 1]
    return pd.Series(out, index=price.index)


def percentile_rank(dist: np.ndarray, x: float) -> float:
    """x 이하 관측치 비율(%) — 무조건부 분포 내 순위."""
    d = dist[~np.isnan(dist)]
    if d.size == 0 or np.isnan(x):
        return float("nan")
    return float(np.mean(d <= x) * 100.0)


def _recovery_days(path: np.ndarray, cap: int,
                   initial_window: int = INITIAL_REACTION_DAYS) -> int | None:
    """path[k] = log(P[t0+k]/P[t0−1]). 초기 반응(첫 initial_window+1일 중 절대값 최대 이동)
    이후 그 방향의 반대로 사건 전 수준(0)을 재교차하는 첫 k. 없으면 None(미복귀)."""
    if path.size == 0 or np.all(np.isnan(path)):
        return None
    head = path[:min(initial_window, path.size - 1) + 1]
    k_star = int(np.nanargmax(np.abs(head)))
    sign = np.sign(head[k_star])
    if sign == 0:
        return k_star
    limit = min(cap, path.size - 1)
    for k in range(k_star + 1, limit + 1):
        v = path[k]
        if np.isnan(v):
            continue
        if (sign > 0 and v <= 0) or (sign < 0 and v >= 0):
            return k
    return None


def event_study(panel: pd.DataFrame, events: tuple[ShockEvent, ...] = EVENTS,
                companions: dict[str, str] | None = None) -> pd.DataFrame:
    """사건별 ZL 창 수익률·백분위·최대 상승/하락·복귀일 + 동반 계열 창 수익률."""
    companions = COMPANION_SERIES if companions is None else companions
    price = panel["ZL"]
    logp = np.log(price.to_numpy(dtype=float))
    idx = price.index
    uncond = {h: _window_log_returns(price, h).to_numpy() for h in EVENT_WINDOWS}
    rows: list[dict[str, object]] = []
    for ev in events:
        ev_ts = pd.Timestamp(ev.event_date)
        pos = int(idx.searchsorted(ev_ts, side="left"))
        if pos <= 0 or pos >= len(idx):
            print(f"[경고] 데이터 범위 밖 사건 건너뜀: {ev.event_date} {ev.label}")
            continue
        base = logp[pos - 1]
        max_k = min(RECOVERY_CAP, len(idx) - 1 - pos)
        path = logp[pos:pos + max_k + 1] - base
        row: dict[str, object] = {
            "event_date": ev.event_date, "t0": idx[pos].date().isoformat(),
            "label": ev.label, "category": ev.category,
            "pre_close": float(np.exp(base)),
        }
        for h in EVENT_WINDOWS:
            if pos + h < len(idx):
                r = float(logp[pos + h] - base)
                row[f"ret_{h}"] = r
                row[f"pct_{h}"] = percentile_rank(uncond[h], r)
            else:
                row[f"ret_{h}"] = float("nan")
                row[f"pct_{h}"] = float("nan")
                print(f"[경고] {ev.label}: t0+{h} 거래일이 데이터 끝을 넘음 — 결측 처리")
        draw = path[:min(MAX_DRAW_WINDOW, len(path) - 1) + 1]
        row["max_drawup_60"] = float(np.nanmax(draw)) if draw.size else float("nan")
        row["max_drawdown_60"] = float(np.nanmin(draw)) if draw.size else float("nan")
        rec = _recovery_days(path, RECOVERY_CAP)
        row["recovery_days"] = rec
        row["recovery_capped"] = max_k < RECOVERY_CAP and rec is None
        for code, name in companions.items():
            if code not in panel.columns:
                continue
            s = np.log(panel[code].to_numpy(dtype=float))
            b = s[pos - 1]
            for h in (1, 5, 20, 60):
                v = s[pos + h] - b if pos + h < len(idx) else float("nan")
                row[f"{name}_ret_{h}"] = float(v)
        rows.append(row)
    out = pd.DataFrame(rows)
    print(f"[정보] M1 사건 연구 {len(out)}건 산출(목록 {len(events)}건)")
    return out


# ---------------------------------------------------------------------------------------------
# M2 국소투영
# ---------------------------------------------------------------------------------------------
def _lp_frame(panel: pd.DataFrame, code: str, h: int, sigma: float) -> pd.DataFrame:
    """지평 h 회귀용 프레임: y=log(P[t+h]/P[t−1]) · shock_t(표준화) · 시차 통제."""
    logp = np.log(panel["ZL"])
    r = logp.diff()
    shock_raw = np.log(panel[code]).diff()
    shock = shock_raw / sigma
    y = logp.shift(-h) - logp.shift(1)
    df = pd.DataFrame({"y": y, "shock": shock})
    df["d_pos"] = (shock > LARGE_SHOCK_SIGMA).astype(float)
    df["d_neg"] = (shock < -LARGE_SHOCK_SIGMA).astype(float)
    for k in range(1, N_CONTROL_LAGS + 1):
        df[f"r_l{k}"] = r.shift(k)
        df[f"s_l{k}"] = shock.shift(k)
    df["t_end"] = pd.Series(panel.index, index=panel.index).shift(-h)
    return df


def _fit_hac(df: pd.DataFrame, main: list[str], h: int) -> tuple[dict[str, tuple[float, float,
                                                                                  float]], int]:
    controls = [c for c in df.columns if c.startswith(("r_l", "s_l"))]
    cols = main + controls
    d = df.dropna(subset=["y"] + cols)
    if len(d) <= len(cols) + 5:
        raise ValueError(f"[오류] 국소투영 표본 부족: n={len(d)} (h={h}, {main})")
    X = sm.add_constant(d[cols].to_numpy(dtype=float), has_constant="add")
    res = sm.OLS(d["y"].to_numpy(dtype=float), X).fit(
        cov_type="HAC", cov_kwds={"maxlags": max(h, 1)})
    ci = res.conf_int(alpha=CI_ALPHA)
    out: dict[str, tuple[float, float, float]] = {}
    for i, name in enumerate(main, start=1):
        out[name] = (float(res.params[i]), float(ci[i, 0]), float(ci[i, 1]))
    return out, int(res.nobs)


def local_projections(panel: pd.DataFrame, proxies: dict[str, str] | None = None,
                      samples: dict[str, tuple[pd.Timestamp, pd.Timestamp]] | None = None
                      ) -> pd.DataFrame:
    """충격 프록시 × 지평 × 표본별 1σ 반응계수(선형) + 대형 충격(±2σ) 지시변수 반응."""
    proxies = SHOCK_PROXIES if proxies is None else proxies
    if samples is None:
        samples = {"2010~2025": (SAMPLE_START, SAMPLE_END),
                   "2020~2025": (STRESS_START, SAMPLE_END)}
    rows: list[dict[str, object]] = []
    for code, name in proxies.items():
        if code not in panel.columns:
            print(f"[경고] 충격 프록시 부재 — M2 건너뜀: {code}")
            continue
        full = panel.loc[SAMPLE_START:SAMPLE_END, code]
        sigma = float(np.log(full).diff().std(ddof=1))
        if not np.isfinite(sigma) or sigma <= 0:
            print(f"[경고] {code}: 표준편차 산출 불가 — M2 건너뜀")
            continue
        n_pos = int((np.log(full).diff() / sigma > LARGE_SHOCK_SIGMA).sum())
        n_neg = int((np.log(full).diff() / sigma < -LARGE_SHOCK_SIGMA).sum())
        print(f"[정보] {name}: 일간 로그변화 σ={sigma:.4f} · "
              f">+2σ {n_pos}일 · <−2σ {n_neg}일 (2010~2025)")
        for h in LP_HORIZONS:
            frame = _lp_frame(panel, code, h, sigma)
            for sname, (s0, s1) in samples.items():
                sub = frame.loc[(frame.index >= s0) & (frame.index <= s1)
                                & (frame["t_end"] <= s1)]
                lin, n_lin = _fit_hac(sub, ["shock"], h)
                big, n_big = _fit_hac(sub, ["d_pos", "d_neg"], h)
                rows.append({
                    "proxy_code": code, "proxy": name, "sample": sname, "h": h,
                    "sigma_daily": sigma,
                    "beta": lin["shock"][0], "ci_lo": lin["shock"][1],
                    "ci_hi": lin["shock"][2], "n": n_lin,
                    "big_pos": big["d_pos"][0], "big_pos_lo": big["d_pos"][1],
                    "big_pos_hi": big["d_pos"][2],
                    "big_neg": big["d_neg"][0], "big_neg_lo": big["d_neg"][1],
                    "big_neg_hi": big["d_neg"][2],
                    "n_pos": int(sub.dropna(subset=["y"])["d_pos"].sum()),
                    "n_neg": int(sub.dropna(subset=["y"])["d_neg"].sum()),
                    "n_big": n_big,
                })
    out = pd.DataFrame(rows)
    print(f"[정보] M2 국소투영 {len(out)}행 산출")
    return out


# ---------------------------------------------------------------------------------------------
# 보고서
# ---------------------------------------------------------------------------------------------
def _pct(x: float, digits: int = 2) -> str:
    return "—" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x * 100:+.{digits}f}%"


def _rank(x: float) -> str:
    return "—" if x is None or np.isnan(x) else f"{x:.0f}"


def _rec(row: pd.Series) -> str:
    v = row["recovery_days"]
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "미복귀(관측 한계)" if bool(row.get("recovery_capped", False)) else "미복귀"
    return f"{int(v)}일"


def _m1_table(ev: pd.DataFrame) -> list[str]:
    lines = ["| 사건(첫 거래일) | 분류 | 당일 | +1일 | +5일 | +20일 | +60일 | "
             "백분위(1·5·20·60) | 60일 최대 상승 | 60일 최대 하락 | 사건 전 수준 복귀 |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in ev.iterrows():
        pct = "·".join(_rank(r[f"pct_{h}"]) for h in (1, 5, 20, 60))
        lines.append(
            f"| {r['label']} ({r['t0']}) | {r['category']} | {_pct(r['ret_0'])} | "
            f"{_pct(r['ret_1'])} | {_pct(r['ret_5'])} | {_pct(r['ret_20'])} | "
            f"{_pct(r['ret_60'])} | {pct} | {_pct(r['max_drawup_60'])} | "
            f"{_pct(r['max_drawdown_60'])} | {_rec(r)} |")
    return lines


def _m1_companion_table(ev: pd.DataFrame, panel_cols: list[str]) -> list[str]:
    names = [n for c, n in COMPANION_SERIES.items() if c in panel_cols]
    if not names:
        return ["(동반 계열 없음 — TE 지표 부재)"]
    head = "| 사건(첫 거래일) | " + " | ".join(f"{n} +1/+5/+20/+60" for n in names) + " |"
    lines = [head, "|---|" + "---|" * len(names)]
    for _, r in ev.iterrows():
        cells = []
        for n in names:
            cells.append(" / ".join(_pct(r.get(f"{n}_ret_{h}", float("nan")), 1)
                                    for h in (1, 5, 20, 60)))
        lines.append(f"| {r['label']} ({r['t0']}) | " + " | ".join(cells) + " |")
    return lines


def _m2_table(lp: pd.DataFrame) -> list[str]:
    if lp.empty:
        return ["(M2 산출 없음 — 충격 프록시 전부 부재)"]
    lines = ["| 충격 프록시 | 표본 | h | 1σ 반응계수 | 90% CI | n | "
             "+2σ 초과일 반응 (CI) [일수] | −2σ 미만일 반응 (CI) [일수] |",
             "|---|---|---|---|---|---|---|---|"]
    for _, r in lp.iterrows():
        lines.append(
            f"| {r['proxy']} | {r['sample']} | {int(r['h'])} | {_pct(r['beta'])} | "
            f"[{_pct(r['ci_lo'])}, {_pct(r['ci_hi'])}] | {int(r['n']):,} | "
            f"{_pct(r['big_pos'])} ([{_pct(r['big_pos_lo'])}, {_pct(r['big_pos_hi'])}]) "
            f"[{int(r['n_pos'])}] | "
            f"{_pct(r['big_neg'])} ([{_pct(r['big_neg_lo'])}, {_pct(r['big_neg_hi'])}]) "
            f"[{int(r['n_neg'])}] |")
    return lines


def _reading_m1(ev: pd.DataFrame) -> list[str]:
    """M1 판독 — 관측된 크기·시점·복귀 빈도만 기술."""
    if ev.empty:
        return ["- 사건 연구 산출 없음."]
    out: list[str] = []
    n = len(ev)
    up20 = int((ev["ret_20"] > 0).sum())
    up60 = int((ev["ret_60"] > 0).sum())
    ext20 = ev[(ev["pct_20"] >= 90) | (ev["pct_20"] <= 10)]
    out.append(f"- 사건 {n}건 중 첫 거래일 이후 +20거래일 누적이 양(+)인 사건 {up20}건, "
               f"+60거래일 양(+) {up60}건. 방향은 사건마다 갈렸음.")
    if not ext20.empty:
        items = "; ".join(f"{r['label']}({_pct(r['ret_20'])}, 백분위 {_rank(r['pct_20'])})"
                          for _, r in ext20.iterrows())
        out.append(f"- +20거래일 누적이 무조건부 분포의 상·하위 10% 밖에 든 사건 "
                   f"{len(ext20)}건: {items}.")
    else:
        out.append("- +20거래일 누적이 무조건부 분포의 상·하위 10% 밖에 든 사건은 없었음.")
    big = ev.loc[ev["ret_20"].abs().idxmax()]
    out.append(f"- +20거래일 절대 크기 최대: {big['label']} {_pct(big['ret_20'])} "
               f"(60일 내 최대 상승 {_pct(big['max_drawup_60'])} · "
               f"최대 하락 {_pct(big['max_drawdown_60'])}).")
    day0 = ev["ret_0"].abs()
    out.append(f"- 첫 거래일 당일 절대 변화의 중앙값 {day0.median() * 100:.2f}%, "
               f"최대 {day0.max() * 100:.2f}%({ev.loc[day0.idxmax(), 'label']}).")
    recs = ev["recovery_days"].dropna()
    n_rec = int(len(recs))
    n_norec = n - n_rec
    if n_rec:
        within20 = int((recs <= 20).sum())
        out.append(f"- 사건 전 수준 복귀: {RECOVERY_CAP}거래일 내 복귀 {n_rec}건"
                   f"(중앙값 {int(recs.median())}일 · 20일 이내 {within20}건), "
                   f"미복귀 {n_norec}건.")
    else:
        out.append(f"- 사건 전 수준 복귀: {RECOVERY_CAP}거래일 내 복귀 0건.")
    return out


def _reading_m2(lp: pd.DataFrame) -> list[str]:
    if lp.empty:
        return ["- 국소투영 산출 없음(충격 프록시 부재)."]
    out: list[str] = []
    for proxy, g in lp.groupby("proxy", sort=False):
        f = g[g["sample"] == "2010~2025"].set_index("h")
        s = g[g["sample"] == "2020~2025"].set_index("h")
        parts = []
        for h in LP_HORIZONS:
            if h in f.index:
                r = f.loc[h]
                excl = "0 제외" if (r["ci_lo"] > 0 or r["ci_hi"] < 0) else "0 포함"
                parts.append(f"h={h} {_pct(r['beta'])}(CI {excl})")
        out.append(f"- {proxy} 1σ 반응(2010~2025): " + ", ".join(parts) + ".")
        if not s.empty:
            parts_s = [f"h={h} {_pct(s.loc[h, 'beta'])}" for h in LP_HORIZONS if h in s.index]
            out.append(f"  - 2020~2025 부분표본: " + ", ".join(parts_s) + ".")
        if 20 in f.index:
            r = f.loc[20]
            out.append(f"  - 대형 충격 h=20: +2σ 초과일 {_pct(r['big_pos'])}"
                       f"({int(r['n_pos'])}일) vs −2σ 미만일 {_pct(r['big_neg'])}"
                       f"({int(r['n_neg'])}일) — 부호·크기의 차이가 관측된 비대칭의 전부임.")
    excl_n = int(((lp["ci_lo"] > 0) | (lp["ci_hi"] < 0)).sum())
    out.append(f"- 전체 {len(lp)}개 선형 추정 중 90% CI가 0을 제외한 것은 {excl_n}개.")
    return out


def render_report(ev: pd.DataFrame, lp: pd.DataFrame, panel: pd.DataFrame,
                  missing: list[str]) -> str:
    p0, p1 = panel.index.min().date(), panel.index.max().date()
    lines: list[str] = [
        "# 지정학·에너지 충격 전후 대두유 가격 반응 — 1차 정량 프로토타입",
        "",
        f"> 생성 일자: {REPORT_DATE} · 데이터 기반: **{DATA_BASIS}** · "
        f"패널 {p0}~{p1} ({len(panel):,}거래일)",
        f"> {CAPTION}",
        "",
        "## 데이터·정의",
        "",
        "- ZL 종가: Databento GLBX.MDP3 `ZL.c.0` UTC 일봉(USc/lb) — 진단 계열(정산가 아님). "
        "주말 세션 행 제거, 동일 일자 중복은 거래량 최대 행.",
        "- TE 일별: Brent(USD/bbl)·BDI(pt)·난방유(USD/gal)·팜유(MYR/MT). ZL 거래일 달력에 "
        f"정렬(최대 {FFILL_LIMIT}일 이월).",
        "- 수익률은 전부 로그수익률. 사건 창은 **사건 직전 종가(t0−1)** 기준 t0+h 누적. "
        "당일 = 첫 거래일 t0의 반응.",
        "- 백분위 = 동일 길이 창의 전 거래일 무조건부 분포에서 해당 사건 수익률 이하 비율(%).",
        f"- 복귀일 = 초기 반응(첫 {INITIAL_REACTION_DAYS}거래일 내 절대값 최대 누적 이동) 이후 "
        f"그 방향의 반대로 사건 전 수준을 재교차하는 첫 거래일(상한 {RECOVERY_CAP}일, "
        "초과 시 '미복귀').",
    ]
    if missing:
        lines.append(f"- [경고] 부재 TE 지표: {', '.join(missing)} — 해당 프록시 생략.")
    lines += ["", "## M1 사건 연구 — ZL 반응", ""] + _m1_table(ev)
    lines += ["", "### 동반 계열 창 수익률(사건 직전 종가 기준 +1/+5/+20/+60거래일)", ""]
    lines += _m1_companion_table(ev, list(panel.columns))
    lines += ["", "## M2 국소투영(Jordà) — 충격 프록시 1σ에 대한 ZL 누적 반응", "",
              "- 종속변수 log(P[t+h]/P[t−1]) — 충격일 당일 반응 포함. 통제: ZL 수익률·충격의 "
              f"1~{N_CONTROL_LAGS}차 시차. Newey–West HAC(maxlags=h), 90% CI.",
              "- 충격 σ는 2010~2025 표본의 일간 로그변화 표준편차(부분표본에도 동일 σ 적용). "
              "표본은 t와 t+h가 모두 표본 종료일 이내인 관측만.",
              "- 대형 충격 열은 +2σ 초과일·−2σ 미만일 지시변수를 같은 통제 하에 동시 투입한 "
              "별도 사양의 계수.", ""]
    lines += _m2_table(lp)
    lines += ["", "## 판독 — 관측된 사실만", "", "### M1"] + _reading_m1(ev)
    lines += ["", "### M2"] + _reading_m2(lp)
    lines += ["", "### 한계", "",
              "- 사건 연구는 사건당 1개 표본이며 동시기 다른 요인(작황·정책·거시)을 분리하지 "
              "못함 — 단일 사건 추론.",
              "- ZL은 UTC 일봉 진단 계열이라 정산가 기준 계열(CBOT_BO_CLOSE)과 일자·크기가 "
              "다를 수 있음(A-156 교차검증 중앙값 약 0.10%).",
              "- 국소투영 계수는 상관 기반 축약이며 인과 식별 장치(외생 도구·서사 식별)가 없음. "
              "충격 프록시 자체가 ZL과 공통 요인에 동시 반응할 수 있음.",
              "- 표본 2010~2025 단일 구간의 요약이며 레짐·원산지별 분리는 미적용. 2026년 "
              "구간은 미완결로 제외(M-008).",
              "- 본 문서는 향후 방향·크기에 관한 어떠한 주장도 담지 않음.",
              "", f"_{CAPTION}_", ""]
    md = "\n".join(lines)
    body = md.replace(CAPTION, "")
    hits = [t for t in FORBIDDEN_TERMS if t in body]
    if hits:
        raise ValueError(f"[오류] 보고서 본문에 금지 어휘 포함: {hits}")
    return md


# ---------------------------------------------------------------------------------------------
# 실행
# ---------------------------------------------------------------------------------------------
def run(out_path: Path = OUT_MD) -> Path:
    t_start = time.time()
    zl = load_zl_close()
    codes = tuple(dict.fromkeys(list(SHOCK_PROXIES) + list(COMPANION_SERIES)))
    te = load_te_series(codes)
    missing = [c for c in codes if c not in te.columns]
    panel = build_panel(zl, te)
    ev = event_study(panel)
    lp = local_projections(panel)
    md = render_report(ev, lp, panel, missing)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")
    print(f"[정보] 소요 {time.time() - t_start:.1f}s")
    return out_path


def _synthetic_panel(days: int = SELF_TEST_DAYS, seed: int = SELF_TEST_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2018-01-02", periods=days)
    shock = rng.normal(0, 0.02, days)
    zl_ret = 0.3 * shock + rng.normal(0, 0.015, days)
    panel = pd.DataFrame({
        "ZL": 40 * np.exp(np.cumsum(zl_ret)),
        "TE_BRENT_CRUDE_OIL": 60 * np.exp(np.cumsum(shock)),
        "TE_BDI": 1500 * np.exp(np.cumsum(rng.normal(0, 0.03, days))),
        "TE_HEATING_OIL": 2 * np.exp(np.cumsum(rng.normal(0, 0.02, days))),
        "TE_PALM_OIL": 3000 * np.exp(np.cumsum(rng.normal(0, 0.015, days))),
    }, index=idx)
    return panel


def self_test() -> None:
    panel = _synthetic_panel()
    events = (ShockEvent("2019-03-09", "합성 사건 A", "합성"),
              ShockEvent("2021-06-15", "합성 사건 B", "합성"),
              ShockEvent("2030-01-01", "범위 밖 사건", "합성"))
    ev = event_study(panel, events)
    assert len(ev) == 2, f"[오류] 사건 연구 행 수 불일치: {len(ev)}"
    for h in EVENT_WINDOWS:
        assert f"ret_{h}" in ev.columns and f"pct_{h}" in ev.columns
    assert ev["ret_0"].notna().all() and ev["pct_20"].between(0, 100).all()
    assert "Brent_ret_20" in ev.columns
    samples = {"전체": (panel.index.min(), panel.index.max())}
    lp = local_projections(panel, samples=samples)
    assert len(lp) == len(SHOCK_PROXIES) * len(LP_HORIZONS), f"[오류] M2 행 수 {len(lp)}"
    assert lp[["beta", "ci_lo", "ci_hi"]].notna().all().all()
    assert (lp["ci_lo"] <= lp["beta"]).all() and (lp["beta"] <= lp["ci_hi"]).all()
    brent_h1 = lp[(lp["proxy"] == "Brent") & (lp["h"] == 1)].iloc[0]
    # 합성 설계(ZL 수익률 = 0.3×충격 + 잡음): Brent 1σ(=0.02) 당일 반응 ≈ +0.6%
    assert 0.003 < brent_h1["beta"] < 0.009, f"[오류] 합성 반응계수 이탈: {brent_h1['beta']}"
    md = render_report(ev, lp, panel, [])
    assert CAPTION in md and "| 합성 사건 A" in md
    # 무조건부 백분위 헬퍼
    assert abs(percentile_rank(np.arange(100, dtype=float), 49.0) - 50.0) < 1e-9
    # 초기 반응 = 첫 5일 내 절대값 최대(k=1, +0.03) → 이후 0 이하 재교차 첫 k=3
    assert _recovery_days(np.array([0.02, 0.03, 0.01, -0.01, 0.0]), 120) == 3
    assert _recovery_days(np.array([0.02, 0.01, 0.005]), 120) is None
    assert _recovery_days(np.array([-0.01, -0.04, -0.02, 0.01]), 120) == 3
    print("[완료] self-test 통과 — M1 2건 · M2 "
          f"{len(lp)}행 · Brent h=1 β={brent_h1['beta'] * 100:.2f}%")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="충격 전후 대두유 가격 반응 프로토타입")
    parser.add_argument("--self-test", action="store_true", help="합성 데이터 형상 검증")
    parser.add_argument("--out", type=Path, default=OUT_MD, help="출력 md 경로")
    args = parser.parse_args(argv)
    if args.self_test:
        self_test()
        return 0
    path = run(args.out)
    print(f"[완료] 보고서 생성: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
