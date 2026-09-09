"""관세청 월 단위 증분 조회 — 공개 월·업로드 커버리지·건너뜀 규칙 (A-253)."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from src.pipeline.connectors import customs_connector as cc


def test_ym_add_and_release_month():
    assert cc._ym_add("202601", -1) == "202512" and cc._ym_add("202612", 1) == "202701"
    assert cc._last_released_month(date(2026, 9, 9)) == "202607"     # 8월 통계는 9/15 공개 전
    assert cc._last_released_month(date(2026, 9, 16)) == "202608"
    assert cc._last_released_month(date(2026, 1, 3)) == "202511"


def test_coverage_env_override(monkeypatch):
    monkeypatch.setenv("CUSTOMS_UPLOAD_COVERAGE_YYYYMM", "202607")
    assert cc._upload_coverage_month() == "202607"


def test_coverage_from_xlsx(tmp_path, monkeypatch):
    monkeypatch.delenv("CUSTOMS_UPLOAD_COVERAGE_YYYYMM", raising=False)
    d = tmp_path / "Soybean Oil (1507)" / "1507.10"
    d.mkdir(parents=True)
    rows = [["구분", "무역수지", "수출액", "수출량", "수입액", "수입량"]] + \
           [[f"{m}월", 0, 0, 0, 100 if m <= 7 else None, 5 if m <= 7 else None] for m in range(1, 13)]
    with pd.ExcelWriter(d / "Argentina.xlsx", engine="openpyxl") as w:
        pd.DataFrame(rows).to_excel(w, sheet_name="2026년", index=False, header=False)
    assert cc._upload_coverage_month(tmp_path) == "202607"


def test_incremental_window_skips_when_nothing_new(monkeypatch):
    monkeypatch.setenv("CUSTOMS_UPLOAD_COVERAGE_YYYYMM", "202607")
    start, end, cov = cc._incremental_window(date(2026, 9, 9))
    assert (start, end, cov) == ("202608", "202607", "202607") and start > end
    start, end, _ = cc._incremental_window(date(2026, 9, 16))
    assert (start, end) == ("202608", "202608")


def test_run_skips_without_api_calls(monkeypatch, capsys):
    monkeypatch.setenv("CUSTOMS_UPLOAD_COVERAGE_YYYYMM", "202607")
    monkeypatch.delenv("BACKFILL_MODE", raising=False)
    monkeypatch.setattr(cc, "_last_released_month", lambda today=None: "202607")
    monkeypatch.setattr(cc, "_fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("API 호출 금지")))
    cc.run()
    assert "조회할 신규 월 없음" in capsys.readouterr().out
