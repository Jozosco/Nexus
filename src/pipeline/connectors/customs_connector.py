"""
한국 세관 수출입 통계 커넥터 — WBS 1.1.2 보완
수집 대상: HS 1507 (대두유) 국가별 수입량·CIF 금액 (관세청 API)

API 출처: 공공데이터포털 — 관세청_품목별 국가별 수출입실적(GW)
  - 포털 페이지: https://www.data.go.kr/data/15100475/openapi.do
  - 엔드포인트: http://apis.data.go.kr/1220000/nitemtrade/getNitemtradeList

파라미터 (검증된 형식 — 2026-05-26 사용자 확인):
  - strtYymm: 시작 년월 (YYYYMM)
  - endYymm:  종료 년월 (YYYYMM)
  - hsSgn:    HS 코드 10단위 (반드시 10단위 사용)
  - cntyCd:   국가코드 2자리 ISO (선택, 미지정 시 전 국가 반환)
  → 연도별 연간 조회 방식 사용 (strtYymm=YYYY01, endYymm=YYYY12)

HS 1507 10단위 코드 (대두유) — 2026-05-26 사용자 확인:
  1507101000: 식품용 대두유 조유 (Crude soybean oil, for food)
  1507901010: 식품용 정제 대두유 (Refined, for food)
  1507901020: 바이오디젤 제조용 정제 대두유 (Refined, for biodiesel)

키 형식: urllib.parse.unquote()로 디코딩 후 params 전달
        (포털 제공 URL-인코딩 키 이중 인코딩 방지)
폴백: 원본 인코딩 키를 URL에 직접 삽입 (2차 시도)

UN Comtrade Plus 대안:
  - 환경변수: UN_COMTRADE_API_KEY
  - 패키지: comtradeapicall (pip install comtradeapicall)
  - 무료 500건/일, 유료 10,000건/일

실행 환경: VS Code Web (Azure ML Studio) 또는 GitHub Actions
"""

from __future__ import annotations

import os
import time
from datetime import date, timedelta
from typing import Any
from urllib.parse import unquote

import json as _json

import httpx
import pandas as pd

OUTPUT_DIR = "data/raw"

CUSTOMS_BASE = "http://apis.data.go.kr/1220000/nitemtrade/getNitemtradeList"

# HS 1507 10단위 코드 (사용자 확인 2026-05-26)
HS_CODES_SOYBEAN_OIL: list[str] = [
    "1507101000",  # 식품용 대두유 조유 (Crude soybean oil, for food)
    "1507901010",  # 식품용 정제 대두유 (Refined soybean oil, for food)
    "1507901020",  # 바이오디젤 제조용 정제 대두유 (Refined, for biodiesel)
]

# 한국 대두유 주요 수입 국가 (사용자 확인 2026-05-26)
COUNTRY_CODES: list[str] = ["US", "CN", "BR", "AR", "MY", "ID"]

COMTRADE_REPORTER_KOREA = "410"


def _fetch(url: str, params: dict[str, Any], max_retries: int = 4) -> dict:
    """외부 API 호출 — 지수 백오프 재시도."""
    delay = 2
    for attempt in range(max_retries):
        try:
            r = httpx.get(url, params=params, timeout=30)
            if r.status_code == 401:
                key_hint = params.get("serviceKey", "?")
                key_hint = (str(key_hint)[:8] + "...") if len(str(key_hint)) > 8 else str(key_hint)
                print(
                    f"[오류] 관세청 API 401 인증 실패 — 서비스키 만료·미승인 가능성\n"
                    f"       사용 키 앞 8자리: {key_hint}\n"
                    f"       확인: data.go.kr → 마이페이지 → 활용현황 → 관세청_품목별국가별수출입실적(GW)\n"
                    f"       조치: 재발급 또는 승인 연장 → GitHub Secrets DATA_GO_KR_SERVICE_KEY 갱신"
                )
                return {}
            if r.status_code in (400, 403, 404):
                snippet = r.text[:300].replace("\n", " ")
                print(f"[경고] API {r.status_code} ({url.split('?')[0]}): {snippet}")
                return {}
            r.raise_for_status()
            try:
                return r.json()
            except (_json.JSONDecodeError, ValueError):
                snippet = r.text[:300].replace("\n", " ")
                print(f"[경고] JSON 파싱 실패 (응답 미리보기): {snippet}")
                return {}
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"[오류] API 호출 실패 ({url}): {e}") from e
            time.sleep(delay)
            delay *= 2
    return {}


def _parse_items(data: dict) -> list[dict]:
    """관세청 API 응답에서 items 추출. 단일 항목(dict)·리스트·items.item 구조 모두 대응."""
    body = data.get("response", {}).get("body", {})
    raw = body.get("items", [])
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        inner = raw.get("item", [])
        return [inner] if isinstance(inner, dict) else (inner or [])
    return []


