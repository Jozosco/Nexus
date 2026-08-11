"""
경제 지표 커넥터 — WBS 1.1.2
수집 대상: Fed 기준금리 (FRED) · 글로벌 CPI (FRED) · KRW/USD 환율 (BOK ECOS) · WTI/Brent 유가 (EIA)
실행 환경: VS Code Web (Azure ML Studio) 또는 GitHub Actions
"""

from __future__ import annotations

import os
import time
from datetime import date
from typing import Any, Callable

import httpx

# A-085: 한국 공공기관 호스트에서 러너 IPv6 경로 블랙홀 → IPv4 강제 트랜스포트
_KR_TRANSPORT = httpx.HTTPTransport(local_address="0.0.0.0", retries=2)
import pandas as pd

# ── 상수 ──────────────────────────────────────────────────────────────────────
FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
EIA_BASE  = "https://api.eia.gov/v2/petroleum/pri/spt/data/"
BOK_BASE  = "https://ecos.bok.or.kr/api/StatisticSearch"
OUTPUT_DIR = "data/raw"


def _fetch(url: str, params: dict[str, Any], max_retries: int = 4) -> dict:
    """외부 API 호출 — 지수 백오프 재시도 (MEMORY A-003).
    400: 시리즈 미존재 또는 파라미터 오류 → 재시도 없이 빈 dict 반환.
    """
    delay = 2
    for attempt in range(max_retries):
        try:
            r = httpx.Client(transport=_KR_TRANSPORT, timeout=60).get(url, params=params)
            if r.status_code == 400:
                base = url.split("?")[0]
                print(f"[경고] API 400 응답 ({base}): 시리즈 미존재 또는 파라미터 오류. 건너뜀.")
                return {}
            r.raise_for_status()
            return r.json()
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"[오류] API 호출 실패 ({url}): {e}") from e
            time.sleep(delay)
            delay *= 2
    return {}


def fetch_fred_series(series_id: str, start: str, end: str) -> pd.DataFrame:
    """FRED 시계열 데이터 수집."""
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise EnvironmentError("[오류] FRED_API_KEY 환경변수가 설정되지 않았습니다.")
    data = _fetch(FRED_BASE, {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start,
        "observation_end": end,
    })
    obs = data.get("observations", [])
    if not obs:
        print(f"[경고] FRED {series_id}: 기간 {start}~{end} 데이터 없음")
        return pd.DataFrame()
    df = pd.DataFrame(obs)
    missing = [c for c in ["date", "value"] if c not in df.columns]
    if missing:
        print(f"[경고] FRED {series_id} 컬럼 누락: {missing}")
        return pd.DataFrame()
    df = df[["date", "value"]].copy()
    df.columns = ["price_date", "value"]
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["source_name"] = "FRED"
    df["indicator_code"] = series_id
    return df.dropna(subset=["value"])


def fetch_eia_brent(start: str, end: str) -> pd.DataFrame:
    """EIA Brent Crude 일간 시계열 수집."""
    api_key = os.environ.get("EIA_API_KEY")
    if not api_key:
        raise EnvironmentError("[오류] EIA_API_KEY 환경변수가 설정되지 않았습니다.")
    data = _fetch(EIA_BASE, {
        "api_key": api_key,
        "frequency": "daily",
        "data[0]": "value",
        "facets[product][]": "EPCBRENT",
        "start": start,
        "end": end,
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "length": 5000,
    })
    rows = data.get("response", {}).get("data", [])
    if not rows:
        print(f"[경고] EIA Brent: 기간 {start}~{end} 데이터 없음")
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    missing = [c for c in ["period", "value"] if c not in df.columns]
    if missing:
        print(f"[경고] EIA Brent 컬럼 누락: {missing}. 실제 컬럼: {list(df.columns)}")
        return pd.DataFrame()
    df = df[["period", "value"]].copy()
    df.columns = ["price_date", "value"]
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["source_name"] = "EIA"
    df["indicator_code"] = "BRENT_USD_BBL"
    return df.dropna(subset=["value"])


