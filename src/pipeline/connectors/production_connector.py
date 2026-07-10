"""
대두유 원산지별 생산량·농업기상 커넥터 — WBS 1.1.7
수집 대상:
  - 미국 주별 대두 생산량: USDA NASS QuickStats (API 키)
  - 국가별 대두 생산 시계열: FAOSTAT (공개) — AgML-CY-Bench 데이터소스
  - 아르헨티나 지역 농업통계: datos.gob.ar / INDEC (공개)
  - 원산지 농업기상 (6개 지역): NASA POWER API (공개, 키 불필요) — 기온·강수·습도
  - 원산지·지역 생산 컨텍스트: Perplexity Pro (실시간 작황 등급·생산량 가이던스)
범위 제외: USDA FAS PSD 글로벌 수급 → wasde_connector.py 담당 (중복 방지)
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
    """USDA NASS QuickStats — 미국 주별 대두 생산량.
    키 이름: USDA_NASS_QUICKSTATS_API_KEY 또는 USDA_API_KEY (하위 호환 fallback).
    """
    api_key = (
        os.environ.get("USDA_NASS_QUICKSTATS_API_KEY", "")
        or os.environ.get("USDA_API_KEY", "")
    )
    if not api_key:
        print("[경고] USDA_NASS_QUICKSTATS_API_KEY / USDA_API_KEY 미등록 — NASS 수집 건너뜀")
        return pd.DataFrame()
    yr = year or date.today().year
    try:
        r = _get(NASS_BASE, {
            "key": api_key,
            "commodity_desc": "SOYBEANS",
            "statisticcat_desc": "PRODUCTION",
            "agg_level_desc": "STATE",
            "year__GE": 2017,   # 수집 범위 표준화: 2017년 이후
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


def fetch_faostat_soybeans(year_start: int = 2017) -> pd.DataFrame:
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


# NASA POWER 파라미터 선별 (Standard Resolution · community=AG · A-065)
# C-03·P1-01·P1-03 협의: 대두 수율 구동 인자(열스트레스·수분·일사·토양수분)만 선별.
# High Resolution은 2024년만 제공 → 9개년 히스토리 부적합. Standard(월별, ~현재)로 확정.
# 근거 문서: docs/research_desk/realtime_data_acquisition/nasa_power_selection_2026_07_10.md
NASA_POWER_PARAMS: dict[str, tuple[str, str]] = {
    "T2M":               ("°C",          "기온(2m)"),
    "T2M_MAX":           ("°C",          "최고기온(열스트레스)"),
    "T2M_MIN":           ("°C",          "최저기온(냉해)"),
    "PRECTOTCORR":       ("mm/day",      "강수(수분 공급)"),
    "RH2M":              ("%",           "상대습도(병해·증산)"),
    "ALLSKY_SFC_SW_DWN": ("MJ/m^2/day",  "전천 일사(광합성 에너지)"),
    "ALLSKY_SFC_PAR_TOT":("W/m^2",       "광합성유효복사 PAR"),
    "GWETROOT":          ("0-1",         "근권 토양수분(가뭄)"),
    "GWETTOP":           ("0-1",         "표층 토양수분"),
}


def fetch_nasa_power_agromet(start_date: date | None = None) -> pd.DataFrame:
    """NASA POWER API — 원산지별 월별 농업기상 (선별 9종 파라미터).
    참고: github.com/kdmayer/nasa-power-api | 키 불필요 | community=AG (Agroclimatology)
    수집 범위: start_date(기본 2017-01-01)부터 현재까지.
    선별 근거: 대두 수율 구동 = 열(T2M/MAX/MIN)·수분(강수/토양수분)·일사(SW/PAR)·습도(A-065).
    """
    end   = date.today()
    start = start_date if start_date else date(2017, 1, 1)
    param_csv = ",".join(NASA_POWER_PARAMS)
    rows = []
    for location, coord in ORIGIN_COORDS.items():
        try:
            r = _get(NASA_POWER, {
                "start":      start.strftime("%Y%m"),
                "end":        end.strftime("%Y%m"),
                "latitude":   coord["lat"],
                "longitude":  coord["lon"],
                "community":  "AG",
                "parameters": param_csv,
                "format":     "JSON",
                "user":       "nexus_project",
                "header":     "true",
            })
            payload = r.json()
            props   = payload.get("properties", {}).get("parameter", {})
            for param, (unit, _desc) in NASA_POWER_PARAMS.items():
                series = props.get(param, {})
                for ym, val in series.items():
                    if val is None or float(val) <= -999:   # POWER 결측 센티넬
                        continue
                    try:
                        rows.append({
                            "price_date":     f"{ym[:4]}-{ym[4:]}-01",
                            "source_name":    "NASA_POWER",
                            "indicator_code": f"{param}_{location}",
                            "region":         location,
                            "country":        coord["country"],
                            "value":          float(val),
                            "unit":           unit,
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


def fetch_fas_esr_soybean_oil(start_year: int = 2017) -> pd.DataFrame:
    """USDA FAS Export Sales Reporting (ESR) — 대두유 수출 판매량 (국가별·마케팅연도별).

    검증된 엔드포인트 (2026-05-13 사용자 확인):
      GET https://api.fas.usda.gov/api/esr/exports/commodityCode/{code}/countryCode/{cc}/marketYear/{yr}
      Header: X-Api-Key: {USDA_FAS_API_KEY}

    수집 대상:
      상품: 902(대두유), 801(대두) — 한국 수입 관련 주요 국가
      국가: 미국(5800=Korea 수출국 관점이 아닌 수입국으로 한국 조회 방식과 상이)
            → 대두유 주요 수출국: 아르헨티나(3570), 브라질(3510), 미국(5700=미국→한국X)

    주의: FAS ESR의 countryCode는 수입국 기준 (수출 목적지).
          한국으로의 수출: countryCode=5800 (Kor, Rep).
    """
    # 올바른 v2 API (api.fas.usda.gov — 사용자 확인)
    FAS_ESR_V2_BASE = "https://api.fas.usda.gov/api/esr/exports"
    api_key = (
        os.environ.get("USDA_FAS_API_KEY", "")
        or os.environ.get("USDA_FAS_PSD_API_KEY", "")
    )

    # 한국(5800)으로 수출하는 주요 대두유 관련 상품
    COMMODITY_CODES = {
        "902":  "SBO_EXPORT",      # Soybean Oil
        "801":  "SOYBEAN_EXPORT",  # Soybeans (원료 수급 맥락)
    }
    # 한국으로의 대두유 주요 수출국 → FAS ESR countryCode=5800(한국)으로 조회
    # 또는 대두유 주요 원산지 국가 코드로 수출 현황 파악
    DEST_KOREA = "5800"

    rows: list[dict] = []
    headers = {"accept": "application/json"}
    if api_key:
        headers["X-Api-Key"] = api_key

    for yr in range(start_year, date.today().year + 1):
        for cmd_code, indicator_prefix in COMMODITY_CODES.items():
            url = f"{FAS_ESR_V2_BASE}/commodityCode/{cmd_code}/countryCode/{DEST_KOREA}/marketYear/{yr}"
            try:
                r = httpx.get(url, headers=headers, timeout=30)
                if r.status_code == 404:
                    continue
                r.raise_for_status()
                data = r.json()
                if not data:
                    continue
                entries = data if isinstance(data, list) else data.get("data", [])
                for entry in entries:
                    try:
                        wk_date = str(entry.get("weeklyExportSalesDate", ""))[:10]
                        rows.append({
                            "price_date":     wk_date,
                            "source_name":    "USDA_FAS_ESR",
                            "indicator_code": f"{indicator_prefix}_TO_KR_{yr}",
                            "country":        "KOR",
                            "value":          float(entry.get("weekSales", 0) or 0),
                            "unit":           "MT",
                            "market_year":    yr,
                        })
                    except (ValueError, TypeError):
                        continue
                print(f"[정보] FAS ESR {cmd_code} → 한국 {yr}: {len(entries)}건")
            except Exception as e:
                print(f"[경고] FAS ESR {cmd_code}/{yr}: {e}")
            time.sleep(0.3)  # API 레이트 리밋 준수

    if not rows:
        print("[경고] FAS ESR: 수집된 데이터 없음 — USDA_FAS_API_KEY 등록 또는 엔드포인트 확인")
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["price_date"] = pd.to_datetime(df["price_date"], errors="coerce")
    df["ingested_at"] = pd.Timestamp.utcnow()
    return df.dropna(subset=["value"])


def run() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y%m%d")
    frames = [
        fetch_usda_nass_soybeans(),                    # year__GE=2020
        fetch_faostat_soybeans(),                      # year_start=2020
        fetch_argentina_indec(),
        fetch_nasa_power_agromet(),                    # start_date=2020-01-01
        fetch_perplexity_production_regions(),
        fetch_fas_esr_soybean_oil(),
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
