# Project Nexus
## 수입원료 공급망 인텔리전스 허브 — Imported Raw Material Supply Chain Intelligence Hub

> **North Star**: Maximize P&L by minimizing procurement risk from global supply chain volatility in imported raw materials.

> **Note**: All data sources and analytical methodologies listed in this document are subject to change as the project evolves.

---

## 1. Problem Statement

An F&B manufacturer importing **Soybean Oil (대두유)** from the US, South America (Brazil, Argentina), and Vietnam faces three structural procurement challenges:

| Challenge | Current State | Target State |
|---|---|---|
| **Volatility management** | Reactive — follows lagging news/free indices | Proactive — real-time structural break detection |
| **Decision basis** | Buyer intuition + subjective judgment | Quantitative models + objective data signals |
| **Lead-time risk** | Discovered post-facto | Anticipated 3-month ahead via predictive pipeline |

**Why these countries**: The US and Argentina alone account for ~80% of global soybean production. Local policy and crop conditions in these origins directly determine CFR import prices.

---

## 2. Three Analytical Goals

| # | Goal | Output |
|---|---|---|
| **G1** | Identify and rank key price-driving variables (internal + external) | Feature importance rankings; risk alert triggers |
| **G2** | Forecast real-time futures price volatility band | Daily price band prediction with confidence intervals |
| **G3** | Generate scenario-based procurement signals | Bear / Bull / Hold positioning with P&L impact estimate |

---

## 3. Data Requirements

> Data inputs are classified into **external market data** (API-sourced) and **internal operational data** (Snowflake-synced from ERP/MES/S&OP systems).

### 3.1 External Data

| Category | Variables |
|---|---|
| **Global Economy / Trade** | Fed funds rate, global CPI, KRW/USD FX rate, WTI/Brent crude, BDI/SCFI shipping indices |
| **Geopolitical / Policy** | US-China trade tensions, Trump tariff policy, Middle East (Hormuz Strait) & Black Sea conflict indicators |
| **Climate / Agri (US, South America, Vietnam)** | ENSO index (El Niño/La Niña), crop yield & weather data (USDA WASDE), EPA Renewable Fuel Standard (RFS) |
| **Domestic Korea** | BOK base rate, domestic CPI, total soybean oil import volumes, substitute oil prices (palm, sunflower), domestic RFS biodiesel mandate (target: 5% blend by 2030), government grain stockpile policy |

### 3.2 Internal Data

| Domain | Key Data Points |
|---|---|
| **S&OP** | Soybean oil input per SKU (kg/unit), Master Production Schedule (MPS), forecast vs. actual deviation (MAPE), seasonality coefficients, portfolio-level demand forecast |
| **Procurement** | Order history (qty, contract price, order date, ETA), crude vs. refined oil ratio & price delta, CFR contract freight history, lead-time variance (contracted vs. actual arrival), hedging P&L vs. spot price at receipt, supplier offer price benchmarks |
| **Supply / Logistics** | Monthly inventory levels (crude / refined), inventory turnover rate (monthly consumption basis), inbound lead-time actuals (order → shipment → arrival) |

---

## 4. Analytical Methodology

> Methodology is mapped to each goal. Selection criteria: data type (quantitative / qualitative) × automation feasibility × business interpretability.

### 4.1 By Goal

| Goal | Primary Methods |
|---|---|
| **G1** — Variable importance | XGBoost + SHAP, Random Forest MDI, LASSO regression, Granger causality test, LDA topic modeling, NLP event detection |
| **G2** — Price band forecasting | VMD-LSTM / GRU, Conformal Quantile Regression (CQR), GARCH volatility modeling, FinBERT sentiment scoring, TF-IDF real-time keyword extraction |
| **G3** — Bear/Bull/Hold signals | SARIMAX, Markov Regime Switching (RS), Temporal Fusion Transformer (TFT), Monte Carlo scenario simulation, ENSO phase encoding, Human-in-the-Loop review |

### 4.2 Methodology Taxonomy

```
Analysis Framework
├── A. Quantitative
│   ├── A-1. Statistical time series   (ARIMA, SARIMA, SARIMAX, Markov RS)
│   ├── A-2. Machine learning          (XGBoost, Random Forest, LASSO)
│   ├── A-3. Deep learning             (LSTM, GRU, TFT)
│   └── A-4. Uncertainty quantification (CQR, GARCH, Monte Carlo)
└── B. Qualitative
    ├── B-1. NLP / text analysis       (FinBERT, TF-IDF, LDA)
    ├── B-2. Event encoding            (geopolitical dummies, ENSO phase)
    └── B-3. Expert judgment layer     (Human-in-the-Loop, scenario definition)
```

> Automation priority: Quantitative pipeline (A) → automated first. Qualitative layer (B) → phased automation with manual override.

---

## 5. Expected Outcomes

### Quantitative
- Structural cost reduction via data-driven procurement timing (vs. intuition-based purchasing)
- KPI targets: proactive buy success rate, target cost reduction rate (to be finalized with stakeholders)
- Safety stock optimization → reduce excess inventory holding costs (logistics + silo)
- Capital risk reduction via scenario-based cash flow protection

### Qualitative
- **Paradigm shift**: from lagging news-reactive to real-time structural-break-aware procurement
- **Decision transparency**: cross-department alignment (S&OP, Procurement, Finance) based on shared quantitative signals
- **Lead-time preparedness**: 3-month horizon risk anticipation, including Hormuz Strait / global logistics bottleneck scenarios

### Operational Integration
- **Dashboard**: Daily Buy/Hold signal + key price drivers → leverage in spot contract negotiations
- **ERP/S&OP linkage**: External shock detection → real-time simulation of impact on monthly production plan and material requirements → enterprise-wide control tower

---

## 6. Tech Stack & Agent Framework

| Layer | Tool |
|---|---|
| Cloud Data Warehouse | Snowflake |
| ML Platform | Azure ML Studio |
| Languages | Python (primary), R (statistical), SQL (data access) |
| Version Control | GitHub via Claude Code Web (Research Preview) |
| LLMs | Claude Pro · ChatGPT Team · Gemini AI Pro · Perplexity Pro |

> Full coding standards, library constraints, and firewall rules: see [`CLAUDE.md`](./CLAUDE.md)
> Agent roles and sub-agent definitions: see [`Skills.md`](./Skills.md)

---

## 7. Delivery Phases

```
Phase 1 — Foundation     : Data pipeline (Snowflake ← external APIs + internal ERP), EDA, baseline models
Phase 2 — Modeling       : G1 variable ranking, G2 price band forecasting, G3 regime detection
Phase 3 — Optimization   : Procurement optimizer, P&L impact simulation, safety stock model
Phase 4 — Productionize  : Scheduled pipelines, Buy/Hold dashboard, automated alerts
Phase 5 — Governance     : Model monitoring, drift detection, documentation, KPI reporting
```

---

## 8. Scope Boundaries

| In Scope | Out of Scope |
|---|---|
| Soybean oil (대두유) — crude and refined | Other raw materials (future extension) |
| Import origins: US, Argentina, Brazil, Vietnam | Domestic sourcing |
| CFR contract-based procurement | Futures/derivatives trading execution |
| AI-generated Buy/Hold recommendations | Autonomous procurement decisions (human approval required) |
