"""
한국 세관 수출입 통계 커넥터 — WBS 1.1.2 보완
수집 대상: HS 1507 (대두유) 국가별 월별 수입량·CIF 금액 (관세청 API)

API 출처: 공공데이터포털 — 관세청_품목별 국가별 수출입실적(GW)
  - 포털 페이지: https://www.data.go.kr/data/15100475/openapi.do
  - 엔드포인트: http://apis.data.go.kr/1220000/nitemtrade/getNitemtradeList
  - 인증: DATA_GO_KR_SERVICE_KEY (GitHub Secrets)
  - 키 형식: 포털은 URL-인코딩 키(%2B, %2F 등) 제공
    → urllib.parse.unquote()로 디코딩 후 httpx params 전달 (이중 인코딩 방지)
    → 디코딩 실패 시 원본 인코딩 키를 URL에 직접 삽입하는 방식으로 자동 폴백
  - 갱신 주기: 월별 (전월 데이터 매월 15일경 반영)
  - 무료 할당: 개발키 10,000건/일, 운영키 100,000건/일

UN Comtrade Plus 대안 (DATA_GO_KR_SERVICE_KEY 미등록 시):
  - comtradeplus.un.org — comtradeapicall 패키지 사용
  - 환경변수: UN_COMTRADE_API_KEY (GitHub Secrets)
  - 레이트 리밋: 무료(previewFinalData) 500건/일, 유료(getFinalData) 10,000건/일
    대두유(HS 1507) 한국 수입 월별 조회 ≈ 12건/년 → 무료 한도 충분
  - 참고: https://github.com/uncomtrade/comtradeapicall

실행 환경: VS Code Web (Azure ML Studio) 또는 GitHub Actions
"""

from __future__ import annotations

import os
import time
from datetime import date, timedelta
from typing import Any
from urllib.parse import unquote

import httpx
import pandas as pd

OUTPUT_DIR = "data/raw"

CUSTOMS_BASE = "http://apis.data.go.kr/1220000/nitemtrade/getNitemtradeList"
HS_SOYBEAN_OIL = "1507"           # HS 4단위: 대두유 챕터
COMTRADE_REPORTER_KOREA = "410"   # UN Comtrade 한국 국가 코드
HISTORY_START = "202001"          # 수집 시작 기간 (2020년 1월)


def _fetch(url: str, params: dict[str, Any], max_retries: int = 4) -> dict:
    """외부 API 호출 — 지수 백오프 재시도."""
    delay = 2
    for attempt in range(max_retries):
        try:
            r = httpx.get(url, params=params, timeout=30)
            if r.status_code in (400, 403, 404):
                print(f"[경고] API {r.status_code} 응답 ({url.split('?')[0]}): 파라미터 또는 인증 오류.")
                return {}
            r.raise_for_status()
            return r.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"[오류] API 호출 실패 ({url}): {e}") from e
            time.sleep(delay)
            delay *= 2
    return {}


