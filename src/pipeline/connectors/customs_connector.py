"""
한국 세관 수출입 통계 커넥터 — WBS 1.1.2 보완
수집 대상: HS 1507 (대두유) 품목별·국가별 수입량·CIF 금액 (관세청 API)

==================================================================
API 1 — 관세청_품목별 수출입실적(GW)
  엔드포인트: https://apis.data.go.kr/1220000/Itemtrade/getItemtradeList
  용도: 국가 구분 없이 HS코드 기준 전체 수출입 실적
  파라미터:
    - serviceKey: DATA_GO_KR_SERVICE_KEY (GitHub Secrets)
    - strtYymm:   YYYYMM (예: 201701)
    - endYymm:    YYYYMM (예: 201712)
    - hsSgn:      6단위 HS코드 (150710, 150790)

API 2 — 관세청_품목별 국가별 수출입실적(GW)
  엔드포인트: https://apis.data.go.kr/1220000/nitemtrade/getNitemtradeList
  용도: HS코드 × 국가별 상세 수출입 실적
  파라미터:
    - serviceKey, strtYymm, endYymm, hsSgn (위와 동일)
    - cntyCd: ISO 2자리 국가코드 (US, AR, BR, CN, ID)
==================================================================

HS 코드 — 2026-06-18 사용자 확인 (6단위 사용):
  150710: 대두유 조유 (Crude soybean oil, 식품용 포함)
  150790: 정제 대두유 및 기타 (Refined/other soybean oil)

  ※ 이전 10단위(1507101000/1507901010/1507901020) → 2026-06-18 6단위로 변경
     6단위 사용 시 해당 품목 전체를 포괄하여 누락 방지

키 형식: 평문 hex 키 (URL-인코딩 불필요)
        3단계 폴백: unquote → 원본 → URL 직삽

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

# API 1: 품목별 수출입실적 (국가 구분 없음)
ITEMTRADE_BASE   = "https://apis.data.go.kr/1220000/Itemtrade/getItemtradeList"
# API 2: 품목별 국가별 수출입실적
NITEMTRADE_BASE  = "https://apis.data.go.kr/1220000/nitemtrade/getNitemtradeList"

# HS 코드 — 6단위 (2026-06-18 사용자 확인)
# 150710: 대두유 조유 / 150790: 정제 및 기타 대두유
HS_CODES_SOYBEAN_OIL: list[str] = [
    "150710",   # 대두유 조유 (Crude soybean oil)
    "150790",   # 정제 대두유 및 기타 (Refined and other soybean oil)
]

# 한국 대두유 주요 수입 국가 (2026-06-18 사용자 확인)
COUNTRY_CODES: list[str] = ["US", "AR", "BR", "CN", "ID"]

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
    use_nitemtrade: bool = True,
) -> list[dict]:
    """관세청 API 기간·국가 조회. 디코딩/인코딩/직삽 키 3단계 폴백.

    strt_yymm, end_yymm: YYYYMM 형식 (예: '202001', '202012')
    hs_sgn: 6단위 HS 코드 (예: '150710', '150790')
    cnty_cd: ISO 2자리 국가코드 (예: 'US', 'AR') — None이면 Itemtrade(전국가 합계) 사용
    use_nitemtrade: True=nitemtrade(국가별), False=Itemtrade(전체)
    """
    base_url = NITEMTRADE_BASE if use_nitemtrade else ITEMTRADE_BASE
    base_params: dict[str, Any] = {
        "strtYymm": strt_yymm,
        "endYymm":  end_yymm,
        "hsSgn":    hs_sgn,
    }
    if cnty_cd and use_nitemtrade:
        base_params["cntyCd"] = cnty_cd

    # 1차: 디코딩 키 → httpx params (포털 URL-인코딩 키 이중 인코딩 방지)
    decoded_key = unquote(service_key)
    data = _fetch(base_url, {"serviceKey": decoded_key, **base_params})
    items = _parse_items(data)
    if items:
        return items

    # 2차: 원본 키 그대로 params (일반 hex 서비스키인 경우 decoded = original)
    if decoded_key != service_key:
        data2 = _fetch(base_url, {"serviceKey": service_key, **base_params})
        items2 = _parse_items(data2)
        if items2:
            return items2

    # 3차: 원본 인코딩 키를 URL에 직접 삽입 (httpx 인코딩 완전 우회)
    direct_url = f"{base_url}?serviceKey={service_key}"
    fb_data = _fetch(direct_url, base_params)
    return _parse_items(fb_data)


def _normalize_customs_df(all_rows: list[dict], source_tag: str) -> pd.DataFrame:
    """관세청 API rows → 정규화 DataFrame."""
    df = pd.DataFrame(all_rows)
    df["ingested_at"] = pd.Timestamp.utcnow()
    df["source_name"] = source_tag

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

    return df


def fetch_customs_total_imports(
    start_year: int = 2017,
    end_year: int | None = None,
) -> pd.DataFrame:
    """관세청 API 1 — 대두유(HS 1507) 전체 수출입실적 (국가 구분 없음).

    엔드포인트: https://apis.data.go.kr/1220000/Itemtrade/getItemtradeList
    수집 방식: 연도별 × HS코드별 API 호출 (cntyCd 미포함)
    """
    service_key = os.environ.get("DATA_GO_KR_SERVICE_KEY", "").strip()
    if not service_key:
        return pd.DataFrame()

    if end_year is None:
        end_year = date.today().year

    today_ym = date.today().strftime("%Y%m")
    all_rows: list[dict] = []
    total_calls = 0

    for yr in range(start_year, end_year + 1):
        strt_ym = f"{yr:04d}01"
        end_ym  = f"{yr:04d}12" if yr < date.today().year else today_ym
        for hs_sgn in HS_CODES_SOYBEAN_OIL:
            total_calls += 1
            items = _fetch_customs_range(service_key, strt_ym, end_ym, hs_sgn, use_nitemtrade=False)
            if items:
                for item in items:
                    item.setdefault("hsSgn", hs_sgn)
                all_rows.extend(items)
            time.sleep(0.3)

    print(f"[정보] Itemtrade: 총 {total_calls}건 호출, {len(all_rows)}건 수집")
    if not all_rows:
        return pd.DataFrame()

    df = _normalize_customs_df(all_rows, "KoreaCustoms/Itemtrade")
    print(f"[완료] 품목별 전체 수출입실적 {len(df)}건 (HS 1507, {start_year}~{end_year})")
    return df


def fetch_customs_sbo_imports(
    start_year: int = 2017,
    end_year: int | None = None,
    country_codes: list[str] | None = None,
) -> pd.DataFrame:
    """관세청 API 2 — 대두유(HS 1507) 국가별 수입 통계 (연도별·국가별 수집).

    엔드포인트: https://apis.data.go.kr/1220000/nitemtrade/getNitemtradeList
    Args:
        start_year:    수집 시작 연도 (기본 2017)
        end_year:      수집 종료 연도 (기본 현재 연도, HISTORICAL_END_YEAR 환경변수 우선)
        country_codes: 수집 대상 국가 코드 목록 (기본 COUNTRY_CODES: US/AR/BR/CN/ID)

    수집 방식:
        - 연도별 × HS코드별 × 국가별 순서로 API 호출
        - HS코드 2개 × 국가 5개 × 연도 N개 = 총 N×10 호출
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
        env_end = os.environ.get("HISTORICAL_END_YEAR", "").strip()
        end_year = int(env_end) if env_end else date.today().year
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
                        item.setdefault("hsSgn",  hs_sgn)
                        item.setdefault("cntyCd", cnty_cd)
                    all_rows.extend(items)
                    success_calls += 1
                time.sleep(0.3)

    print(f"[정보] nitemtrade: 총 {total_calls}건 호출, {success_calls}건 성공")

    if not all_rows:
        print(f"[경고] 관세청 API: HS 1507 수집 실패 ({start_year}~{end_year})")
        return pd.DataFrame()

    df = _normalize_customs_df(all_rows, "KoreaCustoms/nitemtrade")
    print(f"[완료] 국가별 수입통계 {len(df)}건 (HS 1507, {start_year}~{end_year}, {len(country_codes)}개국)")
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

    # A-067 진단 해결: ①12개월 일괄 → 분기(3개월) 배치로 500건 상한 회피
    #   ②429 시 break(전체 중단) → 지수 백오프 재시도 후 다음 배치 계속
    #   ③무료(previewFinalData 500건) 경로 로그 명시
    print(f"[정보] UN Comtrade 경로: {'getFinalData(유료키)' if sub_key else 'previewFinalData(무료·500건/호출)'}")
    end_d = date.today().replace(day=1) - timedelta(days=1)
    quarter_batches: list[tuple[int, int, list[str]]] = []
    d = date(start_year, 1, 1)
    cur: list[str] = []
    while d.replace(day=1) <= end_d.replace(day=1):
        cur.append(d.strftime("%Y%m"))
        if d.month % 3 == 0:          # 분기 경계
            quarter_batches.append((d.year, (d.month - 1) // 3 + 1, cur))
            cur = []
        d = date(d.year + (d.month // 12), (d.month % 12) + 1, 1)
    if cur:
        quarter_batches.append((d.year, (d.month - 1) // 3 + 1, cur))

    def _call_with_backoff(period_str: str, max_retries: int = 4):
        delay = 2
        for attempt in range(max_retries):
            try:
                call_fn = comtradeapicall.getFinalData if sub_key else comtradeapicall.previewFinalData
                kwargs: dict[str, Any] = dict(
                    typeCode="C", freqCode="M", clCode="HS",
                    period=period_str, reporterCode=COMTRADE_REPORTER_KOREA,
                    cmdCode="1507", flowCode="M",
                    partnerCode=None, partner2Code=None,
                    customsCode=None, motCode=None,
                    maxRecords=10000 if sub_key else 500,
                    format_output="JSON", aggregateBy=None,
                    breakdownMode="classic", countOnly=None, includeDesc=True,
                )
                if sub_key:
                    kwargs["subscription_key"] = sub_key
                return call_fn(**kwargs)
            except Exception as e:
                if ("429" in str(e) or "rate" in str(e).lower()) and attempt < max_retries - 1:
                    print(f"[경고] Comtrade 레이트 리밋 — {delay}s 후 재시도 ({attempt+1}/{max_retries})")
                    time.sleep(delay)
                    delay *= 2
                    continue
                print(f"[경고] Comtrade {period_str[:6]}~: {e}")
                return None

    all_frames: list[pd.DataFrame] = []
    for yr, q, periods in quarter_batches:
        df = _call_with_backoff(",".join(periods))
        if df is not None and not df.empty:
            all_frames.append(df)
            print(f"[정보] UN Comtrade {yr}Q{q}: {len(df)}건")
        time.sleep(1)

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
    today_str  = date.today().strftime("%Y%m%d")

    start_year = int(os.environ.get("HISTORICAL_START_YEAR", "2017"))
    end_year   = int(os.environ.get("HISTORICAL_END_YEAR",   str(date.today().year)))

    print(f"[정보] 관세청 수집 범위: {start_year}년 ~ {end_year}년 / HS 코드: {HS_CODES_SOYBEAN_OIL}")

    # API 1: 품목별 전체 (Itemtrade — 국가 구분 없음)
    df_total = fetch_customs_total_imports(start_year=start_year, end_year=end_year)

    # API 2: 품목별 국가별 (nitemtrade)
    df_by_country = fetch_customs_sbo_imports(start_year=start_year, end_year=end_year)

    # 두 소스 병합
    frames = [f for f in [df_total, df_by_country] if not f.empty]
    if frames:
        df = pd.concat(frames, ignore_index=True)
    else:
        df = pd.DataFrame()

    if df.empty:
        print("[정보] 관세청 미수집 — UN Comtrade 폴백 시도")
        df = fetch_comtrade_sbo_imports_fallback(start_year=start_year)

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
