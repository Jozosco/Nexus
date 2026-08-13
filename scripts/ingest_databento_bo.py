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

# as-of 헬퍼 로드 — 스크립트 직접 실행 시 저장소 루트를 경로에 추가
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from src.pipeline.asof import attach_asof  # noqa: E402

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
        # A-111(F12): SDK가 dict가 아닌 객체를 돌려주면 .get에서 AttributeError가 나고
        # 조용히 T-1 추정으로 회귀한다 — 그 T-1이 바로 422의 원인이었다. 양쪽을 모두 처리.
        def _pick(obj, *names):
            for n in names:
                v = obj.get(n) if isinstance(obj, dict) else getattr(obj, n, None)
                if v:
                    return str(v)[:10]
            return ""
        end = _pick(rng, "end", "end_date")
        start = _pick(rng, "start", "start_date")
        if end:
            print(f"[정보] 데이터셋 이용 가능 구간: {start or '?'} ~ {end}")
            return end
        print(f"[경고] get_dataset_range 응답에 종료일 없음: {str(rng)[:120]}")
    except Exception as e:
        print(f"[경고] get_dataset_range 실패({type(e).__name__}): {e}")
    fallback = (date.today() - timedelta(days=1)).isoformat()
    print(f"[경고] T-1 추정({fallback})으로 대체 — 422 발생 시 이 경로가 원인 "
          "(DATABENTO_END 환경변수로 명시 지정 가능)")
    return fallback


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


def _load_from_csv(csv_path: str) -> pd.DataFrame | None:
    """A-128: Actions가 커밋한 CSV에서 parquet을 재생성하는 오프라인 경로.

    왜 필요한가: parquet은 .gitignore 대상이라 **Actions 아티팩트로만** 존재한다.
    반면 CSV·XLSX는 main에 커밋된다. 개발 샌드박스는 Databento API에 접근할 수 없으므로
    (외부 프록시 차단), 커밋된 CSV가 로컬에서 목표변수를 재구성하는 유일한 경로다.
    API 재호출(유료 종량제) 없이 같은 산출물을 만든다.
    """
    p = Path(csv_path)
    if not p.exists():
        print(f"[오류] CSV 없음: {p}")
        return None
    df = pd.read_csv(p)
    df["price_date"] = pd.to_datetime(df["price_date"], errors="coerce")
    bad = int(df["price_date"].isna().sum()) + int((df["price_date"].dt.year < 2000).sum())
    if bad:
        print(f"[오류] CSV 날짜 파손 {bad}행(1970 오염 등) — .BROKEN 산출물 여부 확인")
        return None
    return df


def run() -> None:
    # 오프라인 재구성 모드 — DATABENTO_FROM_CSV=<경로>
    from_csv = os.environ.get("DATABENTO_FROM_CSV", "").strip()
    if from_csv:
        df = _load_from_csv(from_csv)
        if df is None:
            return
        end = str(df["price_date"].max().date())
        _postprocess_and_save(df, end)
        return

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
        # A-111(F7): Databento `end`는 **배타적**이다. `{year}-12-31`을 쓰면 매년
        # 12월 31일이 누락돼 16년 × 약 11거래일이 조용히 사라진다(커버리지 임계 200일에
        # 걸리지 않아 영구 미검출). 다음 해 1월 1일을 배타 종료로 준다.
        c_end   = end   if year == end_year   else f"{year + 1}-01-01"
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
    _postprocess_and_save(df, end)


