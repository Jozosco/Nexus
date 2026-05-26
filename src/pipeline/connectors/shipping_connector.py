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
from datetime import date

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


def fetch_bdi_te() -> pd.DataFrame:
    """Trading Economics에서 BDI 히스토리 수집 (2020-01-01~현재).

    getMarketsHistorical()로 일별 시계열 수집 — z-score 분석에 충분한 기간 확보.
    TRADING_ECONOMICS_API_KEY 미등록 시 빈 DataFrame 반환 (BCAA는 TE 미제공).
    """
    try:
        from src.pipeline.connectors.te_connector import fetch_bdi  # type: ignore
        return fetch_bdi()
    except ImportError:
        pass

    te_key = os.environ.get("TRADING_ECONOMICS_API_KEY", "").strip()
    if not te_key:
        print("[정보] TRADING_ECONOMICS_API_KEY 미등록 — BDI TE 수집 건너뜀")
        return pd.DataFrame()

    start_date = "2020-01-01"
    end_date   = date.today().isoformat()

    try:
        import tradingeconomics as te  # type: ignore
        te.login(te_key)

        for symbol in ("bdi", "BDI", "baltic"):
            try:
                # 히스토리 범위 조회 (2020-01-01 ~ 오늘)
                result = te.getMarketsHistorical(
                    symbols=symbol, d1=start_date, d2=end_date, output_type="df"
                )
                if result is not None and len(result) > 0:
                    date_col  = next((c for c in ["Date", "DateTime", "date"] if c in result.columns), None)
                    value_col = next((c for c in ["Close", "Last", "Value"] if c in result.columns), None)
                    if date_col and value_col:
                        df = pd.DataFrame({
                            "price_date":     pd.to_datetime(result[date_col], errors="coerce"),
                            "value":          pd.to_numeric(result[value_col], errors="coerce"),
                            "source_name":    "TradingEconomics/BalticExchange",
                            "indicator_code": "BDI",
                            "unit":           "points",
                            "note":           f"[TE-OFFICIAL: C-03 z-score 모니터링 | 히스토리 {start_date}~{end_date}]",
                            "ingested_at":    pd.Timestamp.utcnow(),
                        }).dropna(subset=["price_date", "value"])
                        print(f"[완료] BDI 히스토리 {len(df)}건 수집 ({start_date}~{end_date})")
                        return df
            except Exception as inner_e:
                print(f"[경고] TE getMarketsHistorical({symbol}) 실패: {inner_e} — 최신값 폴백 시도")
                # 폴백: 최신 단일 데이터
                try:
                    result = te.getMarketsBySymbol(symbols=symbol, output_type="df")
                    if result is not None and len(result) > 0:
                        date_col  = next((c for c in ["DateTime", "Date", "date"] if c in result.columns), None)
                        value_col = next((c for c in ["Last", "Close", "Value"] if c in result.columns), None)
                        if date_col and value_col:
                            print(f"[경고] BDI 히스토리 조회 실패 — 최신 단일 레코드 반환")
                            return pd.DataFrame({
                                "price_date":     pd.to_datetime(result[date_col], errors="coerce"),
                                "value":          pd.to_numeric(result[value_col], errors="coerce"),
                                "source_name":    "TradingEconomics/BalticExchange",
                                "indicator_code": "BDI",
                                "unit":           "points",
                                "note":           "[TE-OFFICIAL: 폴백 — 최신 단일 레코드 (히스토리 조회 실패)]",
                                "ingested_at":    pd.Timestamp.utcnow(),
                            }).dropna(subset=["price_date", "value"])
                except Exception:
                    continue
    except Exception as e:
        print(f"[경고] TE BDI 수집 실패: {e}")
    return pd.DataFrame()


def run() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y%m%d")
    frames = []

    # BCAA: 식물성유지 탱커 운임 (Perplexity 프록시 — TE 미제공)
    bcaa = fetch_bcaa()
    if not bcaa.empty:
        frames.append(bcaa)

    # BDI: C-03 구조적 단절 모니터링 변수 (Trading Economics 공식 API)
    bdi = fetch_bdi_te()
    if not bdi.empty:
        frames.append(bdi)

    if not frames:
        print("[경고] 해운 지수 수집 실패 — PERPLEXITY_API_KEY 및 TRADING_ECONOMICS_API_KEY 확인.")
        return

    df = pd.concat(frames, ignore_index=True)
    out = f"{OUTPUT_DIR}/shipping_indices_{today}.parquet"
    df.to_parquet(out, index=False)
    print(f"[완료] 해운 지수 {len(df)}건 저장 → {out}")


if __name__ == "__main__":
    run()