def _fetch_customs_range(
    service_key: str,
    strt_yymm: str,
    end_yymm: str,
    hs_sgn: str,
    cnty_cd: str | None = None,
) -> list[dict]:
    """관세청 API 기간·국가 조회. 디코딩/인코딩/직삽 키 3단계 폴백.

    strt_yymm, end_yymm: YYYYMM 형식 (예: '202001', '202012')
    hs_sgn: 10단위 HS 코드 (예: '1507901010')
    cnty_cd: ISO 2자리 국가코드 (예: 'US', 'BR') — None이면 전 국가 반환
    """
    base_params: dict[str, Any] = {
        "strtYymm": strt_yymm,
        "endYymm":  end_yymm,
        "hsSgn":    hs_sgn,
    }
    if cnty_cd:
        base_params["cntyCd"] = cnty_cd

    # 1차: 디코딩 키 → httpx params (포털 URL-인코딩 키 이중 인코딩 방지)
    decoded_key = unquote(service_key)
    data = _fetch(CUSTOMS_BASE, {"serviceKey": decoded_key, **base_params})
    items = _parse_items(data)
    if items:
        return items

    # 2차: 원본 키 그대로 params (일반 hex 서비스키)
    if decoded_key != service_key:
        data2 = _fetch(CUSTOMS_BASE, {"serviceKey": service_key, **base_params})
        items2 = _parse_items(data2)
        if items2:
            return items2

    # 3차: 원본 인코딩 키를 URL에 직접 삽입 (httpx 인코딩 완전 우회)
    direct_url = f"{CUSTOMS_BASE}?serviceKey={service_key}"
    fb_data = _fetch(direct_url, base_params)
    return _parse_items(fb_data)


def fetch_customs_sbo_imports(
    start_year: int = 2017,
    end_year: int | None = None,
    country_codes: list[str] | None = None,
) -> pd.DataFrame:
    """관세청 API — 대두유(HS 1507) 국가별 수입 통계 (연도별·국가별 수집).

    Args:
        start_year:    수집 시작 연도 (기본 2017 — 사용자 확인된 최초 수집 연도)
        end_year:      수집 종료 연도 (기본 현재 연도)
        country_codes: 수집 대상 국가 코드 목록 (기본 COUNTRY_CODES 상수)

    수집 방식:
        - 연도별 × HS코드별 × 국가별 순서로 API 호출
        - 총 호출 횟수: (end_year - start_year + 1) × len(HS_CODES) × len(country_codes)
        - 각 호출 후 0.3초 대기 (레이트 리밋 준수)
    """
    service_key = os.environ.get("DATA_GO_KR_SERVICE_KEY", "").strip()
    if not service_key:
        print(
            "[경고] DATA_GO_KR_SERVICE_KEY 미등록 — 관세청 API 수집 건너뜀.\n"
            "       등록: data.go.kr → 관세청_품목별국가별수출입실적(GW) → GitHub Secrets"
        )
        return pd.DataFrame()

    if end_year is None:
        end_year = date.today().year
    if country_codes is None:
        country_codes = COUNTRY_CODES

    today_ym = date.today().strftime("%Y%m")
    all_rows: list[dict] = []
    total_calls = 0
    success_calls = 0

    for yr in range(start_year, end_year + 1):
        strt_ym = f"{yr:04d}01"
        end_ym  = f"{yr:04d}12" if yr < date.today().year else today_ym

        for hs_sgn in HS_CODES_SOYBEAN_OIL:
            for cnty_cd in country_codes:
                total_calls += 1
                items = _fetch_customs_range(service_key, strt_ym, end_ym, hs_sgn, cnty_cd)
                if items:
                    for item in items:
                        item.setdefault("hsSgn",   hs_sgn)
                        item.setdefault("cntyCd",  cnty_cd)
                    all_rows.extend(items)
                    success_calls += 1
                time.sleep(0.3)

    print(f"[정보] 관세청 API: 총 {total_calls}건 호출, {success_calls}건 성공")

    if not all_rows:
        print(f"[경고] 관세청 API: HS 1507 전 코드 수집 실패 ({start_year}~{end_year})")
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    df["ingested_at"] = pd.Timestamp.utcnow()
    df["source_name"] = "KoreaCustoms/data.go.kr"

    col_map = {
        "strtYymm":  "period_start",
        "endYymm":   "period_end",
        "cntyCd":    "country_code",
        "cntyNm":    "country_name",
        "imAmt":     "import_cif_usd",
        "impAmt":    "import_cif_usd",
        "imWgt":     "import_weight_kg",
        "wgt":       "import_weight_kg",
        "exAmt":     "export_fob_usd",
        "expAmt":    "export_fob_usd",
        "hsSgn":     "hs_code",
    }
    df.rename(columns={k: v for k, v in col_map.items() if k in df.columns}, inplace=True)

    if "period_start" in df.columns:
        df["price_date"] = pd.to_datetime(df["period_start"], format="%Y%m", errors="coerce")
    elif "strtYymm" in df.columns:
        df["price_date"] = pd.to_datetime(df["strtYymm"], format="%Y%m", errors="coerce")

    print(f"[완료] 관세청 수입통계 총 {len(df)}건 (HS 1507, {start_year}~{end_year}, {len(country_codes)}개국)")
    return df


