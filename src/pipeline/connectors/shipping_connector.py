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

    bcaa_match = re.search(r"BCAA[:\s]+([0-9,\.]+)", text, re.IGNORECASE)
    if bcaa_match:
        rows.append({
            "price_date":     today,
            "source_name":    "Perplexity/BalticExchange",
            "indicator_code": "BCAA",
            "value":          float(bcaa_match.group(1).replace(",", "")),
            "unit":           "USD/MT",
            "note":           "[PERPLEXITY-PROXY: BCAA — 식물성유지 탱커 지수 (2025-02 출시)]",
        })

    bcti_match = re.search(r"BCTI[:\s]+([0-9,\.]+)", text, re.IGNORECASE)
    if bcti_match:
        rows.append({
            "price_date":     today,
            "source_name":    "Perplexity/BalticExchange",
            "indicator_code": "BCTI",
            "value":          float(bcti_match.group(1).replace(",", "")),
            "unit":           "points",
            "note":           "[PERPLEXITY-PROXY: BCTI — BCAA 직접 조회 불가 시 대리 지수]",
        })

    if not rows:
        print(f"[경고] BCAA/BCTI 파싱 실패. 원문: {text[:200]}")

    df = pd.DataFrame(rows)
    if not df.empty:
        df["price_date"]  = pd.to_datetime(df["price_date"])
        df["ingested_at"] = pd.Timestamp.utcnow()
    return df


def run() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y%m%d")
    df = fetch_bcaa()
    out = f"{OUTPUT_DIR}/shipping_indices_{today}.parquet"
    df.to_parquet(out, index=False)
    print(f"[완료] 해운 지수 {len(df)}건 저장 → {out}")


if __name__ == "__main__":
    run()
