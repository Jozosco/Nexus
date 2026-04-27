"""
WASDE / USDA 작황 데이터 커넥터 — WBS 1.1.4
수집 대상: WASDE 대두 수급 (USDA FAS PSD API) · 원산지별 작황
API: USDA_FAS_PSD_API_KEY 등록 시 인증 모드, 미등록 시 공개 엔드포인트
실행 환경: VS Code Web (Azure ML Studio) 또는 GitHub Actions
"""

from __future__ import annotations

import os
import time
from datetime import date

import httpx
import pandas as pd

OUTPUT_DIR = "data/raw"
PSD_API  = "https://apps.fas.usda.gov/psdonline/api/psd/exporting"


def _fetch(url: str, params: dict, max_retries: int = 4) -> list | dict:
    delay = 2
    for attempt in range(max_retries):
        try:
            r = httpx.get(url, params=params, timeout=30)
            r.raise_for_status()
            return r.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"[오류] USDA API 호출 실패: {e}") from e
            time.sleep(delay)
            delay *= 2


def fetch_wasde_soybean_oil(marketing_year: int | None = None) -> pd.DataFrame:
    """USDA FAS PSD API에서 대두유(Soybean Oil) 수급 데이터 수집.
    USDA_FAS_PSD_API_KEY 등록 시 인증 요청 (더 많은 데이터·쿼터 제공).
    """
    year = marketing_year or date.today().year
    params: dict = {"commodityCode": "2222000", "marketingYear": year}
    api_key = os.environ.get("USDA_FAS_PSD_API_KEY", "")
    if api_key:
        params["apiKey"] = api_key
    data = _fetch(PSD_API, params)
    if not data:
        print(f"[경고] USDA PSD: {year}년 데이터 없음")
        return pd.DataFrame()

    rows = []
    for item in data:
        rows.append({
            "price_date": f"{year}-10-01",  # WASDE marketing year start
            "source_name": "USDA_PSD",
            "indicator_code": f"SBO_{item.get('attributeId', 'UNKNOWN')}",
            "country": item.get("countryName", ""),
            "value": item.get("value"),
            "unit": item.get("unitDesc", "1000 MT"),
        })
    df = pd.DataFrame(rows)
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["ingested_at"] = pd.Timestamp.utcnow()
    return df.dropna(subset=["value"])


def run() -> None:
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y%m%d")
    df = fetch_wasde_soybean_oil()
    if df.empty:
        print("[경고] WASDE: 수집된 데이터 없음")
        return
    out = f"{OUTPUT_DIR}/crop_data_{today}.parquet"
    df.to_parquet(out, index=False)
    print(f"[완료] WASDE 작황 데이터 {len(df)}건 저장 → {out}")


if __name__ == "__main__":
    run()
