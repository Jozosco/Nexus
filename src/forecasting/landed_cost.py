#!/usr/bin/env python3
"""
CFR 도착가 밴드 v0 — G2 운영 현실화 계층 (D-041 · WBS G2-OPS)

무엇을 만드는가:
    실무자가 실제로 지불하는 것은 CBOT 선물가가 아니라 **CFR 한국항 도착가**다.
    가격 4층 분해(competitive_differentiation §3b: CBOT + basis + 운임 + 보험) 중
    basis·운임 층을 **관세청 실측 CIF 역산**으로 근사해, CBOT 층과 합성한
    P10/P50/P90 도착가 밴드를 산출한다.

층 구성:
    ① CBOT 층   — feature mart의 feat_CBOT_BO_CLOSE(정산가) 최근 60거래일 경험 분포.
                   ⚠️ G2 분위수 모델(quantile LightGBM 등) 산출 전 **임시 스탠드인** —
                   G2 Preview 이후 모델 분위수로 교체한다.
    ② 내재층    — 실측 CIF(수입액USD ÷ 수입량kg × 1000) − CBOT 월평균 = basis+운임+보험
                   내재값. 최근 12개월 분포 P10/P50/P90.
                   부호는 음수 가능: 아르헨티나 수출세(~26%)로 남미 FOB가 할인되고
                   45Z 등 미국 정책이 ZL을 끌어올리면 CIF < CBOT가 실측 정상이다
                   (S&P 2026-07 실증 — basis가 CBOT 변동을 흡수).
    ③ 운임 시나리오 — BDI 90일 z-score 레짐(평시/경계 z>1/급등 z>2)에 따라
                   내재층의 상위 분위를 적용(§3d 판정 로직과 동일 임계).

데이터 소스 (전부 외부 파이프라인 — D-021 준수, 내부 S&OP/ERP 미사용):
    관세청 GW 수입실적(HS 1507.10 조대두유) · CBOT ZL(Databento/정산가) · TE BDI

fold 안전성: 모든 통계는 **후방참조**(rolling·tail)만 사용 — 미래 정보 누수 없음.
as-of: 본 모듈은 모델 학습 입력이 아닌 파생 분석층(보고서)이므로 attach_asof 불요.
       단 신선도(마지막 관측일·경과일)를 보고서 각주로 의무 표기한다.

사용:
    python -m src.forecasting.landed_cost              # 밴드 산출 + 보고서 저장
    python -m src.forecasting.landed_cost --self-test  # 자체검증(단위 정합·밴드폭)

산출: reports/market/landed_cost_band_{date}.md
의존성: pandas · pyarrow (xlsx 폴백 시 openpyxl)
"""
from __future__ import annotations

import argparse
import glob
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

# ── 상수 (매직 넘버 금지 — CLAUDE.md §3.2) ──────────────────────────────────
USC_LB_TO_USD_MT = 22.0462          # USc/lb → USD/MT (USDA 표준 환산)
CBOT_WINDOW_DAYS = 60               # CBOT 경험 분포 창(거래일)
BASIS_WINDOW_MONTHS = 12            # 내재층 분포 창(월)
BDI_Z_WINDOW_DAYS = 90              # BDI z-score 창(관측일)
BDI_Z_MIN_PERIODS = 30
MIN_BULK_KG = 100_000               # 벌크 화물 하한(100 MT) — 소량 샘플 수입 노이즈 제거
CIF_COUNTRY_MONTHS = 6              # 국가별 실측 CIF 표 최근 개월
BDI_Z_WATCH = 1.0                   # 경계 임계 (§3d)
BDI_Z_SURGE = 2.0                   # 급등 임계 (§3d)
SELF_TEST_BASIS_ABS_MIN = 10.0      # 내재층 중앙값 |값| 하한 — kg/MT 단위 오류 감지
SELF_TEST_BASIS_ABS_MAX = 300.0     # 상한 — 자릿수 오류 감지

# 운임 레짐 → 내재층 적용 분위 (하단, 중앙, 상단). 1.00 = 창 내 최대값.
MC_SAMPLES = 20_000                     # 몬테카를로 컨볼루션 표본 수 (시드 고정)

