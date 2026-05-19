"""pytest 공유 픽스처 — 파이프라인 품질 테스트용."""
from __future__ import annotations

import glob
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
STALE_BDAYS = 5


def _load_latest_parquet(prefix: str) -> pd.DataFrame | None:
    """prefix 로 시작하는 가장 최신 parquet 파일을 로드."""
    files = sorted(glob.glob(str(DATA_DIR / f"{prefix}_*.parquet"))
                   + glob.glob(str(DATA_DIR / "**" / f"{prefix}_*.parquet"), recursive=True))
    if not files:
        return None
    try:
        return pd.read_parquet(files[-1])
    except Exception:
        return None


@pytest.fixture(scope="session")
def economic_df() -> pd.DataFrame | None:
    return _load_latest_parquet("economic_indicators")


@pytest.fixture(scope="session")
def shipping_df() -> pd.DataFrame | None:
    return _load_latest_parquet("shipping_indices")


@pytest.fixture(scope="session")
def crop_df() -> pd.DataFrame | None:
    return _load_latest_parquet("crop_data")


@pytest.fixture(scope="session")
def climate_df() -> pd.DataFrame | None:
    return _load_latest_parquet("climate_data")


@pytest.fixture(scope="session")
def geopolitical_df() -> pd.DataFrame | None:
    return _load_latest_parquet("geopolitical_indices")


@pytest.fixture(scope="session")
def production_df() -> pd.DataFrame | None:
    return _load_latest_parquet("production_data")


@pytest.fixture(scope="session")
def commodity_df() -> pd.DataFrame | None:
    return _load_latest_parquet("commodity_data")


@pytest.fixture(scope="session")
def customs_df() -> pd.DataFrame | None:
    return _load_latest_parquet("customs_import")
