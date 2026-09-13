"""전문 매체 RSS 수집 — Google News 검색 프록시(Reuters·AP) 파싱·키워드 필터 단위 테스트."""
from __future__ import annotations

import sys
from datetime import date
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


class _Resp:
    def __init__(self, content: bytes, status: int = 200) -> None:
        self.content, self.status_code = content, status

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


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
