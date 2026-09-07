"""TE xlsx 증분 갱신기 — append·검증 로직 단위 테스트 (A-248, 네트워크 불요)."""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
from openpyxl import Workbook, load_workbook

from scripts.update_te_xlsx_from_api import HEADER, _read_last_date, _validate, append_rows


def _make(path: Path, desc: bool = False) -> None:
    wb = Workbook(); ws = wb.active; ws.title = "2026년"; ws.append(HEADER)
    rows = [[6, 30, 1, 2, 0.5, 1.5], [7, 1, 1, 2, 0.5, 1.6]]
    for r in (reversed(rows) if desc else rows):
        ws.append(r)
    wb.save(path)


def test_last_date_and_direction(tmp_path):
    p = tmp_path / "2010~2026_Soybeans_CBOT_USD Per Bushel.xlsx"; _make(p)
    assert _read_last_date(p) == (date(2026, 7, 1), False)
    q = tmp_path / "2019~2026_Urea_CBOT_USD Per Ton.xlsx"; _make(q, desc=True)
    assert _read_last_date(q) == (date(2026, 7, 1), True)


def test_append_ascending_and_new_year_sheet(tmp_path):
    p = tmp_path / "a.xlsx"; _make(p)
    rows = pd.DataFrame({"date": pd.to_datetime(["2026-07-02", "2027-01-04"]),
                         "open": [1, 1], "high": [2, 2], "low": [0.5, 0.5], "close": [1.7, 1.8]})
    assert append_rows(p, rows, desc=False) == 2
    wb = load_workbook(p)
    assert "2027년" in wb.sheetnames and [c.value for c in wb["2027년"][1]] == HEADER
    assert [c.value for c in wb["2026년"][4]][:2] == [7, 2]
    assert _read_last_date(p)[0] == date(2027, 1, 4)


def test_append_descending_inserts_on_top(tmp_path):
    p = tmp_path / "u.xlsx"; _make(p, desc=True)
    rows = pd.DataFrame({"date": pd.to_datetime(["2026-07-02", "2026-07-03"]),
                         "open": [1, 1], "high": [2, 2], "low": [0.5, 0.5], "close": [1.7, 1.8]})
    append_rows(p, rows, desc=True)
    ws = load_workbook(p)["2026년"]
    assert [ws.cell(2, 1).value, ws.cell(2, 2).value] == [7, 3]     # 최신이 최상단
    assert _read_last_date(p) == (date(2026, 7, 3), True)


def test_validate_rejects_regression(tmp_path):
    a = tmp_path / "a.xlsx"; _make(a)
    b = tmp_path / "b.xlsx"; wb = Workbook(); ws = wb.active; ws.title = "2026년"; ws.append(HEADER); ws.append([6, 1, 1, 1, 1, 1]); wb.save(b)
    ok, msg = _validate(a, b)
    assert not ok and "역행" in msg
