"""
LLM 라우터 — 작업 유형에 따라 최적 LLM으로 자동 라우팅.
에이전트는 직접 특정 LLM을 호출하는 대신 이 모듈을 통해 쿼리를 전달한다.

라우팅 기준 (INDEX.md §LLM Routing Logic 기반):
  REAL_TIME_RESEARCH   → Perplexity  (실시간 웹, 최신 시장 데이터)
  LARGE_DOCUMENT       → Gemini      (문서 > 50 페이지, 멀티모달)
  STRUCTURED_EXTRACT   → OpenAI      (JSON/표 추출, 산술 검증)
  CLAUDE_NATIVE        → passthrough (코드 생성, 복잡한 추론 — Claude가 직접 처리)
"""

from __future__ import annotations

import os
from enum import Enum
from typing import Optional

from src.utils.perplexity_client import query_perplexity, PERPLEXITY_LARGE_MODEL
from src.utils.gemini_client import query_gemini, count_tokens, GEMINI_PRO_MODEL, GEMINI_FLASH_MODEL
from src.utils.openai_client import query_openai, GPT4O_MODEL, GPT4O_MINI_MODEL

# 문서를 Gemini로 보내는 최소 토큰 기준 (~50 페이지 분량)
LARGE_DOCUMENT_TOKEN_THRESHOLD = 30_000


class TaskType(Enum):
    """에이전트가 쿼리 시 지정하는 작업 유형."""
    REAL_TIME_RESEARCH = "real_time_research"   # Perplexity: 최신 시세, 지정학, 기후
    LARGE_DOCUMENT = "large_document"           # Gemini: WASDE, EPA RFS 원문, 보고서
    STRUCTURED_EXTRACT = "structured_extract"   # OpenAI: JSON/표 출력, 산술 검증
    CLAUDE_NATIVE = "claude_native"             # Claude passthrough: 코드, 심층 추론


# 에이전트 ID → 기본 작업 유형 매핑 (INDEX.md 기준)
AGENT_DEFAULT_TASK: dict[str, TaskType] = {
    "C-02": TaskType.REAL_TIME_RESEARCH,    # Market Research
    "C-06": TaskType.LARGE_DOCUMENT,        # EDA (대용량 데이터)
    "P1-01": TaskType.REAL_TIME_RESEARCH,   # Commodity Analyst
    "P1-02": TaskType.REAL_TIME_RESEARCH,   # Geopolitical Analyst
    "P1-03": TaskType.REAL_TIME_RESEARCH,   # Climate Specialist
    "P1-04": TaskType.REAL_TIME_RESEARCH,   # Supply Chain Analyst
    "P2-04": TaskType.LARGE_DOCUMENT,       # NLP/Sentiment Analyst
}


class LLMRouter:
    """
    멀티-LLM 라우터.

    사용 예시:
        router = LLMRouter()

        # 실시간 시장 조사 (Perplexity)
        result = router.query(
            TaskType.REAL_TIME_RESEARCH,
            "2026년 4월 기준 대두유 선물가격 동향 및 주요 변동 요인",
            agent_id="C-02"
        )

        # 대용량 문서 분석 (Gemini)
        result = router.query(
            TaskType.LARGE_DOCUMENT,
            "이 WASDE 보고서에서 대두 수급 전망을 요약하세요",
            document_text=wasde_full_text
        )

        # 구조화된 표 추출 (OpenAI)
        result = router.query(
            TaskType.STRUCTURED_EXTRACT,
            "공급업체별 CIF 단가를 마크다운 표로 추출하세요",
            raw_text=offer_sheet_text
        )
    """

    def query(
        self,
        task_type: TaskType,
        prompt: str,
        document_text: Optional[str] = None,
        system_prompt: Optional[str] = None,
        agent_id: Optional[str] = None,
        use_powerful_model: bool = False,
    ) -> str:
        """
        작업 유형에 따라 최적 LLM으로 라우팅하여 응답 반환.

        Args:
            task_type: 작업 유형 (TaskType enum)
            prompt: 질문 또는 지시사항
            document_text: 분석 대상 문서 (LARGE_DOCUMENT 작업에 사용)
            system_prompt: 시스템 역할 재정의 (기본값 사용 권장)
            agent_id: 호출 에이전트 ID (로깅용, 예: "C-02")
            use_powerful_model: True이면 각 LLM의 대용량/고성능 모델 사용

        Returns:
            LLM 응답 텍스트
        """
        if task_type == TaskType.REAL_TIME_RESEARCH:
            model = PERPLEXITY_LARGE_MODEL if use_powerful_model else None
            kwargs = {}
            if model:
                kwargs["model"] = model
            if system_prompt:
                kwargs["system_prompt"] = system_prompt
            return query_perplexity(prompt, **kwargs)

        elif task_type == TaskType.LARGE_DOCUMENT:
            # 문서 없이 호출된 경우 토큰 체크 후 자동 판단
            if document_text and not use_powerful_model:
                token_count = count_tokens(document_text)
                if token_count < LARGE_DOCUMENT_TOKEN_THRESHOLD:
                    # 소형 문서는 Flash 모델로 비용 절감 (MEMORY L-008: gemini-2.0-flash)
                    return query_gemini(prompt, document_text=document_text,
                                       model=GEMINI_FLASH_MODEL)
            return query_gemini(prompt, document_text=document_text,
                                model=GEMINI_PRO_MODEL)

        elif task_type == TaskType.STRUCTURED_EXTRACT:
            model = GPT4O_MODEL if use_powerful_model else GPT4O_MINI_MODEL
            return query_openai(prompt, system_prompt=system_prompt, model=model)

        elif task_type == TaskType.CLAUDE_NATIVE:
            # Claude Code가 직접 처리 — 프롬프트를 그대로 반환
            # (에이전트가 Claude에 직접 제출하는 용도)
            return prompt

        else:
            raise ValueError(
                f"[오류] 알 수 없는 작업 유형: {task_type}. "
                f"TaskType enum 값을 확인하세요."
            )

    @staticmethod
    def auto_route(prompt: str, agent_id: Optional[str] = None) -> TaskType:
        """
        에이전트 ID 기반 기본 라우팅 추천.
        명시적 TaskType 지정이 불가능한 경우의 fallback.
        """
        if agent_id and agent_id in AGENT_DEFAULT_TASK:
            return AGENT_DEFAULT_TASK[agent_id]

        # 키워드 기반 휴리스틱 라우팅
        lower = prompt.lower()
        if any(kw in lower for kw in ["현재", "최신", "오늘", "지금", "실시간", "today", "latest"]):
            return TaskType.REAL_TIME_RESEARCH
        if any(kw in lower for kw in ["보고서", "문서", "report", "document", "전문"]):
            return TaskType.LARGE_DOCUMENT
        if any(kw in lower for kw in ["표", "테이블", "추출", "table", "extract", "json"]):
            return TaskType.STRUCTURED_EXTRACT
        return TaskType.CLAUDE_NATIVE
