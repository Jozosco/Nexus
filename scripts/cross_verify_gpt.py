#!/usr/bin/env python3
"""
GPT 교차검증 게이트 — 분석·코드 산출물의 외부 모델 검증 (조정자 지시 2026-08-13)

지시: "모든 데이터 분석·코딩 작업은 GPT 5.6 - Sol (Effort - Max)로 교차검증한다."

동작: 지정한 산출물(마크다운 리포트·diff 등)을 OpenAI API로 보내
      ①수치·논리 오류 ②누수(look-ahead) 위험 ③해석 과장 여부를 지적받는다.
      결과는 reports/cross_verify/ 에 저장하고 요약을 stdout으로 남긴다.

주의:
    - 모델명은 GPT_XVERIFY_MODEL 환경변수로 관리한다(기본 gpt-5.6).
      OpenAI 모델명은 수시로 바뀌므로(L-008 전례) 하드코딩하지 않는다.
    - 실패해도 파이프라인을 막지 않는다(외부 서비스 의존을 게이트로 두면
      OpenAI 장애가 곧 우리 장애가 된다). 검증 불가 사실만 크게 남긴다.
    - reasoning effort는 지원 모델에서만 전달한다(미지원이면 자동 생략).

사용:
    python scripts/cross_verify_gpt.py reports/pipeline/variable_importance_*.md
    python scripts/cross_verify_gpt.py --diff HEAD~1   # 직전 커밋 diff 검증
의존성: openai >= 1.30
"""
from __future__ import annotations

import glob
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

OUT_DIR = Path("reports/cross_verify")
MODEL = os.environ.get("GPT_XVERIFY_MODEL", "gpt-5.6")
EFFORT = os.environ.get("GPT_XVERIFY_EFFORT", "xhigh")   # A-166: max는 모델별 미지원(400) — xhigh 기본
MAX_CHARS = 60_000        # 컨텍스트 예산 — 초과분은 앞부분 우선

SYSTEM = (
    "너는 원자재 가격 예측 프로젝트의 적대적 검증자다. 대두유(soybean oil) 조달 AI의 "
    "분석 리포트/코드 변경을 검토해 다음만 보고하라: "
    "①수치·단위·논리 오류 ②시계열 누수(look-ahead) 위험 ③상관을 인과로 과장한 해석 "
    "④재현 불가능한 주장. 문제없는 항목은 언급하지 말고, 각 지적에 심각도(치명/높음/참고)와 "
    "구체 근거를 붙여라. 한국어로 답하라."
)


def _gather(args: list[str]) -> tuple[str, str]:
    if args and args[0] == "--diff":
        ref = args[1] if len(args) > 1 else "HEAD~1"
        text = subprocess.run(["git", "diff", ref, "--", "*.py", "*.yml"],
                              capture_output=True, text=True).stdout
        return f"git diff {ref}", text
    paths: list[str] = []
    for a in args:
        paths.extend(glob.glob(a))
    if not paths:
        # A-208: CI에서 글로브 등재가 대상 파일 커밋보다 먼저 push되면 매칭 0건이 정상 —
        # sys.exit(2) hard-fail이 "검증 실패가 파이프라인을 막지 않는다" 설계를 우회했다(런 #14).
        print(f"[경고] 검증 대상 없음(매칭 0건) — 건너뜀: {' '.join(args) or '(인자 없음)'}")
        sys.exit(0)
    parts = [Path(p).read_text(encoding="utf-8", errors="replace") for p in sorted(paths)]
    return ", ".join(sorted(paths)), "\n\n=====\n\n".join(parts)


def main() -> int:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        print("[경고] OPENAI_API_KEY 미설정 — 교차검증 건너뜀 (검증되지 않은 산출물임을 기록)")
        return 0

    label, text = _gather(sys.argv[1:])
    if len(text) > MAX_CHARS:
        print(f"[정보] 대상 {len(text):,}자 → {MAX_CHARS:,}자로 절단")
        text = text[:MAX_CHARS]

    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        req: dict = {
            "model": MODEL,
            "messages": [{"role": "system", "content": SYSTEM},
                         {"role": "user", "content": f"검증 대상: {label}\n\n{text}"}],
        }
        try:
            resp = client.chat.completions.create(**req, reasoning_effort=EFFORT)
        except TypeError:
            resp = client.chat.completions.create(**req)       # effort 미지원 SDK/모델
        verdict = resp.choices[0].message.content or "(빈 응답)"
    except Exception as e:
        # A-186: 실패도 기록으로 남긴다 — 조용한 무판정이 '검증됨'으로 오인되지 않게.
        #   잡은 계속 비치명(exit 0)이되, 사람이 볼 수 있는 흔적을 남긴다.
        print(f"[경고] 교차검증 호출 실패({type(e).__name__}): {e}")
        print(f"       GPT_XVERIFY_MODEL={MODEL} — 모델명 확인(llm_model_monitor 산출 참조)")
        _write_result(label, f"⚠️ **검증 실패** — `{type(e).__name__}`: {e}\n\n"
                             f"이 대상은 **검증되지 않았습니다**. 재실행 필요.",
                      failed=True)
        _step_summary(f"⚠️ 교차검증 실패 — 대상 `{label}` ({type(e).__name__})")
        return 0

    _write_result(label, verdict, failed=False)
    _step_summary(f"✅ 교차검증 완료 — 대상 `{label}`")
    print(verdict[:1500])
    return 0


def _slug(label: str) -> str:
    """대상 라벨 → 파일명 조각 (A-186: 대상별 분리 저장으로 덮어쓰기 유실 방지)."""
    base = re.sub(r"[^0-9A-Za-z가-힣._-]+", "_", label)[:60].strip("_")
    return base or "target"


def _write_result(label: str, body: str, *, failed: bool) -> Path:
    """대상·순번별 파일로 저장 — 한 실행의 7회 호출이 서로 덮어쓰지 않게 한다.

    A-186: 구 코드는 `xverify_{날짜}.md` 고정이라 한 런의 마지막 판정만 남았다
    (아티팩트가 항상 1파일·수백 바이트였던 원인).
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = date.today()
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    slug = _slug(label)
    n = 1
    while (OUT_DIR / f"xverify_{stamp}_{run_id}_{slug}_{n}.md").exists():
        n += 1
    out = OUT_DIR / f"xverify_{stamp}_{run_id}_{slug}_{n}.md"
    status = "❌ 실패" if failed else "✅ 판정"
    out.write_text(
        f"# GPT 교차검증 — {stamp} [{status}]\n\n"
        f"- 모델: {MODEL} (effort={EFFORT})\n- 대상: {label}\n- 런: {run_id}\n\n---\n\n{body}\n",
        encoding="utf-8")
    print(f"[완료] 교차검증 → {out}")
    return out


def _step_summary(line: str) -> None:
    """GitHub Step Summary에 한 줄 — 실패가 초록 결론에 묻히지 않게 한다."""
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    try:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception:
        pass


if __name__ == "__main__":
    sys.exit(main())
