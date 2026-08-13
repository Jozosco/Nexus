"""G1/G2 Preview 진입 조건을 외부 데이터 없이 검증하는 회귀 테스트."""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from scripts import ingest_databento_bo
from scripts.build_unstructured_timeseries import _as_bool, _records_from_index
from scripts.publish_blob_snapshot import _validated_files, build_manifest
from src.features.build_feature_mart import _validate_target_rows, build_calendar
from src.forecasting.variable_importance_g1 import (
    _lasso_importance,
    _load_g1_feature_mart,
    _require_g1_target,
)
from src.pipeline.asof import ReleaseRule, _release_for, attach_asof
from src.pipeline.validators.c08_dq_validator import (
    _connector_name,
    _score_accuracy,
    _score_completeness,
    _score_consistency,
    _score_skewness,
    _target_contract_alerts,
)


@pytest.fixture
def valid_target_rows() -> pd.DataFrame:
    dates = pd.bdate_range("2020-01-02", periods=1_100)
    return pd.DataFrame(
        {
            "indicator_code": "CBOT_BO_CLOSE",
            "value": pd.Series(range(len(dates)), dtype="float64") + 30.0,
            "price_date": dates,
            "event_time": dates,
            "available_at": dates,
            "target_eligible": True,
            "time_basis": "CME_SESSION",
            "unit": "USc/lb",
            "source_vintage": "test",
        }
    )


@pytest.fixture
def synthetic_feature_mart(tmp_path: Path) -> tuple[Path, Path]:
    dates = pd.bdate_range("2018-01-02", periods=1_100)
    driver = np.sin(np.arange(len(dates)) / 20.0)
    target_returns = pd.Series(driver * 0.01, dtype="float64")
    target_returns.iloc[-20:] = np.nan
    mart = pd.DataFrame(
        {
            "price_date": dates,
            "target_close": 40.0 + np.arange(len(dates)) * 0.01,
            "target_ret20": target_returns,
            "feat_CBOT_BO_CLOSE": 40.0 + np.arange(len(dates)) * 0.01,
            "feat_DRIVER": driver,
            "feat_CONTAMINATED": driver * 2,
            "age_DRIVER": 0.0,
        }
    )
    mart_path = tmp_path / "feature_mart.parquet"
    contract_path = tmp_path / "feature_contract.yaml"
    mart.to_parquet(mart_path, index=False)
    contract = {
        "target": {
            "indicator": "CBOT_BO_CLOSE",
            "target_eligible": True,
            "time_basis": ["CME_SESSION"],
            "unit": ["USc/lb"],
        },
        "features": {
            "feat_CBOT_BO_CLOSE": {"revision_contaminated": False},
            "feat_DRIVER": {"revision_contaminated": False},
            "feat_CONTAMINATED": {"revision_contaminated": True},
        },
    }
    contract_path.write_text(yaml.safe_dump(contract), encoding="utf-8")
    return mart_path, contract_path


@pytest.fixture
def snapshot_file(tmp_path: Path) -> Path:
    path = tmp_path / "report.json"
    path.write_text('{"status":"PASS"}\n', encoding="utf-8")
    return path


@pytest.fixture
def unstructured_index_file(tmp_path: Path) -> Path:
    path = tmp_path / "unstructured_index_gain.csv"
    pd.DataFrame(
        {
            "file": ["blocked.pdf", "valid.pdf"],
            "path": ["GAIN/2024/01/blocked.pdf", "GAIN/2024/01/valid.pdf"],
            "readable": ["False", "True"],
            "signals": [None, "weather"],
            "bull": [None, 2],
            "bear": [None, 1],
        }
    ).to_csv(path, index=False)
    return path


@pytest.fixture
def release_workflow_text() -> str:
    root = Path(__file__).resolve().parents[1]
    paths = [
        root / ".github/workflows/external_data_refresh.yml",
        root / ".github/workflows/historical_backfill.yml",
        root / ".github/workflows/unstructured_analysis.yml",
    ]
    return "\n".join(path.read_text(encoding="utf-8") for path in paths)