def _periods_from(start_period: str) -> list[str]:
    """start_period(YYYYMM)부터 전월까지의 기간 목록 생성."""
    first_of_month = date.today().replace(day=1)
    prev_month = first_of_month - timedelta(days=1)
    start_year, start_month = int(start_period[:4]), int(start_period[4:])
    d = date(start_year, start_month, 1)
    periods: list[str] = []
    while d <= prev_month.replace(day=1):
        periods.append(d.strftime("%Y%m"))
        d = date(d.year + (d.month // 12), (d.month % 12) + 1, 1)
    return periods


def _fetch_customs_month(service_key: str, period: str, hs_cd: str) -> list[dict]:
    """관세청 API 단일 월 수집. 인코딩/디코딩 키 양방향 자동 처리.

    data.go.kr 포털은 URL-인코딩 키(%2B 등)를 제공한다.
    httpx.params에 그대로 전달하면 이중 인코딩 → 400 오류.
    Fix: unquote()로 디코딩 후 전달. 여전히 400이면 원본 키를 URL에 직접 삽입.
    """
    # 1차 시도: 디코딩 키를 params 값으로 전달
    decoded_key = unquote(service_key)
    params = {
        "serviceKey": decoded_key,
        "pageNo":     1,
        "numOfRows":  200,
        "hsCd":       hs_cd,
        "period":     period,
        "type":       "json",
    }
    data = _fetch(CUSTOMS_BASE, params)
    items = data.get("response", {}).get("body", {}).get("items", []) if data else []
    if items:
        return items

    # 2차 폴백: 원본 인코딩 키를 URL 쿼리에 직접 삽입 (이중 인코딩 우회)
    direct_url = f"{CUSTOMS_BASE}?serviceKey={service_key}"
    direct_params: dict[str, Any] = {
        "pageNo":     1,
        "numOfRows":  200,
        "hsCd":       hs_cd,
        "period":     period,
        "type":       "json",
    }
    fb_data = _fetch(direct_url, direct_params)
    return fb_data.get("response", {}).get("body", {}).get("items", []) if fb_data else []


def fetch_customs_sbo_imports(
    start_period: str | None = HISTORY_START,
    period: str | None = None,
    hs_cd: str = HS_SOYBEAN_OIL,
) -> pd.DataFrame:
    """관세청 API — 대두유(HS 1507) 국가별 월별 수입 통계.

    Args:
        start_period: 수집 시작 기간(YYYYMM). 기본값 "202001" (2020년 1월부터 전월까지).
        period:       단일 월 조회(YYYYMM). 지정 시 start_period 무시.
        hs_cd:        HS 코드 (기본 4단위 '1507').
    """
    service_key = os.environ.get("DATA_GO_KR_SERVICE_KEY", "").strip()
    if not service_key:
        print(
            "[경고] DATA_GO_KR_SERVICE_KEY 미등록 — 관세청 수출입실적 API 수집 건너뜀.\n"
            "       등록 경로: data.go.kr → 관세청_품목별국가별수출입실적(GW) → GitHub Secrets"
        )
        return pd.DataFrame()

    periods = [period] if period else _periods_from(start_period or HISTORY_START)
    if not periods:
        return pd.DataFrame()

    all_rows: list[dict] = []
    for p in periods:
        items = _fetch_customs_month(service_key, p, hs_cd)
        if not items:
            continue
        for item in items:
            item["period"] = p
        all_rows.extend(items)

    if not all_rows:
        print(f"[경고] 관세청 API: 수집된 데이터 없음 (HS {hs_cd}, {len(periods)}개월 조회)")
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
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
    # YYYYMM → 월 첫째 날
    df["price_date"] = pd.to_datetime(df["period"], format="%Y%m", errors="coerce")
    print(f"[정보] 관세청 수입 통계 수집 완료: {len(periods)}개월 / HS {hs_cd} / {len(df)}건")
    return df


def fetch_comtrade_sbo_imports_fallback(start_year: int = 2020) -> pd.DataFrame:
    """UN Comtrade Plus — 대두유(HS 1507) 한국 수입 통계 (comtradeapicall 패키지).

    무료: previewFinalData (500건/일, subscription_key 불필요)
    유료: getFinalData (10,000건/일, UN_COMTRADE_API_KEY 필요)
    레이트 리밋: 1초 간격 준수 (API 정책)
    """
    sub_key = os.environ.get("UN_COMTRADE_API_KEY", "").strip()

    try:
        import comtradeapicall  # type: ignore
    except ImportError:
        print("[경고] comtradeapicall 미설치 — UN Comtrade 수집 건너뜀.")
        print("       GitHub Actions pip: pip install comtradeapicall")
        return pd.DataFrame()

    # start_year부터 전월까지 기간 목록 생성 (연도별 배치)
    end_d = date.today().replace(day=1) - timedelta(days=1)
    year_batches: dict[int, list[str]] = {}
    d = date(start_year, 1, 1)
    while d.replace(day=1) <= end_d.replace(day=1):
        year_batches.setdefault(d.year, []).append(d.strftime("%Y%m"))
        d = date(d.year + (d.month // 12), (d.month % 12) + 1, 1)

    all_frames: list[pd.DataFrame] = []
    for yr, yr_periods in sorted(year_batches.items()):
        period_str = ",".join(yr_periods)
        try:
            if sub_key:
                df = comtradeapicall.getFinalData(
                    subscription_key=sub_key,
                    typeCode="C",
                    freqCode="M",
                    clCode="HS",
                    period=period_str,
                    reporterCode=COMTRADE_REPORTER_KOREA,
                    cmdCode=HS_SOYBEAN_OIL,
                    flowCode="M",
                    partnerCode=None,
                    partner2Code=None,
                    customsCode=None,
                    motCode=None,
                    maxRecords=10000,
                    format_output="JSON",
                    aggregateBy=None,
                    breakdownMode="classic",
                    countOnly=None,
                    includeDesc=True,
                )
            else:
                df = comtradeapicall.previewFinalData(
                    typeCode="C",
                    freqCode="M",
                    clCode="HS",
                    period=period_str,
                    reporterCode=COMTRADE_REPORTER_KOREA,
                    cmdCode=HS_SOYBEAN_OIL,
                    flowCode="M",
                    partnerCode=None,
                    partner2Code=None,
                    customsCode=None,
                    motCode=None,
                    maxRecords=500,
                    format_output="JSON",
                    aggregateBy=None,
                    breakdownMode="classic",
                    countOnly=None,
                    includeDesc=True,
                )
            if df is not None and not df.empty:
                all_frames.append(df)
                print(f"[정보] UN Comtrade {yr} 수집 완료: {len(df)}건")
            else:
                print(f"[정보] UN Comtrade {yr}: 데이터 없음")
        except Exception as e:
            err_str = str(e)
            if "rate" in err_str.lower() or "429" in err_str or "limit" in err_str.lower():
                print(f"[경고] UN Comtrade 레이트 리밋 초과 ({yr}): {e}")
                print("       해결책: UN_COMTRADE_API_KEY 유료 구독 키 사용 (10,000건/일)")
                break
            print(f"[경고] UN Comtrade {yr} 수집 실패: {e}")
        time.sleep(1)  # API 레이트 리밋 준수 (1초 간격)

    if not all_frames:
        print("[경고] UN Comtrade: 수집된 데이터 없음 — UN_COMTRADE_API_KEY 확인")
        return pd.DataFrame()

    combined = pd.concat(all_frames, ignore_index=True)

    # UN Comtrade 컬럼 → Nexus 스키마 변환 (버전별 컬럼명 차이 대응)
    period_col  = next((c for c in ["period", "Period", "refPeriodId"] if c in combined.columns), None)
    val_col     = next((c for c in ["primaryValue", "tradeValue", "cifvalue", "CifValue"] if c in combined.columns), None)
    wgt_col     = next((c for c in ["netWgt", "netWeight", "NetWgt"] if c in combined.columns), None)
    partner_col = next((c for c in ["partnerDesc", "partner2Desc", "partnerCode"] if c in combined.columns), None)

    result = pd.DataFrame()
    if period_col:
        result["price_date"] = pd.to_datetime(
            combined[period_col].astype(str), format="%Y%m", errors="coerce"
        )
    if val_col:
        result["import_cif_usd"] = pd.to_numeric(combined[val_col], errors="coerce")
    if wgt_col:
        result["import_weight_kg"] = pd.to_numeric(combined[wgt_col], errors="coerce")
    if partner_col:
        result["country_name"] = combined[partner_col].astype(str)

    result["hs_code"]     = HS_SOYBEAN_OIL
    result["source_name"] = "UNComtrade/comtradeapicall"
    result["ingested_at"] = pd.Timestamp.utcnow()
    print(f"[정보] UN Comtrade 수집 완료 (총): {len(result)}건 ({start_year}-현재)")
    return result


def run() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today_str = date.today().strftime("%Y%m%d")

    # 1차: 관세청 API (2020-01부터 전월까지)
    df = fetch_customs_sbo_imports(start_period=HISTORY_START)

    if df.empty:
        # 2차 폴백: UN Comtrade (comtradeapicall 패키지)
        print("[정보] 관세청 API 미수집 — UN Comtrade 폴백 시도 (2020년 이후)")
        df = fetch_comtrade_sbo_imports_fallback(start_year=2020)

    if df.empty:
        print("[경고] 관세청·UN Comtrade 모두 수집 실패 — API 키 등록 상태 확인.")
        print("       DATA_GO_KR_SERVICE_KEY: data.go.kr 포털 발급")
        print("       UN_COMTRADE_API_KEY: comtradeplus.un.org 발급")
        return

    out = f"{OUTPUT_DIR}/customs_import_{today_str}.parquet"
    df.to_parquet(out, index=False)
    print(f"[완료] 대두유 수입 통계 {len(df)}건 저장 → {out}")


if __name__ == "__main__":
    run()