FREIGHT_SCENARIOS: dict[str, tuple[float, float, float]] = {
    "평시": (0.10, 0.50, 0.90),
    "경계": (0.25, 0.75, 0.90),     # z>1 — 분포 상위로 이동
    "급등": (0.50, 0.90, 1.00),     # z>2 — 상단은 창 내 최대
}

GOLD_MART = Path("data/gold/feature_mart.parquet")
CBOT_SESSION_PARQUET = Path("data/raw/cbot_session_close.parquet")
DATABENTO_CSV_GLOB = "data/raw/Databento/GLBX.MDP3/ZL_ohlcv-1d_*.csv"
CUSTOMS_PARQUET_GLOBS = ["data/raw/customs_import_*.parquet"]
GW_SBO_GLOB = ("data/raw/관세청/Import Export Performance by Commodity and Country(GW)/"
               "Soybean Oil/1507.10/*/*.xlsx")
TE_PARQUET = Path("data/raw/te_commodities_usd_mt.parquet")
REPORT_DIR = Path("reports/market")

_MONTH_RE = re.compile(r"(\d{1,2})\s*월")


@dataclass
class Layer:
    """밴드 구성 층 하나 — 분위수 + 출처·신선도 메타."""
    p10: float
    p50: float
    p90: float
    n: int
    last_date: date | None
    source: str
    note: str = ""


@dataclass
class LandedCostResult:
    cbot: Layer
    basis: Layer                      # 평시 분위(0.10/0.50/0.90) 기준
    scenario: str                     # 평시 / 경계 / 급등
    bdi_z: float | None
    bdi_last: date | None
    band_p10: float
    band_p50: float
    band_p90: float
    basis_applied: tuple[float, float, float]   # 시나리오 적용 후 내재층 (하·중·상)
    band_stress: tuple[float, float, float]     # 완전 순위의존 상계 (분위 단순합 + 운임 레짐)
    cif_country: pd.DataFrame         # 국가별 실측 CIF 최근 N개월
    basis_monthly: pd.Series          # 월별 내재값(최근 창)


# ── 로더 (후방참조 전용 · 읽기 전용) ─────────────────────────────────────────
def load_cbot_usd_mt() -> tuple[pd.Series, str, str]:
    """CBOT ZL 일별 종가(USD/MT) — 우선순위 체인.

    ① cbot_session_close.parquet(정산가·target_eligible·**전 기간**) → ② mart
      feat_CBOT_BO_CLOSE(게이트 통과 정산가 — 단 **분석창 캡**(M-008 DEFAULT_END 2025-12)이라
      당년 월평균이 없음. A-245(런 #87): mart 1순위 시 CIF(당년)와 공통 월 0건으로 매일
      강등 → 세션 parquet를 앞세운다) → ③ Databento UTC 일봉 CSV(**진단 계열 — 정산가
      아님**. V-001 실측: 정산가 대비 중앙값 괴리 0.10%. CBOT_BO_UTC_* 진단 용도).
    """
    if CBOT_SESSION_PARQUET.exists():
        df = pd.read_parquet(CBOT_SESSION_PARQUET)
        df = df[df["indicator_code"] == "CBOT_BO_CLOSE"]
        if len(df):
            s = (df.assign(d=pd.to_datetime(df["event_time"]).dt.normalize())
                   .set_index("d")["value"].astype(float).sort_index())
            return s * USC_LB_TO_USD_MT, "cbot_session_close.parquet(정산가·전기간)", ""
    if GOLD_MART.exists():
        mart = pd.read_parquet(GOLD_MART)
        if "feat_CBOT_BO_CLOSE" in mart.columns:
            s = (mart.set_index(pd.to_datetime(mart["price_date"]))["feat_CBOT_BO_CLOSE"]
                     .dropna().sort_index())
            if len(s):
                return (s * USC_LB_TO_USD_MT,
                        "feature mart(정산가·게이트 통과 — 분석창 캡 2025-12)", "")
    csvs = sorted(glob.glob(DATABENTO_CSV_GLOB))
    if csvs:
        zl = pd.read_csv(csvs[-1], parse_dates=["price_date"])
        zl = zl[pd.to_numeric(zl["close"], errors="coerce") > 0].sort_values("price_date")
        s = zl.set_index("price_date")["close"].astype(float)
        note = ("⚠️ Databento UTC 일봉 **진단 계열** — CME 정산가 아님. "
                "정산가 대비 중앙값 괴리 0.10%(V-001 실측). CI 재실행 시 정산가로 대체됨.")
        return s * USC_LB_TO_USD_MT, "Databento UTC 진단 계열", note
    raise RuntimeError("[오류] CBOT 가격 원천 없음 — feature mart 또는 Databento CSV 필요. "
                       "Historical(connector=databento) 실행 후 재시도하세요.")


