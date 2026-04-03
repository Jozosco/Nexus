# Project Nexus
## 수입원료 공급망 인텔리전스 허브 — Imported Raw Material Supply Chain Intelligence Hub

> **North Star**: Maximize P&L by minimizing procurement risk from soybean oil supply chain volatility.
> **For AI agents**: Load §QR first, then load only the section(s) relevant to your task. Do not re-summarize this file.
> **Mutability notice**: Sections marked `[M]` contain data sources or methods subject to change without notice.

---

## §QR QUICK REFERENCE — Load This First

| Field | Value |
|---|---|
| **Target Commodity** | Soybean Oil (대두유) — crude and refined |
| **Import Origins** | USA · Argentina · Brazil · Vietnam |
| **Contract Basis** | CFR (Cost and Freight) — importer bears risk from origin port |
| **Typical Lead Time** | ~3 months (order → shipment → arrival) |
| **Decision Output** | Daily **Buy / Hold** procurement signal |
| **Signal Basis** | Bear (하락장) / Bull (상승장) regime + price band forecast |
| **Current Scope** | Soybean oil only — do NOT extend to other raw materials without explicit instruction |
| **Human Gate** | AI recommends; procurement team approves. No autonomous execution. |

### Goal Labels (used throughout all project files)
| ID | Goal | Primary Output |
|---|---|---|
| **G1** | Identify and rank price-driving variables | Feature importance rankings + automated risk alerts |
| **G2** | Forecast futures price volatility band in real time | Daily price band with confidence intervals |
| **G3** | Generate scenario-based Bear/Bull/Hold signals | Regime label + P&L impact estimate per scenario |

---

## §1 Problem Statement

An F&B manufacturer importing soybean oil faces three structural procurement failures:

| Failure | Current State | Target State |
|---|---|---|
| **Volatility management** | Reactive — follows lagging news and free indices | Proactive — real-time structural break detection |
| **Decision basis** | Buyer intuition + subjective judgment | Quantitative models + objective data signals |
| **Lead-time risk** | Discovered post-facto | Anticipated 3 months ahead via predictive pipeline |

**Why the US and Argentina dominate**: Together they produce ~80% of global soybeans. Local policy shifts and crop conditions in these two origins directly set CFR import prices. Vietnam is included as a secondary origin for refined oil.

**Current trigger**: US–Iran conflict (Hormuz Strait) causing persistent disruption to global logistics — a real-time test case for this system.

---

## §2 Analytical Goals

> Goal IDs G1/G2/G3 are used as shorthand throughout CLAUDE.md, Skills.md, and all code modules. Always resolve ambiguous references against §QR.

### G1 — Variable Importance & Risk Alerts
Identify which macro/micro factors most influence soybean oil prices and build automated alert triggers when those factors breach thresholds.

### G2 — Price Band Forecasting `[M]`
Forecast a probability-bounded price range for soybean oil futures on a rolling daily basis. Output must include upper/lower bands, not just a point estimate.

### G3 — Bear/Bull/Hold Regime Signal `[M]`
Classify the current market into Bear (하락장) / Bull (상승장) / Neutral regimes and translate into a Buy or Hold procurement recommendation with estimated P&L impact.

---

## §3 Data Requirements `[M]`

> The variable lists below are the current best-estimate pool. Additions and removals are expected as the project progresses. Treat them as a starting set, not a fixed schema.

### 3.1 External Data

| Category | Variables |
|---|---|
| **Global Economy / Trade** | Fed funds rate, global CPI, KRW/USD FX rate, WTI/Brent crude oil price, BDI (Baltic Dry Index), SCFI (Shanghai Containerized Freight Index) |
| **Geopolitical / Policy** | US–China trade tensions, Trump-era tariff schedules, Hormuz Strait / Black Sea conflict intensity indicators |
| **Climate / Agriculture** | ENSO index (El Niño / La Niña phase), USDA WASDE crop yield data, origin-country weather anomalies (US, Argentina, Brazil, Vietnam), EPA Renewable Fuel Standard (RFS) |
| **Domestic Korea** | BOK base rate, domestic CPI, total soybean oil import volumes, substitute oil prices (palm oil, sunflower oil), domestic RFS biodiesel blend mandate (2030 target: 5%), government grain strategic reserve policy |

