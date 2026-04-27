"""
대두유 원산지별 생산량·농업기상 커넥터 — WBS 1.1.x (신규)
수집 대상:
  - 미국 주별 대두 생산량: USDA NASS QuickStats (API 키)
  - 글로벌 대두유 수급: USDA FAS PSD (API 키) + FAOSTAT (공개)
  - 아르헨티나 지역 농업통계: datos.gob.ar / INDEC (공개)
  - 원산지 농업기상: NASA POWER API (공개, 키 불필요)
  - 원산지·지역 생산 컨텍스트: Perplexity Pro (실시간)
실행 환경: VS Code Web (Azure ML Studio) 또는 GitHub Actions
참고: github.com/kdmayer/nasa-power-api, github.com/datosgobar, github.com/WUR-AI/AgML-CY-Bench
"""

from __future__ import annotations

import os
import re
import time
from datetime import date, timedelta

import httpx
import pandas as pd
from openai import OpenAI

OUTPUT_DIR = "data/raw"
PERPLEXITY_MODEL = "sonar-pro"  # MEMORY L-007

# 주요 원산지 좌표 (NASA POWER / 기상 공통)
ORIGIN_COORDS = {
    "US_Iowa":        {"lat": 42.0,  "lon": -93.5,  "country": "US"},
    "US_Illinois":    {"lat": 40.0,  "lon": -89.2,  "country": "US"},
    "BR_Mato_Grosso": {"lat": -12.6, "lon": -55.7,  "country": "BR"},
    "BR_Parana":      {"lat": -24.7, "lon": -51.7,  "country": "BR"},
    "AR_Cordoba":     {"lat": -31.4, "lon": -64.2,  "country": "AR"},
    "AR_Santa_Fe":    {"lat": -31.7, "lon": -60.7,  "country": "AR"},
}

NASS_BASE    = "https://quickstats.nass.usda.gov/api/api_GET/"
FAS_PSD_API  = "https://apps.fas.usda.gov/psdonline/api/psd/exporting"
FAOSTAT_BASE = "https://fenixservices.fao.org/faostat/api/v1/en/data/QCL"
INDEC_API    = "https://apis.datos.gob.ar/series/api/series/"
NASA_POWER   = "https://power.larc.nasa.gov/api/temporal/monthly/point"


def _get(url: str, params: dict | None = None, max_retries: int = 4) -> httpx.Response:
    delay = 2
    for attempt in range(max_retries):
        try:
            r = httpx.get(url, params=params or {}, timeout=60)
            r.raise_for_status()
            return r
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"[오류] API 호출 실패 ({url}): {e}") from e
            time.sleep(delay)
            delay *= 2


def fetch_usda_nass_soybeans(year: int | None = None) -> pd.DataFrame:
    """USDA NASS QuickStats — 미국 주별 대두 생산량 (USDA_NASS_QUICKSTATS_API_KEY 필요)."""
    api_key = os.environ.get("USDA_NASS_QUICKSTATS_API_KEY", "")
    if not api_key:
        print("[경고] USDA_NASS_QUICKSTATS_API_KEY 미등록 — NASS 수집 건너뜀")
        return pd.DataFrame()
    yr = year or date.today().year
    try:
        r = _get(NASS_BASE, {
            "key": api_key,
            "commodity_desc": "SOYBEANS",
            "statisticcat_desc": "PRODUCTION",
            "agg_level_desc": "STATE",
            "year__GE": yr - 3,
            "unit_desc": "BU",
            "format": "JSON",
        })
        items = r.json().get("data", [])
        rows = []
        for it in items:
            try:
                rows.append({
                    "price_date": f"{it['year']}-10-01",
                    "source_name": "USDA_NASS",
                    "indicator_code": "SOYBEAN_PROD_BU",
                    "region": f"US_{it.get('state_alpha', 'UNKNOWN')}",
                    "country": "US",
                    "value": float(it["Value"].replace(",", "")),
                    "unit": "Bushels",
                })
            except (ValueError, KeyError):
                continue
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        df["price_date"] = pd.to_datetime(df["price_date"])
        df["ingested_at"] = pd.Timestamp.utcnow()
        return df
    except Exception as e:
        print(f"[경고] USDA NASS 수집 실패: {e}")
        return pd.DataFrame()


