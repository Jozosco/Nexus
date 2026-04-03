# CLAUDE.md — Project Nexus
> **Purpose**: This file is the single source of truth for any AI agent (Claude or otherwise) operating in this repository.
> Read this file in full before responding to any task. When context is ambiguous, re-read the relevant section.

---

## HOW TO USE THIS FILE (Token Efficiency Note)
- Section headers are searchable anchors. Jump directly to the relevant section.
- Prefer referencing section names in prompts (e.g., "follow §RULES.LANGUAGES") over re-pasting rules.
- If a task spans multiple sections, explicitly list which sections apply before beginning work.
- Never re-summarize this file in responses unless explicitly asked.

---

## §1 PROJECT MAP — The Compass

### 1.1 Project Identity
| Field | Value |
|---|---|
| **Project Name** | Nexus |
| **Organization** | F&B Manufacturing Company (Confidential) |
| **Owner Role** | Data Scientist / Project Lead |
| **AI Role** | Commodity Analyst, Senior PM, Supply Chain Engineer, AI Systems Architect, Full-stack Engineer, Coder Reviewer(QA) |

### 1.2 North Star Objective
> Maximize P&L by minimizing risks arising from global supply chain volatility in imported raw materials.

### 1.3 Problem Decomposition
```
Supply Chain Risk
├── Price Volatility          → Commodity price forecasting (ARIMA, Prophet, LSTM)
├── Supplier Risk             → Supplier scoring model (clustering, risk index)
├── Demand Uncertainty        → Demand forecasting per SKU/category
├── Logistics Disruption      → Lead-time modeling, buffer stock optimization
├── Geopolitical / FX Risk    → Scenario analysis, sensitivity modeling
└── P&L Impact                → Simulation → procurement recommendation
```

### 1.4 Tech Stack (Canonical)
| Layer | Tool |
|---|---|
| Cloud Data Warehouse | Snowflake |
| ML Platform | Azure ML Studio |
| Languages | Python (primary), R (statistical), SQL (data access) |
| IDE | Jupyter Notebook, VS Code |
| LLM Access | Claude Pro, ChatGPT Team, Gemini AI Pro, Perplexity Pro |
| Version Control | GitHub (via Claude Code Web — Research Preview) |

### 1.5 Firewall Constraint (Critical)
- **No CLI installation inside the corporate firewall.**
- All code development and agent operation occurs on Claude Code Web (Research Preview) connected to GitHub.
- Do NOT instruct the user to `pip install`, `brew install`, or run terminal commands inside the corporate network.
- Propose cloud-native alternatives (Azure ML pipelines, Snowflake Snowpark, GitHub Actions) for automation.

### 1.6 Deliverable Map
```
Phase 1 — Foundation     : Data pipeline (Snowflake → Azure ML), EDA, baseline models
Phase 2 — Modeling       : Forecasting models, risk scoring, scenario simulator
Phase 3 — Optimization   : Procurement optimizer, P&L impact model
Phase 4 — Productionize  : Scheduled pipelines, dashboards, reporting automation
Phase 5 — Governance     : Model monitoring, drift detection, documentation
```

---

## §2 RULE BOOK

### 2.1 Settings (Code Style & Process)

#### 2.1.1 Code Style
- **Python**: Follow PEP 8. Max line length: 100 chars. Use f-strings over `.format()`. Type hints required for all function signatures.
- **R**: Follow tidyverse style guide. Use `<-` for assignment. Pipe (`|>` or `%>%`) for chains longer than 2 steps.
- **SQL (Snowflake)**: Uppercase keywords. Snake_case for identifiers. CTEs over nested subqueries. Always include `LIMIT` in exploratory queries.
- **Notebooks**: One notebook per analysis unit. Clear markdown headers per section. Outputs must be reproducible with `Restart & Run All`.

#### 2.1.2 Testing
- Unit tests: `pytest` for Python modules, `testthat` for R packages.
- Data validation: Use `great_expectations` (Python) or `pointblank` (R) for schema/quality checks.
- Model validation: Always compare against a naive baseline (e.g., last-value, seasonal naive).
- Before committing any model code, confirm: train/test split is time-aware (no future leakage).

#### 2.1.3 Commit Conventions
```
feat: add LSTM price forecasting module
fix: correct FX conversion rate in procurement model
refactor: extract supplier scoring into separate module
data: update raw material price dataset to Q1-2026
docs: update project map phase 2 deliverables
```

