# .claude/rules/testing.md
> Load this file when writing or reviewing any test file.
> Minimum coverage threshold: 80% for any new `src/` module before it is merged to main.

---

## Python — pytest

```python
# tests/test_price_band.py
import pytest
import pandas as pd
import numpy as np
from src.forecasting.price_band_g2 import compute_price_band

class TestPriceBandG2:
    """G2 가격 밴드 예측 모듈 단위 테스트."""

    def test_output_has_upper_lower_bands(self, sample_price_df: pd.DataFrame) -> None:
        result = compute_price_band(sample_price_df)
        assert 'upper_band' in result.columns
        assert 'lower_band' in result.columns
        assert (result['upper_band'] >= result['lower_band']).all()

    def test_no_future_data_leakage(self, sample_price_df: pd.DataFrame) -> None:
        """훈련 데이터에 미래 데이터가 포함되지 않았는지 검증."""
        train_max_date = sample_price_df['price_date'].max()
        result = compute_price_band(sample_price_df)
        assert result.index.max() > train_max_date, "예측값이 훈련 기간 내에 있음 — 데이터 누출 가능성"
```

**Rules:**
- Use `pytest` fixtures for all test data (no raw hardcoded DataFrames in test body)
- Every time series model test must include a data-leakage assertion (see MEMORY M-001)
- Test file naming: `test_<module_name>.py` in `tests/` mirroring `src/` structure

## Data Validation — great_expectations

```python
import great_expectations as gx

def validate_soybean_price_schema(df: pd.DataFrame) -> None:
    """원자재 가격 데이터 스키마 검증."""
    context = gx.get_context()
    validator = context.sources.pandas_default.read_dataframe(df)

    validator.expect_column_to_exist("price_date")
    validator.expect_column_to_exist("cif_price_usd_per_mt")
    validator.expect_column_values_to_not_be_null("price_date")
    validator.expect_column_values_to_be_between("cif_price_usd_per_mt", min_value=0, max_value=5000)
    validator.expect_column_values_to_be_of_type("price_date", "datetime64[ns]")

    results = validator.validate()
    if not results["success"]:
        raise ValueError(f"[오류] 데이터 검증 실패: {results['statistics']}")
```

## R — testthat

```r
# tests/testthat/test-garch-volatility.R
library(testthat)
library(rugarch)

test_that("GARCH 모델이 유효한 변동성 예측값을 반환한다", {
  result <- fit_garch_volatility(soybean_price_series)
  expect_true(all(result$sigma > 0))
  expect_equal(length(result$sigma), nrow(soybean_price_series))
})
```

## Time-Series Split Protocol (Mandatory)

```python
from sklearn.model_selection import TimeSeriesSplit

# ✅ Correct: time-aware walk-forward split
tscv = TimeSeriesSplit(n_splits=5, gap=30)   # gap=30 days prevents look-ahead bias
for train_idx, test_idx in tscv.split(X):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]

# ❌ Wrong: random split destroys temporal structure
from sklearn.model_selection import train_test_split
X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)  # NEVER for time series
```

## Model Baseline Requirement

Every model submission must include a comparison against a naive baseline:

| Metric | Your Model | Seasonal Naive | Last-Value Naive |
|---|---|---|---|
| MAPE | X% | Y% | Z% |
| RMSE | X | Y | Z |
| Directional Accuracy | X% | Y% | Z% |

If your model does not outperform both baselines on MAPE **and** directional accuracy, document the reason before merging.