def _postprocess_and_save(df: pd.DataFrame, end: str) -> None:
    """검증 → 중복 해소 → CSV/XLSX/parquet 저장. API·CSV 재구성 양쪽 공용 (A-128)."""
    # A-111(F8): ZL.c.0 연속 심볼은 롤 시점에 같은 날짜로 만기·신규 계약 2행이 올 수 있다.
    # 무조건 drop_duplicates하면 **가격이 다른 두 계약 중 하나를 근거 없이 선택**하게 되고,
    # 그 임의 선택이 G2 타깃 시계열에 계약 전환 점프로 주입된다(연 12회 × 16년 ≈ 190회).
    dup = df["price_date"].duplicated(keep=False)
    if dup.any():
        n_days = df.loc[dup, "price_date"].nunique()
        spread = (df[dup].groupby("price_date")["close"].agg(lambda s: s.max() - s.min())
                  if "close" in df.columns else None)
        worst = float(spread.max()) if spread is not None and len(spread) else 0.0
        print(f"[경고] 롤 중복 {int(dup.sum())}행 / {n_days}일 — 종가 최대 격차 {worst:.4f} USc/lb")
        # 동일 날짜는 거래량이 큰 계약(주력 계약)을 채택 — 규칙을 명시하고 기록한다
        if "volume" in df.columns:
            df = df.sort_values(["price_date", "volume"])
            print("       채택 규칙: 동일 날짜는 **거래량 최대** 계약(주력물) 우선")
        df = df.drop_duplicates(subset=["price_date"], keep="last")
    df = df.sort_values("price_date")
    _assert_date_range(df, START, end)

    # A-111(F11): 날짜만 검증하고 값은 방치하면 같은 종류의 조용한 오염이 가격에서 재발한다.
    # SDK 버전에 따라 가격이 이미 float이면 _PX_SCALE이 미적용되어 1e9배 차이가 무경고로 난다.
    if "close" in df.columns:
        lo, hi = float(df["close"].min()), float(df["close"].max())
        if not (5.0 <= lo <= 200.0 and 5.0 <= hi <= 200.0):
            raise ValueError(
                f"[오류] ZL 종가가 합리 범위(5~200 USc/lb)를 벗어남: {lo:.4f}~{hi:.4f}. "
                "가격 스케일(1e-9) 적용 여부 확인 필요 — 저장 중단")
        print(f"[검증] 종가 범위 OK: {lo:.2f} ~ {hi:.2f} USc/lb")

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

    # A-128(S4): ZL.c.0은 **무조정 연속물**이라 롤일의 전일 대비 수익률은 시장 움직임이
    # 아니라 계약 간 스프레드다(롤 129회 · 롤일 평균 |변동| 1.96% vs 평시 1.13%).
    # 구 parquet은 instrument_id를 버려 소비 측이 롤일을 식별할 수 없었다.
    # 롤일 플래그를 지표로 내보내 G1/G2가 롤 구간 수익률을 분리 처리하게 한다.
    if "instrument_id" in df.columns:
        seq = df.sort_values("price_date")
        roll = (seq["instrument_id"] != seq["instrument_id"].shift()).fillna(False)
        roll.iloc[0] = False                      # 첫 행은 롤이 아니라 시계열 시작
        flag = pd.DataFrame({"price_date": seq["price_date"],
                             "value": roll.astype(float)})
        flag["indicator_code"] = "CBOT_BO_ROLLDAY"
        flag["unit"] = "flag"
        recs.append(flag)
        print(f"[정보] 롤일 플래그 생성: {int(roll.sum())}회 계약 전환 표시 (CBOT_BO_ROLLDAY)")
    out = pd.concat(recs, ignore_index=True)
    out["source_name"] = "Databento/GLBX.MDP3/ZL"
    out["ingested_at"] = pd.Timestamp.now("UTC")
    # D-023: 저장 직전 as-of 5필드 부여 — 규칙은 src/pipeline/asof.py 단일 관리
    out = attach_asof(out, source="CBOT_BO_")
    out.to_parquet(PARQUET, index=False)

    print(f"[완료] CSV → {csv_path}")
    print(f"       XLSX → {OUT_DIR / f'ZL_{SCHEMA}.xlsx'}")
    print(f"       Parquet → {PARQUET} ({len(out):,}행)")
    print(f"       기간: {df['price_date'].min().date()} ~ {df['price_date'].max().date()} "
          f"({df['price_date'].nunique():,} 거래일)")


if __name__ == "__main__":
    run()
