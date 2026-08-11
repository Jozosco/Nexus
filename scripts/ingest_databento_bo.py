#!/usr/bin/env python3
"""
Databento CBOT 대두유 선물(ZL / BO=F) 15개년 수집 (WBS 1.1.52 · A-081)

배경: 무료 경로(yfinance) 레이트리밋으로 히스토리 확보 실패 → 조정자가 Databento 가입·키 등록.
사양(session40 §D2 확정): dataset=GLBX.MDP3 · symbol=ZL.c.0(연속 선물) · schema=ohlcv-1d.

출력(조정자 지정 경로):
  data/raw/Databento/GLBX.MDP3/ZL_ohlcv-1d_{start}_{end}.csv   (원본 보존)
  data/raw/Databento/GLBX.MDP3/ZL_ohlcv-1d.xlsx                (열람용)
  data/raw/databento_bo_historical.parquet                     (파이프라인 입력)

지표코드: CBOT_BO_OPEN/HIGH/LOW/CLOSE/VOLUME (기존 commodity_connector와 동일 규약)
단위: USc/lb (CME ZL 표준) — Databento 가격은 1e-9 스케일 정수 → 변환 필요

인증: 환경변수 DATABENTO_API_KEY (GitHub Secrets) — 하드코딩 금지 (CLAUDE.md §2)
⚠️ 실행: 개발 샌드박스는 외부 API 차단 → **GitHub Actions 전용**
의존성: databento · pandas · pyarrow · openpyxl
"""
from __future__ import annotations

import os
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

DATASET = "GLBX.MDP3"
SYMBOL  = "ZL.c.0"          # 연속 선물(front month roll)
SCHEMA  = "ohlcv-1d"
OUT_DIR = Path("data/raw/Databento") / DATASET
PARQUET = Path("data/raw/databento_bo_historical.parquet")

START = os.environ.get("DATABENTO_START", "2010-06-06")   # GLBX.MDP3 히스토리 개시
# A-085: 422 dataset_unavailable_range — 라이선스 미포함 구간(실시간 근접) 요청 시 발생.
# CME 히스토리는 통상 T-1일까지만 무구독 접근 가능 → 종료일을 어제로 클램프(무료 범위 최대화).
END   = os.environ.get("DATABENTO_END") or (date.today() - timedelta(days=1)).isoformat()

# Databento 가격 필드는 1e-9 고정소수 정수
_PX_SCALE = 1e-9


def run() -> None:
    key = os.environ.get("DATABENTO_API_KEY", "").strip()
    if not key:
        print("[오류] DATABENTO_API_KEY 미등록 — GitHub Secrets 확인 필요")
        return
    try:
        import databento as db
    except ImportError:
        print("[오류] databento 미설치 — pip install databento")
        return

    client = db.Historical(key)
    print(f"[C-04] Databento {DATASET} · {SYMBOL} · {SCHEMA} · {START}~{END} 수집...")
    try:
        data = client.timeseries.get_range(
            dataset=DATASET, symbols=[SYMBOL], schema=SCHEMA,
            stype_in="continuous", start=START, end=END,
        )
        df = data.to_df()
    except Exception as e:
        msg = str(e)
        if "dataset_unavailable_range" in msg or "422" in msg:
            # 응답 메시지의 권장 종료시각을 파싱해 자동 재시도 (수동 개입 없이 최대 범위 확보)
            import re as _re
            m = _re.search(r"before (\d{4}-\d{2}-\d{2})", msg)
            safe_end = m.group(1) if m else (date.today() - timedelta(days=2)).isoformat()
            print(f"[정보] 라이선스 범위 초과 — 종료일 {safe_end}로 축소 재시도")
            try:
                data = client.timeseries.get_range(
                    dataset=DATASET, symbols=[SYMBOL], schema=SCHEMA,
                    stype_in="continuous", start=START, end=safe_end,
                )
                df = data.to_df()
            except Exception as e2:
                print(f"[오류] Databento 재시도 실패: {e2}")
                return
        else:
            print(f"[오류] Databento 수집 실패: {msg}")
            return

    if df.empty:
        print("[경고] 수신 데이터 없음 — 심볼·기간 확인")
        return

    df = df.reset_index()
    date_col = next((c for c in ("ts_event", "index", "date") if c in df.columns), df.columns[0])
    df["price_date"] = pd.to_datetime(df[date_col], utc=True, errors="coerce").dt.tz_localize(None)

    # 가격 스케일 변환 (1e-9 정수 → USc/lb). 이미 float면 그대로.
    for col in ("open", "high", "low", "close"):
        if col in df.columns and pd.api.types.is_integer_dtype(df[col]):
            df[col] = df[col] * _PX_SCALE

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_DIR / f"ZL_{SCHEMA}_{START}_{END}.csv"
    df.to_csv(csv_path, index=False)

    keep = ["price_date"] + [c for c in ("open", "high", "low", "close", "volume") if c in df.columns]
    xl = df[keep].copy()
    xl.to_excel(OUT_DIR / f"ZL_{SCHEMA}.xlsx", index=False)

    # 롱포맷 parquet (기존 지표코드 규약 준수)
    recs = []
    for col in ("open", "high", "low", "close", "volume"):
        if col not in df.columns:
            continue
        sub = df[["price_date", col]].dropna()
        sub = sub.rename(columns={col: "value"})
        sub["indicator_code"] = f"CBOT_BO_{col.upper()}"
        sub["unit"] = "USc/lb" if col != "volume" else "contracts"
        recs.append(sub)
    out = pd.concat(recs, ignore_index=True)
    out["source_name"] = "Databento/GLBX.MDP3/ZL"
    out["ingested_at"] = pd.Timestamp.now("UTC")
    out.to_parquet(PARQUET, index=False)

    print(f"[완료] CSV → {csv_path}")
    print(f"       XLSX → {OUT_DIR / f'ZL_{SCHEMA}.xlsx'}")
    print(f"       Parquet → {PARQUET} ({len(out):,}행)")
    print(f"       기간: {df['price_date'].min().date()} ~ {df['price_date'].max().date()}")


if __name__ == "__main__":
    run()
