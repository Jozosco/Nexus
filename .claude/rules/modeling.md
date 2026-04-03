# .claude/rules/modeling.md
> Load this file when working in `src/forecasting/`, `src/risk/`, or any modeling notebook.
> All method selections marked `[M]` are subject to change. Do not treat them as committed architecture.
> Always reference README.md §QR for goal IDs (G1/G2/G3) before reading this file.

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

### Method Stack `[M]`
| Step | Method | Library | Notes |
|---|---|---|---|
| Pre-processing | VMD decomposition | `vmdpy` | Separate trend/cyclical/noise components |
| Volatility modeling | GARCH / EGARCH | `arch` (Python), `rugarch` (R) | σ² = α₀ + Σαᵢεᵢ² + Σβⱼσⱼ² |
| Sequence modeling | LSTM or GRU | `torch` | Captures long-range dependencies |
| Multi-horizon forecast | TFT | `pytorch-forecasting` | Integrates static + time-varying covariates |
| Prediction interval | CQR | `mapie` | Distribution-free confidence bounds |
| Sentiment layer | FinBERT | `transformers` | Score news sentiment → exogenous input |

### Validation Protocol
1. Walk-forward cross-validation (never random split — see MEMORY M-001)
2. Metrics: MAPE, RMSE, MAE, directional accuracy (% correct Bear/Bull direction)
3. **Baseline required**: compare every model against seasonal naive (last-year same-week)
4. Report as markdown table: `model × metric × validation window`
5. Minimum data requirement: 24 months (see MEMORY M-004); fall back to ETS if insufficient

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
