"""
Google Gemini API 클라이언트 — 대용량 문서 분석 및 멀티모달 처리 전용.
2M 토큰 컨텍스트 윈도우 활용: WASDE 보고서, EPA 정책 문서, 대용량 데이터셋.
사용 에이전트: C-02 Market Research (문서 > 50페이지), C-06 EDA (데이터 > 1M 행)

SDK: google-genai (구 google-generativeai 패키지 지원 종료 — MEMORY L-010)
"""

from __future__ import annotations

import os
import time
from typing import Optional

from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError

# 최신 Gemini 모델 — 2M 토큰 컨텍스트 지원 (2025 기준 최신)
GEMINI_PRO_MODEL   = "gemini-2.5-pro"    # 구: gemini-1.5-pro — 추론 강화, 컨텍스트 확장
GEMINI_FLASH_MODEL = "gemini-2.0-flash"  # 구: gemini-1.5-flash — 속도/비용 최적화


def _get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "[오류] GEMINI_API_KEY 환경변수가 설정되지 않았습니다. "
            "Google AI Studio(aistudio.google.com)에서 키를 발급받으세요."
        )
    return genai.Client(api_key=api_key)


def query_gemini(
    prompt: str,
    document_text: Optional[str] = None,
    model: str = GEMINI_PRO_MODEL,
    max_retries: int = 4,
) -> str:
    """
    Gemini API 호출 — 대용량 문서 분석.

    Args:
        prompt: 분석 지시사항 또는 질문
        document_text: 분석 대상 문서 본문 (None이면 프롬프트만 사용)
        model: 사용할 Gemini 모델
        max_retries: 최대 재시도 횟수

    Returns:
        분석 결과 텍스트
    """
    client = _get_client()

    full_prompt = prompt
    if document_text:
        full_prompt = (
            f"다음 문서를 분석하여 대두유 공급망 및 구매 의사결정과 관련된 핵심 내용을 "
            f"한국어로 요약하세요.\n\n"
            f"분석 요청:\n{prompt}\n\n"
            f"문서 내용:\n{document_text}"
        )

    config = types.GenerateContentConfig(
        temperature=0.1,       # 분석 작업은 낮은 온도로 일관성 유지
        max_output_tokens=8192,
    )

    delay = 2
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=full_prompt,
                config=config,
            )
            return response.text
        except ClientError as e:
            if getattr(e, "code", None) == 429:
                if attempt == max_retries - 1:
                    raise RuntimeError(
                        f"[오류] Gemini API 할당량 초과 ({max_retries}회 재시도 후 실패): {e}"
                    ) from e
                time.sleep(delay)
                delay *= 2
            else:
                raise RuntimeError(f"[오류] Gemini API 클라이언트 오류: {e}") from e
        except ServerError as e:
            if attempt == max_retries - 1:
                raise RuntimeError(
                    f"[오류] Gemini API 서비스 불가 ({max_retries}회 재시도 후 실패): {e}"
                ) from e
            time.sleep(delay)
            delay *= 2
    return ""


def count_tokens(text: str, model: str = GEMINI_PRO_MODEL) -> int:
    """문서를 Gemini에 전달하기 전 토큰 수를 사전 확인."""
    client = _get_client()
    response = client.models.count_tokens(model=model, contents=text)
    return response.total_tokens
