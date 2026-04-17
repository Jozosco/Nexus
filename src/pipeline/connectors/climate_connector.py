"""
기후·기상이상 커넥터 — WBS 1.1.5
수집 대상: ENSO 페이즈 (NOAA CPC) · 원산지 기상이상 (OpenWeatherMap)
실행 환경: VS Code Web (Azure ML Studio) 또는 GitHub Actions
"""

from __future__ import annotations

import os
import time
from datetime import date

import httpx
import pandas as pd

OUTPUT_DIR = "data/raw"
NOAA_ENSO_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"

# 대두유 주요 원산지 (MEMORY: soybean oil origin countries)
ORIGIN_COORDS = {
    "US_Iowa":       {"lat": 42.0, "lon": -93.5},
    "BR_Mato_Grosso":{"lat": -12.6, "lon": -55.7},
    "AR_Cordoba":    {"lat": -31.4, "lon": -64.2},
}


def _fetch(url: str, params: dict | None = None, max_retries: int = 4) -> httpx.Response:
    delay = 2
    for attempt in range(max_retries):
        try:
            r = httpx.get(url, params=params or {}, timeout=30)
            r.raise_for_status()
            return r
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"[오류] 기후 API 호출 실패: {e}") from e
            time.sleep(delay)
            delay *= 2


def fetch_enso_index() -> pd.DataFrame:
    """NOAA CPC ONI (Oceanic Niño Index) 수집 — API 키 불필요."""
    r = _fetch(NOAA_ENSO_URL)
    lines = [l for l in r.text.strip().splitlines() if not l.startswith("YR")]
    rows = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 3:
            try:
                year, season, oni = int(parts[0]), parts[1], float(parts[2])
                rows.append({
                    "price_date": f"{year}-01-01",
                    "source_name": "NOAA_CPC",
                    "indicator_code": "ONI",
                    "season": season,
                    "value": oni,
                    "unit": "°C anomaly",
                    "enso_phase": "La_Nina" if oni <= -0.5 else ("El_Nino" if oni >= 0.5 else "Neutral"),
                })
            except (ValueError, IndexError):
                continue
    df = pd.DataFrame(rows)
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["ingested_at"] = pd.Timestamp.utcnow()
    return df


def fetch_weather_anomalies() -> pd.DataFrame:
    """OpenWeatherMap 원산지 기온·강수 이상 수집. 키 미등록 시 빈 DataFrame 반환."""
    api_key = os.environ.get("OPENWEATHERMAP_API_KEY", "")
    if not api_key:
        print("[경고] OPENWEATHERMAP_API_KEY 미등록 — 기상 이상 수집 건너뜀. openweathermap.org에서 무료 키 등록 필요.")
        return pd.DataFrame()

    rows = []
    today = date.today().isoformat()
    for location, coords in ORIGIN_COORDS.items():
        try:
            data = _fetch("https://api.openweathermap.org/data/2.5/weather", {
                "lat": coords["lat"], "lon": coords["lon"],
                "appid": api_key, "units": "metric",
            }).json()
            rows.append({
                "price_date": today,
                "source_name": "OpenWeatherMap",
                "indicator_code": f"TEMP_{location}",
                "value": data["main"]["temp"],
                "unit": "°C",
            })
        except Exception as e:
            print(f"[경고] {location} 기상 데이터 수집 실패: {e}")
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["ingested_at"] = pd.Timestamp.utcnow()
    return df


def run() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y%m%d")
    frames = [fetch_enso_index(), fetch_weather_anomalies()]
    frames = [f for f in frames if not f.empty]
    if not frames:
        print("[경고] 기후 데이터: 수집된 항목 없음")
        return
    combined = pd.concat(frames, ignore_index=True)
    out = f"{OUTPUT_DIR}/climate_data_{today}.parquet"
    combined.to_parquet(out, index=False)
    print(f"[완료] 기후 데이터 {len(combined)}건 저장 → {out}")


if __name__ == "__main__":
    run()
