#!/usr/bin/env python3
"""교차검증 누적 대시보드 생성 (A-186 · 조정자 요청 2026-08-19).

목적: "지금까지 교차검증이 몇 번 돌았고 무슨 지적이 나왔나"를 **파일 하나로** 볼 수 있게.
      reports/cross_verify/*.md 를 스캔해 실행일·대상·모델·판정 요약(치명/높음 건수)·
      상태를 표로 누적한다.

출력: docs/research_desk/cross_verify_log.md
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

SRC = Path("reports/cross_verify")
OUT = Path("docs/research_desk/cross_verify_log.md")


def _summarize(text: str) -> tuple[int, int, str]:
    """판정문에서 치명·높음 건수와 한 줄 요지를 뽑는다."""
    fatal = len(re.findall(r"\[치명\]", text))
    high = len(re.findall(r"\[높음\]", text))
    if "지적 사항 없음" in text or "지적사항 없음" in text:
        return 0, 0, "지적 사항 없음"
    # 첫 [치명] 또는 [높음] 항목의 제목 한 줄
    m = re.search(r"\[(?:치명|높음)\][^\n]{0,110}", text)
    gist = m.group(0).strip(" *-—") if m else "(요지 추출 불가)"
    return fatal, high, gist


def main() -> int:
    rows: list[tuple] = []
    for f in sorted(SRC.glob("xverify_*.md")):
        t = f.read_text(encoding="utf-8")
        d = re.search(r"# GPT 교차검증 — (\d{4}-\d{2}-\d{2})", t)
        model = re.search(r"- 모델: (\S+)", t)
        target = re.search(r"- 대상: (.+)", t)
        run = re.search(r"- 런: (\S+)", t)
        failed = "❌ 실패" in t.split("\n")[0]
        fatal, high, gist = (0, 0, "검증 실패 — 미판정") if failed else _summarize(t)
        rows.append((
            d.group(1) if d else "?",
            (target.group(1).strip() if target else "?")[:52],
            model.group(1) if model else "?",
            run.group(1) if run else "-",
            "❌ 실패" if failed else ("✅ 무지적" if fatal == 0 and high == 0 else "⚠️ 지적"),
            fatal, high, gist[:100], f.name,
        ))
    rows.sort(key=lambda r: (r[0], r[8]), reverse=True)

    ok = sum(1 for r in rows if not r[4].startswith("❌"))
    fail = len(rows) - ok
    tot_fatal = sum(r[5] for r in rows)
    tot_high = sum(r[6] for r in rows)

    lines = [
        "# GPT-5.6-Sol 교차검증 누적 원장",
        "",
        f"**갱신**: {date.today()} · **자동 생성**: `scripts/build_cross_verify_log.py`",
        "",
        "> 조정자 상시 지시(2026-08-13): 인프라·분석·코드 작업은 GPT-5.6-Sol로 교차검증한다.",
        "> 이 파일은 그 **실행 이력과 판정을 한곳에 모은 원장**이다. 개별 판정 전문은",
        "> `reports/cross_verify/` 의 해당 파일에 있다(저장소에 커밋 — 아티팩트 만료 무관).",
        "",
        "## 요약",
        "",
        f"- 총 검증 기록 **{len(rows)}건** — 판정 산출 {ok} · 실패(미판정) {fail}",
        f"- 누적 지적: **[치명] {tot_fatal}건 · [높음] {tot_high}건**",
        "- ⚠️ 실패 기록은 **그 대상이 검증되지 않았다**는 뜻 — 재검증 대상이다.",
        "",
        "## 실행 이력",
        "",
        "| 일자 | 대상 | 상태 | 치명 | 높음 | 판정 요지 | 런 | 전문 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for d, tgt, model, run, status, fatal, high, gist, fname in rows:
        lines.append(f"| {d} | `{tgt}` | {status} | {fatal} | {high} | {gist} | {run} | "
                     f"[{fname[:28]}…](../../reports/cross_verify/{fname}) |")
    if not rows:
        lines.append("| — | (기록 없음) | — | — | — | — | — | — |")
    lines += [
        "",
        "## 해소 이력",
        "",
        "지적된 [치명] 항목의 수정 경위는 MEMORY 원장에 ID로 남는다:",
        "",
        "- A-167 — 도착가 밴드 분위 단순합 → MC 독립 컨볼루션 · 대체유 임계 부호 정정",
        "- A-169 — 게이트 `always()` 무차별 우회 → `!cancelled()` + PASS/WARNING 명시",
        "- A-179 — vintage 주석(개정 이력 미보존 지표 수) 보고서 삽입",
        "",
        "*미해소 [치명]: G2 대체유 z격차 방향 해석(작업 대기열 등재) · 개정 확정치 94종 분리(M-009 단계)*",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[완료] 교차검증 원장 → {OUT} ({len(rows)}건)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