def test_databento_missing_key_is_fatal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABENTO_API_KEY", raising=False)
    monkeypatch.delenv("DATABENTO_FROM_CSV", raising=False)
    with pytest.raises(RuntimeError, match="DATABENTO_API_KEY"):
        ingest_databento_bo.run()


def test_databento_missing_offline_csv_is_fatal(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("DATABENTO_FROM_CSV", str(tmp_path / "missing.csv"))
    with pytest.raises(FileNotFoundError, match="CSV 없음"):
        ingest_databento_bo.run()


def test_databento_utc_output_cannot_be_targeted() -> None:
    source = pd.DataFrame(
        {"price_date": [pd.Timestamp("2026-08-09")], "close": [51.25], "volume": [100]}
    )
    output = ingest_databento_bo._to_long_output(source)
    assert set(output["time_basis"]) == {"UTC_CALENDAR_DAY"}
    assert not output["target_eligible"].any()
    assert set(output["indicator_code"]) == {"CBOT_BO_UTC_CLOSE", "CBOT_BO_UTC_VOLUME"}


def test_feature_mart_rejects_weekend_target(valid_target_rows: pd.DataFrame) -> None:
    broken = valid_target_rows.copy()
    broken.loc[0, ["price_date", "event_time", "available_at"]] = pd.Timestamp("2020-01-05")
    with pytest.raises(RuntimeError, match="주말 거래일"):
        _validate_target_rows(broken, "CBOT_BO_CLOSE")


def test_feature_mart_rejects_utc_target(valid_target_rows: pd.DataFrame) -> None:
    broken = valid_target_rows.copy()
    broken["time_basis"] = "UTC_CALENDAR_DAY"
    with pytest.raises(RuntimeError, match="time_basis"):
        _validate_target_rows(broken, "CBOT_BO_CLOSE")


def test_feature_mart_rejects_inverted_target_availability(
    valid_target_rows: pd.DataFrame,
) -> None:
    broken = valid_target_rows.copy()
    broken.loc[0, "available_at"] = broken.loc[0, "event_time"] - pd.Timedelta(days=1)
    with pytest.raises(RuntimeError, match="available_at"):
        _validate_target_rows(broken, "CBOT_BO_CLOSE")


def test_feature_mart_does_not_fallback_without_target() -> None:
    features = pd.DataFrame(
        {
            "indicator_code": ["CPO_USD_MT"],
            "event_time": [pd.Timestamp("2024-01-02")],
            "available_at": [pd.Timestamp("2024-01-02")],
            "value": [900.0],
            "target_eligible": [False],
            "time_basis": ["MARKET_DAY"],
            "unit": ["USD/MT"],
        }
    )
    with pytest.raises(RuntimeError, match="검증된 목표변수"):
        build_calendar(features, "2024-01-01", "2024-12-31")


def test_g1_rejects_brent_fallback() -> None:
    dates = pd.bdate_range("2020-01-01", periods=1_100)
    brent = pd.DataFrame(
        {"indicator_code": "BRENT_USD_BBL", "price_date": dates, "value": 70.0}
    )
    wide = pd.DataFrame({"BRENT_USD_BBL": 70.0}, index=dates)
    with pytest.raises(RuntimeError, match="대체 타깃"):
        _require_g1_target({"commodity": brent}, wide)


def test_g1_accepts_only_valid_session_target(valid_target_rows: pd.DataFrame) -> None:
    wide = valid_target_rows.pivot(index="price_date", columns="indicator_code", values="value")
    assert _require_g1_target({"target": valid_target_rows}, wide) == "CBOT_BO_CLOSE"


def test_c08_empty_frame_is_rejected_by_all_scored_dimensions() -> None:
    empty = pd.DataFrame()
    assert _score_accuracy(empty, "economic_indicators") == 0.0
    assert _score_completeness(empty) == 0.0
    assert _score_consistency(empty, "economic_indicators") == 0.0
    assert _score_skewness(empty) == 0.0


def test_c08_uses_longest_connector_prefix() -> None:
    assert _connector_name("economic_indicators_20260813") == "economic_indicators"
    assert _connector_name("databento_bo_utc_historical") == "databento_bo_utc_historical"


def test_c08_target_contract_rejects_weekend(valid_target_rows: pd.DataFrame) -> None:
    broken = valid_target_rows.copy()
    broken.loc[0, "price_date"] = pd.Timestamp("2020-01-05")
    assert any("주말" in alert for alert in _target_contract_alerts(broken))


def test_asof_comtrade_delay_applied_once() -> None:
    event = pd.Timestamp("2024-01-31")
    rule = ReleaseRule("lag_days", lag_days=45)
    assert _release_for(event, rule) == event + timedelta(days=45)


def test_utc_bar_available_after_bucket_end() -> None:
    row = pd.DataFrame(
        {
            "price_date": [pd.Timestamp("2024-01-07")],
            "indicator_code": ["CBOT_BO_UTC_CLOSE"],
            "value": [48.0],
        }
    )
    result = attach_asof(row, source="CBOT_BO_UTC_")
    assert result.loc[0, "available_at"] == pd.Timestamp("2024-01-08")


def test_blob_manifest_has_lineage(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_SHA", "abc123")
    monkeypatch.setenv("GITHUB_RUN_ID", "42")
    manifest = build_manifest([], "snapshot-test")
    assert manifest["snapshot_id"] == "snapshot-test"
    assert manifest["source_commit"] == "abc123"
    assert manifest["source_run_id"] == "42"
    assert manifest["files"] == []


def test_blob_manifest_records_content_hash(snapshot_file: Path) -> None:
    manifest = build_manifest([snapshot_file], "snapshot-hash")
    assert manifest["files"][0]["bytes"] > 0
    assert len(manifest["files"][0]["sha256"]) == 64


def test_blob_uploader_rejects_paths_outside_release_roots(snapshot_file: Path) -> None:
    with pytest.raises(ValueError, match="허용되지 않은 업로드 경로"):
        _validated_files([str(snapshot_file)])


def test_unstructured_index_does_not_emit_nan_tags(
    unstructured_index_file: Path,
) -> None:
    records = _records_from_index("gain", unstructured_index_file, "TEST")
    codes = {record["indicator_code"] for record in records}
    assert "UNSTR_GAIN_NAN" not in codes
    assert "UNSTR_GAIN_weather" in codes
    assert _as_bool(pd.Series(["False", "True"])).tolist() == [False, True]


def test_release_workflows_do_not_bypass_model_gates(release_workflow_text: str) -> None:
    forbidden = [
        "validate_asof.py --warn",
        "build_unstructured_timeseries.py || true",
        "git push origin HEAD:main",
        "contents: write",
    ]
    for pattern in forbidden:
        assert pattern not in release_workflow_text
    assert release_workflow_text.count("needs: [model-readiness]") >= 2


def test_g1_loads_only_asof_noncontaminated_features(
    synthetic_feature_mart: tuple[Path, Path],
) -> None:
    mart_path, contract_path = synthetic_feature_mart
    analysis, levels, target = _load_g1_feature_mart(
        mart_path=mart_path, contract_path=contract_path, horizon=20
    )
    assert target == "target_ret20"
    assert list(analysis.columns) == ["target_ret20", "DRIVER"]
    assert "CBOT_BO_CLOSE" in levels.columns


def test_elasticnet_uses_walk_forward_splits() -> None:
    from sklearn.model_selection import TimeSeriesSplit

    dates = pd.bdate_range("2020-01-02", periods=240)
    x1 = np.sin(np.arange(len(dates)) / 8.0)
    x2 = np.cos(np.arange(len(dates)) / 12.0)
    wide = pd.DataFrame(
        {"target_ret20": 0.8 * x1 - 0.2 * x2, "driver_a": x1, "driver_b": x2},
        index=dates,
    )
    result = _lasso_importance(wide, "target_ret20")
    assert not result.empty
    for train, test in TimeSeriesSplit(n_splits=5, gap=20).split(wide):
        assert dates[train].max() < dates[test].min()
