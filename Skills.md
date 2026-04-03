# Skills.md — Project Nexus
> This file defines all agent roles (Skills) deployable in this project.
> Each skill is a scoped sub-agent with a defined trigger, input, process, and output contract.
> Reference CLAUDE.md §1–§4 for all project rules, constraints, and context.

---

## SKILL ROUTING MAP

```
Human (Data Scientist)
        │
        ▼
[PM Agent] ──────────────── orchestrates ──────────────────────────────┐
        │                                                               │
        ├──► [Data Engineer Agent]   : Snowflake pipelines, SQL        │
        ├──► [EDA Agent]             : Exploratory analysis, profiling  │
        ├──► [Forecasting Agent]     : Price / demand time series       │
        ├──► [Risk Analyst Agent]    : Supplier risk, scenario scoring  │
        ├──► [Optimizer Agent]       : Procurement optimization, P&L    │
        ├──► [Reporting Agent]       : Summaries, slides, stakeholder   │
        └──► [Code Reviewer Agent]   : Style, security, correctness     │
                                                                        │
                        ◄───────────── status reports ─────────────────┘
```

---

## NECESSITY CLASSIFICATION

### TIER 1 — Absolutely Required (Project cannot proceed without these)

| Skill | Justification |
|---|---|
| **PM Agent** | No human PM assigned; project has multi-phase complexity requiring cross-workstream coordination |
| **Data Engineer Agent** | All analysis depends on clean Snowflake pipelines; manual SQL maintenance is error-prone and slow |
| **Forecasting Agent** | Core deliverable — price and demand forecasting is the primary analytical engine |
| **Risk Analyst Agent** | Primary business objective is risk minimization; this agent operationalizes it |

### TIER 2 — High Value (Significant efficiency gain over manual work)

| Skill | Why faster/more accurate than human |
|---|---|
| **EDA Agent** | Runs 20+ statistical checks in seconds; catches data quality issues humans miss in large Snowflake tables |
| **Optimizer Agent** | Solves procurement optimization (linear/mixed-integer programming) — infeasible to do manually at scale |
| **Reporting Agent** | Transforms raw analysis into structured Korean-language reports; eliminates formatting time |

### TIER 3 — Supportive (Good to have, lower urgency)

| Skill | When to activate |
|---|---|
| **Code Reviewer Agent** | Activate before every PR merge to main; can run asynchronously |
| **LLM Router Agent** | Useful once multiple LLMs are being called; initially manual routing is sufficient |

---

## SKILL DEFINITIONS

---

### SKILL: PM Agent
**File**: `skills/PM_agent.md` (also callable as `/pm` in Claude Code)
**Status**: TIER 1 — Activate at project start

#### Purpose
Act as the Project Manager for Project Nexus. The PM Agent maintains project state, tracks progress against the delivery phases defined in CLAUDE.md §1.6, coordinates workstreams, flags blockers, and produces status reports.

#### Justification for Sub-Agent Architecture
1. **Context persistence**: The PM Agent maintains the full project timeline and task backlog across sessions, compensating for LLM context resets.
2. **Separation of concerns**: Separating PM logic from analytical logic prevents prompt pollution — analysis agents answer "how to solve X," the PM answers "what to solve next and whether it's done."
3. **Accountability**: Without a PM role, tasks slip between sessions. This agent acts as the institutional memory.
4. **Multi-agent coordination**: As downstream agents (Forecasting, Risk, Optimizer) produce outputs, the PM Agent ingests their summaries and updates project status — no human tracking required.

#### Trigger Conditions
- Start of every new session: "What is the current project status?"
- After completing any deliverable: "Mark [deliverable] as done, update the project board."
- When blocked: "We can't access [data source] — escalate and find workaround."
- Weekly: "Generate this week's status report."

#### Input Contract
```
Required:
  - current_phase: str          # e.g., "Phase 1 — Foundation"
  - completed_tasks: list[str]  # tasks finished since last update
  - blockers: list[str]         # current impediments
  - questions: list[str]        # items needing human decision

Optional:
  - deadline: date              # if a milestone is approaching
  - stakeholder_update: bool    # whether to format output for external audience
```

