"""E1 스탬프 경보 집계 회귀 테스트 (A-245 — 런 #87 실측 결함)."""
from __future__ import annotations

import importlib
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def stamp_mod(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)
    sys.path.insert(0, str(ROOT / "scripts"))
    mod = importlib.import_module("signed_daily_stamp")
    return importlib.reload(mod)


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# alert", encoding="utf-8")


def test_today_alert_counted_by_compact_tag(stamp_mod, tmp_path):
    """실제 파일명 형식(YYYYMMDD_HHMM)의 당일 경보를 1건으로 센다 — 구 코드는 0건."""
    tag = date.today().strftime("%Y%m%d")
    _touch(tmp_path / "reports/pipeline/run_123" / f"g1_alert_{tag}_0019.md")
    assert stamp_mod._alerts_today() == 1


def test_no_alert_returns_zero(stamp_mod, tmp_path):
    (tmp_path / "reports/pipeline/run_123").mkdir(parents=True)
    assert stamp_mod._alerts_today() == 0


def test_other_day_alert_not_counted(stamp_mod, tmp_path):
    """전일 경보 파일이 남아 있어도 당일 집계에 섞이지 않는다."""
    yday = (date.today() - timedelta(days=1)).strftime("%Y%m%d")
    _touch(tmp_path / "reports/pipeline/run_122" / f"g1_alert_{yday}_0019.md")
    assert stamp_mod._alerts_today() == 0


def test_run_folder_and_recursive_glob_dedupe(stamp_mod, tmp_path, monkeypatch):
    """런 폴더 우선 탐색과 재귀 글로브가 같은 파일을 두 번 세지 않는다."""
    monkeypatch.setenv("GITHUB_RUN_ID", "123")
    tag = date.today().strftime("%Y%m%d")
    _touch(tmp_path / "reports/pipeline/run_123" / f"g1_alert_{tag}_0019.md")
    _touch(tmp_path / "reports/pipeline/run_123" / f"g1_alert_{tag}_0530.md")
    assert stamp_mod._alerts_today() == 2