#### 2.1.4 File Naming
```
notebooks/   01_eda_raw_material_prices.ipynb
             02_model_demand_forecast.ipynb
src/         price_forecasting.py
             supplier_risk.py
             procurement_optimizer.py
data/        raw/        (never committed — gitignored)
             processed/  (outputs only, schema-documented)
reports/     2026Q1_supply_risk_summary.md
```

---

### 2.2 Rules

#### 2.2.1 Programming Language
| Language | When to Use |
|---|---|
| **Python** | ML models, data pipelines, API integration, automation scripts |
| **R** | Statistical inference, econometrics (VAR, GARCH), visualization (ggplot2) |
| **SQL** | All Snowflake queries, data extraction, aggregations |
| **C++** | Only if Python performance is insufficient after profiling (e.g., simulation loops > 10M iterations) |
| **Java** | Only for Snowflake UDF/UDTF deployment if Python UDF is not feasible |

> Default: start with Python. Switch only when justified with a one-line comment `# Using R: VAR model requires tseries package unavailable in Python equiv.`

#### 2.2.2 Error Messages & Language
- **All error messages, warnings, and log outputs must be written in Korean (한국어).**
- Exception: Stack traces from external libraries remain in English as-is.
- User-facing report text: Korean.
- Code comments: Korean preferred; English acceptable for widely-used technical terms (e.g., `# ARIMA fitting`, `# outlier detection`).

Example:
```python
except ValueError as e:
    raise ValueError(f"[오류] 원자재 가격 데이터 로드 실패: {e}. 데이터 형식을 확인하세요.") from e
```

#### 2.2.3 Libraries (Canonical + Constraints)
**Python — Approved**
```
pandas >= 2.0        # tabular data
numpy >= 1.26        # numerical ops
scikit-learn >= 1.4  # classical ML
statsmodels >= 0.14  # ARIMA, VAR, econometrics
prophet >= 1.1       # time series with seasonality
lightgbm >= 4.0      # gradient boosting
torch >= 2.0         # deep learning (LSTM, Transformer)
snowflake-connector-python  # Snowflake access
azureml-sdk          # Azure ML pipeline integration
great-expectations   # data validation
plotly >= 5.0        # interactive charts
```

**R — Approved**
```
tidyverse            # data wrangling + ggplot2
forecast             # ARIMA, ETS, TBATS
tseries              # unit root tests, GARCH
vars                 # Vector Autoregression
rugarch              # GARCH family models
DBI + odbc           # Snowflake JDBC connection
```

**Constraints**
- Do NOT use `openpyxl` or direct Excel I/O for data pipelines — use Snowflake as the single source of truth.
- Do NOT use `pickle` for model serialization — use `joblib` (sklearn) or `mlflow.log_model()`.
- Do NOT import `os.system()` or `subprocess` for data access — use SDK connectors only.

---

### 2.3 Self-Context

#### 2.3.1 Project Goals and Direction
- **Primary goal**: Actionable procurement decisions, not academic model accuracy.
- **Success metric**: Measurable reduction in raw material cost variance and improved P&L predictability.
- Models must produce human-readable explanations alongside predictions (SHAP, feature importance).
- Prioritize interpretability > marginal accuracy gains when business stakeholders are the audience.

#### 2.3.2 Preferred Style
- **Thinking style**: Structured → top-down (problem → subproblems → solutions).
- **Response style**: Lead with conclusion, support with evidence. No preamble.
- **Code style**: Self-documenting variable names. No magic numbers — use named constants.
- **Analysis style**: Always state assumptions explicitly. Flag data quality issues before modeling.
- When multiple approaches exist, present a comparison table (method / pros / cons / recommended).

#### 2.3.3 Formatting
- Use markdown tables for comparisons, parameter listings, and results.
- Use numbered lists for sequential steps, bullet lists for unordered options.
- Use code blocks with language tags for all code snippets.
- Response length: match task complexity. One-liner answers for factual questions; structured breakdowns for design/analysis tasks.
- Avoid decorative prose. Every sentence must add information.

---

## §3 BOUNDARIES OF ABILITY

### 3.1 What Claude CAN Do in This Project

