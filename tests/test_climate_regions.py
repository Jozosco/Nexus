"""산지 설정(config/production_regions.yaml)·Open-Meteo 예보 층·as-of 정합 검증 (2026-09-13).

샌드박스 프록시가 open-meteo 호스트를 차단하므로 httpx는 전부 합성 응답으로 대체한다.
"""
from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import pytest

from src.pipeline.asof import attach_asof, revision_status, rule_for
from src.pipeline.connectors import climate_connector as cc

REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "config" / "production_regions.yaml"
CODE_RE = re.compile(r"^[A-Z]{2}_[A-Za-z]+$")

# 정본 좌표 표 §3.2 (docs/research_desk/_reference/soybean_oil_production_climate.md)
CANONICAL_TIER1: dict[str, tuple[float, float]] = {
    "CN_Heilongjiang": (48.0, 128.0), "CN_Shandong": (36.5, 118.0), "CN_Jiangsu": (32.5, 120.0),
    "US_Illinois": (40.0, -89.0), "US_Iowa": (42.0, -93.5), "US_Indiana": (40.2, -86.1),
    "BR_MatoGrosso": (-13.0, -56.0), "BR_Parana": (-24.5, -51.5),
    "BR_MatoGrossodoSul": (-20.0, -54.5), "AR_Cordoba": (-31.4, -64.2),
    "AR_SantaFe": (-33.0, -60.6), "AR_BuenosAires": (-36.0, -60.0),
}
TIER2_CODES = {
    "BR_RioGrandedoSul", "BR_Goias", "US_Minnesota", "US_Nebraska", "US_Ohio",
    "PY_AltoParana", "IN_MadhyaPradesh", "MY_Sabah", "MY_Johor", "ID_Riau",
    "ID_CentralKalimantan",
}


@pytest.fixture(scope="module")
def regions() -> dict[str, dict]:
    return cc.load_production_regions(CONFIG)


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cc.time, "sleep", lambda *_: None)


# ── 설정 파일 ──────────────────────────────────────────────────────────────────
def test_config_loads_23_regions(regions: dict[str, dict]) -> None:
    assert len(regions) == 23
    tiers = [int(i["tier"]) for i in regions.values()]
    assert tiers.count(1) == 12 and tiers.count(2) == 11


def test_tier1_confirmed_with_canonical_coords(regions: dict[str, dict]) -> None:
    t1 = {c: i for c, i in regions.items() if int(i["tier"]) == 1}
    assert set(t1) == set(CANONICAL_TIER1)
    for code, (lat, lon) in CANONICAL_TIER1.items():
        assert t1[code]["coord_status"] == "CONFIRMED", code
        assert (t1[code]["lat"], t1[code]["lon"]) == (lat, lon), code
        assert t1[code]["crop"] == "soy"


def test_tier2_inference(regions: dict[str, dict]) -> None:
    t2 = {c: i for c, i in regions.items() if int(i["tier"]) == 2}
    assert set(t2) == TIER2_CODES
    assert all(i["coord_status"] == "INFERENCE" for i in t2.values())
    assert {i["crop"] for i in t2.values()} == {"soy", "palm"}
    assert all(i["crop"] == "palm" for c, i in t2.items() if c[:2] in ("MY", "ID"))


def test_codes_unique_and_pattern(regions: dict[str, dict]) -> None:
    codes = list(regions)
    assert len(codes) == len(set(codes))
    assert all(CODE_RE.match(c) for c in codes), [c for c in codes if not CODE_RE.match(c)]


def test_builtin_tier1_matches_config(regions: dict[str, dict]) -> None:
    # 내장 폴백 dict가 설정 파일 tier1과 어긋나면 폴백 시 좌표가 조용히 바뀐다
    for code, info in cc._BUILTIN_REGIONS.items():
        assert (info["lat"], info["lon"]) == (regions[code]["lat"], regions[code]["lon"]), code


def test_minimal_parser_matches_yaml(regions: dict[str, dict]) -> None:
    # pyyaml 부재 CI 경로: 최소 파서가 동일 결과를 내야 tier2가 조용히 사라지지 않는다
    entries = cc._parse_regions_minimal(CONFIG.read_text(encoding="utf-8"))
    parsed = {e["code"]: e for e in entries}
    assert set(parsed) == set(regions)
    for code, info in regions.items():
        got = (float(parsed[code]["lat"]), float(parsed[code]["lon"]))
        assert got == (info["lat"], info["lon"]), code
        assert int(parsed[code]["tier"]) == info["tier"]
        assert parsed[code]["coord_status"] == info["coord_status"]


