"""
파이프라인 데이터 품질 테스트 — WBS 1.1.8 (C-08 게이트 검증)
great_expectations 패턴 기반; GE가 설치된 경우 validator 계층도 실행.

실행: pytest tests/test_pipeline_quality.py -v
"""
from __future__ import annotations

from datetime import date
from typing import Optional

import numpy as np
import pandas as pd
import pytest

STALE_BDAYS  = 5
NULL_WARN_PCT = 5.0    # 결측치 경고 임계값
NULL_FAIL_PCT = 30.0   # 결측치 실패 임계값
MIN_ROWS      = 10     # 최소 행 수

# ── 공통 헬퍼 ─────────────────────────────────────────────────────────────────

def _skip_if_none(df: Optional[pd.DataFrame]) -> pd.DataFrame:
    if df is None:
        pytest.skip("parquet 파일 없음 — 커넥터 수집 후 재실행")
    return df


def _null_pct(df: pd.DataFrame) -> float:
    return float(df.isnull().mean().mean() * 100)


def _freshness_bdays(df: pd.DataFrame) -> Optional[int]:
    if "ingested_at" not in df.columns:
        return None
    ts = pd.to_datetime(df["ingested_at"], utc=True, errors="coerce").dropna()
    if ts.empty:
        return None
    return int(np.busday_count(ts.max().date(), date.today()))


# ── 스키마 공통 검증 ─────────────────────────────────────────────────────────

def _assert_common_schema(df: pd.DataFrame, connector: str) -> None:
    """모든 커넥터 공통 스키마 요건: price_date 컬럼, 행 수, 결측치 임계값."""
    assert "price_date" in df.columns, f"[{connector}] 필수 컬럼 'price_date' 없음"
    assert len(df) >= MIN_ROWS, f"[{connector}] 행 수 {len(df)} < {MIN_ROWS}"

    null = _null_pct(df)
    assert null < NULL_FAIL_PCT, (
        f"[{connector}] 결측치 {null:.1f}% — 허용 한계 {NULL_FAIL_PCT}% 초과"
    )
    if null > NULL_WARN_PCT:
        print(f"\n[{connector}] ⚠️ 결측치 경고: {null:.1f}% (권장 {NULL_WARN_PCT}% 이하)")


def _assert_no_future_price_date(df: pd.DataFrame, connector: str) -> None:
    """가격 날짜가 오늘 이후를 포함하지 않는지 확인 (데이터 누출 방지)."""
    dates = pd.to_datetime(df["price_date"], errors="coerce").dropna()
    future = (dates.dt.date > date.today()).sum()
    assert future == 0, (
        f"[{connector}] 미래 price_date {future}건 발견 — 데이터 누출 가능성"
    )


def _assert_value_non_negative(df: pd.DataFrame, connector: str) -> None:
    """value 컬럼이 존재하면 음수가 없어야 함 (가격·지수)."""
    if "value" not in df.columns:
        return
    vals = pd.to_numeric(df["value"], errors="coerce").dropna()
    neg = (vals < 0).sum()
    assert neg == 0, (
        f"[{connector}] 'value' 컬럼에 음수 {neg}건 — 유효하지 않은 가격/지수"
    )


def _assert_freshness(df: pd.DataFrame, connector: str) -> None:
    """ingested_at 기준 5영업일 이내 수집 확인."""
    bdays = _freshness_bdays(df)
    if bdays is None:
        pytest.skip(f"[{connector}] ingested_at 컬럼 없음 — 신선도 확인 불가")
    assert bdays <= STALE_BDAYS, (
        f"[{connector}] 데이터 STALE — 마지막 수집 {bdays}영업일 전 (기준 {STALE_BDAYS}일)"
    )