def fetch_bok_krw_usd(start: str, end: str) -> pd.DataFrame:
    """BOK ECOS KRW/USD 환율 수집. T+2 결제일 오프셋은 소비 측에서 적용 (MEMORY M-002)."""
    # A-078: ERROR-100(필수값 누락)의 흔한 원인 = 키 끝 공백/개행 → URL 경로 세그먼트 오염.
    #        반드시 strip. 또한 2010~2026 일별은 ~6,000행 → 요청건수 5000 초과분 잘림 → 100000.
    api_key = os.environ.get("BOK_ECOS_API_KEY", "").strip()
    if not api_key:
        raise EnvironmentError("[오류] BOK_ECOS_API_KEY 환경변수가 설정되지 않았습니다.")
    start_fmt = start.replace("-", "")
    end_fmt   = end.replace("-", "")
    url = f"{BOK_BASE}/{api_key}/json/kr/1/100000/731Y001/DD/{start_fmt}/{end_fmt}/0000001"
    data = _fetch(url, {})

    # BOK ECOS 오류 응답: 정상이면 "StatisticSearch" 키, 오류이면 "RESULT" 키
    if not data or "RESULT" in data:
        result_info = data.get("RESULT", {}) if data else {}
        code = result_info.get("CODE", "EMPTY")
        msg  = result_info.get("MESSAGE", "응답 없음")
        print(
            f"[경고] BOK ECOS API 오류 — 코드: {code}, 메시지: {msg}. "
            f"BOK_ECOS_API_KEY 또는 시리즈 코드(731Y001/0000001) 확인 필요."
        )
        return pd.DataFrame()

    rows = data.get("StatisticSearch", {}).get("row", [])
    if not rows:
        print(f"[경고] BOK ECOS: 기간 {start}~{end} 데이터 없음. API 키 또는 날짜 범위 확인.")
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    missing = [c for c in ["TIME", "DATA_VALUE"] if c not in df.columns]
    if missing:
        print(f"[경고] BOK ECOS 컬럼 누락: {missing}. 실제 컬럼: {list(df.columns)}")
        return pd.DataFrame()
    df = df[["TIME", "DATA_VALUE"]].copy()
    df.columns = ["price_date", "value"]
    df["price_date"] = pd.to_datetime(df["price_date"], format="%Y%m%d")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["source_name"] = "BOK_ECOS"
    df["indicator_code"] = "KRW_USD"
    return df.dropna(subset=["value"])


def _kosis_b64_key(raw_key: str) -> str:
    """KOSIS API는 Base64 인코딩 키 사용. 미인코딩 키 자동 변환.
    포털에서 발급된 키가 hex(평문) 또는 Base64 중 어느 형식이든 대응.
    """
    import base64 as _b64
    stripped = raw_key.strip()
    try:
        decoded = _b64.b64decode(stripped, validate=True)
        if decoded:
            return stripped  # 이미 유효한 Base64
    except Exception:
        pass
    return _b64.b64encode(stripped.encode()).decode()


def fetch_kosis_cpi_korea(start_yyyymm: str = "201001") -> pd.DataFrame:
    """KOSIS API — 한국 소비자물가지수(CPI_KOREA) 수집 (신규 URL 방식, A-070).

    구 statisticsData.do 서비스 중단 → **statisticsParameterData.do** URL 생성 방식으로 전환
    (조정자 제공 신규 키·URL). 작성기관: 국가데이터처(orgId=101).
    참조 테이블 2종:
      - DT_1J22003: 소비자물가지수(2020=100) 전국 총지수 → CPI_KOREA_TOTAL
      - DT_1J22002: 품목성질별 소비자물가지수(2020=100) → CPI_KOREA_ITEM_CLASS
    파라미터(조정자 URL): itmId=T+ · objL1(테이블별) · format=json · jsonVD=Y · prdSe=M ·
      startPrdDe=201001 · outputFields · smblChk=N · orgId=101 · tblId
    ⚠️ 키는 env KOSIS_API_KEY (Base64) — 하드코딩 금지, 노출 시 로테이션.
    """
    api_key = os.environ.get("KOSIS_API_KEY", "").strip()
    if not api_key:
        print("[경고] KOSIS_API_KEY 미등록 — CPI_KOREA 수집 건너뜀")
        return pd.DataFrame()

    b64_key = _kosis_b64_key(api_key)
    end_yyyymm = date.today().strftime("%Y%m")
    # A-078: DT(관측값)가 outputFields에 없으면 레코드는 오지만 값 파싱이 전부 None → 0건 저장.
    OUTPUT_FIELDS = "ORG_ID+TBL_ID+OBJ_ID+ITM_ID+OBJ_NM_ENG+NM_ENG+ITM_NM_ENG+UNIT_NM_ENG+PRD_SE+PRD_DE+DT+"

    # 수집 대상 테이블 (CPI 총지수 + 품목성질별). objL1은 테이블별 분류값.
    KOSIS_TABLES = [
        {"tblId": "DT_1J22003", "objL1": "T10", "label": "CPI_KOREA_TOTAL"},
        {"tblId": "DT_1J22002", "objL1": "ALL", "label": "CPI_KOREA_ITEM_CLASS"},
    ]

    all_rows: list[dict] = []
    for tbl in KOSIS_TABLES:
        try:
            raw = _fetch("https://kosis.kr/openapi/Param/statisticsParameterData.do", {
                "method":       "getList",
                "apiKey":       b64_key,
                "itmId":        "T+",
                "objL1":        tbl["objL1"],
                "objL2":        "", "objL3": "", "objL4": "",
                "objL5":        "", "objL6": "", "objL7": "", "objL8": "",
                "format":       "json",
                "jsonVD":       "Y",
                "prdSe":        "M",
                "startPrdDe":   start_yyyymm,
                "endPrdDe":     end_yyyymm,
                "outputFields": OUTPUT_FIELDS,
                "smblChk":      "N",
                "orgId":        "101",
                "tblId":        tbl["tblId"],
            })
            if not raw:
                print(f"[경고] KOSIS {tbl['tblId']}: 응답 없음")
                continue
            records = raw if isinstance(raw, list) else raw.get("data", raw.get("row", []))
            for rec in records:
                period = rec.get("PRD_DE", rec.get("prd_de", ""))
                value  = rec.get("DT", rec.get("dt", None))
                if period and value is not None:
                    all_rows.append({
                        "price_date":     pd.to_datetime(period, format="%Y%m", errors="coerce"),
                        "indicator_code": tbl["label"],
                        "value":          pd.to_numeric(str(value).replace(",", ""), errors="coerce"),
                        "source_name":    "KOSIS/국가데이터처",
                        "tbl_id":         tbl["tblId"],
                    })
            print(f"[정보] KOSIS {tbl['tblId']} ({tbl['label']}): {len(records)}건")
        except Exception as e:
            print(f"[경고] KOSIS {tbl['tblId']} 수집 실패: {e}")

    if not all_rows:
        print("[경고] KOSIS CPI 전체 수집 실패 — API 키 및 파라미터 확인 필요")
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    df["ingested_at"] = pd.Timestamp.utcnow()
    print(f"[완료] KOSIS CPI 총 {len(df)}건 ({start_yyyymm}~{end_yyyymm})")
    return df


