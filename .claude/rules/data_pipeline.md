# .claude/rules/data_pipeline.md
> Load this file when working in `src/pipeline/` or designing any data ingestion component.
> These rules govern all data access patterns for the Nexus project.

---

## Snowflake — SQL Conventions

```sql
-- ✅ Correct: CTE-based, uppercase keywords, snake_case identifiers, LIMIT on exploratory
WITH monthly_prices AS (
    SELECT
        price_date,
        origin_country,
        cif_price_usd_per_mt,
        ROW_NUMBER() OVER (PARTITION BY origin_country ORDER BY price_date DESC) AS rn
    FROM soybean_oil.raw.import_prices
    WHERE price_date >= DATEADD('year', -10, CURRENT_DATE)
)
SELECT * FROM monthly_prices WHERE rn = 1 LIMIT 100;

-- ❌ Wrong: nested subqueries, no LIMIT, lowercase keywords
select * from (select * from soybean_oil.raw.import_prices order by price_date desc);
```

**Rules:**
- Always include `LIMIT` in exploratory queries
- CTEs over nested subqueries
- Use `SNOWFLAKE_WAREHOUSE` env variable — never hardcode warehouse name (see MEMORY C-003)
- For joins > 10M rows: set `statement_timeout_in_seconds = 300` + break into chunked queries (see MEMORY A-001)
- Credentials: `os.environ['SNOWFLAKE_ACCOUNT']`, `os.environ['SNOWFLAKE_USER']`, `os.environ['SNOWFLAKE_PASSWORD']`

## Python Snowflake Connector Pattern

```python
import snowflake.connector
import os
from typing import Optional
import pandas as pd

def get_snowflake_connection() -> snowflake.connector.SnowflakeConnection:
    return snowflake.connector.connect(
        account=os.environ['SNOWFLAKE_ACCOUNT'],
        user=os.environ['SNOWFLAKE_USER'],
        password=os.environ['SNOWFLAKE_PASSWORD'],
        warehouse=os.environ['SNOWFLAKE_WAREHOUSE'],   # never hardcode
        database=os.environ['SNOWFLAKE_DATABASE'],
        schema=os.environ['SNOWFLAKE_SCHEMA'],
        session_parameters={'STATEMENT_TIMEOUT_IN_SECONDS': 300}
    )

def query_to_dataframe(sql: str, conn: Optional[snowflake.connector.SnowflakeConnection] = None) -> pd.DataFrame:
    _conn = conn or get_snowflake_connection()
    try:
        cursor = _conn.cursor()
        cursor.execute(sql)
        return cursor.fetch_pandas_all()
    except Exception as e:
        raise RuntimeError(f"[오류] Snowflake 쿼리 실패: {e}") from e
```

## External API — Retry Pattern

All external API calls (commodity price feeds, WASDE, BDI, ENSO, etc.) must implement exponential backoff.

```python
import time
import httpx
from typing import Any

def fetch_with_retry(url: str, max_retries: int = 4, **kwargs: Any) -> httpx.Response:
    """외부 API 호출 — 지수 백오프 재시도 포함."""
    delay = 2
    for attempt in range(max_retries):
        try:
            response = httpx.get(url, timeout=30, **kwargs)
            response.raise_for_status()
            return response
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"[오류] API 호출 실패 ({url}): {e}") from e
            time.sleep(delay)
            delay *= 2   # 2s → 4s → 8s → 16s
```

## Data Directory Rules

```
data/
├── raw/          # NEVER committed (in .gitignore). Contains PII or proprietary source data.
├── processed/    # Committed if schema-documented. Store as Parquet, not CSV.
└── schemas/      # YAML schema definitions for each processed dataset (column name, dtype, nullable, description)
```

- All `processed/` files must have a corresponding `schemas/` YAML entry before being committed
- Notebook outputs (charts, DataFrames) must be stored in Azure Blob Storage, not in the repo (see MEMORY C-002)

## Environment Variables — `.env.template`

```bash
# Copy to .env locally — NEVER commit .env
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_WAREHOUSE=
SNOWFLAKE_DATABASE=
SNOWFLAKE_SCHEMA=
AZURE_ML_WORKSPACE=
AZURE_ML_SUBSCRIPTION_ID=
AZURE_ML_RESOURCE_GROUP=
```
