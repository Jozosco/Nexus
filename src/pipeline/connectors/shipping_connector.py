"""
해운 지수 커넥터 — WBS 1.1.3
수집 대상: BCAA (Baltic Chemical and Agricultural Oil Assessments) — 식물성 유지 탱커 전용
방법: Perplexity Pro 실시간 검색 (Baltic Exchange/ICE 직접 API = 유료 기업 구독)

제외 근거:
  - BDI (Baltic Dry Index): 건화물 지수 — 대두유(액체 벌크)와 무관
  - SCFI/FBX/WCI/HRCI: 컨테이너 운임 지수 — 대두유는 탱커 선박 수송
  - BCAA: 2025년 2월 Baltic Exchange 출시, 식물성 유지 탱커 전용 (CPO·SBO·팜올레인 경로 포함)
    → 직접 API: Baltic Exchange/ICE 기업 구독 필요 (MEMORY A-013)
    → 현행: Perplexity 프록시로 최신값 수집

실행 환경: VS Code Web (Azure ML Studio) 또는 GitHub Actions
"""

from __future__ import annotations

import os
import re
import time
from datetime import date

import httpx
import pandas as pd
from openai import OpenAI

OUTPUT_DIR = "data/raw"
PERPLEXITY_MODEL = "sonar-pro"  # MEMORY L-006/L-007: 상수 사용, 하드코딩 금지


def _perplexity_client() -> OpenAI:
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        raise EnvironmentError("[오류] PERPLEXITY_API_KEY 환경변수가 설정되지 않았습니다.")
    return OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")


