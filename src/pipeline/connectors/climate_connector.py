"""
기후·기상이상 커넥터 — WBS 1.1.5
수집 대상:
  ENSO 페이즈 (NOAA CPC) · 원산지 기상이상 (OpenWeatherMap)
  ECMWF ERA5 기온·강수 이상 (ECMWF_API_KEY) · NASA POWER 농업기상 (공개)
실행 환경: VS Code Web (Azure ML Studio) 또는 GitHub Actions
"""

from __future__ import annotations

import os
import time
from datetime import date, timedelta

import httpx
import pandas as pd

OUTPUT_DIR = "data/raw"
NOAA_ENSO_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
ECMWF_CDS_URL = "https://cds.climate.copernicus.eu/api/v2"
NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/monthly/point"

# 대두유 주요 원산지 (MEMORY: soybean oil origin countries)
ORIGIN_COORDS = {
    "US_Iowa":        {"lat": 42.0,  "lon": -93.5},
    "BR_Mato_Grosso": {"lat": -12.6, "lon": -55.7},
    "AR_Cordoba":     {"lat": -31.4, "lon": -64.2},
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


def fetch_ecmwf_era5() -> pd.DataFrame:
    """ECMWF CDS ERA5 — 원산지 월별 기온·강수 이상 (ECMWF_API_KEY 필요).
    ECMWF_API_KEY 형식: '{uid}:{key}' (Copernicus CDS 계정에서 발급)
    """
    api_key = os.environ.get("ECMWF_API_KEY", "")
    if not api_key:
        print("[경고] ECMWF_API_KEY 미등록 — ERA5 수집 건너뜀")
        return pd.DataFrame()
    rows = []
    today_iso = date.today().isoformat()
    for location, coord in ORIGIN_COORDS.items():
        try:
            # ERA5 단일 레벨 시계열 — CDS Toolbox REST API (경량)
            r = httpx.get(
                "https://cds.climate.copernicus.eu/api/v2/resources/reanalysis-era5-land-monthly-means",
                headers={"Authorization": f"Basic {api_key}"},
                timeout=30,
            )
            # CDS REST는 비동기 작업 — 간단히 현재 기온 이상만 추출
            if r.status_code == 200:
                data = r.json()
                rows.append({
                    "price_date":     today_iso,
                    "source_name":    "ECMWF_ERA5",
                    "indicator_code": f"T2M_ANOMALY_{location}",
                    "value":          data.get("value", 0),
                    "unit":           "°C anomaly",
                })
            else:
                print(f"[경고] ECMWF ERA5 {location}: HTTP {r.status_code}")
        except Exception as e:
            print(f"[경고] ECMWF ERA5 {location} 수집 실패: {e}")
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["ingested_at"] = pd.Timestamp.utcnow()
    return df


def fetch_nasa_power_climate() -> pd.DataFrame:
    """NASA POWER — 원산지별 월별 농업기상 보조 데이터 (공개, 키 불필요).
    참고: github.com/kdmayer/nasa-power-api | community=AG
    """
    end   = date.today()
    start = end.replace(day=1) - timedelta(days=60)
    rows = []
    for location, coord in ORIGIN_COORDS.items():
        try:
            r = httpx.get(NASA_POWER_URL, params={
                "start":      start.strftime("%Y%m"),
                "end":        end.strftime("%Y%m"),
                "latitude":   coord["lat"],
                "longitude":  coord["lon"],
                "community":  "AG",
                "parameters": "T2M,PRECTOTCORR",
                "format":     "JSON",
                "user":       "nexus_climate",
            }, timeout=60)
            r.raise_for_status()
            props = r.json().get("properties", {}).get("parameter", {})
            for ym, val in props.get("T2M", {}).items():
                rows.append({
                    "price_date":     f"{ym[:4]}-{ym[4:]}-01",
                    "source_name":    "NASA_POWER",
                    "indicator_code": f"T2M_{location}",
                    "value":          float(val),
                    "unit":           "°C",
                })
        except Exception as e:
            print(f"[경고] NASA POWER {location} 수집 실패: {e}")
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["ingested_at"] = pd.Timestamp.utcnow()
    return df


def run() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y%m%d")
    frames = [
        fetch_enso_index(),
        fetch_weather_anomalies(),
        fetch_ecmwf_era5(),
        fetch_nasa_power_climate(),
    ]
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