def fetch_usda_fas_global(year: int | None = None) -> pd.DataFrame:
    """USDA FAS PSD — 국가별 대두유 수급 (USDA_FAS_PSD_API_KEY 사용)."""
    api_key = os.environ.get("USDA_FAS_PSD_API_KEY", "")
    yr = year or date.today().year
    params: dict = {"commodityCode": "2222000", "marketingYear": yr}
    if api_key:
        params["apiKey"] = api_key
    try:
        r = _get(FAS_PSD_API, params)
        data = r.json()
        if not data:
            print(f"[경고] USDA FAS PSD: {yr}년 데이터 없음")
            return pd.DataFrame()
        rows = []
        for it in data:
            try:
                rows.append({
                    "price_date": f"{yr}-10-01",
                    "source_name": "USDA_FAS_PSD",
                    "indicator_code": f"SBO_{it.get('attributeId', 'UNKNOWN')}",
                    "country": it.get("countryName", ""),
                    "value": float(it.get("value") or 0),
                    "unit": it.get("unitDesc", "1000 MT"),
                })
            except (ValueError, KeyError):
                continue
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        df["price_date"] = pd.to_datetime(df["price_date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df["ingested_at"] = pd.Timestamp.utcnow()
        return df.dropna(subset=["value"])
    except Exception as e:
        print(f"[경고] USDA FAS PSD 수집 실패: {e}")
        return pd.DataFrame()


def fetch_faostat_soybeans(year_start: int = 2018) -> pd.DataFrame:
    """FAOSTAT — 국가별 대두 생산량 시계열 (공개, 키 불필요). AgML-CY-Bench 벤치마크 데이터소스."""
    try:
        r = _get(FAOSTAT_BASE, {
            "item": "2555",       # Soybeans
            "element": "5510",   # Production (tonnes)
            "year": ",".join(str(y) for y in range(year_start, date.today().year + 1)),
            "area": "9,21,32,138,231",  # Argentina, Brazil, China, Paraguay, USA
            "outputType": "csv",
        })
        # FAOSTAT CSV 파싱
        from io import StringIO
        df_raw = pd.read_csv(StringIO(r.text))
        df_raw.columns = [c.strip() for c in df_raw.columns]
        rows = []
        for _, row in df_raw.iterrows():
            try:
                rows.append({
                    "price_date": f"{int(row['Year'])}-10-01",
                    "source_name": "FAOSTAT",
                    "indicator_code": "SOYBEAN_PROD_TONNE",
                    "country": str(row.get("Area", "")),
                    "value": float(str(row.get("Value", "0")).replace(",", "")),
                    "unit": "Tonnes",
                })
            except (ValueError, KeyError):
                continue
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        df["price_date"] = pd.to_datetime(df["price_date"])
        df["ingested_at"] = pd.Timestamp.utcnow()
        return df.dropna(subset=["value"])
    except Exception as e:
        print(f"[경고] FAOSTAT 수집 실패: {e}")
        return pd.DataFrame()


def fetch_argentina_indec() -> pd.DataFrame:
    """Argentina INDEC 대두 생산 시계열 — datos.gob.ar 공개 API.
    참고: github.com/datosgobar (Argentina Open Data)
    """
    # INDEC 농업통계 시계열 ID (대두 생산량 및 재배면적)
    SERIES_IDS = {
        "170.1_SOJA_PRODUCCI_0_A_20": ("SOYBEAN_PROD_TONNE_AR", "Tonnes"),
        "170.1_SOJA_SUPERFICI_0_A_20": ("SOYBEAN_AREA_HA_AR", "Hectares"),
    }
    rows = []
    for series_id, (code, unit) in SERIES_IDS.items():
        try:
            r = _get(INDEC_API, {
                "ids": series_id,
                "limit": 100,
                "sort": "desc",
                "format": "json",
            })
            data = r.json()
            for entry in data.get("data", []):
                try:
                    rows.append({
                        "price_date": entry[0],
                        "source_name": "INDEC_AR",
                        "indicator_code": code,
                        "country": "Argentina",
                        "value": float(entry[1]),
                        "unit": unit,
                    })
                except (ValueError, IndexError):
                    continue
        except Exception as e:
            print(f"[경고] INDEC {series_id} 수집 실패: {e}")
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["ingested_at"] = pd.Timestamp.utcnow()
    return df


def fetch_nasa_power_agromet(days_back: int = 30) -> pd.DataFrame:
    """NASA POWER API — 원산지별 월별 농업기상 (기온·강수·습도).
    참고: github.com/kdmayer/nasa-power-api | 키 불필요 | community=AG
    """
    end   = date.today()
    start = end.replace(day=1) - timedelta(days=30 * 3)  # 최근 3개월
    rows = []
    for location, coord in ORIGIN_COORDS.items():
        try:
            r = _get(NASA_POWER, {
                "start":      start.strftime("%Y%m"),
                "end":        end.strftime("%Y%m"),
                "latitude":   coord["lat"],
                "longitude":  coord["lon"],
                "community":  "AG",
                "parameters": "T2M,PRECTOTCORR,RH2M",
                "format":     "JSON",
                "user":       "nexus_project",
                "header":     "true",
            })
            payload = r.json()
            props   = payload.get("properties", {}).get("parameter", {})
            for ym, t2m_val in props.get("T2M", {}).items():
                precip = props.get("PRECTOTCORR", {}).get(ym, None)
                rh2m   = props.get("RH2M", {}).get(ym, None)
                try:
                    rows.append({
                        "price_date":     f"{ym[:4]}-{ym[4:]}-01",
                        "source_name":    "NASA_POWER",
                        "indicator_code": f"T2M_{location}",
                        "region":         location,
                        "country":        coord["country"],
                        "value":          float(t2m_val),
                        "unit":           "°C",
                    })
                    if precip is not None:
                        rows.append({
                            "price_date":     f"{ym[:4]}-{ym[4:]}-01",
                            "source_name":    "NASA_POWER",
                            "indicator_code": f"PRECIP_{location}",
                            "region":         location,
                            "country":        coord["country"],
                            "value":          float(precip),
                            "unit":           "mm/day",
                        })
                except (ValueError, TypeError):
                    continue
        except Exception as e:
            print(f"[경고] NASA POWER {location} 수집 실패: {e}")
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["ingested_at"] = pd.Timestamp.utcnow()
    return df


def fetch_perplexity_production_regions() -> pd.DataFrame:
    """Perplexity Pro — 원산지별 생산 컨텍스트 (지역별 작황 등급, 생산량 가이던스)."""
    api_key = os.environ.get("PERPLEXITY_API_KEY", "")
    if not api_key:
        print("[경고] PERPLEXITY_API_KEY 미등록 — 생산지역 컨텍스트 건너뜀")
        return pd.DataFrame()
    client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
    prompt = (
        "Provide the latest soybean production estimates for major regions: "
        "U.S. (Iowa, Illinois), Brazil (Mato Grosso, Paraná), Argentina (Córdoba, Santa Fe). "
        "For each region: crop condition rating (Excellent/Good/Fair/Poor %) and "
        "latest production estimate in million metric tonnes. "
        "Format: REGION: [name] | CONDITION: [%Good+Excellent] | PRODUCTION: [MMT] | DATE: [date]"
    )
    try:
        r = client.chat.completions.create(
            model=PERPLEXITY_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        text = r.choices[0].message.content
        today = date.today().isoformat()
        rows = []
        for match in re.finditer(
            r"REGION:\s*([^|]+)\|[^|]*CONDITION:\s*([0-9]+)[^|]*\|[^|]*PRODUCTION:\s*([0-9.]+)",
            text, re.IGNORECASE
        ):
            region, condition, production = match.groups()
            rows.append({
                "price_date":     today,
                "source_name":    "Perplexity/USDA_NASS_proxy",
                "indicator_code": f"CROP_CONDITION_{region.strip().replace(' ', '_')}",
                "region":         region.strip(),
                "country":        region.strip()[:2],
                "value":          float(condition),
                "unit":           "% Good+Excellent",
            })
            rows.append({
                "price_date":     today,
                "source_name":    "Perplexity/USDA_NASS_proxy",
                "indicator_code": f"PROD_ESTIMATE_{region.strip().replace(' ', '_')}",
                "region":         region.strip(),
                "country":        region.strip()[:2],
                "value":          float(production),
                "unit":           "MMT",
            })
        if not rows:
            print(f"[경고] Perplexity 생산지역 파싱 실패. 원문: {text[:200]}")
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        df["price_date"] = pd.to_datetime(df["price_date"])
        df["ingested_at"] = pd.Timestamp.utcnow()
        return df
    except Exception as e:
        print(f"[경고] Perplexity 생산지역 수집 실패: {e}")
        return pd.DataFrame()


def run() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y%m%d")
    frames = [
        fetch_usda_nass_soybeans(),
        fetch_usda_fas_global(),
        fetch_faostat_soybeans(),
        fetch_argentina_indec(),
        fetch_nasa_power_agromet(),
        fetch_perplexity_production_regions(),
    ]
    frames = [f for f in frames if not f.empty]
    if not frames:
        print("[경고] 생산량 데이터: 수집된 항목 없음")
        return
    combined = pd.concat(frames, ignore_index=True)
    out = f"{OUTPUT_DIR}/production_data_{today}.parquet"
    combined.to_parquet(out, index=False)
    print(f"[완료] 원산지 생산량 데이터 {len(combined)}건 저장 → {out}")


if __name__ == "__main__":
    run()
