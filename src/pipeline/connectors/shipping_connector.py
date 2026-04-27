"""
해운 지수 커넥터 — WBS 1.1.3
수집 대상: BDI (Baltic Dry Index) · SCFI (Shanghai Containerized Freight Index)
방법: Perplexity Pro 실시간 검색 (B-003 블로커: Baltic Exchange 직접 API 유료)
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


def fetch_bdi_scfi() -> pd.DataFrame:
    """Perplexity 실시간 검색으로 BDI·SCFI 최신 값 수집."""
    client = _perplexity_client()
    prompt = (
        "Provide the latest Baltic Dry Index (BDI) and Shanghai Containerized Freight Index (SCFI) values. "
        "Format your response as: BDI: [value] ([date]) | SCFI: [value] ([date]). "
        "Use exact numeric values only."
    )
    r = client.chat.completions.create(
        model=PERPLEXITY_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    text = r.choices[0].message.content

    rows = []
    today = date.today().isoformat()

    bdi_match = re.search(r"BDI[:\s]+([0-9,]+)", text, re.IGNORECASE)
    if bdi_match:
        rows.append({
            "price_date": today, "source_name": "Perplexity/BalticExchange",
            "indicator_code": "BDI", "value": float(bdi_match.group(1).replace(",", "")),
            "unit": "points", "note": "[PERPLEXITY-PROXY: B-003 블로커]",
        })

    scfi_match = re.search(r"SCFI[:\s]+([0-9,]+)", text, re.IGNORECASE)
    if scfi_match:
        rows.append({
            "price_date": today, "source_name": "Perplexity/SSE",
            "indicator_code": "SCFI", "value": float(scfi_match.group(1).replace(",", "")),
            "unit": "points", "note": "[PERPLEXITY-PROXY: B-003 블로커]",
        })

    if not rows:
        print(f"[경고] BDI/SCFI 파싱 실패. 원문: {text[:200]}")

    df = pd.DataFrame(rows)
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["ingested_at"] = pd.Timestamp.utcnow()
    return df


def run() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y%m%d")
    df = fetch_bdi_scfi()
    out = f"{OUTPUT_DIR}/shipping_indices_{today}.parquet"
    df.to_parquet(out, index=False)
    print(f"[완료] 해운 지수 {len(df)}건 저장 → {out}")


if __name__ == "__main__":
    run()