def fetch_comtrade_sbo_imports_fallback(start_year: int = 2017) -> pd.DataFrame:
    """UN Comtrade Plus — 대두유(HS 1507) 한국 수입 통계 (comtradeapicall 패키지).

    무료: previewFinalData (500건/일)
    유료: getFinalData (10,000건/일, UN_COMTRADE_API_KEY 필요)
    """
    sub_key = os.environ.get("UN_COMTRADE_API_KEY", "").strip()

    try:
        import comtradeapicall  # type: ignore
    except ImportError:
        print("[경고] comtradeapicall 미설치 — pip install comtradeapicall")
        return pd.DataFrame()

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
            call_fn = comtradeapicall.getFinalData if sub_key else comtradeapicall.previewFinalData
            kwargs: dict[str, Any] = dict(
                typeCode="C", freqCode="M", clCode="HS",
                period=period_str,
                reporterCode=COMTRADE_REPORTER_KOREA,
                cmdCode="1507",
                flowCode="M",
                partnerCode=None, partner2Code=None,
                customsCode=None, motCode=None,
                maxRecords=10000 if sub_key else 500,
                format_output="JSON",
                aggregateBy=None, breakdownMode="classic",
                countOnly=None, includeDesc=True,
            )
            if sub_key:
                kwargs["subscription_key"] = sub_key
            df = call_fn(**kwargs)
            if df is not None and not df.empty:
                all_frames.append(df)
                print(f"[정보] UN Comtrade {yr}: {len(df)}건")
            time.sleep(1)
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                print(f"[경고] UN Comtrade 레이트 리밋 ({yr}): {e}")
                break
            print(f"[경고] UN Comtrade {yr}: {e}")

    if not all_frames:
        return pd.DataFrame()

    combined = pd.concat(all_frames, ignore_index=True)
    period_col  = next((c for c in ["period", "Period"] if c in combined.columns), None)
    val_col     = next((c for c in ["primaryValue", "tradeValue", "cifvalue"] if c in combined.columns), None)
    wgt_col     = next((c for c in ["netWgt", "netWeight"] if c in combined.columns), None)
    partner_col = next((c for c in ["partnerDesc", "partnerCode"] if c in combined.columns), None)

    result = pd.DataFrame()
    if period_col:
        result["price_date"] = pd.to_datetime(combined[period_col].astype(str), format="%Y%m", errors="coerce")
    if val_col:
        result["import_cif_usd"] = pd.to_numeric(combined[val_col], errors="coerce")
    if wgt_col:
        result["import_weight_kg"] = pd.to_numeric(combined[wgt_col], errors="coerce")
    if partner_col:
        result["country_name"] = combined[partner_col].astype(str)
    result["source_name"] = "UNComtrade/comtradeapicall"
    result["ingested_at"] = pd.Timestamp.utcnow()
    print(f"[정보] UN Comtrade 총 {len(result)}건 ({start_year}~현재)")
    return result


def run() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today_str = date.today().strftime("%Y%m%d")

    start_year = int(os.environ.get("HISTORICAL_START_YEAR", "2017"))
    df = fetch_customs_sbo_imports(start_year=start_year)
    if df.empty:
        print("[정보] 관세청 미수집 — UN Comtrade 폴백 시도")
        df = fetch_comtrade_sbo_imports_fallback(start_year=2017)

    if df.empty:
        print("[경고] 관세청·UN Comtrade 모두 실패 — API 키 확인 필요")
        print("       DATA_GO_KR_SERVICE_KEY: data.go.kr 포털 발급")
        print("       UN_COMTRADE_API_KEY: comtradeplus.un.org 발급")
        return

    out = f"{OUTPUT_DIR}/customs_import_{today_str}.parquet"
    df.to_parquet(out, index=False)
    print(f"[완료] 대두유 수입통계 {len(df)}건 저장 → {out}")


if __name__ == "__main__":
    run()
