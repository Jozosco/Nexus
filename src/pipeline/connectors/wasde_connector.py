"""
WASDE / USDA 작황 데이터 커넥터 — WBS 1.1.4
수집 대상: WASDE 대두 수급 (USDA FAS OpenData PSD API) · USDA ARMS 생산비용
API 변경 (2025):
  구: https://apps.fas.usda.gov/psdonline/api/psd/exporting  → 404 (폐기)
  신: https://apps.fas.usda.gov/OpenData/api/psd/commodity/{code}/country/all/year/{year}
  인증 방식: 쿼리 파라미터(apiKey) → 요청 헤더(API_KEY)
API 키:
  USDA_FAS_API_KEY  — FAS OpenData 포털(apps.fas.usda.gov/opendatawebV2)에서 발급
  USDA_ARM_API_KEY  — USDA ARMS 생산비용 데이터 (data.ers.usda.gov)
실행 환경: VS Code Web (Azure ML Studio) 또는 GitHub Actions
"""

from __future__ import annotations

import os
import time
from datetime import date

import httpx
import pandas as pd

OUTPUT_DIR = "data/raw"
# USDA FAS OpenData PSD API (2025 신규 엔드포인트)
FAS_OPENDATA_BASE = "https://apps.fas.usda.gov/OpenData/api/psd"
SBO_COMMODITY_CODE = "2222000"  # Soybean Oil (USDA commodity code)
# USDA ARMS (Agricultural Resource Management Survey)
ARMS_BASE = "https://data.ers.usda.gov/api/Data"


def _fetch_fas(url: str, api_key: str = "", max_retries: int = 4) -> list | dict:
    """USDA FAS OpenData API — 헤더 인증 방식 (쿼리 파라미터 아님, MEMORY A-004 참조)."""
    headers: dict[str, str] = {}
    if api_key:
        headers["API_KEY"] = api_key
    delay = 2
    for attempt in range(max_retries):
        try:
            r = httpx.get(url, headers=headers, timeout=30)
            r.raise_for_status()
            return r.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"[오류] USDA FAS API 호출 실패: {e}") from e
            time.sleep(delay)
            delay *= 2
    return []


def _fetch_arms(params: dict, api_key: str = "", max_retries: int = 4) -> list | dict:
    """USDA ERS ARMS API — 쿼리 파라미터 인증."""
    if api_key:
        params = {**params, "api_key": api_key}
    delay = 2
    for attempt in range(max_retries):
        try:
            r = httpx.get(ARMS_BASE, params=params, timeout=30)
            r.raise_for_status()
            return r.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"[오류] USDA ARMS API 호출 실패: {e}") from e
            time.sleep(delay)
            delay *= 2
    return []


def fetch_wasde_soybean_oil(marketing_year: int | None = None) -> pd.DataFrame:
    """USDA FAS OpenData PSD API에서 대두유(Soybean Oil) 수급 데이터 수집.
    URL: {FAS_OPENDATA_BASE}/commodity/{code}/country/all/year/{year}
    키 이름: USDA_FAS_API_KEY (구: USDA_FAS_PSD_API_KEY 하위 호환 유지)
    """
    year = marketing_year or date.today().year
    url = f"{FAS_OPENDATA_BASE}/commodity/{SBO_COMMODITY_CODE}/country/all/year/{year}"
    # 구 키 이름도 fallback으로 지원 (하위 호환)
    api_key = (
        os.environ.get("USDA_FAS_API_KEY", "")
        or os.environ.get("USDA_FAS_PSD_API_KEY", "")
    )
    data = _fetch_fas(url, api_key=api_key)
    if not data:
        print(f"[경고] USDA FAS PSD: {year}년 대두유 데이터 없음")
        return pd.DataFrame()

    rows = []
    for item in data:
        # FAS OpenData 응답 필드명 (구 API와 다를 수 있음)
        attr_id   = item.get("attributeId") or item.get("attributeName", "UNKNOWN")
        country   = item.get("countryName") or item.get("country", "")
        unit_desc = item.get("unitDescription") or item.get("unitDesc", "1000 MT")
        val       = item.get("value")
        rows.append({
            "price_date":     f"{year}-10-01",  # WASDE 마케팅 연도 시작 (10월)
            "source_name":    "USDA_PSD",
            "indicator_code": f"SBO_{attr_id}",
            "country":        country,
            "value":          val,
            "unit":           unit_desc,
        })

    if not rows:
        print(f"[경고] USDA FAS PSD: {year}년 파싱 가능한 레코드 없음")
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["value"]      = pd.to_numeric(df["value"], errors="coerce")
    df["ingested_at"] = pd.Timestamp.utcnow()
    return df.dropna(subset=["value"])


