"""
한국 세관 수출입 통계 커넥터 — WBS 1.1.2 보완
수집 대상: HS 1507 (대두유) 국가별 월별 수입량·CIF 금액 (관세청 API)

API 출처: 공공데이터포털 — 관세청_품목별 국가별 수출입실적(GW)
  - 포털 페이지: https://www.data.go.kr/data/15100475/openapi.do
  - 엔드포인트: http://apis.data.go.kr/1220000/nitemtrade/getNitemtradeList
  - 인증: DATA_GO_KR_SERVICE_KEY (GitHub Secrets)
  - 갱신 주기: 월별 (전월 데이터 매월 15일경 반영)
  - 무료 할당: 개발키 10,000건/일, 운영키 100,000건/일

ATFIS_API_KEY 참고 (MEMORY A-011):
  - ATFIS (atfis.or.kr) = aT FIS 식품산업통계정보 — HS코드별 수입 통계 미제공
  - 대두유 수입 통계는 관세청 API (DATA_GO_KR_SERVICE_KEY) 사용

UN Comtrade Plus 대안 (DATA_GO_KR_SERVICE_KEY 미등록 시):
  - comtradeplus.un.org — 무료 티어 500건/일
  - 패키지: comtradeapicall (pip)

실행 환경: VS Code Web (Azure ML Studio) 또는 GitHub Actions
"""

from __future__ import annotations

import os
import time
from datetime import date, timedelta
from typing import Any

import httpx
import pandas as pd

OUTPUT_DIR = "data/raw"

CUSTOMS_BASE = "http://apis.data.go.kr/1220000/nitemtrade/getNitemtradeList"
HS_SOYBEAN_OIL = "1507"   # HS 4단위: 대두유 챕터 (정밀화 시 10단위 사용)

COMTRADE_BASE = "https://comtradeapi.un.org/data/v1/get"
HS_REPORTER_KOREA = "410"  # UN Comtrade 한국 국가 코드


def _fetch(url: str, params: dict[str, Any], max_retries: int = 4) -> dict:
    """외부 API 호출 — 지수 백오프 재시도."""
    delay = 2
    for attempt in range(max_retries):
        try:
            r = httpx.get(url, params=params, timeout=30)
            if r.status_code in (400, 403, 404):
                print(f"[경고] API {r.status_code} 응답 ({url.split('?')[0]}): 파라미터 또는 인증 오류. 건너뜀.")
                return {}
            r.raise_for_status()
            return r.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"[오류] API 호출 실패 ({url}): {e}") from e
            time.sleep(delay)
            delay *= 2
    return {}


def fetch_customs_sbo_imports(
    period: str | None = None,
    hs_cd: str = HS_SOYBEAN_OIL,
) -> pd.DataFrame:
    """관세청 API — 대두유(HS 1507) 국가별 월별 수입 통계.

    Args:
        period: 조회 기간 (YYYYMM). None이면 전월 자동 계산.
        hs_cd:  HS 코드 (기본 4단위 '1507').

    Returns:
        수입량(kg)·CIF 금액(USD)·국가별 DataFrame.
    """
    service_key = os.environ.get("DATA_GO_KR_SERVICE_KEY", "").strip()
    if not service_key:
        print(
            "[경고] DATA_GO_KR_SERVICE_KEY 미등록 — 관세청 수출입실적 API 수집 건너뜀.\n"
            "       등록 경로: data.go.kr 가입 → 관세청_품목별국가별수출입실적(GW) 활용신청 → GitHub Secrets"
        )
        return pd.DataFrame()

    if period is None:
        first_of_month = date.today().replace(day=1)
        prev_month = first_of_month - timedelta(days=1)
        period = prev_month.strftime("%Y%m")

    params = {
        "serviceKey": service_key,
        "pageNo":     1,
        "numOfRows":  200,
        "hsCd":       hs_cd,
        "period":     period,
        "type":       "json",
    }

    data = _fetch(CUSTOMS_BASE, params)
    if not data:
        return pd.DataFrame()

    try:
        items = (
            data.get("response", {})
                .get("body", {})
                .get("items", [])
        )
    except (KeyError, TypeError) as e:
        print(f"[경고] 관세청 API 응답 파싱 실패: {e}. 원문 키: {list(data.keys())}")
        return pd.DataFrame()

    if not items:
        print(f"[정보] 관세청 API: {period} 기간 HS {hs_cd} 데이터 없음.")
        return pd.DataFrame()

    df = pd.DataFrame(items)
    df["period"]      = period
    df["hs_code"]     = hs_cd
    df["ingested_at"] = pd.Timestamp.utcnow()
    df["source_name"] = "KoreaCustoms/data.go.kr"

    df.rename(columns={
        "cntyCd":  "country_code",
        "cntyNm":  "country_name",
        "impAmt":  "import_cif_usd",
        "wgt":     "import_weight_kg",
        "expAmt":  "export_fob_usd",
    }, errors="ignore", inplace=True)

    print(f"[정보] 관세청 수입 통계 수집 완료: {period} / HS {hs_cd} / {len(df)}개국")
    return df


def fetch_comtrade_sbo_imports_fallback(
    year: int | None = None,
    month: int | None = None,
) -> pd.DataFrame:
    """UN Comtrade Plus 대안 — DATA_GO_KR_SERVICE_KEY 미등록 시 사용.

    무료 티어: 500건/일. 월별 데이터, 2000년 이후.
    """
    sub_key = os.environ.get("COMTRADE_API_KEY", "").strip()
    if not sub_key:
        print("[경고] COMTRADE_API_KEY 미등록 — UN Comtrade 수집 건너뜀.")
        return pd.DataFrame()

    if year is None or month is None:
        prev = date.today().replace(day=1) - timedelta(days=1)
        year, month = prev.year, prev.month

    params = {
        "reporterCode": HS_REPORTER_KOREA,
        "period":       f"{year}{month:02d}",
        "flowCode":     "M",          # M = Import
        "cmdCode":      HS_SOYBEAN_OIL,
        "customsCode":  "C00",
        "subscription-key": sub_key,
    }

    data = _fetch(COMTRADE_BASE, params)
    if not data or "data" not in data:
        return pd.DataFrame()

    df = pd.DataFrame(data["data"])
    df["ingested_at"] = pd.Timestamp.utcnow()
    df["source_name"] = "UNComtrade/comtradeplus.un.org"
    print(f"[정보] UN Comtrade 수입 통계 수집 완료: {year}-{month:02d} / {len(df)}건")
    return df


def run() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today_str = date.today().strftime("%Y%m%d")

    df = fetch_customs_sbo_imports()

    if df.empty:
        df = fetch_comtrade_sbo_imports_fallback()

    if df.empty:
        print("[경고] 관세청·UN Comtrade 모두 데이터 수집 실패 — API 키 등록 상태 확인.")
        return

    out = f"{OUTPUT_DIR}/customs_import_{today_str}.parquet"
    df.to_parquet(out, index=False)
    print(f"[완료] 대두유 수입 통계 {len(df)}건 저장 → {out}")


if __name__ == "__main__":
    run()