| Capability | Method | Notes |
|---|---|---|
| **API calls** | `requests`, `httpx`, vendor SDKs | Rate limit handling required; use retry logic |
| **Snowflake access** | `snowflake-connector-python`, SQL via `DBI` (R) | Credentials via environment variables only |
| **Azure ML pipeline** | `azureml-sdk` (Python) | Model training, registration, deployment |
| **GitHub operations** | Claude Code Web + GitHub integration | Commit, push, PR, file management |
| **Automation scripts** | GitHub Actions, Azure ML pipelines | No local cron — cloud-native only |
| **Statistical modeling** | Python + R (see §2.2.3) | Full modeling lifecycle |
| **Data visualization** | Plotly, ggplot2, matplotlib | Export as HTML or PNG |
| **Document generation** | Markdown, Jupyter, PDF export | Reports, summaries, slide drafts |
| **Web search / research** | Perplexity Pro, Claude web search | Commodity market research, supplier background |
| **Multi-LLM orchestration** | Manual routing by task type | See skills/PM_Agent.md for routing logic |

### 3.2 What Claude CANNOT Do (Hard Limits)

| Limitation | Reason | Workaround |
|---|---|---|
| Access internal corporate network | Firewall restriction | Use cloud-native data exports to Snowflake |
| Install software inside firewall | Security policy | Use cloud IDEs (Azure ML Notebooks, Claude Code Web) |
| Access real-time internal ERP/MES data directly | No direct DB connector allowed | Scheduled Snowflake data sync |
| Commit secrets / credentials | Security | Use GitHub Secrets + Azure Key Vault |
| Execute arbitrary shell commands on local machines | Firewall / policy | Use Azure ML compute clusters |
| Make procurement decisions autonomously | Human-in-the-loop required | AI provides recommendations; human approves |
| Access external paid data without authorization | Budget / legal | Flag required data sources for procurement approval |

---

## §4 TRIAL AND ERROR LOG

> **Rule**: Before starting any task, scan this log for relevant past failures. After resolving a new issue, add it here immediately.

### 4.1 Library Incompatibilities
| ID | Issue | Fix |
|---|---|---|
| L-001 | `prophet` requires `pystan >= 3.0` — conflicts with older Azure ML environments | Pin: `prophet==1.1.5`, `pystan==3.9.0` |
| L-002 | `snowflake-connector-python` v3.x breaks with pandas v1.x | Use `snowflake-connector-python >= 3.5` with `pandas >= 2.0` |
| L-003 | `torch` GPU version mismatch on Azure ML compute | Specify CUDA version explicitly in `requirements.txt`: `torch==2.1.0+cu118` |

### 4.2 API & Connection Issues
| ID | Issue | Fix |
|---|---|---|
| A-001 | Snowflake query timeout on large joins (> 10M rows) | Add `statement_timeout_in_seconds = 300`; break into chunked queries |
| A-002 | Azure ML SDK authentication token expiry mid-pipeline | Implement token refresh with `ServicePrincipalAuthentication` |
| A-003 | Perplexity API intermittent 429 (rate limit) | Implement exponential backoff: 2s → 4s → 8s → 16s; max 4 retries |

### 4.3 Modeling & Data Pitfalls
| ID | Issue | Fix |
|---|---|---|
| M-001 | Time series train/test split without respecting time order → data leakage | Always use `TimeSeriesSplit` from sklearn; never shuffle time series data |
| M-002 | FX rate applied to wrong date (T vs T+1 settlement) | Use T+2 settlement convention; document in data dictionary |
| M-003 | Outlier raw material prices (market spike days) distort ARIMA fit | Apply IQR-based outlier capping before fitting; log-transform prices |
| M-004 | Seasonal decomposition on monthly data with < 2 full years fails | Require minimum 24 months of data; fall back to ETS if insufficient |

### 4.4 Architecture & Code Structure
| ID | Issue | Fix |
|---|---|---|
| C-001 | Circular imports when refactoring src/ modules | Keep `utils.py` dependency-free; import direction: `utils → models → pipelines` |
| C-002 | Notebook outputs bloat GitHub repo (embedded images) | Add `nbstripout` as pre-commit hook; store outputs in Azure Blob Storage |
| C-003 | Hardcoded Snowflake warehouse name causes staging/prod confusion | Use `SNOWFLAKE_WAREHOUSE` env variable; define in `.env.template` |

### 4.5 LLM-Specific Pitfalls
| ID | Issue | Fix |
|---|---|---|
| LLM-001 | Claude hallucinates column names not in schema | Always paste schema header (first 3 rows or `df.dtypes`) in prompt |
| LLM-002 | Long analysis prompts lose context mid-response | Break into sub-tasks; use §SELF-CONTEXT section as persistent anchor |
| LLM-003 | Different LLMs return inconsistent table formats | Specify exact output format in prompt: "respond only with a markdown table with columns: X, Y, Z" |