def _parse_gw_xlsx(path: Path) -> pd.DataFrame:
    """관세청 GW 업로드본(연도 시트 × 월행 × 5지표열) → 월별 수입액·수입량.

    ⚠️ xlsx 직독은 **폴백**이다: 정식 경로는 scripts/ingest_customs_gw_xlsx.py의 parquet.
    관세청 API는 개발 샌드박스 프록시 차단(A-069)으로 GitHub Actions 전용이라,
    로컬에서는 조정자 업로드 원본(동일 데이터)을 직독한다. (verify_customs_gw.py 패턴)
    """
    recs: list[dict] = []
    try:
        xl = pd.ExcelFile(path)
    except Exception as e:
        print(f"  [경고] {path.name} 읽기 실패: {type(e).__name__}")
        return pd.DataFrame()
    for sheet in xl.sheet_names:
        ym = re.search(r"(\d{4})", str(sheet))
        if not ym:
            continue
        raw = xl.parse(sheet, header=None)
        hdr = next((i for i in range(min(5, len(raw)))
                    if raw.iloc[i].astype(str).str.contains("무역수지").any()), None)
        if hdr is None:
            continue
        for r in range(hdr + 1, len(raw)):
            mm = _MONTH_RE.search(str(raw.iloc[r, 0]))
            if not mm:
                continue
            recs.append({
                "year": int(ym.group(1)), "month": int(mm.group(1)),
                "imp_usd": pd.to_numeric(raw.iloc[r, 4], errors="coerce"),
                "imp_kg": pd.to_numeric(raw.iloc[r, 5], errors="coerce"),
            })
    df = pd.DataFrame(recs)
    if df.empty:
        return df
    df["price_date"] = pd.to_datetime(dict(year=df["year"], month=df["month"], day=1))
    return df


def _read_customs_api_frames() -> list[pd.DataFrame]:
    """관세청 API 커넥터 parquet(customs_import_*) — A-216 일별 증분화 후 **당년만** 담긴다."""
    frames: list[pd.DataFrame] = []
    for pattern in CUSTOMS_PARQUET_GLOBS:
        for f in sorted(glob.glob(pattern)):
            try:
                df = pd.read_parquet(f)
            except Exception:
                continue
            cols = set(df.columns)
            if not {"import_cif_usd", "import_weight_kg"}.issubset(cols):
                continue
            sub = pd.DataFrame({
                "price_date": pd.to_datetime(df["price_date"]),
                "imp_usd": pd.to_numeric(df["import_cif_usd"], errors="coerce"),
                "imp_kg": pd.to_numeric(df["import_weight_kg"], errors="coerce"),
                "country": df.get("country_name", pd.Series("전체", index=df.index)),
            })
            if "hs_code" in cols:                    # 조대두유(150710)만
                sub = sub[df["hs_code"].astype(str).str.startswith("150710")]
            frames.append(sub)
    return frames


def _read_customs_gw_frames() -> list[pd.DataFrame]:
    """관세청 GW 업로드본(2010~) — 국가 파일 합산. 통합본(16years)은 검증 참조용이라 제외."""
    frames: list[pd.DataFrame] = []
    for f in sorted(glob.glob(GW_SBO_GLOB)):
        p = Path(f)
        if "16years" in p.stem:
            continue
        df = _parse_gw_xlsx(p)
        if df.empty:
            continue
        df["country"] = p.stem
        frames.append(df[["price_date", "imp_usd", "imp_kg", "country"]])
    return frames