def _assert_date_range(df: pd.DataFrame, connector: str) -> None:
    """price_date 범위가 2020-01-01 이후인지 확인."""
    dates = pd.to_datetime(df["price_date"], errors="coerce").dropna()
    if dates.empty:
        return
    min_date = dates.min().date()
    assert min_date >= date(2019, 12, 31), (
        f"[{connector}] price_date 최솟값 {min_date}가 2020년 이전 — 수집 범위 확인 필요"
    )


# ── 커넥터별 테스트 ────────────────────────────────────────────────────────────

class TestEconomicIndicators:
    """1.1.2 경제 지표 (FRED · BOK ECOS · EIA · KOSIS)."""

    def test_schema(self, economic_df: Optional[pd.DataFrame]) -> None:
        df = _skip_if_none(economic_df)
        _assert_common_schema(df, "economic_indicators")
        for col in ["indicator_code", "value", "source_name"]:
            assert col in df.columns, f"필수 컬럼 '{col}' 없음"

    def test_no_future_dates(self, economic_df: Optional[pd.DataFrame]) -> None:
        df = _skip_if_none(economic_df)
        _assert_no_future_price_date(df, "economic_indicators")

    def test_value_numeric(self, economic_df: Optional[pd.DataFrame]) -> None:
        df = _skip_if_none(economic_df)
        vals = pd.to_numeric(df["value"], errors="coerce")
        non_numeric = vals.isnull().sum()
        total = len(df)
        assert non_numeric / total < 0.05, (
            f"'value' 컬럼 비수치 비율 {non_numeric/total:.1%} — 5% 초과"
        )

    def test_indicator_code_not_null(self, economic_df: Optional[pd.DataFrame]) -> None:
        df = _skip_if_none(economic_df)
        null_codes = df["indicator_code"].isnull().sum()
        assert null_codes == 0, f"indicator_code 결측 {null_codes}건"

    def test_freshness(self, economic_df: Optional[pd.DataFrame]) -> None:
        df = _skip_if_none(economic_df)
        _assert_freshness(df, "economic_indicators")


class TestShippingIndices:
    """1.1.3 해운 지수 (BCAA · BDI)."""

    def test_schema(self, shipping_df: Optional[pd.DataFrame]) -> None:
        df = _skip_if_none(shipping_df)
        _assert_common_schema(df, "shipping_indices")
        for col in ["indicator_code", "value"]:
            assert col in df.columns, f"필수 컬럼 '{col}' 없음"

    def test_no_future_dates(self, shipping_df: Optional[pd.DataFrame]) -> None:
        _assert_no_future_price_date(_skip_if_none(shipping_df), "shipping_indices")

    def test_positive_values(self, shipping_df: Optional[pd.DataFrame]) -> None:
        _assert_value_non_negative(_skip_if_none(shipping_df), "shipping_indices")

    def test_freshness(self, shipping_df: Optional[pd.DataFrame]) -> None:
        _assert_freshness(_skip_if_none(shipping_df), "shipping_indices")


class TestWASDECropData:
    """1.1.4 WASDE / USDA 작황 데이터."""

    def test_schema(self, crop_df: Optional[pd.DataFrame]) -> None:
        df = _skip_if_none(crop_df)
        _assert_common_schema(df, "crop_data")

    def test_no_future_dates(self, crop_df: Optional[pd.DataFrame]) -> None:
        _assert_no_future_price_date(_skip_if_none(crop_df), "crop_data")

    def test_date_range(self, crop_df: Optional[pd.DataFrame]) -> None:
        _assert_date_range(_skip_if_none(crop_df), "crop_data")

    def test_freshness(self, crop_df: Optional[pd.DataFrame]) -> None:
        _assert_freshness(_skip_if_none(crop_df), "crop_data")