def test_fallback_on_missing_path(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out = cc.load_production_regions(tmp_path / "missing.yaml")
    assert len(out) == 12 and set(out) == set(cc._BUILTIN_REGIONS)
    assert all(i["tier"] == 1 for i in out.values())
    assert "[경고]" in capsys.readouterr().out


def test_fallback_on_parse_error(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("regions:\n  - code: X_Y\n    lat: 1.0\n", encoding="utf-8")  # lon 누락
    assert len(cc.load_production_regions(bad)) == 12


def test_climate_tier_env_filters(monkeypatch: pytest.MonkeyPatch,
                                  regions: dict[str, dict]) -> None:
    monkeypatch.setenv("CLIMATE_TIER", "1")
    assert len(cc._select_regions(regions)) == 12
    monkeypatch.setenv("CLIMATE_TIER", "all")
    assert len(cc._select_regions(regions)) == 23


# ── 예보 층 ────────────────────────────────────────────────────────────────────
class _Resp:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


def _synthetic_forecast(days: int = 15) -> dict:
    start = date.today()
    times = [(start + timedelta(days=i)).isoformat() for i in range(days)]
    return {"daily": {"time": times, **{v: [float(i) for i in range(days)]
                                        for v in cc.FORECAST_VARS}}}


@pytest.fixture
def forecast_df(monkeypatch: pytest.MonkeyPatch, regions: dict[str, dict]) -> pd.DataFrame:
    calls: list[dict] = []

    def _fake_get(url: str, params: dict | None = None, timeout: float = 0) -> _Resp:
        assert url == cc.OPEN_METEO_FORECAST_BASE
        calls.append(params or {})
        return _Resp(_synthetic_forecast())

    monkeypatch.setattr(cc.httpx, "get", _fake_get)
    monkeypatch.delenv("CLIMATE_TIER", raising=False)
    two = {c: regions[c] for c in ("BR_MatoGrosso", "MY_Sabah")}
    df = cc.fetch_openmeteo_forecast(two, forecast_days=15)
    assert len(calls) == 2 and all(p["timezone"] == "UTC" for p in calls)
    return df


def test_forecast_rows_shape(forecast_df: pd.DataFrame) -> None:
    assert "FCST_precipitation_sum_BR_MatoGrosso" in set(forecast_df["indicator_code"])
    assert len(forecast_df) == 2 * len(cc.FORECAST_VARS) * 15
    per = forecast_df.groupby(["region_code", "indicator_code"]).size()
    assert (per == 15).all()
    assert (forecast_df["price_date"] >= pd.Timestamp(date.today())).all()
    assert (forecast_df["price_date"] > pd.Timestamp(date.today())).sum() == 2 * 5 * 14
    assert forecast_df["source_name"].eq(cc.FORECAST_SOURCE_NAME).all()
    assert forecast_df["note"].str.startswith(f"issue_date={date.today().isoformat()}").all()


def test_forecast_asof_no_future_availability(forecast_df: pd.DataFrame) -> None:
    out = attach_asof(forecast_df, source="CLIMATE")
    ing = pd.to_datetime(out["ingested_at"]).dt.tz_localize(None)
    assert (out["available_at"] <= ing).all(), "예보 행 available_at이 수집 시각을 넘음"
    fut = out[out["event_time"] > ing]
    assert len(fut) == 2 * 5 * 14
    assert (fut["available_at"] == ing[fut.index]).all()
    assert out["vintage_known"].all() and out["source_vintage"].eq(date.today().isoformat()).all()


def test_fcst_rules_registered() -> None:
    rule = rule_for("FCST_precipitation_sum_BR_MatoGrosso")
    assert rule.kind == "immediate" and rule.lag_days == 0 and rule.revises
    assert revision_status("FCST_temperature_2m_max_US_Iowa") == "full"
    # 기존 아카이브 규칙은 그대로(lag 6)
    assert rule_for("precipitation_sum_BR_MatoGrosso").lag_days == 6


def test_forecast_region_failure_is_nonfatal(monkeypatch: pytest.MonkeyPatch,
                                             regions: dict[str, dict]) -> None:
    def _flaky(url: str, params: dict | None = None, timeout: float = 0) -> _Resp:
        if params and params["latitude"] == regions["MY_Sabah"]["lat"]:
            raise RuntimeError("synthetic 429")
        return _Resp(_synthetic_forecast())

    monkeypatch.setattr(cc.httpx, "get", _flaky)
    monkeypatch.setattr(cc, "_fetch", lambda url, params=None, max_retries=4: _flaky(url, params))
    two = {c: regions[c] for c in ("BR_MatoGrosso", "MY_Sabah")}
    df = cc.fetch_openmeteo_forecast(two)
    assert set(df["region_code"]) == {"BR_MatoGrosso"}
