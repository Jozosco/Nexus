"""
경제 지표 커넥터 — WBS 1.1.2
수집 대상: Fed 기준금리 (FRED) · 글로벌 CPI (FRED) · KRW/USD 환율 (BOK ECOS) · WTI/Brent 유가 (EIA)
실행 환경: VS Code Web (Azure ML Studio) 또는 GitHub Actions
"""

from __future__ import annotations

import os
import time
from datetime import date, timedelta
from typing import Any

import httpx
import pandas as pd

# ── 상수 ──────────────────────────────────────────────────────────────────────
FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
EIA_BASE  = "https://api.eia.gov/v2/petroleum/pri/spt/data/"
BOK_BASE  = "https://ecos.bok.or.kr/api/StatisticSearch"
OUTPUT_DIR = "data/raw"


def _fetch(url: str, params: dict[str, Any], max_retries: int = 4) -> dict:
    """외부 API 호출 — 지수 백오프 재시도 (MEMORY A-003)."""
    delay = 2
    for attempt in range(max_retries):
        try:
            r = httpx.get(url, params=params, timeout=30)
            r.raise_for_status()
            return r.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"[오류] API 호출 실패 ({url}): {e}") from e
            time.sleep(delay)
            delay *= 2


def fetch_fred_series(series_id: str, start: str, end: str) -> pd.DataFrame:
    """FRED 시계열 데이터 수집."""
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise EnvironmentError("[오류] FRED_API_KEY 환경변수가 설정되지 않았습니다.")
    data = _fetch(FRED_BASE, {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start,
        "observation_end": end,
    })
    obs = data.get("observations", [])
    df = pd.DataFrame(obs)[["date", "value"]]
    df.columns = ["price_date", "value"]
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["source_name"] = "FRED"
    df["indicator_code"] = series_id
    return df.dropna(subset=["value"])


def fetch_eia_brent(start: str, end: str) -> pd.DataFrame:
    """EIA Brent Crude 일간 시계열 수집."""
    api_key = os.environ.get("EIA_API_KEY")
    if not api_key:
        raise EnvironmentError("[오류] EIA_API_KEY 환경변수가 설정되지 않았습니다.")
    data = _fetch(EIA_BASE, {
        "api_key": api_key,
        "frequency": "daily",
        "data[0]": "value",
        "facets[product][]": "EPCBRENT",
        "start": start,
        "end": end,
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "length": 5000,
    })
    rows = data.get("response", {}).get("data", [])
    df = pd.DataFrame(rows)[["period", "value"]]
    df.columns = ["price_date", "value"]
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["source_name"] = "EIA"
    df["indicator_code"] = "BRENT_USD_BBL"
    return df.dropna(subset=["value"])


def fetch_bok_krw_usd(start: str, end: str) -> pd.DataFrame:
    """BOK ECOS KRW/USD 환율 수집. T+2 결제일 오프셋은 소비 측에서 적용 (MEMORY M-002)."""
    api_key = os.environ.get("BOK_ECOS_API_KEY")
    if not api_key:
        raise EnvironmentError("[오류] BOK_ECOS_API_KEY 환경변수가 설정되지 않았습니다.")
    start_fmt = start.replace("-", "")
    end_fmt   = end.replace("-", "")
    url = f"{BOK_BASE}/{api_key}/json/kr/1/5000/731Y001/DD/{start_fmt}/{end_fmt}/0000001"
    data = _fetch(url, {})
    rows = data.get("StatisticSearch", {}).get("row", [])
    df = pd.DataFrame(rows)[["TIME", "DATA_VALUE"]]
    df.columns = ["price_date", "value"]
    df["price_date"] = pd.to_datetime(df["price_date"], format="%Y%m%d")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["source_name"] = "BOK_ECOS"
    df["indicator_code"] = "KRW_USD"
    return df.dropna(subset=["value"])


def run(lookback_days: int = 30) -> None:
    end   = date.today().isoformat()
    start = (date.today() - timedelta(days=lookback_days)).isoformat()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y%m%d")

    frames = []
    frames.append(fetch_fred_series("FEDFUNDS",   start, end))
    frames.append(fetch_fred_series("CPIAUCSL",   start, end))
    frames.append(fetch_eia_brent(start, end))
    frames.append(fetch_bok_krw_usd(start, end))

    combined = pd.concat(frames, ignore_index=True)
    combined["ingested_at"] = pd.Timestamp.utcnow()
    combined["unit"] = ""   # downstream enrichment adds units

    out = f"{OUTPUT_DIR}/economic_indicators_{today}.parquet"
    combined.to_parquet(out, index=False)
    print(f"[완료] 경제 지표 {len(combined)}건 저장 → {out}")


if __name__ == "__main__":
    run()
