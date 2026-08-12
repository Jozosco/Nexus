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
# ⚠️ vmdpy — 2026-08-12 기본 구성에서 제외. 전체 시계열 일괄 분해는 미래 정보 누수를 일으킴.
#    사용 시 각 fold 학습 창 내 one-sided/rolling 재적합 필수 (modeling.md G2 참조).

# Uncertainty Quantification
mapie >= 0.8            # G2: EnCQR(Ensemble Conformalized QR) 구간 보정 — 2026-08-12 용도 갱신

# Feature Mart / as-of Join (2026-08-12 신규)
duckdb >= 1.0           # ASOF JOIN 기반 시점 정합 feature view — 서버 불필요, parquet 직접 질의

# Challenger 딥러닝 (해당 실험 단계에서만 설치)
darts >= 0.30           # N-BEATSx · N-HiTS · TFT 통합 인터페이스
neuralforecast >= 1.7   # Nixtla 계열 (PatchTST 포함)

# 외부 저장소 클라이언트 (조정자 계정 발급 후 사용)
supabase >= 2.0         # 사건·근거 관계형 적재 (SUPABASE_URL / SUPABASE_SERVICE_KEY)
neo4j >= 5.0            # 지식그래프 투영 — validated 엣지만 (도입 시점: 조사 §5 게이트 이후)

# Optimization (G3 procurement optimizer)
pulp >= 2.7             # linear/mixed-integer programming
scipy >= 1.12           # scipy.optimize as fallback

# Multi-LLM Integration (src/utils/)
openai >= 1.30              # OpenAI API + Perplexity (OpenAI-compatible endpoint)
google-genai >= 2.0         # Gemini API (⚠ google-generativeai 지원 종료 — MEMORY L-010 참조)

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
