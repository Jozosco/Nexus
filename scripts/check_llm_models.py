#!/usr/bin/env python3
"""
LLM 제공사별 최신 모델 목록을 라이브 API에서 조회하여 config/llm_models.json 핀 목록과 비교.
신규 모델 감지 시 GitHub Actions가 Issue를 자동 생성함 (2-2 LLM Model Monitor).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

CONFIG_PATH = Path("config/llm_models.json")
DIFF_PATH   = Path("model_diff.md")
GH_OUTPUT   = os.environ.get("GITHUB_OUTPUT", "")


def _set_output(key: str, value: str) -> None:
    if GH_OUTPUT:
        with open(GH_OUTPUT, "a") as fh:
            fh.write(f"{key}={value}\n")


def _load_pinned() -> dict[str, list[str]]:
    data = json.loads(CONFIG_PATH.read_text())
    # _comment / role_assignments 키 제외
    return {k: v for k, v in data.items() if not k.startswith("_") and k != "role_assignments"}


def _key(name: str) -> str:
    """환경변수 값 반환; 미등록이거나 공백이면 빈 문자열."""
    return os.environ.get(name, "").strip()


def _fetch_openai() -> list[str]:
    import openai
    key = _key("OPENAI_API_KEY")
    if not key:
        print("[경고] OPENAI_API_KEY 미등록 — OpenAI 모델 목록 수동 확인 필요", file=sys.stderr)
        return []
    try:
        client = openai.Client(api_key=key)
        return sorted(m.id for m in client.models.list())
    except Exception as e:
        print(f"[오류] OpenAI 모델 목록 조회 실패: {e}", file=sys.stderr)
        return []


def _fetch_gemini() -> list[str]:
    from google import genai
    from google.genai import errors as genai_errors
    key = _key("GEMINI_API_KEY")
    if not key:
        print("[경고] GEMINI_API_KEY 미등록 — Gemini 모델 목록 수동 확인 필요", file=sys.stderr)
        return []
    client = genai.Client(api_key=key)
    try:
        return sorted(m.name for m in client.models.list())
    except genai_errors.APIError as e:
        print(f"[오류] Gemini 모델 목록 조회 실패: {getattr(e, 'code', '?')} {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"[오류] Gemini 모델 목록 조회 실패: {e}", file=sys.stderr)
        return []


def _fetch_anthropic() -> list[str]:
    """Anthropic /v1/models — SDK의 models.list() 대신 직접 httpx 호출로 안정성 확보.
    SDK 버전에 따라 models.list() 미지원 케이스 대응 (MEMORY A-021).
    """
    import httpx as _httpx
    key = _key("ANTHROPIC_API_KEY")
    if not key:
        print(
            "[경고] ANTHROPIC_API_KEY 미등록/공백 — Anthropic 모델 목록 수동 확인 필요\n"
            "       등록 경로: GitHub Settings → Secrets → ANTHROPIC_API_KEY",
            file=sys.stderr,
        )
        return []
    try:
        r = _httpx.get(
            "https://api.anthropic.com/v1/models",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
        return sorted(m["id"] for m in data.get("data", []))
    except Exception as e:
        print(f"[오류] Anthropic 모델 목록 조회 실패: {e}", file=sys.stderr)
        return []


def _fetch_perplexity() -> list[str]:
    """Perplexity: /models 엔드포인트 미구현 (공식 문서 확인, 2025-05).
    API 키 유효성을 최소 ping으로 검증 후 공식 문서 기준 모델 목록 반환.
    """
    import httpx as _httpx
    key = _key("PERPLEXITY_API_KEY")
    if not key:
        print("[경고] PERPLEXITY_API_KEY 미등록 — Perplexity 모델 목록 수동 확인 필요", file=sys.stderr)
        return []
    # Perplexity는 /v1/models 엔드포인트가 없음. ping으로 키 유효성만 확인 후 문서 목록 반환.
    DOCUMENTED_MODELS = [
        "sonar", "sonar-pro", "sonar-reasoning", "sonar-reasoning-pro",
        "sonar-deep-research", "r1-1776",
    ]
    try:
        r = _httpx.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "sonar", "messages": [{"role": "user", "content": "1"}], "max_tokens": 1},
            timeout=20,
        )
        if r.status_code in (200, 400, 422):
            # 200: 정상 응답, 400/422: 키는 유효하나 요청 파라미터 문제 — 키 확인 완료
            return sorted(DOCUMENTED_MODELS)
        r.raise_for_status()
        return sorted(DOCUMENTED_MODELS)
    except Exception as e:
        print(f"[경고] Perplexity API 키 검증 실패 — 수동 확인 필요: {e}", file=sys.stderr)
        return []


FETCHERS: dict[str, Any] = {
    "openai":     _fetch_openai,
    "gemini":     _fetch_gemini,
    "anthropic":  _fetch_anthropic,
    "perplexity": _fetch_perplexity,
}


def _build_diff_report(
    pinned: dict[str, list[str]],
    live:   dict[str, list[str]],
    run_date: str,
) -> tuple[bool, str]:
    lines: list[str] = [
        "# LLM 모델 업데이트 감지 보고서",
        "",
        f"**실행 날짜**: {run_date}  ",
        f"**비교 기준 파일**: `config/llm_models.json`",
        "",
    ]
    any_new = False

    for provider in pinned:
        live_models = live.get(provider, [])
        pinned_set  = set(pinned[provider])
        live_set    = set(live_models)
        new_models  = sorted(live_set - pinned_set)
        dropped     = sorted(pinned_set - live_set)

        lines.append(f"## {provider.title()}")

        if not live_models:
            lines.append("_모델 목록 조회 실패 — 수동 확인 필요 (API 키 미등록 또는 엔드포인트 오류)_")
            lines.append("")
            continue

        if new_models:
            any_new = True
            lines.append("### 신규 모델 (config/llm_models.json 추가 + 역할 배정 검토 필요)")
            for m in new_models:
                lines.append(f"- `{m}`")
        if dropped:
            lines.append("### 제거된 모델 (폐기 확인 후 config에서 삭제 필요)")
            for m in dropped:
                lines.append(f"- ~~`{m}`~~")
        if not new_models and not dropped:
            lines.append("_변경 없음_")
        lines.append("")

    lines += [
        "---",
        "## 역할 배정 가이드",
        "",
        "신규 모델 발견 시 아래 기준으로 `config/llm_models.json` 의 `role_assignments` 업데이트:",
        "",
        "| 역할 | 선택 기준 |",
        "|---|---|",
        "| `REAL_TIME_RESEARCH` | 최신 웹 검색 포함 모델 (Perplexity sonar 계열) |",
        "| `LARGE_DOCUMENT` | 컨텍스트 윈도우 최대 모델 (Gemini 2M ctx 계열) |",
        "| `STRUCTURED_EXTRACT` | JSON 출력 신뢰도 최고 모델 (GPT-4o 계열) |",
        "| `CLAUDE_NATIVE` | 코드·추론 최강 모델 (Claude Opus/Sonnet 최신) |",
        "",
        "> **HITL 게이트**: 역할 배정 변경은 인간 검토 후 PR로 반영 (CLAUDE.md §6)",
    ]

    return any_new, "\n".join(lines)


def main() -> None:
    from datetime import date
    pinned   = _load_pinned()
    live     = {p: fn() for p, fn in FETCHERS.items()}
    any_new, report = _build_diff_report(pinned, live, date.today().isoformat())

    print(report)
    DIFF_PATH.write_text(report, encoding="utf-8")
    _set_output("new_models_found", "true" if any_new else "false")

    if any_new:
        print("\n[알림] 신규 모델 감지 — GitHub Issue 생성 예정")
    else:
        print("\n[정보] 모든 제공사 모델 목록 변경 없음")


if __name__ == "__main__":
    main()