### 3.2 Internal Data

| Domain | Key Data Points |
|---|---|
| **S&OP** | Soybean oil input per SKU (kg/unit), Master Production Schedule (MPS), forecast vs. actual MAPE, seasonality coefficients, portfolio demand forecast (planned vs. executed) |
| **Procurement** | Order history (qty · contract unit price · order date · ETA), crude vs. refined import ratio and price delta, CFR freight change history, lead-time variance (contracted vs. actual), hedging P&L vs. market spot price at receipt, supplier offer price vs. market benchmark |
| **Supply / Logistics** | Monthly inventory levels (crude / refined), inventory turnover (monthly consumption basis), inbound lead-time actuals (order → shipment → arrival by stage) |

---

## §4 Analytical Methodology `[M]`

> All method selections are preliminary and subject to change. Do NOT treat a listed method as a committed implementation until it appears in the corresponding `src/` module.

### 4.1 Methods by Goal

| Goal | Quantitative Methods | Qualitative Methods |
|---|---|---|
| **G1** | XGBoost + SHAP, Random Forest MDI, LASSO regression, Granger causality test | LDA topic modeling, NLP event detection, GPR index encoding |
| **G2** | VMD-LSTM / GRU, Conformal Quantile Regression (CQR), GARCH volatility, Quantile Regression | FinBERT sentiment scoring, TF-IDF real-time keyword extraction, automated event dummy generation |
| **G3** | SARIMAX, Markov Regime Switching (RS), Temporal Fusion Transformer (TFT), Monte Carlo simulation | Scenario analysis, ENSO phase encoding, Human-in-the-Loop review gate |

### 4.2 Methodology Taxonomy

```
Analysis Framework
├── A. Quantitative                              ← Automate first (pipeline-native)
│   ├── A-1. Statistical time series   ARIMA · SARIMA · SARIMAX · Markov RS
│   ├── A-2. Machine learning          XGBoost · Random Forest · LASSO
│   ├── A-3. Deep learning             LSTM · GRU · TFT
│   └── A-4. Uncertainty quantification CQR · GARCH · Monte Carlo
└── B. Qualitative                               ← Phased automation; manual override retained
    ├── B-1. NLP / text analysis       FinBERT · TF-IDF · LDA
    ├── B-2. Event encoding            Geopolitical dummies · ENSO phase
    └── B-3. Expert judgment layer     Human-in-the-Loop · scenario definition
```

---

## §5 Expected Outcomes

### Quantitative / Financial
| Outcome | Mechanism |
|---|---|
| Raw material cost reduction | Data-driven buy timing replaces intuition-based purchasing |
| KPI achievement | Proactive buy success rate + target cost reduction rate (targets TBD with stakeholders) |
| Safety stock cost reduction | Forecast-linked hybrid inventory model prevents excess stockpiling |
| Cash flow risk reduction | Scenario-based positioning buffers against price extremes |

### Operational
| Outcome | Mechanism |
|---|---|
| Reactive → Proactive paradigm | Structural break detection replaces lagging news-following |
| Decision transparency | Shared quantitative signals align S&OP, Procurement, Finance |
| Lead-time preparedness | 3-month horizon risk anticipation including Hormuz / logistics shock scenarios |

### Integration Targets
- **Dashboard**: Daily Buy/Hold signal + key price drivers → leverage in spot contract negotiations
- **ERP/S&OP linkage**: External shock detection → real-time simulation of impact on MPS and material requirements → enterprise-wide control tower function

---

## §6 Domain Glossary

> All AI agents operating in this project must resolve domain terms against this table before generating output. Do NOT infer meanings from general knowledge when a project-specific definition exists here.

