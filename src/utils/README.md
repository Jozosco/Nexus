# src/utils/

This package contains the multi-LLM routing layer for Project Nexus.

## Modules
- `llm_router.py`      — Task-type-based routing to the optimal LLM
- `openai_client.py`   — OpenAI GPT wrapper (structured extraction, arithmetic)
- `gemini_client.py`   — Gemini wrapper (large documents, multi-modal)
- `perplexity_client.py` — Perplexity wrapper (real-time web intelligence)

## Usage
```python
from src.utils.llm_router import LLMRouter, TaskType

router = LLMRouter()
result = router.query(TaskType.REAL_TIME_RESEARCH, "Latest soybean oil price drivers")
```

## Security
All API keys are loaded from environment variables only.
Never hardcode keys. See .env.template for required variable names.
