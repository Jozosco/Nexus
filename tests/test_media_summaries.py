"""A-269 — 매체 키워드 오탐·요약 보존·프록시 행 파싱·영문 소스명."""
from __future__ import annotations

import pandas as pd

from scripts import daily_unstructured_digest as dg
from src.reporting.daily_brief import _RSS_ORG_EN, _media_items, _media_title, _parse_kv


def test_korean_false_positives_blocked():
    assert dg._match_keyword("[제42회 신한동해오픈] 1R. 공동 선두 오호리 유지로", "골프", "RSS_CLIMATEPOL") is None
    assert dg._match_keyword("Lettuce Talk About Food Safety", "consumer safety outbreaks", "RSS_FARMDOC_DAILY") is None
    assert dg._match_keyword("정전돼도 72시간 버틴다", "대두유 언급은 본문에만", "RSS_CLIMATEPOL") is None   # 국문 매체는 제목 필수
    assert dg._match_keyword("국내 SAF 의무화 논의", "", "RSS_CLIMATEPOL") == "saf"
    assert dg._match_keyword("바이오디젤 혼합 의무 상향", "", "RSS_CLIMATEPOL") == "바이오디젤"
    assert dg._match_keyword("Attack damages Bunge oilseeds plant", "", "RSS_WORLD_GRAIN") == "oilseed"
    # 범용어(tariff)는 농산물 맥락 없이는 통과 불가 — 실측 오탐(AP 아이리시 위스키 관세)
    assert dg._match_keyword("Trump says he's lifting a 10% tariff on Irish whiskey", "", "RSS_AP_COMMODITIES") is None
    assert dg._match_keyword("Iranian media say 1 killed in ship strike on the Strait of Hormuz", "", "RSS_AP_WORLD") == "hormuz"
    assert dg._match_keyword("US tariff on soybean oil imports raised", "", "RSS_REUTERS_COMMODITIES") == "soybean"


def test_rss_items_keep_description_and_atom():
    rss = b"""<rss><channel><item><title>Soyoil rises</title><link>https://x.y/a</link>
    <description><![CDATA[<p>Soybean oil futures <b>gained</b> on biodiesel demand.</p>]]></description>
    <pubDate>Mon, 14 Sep 2026 06:00:00 GMT</pubDate></item></channel></rss>"""
    it = dg._items_from_rss(rss)[0]
    assert it["desc"] == "Soybean oil futures gained on biodiesel demand."
    atom = b"""<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Palm oil slips</title>
    <link href="https://x.y/b"/><summary>Vegetable oil complex softer.</summary><updated>2026-09-14T06:00:00Z</updated></entry></feed>"""
    at = dg._items_from_rss(atom)[0]
    assert at["link"] == "https://x.y/b" and at["desc"].startswith("Vegetable oil")


def test_filter_records_keyword_and_note_budget():
    items = [{"title": "Soyoil rises", "link": "https://x.y/a", "desc": "d", "date": pd.Timestamp("2026-09-14")}]
    kept = dg._filter_items(items, pd.Timestamp("2026-09-12"), "RSS_WORLD_GRAIN")
    assert kept and kept[0]["_kw"] == "soy oil" or kept[0]["_kw"] == "soyoil"
    assert dg.NOTE_BUDGET >= 900


def test_parse_kv_and_media_title():
    note = ("[PERPLEXITY-PROXY: 아르헨티나 대두유 수출세] RATE: **22.5%**   CHANGE: **unchanged**   "
            "DATE: **December 9, 2025**   SOURCE: **Buenos Aires Herald**  Context and basis: ...")
    kv = _parse_kv(note)
    assert kv[0] == ("세율", "22.5%") and ("변동", "변동 없음") in kv
    t = _media_title(note, "ARG_EXPORT_TAX_NEWS")
    assert t.startswith("세율 22.5% · 변동 변동 없음") and "**" not in t and "Context" not in t
    assert _media_title("[QUALITATIVE:HIGH]", "HORMUZ_THREAT_LEVEL") == "정성 판정 높음"
    prose = "[PERPLEXITY-PROXY: USDA WASDE 컨센서스] USDA's latest WASDE page shows the next report.[1][3] For that report, public data provide detail"
    out = _media_title(prose, "WASDE_CONSENSUS_SCORE", n=60)
    assert "[1]" not in out and len(out) <= 62 and out.endswith("…")


def test_media_items_split_and_english_org_names():
    note = "[채널: 공식 RSS · kw:soybean] Bunge plant hit — Attack damages plant. (https://a.b/1) ⋅ ADM biofuels — Margins improve. (https://a.b/2)"
    items = _media_items(note)
    assert len(items) == 2 and items[1]["url"] == "https://a.b/2" and items[0]["desc"] == "Attack damages plant."
    cut = _media_items("[채널: 공식 RSS] Iranian media say 1 killed - apnews.com (https://apnews.com/arti")
    assert cut[0]["title"].endswith("apnews.com") and "(" not in cut[0]["title"]
    assert _media_title(note, "RSS_WORLD_GRAIN").startswith("Bunge plant hit")
    assert _RSS_ORG_EN["RSS_TFM"] == "Total Farm Marketing" and _RSS_ORG_EN["RSS_CLIMATEPOL"].startswith("Climatepol")