def fetch_wasde_multi_year(start_year: int = 2017) -> pd.DataFrame:
    """2020년부터 현재까지 연도별 WASDE PSD 수급 데이터를 일괄 수집."""
    current_year = date.today().year
    frames = []
    for yr in range(start_year, current_year + 1):
        try:
            df = fetch_wasde_soybean_oil(marketing_year=yr)
            if not df.empty:
                frames.append(df)
        except Exception as e:
            print(f"[경고] USDA FAS PSD {yr}년 수집 실패: {e}")
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def fetch_usda_arms_soybean_costs(year: int | None = None) -> pd.DataFrame:
    """USDA ARMS (Agricultural Resource Management Survey) — 대두 생산비용 수집.
    API: https://data.ers.usda.gov/api/Data
    USDA_ARM_API_KEY 미등록 시 공개 요청 (일부 데이터 제한 있음).
    """
    api_key = os.environ.get("USDA_ARM_API_KEY", "")
    target_year = year or date.today().year - 1  # ARMS는 전년도까지 공개
    params = {
        "year":      target_year,
        "report":    "ARMS",
        "farmtype":  "All Farms",
        "category":  "Soybeans",
        "item":      "Variable costs",
        "state":     "US",
    }
    try:
        data = _fetch_arms(params, api_key=api_key)
    except Exception as e:
        print(f"[경고] USDA ARMS 수집 실패 ({target_year}년): {e}")
        return pd.DataFrame()

    if not data:
        print(f"[경고] USDA ARMS: {target_year}년 대두 생산비용 데이터 없음")
        return pd.DataFrame()

    rows = []
    items = data if isinstance(data, list) else data.get("data", [])
    for item in items:
        val = item.get("value") or item.get("Value")
        rows.append({
            "price_date":     f"{target_year}-01-01",
            "source_name":    "USDA_ARMS",
            "indicator_code": f"SOYBEAN_VARIABLE_COST_{item.get('state', 'US')}",
            "country":        "US",
            "value":          val,
            "unit":           item.get("unit", "USD/acre"),
        })

    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["value"]      = pd.to_numeric(df["value"], errors="coerce")
    df["ingested_at"] = pd.Timestamp.utcnow()
    return df.dropna(subset=["value"])


def run() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y%m%d")

    # HISTORICAL_START_YEAR: 백필 워크플로우가 주입 (미설정 시 기본 2020)
    start_year = int(os.environ.get("HISTORICAL_START_YEAR", "2017"))
    backfill_mode = os.environ.get("BACKFILL_MODE", "").lower() == "true"
    if backfill_mode:
        print(f"[정보] BACKFILL_MODE 활성화 — WASDE PSD {start_year}년~현재 연도별 일괄 수집")
    else:
        print(f"[정보] 일별 갱신 모드 — 현재 마케팅 연도({date.today().year}) 수집")

    frames = []
    psd_df = fetch_wasde_multi_year(start_year=start_year)
    if not psd_df.empty:
        frames.append(psd_df)

    arms_df = fetch_usda_arms_soybean_costs()
    if not arms_df.empty:
        frames.append(arms_df)

    if not frames:
        print("[경고] WASDE: 수집된 데이터 없음")
        return

    combined = pd.concat(frames, ignore_index=True)
    out = f"{OUTPUT_DIR}/crop_data_{today}.parquet"
    combined.to_parquet(out, index=False)
    print(f"[완료] WASDE+ARMS 작황 데이터 {len(combined)}건 저장 → {out}")


if __name__ == "__main__":
    run()
