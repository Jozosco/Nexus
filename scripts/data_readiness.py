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

# ── 모델 요건 (D-015 Phase A 핵심 8변수 + 목표변수) ──────────────────────────
# 각 항목: (표시명, 후보 indicator_code, 조달 경로)
REQUIRED: list[tuple[str, list[str], str]] = [
    ("목표변수 — CBOT 대두유 선물 종가", ["CBOT_BO_CLOSE", "CBOT_SBO_FUTURES"],
     "Historical Analysis Pipeline · connector=databento"),
    ("① CBOT 대두유 선물", ["CBOT_BO_CLOSE", "CBOT_SBO_FUTURES"],
     "Historical · connector=databento"),
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
        has_asof = "available_at" in df.columns
        date_col = "price_date" if "price_date" in df.columns else None
        for code, g in df.groupby("indicator_code"):
            code = str(code)
            where[code].append(os.path.basename(f))
            d = pd.to_datetime(g[date_col], errors="coerce") if date_col else pd.Series(dtype="datetime64[ns]")
            d = d.dropna()
            in_win = d[(d >= WINDOW_START) & (d <= WINDOW_END)]
            prev = stats.get(code)
            cur = {
                "rows": len(g),
                "start": d.min() if len(d) else pd.NaT,
                "end": d.max() if len(d) else pd.NaT,
                "months_in_window": in_win.dt.to_period("M").nunique() if len(in_win) else 0,
                "asof": has_asof,
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
        "## 1. 모델 착수 요건 — 핵심 8변수 + 목표변수",
        "",
        "| 요건 | 상태 | 지표코드 | 관측 개월 | 커버리지 | as-of | 조달 경로 |",
        "|---|---|---|---|---|---|---|",
    ]

    blockers: list[str] = []
    for label, cands, how in REQUIRED:
        hit = next((c for c in cands if c in stats), None)
        if hit is None:
            lines.append(f"| {label} | 🚨 **미보유** | — | — | — | — | {how} |")
            blockers.append(f"{label} → {how}")
            continue
        s = stats[hit]
        cov = s["months_in_window"] / total_months
        mark = "✅" if cov >= 0.85 else ("⚠️" if cov > 0 else "🚨")
        lines.append(
            f"| {label} | {mark} | `{hit}` | {s['months_in_window']}/{total_months} | "
            f"{cov:.0%} | {'✅' if s['asof'] else '🚨'} | {s['file']} |")
        if cov < 0.85:
            blockers.append(f"{label} — 커버리지 {cov:.0%} (게이트 85% 미달)")

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