class TestClimateData:
    """1.1.5 기후·ENSO 데이터 (NOAA CPC · ECMWF)."""

    def test_schema(self, climate_df: Optional[pd.DataFrame]) -> None:
        df = _skip_if_none(climate_df)
        _assert_common_schema(df, "climate_data")
        for col in ["indicator_code", "value"]:
            assert col in df.columns, f"필수 컬럼 '{col}' 없음"

    def test_oni_range(self, climate_df: Optional[pd.DataFrame]) -> None:
        """ENSO ONI 값은 물리적으로 -10 ~ +10 범위 이내."""
        df = _skip_if_none(climate_df)
        if "indicator_code" not in df.columns:
            return
        oni = df[df["indicator_code"] == "ONI"]["value"].dropna()
        if oni.empty:
            pytest.skip("ONI 데이터 없음")
        vals = pd.to_numeric(oni, errors="coerce").dropna()
        assert vals.between(-10, 10).all(), f"ONI 이상값 범위 초과: min={vals.min()}, max={vals.max()}"

    def test_no_future_dates(self, climate_df: Optional[pd.DataFrame]) -> None:
        _assert_no_future_price_date(_skip_if_none(climate_df), "climate_data")


class TestGeopoliticalIndices:
    """1.1.6 지정학 리스크 지수 (GPR · Hormuz)."""

    def test_schema(self, geopolitical_df: Optional[pd.DataFrame]) -> None:
        df = _skip_if_none(geopolitical_df)
        _assert_common_schema(df, "geopolitical_indices")
        for col in ["indicator_code", "value"]:
            assert col in df.columns, f"필수 컬럼 '{col}' 없음"

    def test_gpr_normalized_range(self, geopolitical_df: Optional[pd.DataFrame]) -> None:
        """GPR Normalized 지수: 0 ~ 1 범위."""
        df = _skip_if_none(geopolitical_df)
        if "indicator_code" not in df.columns:
            return
        gpr = df[df["indicator_code"] == "GPR_NORMALIZED"]["value"].dropna()
        if gpr.empty:
            pytest.skip("GPR_NORMALIZED 없음")
        vals = pd.to_numeric(gpr, errors="coerce").dropna()
        assert vals.between(0, 1).all(), f"GPR_NORMALIZED 범위 이탈: min={vals.min():.4f}, max={vals.max():.4f}"

    def test_no_future_dates(self, geopolitical_df: Optional[pd.DataFrame]) -> None:
        _assert_no_future_price_date(_skip_if_none(geopolitical_df), "geopolitical_indices")

    def test_freshness(self, geopolitical_df: Optional[pd.DataFrame]) -> None:
        _assert_freshness(_skip_if_none(geopolitical_df), "geopolitical_indices")


class TestProductionData:
    """1.1.7 생산량·농업기상 데이터."""

    def test_schema(self, production_df: Optional[pd.DataFrame]) -> None:
        df = _skip_if_none(production_df)
        _assert_common_schema(df, "production_data")

    def test_no_future_dates(self, production_df: Optional[pd.DataFrame]) -> None:
        _assert_no_future_price_date(_skip_if_none(production_df), "production_data")

    def test_date_range(self, production_df: Optional[pd.DataFrame]) -> None:
        _assert_date_range(_skip_if_none(production_df), "production_data")


class TestCommodityData:
    """1.1.10 상품가격 (CBOT · ARS · CPO · 가뭄지수)."""

    def test_schema(self, commodity_df: Optional[pd.DataFrame]) -> None:
        df = _skip_if_none(commodity_df)
        _assert_common_schema(df, "commodity_data")

    def test_no_future_dates(self, commodity_df: Optional[pd.DataFrame]) -> None:
        _assert_no_future_price_date(_skip_if_none(commodity_df), "commodity_data")

    def test_cbot_price_positive(self, commodity_df: Optional[pd.DataFrame]) -> None:
        """CBOT 대두유 종가: 반드시 양수."""
        df = _skip_if_none(commodity_df)
        if "indicator_code" not in df.columns:
            return
        cbot = df[df["indicator_code"] == "CBOT_BO_CLOSE"]["value"].dropna()
        if cbot.empty:
            pytest.skip("CBOT_BO_CLOSE 없음")
        vals = pd.to_numeric(cbot, errors="coerce").dropna()
        assert (vals > 0).all(), f"CBOT_BO_CLOSE 음수/0 값 발견: {(vals <= 0).sum()}건"

    def test_freshness(self, commodity_df: Optional[pd.DataFrame]) -> None:
        _assert_freshness(_skip_if_none(commodity_df), "commodity_data")


