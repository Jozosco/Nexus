"""
상품 가격 커넥터 — WBS 1.1.2 보완 (D-002 P0 갭 해소)
수집 대상:
  - CBOT 대두유 선물 BO=F: yfinance (기본) → Nasdaq Data Link CHRIS/CME_BO1 (폴백)
  - 팜유 글로벌 벤치마크: FRED PPOILUSDM (월별, CPO 대리지표)
  - ARS/USD 공식 환율: api.bcra.gob.ar (인증 불필요)
  - 미국 가뭄 지수 D0-D4: drought.gov USDM API (인증 불필요, 주별 갱신)
실행 환경: GitHub Actions / VS Code Web (Azure ML Studio)
참고 MEMORY: D-002 (P0 데이터갭), M-002 (T+2 FX 오프셋)
"""
from __future__ import annotations

import os
import time
from datetime import date, timedelta
from typing import Optional

import httpx
import pandas as pd

OUTPUT_DIR = "data/raw"

# ── USDM 가뭄 지수 대상 주 (미국 대두 Top-5 생산 주) ────────────────────────
SOY_STATES_US = ["IA", "IL", "IN", "MN", "NE"]

# ── Nasdaq Data Link 주의 사항 ──────────────────────────────────────────────
# NASDAQ_DATALINK_API_KEY: CHRIS/CME_BO1 (대두유 선물)은 Nasdaq 인수 후 2018년 삭제됨
# BDI: Nasdaq Data Link에서 제공한 적 없음 (Baltic Exchange 라이선스 — Bloomberg/Refinitiv 전용)
# 이 키는 기타 Nasdaq 독점 데이터셋(예: AMTR, ZILL)에만 사용 가능
# BO=F 대안: yfinance(무료, IP 차단 위험) → 유료는 Databento($5-25/mo), Barchart OnDemand
# BDI 대안: Perplexity(현행), Trading Economics API($65-200/mo), Baltic Exchange Direct(엔터프라이즈)
NASDAQ_BASE = "https://data.nasdaq.com/api/v3/datasets"


def _get(url: str, params: dict | None = None, headers: dict | None = None,
         max_retries: int = 4) -> httpx.Response:
    delay = 2
    for attempt in range(max_retries):
        try:
            r = httpx.get(url, params=params or {}, headers=headers or {},
                          timeout=30)
            r.raise_for_status()
            return r
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"[오류] API 호출 실패 ({url}): {e}") from e
            time.sleep(delay)
            delay *= 2
    raise RuntimeError(f"[오류] API 호출 반복 실패 ({url})")


# ── 1. CBOT 대두유 선물 (BO=F) ──────────────────────────────────────────────

def fetch_bo_futures_yfinance(days_back: int = 10) -> pd.DataFrame:
    """CBOT BO=F 일간 OHLCV — yfinance (Yahoo Finance IP 차단 위험, 재시도 포함)."""
    try:
        import yfinance as yf
    except ImportError:
        print("[경고] yfinance 미설치 — BO=F yfinance 건너뜀 (Nasdaq Data Link 폴백 사용)")
        return pd.DataFrame()

    delay = 10
    for attempt in range(3):
        try:
            df = yf.Ticker("BO=F").history(period=f"{days_back}d", auto_adjust=True)
            if df.empty:
                print("[경고] BO=F yfinance: 데이터 없음 — Nasdaq Data Link 폴백으로 전환")
                return pd.DataFrame()
            df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
            df.index.name = "price_date"
            df = df.reset_index()
            df["price_date"] = pd.to_datetime(df["price_date"]).dt.tz_localize(None)
            result = df.melt(id_vars=["price_date"], var_name="indicator_code", value_name="value")
            result["source_name"] = "yfinance/CME_BO"
            result["indicator_code"] = "CBOT_BO_" + result["indicator_code"].str.upper()
            result["unit"] = "USc/lb"
            result["ingested_at"] = pd.Timestamp.utcnow()
            return result
        except Exception as e:
            if "429" in str(e) or "RateLimit" in str(e) or "Too Many" in str(e):
                print(f"[경고] Yahoo Finance 레이트 리밋 (시도 {attempt + 1}/3): {e}")
                if attempt < 2:
                    time.sleep(delay)
                    delay *= 2
            else:
                print(f"[경고] BO=F yfinance 실패: {e}")
                break
    return pd.DataFrame()