#### Process Logic
```
1. Load project state from CLAUDE.md §1.6 (Deliverable Map) + last status report
2. Diff completed_tasks against pending deliverables → identify % progress per phase
3. For each blocker:
   a. Classify: data / environment / dependency / decision-required
   b. Propose resolution path (cloud-native alternatives per CLAUDE.md §3.2)
   c. Assign to appropriate downstream agent if actionable
4. Identify the single highest-priority next task (WSJF scoring: value / time-criticality / risk)
5. Check §4 Trial and Error Log for known pitfalls relevant to next task
6. Generate output in specified format
```

#### Output Contract
```markdown
## Nexus PM Report — [날짜]

### 전체 진행률
| Phase | 상태 | 완료 항목 | 잔여 항목 |
|---|---|---|---|
| Phase 1 — Foundation     | 🟢 완료 / 🟡 진행중 / 🔴 미시작 | X | Y |
...

### 이번 주 완료 항목
- [item 1]
- [item 2]

### 현재 블로커
| # | 블로커 내용 | 유형 | 해결 방안 | 담당 |
|---|---|---|---|---|
| 1 | ... | 데이터 | ... | Data Engineer Agent |

### 다음 우선순위 작업 (Top 3)
1. [최우선 작업] — 이유: [WSJF 근거]
2. ...
3. ...

### 인간 결정 필요 항목
- [ ] [질문 1]
- [ ] [질문 2]

### 주의: 관련 Trial & Error
- [§4 항목 번호]: [내용 요약]
```

#### Constraints
- Never make procurement or business decisions autonomously (CLAUDE.md §3.2)
- Always cite CLAUDE.md section when referencing rules
- Status report language: Korean
- Do not re-run analysis — delegate to the appropriate skill agent

---

### SKILL: Data Engineer Agent
**File**: `skills/data_engineer_agent.md`
**Status**: TIER 1

#### Purpose
Design, write, validate, and document all Snowflake SQL pipelines and Python data connectors.

#### Core Capabilities
- Write production-quality Snowflake SQL (CTEs, window functions, incremental loads)
- Build `snowflake-connector-python` ingestion scripts
- Design Snowflake schema (tables, views, stages) for raw material + supplier data
- Implement `great_expectations` data quality checks
- Create Azure ML data pipeline components for feature engineering

#### Output Standards
- All SQL: CTEs over nested subqueries; documented with inline Korean comments
- All pipelines: idempotent (safe to re-run without duplicating data)
- Schema changes: accompanied by migration script

#### Known Pitfalls to Check (from §4)
- §4.2 A-001: Query timeout on large joins → chunk queries
- §4.4 C-003: Hardcoded warehouse name → use env variables
- §4.3 M-002: FX date offset → T+2 settlement

---

### SKILL: EDA Agent
**File**: `skills/eda_agent.md`
**Status**: TIER 2

#### Purpose
Perform rapid, standardized exploratory data analysis on any dataset passed to it.

#### Core Capabilities
- Statistical profiling: distributions, missing values, outliers, skew/kurtosis
- Time series checks: stationarity (ADF/KPSS), seasonality (STL), autocorrelation (ACF/PACF)
- Correlation analysis: Pearson, Spearman, cross-correlation with lag
- Data quality report: schema validation, duplicate detection, date gap detection
- Automated flag: columns unsuitable for modeling (too many NAs, zero variance, future leakage risk)

#### Output
Structured markdown report + `plotly` visualizations saved to `reports/eda/`

---

### SKILL: Forecasting Agent
**File**: `skills/forecasting_agent.md`
**Status**: TIER 1

#### Purpose
Build, evaluate, and maintain time series forecasting models for raw material prices and demand.

#### Model Hierarchy (try in order)
```
1. Baseline       : Seasonal Naive, Last Value
2. Statistical    : ARIMA/SARIMA (statsmodels), ETS (R forecast package)
3. ML             : LightGBM with lag features, rolling statistics
4. Deep Learning  : LSTM / Temporal Fusion Transformer (torch)
5. Ensemble       : Weighted blend of top-2 models by validation RMSE
```

#### Evaluation Protocol
- Split: time-aware walk-forward cross-validation (never random split)
- Metrics: MAPE, RMSE, MAE, directional accuracy
- Benchmark: always compare against seasonal naive baseline
- Report: markdown table with model × metric × train period

#### Known Pitfalls (§4)
- §4.3 M-001: Data leakage via random split
- §4.3 M-003: Outlier spikes distorting ARIMA
- §4.3 M-004: Insufficient data length for seasonal decomposition

---

