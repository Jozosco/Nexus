"""
OpenAI API 클라이언트 — 구조화된 데이터 추출 및 정형 출력 전용.
JSON 스키마 강제 출력(structured outputs), 빠른 산술 검증에 특화.
사용 에이전트: C-03 Data Scientist (결과 검증), C-06 EDA (이상값 분류)
참고: ChatGPT Team 구독 ≠ API 액세스. platform.openai.com에서 별도 API 키 발급 필요.
"""

import os
import time
from typing import Optional, Any
from openai import OpenAI, APIStatusError, APIConnectionError

GPT4O_MODEL = "gpt-4o"
GPT4O_MINI_MODEL = "gpt-4o-mini"  # 단순 작업 / 저비용


def get_openai_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "[오류] OPENAI_API_KEY 환경변수가 설정되지 않았습니다. "
            "platform.openai.com에서 API 키를 발급받으세요. "
            "ChatGPT Team 구독은 API 액세스를 포함하지 않습니다."
        )
    return OpenAI(api_key=api_key)


def query_openai(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: str = GPT4O_MINI_MODEL,
    response_format: Optional[dict[str, Any]] = None,
    max_retries: int = 4,
) -> str:
    """
    OpenAI API 호출 — 구조화된 출력 추출.

    Args:
        prompt: 요청 내용
        system_prompt: 시스템 역할 정의
        model: 사용할 GPT 모델
        response_format: JSON 스키마 강제 출력 설정 (예: {"type": "json_object"})
        max_retries: 최대 재시도 횟수

    Returns:
        응답 텍스트
    """
    if system_prompt is None:
        system_prompt = (
            "당신은 정확한 데이터 추출 및 표 형식 변환 전문가입니다. "
            "요청된 형식에 맞게 정확하게 출력하세요. 추가 설명은 불필요합니다."
        )

    client = get_openai_client()
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    }
    if response_format:
        kwargs["response_format"] = response_format

    delay = 2
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except APIStatusError as e:
            if e.status_code == 429:
                if attempt == max_retries - 1:
                    raise RuntimeError(
                        f"[오류] OpenAI API 속도 제한 초과 ({max_retries}회 재시도 후 실패): {e}"
                    ) from e
                time.sleep(delay)
                delay *= 2
            else:
                raise RuntimeError(f"[오류] OpenAI API 호출 실패: {e}") from e
        except APIConnectionError as e:
            if attempt == max_retries - 1:
                raise RuntimeError(
                    f"[오류] OpenAI API 연결 실패 ({max_retries}회 재시도 후 실패): {e}"
                ) from e
            time.sleep(delay)
            delay *= 2
    return ""


def extract_structured_table(
    raw_text: str,
    columns: list[str],
    model: str = GPT4O_MINI_MODEL,
) -> str:
    """
    비정형 텍스트에서 지정된 컬럼의 마크다운 표를 추출.
    예: 공급업체 오퍼 시트 → 구조화된 가격 비교표
    """
    col_list = ", ".join(columns)
    prompt = (
        f"다음 텍스트에서 이 컬럼들을 포함한 마크다운 표를 추출하세요: {col_list}\n\n"
        f"텍스트:\n{raw_text}\n\n"
        f"마크다운 표만 출력하세요. 다른 텍스트는 포함하지 마세요."
    )
    return query_openai(
        prompt,
        response_format={"type": "text"},
        model=model,
    )
