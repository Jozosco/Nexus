"""
Google Gemini API 클라이언트 — 대용량 문서 분석 및 멀티모달 처리 전용.
2M 토큰 컨텍스트 윈도우 활용: WASDE 보고서, EPA 정책 문서, 대용량 데이터셋.
사용 에이전트: C-02 Market Research (문서 > 50페이지), C-06 EDA (데이터 > 1M 행)
"""

import os
import time
from typing import Optional, Union
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable

# 최신 Gemini 모델 — 2M 토큰 컨텍스트 지원
GEMINI_PRO_MODEL = "gemini-1.5-pro"
GEMINI_FLASH_MODEL = "gemini-1.5-flash"  # 빠른 처리 / 저비용 (간단한 요약용)


def get_gemini_model(model: str = GEMINI_PRO_MODEL) -> genai.GenerativeModel:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "[오류] GEMINI_API_KEY 환경변수가 설정되지 않았습니다. "
            "Google AI Studio(aistudio.google.com)에서 키를 발급받으세요."
        )
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model)


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
    gemini_model = get_gemini_model(model)

    full_prompt = prompt
    if document_text:
        full_prompt = (
            f"다음 문서를 분석하여 대두유 공급망 및 구매 의사결정과 관련된 핵심 내용을 "
            f"한국어로 요약하세요.\n\n"
            f"분석 요청:\n{prompt}\n\n"
            f"문서 내용:\n{document_text}"
        )

    generation_config = genai.GenerationConfig(
        temperature=0.1,  # 분석 작업은 낮은 온도로 일관성 유지
        max_output_tokens=8192,
    )

    delay = 2
    for attempt in range(max_retries):
        try:
            response = gemini_model.generate_content(
                full_prompt,
                generation_config=generation_config,
            )
            return response.text
        except ResourceExhausted as e:  # 429 equivalent
            if attempt == max_retries - 1:
                raise RuntimeError(
                    f"[오류] Gemini API 할당량 초과 ({max_retries}회 재시도 후 실패): {e}"
                ) from e
            time.sleep(delay)
            delay *= 2
        except ServiceUnavailable as e:
            if attempt == max_retries - 1:
                raise RuntimeError(
                    f"[오류] Gemini API 서비스 불가 ({max_retries}회 재시도 후 실패): {e}"
                ) from e
            time.sleep(delay)
            delay *= 2
    return ""


def count_tokens(text: str, model: str = GEMINI_PRO_MODEL) -> int:
    """문서를 Gemini에 전달하기 전 토큰 수를 사전 확인."""
    gemini_model = get_gemini_model(model)
    result = gemini_model.count_tokens(text)
    return result.total_tokens