def _bulk_monthly(frames: list[pd.DataFrame]) -> pd.DataFrame:
    """행 목록 → 벌크 하한 적용 후 (국가, 월초) 합산 표. 빈 입력이면 빈 표."""
    if not frames:
        return pd.DataFrame(columns=["country", "price_date", "imp_usd", "imp_kg"])
    allc = pd.concat(frames, ignore_index=True)
    bulk = allc[(allc["imp_kg"] >= MIN_BULK_KG) & (allc["imp_usd"] > 0)].copy()
    if bulk.empty:
        return pd.DataFrame(columns=["country", "price_date", "imp_usd", "imp_kg"])
    # 원천별 일자 관행(월초·월중·연초)이 달라도 CBOT 월평균(MS)과 정렬되도록 월초 정규화
    bulk["price_date"] = pd.to_datetime(bulk["price_date"]).values.astype("datetime64[M]")
    return (bulk.groupby(["country", "price_date"])[["imp_usd", "imp_kg"]].sum()
                .reset_index())


def combine_customs_sources(api_tbl: pd.DataFrame, gw_tbl: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """API 당년분 + GW 히스토리 **합집합** — 월 단위 우선순위(API가 있는 달은 API만).

    A-245(런 #87): 구 코드는 API parquet가 있으면 GW를 아예 읽지 않는 either/or였고,
    일별 증분화(당년만) 이후 API 7개월 vs 분석창 CBOT의 공통 월이 0건이 되어 매일 강등됐다.
    (국가,월) 단위 덮어쓰기는 국가명 표기가 소스마다 달라(한글 vs 파일명) 같은 달을
    이중 합산할 수 있으므로 **월 단위**로 API를 우선한다.
    """
    api_months = set(pd.to_datetime(api_tbl["price_date"])) if len(api_tbl) else set()
    gw_keep = gw_tbl[~pd.to_datetime(gw_tbl["price_date"]).isin(api_months)] if len(gw_tbl) else gw_tbl
    combined = pd.concat([api_tbl, gw_keep], ignore_index=True)
    n_api = len(api_months)
    n_gw = gw_keep["price_date"].nunique() if len(gw_keep) else 0
    if n_api and n_gw:
        label = f"관세청 API 당년 {n_api}개월 + GW 업로드본 {n_gw}개월(1507.10 조대두유)"
    elif n_api:
        label = "customs_import parquet(관세청 API)"
    else:
        label = "관세청 GW 업로드본(1507.10 조대두유 · 국가 파일 합산)"
    return combined, label


def load_customs_sbo_cif() -> tuple[pd.Series, pd.DataFrame, str]:
    """한국 조대두유(HS 1507.10) 월별·국가별 실측 CIF(USD/MT).

    반환: (월별 CIF 시계열[국가 합산·벌크 하한], 국가별 월 CIF 롱테이블, 소스 라벨)
    CIF = 수입액(달러) ÷ 수입량(kg) × 1000. 벌크 하한(MIN_BULK_KG)으로
    소량 샘플 수입($10,000+/MT로 왜곡)을 제거한다. 소스는 API(당년)+GW(히스토리) 합집합.
    """
    api_tbl = _bulk_monthly(_read_customs_api_frames())
    gw_tbl = _bulk_monthly(_read_customs_gw_frames())
    if api_tbl.empty and gw_tbl.empty:
        raise RuntimeError("[오류] 관세청 수입실적 벌크(≥100 MT) 관측 0건 — customs parquet 또는 "
                           "GW xlsx(data/raw/관세청/...) 필요.")
    by_country, source = combine_customs_sources(api_tbl, gw_tbl)
    by_country["price_date"] = pd.to_datetime(by_country["price_date"])
    monthly = by_country.groupby("price_date")[["imp_usd", "imp_kg"]].sum()
    monthly_cif = (monthly["imp_usd"] / monthly["imp_kg"] * 1000).rename("cif_usd_mt")
    by_country["cif_usd_mt"] = by_country["imp_usd"] / by_country["imp_kg"] * 1000
    by_country["volume_mt"] = by_country["imp_kg"] / 1000
    return monthly_cif.sort_index(), by_country, source


def load_bdi_z() -> tuple[float | None, date | None]:
    """TE BDI 90일 롤링 z-score 최신값 — mart 우선, TE parquet 폴백. 후방참조만."""
    series: pd.Series | None = None
    if GOLD_MART.exists():
        mart = pd.read_parquet(GOLD_MART)
        if "feat_TE_BDI" in mart.columns:
            series = (mart.set_index(pd.to_datetime(mart["price_date"]))["feat_TE_BDI"]
                          .dropna().sort_index())
    if series is None and TE_PARQUET.exists():
        te = pd.read_parquet(TE_PARQUET)
        bdi = te[te["indicator_code"] == "TE_BDI"].sort_values("price_date")
        if len(bdi):
            series = bdi.set_index(pd.to_datetime(bdi["price_date"]))["value"].astype(float)
    if series is None or len(series) < BDI_Z_MIN_PERIODS:
        return None, None
    mean = series.rolling(BDI_Z_WINDOW_DAYS, min_periods=BDI_Z_MIN_PERIODS).mean()
    std = series.rolling(BDI_Z_WINDOW_DAYS, min_periods=BDI_Z_MIN_PERIODS).std()
    z = ((series - mean) / std.where(std > 0)).dropna()
    if z.empty:
        return None, None
    return float(z.iloc[-1]), z.index[-1].date()


# ── 밴드 합성 ────────────────────────────────────────────────────────────────
def _quantile(s: pd.Series, q: float) -> float:
    return float(s.max()) if q >= 1.0 else float(s.quantile(q))


def classify_freight_regime(z: float | None) -> str:
    """BDI z-score → 운임 레짐 (§3d 임계와 동일). z 미확보 시 평시 처리(보수 아님 명시)."""
    if z is None:
        return "평시"
    if z > BDI_Z_SURGE:
        return "급등"
    if z > BDI_Z_WATCH:
        return "경계"
    return "평시"


def build_landed_band() -> LandedCostResult:
    """CBOT 층 + 내재 basis·운임 층 합성 → 도착가 밴드.

    합성 규칙(GPT-5.6-Sol 교차검증 정정 2026-08-14):
    - **주 밴드** = 몬테카를로 독립 컨볼루션 — 두 층에서 독립 복원추출한 합의
      P10/P50/P90. 분위 단순합(P10+P10 등)은 완전 순위의존(comonotonic) 가정이라
      합계의 통계적 분위가 아니므로 주 밴드로 쓰지 않는다.
    - **스트레스 상계** = 분위 단순합 + 운임 레짐 시나리오 — 두 층이 함께 극단으로
      움직이는 최악 결합의 보수적 상·하계로만 별도 표기한다.
    """
    cbot_daily, cbot_src, cbot_note = load_cbot_usd_mt()
    recent = cbot_daily.tail(CBOT_WINDOW_DAYS)
    cbot = Layer(
        p10=float(recent.quantile(0.10)), p50=float(recent.quantile(0.50)),
        p90=float(recent.quantile(0.90)), n=len(recent),
        last_date=recent.index[-1].date(), source=cbot_src, note=cbot_note)

    monthly_cif, by_country, customs_src = load_customs_sbo_cif()
    cbot_monthly = cbot_daily.resample("MS").mean()
    basis_all = (monthly_cif - cbot_monthly).dropna()
    if basis_all.empty:
        raise RuntimeError(
            "[오류] CIF·CBOT 공통 월 0건 — 내재층 산출 불가. "
            f"CIF {len(monthly_cif)}개월({monthly_cif.index.min().date()}~"
            f"{monthly_cif.index.max().date()} · {customs_src}) vs "
            f"CBOT {len(cbot_monthly)}개월({cbot_monthly.index.min().date()}~"
            f"{cbot_monthly.index.max().date()})")
    basis_window = basis_all.tail(BASIS_WINDOW_MONTHS)
    basis = Layer(
        p10=float(basis_window.quantile(0.10)), p50=float(basis_window.quantile(0.50)),
        p90=float(basis_window.quantile(0.90)), n=len(basis_window),
        last_date=basis_window.index[-1].date(), source=customs_src,
        note="내재값 = 실측 CIF − CBOT 월평균 (basis+운임+보험 합산층)")

    bdi_z, bdi_last = load_bdi_z()
    scenario = classify_freight_regime(bdi_z)
    q_lo, q_mid, q_hi = FREIGHT_SCENARIOS[scenario]
    applied = (_quantile(basis_window, q_lo), _quantile(basis_window, q_mid),
               _quantile(basis_window, q_hi))

    recent_countries = by_country[by_country["price_date"]
                                  >= by_country["price_date"].max()
                                  - pd.DateOffset(months=CIF_COUNTRY_MONTHS - 1)]

    # 주 밴드: 몬테카를로 독립 컨볼루션 (시드 고정 — 재현성)
    rng = np.random.default_rng(20260814)
    mc_sums = (rng.choice(recent.to_numpy(), MC_SAMPLES, replace=True)
               + rng.choice(basis_window.to_numpy(), MC_SAMPLES, replace=True))
    mc = tuple(float(np.quantile(mc_sums, q)) for q in (0.10, 0.50, 0.90))

    return LandedCostResult(
        cbot=cbot, basis=basis, scenario=scenario, bdi_z=bdi_z, bdi_last=bdi_last,
        band_p10=mc[0], band_p50=mc[1], band_p90=mc[2], basis_applied=applied,
        band_stress=(cbot.p10 + applied[0], cbot.p50 + applied[1], cbot.p90 + applied[2]),
        cif_country=recent_countries.sort_values(["price_date", "country"]),
        basis_monthly=basis_window)


# ── 보고서 ───────────────────────────────────────────────────────────────────
def _age_days(d: date | None) -> str:
    if d is None:
        return "미확보"
    return f"{d.isoformat()} (경과 {(date.today() - d).days}일)"


def render_md(r: LandedCostResult) -> str:
    today = date.today()
    cbot_width = r.cbot.p90 - r.cbot.p10
    band_width = r.band_p90 - r.band_p10
    if r.bdi_z is not None:
        regime_line = f"- 운임 레짐: **{r.scenario}** (BDI 90일 z = {r.bdi_z:+.2f})"
    else:
        regime_line = f"- 운임 레짐: **{r.scenario}** (BDI z 미확보 — 평시 가정)"
    lines = [
        f"# CIF 한국항 도착가 밴드 v0 — {today}",
        "",
        "> G2 운영 현실화 계층(D-041). CBOT 층은 G2 분위수 모델 산출 전 **임시 스탠드인**",
        "> (최근 60거래일 경험 분포)이며, G2 Preview 이후 모델 분위수로 교체함.",
        "> 근거 구조: 가격 4층 분해(CBOT+basis+운임+보험) — competitive_differentiation §3b.",
        "",
        "## 도착가 밴드 (조대두유 CIF 한국항 기준, USD/MT)",
        "",
        "| 분위 | **참고 밴드 (MC 독립 컨볼루션)** | 스트레스 상계 (완전 순위의존 + 운임 레짐) |",
        "|---|---|---|",
        f"| P10 | **{r.band_p10:,.0f}** | {r.band_stress[0]:,.0f} |",
        f"| P50 | **{r.band_p50:,.0f}** | {r.band_stress[1]:,.0f} |",
        f"| P90 | **{r.band_p90:,.0f}** | {r.band_stress[2]:,.0f} |",
        "",
        f"- 참고 밴드폭 {band_width:,.0f} $/MT ≥ CBOT 밴드폭 {cbot_width:,.0f} $/MT — "
        "운임·basis 불확실성 가산",
        "- 참고 밴드는 두 층 독립 복원추출 합의 분위(몬테카를로 20,000표본·시드 고정). "
        "분위 단순합은 합계의 통계적 분위가 아니므로 스트레스 상계로만 표기.",
        "- ⚠️ **해석 한계(8/19 판정 [치명] 반영)**: 내재층(도착월 CIF−동월 CBOT)에는 계약~"
        "도착 사이의 **과거 CBOT 변동분이 포함**되므로, 이를 현재 CBOT 층과 다시 합산하면 "
        "일부 변동이 이중계상된다. 또한 두 층의 독립 가정은 'basis가 CBOT 변동을 흡수한다'는 "
        "관측(음의존 시사)과 상충하며 상관 검정이 없다. 따라서 이 표는 "
        "**'CBOT+basis+운임+보험'의 확률 밴드가 아니라 규모감 참고 범위**다 — "
        "성분 분해·조건부 예측은 G2 분위수 모델(리드타임 시프트 정렬 포함)로 대체 예정.",
        "- 기준 명칭 정정: 원천이 관세청 **CIF**(보험 포함)이므로 CIF 기준으로 표기 "
        "(CFR은 매도인 보험 조달 의무 없음 — Incoterms 구분).",
        regime_line + " — ⚠️ BDI는 건화물 지수로 액체 탱커 운임과 시장이 다름"
        "(A-013) — BCAA 실측 확보(DQ-2) 전 방향 프록시로만 사용",
        f"- 시나리오 임계: 평시 z≤{BDI_Z_WATCH:.0f} / 경계 z>{BDI_Z_WATCH:.0f} / "
        f"급등 z>{BDI_Z_SURGE:.0f} — 인과 근거 CE-010·CE-013·CE-016(ontology causal_edges)",
        "",
        "## 구성 분해",
        "",
        "| 층 | P10 | P50 | P90 | 관측 | 마지막 관측 | 출처 |",
        "|---|---|---|---|---|---|---|",
        f"| CBOT ZL (USD/MT 환산 ×{USC_LB_TO_USD_MT}) | {r.cbot.p10:,.0f} | {r.cbot.p50:,.0f} "
        f"| {r.cbot.p90:,.0f} | {r.cbot.n}거래일 | {r.cbot.last_date} | {r.cbot.source} |",
        f"| 내재 basis+운임 (평시 분위) | {r.basis.p10:+,.0f} | {r.basis.p50:+,.0f} "
        f"| {r.basis.p90:+,.0f} | {r.basis.n}개월 | {r.basis.last_date} | {r.basis.source} |",
        "",
        f"- 내재층 정의: {r.basis.note}",
        "- 내재층 부호 해석: 음수 = 한국 도착 실측 CIF가 CBOT를 하회 — 아르헨티나 수출세"
        " 할인·미국 45Z 정책의 ZL 프리미엄이 원인(§3b, S&P 실증: basis가 CBOT 변동을 흡수).",
        "",
        "### 월별 내재값 (최근 창)",
        "",
        "| 월 | 내재 basis+운임 ($/MT) |",
        "|---|---|",
    ]
    lines += [f"| {d.date()} | {v:+,.0f} |" for d, v in r.basis_monthly.items()]
    lines += [
        "",
        "## 국가별 실측 CIF (조대두유 1507.10 · 벌크 ≥100 MT · 최근 6개월)",
        "",
        "| 월 | 원산지 | CIF (USD/MT) | 물량 (MT) |",
        "|---|---|---|---|",
    ]
    for _, row in r.cif_country.iterrows():
        lines.append(f"| {row['price_date'].date()} | {row['country']} "
                     f"| {row['cif_usd_mt']:,.0f} | {row['volume_mt']:,.0f} |")
    lines += [
        "",
        "## 신선도·한계 각주",
        "",
        f"- CBOT 층 마지막 관측: {_age_days(r.cbot.last_date)}"
        + (f" — {r.cbot.note}" if r.cbot.note else ""),
        f"- 관세청 실측 CIF 마지막 월: {_age_days(r.basis.last_date)} — 월간 확정치"
        "(당월 통계는 익월 15일경 공표)",
        f"- BDI 마지막 관측: {_age_days(r.bdi_last)}",
        f"- 벌크 하한 {MIN_BULK_KG // 1000} MT 미만 소량 수입은 제외(단가 왜곡 방지).",
        "- 보험·부대비는 내재층에 합산 포함(분리 실측 없음 — Platts/BCAA 구독 전).",
        "- 내재층 해석 한계(GPT 교차검증): 도착월 CIF와 동월 CBOT의 차이는 basis+운임 외에"
        " **리드타임(40~50일) 중 가격변동·계약조건·원산지 구성**을 함께 포함함. 순수"
        " basis·운임 분리는 계약 시점 정렬(리드타임 시프트) 또는 실측 호가(DQ-1) 확보 후 가능.",
        "- 본 산출물은 참고 정보임. 조달 의사결정은 CLAUDE.md §6 HITL 게이트를 따름.",
        "",
    ]
    return "\n".join(lines)


# ── 자체검증 ─────────────────────────────────────────────────────────────────
def self_test(r: LandedCostResult) -> list[str]:
    """단위 정합·밴드폭 검증. 실패 항목 목록 반환(빈 리스트 = 통과)."""
    problems: list[str] = []
    # ① 내재층 중앙값 규모: kg↔MT 환산 오류면 자릿수가 이탈한다(×1000 어긋남).
    #    부호는 음수 허용 — 실측이 음수(아르헨 수출세 할인·45Z ZL 프리미엄)이므로 |값| 기준.
    abs_median = abs(r.basis.p50)
    if not (SELF_TEST_BASIS_ABS_MIN <= abs_median <= SELF_TEST_BASIS_ABS_MAX):
        problems.append(
            f"내재층 중앙값 |{r.basis.p50:+,.1f}| $/MT — 허용범위 "
            f"[{SELF_TEST_BASIS_ABS_MIN}, {SELF_TEST_BASIS_ABS_MAX}] 밖 (단위 오류 의심)")
    # ② 도착가 밴드폭 ≥ CBOT 밴드폭 — 운임 불확실성 가산 구조 검증
    band_width = r.band_p90 - r.band_p10
    cbot_width = r.cbot.p90 - r.cbot.p10
    if band_width < cbot_width:
        problems.append(f"도착가 밴드폭 {band_width:,.0f} < CBOT 밴드폭 {cbot_width:,.0f}")
    # ③ 분위 순서·유한성
    if not (r.band_p10 <= r.band_p50 <= r.band_p90):
        problems.append("밴드 분위 역전(P10 ≤ P50 ≤ P90 위반)")
    for name, v in [("P10", r.band_p10), ("P50", r.band_p50), ("P90", r.band_p90)]:
        if not pd.notna(v):
            problems.append(f"밴드 {name} 비유한값")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description="CFR 도착가 밴드 v0 (G2 운영 현실화 계층)")
    ap.add_argument("--self-test", action="store_true", help="자체검증만 수행")
    a = ap.parse_args()

    print("[도착가 밴드] 층 로드 중 — 관세청 CIF · CBOT · BDI (전부 외부 데이터, D-021)")
    r = build_landed_band()
    print(f"  CBOT 층({r.cbot.source}): P10/P50/P90 = "
          f"{r.cbot.p10:,.0f} / {r.cbot.p50:,.0f} / {r.cbot.p90:,.0f} $/MT")
    print(f"  내재층(최근 {r.basis.n}개월): P10/P50/P90 = "
          f"{r.basis.p10:+,.0f} / {r.basis.p50:+,.0f} / {r.basis.p90:+,.0f} $/MT")
    bdi_z_label = f"{r.bdi_z:+.2f}" if r.bdi_z is not None else "미확보"
    print(f"  운임 레짐: {r.scenario} (BDI z={bdi_z_label})")
    print(f"  도착가 밴드: P10/P50/P90 = "
          f"{r.band_p10:,.0f} / {r.band_p50:,.0f} / {r.band_p90:,.0f} $/MT")

    problems = self_test(r)
    for p in problems:
        print(f"  🚨 {p}")
    if problems:
        print("[중단] 자체검증 실패 — 보고서를 저장하지 않습니다.")
        return 1
    print("  ✅ 자체검증 통과 (단위 정합 · 밴드폭 ≥ CBOT 밴드폭 · 분위 순서)")
    if a.self_test:
        return 0

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORT_DIR / f"landed_cost_band_{date.today()}.md"
    out.write_text(render_md(r), encoding="utf-8")
    print(f"[완료] 보고서 → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
