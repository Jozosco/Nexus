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
from datetime import date, timedelta
from typing import Any

import httpx
import pandas as pd

# as-of 헬퍼 로드 — 스크립트 직접 실행 시 저장소 루트를 경로에 추가
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[3]))
from src.pipeline.asof import attach_asof  # noqa: E402

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

# A-110(F15): NOAA CPC ONI 계절 코드 → 해당 3개월 구간의 **중간월**
# (DJF=12·1·2월의 중간 → 1월). 12개 계절이 12개 월에 1:1 대응한다.
_ONI_SEASON_MONTH: dict[str, int] = {
    "DJF": 1, "JFM": 2, "FMA": 3, "MAM": 4, "AMJ": 5, "MJJ": 6,
    "JJA": 7, "JAS": 8, "ASO": 9, "SON": 10, "OND": 11, "NDJ": 12,
}

# A-110(F3): Open-Meteo archive의 **daily 집계로 제공되지 않는** 변수.
# 이들은 hourly 전용이므로 별도 요청 후 일평균으로 집계해야 한다.
# (구 코드는 daily에 함께 요청 → HTTP 400 → 12개 지역 전부 실패)
HOURLY_ONLY_VARS: list[str] = ["soil_temperature_0_to_7cm", "soil_moisture_0_to_7cm"]

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
                # A-179: oni.ascii.txt 실제 형식은 SEAS YR **TOTAL ANOM** 4열 —
                #   구 코드(A-005)가 parts[2](TOTAL = Niño3.4 절대 SST ~26-29°C)를
                #   ANOM으로 오독 → G1 경보값 29.02 이상값(16차 런 실증)·핵심 8변수 오염.
                #   마지막 열(ANOM) 사용 + 물리 범위(±5) 가드로 형식 변화에도 안전.
                oni    = float(parts[-1])
                if abs(oni) > 5:
                    print(f"[경고] ONI 물리 범위(±5) 밖 값 {oni} ({season} {year}) — "
                          "열 오독 의심, 행 건너뜀")
                    continue
                if year < start_year:
                    continue
                # A-110(F15): 구 코드는 연 12개 계절값을 **전부 1월 1일**에 찍었다.
                #   → 같은 날짜에 12행이 중복 적재되어 as-of join이 임의의 한 값을 집는다.
                #   ENSO_ONI는 D-015 핵심 8변수 중 하나라 오염 영향이 크다.
                #   계절 코드를 **중간월**로 변환한다(DJF→1월, JFM→2월, … NDJ→12월).
                month = _ONI_SEASON_MONTH.get(season)
                if month is None:
                    continue
                rows.append({
                    "price_date":     f"{year}-{month:02d}-01",
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
    ok_regions: list[str] = []
    fail_regions: list[str] = []
    # A-107: Open-Meteo는 daily 집계로 지원되지 않는 변수가 **하나라도** 섞이면 HTTP 400을
    # 반환한다. 전체 변수를 한 번에 요청하는 구조에서는 그 한 개 때문에 **12개 지역 전부**가
    # 실패한다("수집된 데이터 없음"의 잠재 원인). 유효 변수 집합을 1회 자동 확정해 재사용한다.
    # A-110(F3): daily 후보에서 hourly 전용 변수를 애초에 제외한다(400 원인 제거)
    daily_candidates = [v for v in OPEN_METEO_VARS if v not in HOURLY_ONLY_VARS]
    active_vars = list(daily_candidates)

    def _fetch_hourly_soil(lat: float, lon: float) -> dict[str, dict[str, float]]:
        """A-110(F3): 토양 변수는 daily 집계가 없어 **hourly로 받아 일평균**을 만든다.

        구 구조는 이 둘을 daily에 넣어 400을 유발했고, A-107의 프로브는 이를 '미지원'으로
        **조용히 제외**했다 — 하필 대두 작황 설명력이 가장 큰 토양수분이 사라진다.
        시끄러운 실패를 조용한 능력 상실로 바꾸지 않기 위해 별도 경로로 복구한다.
        반환: {변수명: {날짜: 일평균}}
        """
        out: dict[str, dict[str, float]] = {v: {} for v in HOURLY_ONLY_VARS}
        try:
            r = _fetch(OPEN_METEO_BASE, params={
                "latitude": lat, "longitude": lon,
                "start_date": start_date, "end_date": end_date,
                "hourly": ",".join(HOURLY_ONLY_VARS), "timezone": "auto"})
            hourly = (r.json() or {}).get("hourly", {})
            times = hourly.get("time", [])
            if not times:
                return out
            for var in HOURLY_ONLY_VARS:
                vals = hourly.get(var) or []
                acc: dict[str, list[float]] = {}
                for t, v in zip(times, vals):
                    if v is None:
                        continue
                    acc.setdefault(t[:10], []).append(float(v))
                out[var] = {d: sum(xs) / len(xs) for d, xs in acc.items() if xs}
        except Exception as e:
            print(f"[경고] 토양 변수(hourly) 수집 실패: {type(e).__name__}: {str(e)[:70]}")
        return out

    def _probe_vars(lat: float, lon: float) -> list[str]:
        """짧은 구간으로 변수별 지원 여부를 확인해 유효 집합을 반환."""
        probe = {"latitude": lat, "longitude": lon,
                 "start_date": "2024-01-01", "end_date": "2024-01-03", "timezone": "auto"}
        try:
            r = httpx.get(OPEN_METEO_BASE, params={**probe, "daily": ",".join(daily_candidates)},
                          timeout=60)
            if r.status_code == 200:
                return list(daily_candidates)
            print(f"[정보] 전체 변수 요청 거부(HTTP {r.status_code}) — 변수별 개별 확인")
        except Exception as e:
            print(f"[경고] 변수 프로브 실패: {e}")
            return list(daily_candidates)
        good: list[str] = []
        for v in daily_candidates:
            try:
                rr = httpx.get(OPEN_METEO_BASE, params={**probe, "daily": v}, timeout=30)
                (good.append(v) if rr.status_code == 200
                 else print(f"[경고] daily 미지원 변수 제외: {v} (HTTP {rr.status_code})"))
            except Exception:
                print(f"[경고] 변수 확인 실패로 제외: {v}")
            time.sleep(0.2)
        return good

    _first = next(iter(PRODUCTION_REGIONS.values()))
    active_vars = _probe_vars(_first["lat"], _first["lon"])
    if not active_vars:
        print("[오류] 유효한 daily 변수가 없음 — Open-Meteo 사양 변경 확인 필요")
        return pd.DataFrame()
    if len(active_vars) < len(daily_candidates):
        dropped = sorted(set(daily_candidates) - set(active_vars))
        print(f"[경고] daily 유효 변수 {len(active_vars)}/{len(daily_candidates)} — 제외: {dropped} "
              f"(수집 실패로 집계됨 — 조용한 상실 방지)")

    for region_code, info in PRODUCTION_REGIONS.items():
        params = {
            "latitude":  info["lat"],
            "longitude": info["lon"],
            "start_date": start_date,
            "end_date":   end_date,
            "daily": ",".join(active_vars),
            "timezone": "auto",
        }
        try:
            r = _fetch(OPEN_METEO_BASE, params=params)
            data = r.json()
            daily = data.get("daily", {})
            times = daily.get("time", [])
            if not times:
                print(f"[경고] {region_code}: Open-Meteo 응답에 'daily.time' 없음")
                fail_regions.append(region_code)
                continue

            for var in active_vars:
                values = daily.get(var, [])
                for t, v in zip(times, values):
                    if v is None:
                        continue
                    all_rows.append({
                        "price_date":     t,
                        "source_name":    "OpenMeteo/ERA5Land",
                        "region_code":    region_code,
                        "country":        info["country"],
                        # A-172: 지역 축을 코드에 반영 — 구 공유 코드는 동일 일자에
                        #   12개 지역 값이 충돌(mart 하드 실패 48,789건의 대부분)
                        "indicator_code": f"{var}_{region_code}",
                        "value":          float(v),
                        "unit":           OPEN_METEO_UNITS.get(var, ""),
                        "ingested_at":    ingested_at,
                    })
            # A-110(F3): 토양 2종을 hourly→일평균으로 복구해 동일 스키마로 합류
            soil = _fetch_hourly_soil(info["lat"], info["lon"])
            n_soil = 0
            for var, by_date in soil.items():
                for t, v in by_date.items():
                    all_rows.append({
                        "price_date":     t,
                        "source_name":    "OpenMeteo/ERA5Land",
                        "region_code":    region_code,
                        "country":        info["country"],
                        "indicator_code": f"{var}_{region_code}",   # A-172 지역 접미
                        "value":          float(v),
                        "unit":           OPEN_METEO_UNITS.get(var, ""),
                        "ingested_at":    ingested_at,
                    })
                    n_soil += 1

            ok_regions.append(region_code)
            print(f"[완료] {region_code} ({info['country']}): {len(times)}일 × {len(active_vars)}변수"
                  f" + 토양 {n_soil:,}건(hourly→일평균)")
            time.sleep(0.3)  # 요청 간격 (API 레이트 리밋 준수)
        except Exception as e:
            fail_regions.append(region_code)
            print(f"[경고] {region_code} 기후 수집 실패: {e}")

    # A-107: 12개 지역 수집 여부를 **명시 리포트**한다 — 조용한 부분 실패 방지
    total = len(PRODUCTION_REGIONS)
    print(f"[집계] 지역 수집 {len(ok_regions)}/{total}"
          + (f" · 실패: {', '.join(fail_regions)}" if fail_regions else " (전 지역 성공)"))

    if not all_rows:
        print("[경고] Open-Meteo 지역 기후: 수집된 데이터 없음")
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    df["price_date"] = pd.to_datetime(df["price_date"])
    total_regions = df["region_code"].nunique()
    per_region = df.groupby("region_code")["price_date"].nunique().to_dict()
    print(f"[완료] Open-Meteo 지역 기후 총 {len(df):,}건 ({total_regions}/{total}개 지역, "
          f"{start_date}~{end_date})")
    print(f"[커버리지] 지역별 일수: {per_region}")
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


def run(start_year: int | None = None) -> None:
    # A-107: 기본값이 2017로 하드코딩돼 분석창(2010~, M-008)과 불일치했다.
    #        HISTORICAL_START_YEAR를 읽어 백필 워크플로우 지정 연도를 따르게 한다.
    if start_year is None:
        start_year = int(os.environ.get("HISTORICAL_START_YEAR", "2010"))
    # A-110(F4): 그러나 **일별 파이프라인이 매 실행마다 15년치를 재수집**하면
    #   12지역 × 8변수 × 약 6,000일이 되어 Open-Meteo 무료 티어 시간당 한도를 단일
    #   실행으로 초과한다(429 → 후반 지역 실패 → `지역 수집 7/12`가 매일 반복).
    #   백필 모드가 아니면 최근 N일 증분만 수집한다.
    backfill = os.environ.get("BACKFILL_MODE", "").lower() == "true"
    incr_days = int(os.environ.get("CLIMATE_INCREMENTAL_DAYS", "90"))
    if backfill:
        om_start = f"{start_year}-01-01"
        print(f"[C-03] 기후 수집 — 백필 모드: {om_start} ~ 현재")
    else:
        om_start = (date.today() - timedelta(days=incr_days)).isoformat()
        print(f"[C-03] 기후 수집 — 증분 모드: 최근 {incr_days}일({om_start}~). "
              f"전 구간 수집은 BACKFILL_MODE=true로 실행")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y%m%d")
    frames = []

    # 1. ENSO 지수 (NOAA CPC ONI)
    enso = fetch_enso_index(start_year=start_year)
    if not enso.empty:
        frames.append(enso)

    # 2. Open-Meteo 12개 생산지역 일별 기후 (2020-01-01~오늘)
    regional = fetch_openmeteo_regional_climate(
        start_date=om_start,
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
    # D-023: 저장 직전 as-of 5필드 부여 — 규칙은 src/pipeline/asof.py 단일 관리
    combined = attach_asof(combined, source="CLIMATE")
    combined.to_parquet(out, index=False)
    print(f"[완료] 기후 데이터 {len(combined):,}건 저장 → {out}")


if __name__ == "__main__":
    run()
