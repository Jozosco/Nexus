#!/usr/bin/env python3
"""
Databento CBOT 대두유 선물(ZL / BO=F) 15개년 수집 (WBS 1.1.52 · A-081 · A-096)

배경: 무료 경로(yfinance) 레이트리밋으로 히스토리 확보 실패 → 조정자가 Databento 가입·키 등록.
사양(session40 §D2 확정): dataset=GLBX.MDP3 · symbol=ZL.c.0(연속 선물) · schema=ohlcv-1d.

A-096 근본 개선 — "Error streaming response: Response ended prematurely":
  16년치(2010~2026)를 **단일 get_range 스트림**으로 요청하면 서버·네트워크 어느 쪽이든
  중간에 끊길 때 전량이 유실된다(부분 저장 불가). 해결:
    ① metadata.get_dataset_range()로 **실제 이용 가능 구간**을 조회해 종료일을 클램프
       (기존 'T-1 추정' 방식 폐기 — 422 dataset_unavailable_range의 근본 원인)
    ② 연 단위 청크로 분할 요청 → 실패해도 해당 연도만 재시도, 나머지는 보존
    ③ 청크별 지수 백오프 재시도 + 부분 성공 저장(수집분 유실 방지)
    ④ metadata.get_dataset_condition()으로 degraded/pending 구간을 사전 로깅
       (degraded = 데이터는 있으나 품질 이슈 — 차단이 아니라 기록 대상)

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
import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

DATASET = "GLBX.MDP3"
SYMBOL  = "ZL.c.0"          # 연속 선물(front month roll)
SCHEMA  = "ohlcv-1d"
OUT_DIR = Path("data/raw/Databento") / DATASET
PARQUET = Path("data/raw/databento_bo_historical.parquet")

START = os.environ.get("DATABENTO_START", "2010-06-06")   # GLBX.MDP3 히스토리 개시
END   = os.environ.get("DATABENTO_END", "")               # 비우면 데이터셋 실제 종료일 사용

MAX_RETRIES = int(os.environ.get("DATABENTO_MAX_RETRIES", "3"))
_PX_SCALE   = 1e-9          # Databento 가격 필드는 1e-9 고정소수 정수


def _dataset_end(client) -> str:
    """데이터셋의 실제 이용 가능 종료일 조회 — 422 방지의 정공법."""
    try:
        rng = client.metadata.get_dataset_range(dataset=DATASET)
        # SDK 버전에 따라 키가 end / end_date, 값이 ISO 문자열 또는 datetime
        raw = rng.get("end") or rng.get("end_date") or ""
        end = str(raw)[:10]
        if end:
            print(f"[정보] 데이터셋 이용 가능 구간: {str(rng.get('start') or '')[:10]} ~ {end}")
            return end
    except Exception as e:
        print(f"[경고] get_dataset_range 실패({type(e).__name__}) — T-1로 대체: {e}")
    return (date.today() - timedelta(days=1)).isoformat()


def _log_condition(client, start: str, end: str) -> None:
    """구간별 데이터 상태(available/degraded/pending/missing)를 집계 로깅."""
    try:
        cond = client.metadata.get_dataset_condition(
            dataset=DATASET, start_date=start, end_date=end)
    except Exception as e:
        print(f"[정보] get_dataset_condition 조회 생략({type(e).__name__})")
        return
    counts: dict[str, int] = {}
    for row in cond or []:
        c = (row.get("condition") if isinstance(row, dict) else getattr(row, "condition", "")) or "unknown"
        counts[str(c)] = counts.get(str(c), 0) + 1
    if counts:
        summary = " · ".join(f"{k} {v}일" for k, v in sorted(counts.items()))
        print(f"[정보] 데이터셋 상태: {summary}")
        if counts.get("degraded"):
            print("       degraded = 데이터는 존재하나 원천 품질 이슈 구간 — 수집은 진행하되 "
                  "해당 구간 값은 교차검증 대상으로 표시")


def _fetch_chunk(client, start: str, end: str) -> pd.DataFrame | None:
    """단일 구간 조회 — 스트림 중단 시 지수 백오프 재시도. 실패 시 None."""
    delay = 5
    for attempt in range(MAX_RETRIES):
        try:
            data = client.timeseries.get_range(
                dataset=DATASET, symbols=[SYMBOL], schema=SCHEMA,
                stype_in="continuous", start=start, end=end,
            )
            return data.to_df()
        except Exception as e:
            msg = str(e)
            last = attempt == MAX_RETRIES - 1
            print(f"    [{'오류' if last else '경고'}] {start}~{end} "
                  f"{type(e).__name__}: {msg[:90]}")
            if last:
                return None
            time.sleep(delay); delay *= 2
    return None


def _to_price_date(part: pd.DataFrame, label: str) -> pd.DataFrame:
    """청크 1건의 시각 인덱스를 **명시적으로** price_date 컬럼으로 승격.

    A-102: 이 함수가 없어서 price_date가 전부 1970-01-01이 됐다.
      기존 경로: `pd.concat(parts, ignore_index=True)` → **DatetimeIndex(ts_event)를 폐기** →
      이어지는 `reset_index()`가 RangeIndex(0,1,2…)를 'index' 컬럼으로 만들고
      `pd.to_datetime(0,1,2…)`가 이를 **에폭 나노초**로 해석 → 1970-01-01 + n ns.
      (증상 일치: min·max 모두 1970-01-01인데 nunique는 행 수와 같음)
    따라서 concat **이전에** 청크별로 시각을 컬럼화한다.
    """
    # ① DatetimeIndex면 그것이 진실 — 이름이 없어도 사용한다.
    if isinstance(part.index, pd.DatetimeIndex):
        out = part.copy()
        out["price_date"] = part.index
        return out.reset_index(drop=True)
    # ② 아니면 알려진 시각 컬럼을 찾는다(RangeIndex 폴백 금지 — 1970 버그의 원인).
    reset = part.reset_index()
    for cand in ("ts_event", "ts_recv", "date", "time"):
        if cand in reset.columns:
            reset["price_date"] = pd.to_datetime(reset[cand], utc=True, errors="coerce")
            return reset
    raise ValueError(
        f"[오류] {label}: 시각 컬럼을 찾지 못함(컬럼={list(reset.columns)[:8]}). "
        "임의 컬럼으로 추정하지 않고 중단 — 1970-01-01 오염 방지")


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    """tz 제거 + 일자 단위 정규화 + 정수 가격 → USc/lb 변환."""
    ts = pd.to_datetime(df["price_date"], utc=True, errors="coerce")
    # ohlcv-1d는 일봉이므로 시각 성분을 버리고 **날짜(yyyy-mm-dd)**로 저장한다(조정자 요청).
    df["price_date"] = ts.dt.tz_localize(None).dt.normalize()
    for col in ("open", "high", "low", "close"):
        if col in df.columns and pd.api.types.is_integer_dtype(df[col]):
            df[col] = df[col] * _PX_SCALE
    return df


def _assert_date_range(df: pd.DataFrame, start: str, end: str) -> None:
    """수집 결과가 요청 구간 안에 있는지 검증 — 조용한 오염을 즉시 실패로 전환."""
    bad = df["price_date"].isna().sum()
    if bad:
        raise ValueError(f"[오류] price_date 파싱 실패 {bad:,}건 — 저장 중단")
    lo, hi = df["price_date"].min(), df["price_date"].max()
    lo_ok = pd.Timestamp(start) - pd.Timedelta(days=7)
    hi_ok = pd.Timestamp(end) + pd.Timedelta(days=7)
    if lo < lo_ok or hi > hi_ok:
        raise ValueError(
            f"[오류] 수집 기간이 요청 범위를 벗어남: {lo.date()}~{hi.date()} "
            f"(요청 {start}~{end}). 시각 파싱 오류 가능성 — 저장 중단")
    print(f"[검증] 기간 정합 OK: {lo.date()} ~ {hi.date()}")


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
    end = END or _dataset_end(client)
    print(f"[C-04] Databento {DATASET} · {SYMBOL} · {SCHEMA} · {START}~{end} 수집(연 단위 분할)...")
    _log_condition(client, START, end)

    start_year, end_year = int(START[:4]), int(end[:4])
    parts: list[pd.DataFrame] = []
    failed: list[str] = []
    for year in range(start_year, end_year + 1):
        c_start = START if year == start_year else f"{year}-01-01"
        c_end   = end   if year == end_year   else f"{year}-12-31"
        got = _fetch_chunk(client, c_start, c_end)
        if got is None:
            failed.append(str(year))
            continue
        if not got.empty:
            # A-102: concat 전에 시각을 컬럼으로 승격해야 한다(ignore_index가 인덱스를 버림)
            named = _to_price_date(got, f"{year}")
            parts.append(named)
            span = f"{named['price_date'].min()} ~ {named['price_date'].max()}"
            print(f"  [{year}] {len(named):,}행 · {span}")

    if not parts:
        print("[오류] 전 구간 수집 실패 — 키·구독 범위·네트워크 확인")
        return
    if failed:
        # 부분 성공을 반드시 저장한다(A-096: 전량 유실 방지가 이번 수정의 핵심)
        print(f"[경고] 미수집 연도: {', '.join(failed)} — 수집분만 저장하고 재실행 시 보완")

    df = _normalize(pd.concat(parts, ignore_index=True))
    df = df.drop_duplicates(subset=["price_date"]).sort_values("price_date")
    _assert_date_range(df, START, end)

    # 연도별 커버리지 리포트 — '누락 데이터'를 눈으로 확인 가능하게(조정자 지적)
    by_year = df.groupby(df["price_date"].dt.year).size()
    thin = [f"{y}({n}일)" for y, n in by_year.items() if n < 200]
    print(f"[커버리지] 연도별 거래일: {dict(by_year)}")
    if thin:
        print(f"[경고] 거래일 200일 미만 연도(누락 의심): {', '.join(thin)}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUT_DIR / f"ZL_{SCHEMA}_{START}_{end}.csv"
    # 조정자 요청: CSV·XLSX의 price_date는 시각 없이 **yyyy-mm-dd**로 기록
    csv_df = df.copy()
    csv_df["price_date"] = csv_df["price_date"].dt.strftime("%Y-%m-%d")
    # tz-aware 컬럼은 엑셀 비호환 → 제거(A-064 동일 규약)
    for c in csv_df.columns:
        if pd.api.types.is_datetime64tz_dtype(csv_df[c]):
            csv_df[c] = csv_df[c].dt.tz_localize(None)
    csv_df.to_csv(csv_path, index=False)

    keep = ["price_date"] + [c for c in ("open", "high", "low", "close", "volume") if c in df.columns]
    csv_df[keep].to_excel(OUT_DIR / f"ZL_{SCHEMA}.xlsx", index=False)

    # 롱포맷 parquet (기존 지표코드 규약 준수)
    recs = []
    for col in ("open", "high", "low", "close", "volume"):
        if col not in df.columns:
            continue
        sub = df[["price_date", col]].dropna().rename(columns={col: "value"})
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
    print(f"       기간: {df['price_date'].min().date()} ~ {df['price_date'].max().date()} "
          f"({df['price_date'].nunique():,} 거래일)")


if __name__ == "__main__":
    run()
