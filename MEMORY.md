# MEMORY.md — Project Nexus
> **Agent auto-memory file.** Append new entries after each resolved blocker or completed session.
> Never overwrite existing entries. Read this file at session start (CLAUDE.md §BOOT step 2).
> Format: `[YYYY-MM-DD] [ID] Category | Issue | Fix`

---

## Failure Patterns — Pre-Populated

> These are known pitfalls pre-loaded from project inception. Add new entries below the last entry.

### Library Incompatibilities
| ID | Issue | Fix |
|---|---|---|
| L-001 | `prophet` requires `pystan >= 3.0` — conflicts with older Azure ML environments | Pin: `prophet==1.1.5`, `pystan==3.9.0` |
| L-002 | `snowflake-connector-python` v3.x breaks with pandas v1.x | Use `snowflake-connector-python >= 3.5` with `pandas >= 2.0` |
| L-003 | `torch` GPU version mismatch on Azure ML compute | Specify CUDA version in `requirements.txt`: `torch==2.1.0+cu118` |

### API & Connection Issues
| ID | Issue | Fix |
|---|---|---|
| A-001 | Snowflake query timeout on large joins (> 10M rows) | Add `statement_timeout_in_seconds = 300`; break into chunked queries |
| A-002 | Azure ML SDK authentication token expiry mid-pipeline | Implement token refresh with `ServicePrincipalAuthentication` |
| A-003 | Perplexity API intermittent 429 (rate limit) | Exponential backoff: 2s → 4s → 8s → 16s; max 4 retries |

### Modeling & Data Pitfalls
| ID | Issue | Fix |
|---|---|---|
| M-001 | Time series train/test split ignoring time order → data leakage | Always use `TimeSeriesSplit`; never shuffle time series data |
| M-002 | FX rate applied to wrong date (T vs T+1 settlement) | Use T+2 settlement convention; document in data dictionary |
| M-003 | Outlier soybean oil prices (market spike days) distort ARIMA fit | IQR-based outlier capping before fitting; log-transform prices |
| M-004 | Seasonal decomposition on monthly data with < 24 months fails | Require minimum 24 months; fall back to ETS if insufficient |

### Architecture & Code Structure
| ID | Issue | Fix |
|---|---|---|
| C-001 | Circular imports when refactoring `src/` modules | Keep `utils.py` dependency-free; import direction: `utils → models → pipelines` |
| C-002 | Notebook outputs bloat GitHub repo (embedded images) | Use `nbstripout` as pre-commit hook; store outputs in Azure Blob Storage |
| C-003 | Hardcoded Snowflake warehouse name causes staging/prod confusion | Use `SNOWFLAKE_WAREHOUSE` env variable; define in `.env.template` |

### LLM-Specific Pitfalls
| ID | Issue | Fix |
|---|---|---|
| LLM-001 | Claude hallucinates column names not in schema | Always paste schema header (first 3 rows or `df.dtypes`) in prompt |
| LLM-002 | Long analysis prompts lose context mid-response | Break into sub-tasks; use README.md §QR as persistent anchor |
| LLM-003 | Different LLMs return inconsistent output formats | Specify exact format in prompt: "respond only with a markdown table with columns: X, Y, Z" |

---

## Session Learnings — Append New Entries Here

<!-- FORMAT: | [YYYY-MM-DD] | [ID] | Category | Issue encountered | Resolution | -->
| Date | ID | Category | Issue | Resolution |
|---|---|---|---|---|
| 2026-04-03 | S-001 | Setup | Initial project scaffolding | CLAUDE.md, README.md, Skills.md, MEMORY.md, .claude/rules/ created |
| 2026-04-09 | S-002 | Setup | Multi-LLM integration | src/utils/ created: llm_router.py, perplexity_client.py, gemini_client.py, openai_client.py. Keys: PERPLEXITY_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY (store in GitHub Secrets + Azure Key Vault — never in code) |
| 2026-04-09 | L-004 | Library | ChatGPT Team ≠ OpenAI API | ChatGPT Team subscription does not include API access. Obtain separate API key from platform.openai.com with billing enabled |
| 2026-04-09 | L-005 | Library | Gemini AI Pro ≠ Gemini API | Gemini AI Pro (Google One) subscription does not auto-provision API access. Use aistudio.google.com to generate a separate API key |
| 2026-04-09 | L-006 | Library | Perplexity API model names change frequently | Use PERPLEXITY_ONLINE_MODEL constant in perplexity_client.py rather than hardcoding model strings |
| 2026-04-10 | PM-001 | PM Session | Session 01: WBS 초안 수립, C-01/C-02 스킬 파일 완성, Phase 1 상세 WBS 작성 완료 | 다음 세션: B-001(Azure KV) 해결 확인 → phase1/ 스킬 파일 5개 작성 → WBS 1.1.1 착수 |
| 2026-04-15 | L-007 | Library | Perplexity 모델명 일괄 변경 (2025년) — llama-3.1-sonar-* 포맷 전면 폐기 | sonar-pro (구 large), sonar-deep-research (구 huge), sonar (구 small). perplexity_client.py 상수 업데이트 완료. llm_health_check.yml ping 모델도 sonar로 수정 |
| 2026-04-15 | S-003 | Setup | Stream idle timeout 발생 원인 | Write 도구로 200줄 이상 파일 생성 시 스트림 타임아웃. 해결: 파일을 섹션별로 분할 작성 후 개별 커밋 |
| 2026-04-15 | S-004 | Setup | GitHub 미반영 반복 원인 | 세션 컨텍스트 소진 시 git commit/push 단계 미도달. 해결: 파일 생성 즉시 소규모 커밋 → 대형 파일 작성 전 먼저 push |
| 2026-04-15 | PM-002 | PM Session | Session 02-03: FRED/EIA/BOK ECOS API 등록 완료. P1-01/P1-02 스킬 파일, Phase 1 가이드, docs/research_desk/MEMORY.md, src/analytics/importance_matrix.json 생성. 작업 환경: Claude Code+GitHub → VS Code Web(Azure ML) → Snowflake | 다음 세션: WBS 한국어 개정(Plan/Execute 분리, 1.6 보고 체계 추가) → Gantt CSV → P1-03/P1-04/P1-05 스킬 파일 작성 → WBS 1.1.1 착수(C-04+P1-05) |
| 2026-04-20 | L-008 | Library | LLM 모델 업그레이드 (2025 최신) | Claude Opus 4.6 → Opus 4.7 (전략 분석 역할 전체: P1-01/02/03, P2-01/02, P3-01/03/04); Gemini 1.5-pro → 2.5-pro, 1.5-flash → 2.0-flash. gemini_client.py 상수 및 전체 스킬 파일 INDEX.md 업데이트 완료 |
| 2026-04-20 | PM-003 | PM Session | Session 04: WBS 1.1.2~1.1.6 커넥터 5종(economic/shipping/wasde/climate/gpr) + GitHub Actions 병렬 워크플로우 + data/schemas/ YAML 5종 + 자동화 절차서 커밋. P1-03 스킬 파일(RISEN 프레임워크, AA 프로토콜 4종) 생성. LLM 모델 전체 업그레이드 완료 | 다음 세션: P1-04(공급망·물류) · P1-05(파이프라인 아키텍트) 스킬 파일 → WBS 1.1.1 Schema Design 착수 |
