#!/usr/bin/env python3
"""E1 — '서명된 무소식' 일별 스탬프 (차별화 6선 1순위 · D-048 승인 · A-202).

무소식이 '아무것도 안 봤다'가 아니라 **'전부 검사했고 이상이 없었다'**임을 증명한다.
fail-open 이력 3회(A-160·A-168·A-169)의 교훈 — 침묵과 검사된 무소식을 구분하려면
게이트 상태·경보 유무·검증 원장 상태·런 ID를 스탬프에 **명시**해야 한다.

입력(모두 선택적 — 없으면 '미확인'으로 정직 표기, 위장 금지):
  ① reports/data_quality/dq_overall_status.txt  — C-08 게이트 판정(A-108)
  ② reports/pipeline/g1_alert_*.md              — G1 일별 경보(D-043 alert 모드)
  ③ reports/market/data_readiness_{오늘}.md      — 모델 준비도
  ④ docs/research_desk/cross_verify_log.md       — GPT 교차검증 원장(A-186)

출력: data/processed/signed_daily_stamps.csv append(A-181 패턴·(date) 중복 제거)
      + GITHUB_STEP_SUMMARY 1줄 + stdout.
"""
from __future__ import annotations

import glob
import os
import re
from datetime import date
from pathlib import Path

import pandas as pd

DQ_STATUS = Path("reports/data_quality/dq_overall_status.txt")
# G1 alert는 실행별 격리 디렉터리(run_{id} — GPT 교차검증 정정)에 산출 — 재귀 탐색
ALERT_GLOB = "reports/pipeline/**/g1_alert_*.md"
READINESS = Path(f"reports/market/data_readiness_{date.today()}.md")
XVERIFY_LOG = Path("docs/research_desk/cross_verify_log.md")
OUT = Path("data/processed/signed_daily_stamps.csv")


def _gate_status() -> str:
    # Actions에서는 C-08 잡 output을 env로 직접 전달(파일은 잡 간 미공유 — A-108 이식성 채널은
    # 같은 잡 안에서만 유효). env 우선, 파일 폴백, 둘 다 없으면 '미확인'(위장 금지).
    env_status = os.environ.get("E1_GATE_STATUS", "").strip()
    if env_status:
        return env_status
    if not DQ_STATUS.exists():
        return "미확인(게이트 산출물 없음)"
    return DQ_STATUS.read_text(encoding="utf-8").strip() or "미확인(빈 파일)"


def _alerts_today() -> int:
    files = [f for f in glob.glob(ALERT_GLOB, recursive=True) if str(date.today()) in f]
    return len(files)


def _readiness() -> str:
    if not READINESS.exists():
        return "미확인"
    t = READINESS.read_text(encoding="utf-8")
    return "차단" if "모델 착수 불가" in t else "통과"


def _xverify_fatal_open(t: str | None = None) -> str:
    """원장 요약의 미해소 치명 여부 — 원장 부재 시 '미확인'(위장 금지)."""
    if t is None:
        if not XVERIFY_LOG.exists():
            return "미확인"
        t = XVERIFY_LOG.read_text(encoding="utf-8")
    m = re.search(r"\*미해소 \[치명\]:\s*([^*]+)\*", t)
    if m and m.group(1).strip() and "없음" not in m.group(1):
        return f"미해소 있음({m.group(1).strip()[:40]}…)"
    return "미해소 0"


def main() -> int:
    today = str(date.today())
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    gate = _gate_status()
    n_alerts = _alerts_today()
    ready = _readiness()
    xv = _xverify_fatal_open()

    all_clear = (gate == "PASS" or gate == "WARNING") and n_alerts == 0
    verdict = ("✅ 검사된 무소식" if all_clear
               else f"⚠️ 경보 {n_alerts}건" if n_alerts else f"🔴 게이트 {gate}")
    stamp = (f"{today} {verdict} — C-08 게이트 {gate} · G1 경보 {n_alerts}건 · "
             f"준비도 {ready} · 교차검증 원장 치명 {xv} · 런 {run_id} · "
             f"원장: docs/research_desk/cross_verify_log.md")
    print(f"[E1 스탬프] {stamp}")

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(f"### 🔏 서명된 무소식 (E1)\n{stamp}\n")

    row = pd.DataFrame([{
        "date": today, "verdict": verdict, "gate": gate, "alerts": n_alerts,
        "readiness": ready, "xverify_fatal": xv, "run_id": run_id,
        "stamped_at": pd.Timestamp.now("UTC").isoformat(timespec="seconds"),
    }])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        old = pd.read_csv(OUT, dtype=str)
        merged = pd.concat([old, row.astype(str)], ignore_index=True)
        merged = merged.drop_duplicates(subset=["date"], keep="last")   # 당일 재실행 시 최신 유지
    else:
        merged = row.astype(str)
    merged = merged.sort_values("date").reset_index(drop=True)
    merged.to_csv(OUT, index=False, encoding="utf-8")
    print(f"[E1 스탬프] append → {OUT} (누적 {len(merged)}행)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
