"""A-284(2026-09-27) 브리프 재설계 회귀 테스트 — 승인자 검증 4건.

① 변동일 편차는 그 날짜 기준(원시 계열) — 날짜마다 다르고, 관측이 멀면 '당시 값 없음'
② 핵심 변인–기사 연결: 온톨로지 파생 키워드·연결 근거(에너지·ICE·관세청 포함), 단어 경계 매칭
③ 유사 시기–사례: 날짜 농축 AND 변수 관련성 필터, 변수→대두유 연결 설명
④ 한국어 헤드라인 note 규약(`ko ‖ 원제 — 요약`) 파싱·렌더
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.forecasting import analogue_g1 as ag
from src.reporting import daily_brief as db


@pytest.fixture
def frames_energy() -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(11)
    dates = pd.bdate_range("2025-11-03", periods=220)
    lvl = 2.0 + np.cumsum(rng.normal(0, 0.03, 220))
    lvl[150:160] += 0.6                                  # 2026년 중반 급등 구간
    daily = pd.DataFrame({"price_date": dates, "indicator_code": "TE_HEATING_OIL", "value": lvl})
    m_dates = pd.date_range("2020-01-01", "2026-07-01", freq="MS")
    monthly = pd.DataFrame({"price_date": m_dates, "indicator_code": "ONI",
                            "value": np.sin(np.arange(len(m_dates)) / 6)})
    return {"te": daily, "enso": monthly}


def test_display_z_differs_by_date(frames_energy) -> None:
    """검증 1: 변동일마다 편차가 달라야 하며 관측일이 조회일과 같아야 한다."""
    d1, d2 = pd.Timestamp("2026-06-02"), pd.Timestamp("2026-07-01")
    z1, why1 = db._display_z_at(frames_energy, "TE_HEATING_OIL", d1)
    z2, why2 = db._display_z_at(frames_energy, "TE_HEATING_OIL", d2)
    assert z1 is not None and z2 is not None and z1 != z2
    assert why1 == "2026-06-02" and why2 == "2026-07-01"


def test_display_z_honest_when_observation_far(frames_energy) -> None:
    """일별 계열이 5거래일 넘게 끊기면 '당시 값 없음' — 옛 값을 끌어오지 않는다."""
    z, why = db._display_z_at(frames_energy, "TE_HEATING_OIL", pd.Timestamp("2026-12-01"))
    assert z is None and "당시 값 없음" in why


def test_display_z_monthly_series_uses_frequency_aware_gap(frames_energy) -> None:
    """월별 계열(ENSO)은 한 달 안이면 직전 월값을 그 날짜의 편차로 인정한다(주기 인지 허용 간격)."""
    z, why = db._display_z_at(frames_energy, "ENSO_ONI", pd.Timestamp("2026-07-20"))
    assert z is not None and why == "2026-07-01"
    z2, why2 = db._display_z_at(frames_energy, "ENSO_ONI", pd.Timestamp("2026-11-20"))
    assert z2 is None and "당시 값 없음" in why2


def test_inflection_block_uses_frames_and_shows_distinct_z(frames_energy) -> None:
    pts = [{"i": 1, "no": "①", "date": pd.Timestamp("2026-06-02"), "chg": 3.1, "close": 70.0},
           {"i": 2, "no": "②", "date": pd.Timestamp("2026-07-01"), "chg": -3.2, "close": 68.0}]
    imp = pd.DataFrame({"변수": ["TE_HEATING_OIL"], "LASSO_계수": [0.0], "피어슨_r": [-0.3]})
    html = db._inflection_block(pts, imp, frames_energy)
    import re
    zs = re.findall(r"난방유 선물\(뉴욕\) ([+-]\d\.\d)", html)
    assert len(zs) == 2 and zs[0] != zs[1], html
    assert "그 날짜 기준" in html


def test_driver_keywords_and_edges_cover_energy_ice_customs() -> None:
    """검증 2: 에너지·ICE·관세청·WASDE 수출 변인이 키워드와 인과 경로(또는 정직 표기)를 가진다."""
    assert "난방유" in db._driver_keywords("TE_HEATING_OIL")
    assert any(e["id"] == "CE-020" for e in db._driver_edges("TE_HEATING_OIL"))
    assert "거래량" in db._driver_keywords("ICE_EU_OIL_PRODUCTS_OPTIONS")
    assert "베트남" in db._driver_keywords("KCS_1507901010_IMP_USD_WORLD")
    assert any(e["id"] == "CE-022" for e in db._driver_edges("WASDE_US_SBO_EXPORTS"))
    line = db._driver_link_line("TE_HEATING_OIL")
    assert "검증된 인과 경로" in line and "CE-" not in line          # 화면에 내부 코드 노출 금지
    assert "상관 기반 참고" in db._driver_link_line("TOTALLY_UNKNOWN_CODE")


def test_ontology_index_derives_keywords_from_semantic_layer() -> None:
    idx = db._ontology_index()
    assert "ENSO_ONI" in idx["code_keywords"] and "CE-006" in idx["edges"]
    assert any("엘니뇨" in k for k in db._driver_keywords("ENSO_ONI"))


def test_keyword_hits_use_word_boundary() -> None:
    """'diesel'이 'biodiesel'에 걸리지 않는다(변인–기사 오연결 차단)."""
    assert db._kw_hits(["diesel"], "Indonesia biodiesel B50 mandate") == 0
    assert db._kw_hits(["diesel"], "diesel crack spreads widen") == 1
    assert db._kw_hits(["option"], "options volume jumps") == 1
    assert db._kw_hits(["난방유"], "미국 난방유 재고 감소") == 1


def test_match_articles_picks_article_level_matches() -> None:
    sig = pd.DataFrame([{
        "date": pd.Timestamp("2026-09-26"), "indicator": "RSS_REUTERS_COMMODITIES",
        "note": "[채널: Google News] Cricket team crush rivals — sports (https://x/1) ⋅ "
                "미 난방유 선물 급등 ‖ US heating oil futures jump on refinery outage — distillate stocks fall (https://x/2)",
        "source_name": "rss_reuters_commodities"}])
    arts = db._match_articles("TE_HEATING_OIL", sig)
    assert arts and arts[0]["url"] == "https://x/2" and arts[0]["ko"] == "미 난방유 선물 급등"


def test_pick_signals_around_prefers_media_and_changed_proxies(tmp_path, monkeypatch) -> None:
    """검증 1 ②: 매일 반복되는 동일 검색 요약은 제외, 매체 기사 우선."""
    csv = tmp_path / "sig.csv"
    rows = []
    for d in ("2026-08-25", "2026-08-26", "2026-08-27", "2026-08-28"):
        rows.append({"date": d, "indicator": "ARG_EXPORT_TAX_NEWS", "category": "정책 뉴스", "value": 22.5,
                     "note": "[PERPLEXITY-PROXY: 수출세] RATE: 22.5% | CHANGE: unchanged | DATE: 2026-06-03 | SOURCE: x",
                     "source_name": "Perplexity/PolicyProxy", "appended_at": ""})
    rows.append({"date": "2026-08-28", "indicator": "INDIA_DUTY_NEWS", "category": "정책 뉴스", "value": 12.5,
                 "note": "[PERPLEXITY-PROXY: 인도 관세] DUTY_RATE: 12.5% | CHANGE: cut | DATE: 2026-08-28 | SOURCE: y",
                 "source_name": "Perplexity/PolicyProxy", "appended_at": ""})
    rows.append({"date": "2026-08-27", "indicator": "INDIA_DUTY_NEWS", "category": "정책 뉴스", "value": 20.0,
                 "note": "[PERPLEXITY-PROXY: 인도 관세] DUTY_RATE: 20% | CHANGE: none | DATE: 2026-08-01 | SOURCE: y",
                 "source_name": "Perplexity/PolicyProxy", "appended_at": ""})
    rows.append({"date": "2026-08-28", "indicator": "RSS_WORLD_GRAIN", "category": "전문 매체", "value": 1,
                 "note": "[채널: 원문] 미 난방유 급등 ‖ Heating oil rallies on refinery fire — distillate (https://wg/1)",
                 "source_name": "rss_world_grain", "appended_at": ""})
    pd.DataFrame(rows).to_csv(csv, index=False)
    monkeypatch.setattr(db, "SIGNALS_CSV", csv)
    picks = db._pick_signals_around(pd.Timestamp("2026-08-28"), db._driver_keywords("TE_HEATING_OIL"))
    assert picks and picks[0]["indicator"] == "RSS_WORLD_GRAIN" and picks[0]["title"] == "미 난방유 급등"
    assert all(p["indicator"] != "ARG_EXPORT_TAX_NEWS" for p in picks)      # 값 불변 반복 요약 제외
    assert any(p["indicator"] == "INDIA_DUTY_NEWS" for p in picks)          # 값이 바뀐 요약은 채택


def test_case_relatedness_filter() -> None:
    """검증 3: 난방유는 아르헨 가뭄 사례와 무관, 복합 위기 사례와는 관련."""
    assert not ag.case_related_to("사례 ④ · 2022-23 아르헨 가뭄", "TE_HEATING_OIL")
    assert ag.case_related_to("사례 ③ · 2021-22 복합 위기", "TE_HEATING_OIL")
    assert ag.case_related_to("사례 ④ · 2022-23 아르헨 가뭄", "ENSO_ONI")
    assert ag.case_related_to("사례 ② · 2012 미국 대가뭄", "PRECTOTCORR_Iowa")


def test_case_badges_require_variable_relatedness() -> None:
    days = pd.DatetimeIndex(pd.bdate_range("2022-12-05", "2023-04-20", freq="10B"))   # 아르헨 가뭄 창 안에 몰림
    sample = pd.bdate_range("2010-01-01", "2025-12-31")
    plain = ag.case_badges_for(days, sample)
    assert any("아르헨" in b for b in plain)
    assert not ag.case_badges_for(days, sample, var_code="TE_HEATING_OIL")
    assert any("아르헨" in b for b in ag.case_badges_for(days, sample, var_code="ENSO_ONI"))
    only = ag.date_only_case_badges(days, sample, "TE_HEATING_OIL")
    assert any("아르헨" in b for b in only)


def test_analogue_uses_current_override_and_link_line() -> None:
    rng = np.random.default_rng(3)
    idx = pd.bdate_range("2015-01-01", periods=1500)
    z = pd.Series(np.sin(np.arange(1500) / 40) + rng.normal(0, .3, 1500), index=idx)
    ret = pd.Series(rng.normal(0.01, 0.05, 1500), index=idx)
    analysis = pd.DataFrame({"TE_HEATING_OIL__z90": z, "target_ret5": ret, "target_ret20": ret, "target_ret60": ret})
    res_a = ag.build_analogue_context(["TE_HEATING_OIL"], [], analysis=analysis, current_z_map={"TE_HEATING_OIL": 2.5})
    res_b = ag.build_analogue_context(["TE_HEATING_OIL"], [], analysis=analysis, current_z_map={"TE_HEATING_OIL": -2.5})
    assert res_a[0].current_z == 2.5 and res_b[0].current_z == -2.5
    assert res_a[0].n_days != res_b[0].n_days                 # 버킷이 달라야 한다
    md = "\n".join(ag.render_analogue_md(res_a))
    assert "이 변수가 대두유에 닿는 경로" in md and ag._REQUIRED_CAPTION in md
    for w in ag._FORBIDDEN_WORDS:
        assert w not in md


def test_media_items_parse_ko_headline() -> None:
    note = "[채널: Bing · kw:hormuz] 호르무즈 통항 감소 ‖ Hormuz transits fall — tanker traffic (https://r/1) ⋅ Plain title — d (https://r/2)"
    items = db._media_items(note)
    assert items[0]["ko"] == "호르무즈 통항 감소" and items[0]["title"] == "Hormuz transits fall"
    assert items[1]["ko"] == "" and items[1]["title"] == "Plain title"
    head, _ = db._article_head_html(items[0])
    assert "호르무즈 통항 감소" in head and "Hormuz transits fall" in head
    assert db._media_title("[PERPLEXITY-PROXY: 브라질] 브라질 수확 완료 ‖ Brazil harvest completed", "X") == "브라질 수확 완료"


def test_digest_ko_note_format(monkeypatch) -> None:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    import daily_unstructured_digest as dg
    monkeypatch.setattr(dg, "_llm_ko_batch", lambda items: {it["key"]: "미 대두유 선물 상승" for it in items})
    monkeypatch.setattr(dg, "KO_CACHE", Path("/nonexistent/ko.json"))
    monkeypatch.setattr(dg, "_save_ko_cache", lambda c: None)
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    kos = dg.ko_headlines([{"title": "Soyoil futures rise", "desc": "biodiesel demand"}])
    assert list(kos.values()) == ["미 대두유 선물 상승"]
    rows = [{"indicator": "BRAZIL_HARVEST_PROGRESS", "value": 1, "date": "2026-09-27", "source": "p",
             "note": "[PERPLEXITY-PROXY: 브라질] " + "Brazil soybean harvest is effectively complete as of mid-August, per Conab."}]
    dg._attach_proxy_ko(rows)
    assert rows[0]["note"].startswith("[PERPLEXITY-PROXY: 브라질] 미 대두유 선물 상승 ‖ Brazil")
    assert dg._is_kv_note("RATE: 22.5% | CHANGE: unchanged | DATE: x") and not dg._is_kv_note("prose only text here")


def test_wasde_query_window_and_consensus_unknown() -> None:
    from datetime import date
    from src.pipeline.connectors import gpr_connector as g
    assert g._wasde_query_window(date(2026, 9, 11)) and g._wasde_query_window(date(2026, 9, 16))
    assert not g._wasde_query_window(date(2026, 9, 27))
    assert g._extract_value("CONSENSUS: 1,250 million lbs | ACTUAL: 1,300 | SURPRISE_SCORE: -0.4", ("SURPRISE_SCORE",)) == -0.4


def test_proxy_change_rule_nan_and_note(tmp_path) -> None:
    """적대 검증 반영: NaN 값은 note 비교, 값이 같아도 사건 서술이 바뀌면 변경."""
    arc = pd.DataFrame([
        {"date": pd.Timestamp("2026-09-24"), "indicator": "US_IRAN_CONFLICT_STATUS", "value": 2.0,
         "note": "[P] LEVEL: MEDIUM | KEY_EVENT: A | DATE: x"},
        {"date": pd.Timestamp("2026-09-24"), "indicator": "WASDE_CONSENSUS_SCORE", "value": float("nan"),
         "note": "[P] CONSENSUS: unknown | ACTUAL: 21"},
    ])
    same_geo = pd.Series({"date": pd.Timestamp("2026-09-25"), "indicator": "US_IRAN_CONFLICT_STATUS", "value": 2.0,
                          "note": "[P] LEVEL: MEDIUM | KEY_EVENT: A | DATE: x"})
    new_geo = same_geo.copy(); new_geo["note"] = "[P] LEVEL: MEDIUM | KEY_EVENT: B | DATE: y"
    nan_same = pd.Series({"date": pd.Timestamp("2026-09-25"), "indicator": "WASDE_CONSENSUS_SCORE",
                          "value": float("nan"), "note": "[P] CONSENSUS: unknown | ACTUAL: 21"})
    assert not db._proxy_value_changed(same_geo, arc)
    assert db._proxy_value_changed(new_geo, arc)
    assert not db._proxy_value_changed(nan_same, arc)


def test_match_articles_prefers_latest_on_tie() -> None:
    sig = pd.DataFrame([
        {"date": pd.Timestamp("2026-09-15"), "indicator": "RSS_WORLD_GRAIN", "source_name": "x",
         "note": "[채널: 원문] Heating oil futures jump — d (https://old)"},
        {"date": pd.Timestamp("2026-09-26"), "indicator": "RSS_WORLD_GRAIN", "source_name": "x",
         "note": "[채널: 원문] Heating oil futures fall — d (https://new)"},
    ])
    arts = db._match_articles("TE_HEATING_OIL", sig)
    assert arts[0]["url"] == "https://new"


def test_dated_series_handles_tz_aware() -> None:
    df = pd.DataFrame({"price_date": pd.date_range("2026-01-01", periods=3, tz="UTC"),
                       "indicator_code": "X", "value": [1.0, 2.0, 3.0]})
    s = db._dated_series({"a": df}, ["X"])
    assert s["price_date"].dt.tz is None and len(s) == 3
