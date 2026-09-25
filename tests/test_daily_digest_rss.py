"""전문 매체 RSS 수집 — Google News 검색 프록시(Reuters·AP) 파싱·키워드 필터 단위 테스트.

2026-09-13 (A-259) 확장: 3단 폴백 체인(Google News → GDELT DOC 2.0 → Bing News → 원문)의
슬롯 순서·승자 규칙(관련 기사 ≥1건을 낸 첫 채널)·채널 라벨·중복 링크 제거·헬퍼 인코딩.
"""
from __future__ import annotations

import sys
from datetime import date, datetime, timezone
from email.utils import format_datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import daily_unstructured_digest as dg  # noqa: E402

_GNEWS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>"soybean" - Google News</title>
<item><title>Soybean oil futures rise as biodiesel demand firms - Reuters</title>
<link>https://news.google.com/rss/articles/abc</link>
<pubDate>{d}</pubDate><description>Soyoil gained on RVO expectations.</description></item>
<item><title>Local election results - Reuters</title>
<link>https://news.google.com/rss/articles/def</link>
<pubDate>{d}</pubDate><description>Unrelated politics.</description></item>
</channel></rss>"""

# 무관 기사만 있는 피드 — 구 규칙('항목이 있는 첫 URL')이면 이 채널이 승리해 폴백을 가렸다
_IRRELEVANT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>x</title>
<item><title>Local election results - Reuters</title>
<link>https://news.google.com/rss/articles/def</link>
<pubDate>{d}</pubDate><description>Unrelated politics.</description></item>
</channel></rss>"""