def fetch_cbot_soybean_oil(days_back: int = 10) -> pd.DataFrame:
    """CBOT 대두유 선물 종합 수집 — yfinance(무료, IP차단 위험).
    유료 대안: Databento(CME ZL 일간 $5-25/mo) · Barchart OnDemand.
    Nasdaq DataLink CHRIS/CME_BO1: 2018년 삭제 — 사용 불가.
    """
    df = fetch_bo_futures_yfinance(days_back)
    if df.empty:
        print("[경고] BO=F 수집 실패 — 유료 대안(Databento/Barchart) 도입 검토 필요")
    return df


# ── 2. 팜유 글로벌 벤치마크 (FRED PPOILUSDM — 월별, CPO 대리지표) ────────────

def fetch_cpo_proxy_fred(start: str = "2017-01-01") -> pd.DataFrame:
    """
    IMF 팜유 글로벌 벤치마크 (FRED PPOILUSDM) — 한국 CIF CPO 대리 지표.
    주의: 월별 데이터. 실제 한국 CIF 가격은 MPOB/Reuters 수동 수집 필요.
    """
    api_key = os.environ.get("FRED_API_KEY", "")
    if not api_key:
        print("[경고] FRED_API_KEY 미등록 — CPO 프록시 건너뜀")
        return pd.DataFrame()
    try:
        r = _get("https://api.stlouisfed.org/fred/series/observations", params={
            "series_id": "PPOILUSDM",
            "api_key": api_key,
            "file_type": "json",
            "observation_start": start,
        })
        obs = r.json().get("observations", [])
        if not obs:
            return pd.DataFrame()
        df = pd.DataFrame(obs)[["date", "value"]]
        df.columns = ["price_date", "value"]
        df["price_date"] = pd.to_datetime(df["price_date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df["source_name"] = "FRED"
        df["indicator_code"] = "CPO_GLOBAL_USD_MT_PROXY"
        df["unit"] = "USD/mt"
        df["ingested_at"] = pd.Timestamp.utcnow()
        return df.dropna(subset=["value"])
    except Exception as e:
        print(f"[경고] FRED CPO 프록시 수집 실패: {e}")
        return pd.DataFrame()


# ── 3. ARS/USD 공식 환율 (api.bcra.gob.ar — 인증 불필요) ─────────────────────

def fetch_ars_usd_bcra(days_back: int = 10) -> pd.DataFrame:
    """
    아르헨티나 중앙은행(BCRA) 공식 ARS/USD 환율.
    api.bcra.gob.ar/estadisticas/v3.0/cotizaciones — 인증 불필요.
    """
    rows = []
    for d in range(days_back):
        target = date.today() - timedelta(days=d)
        if target.weekday() >= 5:  # 주말 건너뜀
            continue
        try:
            r = _get(
                f"https://api.bcra.gob.ar/estadisticas/v3.0/cotizaciones/{target.isoformat()}",
                headers={"Accept": "application/json"},
            )
            data = r.json()
            results_list = data.get("results", [])
            for entry in results_list:
                if entry.get("codigoMoneda") == "USD":
                    rows.append({
                        "price_date":     target.isoformat(),
                        "source_name":    "BCRA_OFICIAL",
                        "indicator_code": "ARS_USD_OFICIAL",
                        "value":          float(entry.get("tipoPase", 0)),
                        "unit":           "ARS/USD",
                    })
                    break
        except Exception as e:
            print(f"[경고] BCRA ARS/USD {target}: {e}")
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["ingested_at"] = pd.Timestamp.utcnow()
    return df


# ── 4. 미국 가뭄 지수 D0-D4 (USDM API — 인증 불필요, 주별 갱신) ─────────────

DROUGHT_API = (
    "https://usdmdataservices.unl.edu/api/"
    "StateStatistics/GetDroughtSeverityStatisticsByArea"
)

def fetch_us_drought_stats(states: list[str] = SOY_STATES_US,
                           lookback_days: int = 21) -> pd.DataFrame:
    """
    미국 가뭄 모니터 D0-D4 통계 — drought.gov USDM API (인증 불필요).
    대두 주요 생산 주: Iowa·Illinois·Indiana·Minnesota·Nebraska.
    갱신 주기: 매주 목요일. 일간 파이프라인에서 동일 주 중복 저장 허용 (idempotent).
    """
    end   = date.today()
    start = end - timedelta(days=lookback_days)
    rows  = []
    for state in states:
        try:
            r = _get(DROUGHT_API, params={
                "aoi":            state,
                "startdate":      start.strftime("%-m/%-d/%Y"),
                "enddate":        end.strftime("%-m/%-d/%Y"),
                "statisticsType": 2,  # 배타적(exclusive) 카테고리
            }, headers={"Accept": "application/json"})
            entries = r.json()
            for entry in entries:
                map_date = entry.get("MapDate", "")
                if not map_date:
                    continue
                for level in ["None", "D0", "D1", "D2", "D3", "D4"]:
                    val = entry.get(level)
                    if val is None:
                        continue
                    rows.append({
                        "price_date":     map_date[:10],  # YYYY-MM-DD
                        "source_name":    "USDM_drought.gov",
                        "indicator_code": f"DROUGHT_{level}_{state}",
                        "region":         state,
                        "country":        "US",
                        "value":          float(val),
                        "unit":           "% of area",
                    })
        except Exception as e:
            print(f"[경고] USDM 가뭄 지수 {state} 수집 실패: {e}")
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["ingested_at"] = pd.Timestamp.utcnow()
    return df


def fetch_cpo_te() -> pd.DataFrame:
    """Trading Economics CPO 현물 가격 — FRED 월별 프록시보다 갱신 빈도 높음.

    TRADING_ECONOMICS_API_KEY 등록 시 FRED 프록시 대신 사용.
    """
    te_key = os.environ.get("TRADING_ECONOMICS_API_KEY", "").strip()
    if not te_key:
        return pd.DataFrame()
    try:
        from src.pipeline.connectors.te_connector import fetch_cpo  # type: ignore
        return fetch_cpo()
    except ImportError:
        pass
    try:
        import tradingeconomics as te  # type: ignore
        te.login(te_key)
        for symbol in ("cpo", "palm-oil"):
            try:
                result = te.getMarketsBySymbol(symbols=symbol, output_type="df")
                if result is not None and len(result) > 0:
                    date_col  = next((c for c in ["DateTime", "Date", "date"] if c in result.columns), None)
                    value_col = next((c for c in ["Last", "Close", "Value"] if c in result.columns), None)
                    if date_col and value_col:
                        df = pd.DataFrame({
                            "price_date":     pd.to_datetime(result[date_col], errors="coerce"),
                            "value":          pd.to_numeric(result[value_col], errors="coerce"),
                            "source_name":    "TradingEconomics/BursaMalaysia",
                            "indicator_code": "CPO_USD_MT",
                            "unit":           "USD/MT",
                            "ingested_at":    pd.Timestamp.utcnow(),
                        })
                        return df.dropna(subset=["price_date", "value"])
            except Exception:
                continue
    except Exception as e:
        print(f"[경고] Trading Economics CPO 수집 실패: {e}")
    return pd.DataFrame()


def run() -> None:
    import os as _os
    _os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y%m%d")

    frames = []
    # 1. CBOT 대두유 선물
    frames.append(fetch_cbot_soybean_oil(days_back=10))
    # 2. CPO — Trading Economics 우선, FRED 프록시 폴백
    cpo_te = fetch_cpo_te()
    if not cpo_te.empty:
        frames.append(cpo_te)
        print("[정보] CPO: Trading Economics 수집 성공 — FRED 프록시 건너뜀")
    else:
        frames.append(fetch_cpo_proxy_fred())
    # 3. ARS/USD 공식 환율
    frames.append(fetch_ars_usd_bcra(days_back=10))
    # 4. 미국 가뭄 지수
    frames.append(fetch_us_drought_stats())

    frames = [f for f in frames if not f.empty]
    if not frames:
        print("[경고] 상품 가격 데이터: 수집된 항목 없음 — API 키 및 네트워크 확인 필요")
        return

    combined = pd.concat(frames, ignore_index=True)
    out = f"{OUTPUT_DIR}/commodity_data_{today}.parquet"
    combined.to_parquet(out, index=False)
    print(f"[완료] 상품 가격·가뭄 데이터 {len(combined)}건 저장 → {out}")


if __name__ == "__main__":
    run()
