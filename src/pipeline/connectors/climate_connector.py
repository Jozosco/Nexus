"""
기후·기상이상 커넥터 — WBS 1.1.5 / 1.1.20
수집 대상:
  ENSO 페이즈 (NOAA CPC ONI) · 원산지 기상이상 (OpenWeatherMap)
  Open-Meteo 아카이브 — 12개 주요 생산지역 일별 기후 (2020-01-01~현재)
  ECMWF ERA5 기온·강수 이상 (ECMWF_API_KEY)
범위 제외: NASA POWER 농업기상 → production_connector.py 담당
실행 환경: VS Code Web (Azure ML Studio) 또는 GitHub Actions
"""

from __future__ import annotations

import os
import time
from datetime import date
from typing import Any

import httpx
import pandas as pd

OUTPUT_DIR = "data/raw"
NOAA_ENSO_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
OPEN_METEO_BASE = "https://archive-api.open-meteo.com/v1/archive"

# Open-Meteo 일별 수집 변수 (ERA5-Land 기반, API 키 불필요)
# 주의: direct_radiation_spread/soil_temperature_0_to_7cm_spread 는 비표준 — 표준명으로 교정
OPEN_METEO_VARS: list[str] = [
    "temperature_2m_max",          # 일 최고기온 (°C)
    "temperature_2m_min",          # 일 최저기온 (°C)
    "precipitation_sum",           # 일 강수량 (mm)
    "shortwave_radiation_sum",     # 일 단파복사 합계 (MJ/m²) ← direct_radiation 표준명
    "soil_temperature_0_to_7cm",   # 0–7cm 토양 온도 (°C, ERA5-Land 일평균)
    "soil_moisture_0_to_7cm",      # 0–7cm 토양 수분 (m³/m³, ERA5-Land 일평균)
    "et0_fao_evapotranspiration",  # FAO 기준증발산량 (mm)
    "sunshine_duration",           # 일조시간 (s/day)
]

OPEN_METEO_UNITS: dict[str, str] = {
    "temperature_2m_max":         "°C",
    "temperature_2m_min":         "°C",
    "precipitation_sum":          "mm",
    "shortwave_radiation_sum":    "MJ/m²",
    "soil_temperature_0_to_7cm":  "°C",
    "soil_moisture_0_to_7cm":     "m³/m³",
    "et0_fao_evapotranspiration": "mm",
    "sunshine_duration":          "s",
}

# 12개 주요 생산지역 — soybean_oil_production_climate.md Part 3.2
PRODUCTION_REGIONS: dict[str, dict[str, Any]] = {
    "CN_Heilongjiang": {"lat":  48.0, "lon":  128.0, "country": "China",     "role": "grow"},
    "CN_Shandong":     {"lat":  36.5, "lon":  118.0, "country": "China",     "role": "crush"},
    "CN_Jiangsu":      {"lat":  32.5, "lon":  120.0, "country": "China",     "role": "crush"},
    "US_Illinois":     {"lat":  40.0, "lon":  -89.0, "country": "USA",       "role": "grow_crush"},
    "US_Iowa":         {"lat":  42.0, "lon":  -93.5, "country": "USA",       "role": "grow_crush"},
    "US_Indiana":      {"lat":  40.2, "lon":  -86.1, "country": "USA",       "role": "grow"},
    "BR_MatoGrosso":   {"lat": -13.0, "lon":  -56.0, "country": "Brazil",    "role": "grow_crush"},
    "BR_Parana":       {"lat": -24.5, "lon":  -51.5, "country": "Brazil",    "role": "grow_crush"},
    "BR_MatoGrossodoSul": {"lat": -20.0, "lon": -54.5, "country": "Brazil",  "role": "grow"},
    "AR_Cordoba":      {"lat": -31.4, "lon":  -64.2, "country": "Argentina", "role": "grow"},
    "AR_SantaFe":      {"lat": -33.0, "lon":  -60.6, "country": "Argentina", "role": "crush"},
    "AR_BuenosAires":  {"lat": -36.0, "lon":  -60.0, "country": "Argentina", "role": "grow"},
}

# OpenWeatherMap 현재 기상 수집 (3개 원산지, 레거시)
ORIGIN_COORDS: dict[str, dict[str, float]] = {
    "US_Iowa":        {"lat": 42.0,  "lon": -93.5},
    "BR_Mato_Grosso": {"lat": -12.6, "lon": -55.7},
    "AR_Cordoba":     {"lat": -31.4, "lon": -64.2},
}


def _fetch(url: str, params: dict | None = None, max_retries: int = 4) -> httpx.Response:
    delay = 2
    for attempt in range(max_retries):
        try:
            r = httpx.get(url, params=params or {}, timeout=60)
            r.raise_for_status()
            return r
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"[오류] 기후 API 호출 실패: {e}") from e
            time.sleep(delay)
            delay *= 2


