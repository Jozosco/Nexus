#!/usr/bin/env python3
"""
데이터 준비도 감사 — 모델 착수 전 사실 확인 (D-032)

왜 필요한가:
    "데이터가 많다"와 "모델을 돌릴 수 있다"는 다른 문제다. 조사 패키지(01_data_inventory)의
    판정도 **"데이터는 풍부하지만 모델 학습 테이블은 아직 준비 중"**이었다.
    이 스크립트는 추정 없이 **실제 parquet을 열어** 다음을 사실로 확정한다.

검사 항목:
    ① 목표변수 존재 여부      — 없으면 G1·G2 모두 착수 불가
    ② 핵심 8변수 보유 여부     — D-015 Phase A 확정 목록
    ③ 지표별 실제 커버리지     — 분석창(2010-01~2025-12) 대비 관측 비율
    ④ as-of 필드 충족         — available_at 없으면 모델 투입 금지(CLAUDE.md §1)
    ⑤ 미보유 항목의 조달 경로   — 어떤 워크플로우를 돌려야 채워지는가

출력: reports/market/data_readiness_{YYYY-MM-DD}.md
사용: python scripts/data_readiness.py
의존성: pandas · pyarrow
"""
from __future__ import annotations

import glob
import os
from collections import defaultdict
from datetime import date
from pathlib import Path

import pandas as pd

RAW_DIR = os.environ.get("NEXUS_DATA_ROOT", "data/raw")
OUT_DIR = Path("reports/market")

# 분석창 — M-008 확정(추정 2010-01~2025-12, 2026은 검증용 shadow slice)
WINDOW_START = pd.Timestamp("2010-01-01")
WINDOW_END   = pd.Timestamp("2025-12-31")

# ── 모델 요건 (D-015 Phase A 핵심 변수 + 목표변수 계약) ─────────────────────
# 각 항목: (표시명, 후보 indicator_code, 조달 경로)
TARGET_REQUIREMENT = (
    "목표변수 — CBOT 대두유 거래세션 종가/정산가",
    ["CBOT_BO_CLOSE", "CBOT_SBO_FUTURES"],
    "CME 세션 재집계 또는 공식 settlement 검증 파이프라인",
)
REQUIRED_FEATURES: list[tuple[str, list[str], str]] = [
    ("② CPO(팜유) — CPO–SBO 스프레드 재료", ["CPO", "TE_PALM_OIL", "CPO_USD_MT"],
     "Data Integration · connector=commodity (또는 TE_PALM_OIL 대용)"),
    ("③ WASDE 대두유 재고사용비율", ["WASDE_SBO_STU"], "수동 업로드 — 확보됨"),
    ("④ BDI 해운지수", ["BDI", "TE_BDI"], "수동 업로드(TE 9개년) — 확보됨"),
    ("⑤ FX BRL/USD", ["DEXBZUS", "FX_BRL_USD"],
     "Data Integration · connector=economic"),
    ("⑥ ENSO ONI", ["ONI", "ENSO_ONI"], "Data Integration · connector=climate"),
    ("⑦ 대두 압착량", ["WASDE_SOY_CRUSH", "PSD_SOY_CRUSH"], "수동 업로드 — 확보됨"),
    ("⑧ GATS 미국→한국 대두유 수출", ["GATS_US_SBO_EXPORT_KOREA",
                                      "GATS_US_RSBO_EXPORT_KOREA"],
     "수동 업로드 — 확보됨"),
]
TARGET_TIME_BASES = {"CME_SESSION", "EXCHANGE_SETTLEMENT"}
TARGET_MIN_COVERAGE = 0.98
FEATURE_MIN_COVERAGE = 0.85
TARGET_MIN_SPAN_DAYS = 365 * 14


def _as_bool(series: pd.Series) -> pd.Series:
    """문자/정수/불리언 메타데이터를 안전하게 bool로 정규화한다."""
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False).astype(bool)
    return series.astype("string").str.lower().isin({"true", "1", "yes"})


def _expected_trading_sessions(start: pd.Timestamp, end: pd.Timestamp) -> int:
    """연 252세션을 부분연도의 평일 비율로 안분한 보수적 기대 세션 수."""
    if pd.isna(start) or pd.isna(end) or start > end:
        return 0
    expected = 0.0
    for year in range(start.year, end.year + 1):
        year_start = pd.Timestamp(year=year, month=1, day=1)
        year_end = pd.Timestamp(year=year, month=12, day=31)
        segment_start = max(start, year_start)
        segment_end = min(end, year_end)
        year_weekdays = len(pd.bdate_range(year_start, year_end))
        segment_weekdays = len(pd.bdate_range(segment_start, segment_end))
        expected += 252 * segment_weekdays / max(year_weekdays, 1)
    return max(int(round(expected)), 1)


