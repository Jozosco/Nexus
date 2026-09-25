"""A-273/A-274 — 지정학 동향 레인·게이트 강화·중복 제거·팜유 원천 분리·도착가 원천 탐색."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import pytest

from scripts import daily_unstructured_digest as dg
from src.reporting import daily_brief as db


def test_geo_lane_gate_passes_without_agri_context():
    assert dg._match_keyword("Iran threatens Hormuz closure - Reuters", "", "RSS_REUTERS_GEO") == "iran"
    assert dg._match_keyword("CIA director says Russia is testing EU resolve", "", "RSS_AP_GEO") == "cia"
    assert dg._match_keyword("US strikes Iranian military sites", "", "RSS_AP_GEO") == "iranian"
    # 지정학 레인이라도 무관 기사는 탈락
    assert dg._match_keyword("Brook hits lightning century as England crush Sri Lanka", "", "RSS_REUTERS_GEO") is None
    # 기존 농산물 레인에서는 여전히 맥락어 필요 — 회귀 방지
    assert dg._match_keyword("Iran threatens Hormuz closure - Reuters", "", "RSS_AP_WORLD") is None
    assert dg._match_keyword("Iran threatens to close Strait of Hormuz", "", "RSS_AP_WORLD") == "hormuz"


def test_agri_gate_tightened_against_false_positives():
    # 'crush'(크리켓)·'el niño'(보건)·'oil'(원유 정책)은 농산물 맥락 없이는 탈락
    assert dg._match_keyword("Brook hits lightning century as England crush Sri Lanka", "", "RSS_REUTERS_COMMODITIES") is None
    assert dg._match_keyword("Super El Nino could cause 451,000 excess deaths", "health study", "RSS_REUTERS_CLIMATE_ENERGY") is None
    assert dg._match_keyword("South Korea plans to cut its reliance on Middle East crude oil", "", "RSS_REUTERS_COMMODITIES") is None
    # 정당한 기사는 통과
    assert dg._match_keyword("Soybean crush margins widen on renewable diesel demand", "", "RSS_REUTERS_COMMODITIES") == "soybean"
    assert dg._match_keyword("El Nino threatens Malaysian palm oil output", "", "RSS_REUTERS_CLIMATE_ENERGY") == "palm oil"
    assert dg._match_keyword("Traders nervous ahead of EPA RVO decision on biofuel", "", "RSS_REUTERS_CLIMATE_ENERGY") == "rvo"   # 단어 경계 RVO
    assert dg._match_keyword("Markets nervous about oil demand", "", "RSS_REUTERS_CLIMATE_ENERGY") is None   # 'rvo' 부분 일치 차단


def test_filter_dedupes_same_article_across_channels_and_caps_geo_lane():
    seen: set[str] = set()
    d = pd.Timestamp("2026-09-25")
    items_a = [{"title": "Iran claims it struck an oil tanker in the Strait of Hormuz - AP News", "link": "https://a/1",
                "desc": "", "date": d}]
    items_b = [{"title": "Iran claims it struck an oil tanker in the Strait of Hormuz | AP News", "link": "https://b/1",
                "desc": "", "date": d}]
    k1 = dg._filter_items(items_a, d - pd.Timedelta(days=2), "RSS_AP_WORLD", seen)
    k2 = dg._filter_items(items_b, d - pd.Timedelta(days=2), "RSS_AP_COMMODITIES", seen)
    assert len(k1) == 1 and k2 == []
    many = [{"title": f"Iran sanctions story {i}", "link": f"https://g/{i}", "desc": "", "date": d} for i in range(6)]
    assert len(dg._filter_items(many, d - pd.Timedelta(days=2), "RSS_REUTERS_GEO")) == dg._GEO_LANE_CAP


def test_geo_codes_registered_everywhere():
    for c in ("US_IRAN_CONFLICT_STATUS", "RUSSIA_EU_RELATIONS_STATUS", "RSS_REUTERS_GEO", "RSS_AP_GEO"):
        assert c in dg.DAILY_UNSTRUCTURED["지정학 동향"]
        assert c in db._ONTOLOGY_CHAINS and c in db._GEO_CODES
    assert "RSS_REUTERS_GEO" in dg.RSS_SOURCES and dg.RSS_SOURCES["RSS_AP_GEO"][0].startswith("https://news.google.com/rss/search")
    assert "GPR_QUALITATIVE" in dg.DAILY_UNSTRUCTURED["지정학 위험"]
    assert "AIS_HORMUZ_TANKER_COUNT" in dg.DAILY_UNSTRUCTURED["해협 탱커"]
    # 대두유 가격 방향 서술 금지(흑해·제재는 후보 경로) — 체인 마지막 노드가 '검증 대기'
    assert db._ONTOLOGY_CHAINS["RUSSIA_EU_RELATIONS_STATUS"][-1] == "검증 대기"


def test_geo_cards_render_and_dedupe(tmp_path):
    rows = [
        {"date": "2026-09-25", "indicator": "US_IRAN_CONFLICT_STATUS", "category": "지정학 동향", "value": 3.0,
         "note": "[PERPLEXITY-PROXY: 미국–이란 분쟁 상태] LEVEL: HIGH | KEY_EVENT: On Sep 24 Iran fired on a tanker near Hormuz | HORMUZ_IMPACT: transits reduced | SOURCE: Reuters | DATE: 2026-09-25",
         "source_name": "Perplexity/GeoEventProxy", "appended_at": ""},
        {"date": "2026-09-25", "indicator": "RUSSIA_EU_RELATIONS_STATUS", "category": "지정학 동향", "value": 3.0,
         "note": "[PERPLEXITY-PROXY: 러시아–EU 관계 상태] TENSION: HIGH | KEY_STATEMENT: CIA director said Russia is testing EU resolve (Sep 25) | SANCTIONS_ENERGY: none | BLACK_SEA_IMPACT: none | SOURCE: AP | DATE: 2026-09-25",
         "source_name": "Perplexity/GeoEventProxy", "appended_at": ""},
        {"date": "2026-09-25", "indicator": "RSS_REUTERS_GEO", "category": "지정학 동향", "value": 1,
         "note": "[채널: Google News · kw:hormuz] Hormuz vessel traffic falls to two - Reuters — Hormuz vessel traffic falls to two Reuters (https://x/1)",
         "source_name": "rss_reuters_geo", "appended_at": ""},
        {"date": "2026-09-25", "indicator": "RSS_AP_GEO", "category": "지정학 동향", "value": 1,
         "note": "[채널: Google News · kw:hormuz] Hormuz vessel traffic falls to two - AP News — Hormuz vessel traffic falls to two AP News (https://x/2)",
         "source_name": "rss_ap_geo", "appended_at": ""},
    ]
    sig = pd.DataFrame(rows)
    sig["date"] = pd.to_datetime(sig["date"])
    html = db._geo_cards_html(sig)
    assert html.count('class="tag">지정학 동향') == 3          # 프록시 2 + 매체 1(동일 기사 중복 제거)
    assert "미국–이란 분쟁 상태" in html and "러시아–EU 관계 상태" in html
    assert "핵심 사건" in html and "핵심 발언" in html and "CIA director" in html
    assert "검증 대기" in html
    assert not re.search(r"\b[A-Z]{2,}(?:_[A-Z0-9]{2,})+\b", re.sub(r"<[^>]+>", " ", html))   # 코드 노출 금지
    assert "예측" not in html and "확률" not in html


def test_geo_status_line_only_when_elevated():
    f = {"geo": pd.DataFrame({"indicator_code": ["US_IRAN_CONFLICT_STATUS", "RUSSIA_EU_RELATIONS_STATUS"],
                              "value": [3.0, 1.0], "price_date": ["2026-09-25", "2026-09-25"],
                              "note": ["x", "y"]})}
    line = db._geo_status_line(f)
    assert line.startswith("지정학 관찰: 미국–이란 분쟁 높음") and "러시아" not in line and "전망" not in line
    assert db._geo_status_line({"geo": f["geo"].assign(value=[1.0, 1.0])}) == ""


def test_palm_snapshot_sources_not_mixed():
    specs = {s["label"]: s["codes"] for s in db._snapshot_specs()}
    assert specs["팜유(말레이시아 선물, MYR/톤)"] == ["TE_PALM_OIL"]
    assert "CPO_USD_MT" in specs["팜유(달러/톤 환산)"] and "TE_PALM_OIL" not in specs["팜유(달러/톤 환산)"]


def test_landed_cost_finds_nested_session_parquet(tmp_path, monkeypatch):
    from src.forecasting import landed_cost as lc
    nested = tmp_path / "data/raw/data/raw"
    nested.mkdir(parents=True)
    df = pd.DataFrame({"indicator_code": ["CBOT_BO_CLOSE"] * 3, "value": [60.0, 61.0, 62.0],
                       "event_time": pd.to_datetime(["2026-09-22", "2026-09-23", "2026-09-24"])})
    df.to_parquet(nested / "cbot_session_close.parquet", index=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(lc, "CBOT_SESSION_PARQUET", Path("data/raw/cbot_session_close.parquet"))
    monkeypatch.setattr(lc, "GOLD_MART", Path("data/gold/feature_mart.parquet"))
    s, src, _ = lc.load_cbot_usd_mt()
    assert src.startswith("cbot_session_close.parquet") and abs(float(s.iloc[-1]) - 62.0 * lc.USC_LB_TO_USD_MT) < 1e-6


def test_no_specialist_jargon_in_smoke_brief():
    """A-275: 승인자 지시 — 비전문가 용어 교체 후 화면 회귀 방지(원장·스탬프·잔차층·몬테카를로·십분위·프록시·시점 정합·게이트 등)."""
    from tests.test_daily_brief_wording import _alerts, _frames, _importance, _status, _visible_text
    html = db.build_daily_brief(_frames(), _importance(), _alerts(True), _status(),
                                "2026-09-25T06:30:00", "1", "target_ret20", n_features=10)
    text = _visible_text(html)
    banned = ["원장", "스탬프", "락박스", "잔차층", "몬테카를로", "컨볼루션", "십분위", "프록시", "시점 정합",
              "파케이", "Databento", "레짐", "컨센서스", "서프라이즈", "모멘텀", "게이트", "협정세계시", "파이프라인",
              "리드타임", "모식도", "신뢰 스트립", "USc/lb", "MMT"]
    hits = [w for w in banned if w in text]
    assert not hits, f"비전문가 용어 잔존: {hits}"


def test_production_price_dates_normalized_across_tz(monkeypatch):
    """A-277: naive·tz-aware 혼합 프레임 concat 후 event_time 전량 NaT(런 #110) 회귀 방지."""
    from src.pipeline.connectors import production_connector as pc
    naive = pd.DataFrame({"price_date": pd.to_datetime(["2026-01-01", "2026-02-01"]),
                          "source_name": ["NASA_POWER"] * 2, "indicator_code": ["T2M_US"] * 2,
                          "value": [1.0, 2.0]})
    aware = pd.DataFrame({"price_date": pd.to_datetime(["2026-09-18", "2026-09-25"], utc=True),
                          "source_name": ["USDA_FAS_ESR"] * 2, "indicator_code": ["ESR_KR"] * 2,
                          "value": [3.0, 4.0]})
    strings = pd.DataFrame({"price_date": ["2025-01-01", "not-a-date"],
                            "source_name": ["FAOSTAT"] * 2, "indicator_code": ["PROD_BR"] * 2,
                            "value": [5.0, 6.0]})
    out = pc.normalize_price_dates([naive, aware, strings])
    assert str(out["price_date"].dtype).startswith("datetime64") and out["price_date"].dt.tz is None
    assert int(out["price_date"].isna().sum()) == 1            # 파싱 불가 문자열 1건만 NaT
    assert out.loc[out["source_name"] == "USDA_FAS_ESR", "price_date"].notna().all()