def fetch_enso_index(start_year: int = 2017) -> pd.DataFrame:
    """NOAA CPC ONI (Oceanic Niño Index) 수집 — API 키 불필요.
    파일 형식: SEAS YR ANOM (예: DJF 1950 -1.28)
    """
    r = _fetch(NOAA_ENSO_URL)
    lines = [l for l in r.text.strip().splitlines()
             if not l.startswith("SEAS") and not l.startswith("YR")]
    rows = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 3:
            try:
                season = parts[0]
                year   = int(parts[1])
                oni    = float(parts[2])
                if year < start_year:
                    continue
                rows.append({
                    "price_date":     f"{year}-01-01",
                    "source_name":    "NOAA_CPC",
                    "region_code":    "GLOBAL",
                    "country":        "Global",
                    "indicator_code": "ONI",
                    "season":         season,
                    "value":          oni,
                    "unit":           "°C anomaly",
                    "enso_phase":     "La_Nina" if oni <= -0.5 else ("El_Nino" if oni >= 0.5 else "Neutral"),
                })
            except (ValueError, IndexError):
                continue
    if not rows:
        print(f"[경고] NOAA ONI: {start_year}년 이후 데이터 파싱 실패. NOAA 파일 형식 확인 필요.")
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["ingested_at"] = pd.Timestamp.utcnow()
    return df


def fetch_openmeteo_regional_climate(
    start_date: str = "2017-01-01",
    end_date: str | None = None,
) -> pd.DataFrame:
    """Open-Meteo 아카이브 API — 12개 주요 대두유 생산지역 일별 기후 수집.

    API 키 불필요. ERA5-Land 기반. 비상업적 무료 사용.
    수집 대상 지역: 중국(3) · 미국(3) · 브라질(3) · 아르헨티나(3)
    참고: docs/research_desk/soybean_oil_production_climate.md Part 3.2
    """
    if end_date is None:
        end_date = date.today().isoformat()

    all_rows: list[dict] = []
    ingested_at = pd.Timestamp.utcnow()

    for region_code, info in PRODUCTION_REGIONS.items():
        params = {
            "latitude":  info["lat"],
            "longitude": info["lon"],
            "start_date": start_date,
            "end_date":   end_date,
            "daily": ",".join(OPEN_METEO_VARS),
            "timezone": "auto",
        }
        try:
            r = _fetch(OPEN_METEO_BASE, params=params)
            data = r.json()
            daily = data.get("daily", {})
            times = daily.get("time", [])
            if not times:
                print(f"[경고] {region_code}: Open-Meteo 응답에 'daily.time' 없음")
                continue

            for var in OPEN_METEO_VARS:
                values = daily.get(var, [])
                for t, v in zip(times, values):
                    if v is None:
                        continue
                    all_rows.append({
                        "price_date":     t,
                        "source_name":    "OpenMeteo/ERA5Land",
                        "region_code":    region_code,
                        "country":        info["country"],
                        "indicator_code": var,
                        "value":          float(v),
                        "unit":           OPEN_METEO_UNITS.get(var, ""),
                        "ingested_at":    ingested_at,
                    })
            print(f"[완료] {region_code} ({info['country']}): {len(times)}일 × {len(OPEN_METEO_VARS)}변수")
            time.sleep(0.3)  # 요청 간격 (API 레이트 리밋 준수)
        except Exception as e:
            print(f"[경고] {region_code} 기후 수집 실패: {e}")

    if not all_rows:
        print("[경고] Open-Meteo 지역 기후: 수집된 데이터 없음")
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    df["price_date"] = pd.to_datetime(df["price_date"])
    total_regions = df["region_code"].nunique()
    print(f"[완료] Open-Meteo 지역 기후 총 {len(df):,}건 ({total_regions}개 지역, {start_date}~{end_date})")
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
                "price_date":     today,
                "source_name":    "OpenWeatherMap",
                "region_code":    location,
                "country":        location.split("_")[0],
                "indicator_code": f"TEMP_{location}",
                "value":          data["main"]["temp"],
                "unit":           "°C",
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
            r = httpx.get(
                "https://cds.climate.copernicus.eu/api/v2/resources/reanalysis-era5-land-monthly-means",
                headers={"Authorization": f"Basic {api_key}"},
                timeout=30,
            )
            if r.status_code == 200:
                data = r.json()
                rows.append({
                    "price_date":     today_iso,
                    "source_name":    "ECMWF_ERA5",
                    "region_code":    location,
                    "country":        location.split("_")[0],
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


def run(start_year: int = 2017) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y%m%d")
    frames = []

    # 1. ENSO 지수 (NOAA CPC ONI)
    enso = fetch_enso_index(start_year=start_year)
    if not enso.empty:
        frames.append(enso)

    # 2. Open-Meteo 12개 생산지역 일별 기후 (2020-01-01~오늘)
    regional = fetch_openmeteo_regional_climate(
        start_date=f"{start_year}-01-01",
        end_date=date.today().isoformat(),
    )
    if not regional.empty:
        frames.append(regional)

    # 3. OpenWeatherMap 현재 기상 이상 (API 키 있을 때)
    owm = fetch_weather_anomalies()
    if not owm.empty:
        frames.append(owm)

    # 4. ECMWF ERA5 (API 키 있을 때)
    era5 = fetch_ecmwf_era5()
    if not era5.empty:
        frames.append(era5)

    if not frames:
        print("[경고] 기후 데이터: 수집된 항목 없음")
        return

    combined = pd.concat(frames, ignore_index=True)
    out = f"{OUTPUT_DIR}/climate_data_{today}.parquet"
    combined.to_parquet(out, index=False)
    print(f"[완료] 기후 데이터 {len(combined):,}건 저장 → {out}")


if __name__ == "__main__":
    run()
