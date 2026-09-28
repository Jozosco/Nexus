"""시장·유통 구조 지표 회귀 테스트 (A-291) — as-of·원산지 결측 처리·키 유일성."""
import pandas as pd

from src.features.structural_indicators import _self_test, build


def test_spread_asof_and_fx_not_used_before_release() -> None:
    _self_test()        # 환율 공표 전 날짜는 산출하지 않음 · BOHO 산식 · available_at ≥ event_time


def test_origin_share_treats_missing_country_as_no_import() -> None:
    months = pd.date_range("2025-01-01", periods=12, freq="MS")
    rows = []
    for i, m in enumerate(months):
        rows.append(("KCS_1507101000_IMP_KG_WORLD", m, 100.0))
        rows.append(("KCS_1507101000_IMP_KG_VN", m, 100.0 if i % 2 else 50.0))
        if i % 2 == 0:                                   # 짝수 달만 아르헨 행 존재 — 홀수 달은 '수입 없음'
            rows.append(("KCS_1507101000_IMP_KG_AR", m, 50.0))
    long = pd.DataFrame(rows, columns=["indicator_code", "price_date", "value"])
    long["available_at"] = long["price_date"] + pd.offsets.MonthBegin(1) + pd.Timedelta(days=14)
    out = build(long)
    vn = out[out["indicator_code"] == "STR_KR_CRUDE_SBO_VN_SHARE"].set_index("price_date")["value"]
    assert abs(vn.iloc[-1] - 0.75) < 1e-9                  # 12개월 VN 900 / WORLD 1,200
    assert not out.duplicated(["indicator_code", "price_date"]).any()
    assert (out["available_at"] >= out["period_end"]).all()   # 월별 값은 월말 전 공표 불가
    assert out.groupby("indicator_code")["unit"].nunique().max() == 1