def _load_index() -> tuple[dict[str, list[str]], dict[str, dict]]:
    """전 parquet을 훑어 지표 → 파일 매핑과 지표별 통계를 만든다."""
    where: dict[str, list[str]] = defaultdict(list)
    stats: dict[str, dict] = {}
    for f in sorted(glob.glob(os.path.join(RAW_DIR, "**", "*.parquet"), recursive=True)):
        try:
            df = pd.read_parquet(f)
        except Exception as e:
            print(f"[경고] 읽기 실패 {os.path.basename(f)}: {type(e).__name__}")
            continue
        if "indicator_code" not in df.columns:
            continue
        file_codes = set(df["indicator_code"].dropna().astype(str).unique())
        target_codes = file_codes.intersection(TARGET_REQUIREMENT[1])
        missing_target_meta = [
            c for c in ("target_eligible", "time_basis", "unit") if c not in df.columns
        ]
        if target_codes and missing_target_meta:
            for code in target_codes:
                where[code].append(os.path.basename(f))
                stats[code] = {
                    "rows": int((df["indicator_code"].astype(str) == code).sum()),
                    "start": pd.NaT,
                    "end": pd.NaT,
                    "months_in_window": 0,
                    "asof": False,
                    "asof_inversions": 0,
                    "target_eligible": False,
                    "time_basis": ["MISSING_METADATA"],
                    "units": ["MISSING_METADATA"],
                    "weekend_days": 0,
                    "observed_sessions": 0,
                    "expected_sessions": 0,
                    "daily_coverage": 0.0,
                    "span_days": 0,
                    "positive": False,
                    "file": os.path.basename(f),
                }
            print(
                f"[오류] {os.path.basename(f)} canonical target {sorted(target_codes)} "
                f"계약 메타데이터 누락: {missing_target_meta}")
            # Never let a legacy canonical-code file be inferred as a valid target.
            df = df[~df["indicator_code"].astype(str).isin(target_codes)]
            if df.empty:
                continue
        has_asof = "available_at" in df.columns
        date_col = "price_date" if "price_date" in df.columns else None
        for code, g in df.groupby("indicator_code"):
            code = str(code)
            where[code].append(os.path.basename(f))
            d = (pd.to_datetime(g[date_col], utc=True, errors="coerce").dt.tz_localize(None)
                 if date_col else pd.Series(dtype="datetime64[ns]"))
            d = d.dropna()
            in_win = d[(d >= WINDOW_START) & (d <= WINDOW_END)]
            available = (pd.to_datetime(g["available_at"], utc=True, errors="coerce")
                         if has_asof else pd.Series(pd.NaT, index=g.index, dtype="datetime64[ns, UTC]"))
            event = (pd.to_datetime(g["event_time"], utc=True, errors="coerce")
                     if "event_time" in g.columns else pd.Series(pd.NaT, index=g.index,
                                                                  dtype="datetime64[ns, UTC]"))
            eligible = _as_bool(g.get("target_eligible", pd.Series(False, index=g.index)))
            bases = sorted(g.get("time_basis", pd.Series("UNSPECIFIED", index=g.index))
                           .dropna().astype(str).unique().tolist())
            units = sorted(g.get("unit", pd.Series("UNSPECIFIED", index=g.index))
                           .dropna().astype(str).unique().tolist())
            observed_weekdays = in_win[in_win.dt.dayofweek < 5].nunique()
            target_start = in_win.min() if len(in_win) else pd.NaT
            target_end = in_win.max() if len(in_win) else pd.NaT
            expected_sessions = _expected_trading_sessions(target_start, target_end)
            prev = stats.get(code)
            cur = {
                "rows": len(g),
                "start": d.min() if len(d) else pd.NaT,
                "end": d.max() if len(d) else pd.NaT,
                "months_in_window": in_win.dt.to_period("M").nunique() if len(in_win) else 0,
                "asof": bool(has_asof and available.notna().all()),
                "asof_inversions": int((available < event).fillna(False).sum()),
                "target_eligible": bool(len(eligible) and eligible.all()),
                "time_basis": bases,
                "units": units,
                "weekend_days": int(in_win[in_win.dt.dayofweek >= 5].nunique()),
                "observed_sessions": int(observed_weekdays),
                "expected_sessions": int(expected_sessions),
                "daily_coverage": min(observed_weekdays / expected_sessions, 1.0)
                if expected_sessions else 0.0,
                "span_days": int((target_end - target_start).days)
                if pd.notna(target_start) and pd.notna(target_end) else 0,
                "positive": bool(pd.to_numeric(g["value"], errors="coerce").dropna().gt(0).all()),
                "file": os.path.basename(f),
            }
            # 같은 지표가 여러 파일에 있으면 관측이 더 많은 쪽을 대표로
            if prev is None or cur["rows"] > prev["rows"]:
                stats[code] = cur
    return where, stats