### SKILL: Risk Analyst Agent
**File**: `skills/risk_analyst_agent.md`
**Status**: TIER 1

#### Purpose
Quantify and score supply chain risks (price, supplier, logistics, geopolitical) and produce actionable risk rankings.

#### Core Capabilities
- Supplier risk scoring (multi-factor index: reliability, concentration, geopolitical exposure, financial stability)
- Price-at-Risk (PaR): VaR-equivalent for commodity price exposure (GARCH via R `rugarch`)
- Scenario analysis: define shock scenarios (currency crisis, port strike, crop failure) → simulate P&L impact
- Concentration risk: identify over-dependence on single suppliers/regions
- Risk-adjusted procurement window: recommend optimal buy timing based on risk-adjusted price forecast

#### Output
- Risk heatmap (supplier × risk dimension)
- Monthly PaR report per raw material category
- Scenario impact table: scenario / probability / P&L impact / recommended action

---

### SKILL: Optimizer Agent
**File**: `skills/optimizer_agent.md`
**Status**: TIER 2

#### Purpose
Solve procurement optimization problems: minimize cost subject to supply security, budget, and inventory constraints.

#### Core Capabilities
- Linear programming: `scipy.optimize.linprog`, `PuLP`
- Mixed-integer programming for binary decisions (buy/not-buy, supplier selection)
- Multi-objective optimization: cost vs. risk trade-off frontier
- Sensitivity analysis: how robust is the solution to forecast error?

#### Input
- Price forecasts (from Forecasting Agent)
- Risk scores (from Risk Analyst Agent)
- Constraints: budget, min/max inventory, supplier limits, lead times

#### Output
- Optimal procurement schedule: quantity × supplier × timing
- Cost savings estimate vs. current baseline
- Sensitivity table: solution stability under ±X% forecast error

---

### SKILL: Reporting Agent
**File**: `skills/reporting_agent.md`
**Status**: TIER 2

#### Purpose
Transform analytical outputs into polished Korean-language reports and stakeholder communications.

#### Core Capabilities
- Executive summary: 1-page (300 words max) business summary of any analysis
- Structured report: methodology → findings → recommendations → next steps
- Data storytelling: select key charts, write interpretations in plain Korean
- Slide outline: convert report to bullet-point slide structure (PowerPoint-ready)
- Anomaly alerts: plain-language Korean alert when a model flags significant risk change

#### Output Formats
- Markdown (default) → saved to `reports/`
- Plain text (for email / messaging)
- Slide outline (markdown with `---` slide breaks)

---

### SKILL: Code Reviewer Agent
**File**: `skills/code_reviewer_agent.md`
**Status**: TIER 3

#### Purpose
Review Python/R/SQL code for correctness, security, style compliance, and performance.

#### Review Checklist
- [ ] PEP 8 / tidyverse style compliance (CLAUDE.md §2.1.1)
- [ ] No hardcoded credentials or secrets
- [ ] No use of forbidden patterns (CLAUDE.md §2.2.3 constraints)
- [ ] Error messages in Korean (CLAUDE.md §2.2.2)
- [ ] Time series splits are time-aware (§4.3 M-001)
- [ ] Model serialization uses joblib/mlflow, not pickle (§2.2.3)
- [ ] No circular imports (§4.4 C-001)
- [ ] Notebook outputs stripped before commit (§4.4 C-002)

#### Output
Inline code comments + a structured review table:
```
| Line | Severity | Issue | Fix |
|------|----------|-------|-----|
| 42   | HIGH     | Hardcoded password | Use os.environ['SNOWFLAKE_PASS'] |
```

---

## LLM ROUTING GUIDE
> Which LLM to use for which task — aligned with current subscriptions.

| Task Type | Recommended LLM | Reason |
|---|---|---|
| Code generation (Python/R/SQL) | **Claude Pro** | Best code quality, follows CLAUDE.md rules |
| Statistical research / methodology | **Perplexity Pro** | Up-to-date citations, academic sources |
| Long-form document drafting | **Claude Pro** | Context retention, structured output |
| Commodity market research | **Perplexity Pro** | Real-time web search |
| Quick calculations / sanity checks | **ChatGPT Team** | Fast, reliable for arithmetic |
| Large file / long context analysis | **Gemini AI Pro** | 2TB context window for large datasets |
| Agent orchestration (this file) | **Claude Pro + Claude Code** | Native CLAUDE.md integration |