| Term | Definition in This Project |
|---|---|
| **Bear (하락장)** | Market regime where soybean oil price is in sustained decline; triggers **Hold** signal |
| **Bull (상승장)** | Market regime where soybean oil price is in sustained rise; triggers **Buy** signal |
| **Hold** | Procurement posture: delay purchasing and wait for a better price entry point |
| **Buy** | Procurement posture: execute purchase now at current market price |
| **CFR** | Cost and Freight — supplier covers cost + shipping to destination port; importer bears risk from origin port onward |
| **S&OP** | Sales & Operations Planning — cross-functional process aligning production, sales, and supply |
| **MPS** | Master Production Schedule — month-level production plan per SKU |
| **MES** | Manufacturing Execution System — real-time production tracking system |
| **Lead Time** | ~3 months from purchase order to warehouse arrival (order → shipment → customs → arrival) |
| **Safety Stock** | Minimum buffer inventory held to cover demand spikes or supply delays |
| **BDI** | Baltic Dry Index — global bulk shipping cost indicator; proxy for logistics cost |
| **SCFI** | Shanghai Containerized Freight Index — container shipping cost indicator |
| **ENSO** | El Niño–Southern Oscillation — climate pattern; La Niña phase historically reduces South American soy yields |
| **RFS** | Renewable Fuel Standard — US EPA policy mandating biofuel blend ratios; increases soybean oil demand |
| **WASDE** | World Agricultural Supply and Demand Estimates — USDA monthly global crop report |
| **PaR** | Price-at-Risk — VaR equivalent for commodity price exposure |
| **VMD** | Variational Mode Decomposition — signal decomposition method for non-stationary price series |
| **CQR** | Conformal Quantile Regression — distribution-free prediction interval method |
| **TFT** | Temporal Fusion Transformer — attention-based multi-horizon time series model |
| **FinBERT** | BERT variant fine-tuned on financial text; used for news/report sentiment scoring |
| **Structural Break** | Sudden, permanent shift in a time series' statistical properties (e.g., post-sanction price regime change) |

---

## §7 Scope Boundaries

| In Scope | Out of Scope |
|---|---|
| Soybean oil (대두유) — crude and refined | Other raw materials (future project extension) |
| Import origins: US, Argentina, Brazil, Vietnam | Domestic Korean sourcing |
| CFR contract-based procurement decisions | Futures/derivatives trading execution |
| AI-generated Buy/Hold recommendations | Autonomous procurement decisions (human approval required) |
| Cloud-native pipeline (Snowflake + Azure ML) | On-premise or firewall-internal system modification |

---

## §8 Documentation Architecture

> This repository uses a **layered documentation hierarchy** so that AI agents load only the context relevant to their current task — preventing context rot and minimising token cost.

### 8.1 File Responsibilities

| File | Location | Loaded By | Purpose |
|---|---|---|---|
| [`README.md`](./README.md) | Root | Humans + agents (discovery) | Project mission, data inventory, goals, glossary, scope. The entry point. |
| [`CLAUDE.md`](./CLAUDE.md) | Root | Claude Code (every session) | Persistent agent operating rules: session protocol, hard constraints, code style, WISC/HITL. **≤ 120 lines.** |
| [`AGENTS.md`](./AGENTS.md) | Root | All coding assistants | Tool-agnostic instructions valid for any AI assistant (Copilot, Gemini, etc.). |
| [`Skills.md`](./Skills.md) | Root | On-demand (`/skill-name`) | Sub-agent definitions: PM, Data Engineer, Forecasting, Risk Analyst, Optimizer, Reporting, Code Reviewer. |
| [`llms.txt`](./llms.txt) | Root | External LLM ingestion | Structured URL manifest for semantic discovery by external agents. |

### 8.2 Path-Scoped Rules

Detailed, module-specific rules live in `.claude/rules/` and are loaded **only when the agent is working in the corresponding directory**. This keeps `CLAUDE.md` concise while ensuring full context is available when needed.

| Rule File | Loaded When Working In | Contents |
|---|---|---|
| `.claude/rules/modeling.md` | `src/forecasting/`, `notebooks/` | G1/G2/G3 method details, model validation protocol, baseline comparison rules |
| `.claude/rules/libraries.md` | Any `src/` or `notebooks/` | Full approved library list with version pins (Python + R) |
| `.claude/rules/data_pipeline.md` | `src/pipeline/` | Snowflake SQL patterns, API retry logic, schema conventions |
| `.claude/rules/testing.md` | Any test file | pytest, great_expectations, time-aware split rules |

### 8.3 Memory Files

| File | Purpose |
|---|---|
| [`MEMORY.md`](./MEMORY.md) | Agent auto-memory: append learnings and resolved blockers after each session |
| Git log | Long-term decision history — run `git log --oneline -20` to reconstruct prior context |