def fetch_bcaa() -> pd.DataFrame:
    """Perplexity 실시간 검색으로 BCAA 최신 값 수집.

    BCAA(Baltic Chemical and Agricultural Oil Assessments): 2025년 2월 출시.
    식물성 유지(대두유·팜유·팜올레인) 탱커 운임 전용 지수.
    직접 API는 Baltic Exchange/ICE 기업 구독 필요 — Perplexity 프록시로 대체.
    """
    client = _perplexity_client()
    prompt = (
        "Provide the latest BCAA (Baltic Chemical and Agricultural Oil Assessments) index value. "
        "BCAA is the Baltic Exchange's vegetable oil tanker freight assessment launched February 2025. "
        "If BCAA is unavailable, provide the latest Baltic Clean Tanker Index (BCTI) as a proxy. "
        "Format: BCAA: [value] ([date]) or BCTI: [value] ([date]). "
        "Use exact numeric values only."
    )
    r = client.chat.completions.create(
        model=PERPLEXITY_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    text = r.choices[0].message.content

    rows = []
    today = date.today().isoformat()

    # BCAA: 다양한 응답 형식 대응 ("BCAA: 1234", "BCAA index is 1,234", "BCAA stood at 1234.5")
    bcaa_match = re.search(
        r"BCAA[^0-9\n]{0,40}?(\d[\d,\.]*)",
        text, re.IGNORECASE
    )
    if bcaa_match:
        rows.append({
            "price_date":     today,
            "source_name":    "Perplexity/BalticExchange",
            "indicator_code": "BCAA",
            "value":          float(bcaa_match.group(1).replace(",", "")),
            "unit":           "USD/MT",
            "note":           "[PERPLEXITY-PROXY: BCAA — 식물성유지 탱커 지수 (2025-02 출시)]",
        })

    # BCTI: 다양한 응답 형식 대응
    bcti_match = re.search(
        r"BCTI[^0-9\n]{0,40}?(\d[\d,\.]*)",
        text, re.IGNORECASE
    )
    if bcti_match:
        rows.append({
            "price_date":     today,
            "source_name":    "Perplexity/BalticExchange",
            "indicator_code": "BCTI",
            "value":          float(bcti_match.group(1).replace(",", "")),
            "unit":           "points",
            "note":           "[PERPLEXITY-PROXY: BCTI — BCAA 직접 조회 불가 시 대리 지수]",
        })

    # 마지막 폴백: "Baltic" + 숫자가 포함된 경우 BCTI 추정값으로 사용
    if not rows:
        baltic_match = re.search(
            r"(?:Baltic[^\n]{0,60}?)(\d{3,5}(?:\.\d+)?)",
            text, re.IGNORECASE
        )
        if baltic_match:
            rows.append({
                "price_date":     today,
                "source_name":    "Perplexity/BalticExchange",
                "indicator_code": "BCTI_PROXY",
                "value":          float(baltic_match.group(1).replace(",", "")),
                "unit":           "points",
                "note":           "[PERPLEXITY-PROXY: Baltic 키워드 근처 추출값 — 해석 주의]",
            })

    if not rows:
        print(f"[경고] BCAA/BCTI 파싱 실패. 원문: {text[:300]}")

    df = pd.DataFrame(rows)
    if not df.empty:
        df["price_date"]  = pd.to_datetime(df["price_date"])
        df["ingested_at"] = pd.Timestamp.utcnow()
    return df


def fetch_bdi_te(start_date: str | None = None, end_date: str | None = None) -> pd.DataFrame:
    """Trading Economics REST API 직접 호출로 BDI 히스토리 수집.

    SDK의 getMarketsHistorical()은 설치된 TE 버전에서 미지원 (MEMORY A-034).
    pandas 2.0과 구형 TE SDK의 deprecate_kwarg() 호환성 오류도 동시 해소.
    REST: GET https://api.tradingeconomics.com/markets/historical/{symbol}
    파라미터: c={api_key}&d1={start}&d2={end}&f=json
    """
    te_key = os.environ.get("TRADING_ECONOMICS_API_KEY", "").strip()
    if not te_key:
        print("[정보] TRADING_ECONOMICS_API_KEY 미등록 — BDI TE REST 수집 건너뜀")
        return pd.DataFrame()

    _start = start_date or "2020-01-01"
    _end   = end_date or date.today().isoformat()

    for symbol in ("BDI", "BALTDRYIDX", "bdi"):
        try:
            url = f"https://api.tradingeconomics.com/markets/historical/{symbol}"
            params = {"c": te_key, "d1": _start, "d2": _end, "f": "json"}
            r = httpx.get(url, params=params, timeout=30)
            if r.status_code == 401:
                print("[경고] TE API 401 인증 실패 — TRADING_ECONOMICS_API_KEY 값 확인 필요")
                return pd.DataFrame()
            if r.status_code == 403:
                print("[경고] TE API 403 권한 없음 — TE 구독 플랜에서 Markets Historical 포함 확인")
                return pd.DataFrame()
            r.raise_for_status()
            data = r.json()
            if not data or not isinstance(data, list):
                print(f"[경고] TE REST BDI({symbol}): 빈 응답 — 다음 심볼 시도")
                continue
            df_raw = pd.DataFrame(data)
            date_col  = next((c for c in ["Date", "DateTime", "date"] if c in df_raw.columns), None)
            value_col = next((c for c in ["Close", "Last", "close", "Value"] if c in df_raw.columns), None)
            if not date_col or not value_col:
                print(f"[경고] TE REST BDI({symbol}): 예상 컬럼 없음 ({list(df_raw.columns)[:5]})")
                continue
            df = pd.DataFrame({
                "price_date":     pd.to_datetime(df_raw[date_col], errors="coerce"),
                "value":          pd.to_numeric(df_raw[value_col], errors="coerce"),
                "source_name":    "TradingEconomics/BalticExchange",
                "indicator_code": "BDI",
                "unit":           "points",
                "note":           f"[TE-REST: BDI 히스토리 ({_start}~{_end}) — SDK 미사용 직접 호출]",
                "ingested_at":    pd.Timestamp.utcnow(),
            }).dropna(subset=["price_date", "value"])
            if not df.empty:
                print(f"[완료] TE REST BDI {len(df)}건 수집 ({symbol}, {_start}~{_end})")
                return df.sort_values("price_date").reset_index(drop=True)
        except httpx.HTTPStatusError as e:
            print(f"[경고] TE REST BDI({symbol}) HTTP {e.response.status_code}: {e}")
            continue
        except Exception as e:
            print(f"[경고] TE REST BDI({symbol}) 실패: {e}")
            continue

    print("[경고] TE REST BDI 전체 심볼 실패 — stooq 폴백으로 전환")
    return pd.DataFrame()


def fetch_bdi_stooq(start_date: str = "2020-01-01") -> pd.DataFrame:
    """pandas-datareader stooq를 통한 BDI 히스토리 폴백 (Trading Economics 키 미등록 시).

    stooq.com 무료 데이터 — API 키 불필요. BDI 심볼: ^BDI 또는 BCOM:IN.
    TE 히스토리 조회 실패 또는 키 미등록 시에만 호출.
    """
    try:
        from pandas_datareader import data as pdr  # type: ignore
        end = date.today().isoformat()
        # stooq BDI 심볼: ^BDI (stooq 인덱스 형식). BCOM:IN은 Bloomberg 상품 지수 — 잘못된 심볼이었음.
        for symbol in ("BDI", "^BDI", "BALT:IN"):
            try:
                df_raw = pdr.get_data_stooq(symbol, start=start_date, end=end)
                if df_raw is not None and not df_raw.empty:
                    close_col = next((c for c in ["Close", "close", "Zamkniecie"] if c in df_raw.columns), None)
                    if close_col:
                        df = pd.DataFrame({
                            "price_date":     pd.to_datetime(df_raw.index),
                            "value":          pd.to_numeric(df_raw[close_col], errors="coerce"),
                            "source_name":    "stooq/BalticExchange",
                            "indicator_code": "BDI",
                            "unit":           "points",
                            "note":           f"[STOOQ-FREE: BDI 히스토리 ({start_date}~{end})]",
                            "ingested_at":    pd.Timestamp.utcnow(),
                        }).dropna(subset=["price_date", "value"])
                        if not df.empty:
                            print(f"[완료] BDI stooq 히스토리 {len(df)}건 ({symbol})")
                            return df.sort_values("price_date")
            except Exception as inner_e:
                print(f"[경고] stooq {symbol} 실패: {inner_e}")
                continue
    except ImportError:
        print("[경고] pandas-datareader 미설치 — pip install pandas-datareader")
    return pd.DataFrame()


def run() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y%m%d")
    frames = []

    # BACKFILL_MODE=true: Perplexity BCAA(오늘만 반환) 건너뜀 — 역사 데이터는 TE/stooq BDI만 사용
    backfill_mode = os.environ.get("BACKFILL_MODE", "").lower() == "true"

    if backfill_mode:
        print("[정보] BACKFILL_MODE 활성화 — Perplexity BCAA 수집 건너뜀 (BDI 역사 데이터만 수집)")
    else:
        # BCAA: 식물성유지 탱커 운임 (Perplexity 프록시 — TE 미제공)
        try:
            bcaa = fetch_bcaa()
            if not bcaa.empty:
                frames.append(bcaa)
        except EnvironmentError:
            print("[경고] PERPLEXITY_API_KEY 미등록 — BCAA 수집 건너뜀")

    # BDI: C-03 구조적 단절 모니터링 (Trading Economics REST API → stooq 폴백)
    hist_start = f"{os.environ.get('HISTORICAL_START_YEAR', '2020')}-01-01"
    bdi = fetch_bdi_te(start_date=hist_start)
    if not bdi.empty:
        frames.append(bdi)
    else:
        print(f"[정보] TE BDI 미수집 — stooq 폴백 시도 ({hist_start}~)")
        bdi_stooq = fetch_bdi_stooq(start_date=hist_start)
        if not bdi_stooq.empty:
            frames.append(bdi_stooq)

    if not frames:
        print("[경고] 해운 지수 수집 실패 — PERPLEXITY_API_KEY 및 TRADING_ECONOMICS_API_KEY 확인.")
        return

    df = pd.concat(frames, ignore_index=True)
    out = f"{OUTPUT_DIR}/shipping_indices_{today}.parquet"
    df.to_parquet(out, index=False)
    print(f"[완료] 해운 지수 {len(df)}건 저장 → {out}")


if __name__ == "__main__":
    run()
