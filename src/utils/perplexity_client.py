"""
Perplexity API 클라이언트 — 실시간 웹 인텔리전스 전용.
OpenAI SDK와 호환되는 엔드포인트를 사용하므로 openai 패키지로 구동.
사용 에이전트: C-02 Market Research, P1-01~04 Phase 1 analysts
"""

import os
import time
from typing import Optional
from openai import OpenAI, APIStatusError, APIConnectionError

# 실시간 검색이 가능한 온라인 모델 — 오프라인 모델보다 비용이 높지만 최신 데이터 필수
# MEMORY L-006 / L-007: Perplexity 모델명은 자주 변경됨 — 아래 상수만 수정하면 전체 반영
# 2025년 이후 명칭 변경: llama-3.1-sonar-* → sonar / sonar-pro / sonar-deep-research
# Perplexity Pro 구독 사용 가능 모델:
PERPLEXITY_PING_MODEL   = "sonar"              # 헬스 체크·저비용 단순 쿼리
PERPLEXITY_ONLINE_MODEL = "sonar-pro"          # 구: llama-3.1-sonar-large-128k-online — 실시간 연구 기본
PERPLEXITY_LARGE_MODEL  = "sonar-deep-research" # 구: llama-3.1-sonar-huge-128k-online — 심층 조사 (고비용)


def get_perplexity_client() -> OpenAI:
    api_key = os.environ.get("PERPLEXITY_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "[오류] PERPLEXITY_API_KEY 환경변수가 설정되지 않았습니다. "
            ".env.template을 참고하여 설정하세요."
        )
    return OpenAI(
        api_key=api_key,
        base_url="https://api.perplexity.ai",
    )


def query_perplexity(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: str = PERPLEXITY_ONLINE_MODEL,
    max_retries: int = 4,
) -> str:
    """
    Perplexity API 호출 — 지수 백오프 재시도 포함.

    Args:
        prompt: 검색/질의 내용
        system_prompt: 시스템 역할 정의 (없으면 기본값 사용)
        model: 사용할 Perplexity 모델
        max_retries: 최대 재시도 횟수

    Returns:
        응답 텍스트 (인용 출처 포함)
    """
    if system_prompt is None:
        system_prompt = (
            "당신은 대두유 공급망 및 원자재 시장 전문 리서치 어시스턴트입니다. "
            "최신 시장 데이터, 지정학적 이벤트, 기후 동향을 기반으로 "
            "출처를 명시한 간결한 한국어 분석을 제공하세요."
        )

    client = get_perplexity_client()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]

    delay = 2
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
            )
            return response.choices[0].message.content
        except APIStatusError as e:
            if e.status_code == 429:  # Rate limit
                if attempt == max_retries - 1:
                    raise RuntimeError(
                        f"[오류] Perplexity API 속도 제한 초과 ({max_retries}회 재시도 후 실패): {e}"
                    ) from e
                time.sleep(delay)
                delay *= 2  # 2s → 4s → 8s → 16s (MEMORY A-003)
            else:
                raise RuntimeError(f"[오류] Perplexity API 호출 실패: {e}") from e
        except APIConnectionError as e:
            if attempt == max_retries - 1:
                raise RuntimeError(
                    f"[오류] Perplexity API 연결 실패 ({max_retries}회 재시도 후 실패): {e}"
                ) from e
            time.sleep(delay)
            delay *= 2
    return ""  # 실행되지 않음 — 타입 체커용
