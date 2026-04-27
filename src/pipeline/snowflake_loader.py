"""
Snowflake Raw 테이블 업로더 — Phase B (WBS 1.2.1)
data/raw/*.parquet → SOYBEAN_OIL.RAW.* (MERGE INTO, 멱등성 보장)
실행 환경: GitHub Actions (snowflake-upload job) 또는 VS Code Web (Azure ML)
"""

from __future__ import annotations

import glob
import os
from pathlib import Path

import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

# 테이블 매핑: 파일 패턴 → (테이블명, 자연 키 컬럼 목록)
TABLE_MAP: dict[str, tuple[str, list[str]]] = {
    "economic_indicators": ("ECONOMIC_INDICATORS", ["PRICE_DATE", "SOURCE_NAME", "INDICATOR_CODE"]),
    "shipping_indices":    ("SHIPPING_INDICES",    ["PRICE_DATE", "INDICATOR_CODE"]),
    "crop_data":           ("CROP_DATA",           ["PRICE_DATE", "SOURCE_NAME", "INDICATOR_CODE", "COUNTRY"]),
    "climate_data":        ("CLIMATE_DATA",        ["PRICE_DATE", "SOURCE_NAME", "INDICATOR_CODE", "SEASON"]),
    "geopolitical_indices":("GEOPOLITICAL_INDICES",["PRICE_DATE", "SOURCE_NAME", "INDICATOR_CODE"]),
}
RAW_DIR = "data/raw"
SCHEMA   = "RAW"


def get_connection() -> snowflake.connector.SnowflakeConnection:
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=SCHEMA,
        session_parameters={"STATEMENT_TIMEOUT_IN_SECONDS": 300},
    )


def _normalize_df(df: pd.DataFrame, table_key: str) -> pd.DataFrame:
    """컬럼명 대문자 정규화 + 자연 키 NULL 대체 (MERGE 키는 NULL 불가)."""
    df = df.copy()
    df.columns = [c.upper() for c in df.columns]
    # CROP_DATA: COUNTRY null → ''
    if "COUNTRY" in df.columns:
        df["COUNTRY"] = df["COUNTRY"].fillna("")
    # CLIMATE_DATA: SEASON null → ''
    if "SEASON" in df.columns:
        df["SEASON"] = df["SEASON"].fillna("")
    # PRICE_DATE → date (not datetime) for Snowflake DATE type
    if "PRICE_DATE" in df.columns:
        df["PRICE_DATE"] = pd.to_datetime(df["PRICE_DATE"]).dt.date
    return df


def _merge_into(conn: snowflake.connector.SnowflakeConnection,
                df: pd.DataFrame, table: str, key_cols: list[str]) -> int:
    """임시 스테이징 테이블 경유 MERGE INTO (업서트, 멱등성 보장)."""
    stage_table = f"STAGE_{table}_{os.getpid()}"
    cur = conn.cursor()
    try:
        # 1. 스테이징 테이블 생성
        cur.execute(f"CREATE TEMP TABLE {stage_table} LIKE {SCHEMA}.{table}")
        write_pandas(conn, df, stage_table, schema=SCHEMA, auto_create_table=False)

        # 2. MERGE INTO
        join_cond  = " AND ".join(f"t.{c} = s.{c}" for c in key_cols)
        all_cols   = [c for c in df.columns if c not in ("_LOADED_AT",)]
        update_set = ", ".join(f"t.{c} = s.{c}" for c in all_cols if c not in key_cols)
        insert_cols = ", ".join(all_cols)
        insert_vals = ", ".join(f"s.{c}" for c in all_cols)

        cur.execute(f"""
            MERGE INTO {SCHEMA}.{table} t
            USING {stage_table} s ON ({join_cond})
            WHEN MATCHED THEN UPDATE SET {update_set}
            WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})
        """)
        return cur.rowcount
    finally:
        cur.execute(f"DROP TABLE IF EXISTS {stage_table}")
        cur.close()


def load_all(raw_dir: str = RAW_DIR) -> None:
    """data/raw/ 디렉토리의 모든 parquet 파일을 Snowflake에 업로드."""
    conn = get_connection()
    total_rows = 0

    for pattern_key, (table, key_cols) in TABLE_MAP.items():
        files = sorted(glob.glob(f"{raw_dir}/{pattern_key}_*.parquet"))
        if not files:
            print(f"[경고] {pattern_key}: parquet 파일 없음 — 건너뜀")
            continue

        latest = files[-1]  # 날짜 정렬 → 최신 파일 사용
        df = pd.read_parquet(latest)
        df = _normalize_df(df, pattern_key)
        rows = _merge_into(conn, df, table, key_cols)
        total_rows += rows
        print(f"[완료] {Path(latest).name} → {SCHEMA}.{table}: {rows}행 업서트")

    conn.close()
    print(f"[완료] Snowflake 업로드 완료 — 총 {total_rows}행")


if __name__ == "__main__":
    load_all()
