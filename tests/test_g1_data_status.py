"""G1 활용 데이터 현황 표 — 일별 비정형 신호 CSV 행(2026-09-13 신설) 단위 테스트.

① 임시 CSV(3행·2지표) → 행수·지표 수·날짜범위·무결성·신선도 산출
② 파일 부재 → '미수집' + '❌ 데이터 없음' 정직 표기
③ _build_data_status({})가 현황 표에 해당 행을 항상 포함
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

pytest.importorskip("numpy")
vi = pytest.importorskip("src.forecasting.variable_importance_g1")

COLUMNS = ["변수 항목", "변수별 항목 수", "행수", "날짜범위", "무결성", "신선도"]


@pytest.fixture
def signals_csv(tmp_path: Path) -> Path:
    """3행·2지표 일별 신호 CSV — appended_at은 오늘(UTC)로 신선."""
    now = datetime.now(timezone.utc).isoformat()
    # A-274: 고정 날짜는 실행일이 지나면 '기한 초과'로 바뀌어 테스트가 날짜에 종속됐다 → 오늘 기준 상대 날짜
    _d1 = (datetime.now(timezone.utc) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    _d0 = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    df = pd.DataFrame({
        "date": [_d1, _d0, _d0],
        "indicator": ["RSS_FARMDOC_DAILY", "RSS_FARMDOC_DAILY", "HORMUZ_THREAT_LEVEL"],
        "category": ["전문 매체", "전문 매체", "해협"],
        "value": [2.0, 1.0, 3.0],
        "note": ["a", "b", "c"],
        "source_name": ["RSS", "RSS", "Perplexity"],
        "appended_at": [now, now, now],
    })
    path = tmp_path / "unstructured_daily_signals.csv"
    df.to_csv(path, index=False)
    return path


def test_row_from_tmp_csv(signals_csv: Path) -> None:
    row = vi._daily_signals_status_row(signals_csv)
    assert list(row.keys()) == COLUMNS
    assert row["변수 항목"] == vi.DAILY_SIGNALS_LABEL
    assert row["변수별 항목 수"] == 2
    assert row["행수"] == 3
    _d1 = (datetime.now(timezone.utc) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    _d0 = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    assert row["날짜범위"] == f"{_d1} ~ {_d0}"
    assert row["무결성"].startswith("✅")
    assert row["신선도"].startswith("✅")   # A-267: 내용 기준 적시성 라벨


def test_missing_file_is_honest(tmp_path: Path) -> None:
    row = vi._daily_signals_status_row(tmp_path / "없음.csv")
    assert row["변수 항목"] == vi.DAILY_SIGNALS_LABEL
    assert row["행수"] == 0
    assert row["변수별 항목 수"] == 0
    assert row["날짜범위"] == "미수집"
    assert row["신선도"] == "❌ 데이터 없음"


def test_build_data_status_includes_daily_signals_row() -> None:
    status = vi._build_data_status({})
    assert list(status.columns) == COLUMNS
    labels = status["변수 항목"].astype(str).tolist()
    assert vi.DAILY_SIGNALS_LABEL in labels
    assert labels.count(vi.DAILY_SIGNALS_LABEL) == 1
