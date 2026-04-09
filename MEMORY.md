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