def run(start_date: str | None = None, end_date: str | None = None) -> None:
    # 2010.01 기준선(조정자): HISTORICAL_START_YEAR 환경변수 우선, 기본 2010
    if start_date is None:
        start_date = f"{os.environ.get('HISTORICAL_START_YEAR', '2010')}-01-01"
    end   = end_date or date.today().isoformat()
    start = start_date
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y%m%d")

    def _safe(fn: Callable, *args: Any, label: str = "", **kwargs: Any) -> pd.DataFrame:
        """개별 커넥터 실패를 격리 — 단일 실패가 전체 파이프라인을 중단시키지 않음."""
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            print(f"[경고] {label or fn.__name__} 수집 실패: {e}")
            return pd.DataFrame()

    frames = [
        # ── 금리·물가 ──────────────────────────────────────────────────────────
        _safe(fetch_fred_series, "FEDFUNDS", start, end, label="FRED FEDFUNDS"),
        _safe(fetch_fred_series, "CPIAUCSL", start, end, label="FRED CPIAUCSL"),
        # ── 유가 ───────────────────────────────────────────────────────────────
        _safe(fetch_eia_brent,   start, end, label="EIA Brent"),
        # ── 환율 (원산지·결제통화) ─────────────────────────────────────────────
        _safe(fetch_bok_krw_usd, start, end, label="BOK ECOS KRW/USD"),
        _safe(fetch_fred_series, "DEXBZUS", start, end, label="FRED DEXBZUS (BRL/USD)"),
        # DEXARUE(아르헨티나 페소): FRED 미제공 — 다중 환율제도로 공식 시리즈 없음
        # 추후 BCRA(아르헨티나 중앙은행) API 또는 IMF IFS API로 대체 예정 (MEMORY D-002)
        _safe(fetch_fred_series, "DEXCHUS", start, end, label="FRED DEXCHUS (CNY/USD)"),
        _safe(fetch_fred_series, "DEXMAUS", start, end, label="FRED DEXMAUS (MYR/USD)"),
        # ── 시장 리스크 ────────────────────────────────────────────────────────
        _safe(fetch_fred_series, "VIXCLS",  start, end, label="FRED VIXCLS"),
        # ── 한국 수입 통계 (KOSIS — 연결 확인만; 실 데이터는 data.go.kr 전환 예정) ──
        _safe(fetch_kosis_cpi_korea, label="KOSIS CPI_KOREA (DT_1J22003)"),
    ]

    frames = [f for f in frames if not f.empty]
    if not frames:
        print("[경고] 경제 지표: 모든 소스 응답 없음 — API 키 및 네트워크 확인 필요")
        return

    combined = pd.concat(frames, ignore_index=True)
    combined["ingested_at"] = pd.Timestamp.utcnow()
    combined["unit"] = ""

    out = f"{OUTPUT_DIR}/economic_indicators_{today}.parquet"
    combined.to_parquet(out, index=False)
    print(f"[완료] 경제 지표 {len(combined)}건 저장 → {out}")


if __name__ == "__main__":
    run()