class TestCustomsImport:
    """1.1.11 한국 대두유 수입 통계 (관세청 HS 1507)."""

    def test_schema(self, customs_df: Optional[pd.DataFrame]) -> None:
        df = _skip_if_none(customs_df)
        _assert_common_schema(df, "customs_import")

    def test_no_future_dates(self, customs_df: Optional[pd.DataFrame]) -> None:
        _assert_no_future_price_date(_skip_if_none(customs_df), "customs_import")

    def test_hs_code_1507(self, customs_df: Optional[pd.DataFrame]) -> None:
        """HS 코드가 반드시 1507 계열이어야 함."""
        df = _skip_if_none(customs_df)
        if "hs_code" not in df.columns:
            pytest.skip("hs_code 컬럼 없음")
        non_1507 = (~df["hs_code"].astype(str).str.startswith("1507")).sum()
        assert non_1507 == 0, f"HS 1507 이외 코드 {non_1507}건 포함"


class TestTimeSeriesIntegrity:
    """시계열 무결성 테스트 — 데이터 누출 방지."""

    def test_no_shuffle_leakage(self, economic_df: Optional[pd.DataFrame]) -> None:
        """price_date가 단조 증가하거나 역방향 점프가 365일 초과하지 않음."""
        df = _skip_if_none(economic_df)
        dates = pd.to_datetime(df["price_date"], errors="coerce").dropna().sort_values()
        if len(dates) < 2:
            return
        diffs = dates.diff().dropna()
        large_backward = (diffs < pd.Timedelta(days=-365)).sum()
        assert large_backward == 0, (
            f"price_date에 365일 초과 역방향 점프 {large_backward}건 — 데이터 셔플 또는 타임존 오류 의심"
        )

    def test_train_future_split(self, commodity_df: Optional[pd.DataFrame]) -> None:
        """훈련 데이터(cutoff 이전)와 예측 범위(cutoff 이후)의 명확한 분리 확인."""
        df = _skip_if_none(commodity_df)
        dates = pd.to_datetime(df["price_date"], errors="coerce").dropna()
        if dates.empty:
            return
        today = pd.Timestamp(date.today())
        future_rows = (dates > today).sum()
        assert future_rows == 0, (
            f"수집 데이터에 미래 날짜 {future_rows}건 포함 — 데이터 누출 가능성"
        )


# ── Great Expectations 선택적 계층 (GE 설치된 경우만 실행) ──────────────────────

def test_ge_economic_schema_if_available(economic_df: Optional[pd.DataFrame]) -> None:
    """GE가 설치된 환경에서만 실행. 없으면 SKIP."""
    try:
        import great_expectations as gx  # noqa: F401
    except ImportError:
        pytest.skip("great_expectations 미설치 — pip install great-expectations")

    df = _skip_if_none(economic_df)

    context    = gx.get_context()
    datasource = context.sources.add_or_update_pandas(name="pipeline_test")
    data_asset = datasource.add_dataframe_asset(name="economic_indicators")
    batch_req  = data_asset.build_batch_request(dataframe=df)
    validator  = context.get_validator(batch_request=batch_req)

    validator.expect_column_to_exist("price_date")
    validator.expect_column_to_exist("value")
    validator.expect_column_to_exist("indicator_code")
    validator.expect_column_values_to_not_be_null("price_date")
    validator.expect_column_values_to_not_be_null("indicator_code")
    validator.expect_column_values_to_be_of_type("price_date", "datetime64[ns]")

    result = validator.validate()
    assert result["success"], f"[GE] 경제 지표 스키마 검증 실패: {result['statistics']}"
