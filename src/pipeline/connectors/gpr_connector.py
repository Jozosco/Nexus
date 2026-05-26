"""
지정학 리스크 지수 커넥터 — WBS 1.1.6
수집 대상: Caldara & Iacoviello GPR Index (공개) · Perplexity 실시간 지정학 뉴스
실행 환경: VS Code Web (Azure ML Studio) 또는 GitHub Actions
"""

from __future__ import annotations

import io
import os
import re
from datetime import date

import httpx
import pandas as pd
from openai import OpenAI

OUTPUT_DIR = "data/raw"
GPR_CSV_URL = "https://www.policyuncertainty.com/media/GPR_Web_latest.xlsx"
PERPLEXITY_MODEL = "sonar-pro"  # MEMORY L-006/L-007


def _fetch_gpr_index() -> pd.DataFrame:
    """Caldara & Iacoviello GPR Index 공개 엑셀 다운로드 (API 키 불필요)."""
    try:
        r = httpx.get(GPR_CSV_URL, timeout=60, follow_redirects=True)
        r.raise_for_status()
        df_raw = pd.read_excel(io.BytesIO(r.content))
        # 컬럼 구조: Year, Month, GPRH (historical), GPR (점수)
        df_raw.columns = [str(c).strip() for c in df_raw.columns]

        # Year/Month 컬럼 탐지 (컬럼명이 다를 수 있음)
        year_col  = next((c for c in df_raw.columns if "year"  in c.lower()), None)
        month_col = next((c for c in df_raw.columns if "month" in c.lower()), None)
        gpr_col   = next((c for c in df_raw.columns if c.upper() in ("GPR", "GPRD")), None)

        if not (year_col and month_col and gpr_col):
            print(f"[경고] GPR 엑셀 컬럼 구조 변경 감지. 실제 컬럼: {list(df_raw.columns)}")
            return pd.DataFrame()

        df = df_raw[[year_col, month_col, gpr_col]].dropna()
        df["price_date"] = pd.to_datetime(
            df[year_col].astype(int).astype(str) + "-" +
            df[month_col].astype(int).astype(str).str.zfill(2) + "-01"
        )
        df = df[["price_date", gpr_col]].rename(columns={gpr_col: "value"})
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df["source_name"]     = "Caldara_Iacoviello"
        df["indicator_code"]  = "GPR"
        df["unit"]            = "index (baseline≈100)"
        df["ingested_at"]     = pd.Timestamp.utcnow()
        df = df.dropna(subset=["value"])
        # 수집 범위 표준화: 2020-01-01 이후 (다른 커넥터와 통일)
        df = df[df["price_date"] >= pd.Timestamp("2020-01-01")]
        return df
    except Exception as e:
        print(f"[경고] GPR 인덱스 다운로드 실패: {e}")
        return pd.DataFrame()


