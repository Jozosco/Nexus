# .claude/rules/libraries.md
> Load this file when working in any `src/` module or `notebooks/`.
> These are the **only** approved libraries. Do not introduce new dependencies without updating this file.
> All version constraints are minimum versions unless a specific pin is noted.

---

## Python — Approved Libraries

```
# Data & Numerics
pandas >= 2.0           # tabular data (⚠ incompatible with snowflake-connector < 3.5 — see MEMORY L-002)
numpy >= 1.26           # numerical operations

# Machine Learning
scikit-learn >= 1.4     # classical ML, preprocessing, TimeSeriesSplit
xgboost >= 2.0          # G1: XGBoost variable importance
shap >= 0.44            # G1: SHAP explainability (required alongside xgboost)
lightgbm >= 4.0         # gradient boosting alternative

# Statistical / Econometric Time Series
statsmodels >= 0.14     # ARIMA, SARIMA, SARIMAX, VAR, Granger causality
arch >= 6.0             # G2: GARCH / EGARCH volatility modeling (Python-native)
prophet >= 1.1          # seasonal time series (⚠ pin pystan==3.9.0 — see MEMORY L-001)

# Deep Learning
torch >= 2.0            # LSTM, TFT (⚠ specify CUDA version — see MEMORY L-003)
pytorch-forecasting >= 1.0  # G2/G3: Temporal Fusion Transformer (TFT)

# NLP / Sentiment (G2 qualitative layer)
transformers >= 4.38    # G2: FinBERT sentiment scoring
sentence-transformers >= 2.5  # embedding-based document similarity

# Signal Processing
vmdpy >= 0.1            # G2: Variational Mode Decomposition (VMD) pre-processing

# Uncertainty Quantification
mapie >= 0.8            # G2: Conformal Quantile Regression (CQR) / prediction intervals

# Optimization (G3 procurement optimizer)
pulp >= 2.7             # linear/mixed-integer programming
scipy >= 1.12           # scipy.optimize as fallback

# Multi-LLM Integration (src/utils/)
openai >= 1.30              # OpenAI API + Perplexity (OpenAI-compatible endpoint)
google-generativeai >= 0.7  # Gemini API (⚠ not the same as google-cloud-aiplatform)

# Cloud Connectors
snowflake-connector-python >= 3.5   # Snowflake access
azureml-sdk >= 1.56                 # Azure ML pipeline integration
mlflow >= 2.10                      # model tracking and registration (use over pickle)

# Data Validation
great-expectations >= 0.18  # schema and quality checks on pipeline inputs

# Visualization
plotly >= 5.0           # interactive charts (export as HTML or PNG)
```

## R — Approved Libraries

```r
tidyverse            # data wrangling + ggplot2 visualization
forecast             # ARIMA, ETS, TBATS
tseries              # ADF/KPSS unit root tests, GARCH
vars                 # Vector Autoregression (VAR)
rugarch              # GARCH family models (primary for G2 volatility)
DBI + odbc           # Snowflake JDBC connection
pointblank           # data quality checks (R equivalent of great_expectations)
```

## Hard Constraints — Forbidden Patterns

| Pattern | Reason | Use Instead |
|---|---|---|
| `pickle` | Insecure, version-fragile | `joblib.dump()` or `mlflow.log_model()` |
| `openpyxl` / Excel I/O | Bypasses Snowflake as source of truth | Snowflake query via `snowflake-connector-python` |
| `os.system()` / `subprocess` for data | Security policy violation | SDK connectors only |
| `random_state` shuffle on time series | Causes data leakage (see MEMORY M-001) | `sklearn.model_selection.TimeSeriesSplit` |