def main() -> int:
    print(f"[준비도 감사] 대상 {RAW_DIR} · 분석창 {WINDOW_START.date()}~{WINDOW_END.date()}")
    where, stats = _load_index()
    total_months = (WINDOW_END.to_period("M") - WINDOW_START.to_period("M")).n + 1

    lines: list[str] = [
        f"# 데이터 준비도 감사 — {date.today()}",
        "",
        f"**분석창**: {WINDOW_START.date()} ~ {WINDOW_END.date()} ({total_months}개월, M-008)",
        f"**보유 지표 수**: {len(stats):,}종",
        "",
        "> 이 문서는 추정이 아니라 **실제 parquet을 열어 확인한 사실**이다.",
        "",
        "## 1. 모델 착수 요건 — 목표변수 계약 + 핵심 피처",
        "",
        "| 요건 | 상태 | 지표코드 | 관측 개월 | 커버리지 | as-of | 조달 경로 |",
        "|---|---|---|---|---|---|---|",
    ]

    blockers: list[str] = []
    requirements = [(True, TARGET_REQUIREMENT)] + [(False, item) for item in REQUIRED_FEATURES]
    for is_target, (label, cands, how) in requirements:
        hit = next((c for c in cands if c in stats), None)
        if hit is None:
            lines.append(f"| {label} | 🚨 **미보유** | — | — | — | — | {how} |")
            blockers.append(f"{label} → {how}")
            continue
        s = stats[hit]
        cov = (s["daily_coverage"] if is_target
               else s["months_in_window"] / total_months)
        threshold = TARGET_MIN_COVERAGE if is_target else FEATURE_MIN_COVERAGE
        target_contract_ok = (
            not is_target
            or (
                s["target_eligible"]
                and set(s["time_basis"]).issubset(TARGET_TIME_BASES)
                and bool(s["time_basis"])
                and s["weekend_days"] == 0
                and s["span_days"] >= TARGET_MIN_SPAN_DAYS
                and s["positive"]
                and s["units"] == ["USc/lb"]
            )
        )
        asof_ok = s["asof"] and s["asof_inversions"] == 0
        passed = cov >= threshold and target_contract_ok and asof_ok
        mark = "✅" if passed else ("⚠️" if cov > 0 else "🚨")
        observations = (f"{s['observed_sessions']}/{s['expected_sessions']} 거래세션"
                        if is_target else f"{s['months_in_window']}/{total_months} 개월")
        lines.append(
            f"| {label} | {mark} | `{hit}` | {observations} | "
            f"{cov:.0%} | {'✅' if asof_ok else '🚨'} | {s['file']} |")
        if cov < threshold:
            blockers.append(f"{label} — 커버리지 {cov:.0%} (게이트 {threshold:.0%} 미달)")
        if not asof_ok:
            blockers.append(f"{label} — available_at 결측 또는 시점 역전")
        if is_target and not target_contract_ok:
            blockers.append(
                f"{label} — 세션 계약 미충족(time_basis={s['time_basis']}, "
                f"주말={s['weekend_days']}, 단위={s['units']}, "
                f"target_eligible={s['target_eligible']})")

    lines += ["", "## 2. 판정", ""]
    if blockers:
        lines += [
            f"🚨 **모델 착수 불가 — 미충족 {len(blockers)}건**", "",
            "c03 스펙 §6 모델 진입 게이트는 목표가격 ≥98%·핵심 피처 커버리지 ≥85%를 요구한다.",
            "아래가 해소되기 전 G1 동인분석·G2 가격밴드는 **의미 있는 결과를 낼 수 없다**.", "",
        ] + [f"- {b}" for b in blockers]
    else:
        lines.append("✅ 핵심 요건 충족 — 모델 착수 가능")

    # ── 보유 지표 상위(관측 많은 순) ────────────────────────────────────────
    lines += ["", "## 3. 보유 지표 요약 (관측 상위 25)", "",
              "| 지표코드 | 행 수 | 기간 | 분석창 개월 | as-of |", "|---|---|---|---|---|"]
    top = sorted(stats.items(), key=lambda kv: kv[1]["rows"], reverse=True)[:25]
    for code, s in top:
        span = (f"{s['start'].date()}~{s['end'].date()}"
                if pd.notna(s["start"]) else "—")
        lines.append(f"| `{code}` | {s['rows']:,} | {span} | {s['months_in_window']} | "
                     f"{'✅' if s['asof'] else '🚨'} |")

    # ── as-of 미충족 지표 ───────────────────────────────────────────────────
    no_asof = sorted(c for c, s in stats.items() if not s["asof"])
    lines += ["", "## 4. as-of 미충족 지표", ""]
    lines.append(f"**{len(no_asof)}종** — `available_at` 없는 피처는 모델 투입 금지(CLAUDE.md §1)")
    if no_asof:
        lines.append("")
        lines.append(", ".join(f"`{c}`" for c in no_asof[:40])
                     + (" …" if len(no_asof) > 40 else ""))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"data_readiness_{date.today()}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\n[완료] → {out}")
    print(f"  보유 지표 {len(stats):,}종 · as-of 미충족 {len(no_asof)}종")
    if blockers:
        print(f"  🚨 모델 착수 불가 — 미충족 {len(blockers)}건:")
        for b in blockers:
            print(f"     · {b}")
        return 1
    print("  ✅ 핵심 요건 충족")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