# Bing News RSS — 동일 링크 중복 2건 + 무관 1건
_BING_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>site:reuters.com soybean - Bing News</title>
<item><title>Palm oil slips as soybean oil weakens</title>
<link>https://www.reuters.com/markets/commodities/palm-1</link>
<pubDate>{d}</pubDate><description>Vegetable oil complex softer.</description></item>
<item><title>Palm oil slips as soybean oil weakens</title>
<link>https://www.reuters.com/markets/commodities/palm-1</link>
<pubDate>{d}</pubDate><description>Vegetable oil complex softer.</description></item>
<item><title>Sports roundup</title>
<link>https://www.reuters.com/sports/x</link>
<pubDate>{d}</pubDate><description>Football.</description></item>
</channel></rss>"""

_CODES = ["RSS_REUTERS_COMMODITIES", "RSS_REUTERS_CLIMATE_ENERGY",
          "RSS_AP_COMMODITIES", "RSS_AP_WORLD"]


class _Resp:
    def __init__(self, content: bytes, status: int = 200) -> None:
        self.content, self.status_code = content, status

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def _stamp() -> str:
    return format_datetime(datetime.now(timezone.utc))


def _gdelt_seendate() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _canned_gdelt() -> dict:
    d = _gdelt_seendate()
    return {"articles": [
        {"url": "https://www.reuters.com/markets/commodities/soyoil-1",
         "title": "Argentina export tax cut lifts soybean oil shipments",
         "seendate": d, "domain": "reuters.com"},
        {"url": "https://www.reuters.com/world/politics-1",
         "title": "Parliament vote delayed", "seendate": d, "domain": "reuters.com"},
    ]}


def test_gnews_url_is_site_scoped_and_topic_filtered() -> None:
    url = dg._gnews("reuters.com", "(soybean OR soyoil)")
    assert url.startswith("https://news.google.com/rss/search?q=")
    assert "site%3Areuters.com" in url and "when%3A2d" in url and "soybean" in url


def test_reuters_ap_codes_registered_everywhere() -> None:
    codes = ["RSS_REUTERS_COMMODITIES", "RSS_REUTERS_CLIMATE_ENERGY",
             "RSS_AP_COMMODITIES", "RSS_AP_WORLD"]
    for c in codes:
        assert c in dg.RSS_SOURCES
        assert c in dg.DAILY_UNSTRUCTURED["전문 매체"]
        assert dg.RSS_SOURCES[c][0].startswith("https://news.google.com/rss/search")


def test_gnews_feed_parsed_with_keyword_gate(monkeypatch) -> None:
    from email.utils import format_datetime
    from datetime import datetime, timezone
    stamp = format_datetime(datetime.now(timezone.utc))
    calls: list[str] = []

    def fake_get(url, **kw):
        calls.append(url)
        if "news.google.com" in url and "reuters.com" in url and "commodities" not in url:
            return _Resp(_GNEWS_XML.format(d=stamp).encode())
        return _Resp(b"", 403)                     # 원문 섹션·타 매체는 차단 시뮬레이션

    monkeypatch.setattr(dg, "RSS_SOURCES", {
        "RSS_REUTERS_COMMODITIES": dg.RSS_SOURCES["RSS_REUTERS_COMMODITIES"]})
    import httpx
    monkeypatch.setattr(httpx, "get", fake_get)
    rows = dg._fetch_specialist_media()
    assert len(rows) == 1
    r = rows[0]
    assert r["indicator"] == "RSS_REUTERS_COMMODITIES" and r["value"] == 1   # 무관 기사 1건 제외
    assert "Soybean oil futures" in r["note"] and "news.google.com" in r["note"]
    assert r["date"] == str(date.today())
    assert calls and "news.google.com" in calls[0]                          # 1순위 = 프록시


# ── A-259 3단 폴백 체인 ─────────────────────────────────────────────────────────

def test_chain_order_for_reuters_ap_codes() -> None:
    """슬롯 0 = Google News(str) · 1 = GDELT dict(domain) · 2 = Bing RSS URL · 이후 원문."""
    for c in _CODES:
        chain = dg.RSS_SOURCES[c]
        domain = "reuters.com" if "REUTERS" in c else "apnews.com"
        assert isinstance(chain[0], str) and chain[0].startswith("https://news.google.com/rss")
        assert isinstance(chain[1], dict) and chain[1]["gdelt"]["domain"] == domain
        assert isinstance(chain[2], str) and chain[2].startswith("https://www.bing.com/news/search")
        assert "format=rss" in chain[2] and f"site%3A{domain}" in chain[2]
        assert all(_c in ("gnews", "gdelt", "bing", "raw")
                   for _c in map(dg._channel_of, chain))
        assert [dg._channel_of(e) for e in chain[:3]] == ["gnews", "gdelt", "bing"]
        assert all(dg._channel_of(e) == "raw" for e in chain[3:])


def test_gdelt_fallback_fires_only_when_rss_yields_nothing(monkeypatch) -> None:
    """Google News 403 → GDELT 응답(관련 1·무관 1) → 1행·값 1·[채널: GDELT]·domain: 질의."""
    import httpx
    seen_params: list[dict] = []
    sleeps: list[float] = []

    def fake_get(url, **kw):
        return _Resp(b"", 403)

    def fake_gdelt(params):
        seen_params.append(dict(params))
        return _canned_gdelt()

    monkeypatch.setattr(dg, "RSS_SOURCES", {
        "RSS_REUTERS_COMMODITIES": dg.RSS_SOURCES["RSS_REUTERS_COMMODITIES"]})
    monkeypatch.setattr(dg, "_GDELT_CALLS", 0)
    monkeypatch.setattr(httpx, "get", fake_get)
    monkeypatch.setattr(dg, "_gdelt_get_json", fake_gdelt)
    monkeypatch.setattr(dg.time, "sleep", lambda s: sleeps.append(s))
    rows = dg._fetch_specialist_media()
    assert len(rows) == 1
    r = rows[0]
    assert r["indicator"] == "RSS_REUTERS_COMMODITIES" and r["value"] == 1
    assert r["note"].startswith("[채널: GDELT")
    assert "Argentina export tax" in r["note"] and "soyoil-1" in r["note"]
    assert r["date"] == str(date.today()) and r["source"] == "rss_reuters_commodities"
    assert len(seen_params) == 1
    p = seen_params[0]
    assert p["query"].startswith("domain:reuters.com ") and p["mode"] == "artlist"
    assert p["format"] == "json" and p["timespan"] == "2d"
    assert p["maxrecords"] == "25" and p["sort"] == "DateDesc"
    assert sleeps == []                        # 프로세스 첫 GDELT 호출은 대기 없음


def test_gdelt_paced_six_seconds_between_calls(monkeypatch) -> None:
    import httpx
    sleeps: list[float] = []
    monkeypatch.setattr(dg, "RSS_SOURCES", {c: dg.RSS_SOURCES[c] for c in _CODES[:2]})
    monkeypatch.setattr(dg, "_GDELT_CALLS", 0)
    monkeypatch.setattr(httpx, "get", lambda url, **kw: _Resp(b"", 403))
    monkeypatch.setattr(dg, "_gdelt_get_json", lambda params: _canned_gdelt())
    monkeypatch.setattr(dg.time, "sleep", lambda s: sleeps.append(s))
    rows = dg._fetch_specialist_media()
    # A-274: 두 채널이 같은 기사(동일 제목)를 내면 뒤 채널에서는 제거되므로 행은 1건 — 호출·대기는 그대로 2회·[6]
    assert len(rows) == 1 and sleeps == [6]    # 두 번째 GDELT 호출 앞에서만 6초


def test_gdelt_not_called_when_gnews_relevant(monkeypatch) -> None:
    import httpx
    called: list[dict] = []

    def fake_get(url, **kw):
        if "news.google.com" in url:
            return _Resp(_GNEWS_XML.format(d=_stamp()).encode())
        return _Resp(b"", 403)

    monkeypatch.setattr(dg, "RSS_SOURCES", {
        "RSS_REUTERS_COMMODITIES": dg.RSS_SOURCES["RSS_REUTERS_COMMODITIES"]})
    monkeypatch.setattr(httpx, "get", fake_get)
    monkeypatch.setattr(dg, "_gdelt_get_json", lambda p: called.append(p) or _canned_gdelt())
    rows = dg._fetch_specialist_media()
    assert len(rows) == 1 and rows[0]["note"].startswith("[채널: Google News")
    assert called == []


def test_irrelevant_only_channel_does_not_block_fallback(monkeypatch) -> None:
    """승자 규칙 변경 검증 — 무관 기사만 있는 Google News 는 GDELT 폴백을 가리지 않는다."""
    import httpx

    def fake_get(url, **kw):
        if "news.google.com" in url:
            return _Resp(_IRRELEVANT_XML.format(d=_stamp()).encode())
        return _Resp(b"", 403)

    monkeypatch.setattr(dg, "RSS_SOURCES", {
        "RSS_REUTERS_COMMODITIES": dg.RSS_SOURCES["RSS_REUTERS_COMMODITIES"]})
    monkeypatch.setattr(dg, "_GDELT_CALLS", 0)
    monkeypatch.setattr(httpx, "get", fake_get)
    monkeypatch.setattr(dg, "_gdelt_get_json", lambda p: _canned_gdelt())
    monkeypatch.setattr(dg.time, "sleep", lambda s: None)
    rows = dg._fetch_specialist_media()
    assert len(rows) == 1 and rows[0]["note"].startswith("[채널: GDELT")


def test_bing_slot_parsed_with_duplicate_links_deduped(monkeypatch) -> None:
    """Google News 403 · GDELT 빈 응답 → Bing RSS 승리, 중복 링크 1건 제거·무관 1건 제외."""
    import httpx

    def fake_get(url, **kw):
        if "bing.com" in url and "format=rss" in url:
            return _Resp(_BING_XML.format(d=_stamp()).encode())
        return _Resp(b"", 403)

    monkeypatch.setattr(dg, "RSS_SOURCES", {
        "RSS_REUTERS_COMMODITIES": dg.RSS_SOURCES["RSS_REUTERS_COMMODITIES"]})
    monkeypatch.setattr(dg, "_GDELT_CALLS", 0)
    monkeypatch.setattr(httpx, "get", fake_get)
    monkeypatch.setattr(dg, "_gdelt_get_json", lambda p: {})
    monkeypatch.setattr(dg.time, "sleep", lambda s: None)
    rows = dg._fetch_specialist_media()
    assert len(rows) == 1
    r = rows[0]
    assert r["value"] == 1 and r["note"].startswith("[채널: Bing News")
    assert r["note"].count("palm-1") == 1 and "Sports" not in r["note"]


def test_helpers_gdelt_channel_bing_encoding() -> None:
    spec = dg._gdelt("apnews.com", "(soybean OR \"palm oil\")")
    assert spec == {"gdelt": {"domain": "apnews.com", "topic": "(soybean OR \"palm oil\")",
                              "timespan": "2d"}}
    assert dg._gdelt("reuters.com", "x", timespan="1d")["gdelt"]["timespan"] == "1d"
    assert dg._channel_of(spec) == "gdelt"
    assert dg._channel_of("https://news.google.com/rss/search?q=x") == "gnews"
    assert dg._channel_of("https://www.bing.com/news/search?q=x&format=rss") == "bing"
    assert dg._channel_of("https://www.reuters.com/markets/commodities/") == "raw"
    assert dg._channel_of("https://apnews.com/world-news") == "raw"
    assert dg._channel_of("https://farmdocdaily.illinois.edu/feed") == "rss"
    url = dg._bing("reuters.com", "(soybean OR soyoil)")
    assert url.startswith("https://www.bing.com/news/search?q=site%3Areuters.com+")
    assert url.endswith("&format=rss") and "soyoil" in url
    # 표준 RSS 파서·필터 헬퍼 — 2일 컷오프 밖 항목 제외
    items = dg._items_from_rss(_BING_XML.format(d=_stamp()).encode())
    assert len(items) == 3 and items[0]["link"].endswith("palm-1")
    import pandas as pd
    far = pd.Timestamp(date.today()) + pd.Timedelta(days=1)
    assert dg._filter_items(items, far) == []
    kept = dg._filter_items(items, pd.Timestamp(date.today()) - pd.Timedelta(days=2))
    assert [i["link"] for i in kept] == ["https://www.reuters.com/markets/commodities/palm-1"]


def test_gdelt_failure_is_non_fatal_and_continues_chain(monkeypatch) -> None:
    """GDELT 헬퍼 예외 → 경고 후 다음 채널(Bing)로 계속."""
    import httpx

    def fake_get(url, **kw):
        if "bing.com" in url:
            return _Resp(_BING_XML.format(d=_stamp()).encode())
        return _Resp(b"", 403)

    def boom(params):
        raise RuntimeError("simulated")

    monkeypatch.setattr(dg, "RSS_SOURCES", {
        "RSS_AP_WORLD": dg.RSS_SOURCES["RSS_AP_WORLD"]})
    monkeypatch.setattr(dg, "_GDELT_CALLS", 0)
    monkeypatch.setattr(httpx, "get", fake_get)
    monkeypatch.setattr(dg, "_gdelt_get_json", boom)
    monkeypatch.setattr(dg.time, "sleep", lambda s: None)
    rows = dg._fetch_specialist_media()
    assert len(rows) == 1 and rows[0]["note"].startswith("[채널: Bing News")
