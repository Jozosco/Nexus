"""일별 브리프 표기 게이트 — 승인자 지시(2026-09-13) 화면 규칙.

① 영문 지표 코드·분석 용어의 한글화 ② 에이전트·결정 코드(A-xxx·CE-xxx·실행 번호) 미노출
③ 정상 항로는 상세 카드 생략 · 규칙 버전·커버리지 캡션 미표시.
스모크 3케이스(정상·전면 결측·무경보) 전부에 대해 화면 텍스트 기준으로 검사한다.
"""
from __future__ import annotations

import html as _html
import re

import numpy as np
import pandas as pd
import pytest

from src.reporting.daily_brief import (_humanize, _label_ko, _media_title,
                                       build_daily_brief)

# 내부 참조 코드(D-는 D-day 표기와 충돌하므로 제외) · 실행 번호 · 영문 지표 코드(대문자_언더스코어)
_FORBIDDEN = [
    re.compile(r"\b(?:A|CE|DQ|M|V|R|C|P1|S|TERM)-\d{3}\b"),
    re.compile(r"\brun_\d+"),
    re.compile(r"런 \d{6,}"),
    re.compile(r"\b[A-Z]{2,}(?:_[A-Z0-9]{2,})+\b"),
    re.compile(r"USc/lb|P10/P50|Elastic Net|SHAP|Granger|target_ret|maritime_rules"),
]


def _visible_text(html: str) -> str:
    body = re.sub(r"<style.*?</style>", " ", html, flags=re.S)
    body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
    body = re.sub(r"<[^>]+>", " ", body)
    return _html.unescape(body)


def _frames(n: int = 320, with_maritime: bool = True) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(11)
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=n)
    close = pd.DataFrame({"price_date": dates, "indicator_code": "CBOT_BO_CLOSE",
                          "value": 60 + np.cumsum(rng.normal(0, 0.4, n))})
    out = {"commodity": close}
    if with_maritime:
        today = dates[-1]
        out["gpr"] = pd.DataFrame({
            "price_date": [today] * 3,
            "indicator_code": ["HORMUZ_THREAT_LEVEL", "SUEZ_RED_SEA_RISK", "GDELT_EVENT_SCORE"],
            "value": [3.0, 2.0, 12.0]})
    return out


def _importance() -> pd.DataFrame:
    return pd.DataFrame({
        "변수": ["ALLSKY_SFC_PAR_TOT_Buenos_Aires__z90", "TE_BDI__z90", "DEXBZUS",
                 "HORMUZ_THREAT_LEVEL", "GWETROOT_Illinois"],
        "LASSO_계수": [0.31, -0.22, 0.10, 0.08, -0.05],
        "피어슨_r": [0.41, -0.30, 0.12, 0.09, -0.07]})


def _alerts(breach: bool) -> list[dict]:
    return [{"변수": "ENSO_ONI", "설명": "엘니뇨 강도", "현재값": "1.39", "임계값": "1.0",
             "데이터신선도": "✅", "상태": "🚨 초과" if breach else "✅ 정상"},
            {"변수": "TE_BDI", "설명": "해상운임", "현재값": "3620", "임계값": "z 2σ",
             "데이터신선도": "✅", "상태": "✅ 정상"}]


def _status() -> pd.DataFrame:
    return pd.DataFrame({"변수 항목": ["a", "b", "c"], "신선도": ["✅", "✅", "⚠️"]})


@pytest.mark.parametrize("case", ["normal", "all_missing", "no_alert"])
def test_brief_has_no_internal_codes_or_english_terms(case: str) -> None:
    if case == "all_missing":
        frames, imp, alerts = {}, pd.DataFrame(), []
    else:
        frames, imp = _frames(), _importance()
        alerts = _alerts(breach=(case == "normal"))
    html = build_daily_brief(frames, imp, alerts, _status(), "2026-09-13T20:30:00",
                             "34538786606", "target_ret20", n_features=2073)
    text = _visible_text(html)
    for pat in _FORBIDDEN:
        hits = sorted(set(pat.findall(text)))
        assert not hits, f"[{case}] 화면 금지 패턴 잔존 {pat.pattern}: {hits[:8]}"
    assert "34538786606" not in text                 # 실행 번호 미노출
    assert "규칙 기반 편집상 참고 지수" not in text  # 삭제 대상 캡션
    assert "커버리지" not in text
    assert "오늘의 시장 뉴스" in text and "참고: 전문 매체 최신 기사" in text
    assert "공급 경로와 해상 위험" in text


def test_normal_chokepoints_collapsed_and_labels_korean() -> None:
    html = build_daily_brief(_frames(), _importance(), _alerts(True), _status(),
                             "2026-09-13T20:30:00", "1", "target_ret20", n_features=10)
    text = _visible_text(html)
    # 말라카·파나마(구조 등급 normal → 정상)는 카드 대신 한 줄 요약
    assert "정상 통과(설명 생략)" in text and "말라카 해협" in text
    assert text.count("한국향 직접 경유 —") <= 1
    # 호르무즈는 동적 승급(위협 수준 3 → 심각) 카드 유지 · 등급어 한글
    assert "호르무즈 해협 위협 수준" in text and "심각 승급" in text
    assert "critical" not in text and "elevated" not in text
    # 기후 변수 코드 한글화 · 분석 대상 한글화
    assert "일사량(광합성 유효) — 부에노스아이레스" in text
    assert "20거래일 뒤 가격 변화율" in text
    assert "센트/파운드" in text and "달러/톤" in text


def test_label_and_humanize_helpers() -> None:
    assert _label_ko("feat_GWETROOT_Illinois__z90") == "근권 토양수분 — 일리노이"
    # Open-Meteo 코드는 국가 접두(_CN·_US)가 지역 앞에 붙는다 — 접두가 라벨에 새지 않아야 함
    assert _label_ko("temperature_2m_max_CN_Heilongjiang") == "최고 기온 — 헤이룽장"
    assert _label_ko("soil_moisture_0_to_7cm_BR_RioGrandedoSul") == "표층 토양수분 — 히우그란지두술"
    assert _label_ko("FCST_precipitation_sum_BR_Goias") == "15일 예보: 강수량 — 고이아스"
    assert _label_ko("sunshine_duration_MY_Sabah") == "일조 시간 — 사바(말레이시아)"
    assert _label_ko("HORMUZ_THREAT_LEVEL") == "호르무즈 해협 위협 수준"
    assert _label_ko("RSS_REUTERS_COMMODITIES").startswith("로이터")
    assert "unknown code xyz" in _label_ko("UNKNOWN_CODE_XYZ")     # 대문자 코드 원문 미노출
    out = _humanize("HORMUZ_THREAT_LEVEL=3 → critical 승급 (CE-010 validated · DATA GAP)")
    assert "호르무즈 해협 위협 수준=3 → 심각 승급" in out
    assert "CE-010" not in out and "validated" not in out and "자료 없음" in out
    assert _humanize("운임 시장 전파(CE-010·CE-013) — 직접 경유 아님") == "운임 시장 전파 — 직접 경유 아님"
    assert _humanize("우회 국면(CE-013 validated) 근거") == "우회 국면(검증됨) 근거"
    t = _media_title("[정책] REPORT_DATE: 2026-09-11 CONSENSUS: 5.4 (https://x.y/z)", "X")
    assert t.startswith("발표일: 2026-09-11 컨센서스: 5.4") and "http" not in t
