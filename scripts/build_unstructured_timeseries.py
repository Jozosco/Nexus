#!/usr/bin/env python3
"""
비정형 신호 시계열화 (WBS 1.1.53 · 비정형 → 정형 통합 분석 1단계)

목적(조정자 Req): 요약·정제된 비정형 산출물(GAIN 판독 parquet + FAO/GAIN 코퍼스 인덱스)을
월별 시계열 지표로 변환해, Historical Analysis Pipeline의 G1 통합 분석이 정형 지표와 함께
소비할 수 있게 한다.

입력:
  data/raw/gain_historical.parquet               (ingest_gain_pdf.py — 문서별 신호 태그)
  data/processed/unstructured_index_fao.csv      (summarize_pdfs.py — FAO 코퍼스 인덱스)
  data/processed/unstructured_index_gain.csv     (summarize_pdfs.py — GAIN 코퍼스 인덱스)

출력: data/raw/unstructured_signals_historical.parquet (표준 롱포맷)
  UNSTR_GAIN_{TAG}   : 월별 신호 태그 문서 수 (doc_count)
  UNSTR_FAO_{TAG}    : 월별 신호 태그 문서 수 (doc_count)
  UNSTR_GAIN_TONE    : 월별 방향성 톤 평균 (bull-bear)/(bull+bear) ∈ [-1, 1]
  UNSTR_FAO_TONE     : 동일 (FAO)

원칙: 키워드 기반 자동 신호(Phase A) — LLM 정밀 ABSA(P1-05 Phase B)의 선행 지표.
      원문에 없는 값 추정 금지 · 결측 월은 0이 아니라 미기록(무보간, D4).
의존성: pandas · pyarrow
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

# as-of 헬퍼 로드 — 스크립트 직접 실행 시 저장소 루트를 경로에 추가
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from src.pipeline.asof import attach_asof  # noqa: E402

GAIN_PARQUET = Path("data/raw/gain_historical.parquet")
IDX_FAO      = Path("data/processed/unstructured_index_fao.csv")
IDX_GAIN     = Path("data/processed/unstructured_index_gain.csv")
OUT_PARQUET  = Path("data/raw/unstructured_signals_historical.parquet")

# FAO 파일명 규칙: '19년 6월_Market Monitor Issue.pdf'
_FAO_DATE = re.compile(r"(\d{2})년\s*(\d{1,2})월")


def _as_bool(series: pd.Series) -> pd.Series:
    """CSV의 'False' 문자열을 True로 오인하지 않도록 명시적으로 변환한다."""
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False).astype(bool)
    return series.astype("string").str.strip().str.lower().isin({"true", "1", "yes"})


def _records_from_gain_parquet() -> list[dict]:
    """GAIN 판독 parquet → 월별 신호 태그 카운트."""
    if not GAIN_PARQUET.exists():
        print(f"[정보] {GAIN_PARQUET} 없음 — GAIN 신호 건너뜀")
        return []
    df = pd.read_parquet(GAIN_PARQUET)
    tags = df["signal_tags"].fillna("").astype(str).str.strip()
    df = df[_as_bool(df["readable"]) & tags.ne("")].copy()
    if df.empty:
        return []
    df["price_date"] = pd.to_datetime(df["price_date"]).dt.to_period("M").dt.to_timestamp()
    df["tag"] = df["signal_tags"].fillna("").astype(str).str.split(",")
    long = df.explode("tag")
    long["tag"] = long["tag"].str.strip()
    long = long[long["tag"].str.len() > 0]
    grp = long.groupby(["price_date", "tag"]).size().reset_index(name="value")
    return [
        {"price_date": r.price_date, "indicator_code": f"UNSTR_GAIN_{r.tag}",
         "value": float(r.value), "unit": "doc_count",
         "source_name": "USDA_FAS_GAIN_PDF", "note": "월별 신호 태그 문서 수"}
        for r in grp.itertuples()
    ]


def _month_from_index_row(target: str, path_str: str, file_name: str) -> pd.Timestamp | None:
    """코퍼스 인덱스 행에서 발행 연·월 추출 (FAO=파일명, GAIN=경로 {YYYY}/{MM})."""
    if target == "fao":
        m = _FAO_DATE.search(file_name)
        if not m:
            return None
        mo = int(m.group(2))
        if not 1 <= mo <= 12:      # A-159: 파일명 오기가 month must be in 1..12 크래시 유발
            return None
        return pd.Timestamp(year=2000 + int(m.group(1)), month=mo, day=1)
    m = re.search(r"/(\d{4})/(\d{2})/", path_str.replace("\\", "/"))
    if not m:
        return None
    mo = int(m.group(2))
    if not 1 <= mo <= 12:          # A-159: 동일 방어 — 잘못된 행은 결측으로
        return None
    return pd.Timestamp(year=int(m.group(1)), month=mo, day=1)


def _records_from_index(target: str, idx_path: Path, source_name: str) -> list[dict]:
    """코퍼스 인덱스 CSV → 월별 신호 카운트 + 톤 평균."""
    if not idx_path.exists():
        print(f"[정보] {idx_path} 없음 — {target} 인덱스 건너뜀")
        return []
    df = pd.read_csv(idx_path)
    needed = {"file", "path", "readable", "signals", "bull", "bear"}
    if not needed.issubset(df.columns):
        print(f"[경고] {idx_path} 컬럼 불일치 — 건너뜀 (필요: {sorted(needed)})")
        return []
    df = df[_as_bool(df["readable"])].copy()
    df["bull"] = pd.to_numeric(df["bull"], errors="coerce").fillna(0)
    df["bear"] = pd.to_numeric(df["bear"], errors="coerce").fillna(0)
    df["price_date"] = [
        _month_from_index_row(target, str(p), str(f)) for p, f in zip(df["path"], df["file"])
    ]
    df = df.dropna(subset=["price_date"])
    if df.empty:
        return []

    recs: list[dict] = []
    # ① 신호 태그 카운트 ('|' 구분)
    signals = df["signals"].fillna("").astype(str).str.strip()
    sig = df[signals.ne("")].copy()
    if not sig.empty:
        sig["tag"] = sig["signals"].fillna("").astype(str).str.split("|")
        long = sig.explode("tag")
        long["tag"] = long["tag"].str.strip()
        long = long[long["tag"].str.len() > 0]
        grp = long.groupby(["price_date", "tag"]).size().reset_index(name="value")
        prefix = f"UNSTR_{target.upper()}_"
        recs += [
            {"price_date": r.price_date, "indicator_code": f"{prefix}{r.tag}",
             "value": float(r.value), "unit": "doc_count",
             "source_name": source_name, "note": "월별 신호 태그 문서 수"}
            for r in grp.itertuples()
        ]
    # ② 방향성 톤: 문서별 (bull-bear)/(bull+bear) → 월 평균
    tone = df[(df["bull"] + df["bear"]) > 0].copy()
    if not tone.empty:
        tone["tone"] = (tone["bull"] - tone["bear"]) / (tone["bull"] + tone["bear"])
        grp = tone.groupby("price_date")["tone"].mean().reset_index()
        recs += [
            {"price_date": r.price_date, "indicator_code": f"UNSTR_{target.upper()}_TONE",
             "value": float(r.tone), "unit": "sentiment_score",
             "source_name": source_name, "note": "월별 방향성 톤 평균 (키워드 기반 Phase A)"}
            for r in grp.itertuples()
        ]
    return recs


def run() -> None:
    records: list[dict] = []
    records += _records_from_gain_parquet()
    records += _records_from_index("fao", IDX_FAO, "FAO_AMIS_PDF")
    records += _records_from_index("gain", IDX_GAIN, "USDA_FAS_GAIN_PDF")
    if not records:
        print("[경고] 시계열화할 비정형 신호 없음 — 요약·판독 산출물 존재 여부 확인")
        return
    out = pd.DataFrame(records)
    # GAIN 신호가 parquet·인덱스 양쪽에서 중복 산출될 수 있음 → 동일 (월, 지표)는 최대값 유지
    out = (out.sort_values("value")
              .drop_duplicates(subset=["price_date", "indicator_code"], keep="last")
              .sort_values(["indicator_code", "price_date"])
              .reset_index(drop=True))
    out["ingested_at"] = pd.Timestamp.now("UTC")
    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    # D-023: 저장 직전 as-of 5필드 부여 — 규칙은 src/pipeline/asof.py 단일 관리
    out = attach_asof(out, source="UNSTR_")
    out.to_parquet(OUT_PARQUET, index=False)
    n_ind = out["indicator_code"].nunique()
    span = f"{out['price_date'].min().date()} ~ {out['price_date'].max().date()}"
    print(f"[완료] → {OUT_PARQUET} ({len(out):,}행 · {n_ind}개 지표 · {span})")


if __name__ == "__main__":
    run()