def _fetch_gpr_realtime() -> pd.DataFrame:
    """Perplexity 실시간 검색으로 GPR 최신 동향 수집."""
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        print("[경고] PERPLEXITY_API_KEY 미등록 — 지정학 실시간 수집 건너뜀.")
        return pd.DataFrame()

    client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
    prompt = (
        "What is the current Geopolitical Risk (GPR) index level? "
        "Also provide the latest GPR score if available. "
        "Format: GPR: [numeric value] ([source/date]). "
        "If exact GPR index is unavailable, provide qualitative assessment: HIGH/MEDIUM/LOW."
    )
    try:
        r = client.chat.completions.create(
            model=PERPLEXITY_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        text = r.choices[0].message.content
        today = date.today().isoformat()

        rows = []
        gpr_match = re.search(r"GPR[:\s]+([0-9]+\.?[0-9]*)", text, re.IGNORECASE)
        if gpr_match:
            rows.append({
                "price_date":     today,
                "source_name":    "Perplexity/GPR",
                "indicator_code": "GPR_REALTIME",
                "value":          float(gpr_match.group(1)),
                "unit":           "index (baseline≈100)",
                "note":           "[PERPLEXITY-PROXY]",
            })

        level_match = re.search(r"\b(HIGH|MEDIUM|LOW)\b", text, re.IGNORECASE)
        if level_match and not gpr_match:
            level_map = {"HIGH": 250.0, "MEDIUM": 150.0, "LOW": 80.0}
            level = level_match.group(1).upper()
            rows.append({
                "price_date":     today,
                "source_name":    "Perplexity/GPR",
                "indicator_code": "GPR_QUALITATIVE",
                "value":          level_map[level],
                "unit":           "index (baseline≈100)",
                "note":           f"[QUALITATIVE:{level}]",
            })

        if not rows:
            print(f"[경고] GPR 실시간 파싱 실패. 원문: {text[:200]}")

        df = pd.DataFrame(rows)
        if not df.empty:
            df["price_date"] = pd.to_datetime(df["price_date"])
            df["ingested_at"] = pd.Timestamp.utcnow()
        return df
    except Exception as e:
        print(f"[경고] Perplexity GPR 수집 실패: {e}")
        return pd.DataFrame()


def _fetch_hormuz_realtime() -> pd.DataFrame:
    """Perplexity 실시간 호르무즈 해협 모니터링.

    Inspired by Globot early-warning methodology (github.com/Vector897/Globot):
    AIS 선박 이상 · AWRP 보험료 급등 · 이란-미국 긴장 신호
    SBO 관련성: 호르무즈 봉쇄 → 유가 급등 → 벙커유 비용 → CFR 운임 프리미엄 + 3~8%
    """
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        print("[경고] PERPLEXITY_API_KEY 미등록 — 호르무즈 모니터링 건너뜀.")
        return pd.DataFrame()

    client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
    prompt = (
        "Provide the latest risk assessment for the Strait of Hormuz for tanker shipping. "
        "Include: "
        "(1) Current threat level for tanker traffic: HIGH / MEDIUM / LOW, "
        "(2) Any IRGC or Houthi vessel incidents in the past 7 days (Yes/No + brief), "
        "(3) War risk premium surcharge multiplier vs baseline (e.g. 2x, 3x, 5x), "
        "(4) Any tanker re-routing to Cape of Good Hope reported this week (count or None). "
        "Format each item as: METRIC: [name] | VALUE: [value] | SOURCE: [source] | DATE: [date]"
    )
    today = date.today().isoformat()
    try:
        r = client.chat.completions.create(
            model=PERPLEXITY_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        text = r.choices[0].message.content
        rows = []

        # Threat level → numeric encoding
        threat_match = re.search(r"METRIC:[^|]*(?:threat|level)[^|]*\|[^|]*VALUE:\s*(HIGH|MEDIUM|LOW)", text, re.IGNORECASE)
        if threat_match:
            level_map = {"HIGH": 3.0, "MEDIUM": 2.0, "LOW": 1.0}
            level = threat_match.group(1).upper()
            rows.append({
                "price_date":     today,
                "source_name":    "Perplexity/Hormuz",
                "indicator_code": "HORMUZ_THREAT_LEVEL",
                "value":          level_map[level],
                "unit":           "1=Low/2=Med/3=High",
                "note":           f"[QUALITATIVE:{level}]",
            })

        # AWRP multiplier
        awrp_match = re.search(
            r"METRIC:[^|]*(?:premium|AWRP|war risk)[^|]*\|[^|]*VALUE:\s*([0-9]+\.?[0-9]*)\s*[xX×]?",
            text, re.IGNORECASE
        )
        if awrp_match:
            rows.append({
                "price_date":     today,
                "source_name":    "Perplexity/Hormuz",
                "indicator_code": "HORMUZ_AWRP_MULTIPLIER",
                "value":          float(awrp_match.group(1)),
                "unit":           "× baseline AWRP",
                "note":           "[PERPLEXITY-PROXY]",
            })

        if not rows:
            print(f"[경고] Hormuz 파싱 실패. 원문: {text[:200]}")
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        df["price_date"] = pd.to_datetime(df["price_date"])
        df["ingested_at"] = pd.Timestamp.utcnow()
        return df
    except Exception as e:
        print(f"[경고] Hormuz 실시간 수집 실패: {e}")
        return pd.DataFrame()


def _fetch_policy_news_proxy() -> pd.DataFrame:
    """Perplexity 실시간 검색 — 대두유 가격 주요 정책·수급 뉴스 4종.

    ARG_EXPORT_TAX_NEWS:   아르헨티나 대두유 수출세 동향
    INDIA_DUTY_NEWS:       인도 식용유 수입관세 변동
    BIODIESEL_MANDATE_NEWS: 인도네시아·말레이시아 바이오디젤 의무혼합 정책
    WASDE_CONSENSUS_SCORE: USDA WASDE 발표 전 컨센서스 및 시장 서프라이즈 스코어
    """
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        print("[경고] PERPLEXITY_API_KEY 미등록 — 정책 뉴스 프록시 수집 건너뜀.")
        return pd.DataFrame()

    client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
    today = date.today().isoformat()

    queries: list[tuple[str, str, str, str]] = [
        (
            "ARG_EXPORT_TAX_NEWS",
            (
                "What is the current Argentina soybean oil export tax rate (retenciones)? "
                "Has there been any change or announcement in the past 30 days? "
                "Format: RATE: [percentage]% | CHANGE: [increase/decrease/unchanged] | "
                "DATE: [date of latest change or news] | SOURCE: [source name]"
            ),
            "% retenciones",
            "아르헨티나 대두유 수출세",
        ),
        (
            "INDIA_DUTY_NEWS",
            (
                "What is the current India import duty rate on refined soybean oil (HS 1507.90)? "
                "Has there been any change in the past 60 days? Include basic customs duty + AIDC + GST if available. "
                "Format: DUTY_RATE: [total %] | CHANGE: [increase/decrease/unchanged] | "
                "DATE: [latest change date] | SOURCE: [source name]"
            ),
            "% import duty",
            "인도 식용유 수입관세",
        ),
        (
            "BIODIESEL_MANDATE_NEWS",
            (
                "What are the current biodiesel blending mandates for Indonesia and Malaysia? "
                "Any policy change or announcement in the past 60 days? "
                "Format: INDONESIA: B[number]% mandate | MALAYSIA: B[number]% mandate | "
                "CHANGE: [yes/no + brief description] | DATE: [latest news date] | SOURCE: [source]"
            ),
            "B% mandate",
            "인도네시아·말레이시아 바이오디젤 의무",
        ),
        (
            "WASDE_CONSENSUS_SCORE",
            (
                "What is the latest USDA WASDE report release date and the market consensus vs actual "
                "for global soybean oil ending stocks or production? Was the report bullish or bearish vs consensus? "
                "Format: REPORT_DATE: [date] | CONSENSUS: [value + unit] | ACTUAL: [value + unit] | "
                "SURPRISE: [bullish/bearish/neutral] | SOURCE: [source]"
            ),
            "surprise score",
            "USDA WASDE 컨센서스",
        ),
    ]

    rows: list[dict] = []
    for indicator_code, prompt, unit_hint, label_kr in queries:
        try:
            r = client.chat.completions.create(
                model=PERPLEXITY_MODEL,
                messages=[{"role": "user", "content": prompt}],
            )
            text = r.choices[0].message.content

            # 숫자 추출 — 응답 첫 번째 숫자를 대표값으로 사용
            num_match = re.search(r"(\d+\.?\d*)", text)
            value = float(num_match.group(1)) if num_match else float("nan")

            rows.append({
                "price_date":     today,
                "source_name":    "Perplexity/PolicyProxy",
                "indicator_code": indicator_code,
                "value":          value,
                "unit":           unit_hint,
                "note":           f"[PERPLEXITY-PROXY: {label_kr}] {text[:300]}",
            })
        except Exception as e:
            print(f"[경고] {indicator_code} 수집 실패: {e}")

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["ingested_at"] = pd.Timestamp.utcnow()
    return df


def run() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y%m%d")

    # BACKFILL_MODE=true: Perplexity 실시간 함수(오늘 날짜만 반환) 건너뜀
    # 과거 데이터 수집에는 C&I 공개 xlsx 히스토리만 사용
    backfill_mode = os.environ.get("BACKFILL_MODE", "").lower() == "true"

    if backfill_mode:
        print("[정보] BACKFILL_MODE 활성화 — Perplexity 실시간 수집 건너뜀 (역사 데이터만 수집)")
        frames = [_fetch_gpr_index()]
    else:
        frames = [
            _fetch_gpr_index(),
            _fetch_gpr_realtime(),
            _fetch_hormuz_realtime(),
            _fetch_policy_news_proxy(),
        ]

    frames = [f for f in frames if not f.empty]
    if not frames:
        print("[경고] GPR 데이터: 수집된 항목 없음")
        return

    combined = pd.concat(frames, ignore_index=True)
    out = f"{OUTPUT_DIR}/geopolitical_indices_{today}.parquet"
    combined.to_parquet(out, index=False)
    print(f"[완료] 지정학 리스크 데이터 {len(combined)}건 저장 → {out}")


if __name__ == "__main__":
    run()
