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

import httpx
import pandas as pd

# as-of 헬퍼 로드 — 스크립트 직접 실행 시 저장소 루트를 경로에 추가
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[3]))
from src.pipeline.asof import attach_asof  # noqa: E402

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

def _yf_session():
    """curl_cffi 브라우저 임퍼소네이션 세션 — Yahoo 레이트리밋/차단 완화 (A-071).
    원인①: yfinance 기본 requests가 Yahoo에 429(레이트리밋)·차단 유발.
    해결: curl_cffi로 실제 브라우저 TLS 지문(impersonate) 모방 → 429 대폭 감소.
    미설치 시 None 반환(기본 세션 사용).
    """
    try:
        from curl_cffi import requests as cffi_requests
        return cffi_requests.Session(impersonate="chrome")
    except ImportError:
        print("[정보] curl_cffi 미설치 — 기본 세션 사용(429 위험). pip install curl_cffi 권장")
        return None


def fetch_bo_futures_yfinance(days_back: int = 10) -> pd.DataFrame:
    """CBOT BO=F 일간 OHLCV — yfinance + curl_cffi 세션 (A-071).

    미수집 원인·해결(조정자 확인):
      ① 레이트리밋(429) → curl_cffi 브라우저 임퍼소네이션 세션 사용(하단 _yf_session).
      ② 사내 IP 방화벽 → yfinance 요청 도메인(query1/2.finance.yahoo.com) 승인 요청 필요
         (담당자 방화벽 허용). Actions runner는 사내망 밖이라 ②는 해당 없음.
    """
    try:
        import yfinance as yf
    except ImportError:
        print("[경고] yfinance 미설치 — BO=F yfinance 건너뜀 (Nasdaq Data Link 폴백 사용)")
        return pd.DataFrame()

    session = _yf_session()
    delay = 10
    for attempt in range(3):
        try:
            ticker = yf.Ticker("BO=F", session=session) if session else yf.Ticker("BO=F")
            df = ticker.history(period=f"{days_back}d", auto_adjust=True)
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

# A-144: /estadisticas/v3.0/cotizaciones/{date} 404 — 엔드포인트 개편 추정.
#        신규 estadisticascambiarias/v1.0 (기간 조회) 우선, 구 v3.0 폴백 체인.
def _bcra_extract_rate(entry: dict) -> float | None:
    """BCRA 응답 상세 항목에서 환율 숫자 필드 유연 추출 (A-144).

    알려진 필드(tipoCotizacion/tipoPase) 우선, 없으면 첫 양수 숫자 필드 자동 탐지.
    """
    for key in ("tipoCotizacion", "tipoPase"):
        v = entry.get(key)
        if isinstance(v, (int, float)) and v > 0:
            return float(v)
    for v in entry.values():
        if isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0:
            return float(v)
    return None


def _fetch_bcra_v1_range(start: date, end: date) -> list[dict]:
    """BCRA estadisticascambiarias v1.0 — USD 기간 조회 (단일 호출)."""
    url = (
        "https://api.bcra.gob.ar/estadisticascambiarias/v1.0/Cotizaciones/USD"
        f"?fechadesde={start.isoformat()}&fechahasta={end.isoformat()}"
    )
    r = _get(url, headers={"Accept": "application/json"}, max_retries=2)
    data = r.json()
    results = data.get("results", data if isinstance(data, list) else [])
    rows: list[dict] = []
    for item in results:
        fecha = item.get("fecha") or item.get("fechaCotizacion")
        detalles = item.get("detalle", [item])   # detalle 없으면 항목 자체를 상세로 간주
        for entry in detalles:
            rate = _bcra_extract_rate(entry)
            if fecha and rate is not None:
                rows.append({
                    "price_date":     fecha,
                    "source_name":    "BCRA_OFICIAL",
                    "indicator_code": "ARS_USD_OFICIAL",
                    "value":          rate,
                    "unit":           "ARS/USD",
                })
                break
    if rows:
        print(f"[정보] BCRA 성공 URL: {url} ({len(rows)}건)")
    return rows


def fetch_ars_usd_bcra(days_back: int = 10) -> pd.DataFrame:
    """
    아르헨티나 중앙은행(BCRA) 공식 ARS/USD 환율 (A-144: 후보 엔드포인트 체인).
    ① estadisticascambiarias/v1.0/Cotizaciones/USD (기간 조회, 신규)
    ② estadisticas/v3.0/cotizaciones/{date} (일별, 구 — 폴백)
    """
    start = date.today() - timedelta(days=days_back)
    rows: list[dict] = []

    # ① v1.0 기간 조회 (단일 호출)
    try:
        rows = _fetch_bcra_v1_range(start, date.today())
    except Exception as e:
        print(f"[경고] BCRA v1.0 기간 조회 실패: {e} — 구 v3.0 폴백 시도")

    # ② 구 v3.0 일별 폴백
    if not rows:
        v3_logged = False
        for d in range(days_back):
            target = date.today() - timedelta(days=d)
            if target.weekday() >= 5:  # 주말 건너뜀
                continue
            url = f"https://api.bcra.gob.ar/estadisticas/v3.0/cotizaciones/{target.isoformat()}"
            try:
                r = _get(url, headers={"Accept": "application/json"}, max_retries=2)
                data = r.json()
                for entry in data.get("results", []):
                    if entry.get("codigoMoneda") == "USD":
                        rate = _bcra_extract_rate(entry)
                        if rate is not None:
                            rows.append({
                                "price_date":     target.isoformat(),
                                "source_name":    "BCRA_OFICIAL",
                                "indicator_code": "ARS_USD_OFICIAL",
                                "value":          rate,
                                "unit":           "ARS/USD",
                            })
                            if not v3_logged:
                                print(f"[정보] BCRA 성공 URL(폴백 v3.0): {url}")
                                v3_logged = True
                        break
            except Exception as e:
                print(f"[경고] BCRA ARS/USD {target}: {e}")

    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["price_date"] = pd.to_datetime(df["price_date"], format="mixed", errors="coerce")
    df = df.dropna(subset=["price_date"])
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
    # D-023: 저장 직전 as-of 5필드 부여 — 규칙은 src/pipeline/asof.py 단일 관리
    combined = attach_asof(combined, source="COMMODITY")
    combined.to_parquet(out, index=False)
    print(f"[완료] 상품 가격·가뭄 데이터 {len(combined)}건 저장 → {out}")


if __name__ == "__main__":
    run()
