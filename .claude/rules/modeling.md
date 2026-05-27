# .claude/rules/modeling.md
> Load this file when working in `src/forecasting/`, `src/risk/`, or any modeling notebook.
> All method selections marked `[M]` are subject to change. Do not treat them as committed architecture.
> Always reference README.md §QR for goal IDs (G1/G2/G3) before reading this file.

---

## Phase A Data Constraint (Applies to G1 and G2)
> **MEMORY D-006**: Internal S&OP data (daily inventory, shipment volume, unit cost)
> unavailable in Phase A — only monthly aggregates exist. All G1/G2 modeling uses
> **external pipeline data exclusively**. Internal monthly data enters as Phase B validation only.

---

## G1 — Variable Importance & Risk Alert System

**Objective**: Identify which macro/micro factors most drive soybean oil price movements.

### Method Stack `[M]`
| Step | Method | Library | Output |
|---|---|---|---|
| Feature selection | LASSO regression | `statsmodels` | Reduced variable set |
| Importance ranking | XGBoost + SHAP | `xgboost`, `shap` | SHAP bar chart + importance table |
| Importance ranking (alt) | Random Forest MDI | `scikit-learn` | Mean Decrease in Impurity |
| Causal validation | Granger causality test | `statsmodels` | Lead-lag relationships with p-values |
| Qualitative signals | LDA topic modeling | `sklearn.decomposition` | Topic clusters from news corpus |
| Event detection | NLP keyword trigger | `transformers` (FinBERT) | Binary event flag per article |

### Alert Trigger Logic
- Define threshold per variable (e.g., BDI > 2σ from 90-day rolling mean → alert)
- Alert output: Korean-language message + variable name + current vs. threshold value
- Alerts must be explainable: include top-3 SHAP contributors for each triggered alert

---

## G2 — Price Band Forecasting (Futures Price Volatility)

**Objective**: Produce a probability-bounded daily price range for soybean oil futures.
**Output contract**: Upper band · Point estimate · Lower band · Confidence level (%)

> **Phase A Data Constraint (MEMORY D-006)**: Internal S&OP data (daily inventory, shipment volume)
> unavailable — monthly aggregates only. G2 is built **exclusively on external pipeline data**.
> Internal monthly stock/unit-price data may be used as a post-hoc validation signal in Phase B only.

> **Compute Environment**: G2 is developed and trained in **Azure ML Studio**.
> All training jobs must use Azure ML `ScriptRunConfig` or `Command` job objects.
> Experiment tracking via `mlflow` (Azure ML autolog). Never run training locally or in GitHub Actions.

### Data Sources (External Only — Phase A)
| Category | Source | Connector | Indicator |
|---|---|---|---|
| CBOT Futures | yfinance BO=F | `commodity_connector.py` | `CBOT_SBO_FUTURES` |
| Geopolitical | Caldara GPR + Perplexity | `gpr_connector.py` | `GPR`, `HORMUZ_THREAT_LEVEL` |
| AIS Strait Risk | AISstream.io | `ais_connector.py` | `SBO_STRAIT_RISK_COMPOSITE` |
| GeoIntel | USGS/NOAA/GDELT/FIRMS | `geointel_connector.py` | `GEOINTEL_RISK_COMPOSITE` |
| Shipping | TE BDI REST / stooq | `shipping_connector.py` | `BDI` |
| FX | FRED DEXBZUS/DEXCHUS | `economic_connector.py` | `FX_BRL_USD`, `FX_CNY_USD` |
| ENSO/Climate | NOAA CPC ONI | `climate_connector.py` | `ENSO_ONI` |
| Crop Supply | USDA FAS PSD | `wasde_connector.py` | `WASDE_SBO_PRODUCTION` |

### Method Stack `[M]`
| Step | Method | Library | Notes |
|---|---|---|---|
| Pre-processing | VMD decomposition | `vmdpy` | Separate trend/cyclical/noise components |
| Volatility modeling | GARCH / EGARCH | `arch` (Python), `rugarch` (R) | σ² = α₀ + Σαᵢεᵢ² + Σβⱼσⱼ² |
| Sequence modeling | LSTM or GRU | `torch` | Captures long-range dependencies |
| Multi-horizon forecast | TFT | `pytorch-forecasting` | Integrates static + time-varying covariates |
| Prediction interval | CQR | `mapie` | Distribution-free confidence bounds |
| Sentiment layer | FinBERT | `transformers` | Score news sentiment → exogenous input |

### Azure ML Studio Workflow
```
1. data/raw/*.parquet → Azure Blob Storage (pipeline upload step)
2. Azure ML Data Asset → registered dataset (versioned)
3. ScriptRunConfig → src/forecasting/price_band_g2.py (training script)
4. mlflow.autolog() → experiment tracking (no manual log calls needed)
5. mlflow.log_model() → Azure ML Model Registry (never pickle)
6. Registered model → batch inference pipeline (daily score job)
```

### Validation Protocol
1. Walk-forward cross-validation (never random split — see MEMORY M-001)
2. Metrics: MAPE, RMSE, MAE, directional accuracy (% correct Bear/Bull direction)
3. **Baseline required**: compare every model against seasonal naive (last-year same-week)
4. Report as markdown table: `model × metric × validation window`
5. Minimum data requirement: 24 months (see MEMORY M-004); fall back to ETS if insufficient
6. G2 gate: must have C-08 DQSOps PASS on all 8 external data sources before first training run

---

## G3 — Bear/Bull/Hold Regime Signal

**Objective**: Classify current market regime and translate into Buy / Hold procurement recommendation.
**Output contract**: Regime label (Bear/Bull/Neutral) · Confidence · P&L impact estimate · Recommended action

### Method Stack `[M]`
| Step | Method | Library | Notes |
|---|---|---|---|
| Regime detection | Markov Regime Switching | `statsmodels` | 2–3 state hidden Markov model |
| Seasonal exogenous | SARIMAX | `statsmodels` | Integrates macro covariates (FX, BDI, ENSO) |
| Multi-horizon regime | TFT | `pytorch-forecasting` | 3-month forward regime probability |
| P&L simulation | Monte Carlo (10,000 runs) | `numpy`, `scipy` | Distribution of outcomes per Buy/Hold |
| Scenario encoding | ENSO phase dummy + geopolitical index | Manual + `transformers` | Encodes climate + geopolitical shock inputs |

### Human-in-the-Loop Gate (Mandatory)
- G3 output always passes through CLAUDE.md §6 HITL protocol before being surfaced as a recommendation
- Never output a Buy/Hold signal without the P&L impact estimate and confidence range
- If Monte Carlo variance > 20%, flag output as HIGH UNCERTAINTY and escalate to human review

---

## Cross-Goal Rules

### Time Series Non-Negotiables
- **Never** shuffle or randomly split time series data. Use `TimeSeriesSplit` (sklearn).
- Always apply outlier capping (IQR method) before fitting ARIMA/GARCH (see MEMORY M-003).
- FX rate: use T+2 settlement convention. Document date offset in all pipeline schemas (see MEMORY M-002).
- Log-transform soybean oil prices before fitting unless the model explicitly handles non-stationarity.

### Model Serialization
- Save all trained models with `mlflow.log_model()` or `joblib.dump()`. Never use `pickle`.
- Register model version in Azure ML Model Registry after each production-quality fit.

### Interpretability Requirement
- All G1/G2/G3 outputs must include a human-readable explanation alongside the numerical result.
- G1: SHAP plot + top-5 variable narrative.
- G2: "Price expected between X–Y because of [top 2 drivers]" in Korean.
- G3: Regime label + one-sentence Korean rationale + P&L range.
