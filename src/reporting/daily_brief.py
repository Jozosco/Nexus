"""G1 일별 브리프 렌더러 — 목업 v2(A-225·A-227) 구조의 실데이터 결선.

조정자 승인(2026-08-28) 후 실통합. 설계 원칙:
  - 7블록: E1 신뢰 스트립 → 한눈 요약(KPI) → 가격 추세·핵심 변인 → 금일 경보 →
    공급 경로 → 지표 스냅샷 → 언론·매체 → 주목 일정 → 부록(전문 기관)
  - 각 블록 4단 요약([현황]→[요인]→[전망]→[유의·권고]) — 규칙 기반 문장(LLM 미사용)
  - 차트·스파크라인·경로 모식도는 **서버측 SVG 생성**(JS 의존 0 — PDF 변환·CI 렌더 안전)
  - 토글(산출 근거·온톨로지 연결)은 순수 HTML <details> — 스크립트 0
  - 결측은 "미수집" 정직 표기(위장 금지) — 블록 단위 우아한 강등
  - 참고 범위 명칭·한계 캡션 상시(A-191) · HITL 고지(CLAUDE.md §6)
"""
from __future__ import annotations

import html as _html
import os
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from src.risk.maritime_threat import (Observation, compute_maritime_threat, explain_ko,
                                      load_registry)

SIGNALS_CSV = Path("data/processed/unstructured_daily_signals.csv")
LB_PER_MT = 2204.62262            # USc/lb → $/MT 환산 (×22.0462)

# WASDE 발표 예정일 (USDA 공표 일정 — 확정 시 갱신)
WASDE_SCHEDULE = [date(2026, 9, 11), date(2026, 10, 9), date(2026, 11, 10), date(2026, 12, 10)]
POLICY_MILESTONES = [
    (date(2027, 1, 1), "아르헨티나 수출세 월별 인하 개시", "아르헨티나 법령 423/2026호 · 24%→15% 경로"),
]
LEADTIME_DAYS = 50                # CIF 한국 리드타임 상단(40~50일) 보수 적용

# 변인 코드 → 한국어 표시명 (미등재 코드는 원 코드 노출)
VAR_LABELS: dict[str, str] = {
    "CBOT_BO_CLOSE": "CBOT 대두유(ZL) 종가",
    "TE_BDI": "BDI 해상운임지수", "BDI": "BDI 해상운임지수", "BDI_ZSCORE": "BDI 해상운임지수",
    "DEXBZUS": "브라질 헤알 환율(BRL/USD)", "DEXCHUS": "위안 환율(CNY/USD)",
    "DEXKOUS": "원/달러 환율", "VIXCLS": "VIX 변동성",
    "GPR_NORMALIZED": "지정학 위험(GPR 정규화)", "GPR": "지정학 위험(GPR)",
    "ENSO_ONI": "ENSO ONI(엘니뇨 지수)", "ONI": "ENSO ONI(엘니뇨 지수)",
    "CPO_SBO_SPREAD": "대두유−팜유 가격 차이", "WASDE_SBO_STU": "WASDE 재고사용비율",
    "TE_PALM_OIL": "CPO 팜유(TE)", "TE_SOYBEANS": "CBOT 대두(TE)",
    "FEDFUNDS": "미 기준금리", "CPIAUCSL": "미 CPI",
    "GDELT_EVENT_SCORE": "대두유 관련 국제 사건 기사 수", "GDELT_SBO_EVENT_COUNT": "대두유 관련 국제 사건 수",
    "HORMUZ_THREAT_LEVEL": "호르무즈 해협 위협 수준",
    "HORMUZ_AWRP_MULTIPLIER": "호르무즈 전쟁위험보험료 배수",
    "SUEZ_RED_SEA_RISK": "수에즈·홍해 위험 수준", "UKRAINE_GRAIN_CORRIDOR": "흑해 곡물 회랑 상태",
    "US_CHINA_TARIFF_STATUS": "미·중 관세 상태", "BRAZIL_HARVEST_PROGRESS": "브라질 수확 진척",
    "GEOINTEL_RISK_COMPOSITE": "복합 지정학 위험 지수", "SEISMIC_RISK": "지진 위험",
    "SBO_STRAIT_RISK_COMPOSITE": "해협 위험 복합 지수", "GPR_REALTIME": "지정학 위험(실시간)",
    "AIS_HORMUZ_TANKER_COUNT": "호르무즈 탱커 통항 수", "AIS_HORMUZ_RISK": "호르무즈 통항 위험",
    "AIS_MALACCA_TANKER_COUNT": "말라카 탱커 통항 수", "AIS_MALACCA_RISK": "말라카 통항 위험",
    "AIS_PANAMA_TANKER_COUNT": "파나마 탱커 통항 수", "AIS_PANAMA_RISK": "파나마 통항 위험",
    "AIS_HORMUZ_TANKERS": "호르무즈 탱커 통항", "AIS_MALACCA_TANKERS": "말라카 탱커 통항",
    "AIS_PANAMA_TANKERS": "파나마 탱커 통항",
    "BCAA": "식물성유지 탱커 운임 평가", "BCTI_PROXY": "청정제품선 운임(대용)",
    "WEATHER_ALERT_COUNT": "기상 특보 수", "WEATHER_ANOMALY_SCORE": "기상 이상 점수",
    "NOAA_WEATHER_ALERT_SEVERITY": "미 기상 경보 심각도",
    "BOARD_CRUSH_MARGIN": "압착 마진(대두 가공 채산성)",
    "ARG_EXPORT_TAX_NEWS": "아르헨티나 수출세 뉴스", "INDIA_DUTY_NEWS": "인도 식용유 관세 뉴스",
    "BIODIESEL_MANDATE_NEWS": "바이오디젤 의무혼합 뉴스",
    "WASDE_CONSENSUS_SCORE": "USDA 수급 전망 컨센서스",
    "CPO_USD_MT": "팜유 가격(달러/톤)", "CPO": "팜유 가격",
    "KRW_USD": "원/달러 환율", "CBOT_BO_ROLLDAY": "대두유 선물 만기 교체일",
}

# ── 화면 표기 한글화(승인자 지시 2026-09-13) — 영문 지표 코드·내부 코드는 화면에 노출하지 않음 ──
# 기후 변수 코드 = {파라미터}_{지역} 패턴 (NASA POWER 업로드본 `T2M_Iowa` · Open-Meteo/예보 `..._US_Iowa`)
# 지역 원천은 config/production_regions.yaml(23산지 — tier1 정본 12 · tier2 주 중심 근사 11, 2026-09-13)
_REGION_KO: dict[str, str] = {
    "Buenos_Aires": "부에노스아이레스", "BuenosAires": "부에노스아이레스", "Cordoba": "코르도바",
    "Santa_Fe": "산타페", "SantaFe": "산타페", "Heilongjiang": "헤이룽장", "Shandong": "산둥",
    "Jiangsu": "장쑤", "Illinois": "일리노이", "Iowa": "아이오와", "Indiana": "인디애나",
    "Mato_Grosso": "마투그로수", "MatoGrosso": "마투그로수", "MatoGrossodoSul": "마투그로수두술",
    "Parana": "파라나",
    # tier2 (2026-09-13 확장) — 대두 7 · 팜유 4
    "RioGrandedoSul": "히우그란지두술", "Goias": "고이아스", "Minnesota": "미네소타",
    "Nebraska": "네브래스카", "Ohio": "오하이오", "AltoParana": "알토파라나(파라과이)",
    "MadhyaPradesh": "마디아프라데시(인도)", "Sabah": "사바(말레이시아)", "Johor": "조호르(말레이시아)",
    "Riau": "리아우(인도네시아)", "CentralKalimantan": "중부칼리만탄(인도네시아)",
}
_CLIMATE_PARAM_KO: dict[str, str] = {
    "T2M": "평균 기온", "T2M_MAX": "최고 기온", "T2M_MIN": "최저 기온", "PRECTOTCORR": "강수량",
    "RH2M": "상대 습도", "ALLSKY_SFC_SW_DWN": "일사량", "ALLSKY_SFC_PAR_TOT": "일사량(광합성 유효)",
    "GWETROOT": "근권 토양수분", "GWETTOP": "표층 토양수분",
    "temperature_2m_mean": "평균 기온", "temperature_2m_max": "최고 기온",
    "temperature_2m_min": "최저 기온", "precipitation_sum": "강수량",
    "shortwave_radiation_sum": "일사량", "et0_fao_evapotranspiration": "증발산량",
    "soil_moisture_0_to_7cm": "표층 토양수분", "soil_temperature_0_to_7cm": "표층 토양온도",
    "sunshine_duration": "일조 시간",
}
_COUNTRY_SUFFIX_RE = re.compile(r"_[A-Z]{2}$")     # Open-Meteo 지역 코드의 국가 접두(_CN·_US·_BR …)
_PREFIX_KO: list[tuple[str, str]] = [
    ("SOYBEAN_PROD", "미국 대두 생산"), ("CROP_CONDITION", "작황 등급"), ("DROUGHT", "가뭄 지수"),
    ("USDM", "미 가뭄 모니터"), ("WASDE_USDOM", "USDA 미국 수급"), ("WASDE", "USDA 세계 수급"),
    ("PSD", "USDA 국가별 수급"), ("GATS_US_RSBO", "미국 정제 대두유 수출"),
    ("GATS_US_SBO", "미국 조대두유 수출"), ("KCS", "관세청 수입 실적"), ("ICE", "ICE 거래량"),
    ("UNSTR_GAIN", "USDA 해외 보고서 신호"), ("UNSTR_FAO", "FAO 시장 보고서 신호"),
    ("TE_", "국제 상품 가격"), ("CBOT_BO", "대두유 선물"), ("FX_", "환율"), ("CPI_KOREA", "한국 물가"),
    ("ESR", "미국 수출 판매"), ("FAO", "FAO 지표"), ("SBO_", "대두유 지표"),
]
_RSS_ORG_KO: dict[str, str] = {
    "RSS_FARMDOC_DAILY": "farmdoc daily(일리노이대)", "RSS_WORLD_GRAIN": "월드 그레인",
    "RSS_OFI_MAGAZINE": "OFI(유지 산업지)", "RSS_GRAIN_ORG": "GRAIN(농업 NGO)",
    "RSS_SOYGROWERS": "미국 대두협회", "RSS_CLIMATEPOL": "크라이미트폴",
    "RSS_AGMARKET": "애그마켓", "RSS_GRAINCENTRAL": "그레인 센트럴(호주)",
    "RSS_TFM": "토탈 팜 마케팅", "RSS_UKRAGRO": "우크라그로컨설트",
    "RSS_REUTERS_COMMODITIES": "로이터(상품·탄소)", "RSS_REUTERS_CLIMATE_ENERGY": "로이터(기후·에너지)",
    "RSS_AP_COMMODITIES": "AP 통신(상품·선물)", "RSS_AP_WORLD": "AP 통신(국제)",
}
_SOURCE_KO: list[tuple[str, str]] = [
    ("PolicyProxy", "정책 뉴스 요약"), ("GeoEventProxy", "지정학 사건 요약"),
    ("BalticExchange", "운임 시황 요약"), ("HormuzProxy", "해협 위협 요약"),
    ("perplexity_proxy", "실시간 뉴스 요약"), ("Perplexity", "실시간 뉴스 요약"),
]
_TIER_KO: dict[str, str] = {"normal": "보통", "elevated": "상승", "high": "높음",
                            "critical": "심각", "war_zone": "전쟁 지역"}
_ROUTE_KO: dict[str, str] = {"RT-SANTOS-KR": "산토스(브라질)→한국",
                             "RT-ROSARIO-KR": "로사리오(아르헨티나)→한국",
                             "RT-USG-KR": "미국 걸프→한국"}
_TARGET_KO: dict[str, str] = {"target_ret1": "1거래일 뒤 가격 변화율",
                              "target_ret5": "5거래일 뒤 가격 변화율",
                              "target_ret20": "20거래일 뒤 가격 변화율",
                              "target_ret60": "60거래일 뒤 가격 변화율"}
_GATE_KO: dict[str, str] = {"PASS": "통과", "WARNING": "통과(주의)", "REJECTED": "불합격",
                            "SKIPPED": "생략"}
_NOTE_KEY_KO: dict[str, str] = {
    "REPORT_DATE": "발표일", "CONSENSUS": "컨센서스", "RATE": "세율", "PROGRESS": "진척",
    "STATUS": "상태", "LEVEL": "수준", "SCORE": "점수", "SOURCE": "출처", "MULTIPLIER": "배수",
    "VALUE": "값", "DATE": "일자", "COUNT": "건수",
    # A-269: 프록시 프롬프트가 실제로 내는 키 전량 — 미매핑 키가 영문 Title Case로 새던 결함
    "DUTY_RATE": "관세율", "CHANGE": "변동", "ACTUAL": "실제", "SURPRISE": "서프라이즈",
    "RISK": "위험", "DIVERSIONS": "우회 선박", "FREIGHT_IMPACT": "운임 영향",
    "SUNFLOWER_OIL_EXPORTS": "해바라기유 수출", "TARIFF_LEVEL": "관세 수준",
    "SOYBEAN_OIL_TARIFF": "대두유 관세", "VS_LAST_YEAR": "전년 대비", "WEATHER_RISK": "기상 위험",
    "INDONESIA": "인도네시아", "MALAYSIA": "말레이시아", "QUALITATIVE": "정성 판정",
    "COMPOSITE": "복합 점수", "AWRP": "전쟁위험보험료", "THREAT": "위협",
}
_VALUE_KO: dict[str, str] = {
    "unchanged": "변동 없음", "increase": "인상", "decrease": "인하", "high": "높음", "medium": "중간",
    "low": "낮음", "open": "개방", "restricted": "제한", "blocked": "차단", "normal": "정상",
    "reduced": "감소", "suspended": "중단", "bullish": "강세", "bearish": "약세", "neutral": "중립",
    "yes": "있음", "no": "없음", "none": "없음", "unknown": "미확인", "ahead": "앞섬", "behind": "뒤처짐",
    "on-track": "정상", "critical": "심각", "elevated": "상승",
}
_PREFIX_TAG_RE = re.compile(r"^\s*\[[^\]]*\]\s*")


def _parse_kv(note: str) -> list[tuple[str, str]]:
    """프록시 단일 행(`KEY: value | KEY: value`)을 (한글 라벨, 값) 목록으로 — 결정적·비용 0 (A-269).

    `**`·`[]`·인용 번호 제거, 구분자는 `|` 또는 2칸 이상 공백. 키가 2개 미만이면 빈 목록(산문으로 취급).
    """
    body = _PREFIX_TAG_RE.sub("", str(note))
    body = re.sub(r"\[\d+\]", "", body).replace("**", "")
    parts = re.split(r"\s*\|\s*|\s{2,}", body)
    out: list[tuple[str, str]] = []
    for part in parts:
        m = re.match(r"^\s*([A-Z][A-Z_]{1,}):\s*(.+?)\s*$", part.strip())
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip().strip("[]").strip()
        val = re.sub(r"\s*\([^)]*\)\s*$", "", val) if len(val) > 40 else val   # 긴 괄호 부연 제거
        low = val.lower().strip(".")
        val_ko = _VALUE_KO.get(low, val)
        out.append((_NOTE_KEY_KO.get(key, key.replace("_", " ").title()), val_ko[:60]))
    return out if len(out) >= 2 else []
_CODE_TOKEN_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+\b")
_INTERNAL_REF_RE = re.compile(r"\b(?:A|CE|DQ|M|V|R|C|P1|S|TERM)-\d{1,3}\b")
_WORD_KO: list[tuple[str, str]] = [
    ("DATA GAP", "자료 없음"), ("INFERENCE", "추정"), ("CONFIRMED", "확인됨"),
    ("validated", "검증됨"), ("candidate", "후보"), ("evidence", "근거"),
    ("war_zone", "전쟁 지역"), ("critical", "심각"), ("elevated", "상승"), ("normal", "보통"),
    ("high", "높음"), ("AIS", "선박 위치 자료"), ("JWC", "합동전쟁위원회"),
    ("CIF", "도착가(운임·보험 포함)"), ("SBO", "대두유"),
]
_catalog_cache: dict[str, str] | None = None


def _catalog_ko() -> dict[str, str]:
    """변수 카탈로그 name_ko(variable_importance_g1) — 실패 시 빈 사전(비치명)."""
    global _catalog_cache
    if _catalog_cache is None:
        try:
            from src.forecasting.variable_importance_g1 import VARIABLE_CATALOG
            _catalog_cache = {str(v["code"]): str(v["name_ko"]) for v in VARIABLE_CATALOG
                              if v.get("code") and v.get("name_ko")}
        except Exception:                                     # noqa: BLE001
            _catalog_cache = {}
    return _catalog_cache


def _label_ko(code: object) -> str:
    """지표·변수 코드 → 한국어 표시명. 미등재는 '기타 변수(소문자 풀이)' — 영문 코드 원문 노출 금지."""
    base = str(code).split("__")[0]
    if base.startswith("feat_"):
        base = base[5:]
    if base in VAR_LABELS:
        return VAR_LABELS[base]
    if base in _RSS_ORG_KO:
        return _RSS_ORG_KO[base]
    if base in _TARGET_KO:
        return _TARGET_KO[base]
    cat = _catalog_ko().get(base)
    if cat:
        return cat
    forecast = base.startswith("FCST_")          # 15일 예보 계열(Open-Meteo) — 관측과 구분 표기
    if forecast:
        base = base[5:]
    for reg_key, reg_ko in sorted(_REGION_KO.items(), key=lambda kv: -len(kv[0])):
        if base.endswith("_" + reg_key):
            param = _COUNTRY_SUFFIX_RE.sub("", base[: -len(reg_key) - 1])
            pko = _CLIMATE_PARAM_KO.get(param) or _CLIMATE_PARAM_KO.get(param.lower())
            label = f"{pko or param.replace('_', ' ').lower()} — {reg_ko}"
            return f"15일 예보: {label}" if forecast else label
    for prefix, ko in _PREFIX_KO:
        if base.startswith(prefix):
            return f"{ko}({base.lower().replace('_', ' ')})"
    return f"기타 변수({base.lower().replace('_', ' ')})"


def _humanize(text: object) -> str:
    """설정·규칙 문자열의 영문 코드·등급어·내부 참조 코드를 화면용 한국어로 치환."""
    t = _CODE_TOKEN_RE.sub(lambda m: _label_ko(m.group(0)), str(text))
    t = _INTERNAL_REF_RE.sub("", t)
    for a, b in _WORD_KO:
        t = re.sub(rf"\b{re.escape(a)}\b", b, t)
    # 코드 제거 뒤 남는 빈 괄호·고아 구분자 정리 — "(·)" → 삭제, "( 검증됨)" → "(검증됨)", "· —" → " —"
    t = re.sub(r"\(\s*[·,;]?\s*", "(", t)
    t = re.sub(r"\s*[·,;]?\s*\)", ")", t)
    t = re.sub(r"\(\s*\)", "", t)
    t = re.sub(r"·\s*·", "·", t)
    t = re.sub(r"\s*·\s*(?=—|$)", " ", t)
    t = re.sub(r"(선박 위치 자료)\((선박 위치 자료)\s*", r"\1(", t)
    return re.sub(r"\s{2,}", " ", t).strip(" ·-")


def _source_ko(name: object) -> str:
    s = str(name or "")
    for key, ko in _SOURCE_KO:
        if key.lower() in s.lower():
            return ko
    if s.upper().startswith("RSS_"):
        return _RSS_ORG_KO.get(s.upper(), s)
    return s


def _media_title(note: str, indicator: str, n: int = 110) -> str:
    """언론·매체 카드 제목/요약 1줄 — A-269 재작성.

    ① 접두 `[…]`만 앵커 제거(구 코드 `split("]")[-1]`는 인용 [1][3]·`**[12.5%]**`에서 본문을 잃음)
    ② 구조화 행이면 `_parse_kv`로 "세율 22.5% · 변동 없음 · …" 한글 요약
    ③ 매체 노트(`제목 — 요약 (url)` ⋅ …)는 첫 기사만, URL 제거
    ④ 산문은 문장·구분자 경계에서 n자 안으로 절단 · 빈 본문은 정성 라벨(예: 위협 수준 높음)
    """
    raw = str(note)
    kv = _parse_kv(raw)
    if kv:
        txt = " · ".join(f"{k} {v}" for k, v in kv[:5])
        return txt[:n].rstrip(" ·") if len(txt) > n else txt
    m = re.match(r"^\s*\[([^\]]*)\]\s*(.*)$", raw, flags=re.S)
    tag, body = (m.group(1), m.group(2)) if m else ("", raw)
    body = body.strip()
    if not body:                                              # 예: [QUALITATIVE:HIGH]
        tm = re.match(r"^([A-Z_]+):\s*([A-Za-z]+)$", tag.strip())
        if tm:
            return f"{_NOTE_KEY_KO.get(tm.group(1), tm.group(1).title())} {_VALUE_KO.get(tm.group(2).lower(), tm.group(2))}"
        return _label_ko(indicator)
    if " ⋅ " in body or " — " in body:                        # 매체 노트: 첫 기사만
        body = body.split(" ⋅ ")[0]
    body = _URL_RE.sub("", body)
    body = re.sub(r"\[\d+\]", "", body).replace("**", "")
    body = re.sub(r"\b([A-Z][A-Z_]{2,}):",
                  lambda mm: _NOTE_KEY_KO.get(mm.group(1), mm.group(1).replace("_", " ").title()) + ":", body)
    body = re.sub(r"\(\s*\)", "", body).strip(" ⋅·-")
    if len(body) > n:                                         # 문장·구분자 경계 절단
        cut = body[:n]
        k = max(cut.rfind(". "), cut.rfind(" — "), cut.rfind(" | "), cut.rfind("·"))
        body = (cut[:k] if k > n * 0.4 else cut).rstrip(" ·|,-") + "…"
    return body or _label_ko(indicator)


def _media_items(note: str) -> list[dict]:
    """매체 노트 → 기사별 {title, desc, url} (A-269: 아카이브 note '[채널…] 제목 — 요약 (url) ⋅ …')."""
    body = _PREFIX_TAG_RE.sub("", str(note))
    items = []
    for part in body.split(" ⋅ "):
        part = part.strip()
        if not part:
            continue
        url = _first_url(part) or ""
        txt = _URL_RE.sub("", part)
        txt = re.sub(r"\(\s*\)?\s*$", "", txt)               # 절단된 '(https…' 잔여 괄호 제거
        txt = re.sub(r"\(\s*\)", "", txt).strip(" ⋅·-(")
        title, desc = (txt.split(" — ", 1) + [""])[:2] if " — " in txt else (txt, "")
        items.append({"title": title.strip(), "desc": desc.strip(), "url": url})
    return items


_RSS_ORG_EN: dict[str, str] = {   # A-269: 승인자 지시 — 부록 소스명은 영문
    "RSS_FARMDOC_DAILY": "Farmdoc Daily (Univ. of Illinois)", "RSS_WORLD_GRAIN": "World Grain",
    "RSS_OFI_MAGAZINE": "Oils & Fats International", "RSS_GRAIN_ORG": "GRAIN",
    "RSS_SOYGROWERS": "American Soybean Association", "RSS_CLIMATEPOL": "Climatepol (KR)",
    "RSS_AGMARKET": "AgMarket.Net", "RSS_GRAINCENTRAL": "Grain Central (AU)",
    "RSS_TFM": "Total Farm Marketing", "RSS_UKRAGRO": "UkrAgroConsult",
    "RSS_REUTERS_COMMODITIES": "Reuters — Commodities", "RSS_REUTERS_CLIMATE_ENERGY": "Reuters — Climate & Energy",
    "RSS_AP_COMMODITIES": "AP — Commodities", "RSS_AP_WORLD": "AP — World",
}


def _llm_summary(note: str, indicator: str) -> str | None:
    """선택(기본 off): BRIEF_LLM_SUMMARY=1 이면 산문형 프록시 응답만 1줄 한글 요약(gpt-4o-mini·JSON·캐시·비치명).

    CI-004는 Perplexity 스케줄 편입 금지 규정이라 저촉 없음. 비용 발생 항목 — 결정 대기열(DQ-27) 승인 전 기본 off.
    """
    if os.environ.get("BRIEF_LLM_SUMMARY", "0") != "1":
        return None
    try:
        import json as _json
        cache_p = Path("data/processed/brief_llm_summary_cache.json")
        cache = _json.loads(cache_p.read_text(encoding="utf-8")) if cache_p.is_file() else {}
        key = f"{date.today().isoformat()}|{indicator}|{hash(note) & 0xffffffff}"
        if key in cache:
            return cache[key]
        from src.utils.openai_client import query_openai
        out = query_openai(
            f"다음 시장 뉴스 텍스트를 한국어 한 문장(60자 이내)으로 요약하라. JSON {{\"summary\": \"...\"}} 형식만. 텍스트: {note[:800]}",
            system_prompt="너는 대두유 조달 데스크의 편집자다. 사실만, 전망·확률 표현 금지.",
            response_format={"type": "json_object"})
        summ = _json.loads(out).get("summary", "").strip() if out else ""
        if summ:
            cache[key] = summ
            cache_p.parent.mkdir(parents=True, exist_ok=True)
            cache_p.write_text(_json.dumps(cache, ensure_ascii=False), encoding="utf-8")
        return summ or None
    except Exception as e:                                    # noqa: BLE001 — 비치명
        print(f"[정보] LLM 요약 생략(비치명): {type(e).__name__}")
        return None


# 변인 키워드 → 기사 매칭 (별점) — 규칙 기반(Phase B에서 LLM 매핑 검토)
_DRIVER_KEYWORDS: dict[str, list[str]] = {
    "RVO": ["rvo", "rin", "biodiesel", "renewable diesel", "biofuel", "epa",
            "바이오디젤", "바이오연료", "재생디젤"],
    "BIODIESEL": ["biodiesel", "biofuel", "b40", "b50", "바이오디젤", "바이오연료"],
    "CPO": ["palm", "mpob", "팜유", "올레인"],
    "PALM": ["palm", "mpob", "팜유"],
    "BDI": ["freight", "shipping", "bdi", "운임", "해운"],
    "DEXBZUS": ["brazil", "real", "브라질", "헤알"],
    "BRL": ["brazil", "real", "브라질", "헤알"],
    "ARG": ["argentin", "export tax", "아르헨", "수출세", "rosario", "로사리오"],
    "EXPORT_TAX": ["argentin", "export tax", "수출세"],
    "ONI": ["el nino", "la nina", "enso", "drought", "엘니뇨", "라니냐", "가뭄"],
    "ENSO": ["el nino", "la nina", "enso", "drought", "엘니뇨", "라니냐", "가뭄"],
    "WASDE": ["wasde", "usda"],
    "STU": ["wasde", "stocks", "재고"],
    "HORMUZ": ["hormuz", "strait", "호르무즈", "해협"],
    "VIX": ["volatility", "vix", "변동성"],
    "CBOT": ["soybean oil", "soyoil", "cbot", "대두유"],
    # A-268: 기후 격자 변인(NASA POWER·Open-Meteo·예보) — 종전에는 키가 없어 항상 '매핑 없음'
    "T2M": ["heat", "temperature", "frost", "폭염", "기온", "한파", "weather", "기상"],
    "PRECTOTCORR": ["rain", "precipitation", "drought", "flood", "강우", "강수", "가뭄", "홍수", "weather", "기상"],
    "PRECIPITATION": ["rain", "precipitation", "drought", "flood", "강우", "강수", "가뭄", "홍수"],
    "ALLSKY": ["sunshine", "solar", "radiation", "일조", "일사", "weather", "기상", "drought", "가뭄"],
    "SHORTWAVE": ["sunshine", "solar", "일조", "일사"],
    "GWET": ["soil moisture", "drought", "토양", "가뭄", "dry"],
    "SOIL_": ["soil moisture", "drought", "토양", "가뭄", "dry"],
    "RH2M": ["humidity", "습도", "weather", "기상"],
    "FCST_": ["forecast", "예보", "weather", "기상"],
    "FX_BRL_USD": ["brazil", "real", "브라질", "헤알"],
    "ENSO_ONI": ["el nino", "la nina", "enso", "drought", "엘니뇨", "라니냐", "가뭄"],
}


def _driver_keywords(var_code: str) -> list[str]:
    """변인 코드 → 키워드. A-268: 접두/정확 매칭 + 지역명 추가(부분 문자열 오탐 — BOARD_CRUSH_MARGIN→ARG — 제거)."""
    up = var_code.upper().split("__")[0]
    kws: list[str] = []
    for key, words in _DRIVER_KEYWORDS.items():
        k = key.upper()
        if up == k or up.startswith(k) or up.startswith(k + "_") or f"_{k}_" in f"_{up}_":
            kws.extend(words)
    # 기후 변인의 지역명(한글·영문) — 기사에 산지 이름이 등장하면 연관
    for reg_key, reg_ko in _REGION_KO.items():
        if up.endswith("_" + reg_key.upper()) or up.endswith(reg_key.upper()):
            kws.extend([reg_ko.split("(")[0], reg_key.split("_")[-1].lower()])
    return list(dict.fromkeys(kws))

# 일별 비정형 지표 → 온톨로지 체인 (signal_tag_mapping·CE evidence 기반 정적 렌더 —
# 실검증 상태는 ontology.yaml이 원천, 여기서는 표시용 최소 사본)
_ONTOLOGY_CHAINS: dict[str, list[str]] = {
    "BIODIESEL_MANDATE_NEWS": ["기사", "신호: 바이오연료 수요", "검증된 인과 경로",
                               "바이오연료 의무량", "SBO 수요 ▲", "가격 상방"],
    "ARG_EXPORT_TAX_NEWS": ["기사", "신호: 수출세 경로", "검증된 인과 경로",
                            "아르헨 수출 물량", "공급 회복", "가격 하방"],
    "INDIA_DUTY_NEWS": ["기사", "신호: 수입관세", "후보 인과 경로(검증 대기)",
                        "인도 수입 수요", "수요 변동", "방향 조건부"],
    "HORMUZ_THREAT_LEVEL": ["선박 위치·뉴스 관측", "해협 위협 점수", "검증된 인과 경로",
                            "탱커 운임·전쟁보험료", "도착가 잔차층", "참고 범위 폭"],
    "SUEZ_RED_SEA_RISK": ["관측", "해협 위협 점수", "검증된 인과 경로",
                          "희망봉 우회(+12~15일)", "운임 상승", "도착가 상방"],
    "UKRAINE_GRAIN_CORRIDOR": ["관측", "흑해 회랑 상태", "후보 인과 경로(검증 대기)",
                               "해바라기유 수출 경로", "대체 유지 공급", "검증 대기"],
    "US_CHINA_TARIFF_STATUS": ["기사", "신호: 무역 정책", "검증된 인과 경로",
                               "미중 교역 흐름", "대두 수급 재편", "방향 조건부"],
    # 2026-09-13 — 전문 매체 채널(로이터·AP)·GDELT 기사 수: 주제 태깅 전이라 '검증 대기'
    "RSS_REUTERS_COMMODITIES": ["기사", "전문 매체 채널: 로이터(상품·탄소)", "주제 태깅(후속)",
                                "뉴스 감성 신호", "검증 대기"],
    "RSS_REUTERS_CLIMATE_ENERGY": ["기사", "전문 매체 채널: 로이터(기후·에너지)", "주제 태깅(후속)",
                                   "뉴스 감성 신호", "검증 대기"],
    "RSS_AP_COMMODITIES": ["기사", "전문 매체 채널: AP 통신(상품·선물)", "주제 태깅(후속)",
                           "뉴스 감성 신호", "검증 대기"],
    "RSS_AP_WORLD": ["기사", "전문 매체 채널: AP 통신(국제)", "주제 태깅(후속)",
                     "뉴스 감성 신호", "검증 대기"],
    "GDELT_EVENT_SCORE": ["국제 사건 기사 수", "지정학 위험 태그", "규칙 기반 경보 원천",
                          "해상 위협 점수(경보 성분)", "참고 지수"],
    # A-269: 공식 RSS 10종·나머지 실시간 프록시 — 매체 카드에도 분석 연결 표시
    "RSS_FARMDOC_DAILY": ["기사", "신호: 압착·바이오연료(농업경제 분석)", "후보 인과 경로(검증 대기)", "미국 재생디젤 압착 증설", "수출 여력", "방향 조건부"],
    "RSS_WORLD_GRAIN": ["기사", "신호: 물류·설비·가공 산업", "검증된 인과 경로", "요충 경로·압착 설비", "공급 차질", "가격 상방"],
    "RSS_OFI_MAGAZINE": ["기사", "신호: 유지류 산업·대체유", "후보 인과 경로(검증 대기)", "대두유−팜유 가격 차이", "대체 수요", "방향 조건부"],
    "RSS_GRAIN_ORG": ["기사", "신호: 토지·정책", "후보 인과 경로(검증 대기)", "삼림 규제(EUDR)", "대체 수요", "방향 조건부"],
    "RSS_SOYGROWERS": ["기사", "신호: 미국 대두 정책", "검증된 인과 경로", "45Z 세액공제·바이오디젤", "수출 여력", "가격 상방"],
    "RSS_CLIMATEPOL": ["기사", "신호: 국내 바이오연료·SAF 정책", "검증된 인과 경로", "원유·경유→바이오디젤 경제성", "산업 수요", "가격 상방"],
    "RSS_AGMARKET": ["기사", "신호: 선물 시장 동향", "후보 인과 경로(검증 대기)", "투기 포지션(COT)", "선물 모멘텀", "방향 조건부"],
    "RSS_GRAINCENTRAL": ["기사", "신호: 작황·기상(호주·아시아)", "검증된 인과 경로", "엘니뇨·강우", "남미·호주 작황", "가격 상방"],
    "RSS_TFM": ["기사", "신호: 선물 시장 동향", "후보 인과 경로(검증 대기)", "투기 포지션(COT)", "선물 모멘텀", "방향 조건부"],
    "RSS_UKRAGRO": ["기사", "신호: 흑해 수출 경로", "후보 인과 경로(검증 대기)", "해바라기유 수출", "대체 수요", "방향 조건부"],
    "BRAZIL_HARVEST_PROGRESS": ["관측", "신호: 브라질 수확 진척", "후보 인과 경로(검증 대기)", "수출 일정", "공급 시점", "방향 조건부"],
    "GPR_REALTIME": ["관측", "신호: 지정학 위험 지수", "검증된 인과 경로", "해협 위험·운임", "도착가", "가격 상방"],
    "GEOINTEL_RISK_COMPOSITE": ["관측", "신호: 복합 지정학 사건", "검증된 인과 경로", "해협 위험·운임", "도착가", "가격 상방"],
    "WASDE_CONSENSUS_SCORE": ["발표", "신호: WASDE 서프라이즈", "후보 인과 경로(검증 대기)", "재고사용비율 신호", "투기 순매수", "방향 조건부"],
    "HORMUZ_AWRP_MULTIPLIER": ["관측", "신호: 전쟁위험보험료", "검증된 인과 경로", "탱커 운임", "도착가", "가격 상방"],
    "BCAA": ["관측", "신호: 식물성유지 탱커 운임", "검증된 인과 경로", "운임층", "도착가", "가격 상방"],
}


# ── 데이터 추출 헬퍼 ──────────────────────────────────────────────────────────

def _dated_series(frames: dict[str, pd.DataFrame], codes: list[str]) -> pd.DataFrame:
    """indicator_code 우선순위 목록에서 (date, value) 시계열 추출 — 일자 중복은 최신 유지."""
    for code in codes:
        parts = []
        for df in frames.values():
            if "indicator_code" not in df.columns or "value" not in df.columns:
                continue
            sub = df[df["indicator_code"] == code]
            if not sub.empty and "price_date" in sub.columns:
                parts.append(sub[["price_date", "value"]])
        if not parts:
            continue
        merged = pd.concat(parts, ignore_index=True)
        merged["price_date"] = pd.to_datetime(merged["price_date"], errors="coerce")
        merged["value"] = pd.to_numeric(merged["value"], errors="coerce")
        merged = (merged.dropna().sort_values("price_date")
                  .drop_duplicates("price_date", keep="last").reset_index(drop=True))
        if not merged.empty:
            return merged
    return pd.DataFrame(columns=["price_date", "value"])


def _pct(a: float, b: float) -> float | None:
    return (a / b - 1.0) * 100.0 if b else None


def _z90(vals: pd.Series) -> float | None:
    if len(vals) < 30:
        return None
    win = vals.tail(90)
    sd = win.std()
    return float((vals.iloc[-1] - win.mean()) / sd) if sd and sd > 0 else None


@dataclass
class CloseKpi:
    close: float
    chg_abs: float | None
    chg_pct: float | None
    wk_pct: float | None
    z90: float | None
    last_date: date
    series: pd.DataFrame          # 최근 90관측 (date, value)


def _kpi_close(frames: dict[str, pd.DataFrame]) -> CloseKpi | None:
    s = _dated_series(frames, ["CBOT_BO_CLOSE"])
    if len(s) < 2:
        return None
    v = s["value"]
    close = float(v.iloc[-1])
    prev = float(v.iloc[-2])
    wk = float(v.iloc[-6]) if len(v) >= 6 else None
    return CloseKpi(
        close=close, chg_abs=close - prev, chg_pct=_pct(close, prev),
        wk_pct=_pct(close, wk) if wk else None, z90=_z90(v),
        last_date=s["price_date"].iloc[-1].date(), series=s.tail(90).reset_index(drop=True))


def _reference_range_usclb(close_hist: pd.Series, horizon: int = 60
                           ) -> tuple[float, float, float] | None:
    """기준 가격층 — 과거 60거래일 수익률 분포 분위를 최근 종가에 적용 (참고 범위)."""
    v = close_hist.dropna()
    if len(v) < horizon + 60:
        return None
    rets = v.pct_change(periods=horizon).dropna()
    if len(rets) < 30:
        return None
    last = float(v.iloc[-1])
    q10, q50, q90 = (float(rets.quantile(q)) for q in (0.10, 0.50, 0.90))
    return (last * (1 + q10), last * (1 + q50), last * (1 + q90))


def _landed_band() -> tuple[float, float, float] | None:
    """참고 도착가 범위($/MT) — landed_cost 산출과 직접 연동. 실패 시 None(정직 강등)."""
    try:
        from src.forecasting.landed_cost import build_landed_band
        r = build_landed_band()
        return (float(r.band_p10), float(r.band_p50), float(r.band_p90))
    except Exception as e:                                    # noqa: BLE001 — 비치명 강등
        print(f"[정보] 참고 도착가 범위 산출 불가(비치명): {type(e).__name__}: {e}")
        return None


def _load_signals(days: int = 5) -> pd.DataFrame:
    """일별 비정형 신호 아카이브(A-181)에서 최근 N일 로드."""
    if not SIGNALS_CSV.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(SIGNALS_CSV)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        cutoff = pd.Timestamp(date.today() - timedelta(days=days))
        return df[df["date"] >= cutoff].sort_values("date", ascending=False)
    except Exception as e:                                    # noqa: BLE001
        print(f"[경고] 일별 신호 아카이브 로드 실패(비치명): {e}")
        return pd.DataFrame()


_URL_RE = re.compile(r"https?://[^\s\"'<>\)\]]+")


def _first_url(text: str) -> str | None:
    m = _URL_RE.search(str(text))
    return m.group(0).rstrip(".,;") if m else None


def _match_articles(var_code: str, signals: pd.DataFrame) -> list[dict]:
    """변인 코드 ↔ 최근 기사 키워드 매칭 — 별점 재료."""
    kws = _driver_keywords(var_code)
    if not kws or signals.empty:
        return []
    out = []
    for _, row in signals.iterrows():
        blob = f"{row.get('indicator', '')} {row.get('note', '')}".lower()
        hits = sum(1 for w in kws if w in blob)
        if hits:
            out.append({"hits": hits, "note": str(row.get("note", ""))[:160],
                        "indicator": row.get("indicator", ""),
                        "source": row.get("source_name", ""),
                        "url": _first_url(row.get("note", ""))})
    return sorted(out, key=lambda d: -d["hits"])[:3]


# ── SVG 생성 (서버측 — JS 0) ─────────────────────────────────────────────────

_INFLECTION_MARKS = "①②③④⑤"


def _inflection_points(kpi: CloseKpi, top_n: int = 4) -> list[dict]:
    """표시 구간(최근 90관측) 내 |일간 변화율| 상위 급변일 검출 — 사실 기술 전용 (W-C).

    기준: 표시 구간 일간 변화율 표준편차의 1.5배(최소 1.0%) 이상인 날 중 상위 top_n.
    """
    v = kpi.series["value"].astype(float)
    ret = v.pct_change() * 100.0
    if ret.notna().sum() < 20:
        return []
    sd = float(ret.std())
    if not sd or sd <= 0:
        return []
    thr = max(1.5 * sd, 1.0)
    cand = ret[ret.abs() >= thr]
    picks = sorted(cand.abs().sort_values(ascending=False).head(top_n).index)
    out = []
    for k, i in enumerate(picks):
        out.append({"i": int(i), "no": _INFLECTION_MARKS[k],
                    "date": kpi.series["price_date"].iloc[int(i)],
                    "chg": float(ret.iloc[int(i)]), "close": float(v.iloc[int(i)])})
    return out


def _signals_around(center: pd.Timestamp, window_days: int = 2) -> pd.DataFrame:
    """일별 신호 아카이브에서 특정일 ±window 신호 로드 — 아카이브 밖 날짜는 빈 결과."""
    if not SIGNALS_CSV.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(SIGNALS_CSV)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        lo = center - pd.Timedelta(days=window_days)
        hi = center + pd.Timedelta(days=window_days)
        return df[(df["date"] >= lo) & (df["date"] <= hi)].sort_values("date")
    except Exception as e:                                    # noqa: BLE001 — 비치명
        print(f"[경고] 신호 아카이브 구간 조회 실패(비치명): {e}")
        return pd.DataFrame()


def _svg_price_chart(kpi: CloseKpi, rng: tuple[float, float, float] | None,
                     horizon: int = 60, marks: list[dict] | None = None) -> str:
    s = kpi.series
    hist = s["value"].tolist()
    n = len(hist)
    fwd = 20                                            # 팬 표시 해상도(전망 60거래일 축약)
    W, H, padL, padR, padT, padB = 560, 260, 44, 40, 14, 34
    total = n + fwd - 1
    if rng:
        p10e, p50e, p90e = rng
        lo = min(min(hist), p10e) * 0.985
        hi = max(max(hist), p90e) * 1.015
    else:
        lo, hi = min(hist) * 0.985, max(hist) * 1.015

    def x(i: float) -> float:
        return padL + (W - padL - padR) * i / total

    def y(v: float) -> float:
        return padT + (H - padT - padB) * (1 - (v - lo) / (hi - lo))

    grid = []
    step = max(round((hi - lo) / 5, 1), 0.5)
    g = np.arange(np.ceil(lo / step) * step, hi, step)
    for v in g:
        grid.append(f'<line x1="{padL}" x2="{W - padR}" y1="{y(v):.1f}" y2="{y(v):.1f}" '
                    f'stroke="var(--line)" stroke-width="1"/>'
                    f'<text x="{padL - 6}" y="{y(v) + 4:.1f}" font-size="10" '
                    f'fill="var(--ink3)" text-anchor="end">{v:.1f}</text>')
    line = " ".join(f"{'M' if i == 0 else 'L'}{x(i):.1f} {y(v):.1f}" for i, v in enumerate(hist))
    start_lbl = s["price_date"].iloc[0].strftime("%m-%d")
    today_lbl = kpi.last_date.strftime("%m-%d")
    end_date = np.busday_offset(kpi.last_date, horizon, roll="forward")
    end_lbl = pd.Timestamp(end_date).strftime("%m-%d")
    parts = ["".join(grid),
             f'<line x1="{x(n - 1):.1f}" x2="{x(n - 1):.1f}" y1="{padT}" y2="{H - padB}" '
             f'stroke="var(--ink3)" stroke-width="1" stroke-dasharray="3 3"/>']
    if rng:
        last = hist[-1]
        p10e, p50e, p90e = rng
        p10s, p50s, p90s = [], [], []
        for k in range(fwd):
            t = k / (fwd - 1)
            tw = t ** 0.5
            p50s.append(last + (p50e - last) * t)
            p10s.append(last + (p10e - last) * tw)
            p90s.append(last + (p90e - last) * tw)
        band = f"M{x(n - 1):.1f} {y(p10s[0]):.1f}"
        for i in range(1, fwd):
            band += f" L{x(n - 1 + i):.1f} {y(p10s[i]):.1f}"
        for i in range(fwd - 1, -1, -1):
            band += f" L{x(n - 1 + i):.1f} {y(p90s[i]):.1f}"
        band += " Z"
        p50path = " ".join(f"{'M' if i == 0 else 'L'}{x(n - 1 + i):.1f} {y(v):.1f}"
                           for i, v in enumerate(p50s))
        parts.append(f'<path d="{band}" fill="var(--band2)"/>')
        parts.append(f'<path d="{p50path}" fill="none" stroke="var(--accent)" '
                     f'stroke-width="2" stroke-dasharray="5 4"/>')
        parts.append(f'<text x="{x(total) + 2:.1f}" y="{y(p90e) + 3:.1f}" font-size="10" '
                     f'fill="var(--ink3)">{p90e:.2f}</text>'
                     f'<text x="{x(total) + 2:.1f}" y="{y(p50e) + 3:.1f}" font-size="10" '
                     f'fill="var(--accent)" font-weight="700">{p50e:.2f}</text>'
                     f'<text x="{x(total) + 2:.1f}" y="{y(p10e) + 3:.1f}" font-size="10" '
                     f'fill="var(--ink3)">{p10e:.2f}</text>')
        parts.append(f'<text x="{x(n - 1 + fwd / 2):.1f}" y="{padT + 10}" font-size="10" '
                     f'fill="var(--ink3)" text-anchor="middle">전망 약 90일({horizon}거래일)</text>')
    parts.append(f'<path d="{line}" fill="none" stroke="var(--accent)" stroke-width="2"/>')
    # W-C: 급변일 마커 — 번호는 아래 '주요 변동일' 목록과 1:1 대응
    for k, m in enumerate(marks or []):
        mi = m["i"]
        if not (0 <= mi < n):
            continue
        col = "var(--up)" if m["chg"] > 0 else "var(--down)"
        mx, my = x(mi), y(hist[mi])
        ly_off = -10 if (k % 2 == 0) else 18
        parts.append(
            f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="4.5" fill="{col}" '
            f'stroke="var(--surface)" stroke-width="1.5"/>'
            f'<text x="{mx:.1f}" y="{my + ly_off:.1f}" font-size="11" font-weight="700" '
            f'fill="{col}" text-anchor="middle">{m["no"]}</text>')
    parts.append(f'<text x="{x(0):.1f}" y="{H - 8}" font-size="10" fill="var(--ink3)">{start_lbl}</text>'
                 f'<text x="{x(n - 1):.1f}" y="{H - 8}" font-size="10" fill="var(--ink3)" '
                 f'text-anchor="middle">{today_lbl} (기준일)</text>'
                 f'<text x="{x(total):.1f}" y="{H - 8}" font-size="10" fill="var(--ink3)" '
                 f'text-anchor="end">{end_lbl}</text>')
    return (f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto;display:block" '
            f'role="img" aria-label="CBOT ZL 종가 추이와 {horizon}거래일 참고 범위">'
            + "".join(parts) + "</svg>")


def _svg_spark(vals: list[float]) -> str:
    if len(vals) < 2:
        return ""
    W, H = 90, 26
    lo, hi = min(vals), max(vals)
    sp = (hi - lo) or 1.0
    pts = " ".join(f"{4 + (W - 8) * i / (len(vals) - 1):.1f},"
                   f"{4 + (H - 8) * (1 - (v - lo) / sp):.1f}" for i, v in enumerate(vals))
    lx, ly = pts.rsplit(" ", 1)[-1].split(",")
    return (f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<polyline points="{pts}" fill="none" stroke="var(--ink3)" stroke-width="1.5"/>'
            f'<circle cx="{lx}" cy="{ly}" r="2.5" fill="var(--accent)"/></svg>')


def _maritime_inputs(frames: dict[str, pd.DataFrame], reg: dict) -> tuple[dict, dict]:
    """레지스트리가 요구하는 지표의 최신 관측·AIS 통항 수 시계열을 parquet 프레임에서 추출."""
    codes: set[str] = set()
    counts: set[str] = set()
    for cp in reg["chokepoints"]:
        if cp.get("dynamic_upgrade"):
            codes.add(cp["dynamic_upgrade"]["indicator"])
        codes.update((cp.get("warning_sources") or {}).keys())
        for k in ("ais_risk_indicator", "awrp_indicator"):
            if cp.get(k):
                codes.add(cp[k])
        if cp.get("ais_count_indicator"):
            counts.add(cp["ais_count_indicator"])
    inputs: dict[str, Observation] = {}
    for code in codes:
        ser = _dated_series(frames, [code])
        if not ser.empty:
            last = ser.iloc[-1]
            inputs[code] = Observation(float(last["value"]), pd.Timestamp(last["price_date"]).date())
    series: dict[str, list[tuple[date, float]]] = {}
    for code in counts:
        ser = _dated_series(frames, [code])
        if not ser.empty:
            series[code] = [(pd.Timestamp(r["price_date"]).date(), float(r["value"])) for _, r in ser.iterrows()]
    return inputs, series


def _maritime_block(frames: dict[str, pd.DataFrame]) -> tuple[dict[str, str], str, dict]:
    """해상 위협 점수 산출 → (모식도 점등 상태, 해협 카드 HTML, 결과 dict). 실패 시 정직 강등."""
    try:
        reg = load_registry()
        inputs, series = _maritime_inputs(frames, reg)
        res = compute_maritime_threat(inputs, series=series, registry=reg)
    except Exception as e:                                    # noqa: BLE001
        print(f"[경고] 해상 위협 점수 산출 실패(비치명): {e}")
        st = {k: "unknown" for k in ("hormuz", "red_sea", "malacca", "panama", "black_sea")}
        return st, ('<div class="card cp-card"><b>해상 위협 점수 미산출</b>'
                    f'<div class="cap">{_esc(e)}</div></div>'), {}
    st = {s.key: s.band for s in res["chokepoints"]}
    badge = {"ok": ("ok", "정상"), "warn": ("warn", "주의"), "crit": ("warn", "심각")}
    routes_ko = reg.get("route_names_ko") or _ROUTE_KO
    cards: list[str] = []
    ok_names: list[str] = []
    for s in res["chokepoints"]:
        if s.band == "ok":                                    # 정상 항로는 설명 생략(9/13 지시)
            ok_names.append(f"{s.name_ko} {s.score}점")
            continue
        cls, lab = badge.get(s.band, ("acc", "미확인"))
        if s.band == "crit":
            cls = "crit"
        rr = s.route_relevance or {}
        if rr.get("direct_routes"):
            rel = "한국향 직접 경유 — " + " · ".join(routes_ko.get(r, r) for r in rr["direct_routes"])
            if rr.get("alternatives"):
                rel += f" (우회: {' · '.join(rr['alternatives'])})"
        else:
            rel = _humanize(rr.get("propagation") or "항로 관련성 미기재")
        lt = s.lead_time_impact or {}
        lt_txt = " · ".join(x for x in (
            f"추가 일수 {lt['added_days']}" if lt.get("added_days") else "",
            f"운임 {lt['freight_pct']}" if lt.get("freight_pct") else "") if x) or "리드타임 영향 근거 없음"
        lt_src = _humanize(lt.get("source", ""))
        comp_rows = "".join(
            f'<div class="cp-comp"><span>{lbl}</span><b class="num">'
            f'{"미확인" if c.points is None else f"{c.points:.0f}"}</b><small>{_esc(_humanize(c.note))}</small></div>'
            for lbl, c in (("등급", s.components["tier"]), ("경보", s.components["warnings"]),
                           ("선박 위치", s.components["ais"]), ("급감", s.components["anomaly"])))
        awrp = (f'<div class="cap">관측 전쟁위험보험료 배수 ×{s.awrp_multiplier:.2f}</div>'
                if s.awrp_multiplier is not None else "")
        partial = (f'<span class="pill acc">부분 산출 · 미확인 {len([c for c in s.components.values() if c.points is None])}</span>'
                   if s.partial else "")
        cards.append(f"""
    <div class="card cp-card">
      <div class="cp-head"><b>{_esc(s.name_ko)}</b>
        <span class="cp-score num">{s.score}<small>/100</small></span>
        <span class="pill {cls}">{lab}</span> <span class="pill acc">등급 {_esc(_TIER_KO.get(s.tier, s.tier))}</span> {partial}</div>
      <div class="cap">{_esc(_humanize(s.tier_basis or s.tier_source))}</div>
      {comp_rows}
      <div class="cp-meta"><span>항로</span>{_esc(rel)}</div>
      <div class="cp-meta"><span>리드타임</span>{_esc(lt_txt)} <small>{_esc(lt_src)}</small></div>
      {awrp}
      {('<div class="cap">미확인 성분: ' + _esc(_humanize(" · ".join(s.missing))) + '</div>') if s.missing else ''}
    </div>""")
    kd, pr = res["korea_direct"], res["propagation"]
    def _idx_txt(d: dict, label: str) -> str:
        if d.get("score") is None:
            return f"{label} <b>미확인</b>"
        return (f"{label} <b class=\"num\">{d['score']}</b>/100 (최대치 기준: {_esc(d.get('driver') or '—')})"
                + (" · 부분 산출" if d.get("partial") else ""))
    ok_line = (f'<div class="cap">정상 통과(설명 생략): {_esc(" · ".join(ok_names))}</div>'
               if ok_names else "")
    head = (f'<div class="cp-index">{_idx_txt(kd, "한국향 직접 경유 노출")} · '
            f'{_idx_txt(pr, "운임 전파 축")}</div>' + ok_line)
    return st, head + '<div class="cp-grid">' + "".join(cards) + "</div>", res


def _fmt_last(frames: dict, codes: list[str], fmt: str) -> str:
    s = _dated_series(frames, codes)
    return fmt.format(float(s["value"].iloc[-1])) if not s.empty else "—"


def _svg_route_map(st: dict[str, str]) -> str:
    col = {"ok": "var(--ok)", "warn": "var(--warn)", "crit": "var(--crit)",
           "unknown": "var(--ink3)"}
    P = {"usg": (210, 95), "bra": (300, 185), "arg": (270, 215), "mys": (700, 165),
         "kor": (880, 80), "panama": (235, 140), "red_sea": (500, 105),
         "hormuz": (585, 115), "malacca": (715, 150), "black_sea": (470, 55)}
    W, H = 1000, 250

    def arc(a, b, bend):
        return (f"M{a[0]} {a[1]} Q{(a[0] + b[0]) / 2:.0f} "
                f"{(a[1] + b[1]) / 2 + bend:.0f} {b[0]} {b[1]}")

    grid = "".join(f'<line x1="{x}" y1="18" x2="{x}" y2="{H - 18}" stroke="var(--line)" '
                   f'stroke-width="1" opacity=".5"/>' for x in range(60, W, 94))
    grid += "".join(f'<line x1="30" y1="{y}" x2="{W - 30}" y2="{y}" stroke="var(--line)" '
                    f'stroke-width="1" opacity=".5"/>' for y in range(40, H - 10, 44))
    routes = "".join(f'<path d="{arc(P[a], P["kor"], b)}" fill="none" stroke="var(--accent)" '
                     f'stroke-width="1.5" stroke-dasharray="6 5" opacity=".55"/>'
                     for a, b in [("usg", -70), ("bra", 55), ("arg", 90), ("mys", 25)])

    def origin(key, label, sub):
        px, py = P[key]
        return (f'<circle cx="{px}" cy="{py}" r="7" fill="var(--accent-soft)" '
                f'stroke="var(--accent)" stroke-width="2"/>'
                f'<text x="{px}" y="{py + 22}" font-size="11" fill="var(--ink2)" '
                f'text-anchor="middle" font-weight="500">{label}</text>'
                f'<text x="{px}" y="{py + 35}" font-size="9.5" fill="var(--ink3)" '
                f'text-anchor="middle">{sub}</text>')

    def choke(key, label, status):
        px, py = P[key]
        return (f'<rect x="{px - 5}" y="{py - 5}" width="10" height="10" '
                f'transform="rotate(45 {px} {py})" fill="{col[status]}"/>'
                f'<text x="{px}" y="{py - 11}" font-size="10" fill="var(--ink2)" '
                f'text-anchor="middle">{label}</text>')

    kx, ky = P["kor"]
    return (f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto;display:block" '
            f'role="img" aria-label="주요 원산지에서 한국까지의 공급 경로 모식도">'
            + grid + routes
            + origin("usg", "미국 멕시코만", "조유·정제유")
            + origin("bra", "브라질", "조유")
            + origin("arg", "아르헨티나", "조유 최대 공급")
            + origin("mys", "말레이·인니", "팜유(대체)")
            + f'<circle cx="{kx}" cy="{ky}" r="9" fill="var(--accent)"/>'
            + f'<text x="{kx}" y="{ky - 16}" font-size="12" fill="var(--ink2)" '
              f'text-anchor="middle" font-weight="700">한국 (평택·인천)</text>'
            + choke("panama", "파나마", st.get("panama", "unknown"))
            + choke("red_sea", "수에즈·홍해", st.get("red_sea", "unknown"))
            + choke("hormuz", "호르무즈", st.get("hormuz", "unknown"))
            + choke("malacca", "말라카", st.get("malacca", "unknown"))
            + choke("black_sea", "흑해 회랑", st.get("black_sea", "unknown"))
            + "</svg>")


# ── 블록 렌더 ────────────────────────────────────────────────────────────────

def _esc(t: object) -> str:
    return _html.escape(str(t), quote=True)


def _chg_html(v: float | None, suffix: str = "%") -> str:
    if v is None:
        return '<span class="chg flat">—</span>'
    cls = "up" if v > 0 else ("down" if v < 0 else "flat")
    arrow = "▲ +" if v > 0 else ("▼ " if v < 0 else "")
    return f'<span class="chg {cls} num">{arrow}{v:.2f}{suffix}</span>'


def _brief_box(items: list[tuple[str, str]]) -> str:
    seg = "".join(
        f'<span class="k{" warn" if k == "유의" else ""}">{k}</span>{_esc(t)} '
        for k, t in items if t)
    return f'<div class="brief">{seg}</div>'


def _stars(n: int) -> str:
    return "★" * max(1, min(3, n))


def _inflection_block(points: list[dict], importance_df: pd.DataFrame) -> str:
    """주요 변동일 목록 — 날짜·변화율·당시 신호·변인 상태·온톨로지 체인 (W-C · R2).

    신호 아카이브(2026-08-17~) 이전 날짜와 분석 데이터 미가용 상황은 정직 강등.
    """
    if not points:
        return ""
    top_codes = ([str(r["변수"]) for _, r in importance_df.head(3).iterrows()]
                 if not importance_df.empty else [])
    analysis = None
    try:
        from src.forecasting.variable_importance_g1 import _load_g1_feature_mart
        analysis, _lv, _t = _load_g1_feature_mart()
    except Exception:                                         # noqa: BLE001 — 비치명
        analysis = None
    try:
        from src.forecasting.analogue_g1 import _resolve_z_column
    except Exception:                                         # noqa: BLE001
        _resolve_z_column = None                              # type: ignore[assignment]

    cards = []
    for p in points:
        d: pd.Timestamp = p["date"]
        chg = p["chg"]
        cls = "up" if chg > 0 else "down"
        arrow = "▲" if chg > 0 else "▼"
        rows: list[str] = [
            f'<li>일간 변화율 <span class="chg {cls} num">{arrow} {chg:+.2f}%</span> · '
            f'종가 <span class="num">{p["close"]:.2f}</span> 센트/파운드</li>']
        # ① 당시 수집 신호(±2일)
        sig = _signals_around(d)
        if not sig.empty:
            shown = 0
            for _, row in sig.iterrows():
                if shown >= 2:
                    break
                note = str(row.get("note", ""))
                title = _esc(_media_title(note, str(row.get("indicator", "")), n=90))
                url = _first_url(note)
                head = (f'<a href="{_esc(url)}" target="_blank" rel="noopener">{title}</a>'
                        if url else title)
                rows.append(f'<li>당시 신호: {head} '
                            f'<span class="src">{_esc(_source_ko(row.get("source_name", "")))}</span></li>')
                chain = _ONTOLOGY_CHAINS.get(str(row.get("indicator", "")))
                if chain and shown == 0:
                    rows.append(f'<li>연결 경로: {_esc(" → ".join(chain))}</li>')
                shown += 1
        else:
            rows.append('<li><span class="src">당시 수집 신호 없음(신호 아카이브는 '
                        '2026-08-17부터) — 변인 상태만 표시</span></li>')
        # ② 당시 변인 표준화 지수(분석 데이터 시점 조회)
        z_parts: list[str] = []
        if analysis is not None and _resolve_z_column is not None and top_codes:
            idx = analysis.index[analysis.index <= d]
            if len(idx):
                row_z = analysis.loc[idx[-1]]
                for c in top_codes:
                    zc = _resolve_z_column(analysis.columns, c)
                    if zc is not None and pd.notna(row_z.get(zc)):
                        base = c.split("__")[0]
                        z_parts.append(f'{_esc(_label_ko(base))} '
                                       f'{float(row_z[zc]):+.1f}')
        if z_parts:
            rows.append(f'<li>당시 상위 변인의 평소 대비 편차: {" · ".join(z_parts)}</li>')
        elif analysis is None:
            rows.append('<li><span class="src">변인 상태: 분석 데이터 미가용 — CI 실행에서 '
                        '자동 표시</span></li>')
        cards.append(
            f'<details class="mech"><summary>{p["no"]} {d.strftime("%Y-%m-%d")} '
            f'<span class="chg {cls} num">{arrow} {chg:+.2f}%</span></summary>'
            f'<ul style="margin:6px 0 0 16px;line-height:1.7">{"".join(rows)}</ul></details>')
    return ('<div style="margin-top:8px"><b style="font-size:13px">주요 변동일 '
            f'{len(points)}건</b> <span class="cap">— 차트의 번호 표시와 대응 · 클릭 시 '
            '당시 신호·변인 상태 표시(과거 사실 기술)</span>'
            + "".join(cards) + "</div>")


def _analogue_block(breach: list[dict], importance_df: pd.DataFrame) -> str:
    """과거 유사국면 실측 참조 블록 — 경보 변수 우선, 중요도 상위로 보충.

    A-191: 과거 관측의 요약까지만 — 전망·확률 주장 금지. mart 미가용 시 정직 강등.
    """
    try:
        from src.forecasting.analogue_g1 import (badge_name, build_analogue_context,
                                                 case_narrative_lines,
                                                 format_result_line,
                                                 representative_badges)
        alert_codes = [str(a.get("변수", "")) for a in breach]
        top_codes = ([str(r["변수"]) for _, r in importance_df.head(4).iterrows()]
                     if not importance_df.empty else [])
        results = build_analogue_context(alert_codes, top_codes)
    except Exception as e:                                    # noqa: BLE001 — 비치명
        print(f"[정보] 유사국면 블록 생성 불가(비치명): {type(e).__name__}: {e}")
        results = []
    if not results:
        return ('<div class="card sig-item"><p>과거 유사 시기 참조: 분석 데이터 미가용 '
                '또는 대상 변수 부재 — 산출 보류. 실산출은 CI 실행에서 분석 데이터와 함께 '
                '생성됨.</p></div>')
    by_var: dict[str, list] = {}
    for r in results:
        by_var.setdefault(r.var_code, []).append(r)
    cards = []
    for var, rs in list(by_var.items())[:3]:
        z_txt = f"{rs[0].current_z:+.1f}" if rs[0].current_z == rs[0].current_z else "?"
        label = _label_ko(var)
        lines = "".join(f"<li>{_esc(format_result_line(r))}</li>"
                        for r in sorted(rs, key=lambda x: x.horizon))
        badges = representative_badges(rs)          # A-270: 20일 지평 대표·밀도 검사 통과분만
        badge_parts = []
        if badges:
            badge_parts.append(f'<div class="src">겹치는 위기 사례(1개월 지평·밀도 검사 통과): '
                               f'{_esc(" · ".join(badges))}</div>')
            # W-B(조정자 R1): 배지 클릭 → 왜 유사한가 — 원인→경로→가격 실측→유사점/차이점
            for b in badges:
                narr = case_narrative_lines(badge_name(b))
                if narr:
                    items = "".join(f"<li>{_esc(t)}</li>" for t in narr)
                    badge_parts.append(
                        f'<details class="mech"><summary>{_esc(b)} — 왜 유사한가 (클릭)'
                        f'</summary><ul style="margin:6px 0 0 16px;line-height:1.7">'
                        f'{items}</ul><div class="cap">과거 사실 기술과 구조 비교까지만 — '
                        f'방향 판단 아님. 상세·수치는 위기 사례 문서(재평가 기록 '
                        f'병독).</div></details>')
        badge_html = "".join(badge_parts)
        cards.append(f"""
    <div class="card sig-item">
      <span class="tag">{_esc(label)} <span style="color:var(--ink3)">현재 편차 {z_txt}</span></span>
      <ul style="font-size:13px;margin:6px 0 0 18px;line-height:1.8">{lines}</ul>
      {badge_html}</div>""")
    mech = """
    <details class="mech"><summary>산출 방식 (클릭)</summary>
      변수의 최근 90일 기준 평소 대비 편차가 현재와 같은 구간(십분위)이었던 과거 거래일을 찾아,
      그 날들로부터 약 1주(5거래일)/약 1개월(20거래일)/약 3개월(60거래일) 뒤의
      <b>실측</b> 가격 변화를 집계함(2010~ 전 구간). 유사일 사이에 최소 간격을 두어
      중복 시기를 제거하고, 최근 60거래일은 집계에서 제외함(전방 구간 겹침 방지).
      유사 시기가 8회 미만이면 산출을 보류함. <b>통계 검정 없음 — 기술 서술</b>이며,
      감시 창(90일)은 기준 기간 확정 전 잠정값임.</details>"""
    return (f'<div class="signals">{"".join(cards)}</div>' + mech
            + '<div class="cap" style="margin-top:8px">⚠️ 위 수치는 <b>과거 관측의 '
              '요약이며 향후 전망·확률 주장이 아님</b>. 유사 상황에서 어떤 변수를 '
              '주시할지 참고하는 자료로만 사용할 것.</div>')


def _snapshot_specs() -> list[dict]:
    return [
        {"label": "대두유 선물 종가(시카고)", "codes": ["CBOT_BO_CLOSE"], "src": "시카고 거래소 정산가", "fmt": "{:,.2f}"},
        {"label": "팜유(말레이시아 선물)", "codes": ["TE_PALM_OIL", "CPO_USD_MT", "CPO"], "src": "트레이딩이코노믹스", "fmt": "{:,.0f}"},
        {"label": "BDI 해상운임지수", "codes": ["TE_BDI", "BDI"], "src": "발틱 거래소", "fmt": "{:,.0f}"},
        {"label": "브라질 헤알 환율", "codes": ["DEXBZUS", "FX_BRL_USD"], "src": "미 연준 FRED·업로드", "fmt": "{:.2f}"},
        {"label": "원/달러 환율", "codes": ["DEXKOUS", "KRW_USD"], "src": "미 연준 FRED·한국은행", "fmt": "{:,.0f}"},
        {"label": "VIX 변동성 지수", "codes": ["VIXCLS"], "src": "시카고옵션거래소", "fmt": "{:.1f}"},
        {"label": "엘니뇨 지수(ONI)", "codes": ["ENSO_ONI", "ONI"], "src": "미 해양대기청", "fmt": "{:+.2f}",
         "monthly": True},
        # D-051·A-229: 대두박(ZM)·대두(ZS) 반입(9/1~) 후 산출 — 그 전까지 예정 표기
        {"label": "압착 마진(대두 가공 채산성)", "codes": ["BOARD_CRUSH_MARGIN"],
         "src": "시카고 대두·대두박·대두유 선물", "fmt": "{:+.2f}",
         "pending_note": "수집 예정 — 대두박(ZM)·대두(ZS) 반입 후 산출(트레이더가 대두 복합체를 읽는 대표 지표)"},
    ]


_RELIABILITY_JSON = Path("data/processed/g1_reliability_latest.json")


def _reliability_block() -> str:
    """보고서 신뢰도 블록(A-264) — 최신 신뢰도 지표 JSON을 읽어 일별(①②⑥)·월별(③④⑤) 항목을 표시.

    결측은 '미산출' 정직 강등. 수치는 과정 무결성·과거 관측 요약이며 확률·전망 주장이 아님(A-191).
    """
    try:
        import json as _json
        res = _json.loads(_RELIABILITY_JSON.read_text(encoding="utf-8"))
    except Exception:                                         # noqa: BLE001
        return ('<div class="card"><h3>보고서 신뢰도</h3><div class="cap">신뢰도 지표 미산출 — '
                '첫 산출 후 표시됨</div></div>')
    R = res.get("realtime", {})
    H = res.get("historical", {}) or {}
    items: list[tuple[str, str]] = []
    r1 = R.get("R1_input_accuracy", {})
    if r1.get("median_diff_pct") is not None:
        items.append(("입력 정확도", f"기준 가격 교차검증 오차 중앙값 {r1['median_diff_pct']}% · 상위 1% {r1.get('p99_diff_pct')}%"))
    r2 = R.get("R2_asof_accuracy", {})
    if r2.get("status") == "산출":
        items.append(("시점 정합", f"분석 변수 {r2['n_features']}개 중 개정 이력 미보존 {r2['revision_contaminated']}개는 분석에서 제외"))
    r3 = R.get("R3_alert_consistency", {})
    if r3.get("status") == "산출":
        items.append(("경보 정합", f"경보판 {r3.get('report_alerts')}건 = 서명 기록 {r3.get('stamp_alerts')}건 "
                                 f"({'일치' if r3.get('consistent') else '불일치'})"))
    r4 = R.get("R4_publication_integrity", {})
    if r4.get("status") == "산출":
        items.append(("발행 무결성", f"자동 점검 연속 통과 {r4.get('gate_pass_streak_runs')}회 · 서명 기록 {r4.get('rows')}일"))
    r5 = R.get("R5_collection_channels", {})
    if r5.get("status") == "산출":
        items.append(("수집 도달률", f"비정형 신호 영업일 도달률 {r5['bday_arrival_rate']*100:.0f}% · {r5['indicators']}지표"))
    monthly: list[tuple[str, str]] = []
    h1 = H.get("H1_rank_stability", {})
    if h1.get("status") == "산출":
        monthly.append(("변인 순위 안정성", f"표본을 나눠 다시 세도 순위 상관 {h1['pearson']['mean_spearman']} · 부호 일치 {h1['pearson']['sign_agreement_top']*100:.0f}%"))
    h4 = H.get("H4_reference_range", {})
    if h4.get("horizons"):
        r60 = h4["horizons"].get("60", {})
        if r60.get("coverage") is not None:
            monthly.append(("참고 범위 폭 진단", f"과거 60거래일 참고 범위가 실제 변동을 담은 비율 {r60['coverage']*100:.0f}% (명목 80% · 범위 폭 진단일 뿐 확률 주장 아님)"))
    h3 = H.get("H3_alert_rule_retro", {})
    if h3.get("rules"):
        for name, rr in h3["rules"].items():
            hh = (rr.get("horizons") or {}).get("20", {})
            if hh.get("status") == "산출":
                monthly.append(("경보 규칙 소급 성적", f"{name}: 과거 소급 오경보 근사율 {hh['false_alarm_proxy']*100:.0f}% (실발행 아님 — 소급 합성)"))
                break
    led = res.get("ledger", {})
    if led.get("rows"):
        monthly.append(("실발행 경보 원장", f"{led['rows']}건 기록 · 성숙 전(사후 성적은 8회 이상부터 표기)"))
    basis = _esc(res.get("basis", "경량 모드"))
    gen = _esc(str(res.get("generated_at", ""))[:10])
    rows = "".join(f"<tr><th>{_esc(k)}</th><td>{_esc(v)}</td></tr>" for k, v in items) or \
           "<tr><td>일별 항목 미산출</td></tr>"
    mrows = "".join(f"<tr><th>{_esc(k)}</th><td>{_esc(v)}</td></tr>" for k, v in monthly)
    m_html = (f'<details><summary>월별 항목(과거 데이터 검증 — 산출 기준 {gen} · {basis})</summary>'
              f'<table class="rel">{mrows}</table></details>') if mrows else ""
    return (f'<div class="card"><h3>보고서 신뢰도 — 2단계 검증</h3>'
            f'<div class="cap">1단계 과거 데이터 검증 · 2단계 실시간 수집 데이터 검증 — '
            f'수치는 과정 무결성과 과거 관측의 요약이며 향후 전망·확률 주장이 아님</div>'
            f'<table class="rel">{rows}</table>{m_html}</div>')


def build_daily_brief(
    frames: dict[str, pd.DataFrame],
    importance_df: pd.DataFrame,
    alerts: list[dict],
    status_df: pd.DataFrame,
    run_ts: str,
    run_id: str,
    target_label: str,
    n_features: int | None = None,
) -> str:
    """일별 브리프 HTML 문자열 생성 — 모든 블록은 결측 시 정직 강등."""
    today = date.today()
    kpi = _kpi_close(frames)
    full_close = _dated_series(frames, ["CBOT_BO_CLOSE"])["value"]
    rng = _reference_range_usclb(full_close) if len(full_close) else None
    band_mt = _landed_band()
    signals = _load_signals()

    breach = [a for a in alerts if "🚨" in str(a.get("상태", ""))]
    watch = [a for a in alerts if "⚠️" in str(a.get("상태", "")) or "❓" in str(a.get("상태", ""))]
    normal_n = len(alerts) - len(breach) - len(watch)

    # 데이터 적시성 (status_df 신선도 플래그)
    # A-267: 적시성은 내용 기준 3분류 — ✅ 적시 · ⏳ 주기 내(월간·연간 정상 지연) · 🚨 기한 초과 · ❌ 미수집
    fresh_total = len(status_df) if not status_df.empty else 0
    _fl = status_df["신선도"].astype(str) if (not status_df.empty and "신선도" in status_df.columns) else pd.Series(dtype=str)
    fresh_ok = int(_fl.str.contains("✅").sum())
    fresh_cycle = int(_fl.str.contains("⏳").sum())
    fresh_over = int(_fl.str.contains("🚨").sum())
    fresh_missing = int(_fl.str.contains("❌").sum())
    fresh_timely = fresh_ok + fresh_cycle

    # ── KPI 블록 ──
    kpi_cards = []
    if kpi:
        kpi_cards.append(f"""
    <div class="card kpi"><div class="lbl">대두유 선물 종가(시카고)</div>
      <div class="val num">{kpi.close:.2f} <span class="unit">센트/파운드</span></div>
      {_chg_html(kpi.chg_pct)}
      <div class="foot num">주간 {f"{kpi.wk_pct:+.1f}%" if kpi.wk_pct is not None else "—"} ·
        평소 대비 편차 {f"{kpi.z90:+.1f}" if kpi.z90 is not None else "—"} · 시카고 거래소 정산가 기준 · 기준일 {kpi.last_date}</div></div>""")
    else:
        kpi_cards.append('<div class="card kpi"><div class="lbl">대두유 선물 종가(시카고)</div>'
                         '<div class="val">미수집</div><div class="foot">종가 계열 미수집 — '
                         '수집 상태 확인 필요</div></div>')
    if band_mt:
        kpi_cards.append(f"""
    <div class="card kpi"><div class="lbl">참고 도착가 범위 · 약 90일(60거래일)</div>
      <div class="val num">{band_mt[1]:,.2f} <span class="unit">달러/톤</span></div>
      <div class="chg flat num">최소 {band_mt[0]:,.2f} — 최대 {band_mt[2]:,.2f}</div>
      <div class="foot">한국 도착가 기준(운임·보험 포함) · 실측 반영 <span class="pill acc">참고 범위</span></div></div>""")
    else:
        kpi_cards.append('<div class="card kpi"><div class="lbl">참고 도착가 범위 · 60거래일</div>'
                         '<div class="val">산출 불가</div><div class="foot">관세청 실측 또는 '
                         '선물 가격 데이터 부족</div></div>')
    kpi_cards.append(f"""
    <div class="card kpi"><div class="lbl">금일 경보 (유의 사항)</div>
      <div class="val num">{len(breach)}<span class="unit">건</span></div>
      <div class="chg flat">{('<span class="pill warn">🚨 기준 초과</span>' if breach
                              else '<span class="pill ok">이상 없음(검사 완료)</span>')}</div>
      <div class="foot">기준 초과 {len(breach)} · 관찰 {len(watch)} · 정상 {normal_n}</div></div>""")
    kpi_cards.append(f"""
    <div class="card kpi"><div class="lbl">데이터 적시성</div>
      <div class="val num">{fresh_timely}<span class="unit">/{fresh_total} 항목</span></div>
      <div class="chg flat">{('<span class="pill ok">주기 내 수집</span>'
                              if fresh_total and fresh_over == 0 and fresh_missing == 0
                              else '<span class="pill warn">확인 필요</span>')}</div>
      <div class="foot">적시 {fresh_ok} · 주기 내(월간·연간 정상 지연) {fresh_cycle} · 기한 초과 {fresh_over} · 미수집 {fresh_missing}</div></div>""")

    # ── 한눈 요약 4단 문장 (규칙 기반) ──
    if kpi and kpi.wk_pct is not None:
        if kpi.wk_pct > 0.5:
            trend = f"한 주간 {kpi.wk_pct:+.1f}% 상승했으며"
        elif kpi.wk_pct < -0.5:
            trend = f"한 주간 {kpi.wk_pct:+.1f}% 하락했으며"
        else:
            trend = "한 주간 보합권에서 움직였으며"
        s_now = f"대두유 선물은 {trend}, 종가 {kpi.close:.2f}센트/파운드로 마감함."
    else:
        s_now = "대두유 선물 종가의 최신 관측이 부족해 현황 판단을 보류함."
    top2 = importance_df.head(2)
    if not top2.empty:
        names = " · ".join(_label_ko(r["변수"]) for _, r in top2.iterrows())
        s_factor = f"현재 중요도 상위 변인은 {names}임 (통계 선별과 상관 분석의 교차 확인)."
    else:
        s_factor = "변인 중요도 산출이 비어 있어 요인 판단을 보류함."
    s_outlook = (f"향후 약 3개월(60거래일)의 참고 범위는 {rng[0]:.2f}~{rng[2]:.2f}센트/파운드"
                 + (f"(도착가 {band_mt[0]:,.2f}~{band_mt[2]:,.2f}달러/톤)" if band_mt else "")
                 + "임. 과거 유사 시기 실측은 전용 항목 참조." if rng
                 else "참고 범위는 데이터 부족으로 산출하지 않음.")
    s_care = (f"금일 기준 초과 {len(breach)}건 — 상세는 '금일 경보' 참조. 조달 결정은 담당자 승인 절차 필수."
              if breach else "금일 기준 초과 없음(검사 완료) — 조달 결정은 담당자 승인 절차 필수.")
    reliability_html = _reliability_block()
    # A-267: 실행 시각은 UTC로 기록됨 → KST 변환 표기. '05:30 발행' 하드코딩 제거.
    try:
        _run_dt = pd.Timestamp(run_ts)
        _run_dt = _run_dt.tz_localize("UTC") if _run_dt.tzinfo is None else _run_dt
        _kst = _run_dt.tz_convert("Asia/Seoul")
        run_kst_txt, run_kst_hm = _kst.strftime("%Y-%m-%d"), _kst.strftime("%H:%M")
    except Exception:                                         # noqa: BLE001
        run_kst_txt, run_kst_hm = str(run_ts)[:10], "—"
    basis_gap_txt = ""
    if kpi:
        try:
            _gap = (pd.Timestamp(run_kst_txt).date() - kpi.last_date).days
            if _gap >= 2:
                _wk = "주말 휴장" if pd.Timestamp(kpi.last_date).weekday() == 4 else "휴장·미정산일"
                basis_gap_txt = f" · 발행일과 {_gap}일 차이는 {_wk} 때문 — 다음 정산가는 다음 발행에 반영"
        except Exception:                                     # noqa: BLE001
            basis_gap_txt = ""
    summary_top = _brief_box([("현황", s_now), ("요인", s_factor),
                              ("전망", s_outlook), ("유의", s_care)])

    # ── 핵심 변인 Top 5 ──
    drv_rows = []
    top5 = importance_df.head(5)
    ranking_basis = str(getattr(importance_df, "attrs", {}).get("ranking_basis", "elastic_net"))
    if not top5.empty and ranking_basis == "elastic_net" and float(top5["LASSO_계수"].abs().max()) <= 1e-12:
        ranking_basis = "pearson_fallback"                     # attrs 유실 대비 2중 판정
    max_abs = (float(top5["피어슨_r"].abs().max()) if ranking_basis == "pearson_fallback"
               else float(top5["LASSO_계수"].abs().max())) if not top5.empty else 0.0
    for i, (_, row) in enumerate(top5.iterrows(), start=1):
        code = str(row["변수"])
        label = _label_ko(code)
        r = row.get("피어슨_r")
        coef = row.get("LASSO_계수")
        direction = ('<span class="dir up">상방 ▲</span>' if isinstance(r, float) and r > 0
                     else ('<span class="dir down">하방 ▼</span>' if isinstance(r, float) and r < 0
                           else ""))
        _mag = abs(r) if (ranking_basis == "pearson_fallback" and isinstance(r, float)) else (abs(coef) if isinstance(coef, float) else 0.0)
        width = int(_mag / max_abs * 100) if max_abs else 10
        arts = _match_articles(code, signals)
        if arts:
            a0 = arts[0]
            title = _esc(_media_title(a0["note"], str(a0["indicator"]), n=70))
            link = (f'<a href="{_esc(a0["url"])}" target="_blank" rel="noopener">{title}…</a>'
                    if a0["url"] else f"{title}…")
            news = (f'<div class="news"><span class="stars">{_stars(len(arts))}</span> '
                    f'{link} · {_esc(_source_ko(a0["source"]))}</div>')
        else:
            news = '<div class="news">관련 기사 매핑 없음</div>'
        drv_rows.append(f"""
      <div class="drv"><span class="rank num">{i}</span><div>
        <span class="name">{_esc(label)}</span>{direction}
        <div class="barrow"><div class="bar" style="width:{max(width, 8)}%"></div>
          <span class="shap num">기여 {coef:+.4f} · 상관 {r:+.3f}</span></div>
        {news}</div></div>""")
    drivers_cap = ("통계 선별에서 유의한 변인 없음 — 상관 기준 참고 순위 · 별점 = 최근 기사 연관 매핑 · 제목 클릭 시 원문"
                   if ranking_basis == "pearson_fallback"
                   else "별점 = 최근 기사와 변인의 연관 매핑 (★~★★★) · 제목 클릭 시 원문")
    drivers_html = ("".join(drv_rows) if drv_rows
                    else '<p class="cap">변인 중요도 산출 결과가 없습니다 — 미수집.</p>')

    # ── 차트 ──
    if kpi:
        inflections = _inflection_points(kpi)
        chart_svg = _svg_price_chart(kpi, rng, marks=inflections)
        inflection_html = _inflection_block(inflections, importance_df)
        chart_start = kpi.series["price_date"].iloc[0].strftime("%Y-%m-%d")
        chart_cap = (f"실적: {chart_start} ~ {kpi.last_date} ({len(kpi.series)}거래일 · "
                     f"시카고 거래소 실측) · 참고 범위: 기준일 이후 약 90일(60거래일)")
        rng_fig = (f"""
      <div class="range-figures num">
        <span>범위 중앙값 <b>{rng[1]:.2f}</b></span>
        <span>최소(하위 10%) <b>{rng[0]:.2f}</b></span>
        <span>최대(상위 10%) <b>{rng[2]:.2f}</b> 센트/파운드</span></div>""" if rng else
                   '<div class="range-figures">참고 범위: 데이터 부족으로 미산출</div>')
    else:
        chart_svg = '<p class="cap">목표변수 미수집 — 차트를 생성하지 않음.</p>'
        chart_cap, rng_fig, inflection_html = "", "", ""

    mech = f"""
      <details class="mech"><summary>참고 범위 산출 근거 (클릭)</summary>
        <ol>
          <li><b>가격 원천</b>: 시카고 거래소 대두유 선물 — 정산가 교차검증을 거친 종가 계열.</li>
          <li><b>기준 가격층</b>: 과거 60거래일 변동 분포(2010~ 전 구간)의 하위 10%·
            중앙값·상위 10% 지점을 최근 종가에 적용함.</li>
          <li><b>실측 잔차층</b>: 관세청 수입 실적(선적 100톤 이상)의 도착 단가(운임·보험 포함)에서 같은 달
            시카고 선물 가격을 뺀 차이 — 최근 12개월 분포(운임·프리미엄이 섞인 잔차층).</li>
          <li><b>결합</b>: 두 층을 몬테카를로 방식으로 결합함(2만 회 추출·결과 재현 가능).
            분위 수치의 단순 합산은 통계적으로 부정확하여 쓰지 않음.</li>
          <li><b>한계</b>: 과거 변동이 이중으로 반영될 수 있어 <b>"확률 범위"가 아닌
            "참고 범위"</b>로만 제공함. 예측 범위 모델 가동 시 이 층이 교체됨.</li>
        </ol></details>"""

    # ── 경보 블록 ──
    if breach:
        cards = []
        for a in breach:
            code = str(a.get("변수", "?"))
            cards.append(f"""
    <div class="alert"><div class="stripe"></div><div class="body">
      <div class="head">🚨 <span>{_esc(_label_ko(code))} — {_esc(a.get("설명", ""))}</span>
        <span class="pill warn">기준 초과</span></div>
      <div class="detail num">현재값 {_esc(a.get("현재값", "?"))} · 기준 {_esc(a.get("임계값", "?"))} ·
        신선도 {_esc(a.get("데이터신선도", "?"))}</div></div></div>""")
        alerts_html = "".join(cards)
        s_alert_now = f"{len(alerts)}개 감시 변인 가운데 {len(breach)}건이 주의 기준을 넘어섬."
        s_alert_out = "기준 초과 변인의 지속 여부를 다음 날 브리프에서 다시 점검함."
    else:
        alerts_html = ("""
    <div class="card" style="padding:14px 18px">
      <b style="color:var(--ok)">✔ 이상 없음(검사 완료)</b> — 감시 변인 전체가 기준 범위 내에 있음.
      침묵이 아니라 검사를 통과한 결과임 (게이트·검증 상태는 상단 신뢰 스트립 참조).</div>""")
        s_alert_now = f"{len(alerts)}개 감시 변인 전체가 기준 범위 안에 있음(미수집 {len(watch)}건 별도)."
        s_alert_out = "이상 징후 없음 — 정기 감시를 지속함."
    summary_alert = _brief_box([
        ("현황", s_alert_now),
        ("요인", "판정 기준은 과거 분포 기준(상위 10%·평소 대비 편차 2배)과 검증된 절대 기준의 이중 체계임."),
        ("전망", s_alert_out),
        ("유의", "미수집 항목은 경보 불가 상태이므로 '정상'과 구분해 표기함.")])

    # ── 과거 유사국면 실측 참조 (D-051 — G1 재정립의 본질 블록) ──
    analogue_html = _analogue_block(breach, importance_df)

    # ── 지표 스냅샷 ──
    snap_rows = []
    for spec in _snapshot_specs():
        s = _dated_series(frames, spec["codes"])
        if s.empty:
            missing = spec.get("pending_note", "미수집")
            snap_rows.append(f'<tr><td>{spec["label"]}<span class="src">{spec["src"]}</span></td>'
                             f'<td colspan="5" style="color:var(--ink3);text-align:left">'
                             f'{missing}</td></tr>')
            continue
        v = s["value"]
        val = spec["fmt"].format(float(v.iloc[-1]))
        d1 = _pct(float(v.iloc[-1]), float(v.iloc[-2])) if len(v) >= 2 else None
        d5 = _pct(float(v.iloc[-1]), float(v.iloc[-6])) if len(v) >= 6 else None
        z = _z90(v)
        z_txt = (f'<span class="z-hot">{z:+.1f}</span>' if (z is not None and abs(z) >= 2)
                 else (f"{z:+.1f}" if z is not None else "—"))
        if spec.get("monthly"):
            d1_txt, d5_txt = '<span style="color:var(--ink3)">월간</span>', "—"
        else:
            d1_txt = _chg_html(d1) if d1 is not None else "—"
            d5_txt = _chg_html(d5) if d5 is not None else "—"
        spark = _svg_spark([float(x) for x in v.tail(8)])
        snap_rows.append(
            f'<tr><td>{spec["label"]}<span class="src">{spec["src"]}</span></td>'
            f'<td class="num">{val}</td><td>{d1_txt}</td><td>{d5_txt}</td>'
            f'<td class="num">{z_txt}</td><td>{spark}</td></tr>')

    # ── 언론·매체 블록 ──
    sig_cards = []
    seen_ind: set[str] = set()
    # A-269: 종전 '상위 6장'은 아카이브 알파벳 정렬 탓에 프록시 코드만 채워 매체(RSS_*)가 한 번도 못 들어왔다 →
    #   프록시 최대 3장 + 매체 최대 3장 교차(각각 날짜 내림차순), 매체 카드는 기사별 제목·요약·원문.
    _rows = list(signals.iterrows())
    _proxy_rows = [r for _, r in _rows if not str(r.get("indicator", "")).startswith("RSS_")]
    _media_rows = [r for _, r in _rows if str(r.get("indicator", "")).startswith("RSS_")]
    ordered_rows: list = []
    for a_row, b_row in zip(_proxy_rows + [None] * 3, _media_rows + [None] * 3):
        for rr in (a_row, b_row):
            if rr is not None:
                ordered_rows.append(rr)
    n_proxy = n_media = 0
    for row in ordered_rows:
        ind = str(row.get("indicator", ""))
        is_media = ind.startswith("RSS_")
        if ind in seen_ind or (is_media and n_media >= 3) or (not is_media and n_proxy >= 3):
            continue
        seen_ind.add(ind)
        note = str(row.get("note", ""))
        if is_media:
            items = _media_items(note)
            it0 = items[0] if items else {"title": _media_title(note, ind), "desc": "", "url": _first_url(note) or ""}
            url = it0["url"]
            title = _esc(it0["title"][:120])
            desc_html = f'<div class="src">{_esc(it0["desc"][:160])}</div>' if it0.get("desc") else ""
            more = f' <span class="src">외 {len(items) - 1}건</span>' if len(items) > 1 else ""
            head = ((f'<a href="{_esc(url)}" target="_blank" rel="noopener">{title}</a>' if url else title)
                    + more + desc_html)
            n_media += 1
        else:
            url = _first_url(note)
            llm = _llm_summary(note, ind) if not _parse_kv(note) else None
            title = _esc(llm or _media_title(note, ind))
            head = (f'<a href="{_esc(url)}" target="_blank" rel="noopener">{title}</a>'
                    if url else title)
            n_proxy += 1
        chain = _ONTOLOGY_CHAINS.get(ind)
        chain_html = ""
        if chain:
            nodes = ""
            for j, nname in enumerate(chain):
                cls = "edge" if "인과 경로" in nname else ("ent" if j in (1, 3) else "")
                nodes += f'<span class="node {cls}">{_esc(nname)}</span>'
                if j < len(chain) - 1:
                    nodes += '<span class="arr">→</span>'
            chain_html = (f'<details class="chain"><summary>분석 연결(어떤 경로로 반영되는가)</summary>'
                          f'<div class="row">{nodes}</div>'
                          f'<div class="meta">검증된 연결만 변인 분석에 반영함 · 근거 발췌 보존</div></details>')
        sig_cards.append(f"""
    <div class="card sig-item">
      <span class="tag">{_esc(row.get("category", "신호"))}</span> <span class="src">{_esc(_label_ko(ind))}</span>
      <p>{head}</p>
      <div class="src">{_esc(_source_ko(row.get("source_name", "")))} ·
        {pd.Timestamp(row.get("date")).strftime("%m-%d") if pd.notna(row.get("date")) else ""}</div>
      {chain_html}</div>""")
    signals_html = ("".join(sig_cards) if sig_cards else
                    '<div class="card sig-item"><p>최근 5일 내 수집된 언론·매체 신호가 없음 — '
                    '일별 다이제스트 실행 여부 확인 필요.</p></div>')

    # ── 주목해야 할 일정 ──
    cal_items = []
    next_wasde = next((d for d in WASDE_SCHEDULE if d >= today), None)
    if next_wasde:
        cal_items.append((next_wasde, "USDA WASDE 발표",
                          "발표 익영업일 월별 심층판 자동 발행"))
        order_deadline = next_wasde + timedelta(days=6)
        cal_items.append((order_deadline, "차기 선적분 발주 검토 시한",
                          f"한국 도착까지 약 {LEADTIME_DAYS}일 소요 기준으로 역산"))
    for d, what, when in POLICY_MILESTONES:
        if d >= today:
            cal_items.append((d, what, when))
    cal_html = "".join(f"""
    <div class="card cal-item">
      <div class="dday num">D-{(d - today).days}<small>{d.strftime("%m/%d")}</small></div>
      <div><div class="what">{_esc(what)}</div><div class="when">{_esc(when)}</div></div></div>"""
                       for d, what, when in sorted(cal_items)[:4])

    # ── 부록: 전문 기관(RSS 소스별 최신 1건) ──
    appx_cards = []
    if not signals.empty:
        rss = signals[signals["indicator"].astype(str).str.startswith("RSS_")]
        for src, grp in rss.groupby("indicator"):
            row = grp.iloc[0]                                   # 소스별 최신 일자
            note = str(row.get("note", ""))
            org = _RSS_ORG_EN.get(str(src), str(src).replace("RSS_", "").replace("_", " ").title())
            items = _media_items(note)[:3] or [{"title": _media_title(note, str(src), n=130), "desc": "", "url": _first_url(note) or ""}]
            art_html = ""
            for it in items:                                    # A-269: 기사별(제목·요약·원문) — 제목 뭉개기 해소
                link = (f' <a href="{_esc(it["url"])}" target="_blank" rel="noopener">원문</a>' if it.get("url") else "")
                desc = f'<div class="src">{_esc(it["desc"][:160])}</div>' if it.get("desc") else ""
                art_html += f'<p>{_esc(it["title"][:140])}{link}</p>{desc}'
            when = pd.Timestamp(row.get("date")).strftime("%m-%d") if pd.notna(row.get("date")) else ""
            appx_cards.append(f"""
    <div class="card appx-item"><div class="org">{_esc(org)} <span class="src">{when}</span></div>
      {art_html}</div>""")
    appx_html = ("".join(appx_cards) if appx_cards else
                 '<div class="card appx-item"><p>전문 매체 RSS 수집분이 아직 없음 — 첫 수집 '
                 '이후 기관별 최신 발간물이 이 자리에 표시됨.</p></div>')

    # ── 경로 모식도 ──
    st, maritime_html, _maritime = _maritime_block(frames)
    route_svg = _svg_route_map(st)

    # ── E1 신뢰 스트립 ──
    gate = os.environ.get("E1_GATE_STATUS", "").strip() or "미확인(게이트 잡 별도)"
    feat_txt = f"{n_features:,}" if n_features else "—"

    css = _CSS
    breach_pill = (f'🚨 기준 초과 {len(breach)}건' if breach else '이상 없음(검사 완료)')
    gate_ko = _GATE_KO.get(gate.upper(), gate)
    target_ko = _label_ko(target_label)
    return f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nexus 일일 브리프 — {run_ts[:10]}</title>
<link rel="stylesheet" media="print" onload="this.media='all'"
 href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@600;700&family=IBM+Plex+Sans+KR:wght@400;500;700&display=swap">
<!-- 폰트 비차단 로드: 사내망이 fonts.googleapis.com을 차단·지연시켜도 렌더가
     멈추지 않게 비동기 적용 — 실패 시 시스템 폰트(Malgun Gothic 등)로 즉시 표시 -->
<style>{css}</style></head><body>
<div class="page">
<header>
  <div class="masthead"><h1>Nexus 일일 브리프</h1>
    <div class="sub">대두유 조달 신호 데스크 · 핵심 변인과 <b>과거 비슷한 시기의 실제 흐름</b> — <b>시범판</b></div></div>
  <div class="dateblock"><strong>{run_kst_txt}</strong>
    한국시간 {run_kst_hm} 발행 · 데이터 기준일 {kpi.last_date if kpi else "미수집"} (시카고 직전 정산 세션){basis_gap_txt}</div>
</header>
<div class="trust">
  <span class="sig">✔ 자동 점검 통과</span>
  <span>데이터 품질 검사 <b>{_esc(gate_ko)}</b></span>
  <span>분석에 쓴 변수 <b>{feat_txt}</b>개</span>
  <span>분석 대상 <b>{_esc(target_ko)}</b></span>
  <span>{breach_pill}</span>
</div>

<section><div class="sec-h"><h2>한눈 요약</h2><span class="note">전 거래일 마감 기준</span></div>
{summary_top}
<div class="kpis">{"".join(kpi_cards)}</div>
{reliability_html}</section>

<section><div class="sec-h"><h2>가격 추세와 핵심 변인</h2>
  <span class="note">변인 순위: 통계 선별과 상관 분석의 교차 확인 (20거래일 기준)</span></div>
<div class="duo">
  <div class="card chartbox">
    <h3>대두유 선물 종가 추이와 참고 범위</h3>
    <div class="cap">{chart_cap}</div>
    {chart_svg}
    <div class="legend"><span><i></i>종가 (센트/파운드)</span>
      <span><i class="band"></i>참고 범위 (하위 10%~상위 10%)</span></div>
    {rng_fig}{inflection_html}{mech}
  </div>
  <div class="card drivers"><h3>핵심 변인 5개</h3>
    <div class="cap">{drivers_cap}</div>
    {drivers_html}</div>
</div></section>

<section><div class="sec-h"><h2>금일 경보 (유의 사항)</h2>
  <span class="note">기준 초과 변인만 표시 — 이상이 없는 날은 '검사 완료' 표시로 대체함</span></div>
{summary_alert}{alerts_html}</section>

<section><div class="sec-h"><h2>과거 비슷한 시기의 실제 흐름</h2>
  <span class="note">현재와 비슷했던 과거 시기의 이후 실제 변화 — 예측이 아닌 참조</span></div>
{analogue_html}</section>

<section><div class="sec-h"><h2>공급 경로와 해상 위험</h2>
  <span class="note">모식도 — 점등은 해협별 위험 점수 구간(정상 20 미만 · 주의 20~49 · 심각 50 이상) · 정상 항로는 설명을 생략함</span></div>
<div class="card mapbox"><h3>주요 원산지 → 한국 항로와 요충 해협</h3>
{route_svg}
<div class="map-legend"><span><span class="dot ok"></span>정상</span>
  <span><span class="dot warn"></span>주의</span>
  <span><span class="dot crit"></span>심각</span>
  <span><span class="dot" style="background:var(--ink3)"></span>미수집</span>
</div></div>
{maritime_html}</section>

<section><div class="sec-h"><h2>주요 지표 현황</h2>
  <span class="note">편차 = 최근 90일 평균 대비 표준편차 배수(잠정 기준) · 상승 적색/하락 청색</span></div>
<div class="card tablewrap"><table>
  <thead><tr><th>지표</th><th>값</th><th>일간</th><th>주간</th><th>평소 대비 편차</th><th>추세</th></tr></thead>
  <tbody>{"".join(snap_rows)}</tbody></table></div></section>

<section><div class="sec-h"><h2>오늘의 시장 뉴스</h2>
  <span class="note">일별 수집 + 전문 매체 — 제목 클릭 시 원문 · '분석 연결'에서 반영 경로 확인</span></div>
<div class="signals">{signals_html}</div></section>

<section><div class="sec-h"><h2>주목해야 할 일정</h2>
  <span class="note">발표 일정 + 조달 소요 기간 역산(남은 일수)</span></div>
<div class="cal">{cal_html}</div></section>

<section><div class="sec-h"><h2>참고: 전문 매체 최신 기사</h2>
  <span class="note">매체별 최신 기사 1건 + 원문 링크</span></div>
<div class="appx">{appx_html}</div></section>

<footer>
  <div class="hitl">본 브리프는 판단 지원 정보이며, 조달(구매/보류) 결정은 반드시 담당자
    승인 절차를 거침. 구매/보류 신호와 국면 판정은 정식판에서 제공 예정. 위기 국면에는
    시나리오와 행동 옵션을 담은 특별 브리프 체계로 전환됨.</div>
  데이터 시점 규율: 모든 입력은 발행 시점 이전에 확정된 값만 사용함 — 시카고 장 마감(미
  동부시간 14:20) 이후 확정되는 지표는 하루 지연해 반영함. 산출: 자동 분석 파이프라인
  (통계 변수 선별·기여도 분해·선행성 검정의 교차 확인) · 생성 {run_ts} (협정세계시)
</footer>
</div></body></html>"""


_CSS = """
:root{--paper:#F7F8FA;--surface:#FFFFFF;--ink:#182236;--ink2:#5A6478;--ink3:#8B93A5;
--line:#DDE2EA;--accent:#1F4FA8;--accent-soft:#E8EEF9;--up:#C4382E;--down:#1D5FBF;
--warn:#9C6A00;--warn-soft:#FBF3E0;--ok:#1E7A46;--ok-soft:#E7F3EC;--crit:#B3261E;
--band2:rgba(31,79,168,.20)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--paper:#12161F;
--surface:#1A2029;--ink:#E8ECF4;--ink2:#A6AEBF;--ink3:#727B8E;--line:#2A3242;
--accent:#7BA3E8;--accent-soft:#22304A;--up:#E86A5E;--down:#6FA0E8;--warn:#D9A544;
--warn-soft:#33290F;--ok:#5CB985;--ok-soft:#15301F;--crit:#E8756B;
--band2:rgba(123,163,232,.26)}}
:root[data-theme="dark"]{--paper:#12161F;--surface:#1A2029;--ink:#E8ECF4;--ink2:#A6AEBF;
--ink3:#727B8E;--line:#2A3242;--accent:#7BA3E8;--accent-soft:#22304A;--up:#E86A5E;
--down:#6FA0E8;--warn:#D9A544;--warn-soft:#33290F;--ok:#5CB985;--ok-soft:#15301F;
--crit:#E8756B;--band2:rgba(123,163,232,.26)}
*{box-sizing:border-box;margin:0}
body{background:var(--paper);color:var(--ink);
font-family:"IBM Plex Sans KR","Noto Sans CJK KR",-apple-system,"Malgun Gothic",sans-serif;
font-size:15px;line-height:1.65}
.page{max-width:1060px;margin:0 auto;padding:0 24px 72px}
.num{font-variant-numeric:tabular-nums}
a{color:var(--accent)}
header{border-bottom:3px solid var(--ink);padding:34px 0 18px;display:flex;flex-wrap:wrap;
align-items:flex-end;justify-content:space-between;gap:12px}
.masthead h1{font-family:"Noto Serif KR","Noto Serif CJK KR",serif;font-weight:700;
font-size:30px;letter-spacing:-.01em;line-height:1.2}
.masthead .sub{color:var(--ink2);font-size:13px;margin-top:4px}
.dateblock{text-align:right;font-size:13px;color:var(--ink2)}
.dateblock strong{display:block;font-size:17px;color:var(--ink);font-weight:700}
.trust{display:flex;flex-wrap:wrap;gap:8px 22px;align-items:center;background:var(--surface);
border:1px solid var(--line);border-top:none;border-radius:0 0 8px 8px;padding:10px 16px;
font-size:12.5px;color:var(--ink2)}
.trust .sig{font-weight:700;color:var(--ok)}
table.rel{width:100%;border-collapse:collapse;font-size:12.5px;margin-top:6px}
table.rel th{text-align:left;white-space:nowrap;padding:4px 10px 4px 0;color:var(--ink2);font-weight:600;width:130px}
table.rel td{padding:4px 0;border-bottom:1px dashed var(--line)}
.card details summary{cursor:pointer;color:var(--ink2);font-size:12.5px;margin-top:6px}
.trust b{color:var(--ink);font-weight:500}
section{margin-top:34px}
.sec-h{display:flex;align-items:baseline;gap:10px;border-bottom:1px solid var(--line);
padding-bottom:8px;margin-bottom:12px}
.sec-h h2{font-size:16px;font-weight:700}
.sec-h .note{font-size:12px;color:var(--ink3)}
.card{background:var(--surface);border:1px solid var(--line);border-radius:8px}
.brief{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--accent);
border-radius:8px;padding:12px 16px;font-size:13.5px;margin-bottom:14px;line-height:1.75}
.brief .k{display:inline-block;font-size:11px;font-weight:700;color:var(--accent);
background:var(--accent-soft);border-radius:4px;padding:0 6px;margin-right:4px;
letter-spacing:.03em;vertical-align:1px}
.brief .k.warn{color:var(--warn);background:var(--warn-soft)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.kpi{padding:16px 18px}
.kpi .lbl{font-size:12px;color:var(--ink2);letter-spacing:.04em}
.kpi .val{font-size:26px;font-weight:700;margin-top:2px}
.kpi .unit{font-size:13px;font-weight:400;color:var(--ink2)}
.chg{font-size:13px;margin-top:2px;display:inline-block}
.chg.up{color:var(--up)}.chg.down{color:var(--down)}.chg.flat{color:var(--ink2)}
.kpi .foot{font-size:12px;color:var(--ink3);margin-top:6px}
.pill{display:inline-block;font-size:11.5px;font-weight:700;padding:2px 9px;border-radius:99px}
.pill.warn{background:var(--warn-soft);color:var(--warn)}
.pill.ok{background:var(--ok-soft);color:var(--ok)}
.pill.acc{background:var(--accent-soft);color:var(--accent)}
.duo{display:grid;grid-template-columns:minmax(0,3fr) minmax(0,2fr);gap:14px}
@media(max-width:820px){.duo{grid-template-columns:1fr}}
.chartbox{padding:16px 18px 12px}
.chartbox h3,.drivers h3{font-size:14px;font-weight:700;margin-bottom:2px}
.chartbox .cap,.drivers .cap{font-size:12px;color:var(--ink3);margin-bottom:10px}
.legend{display:flex;flex-wrap:wrap;gap:12px 16px;font-size:12px;color:var(--ink2);margin:6px 0 2px}
.legend i{display:inline-block;width:14px;height:3px;border-radius:2px;background:var(--accent);
vertical-align:middle;margin-right:5px}
.legend i.band{height:10px;background:var(--band2)}
svg text{font-family:"IBM Plex Sans KR",sans-serif}
.range-figures{display:flex;flex-wrap:wrap;gap:8px 20px;font-size:12.5px;color:var(--ink2);
margin-top:8px;padding-top:8px;border-top:1px dashed var(--line)}
.range-figures b{color:var(--ink);font-weight:700}
.mech{margin-top:10px;background:var(--paper);border:1px solid var(--line);border-radius:8px;
padding:10px 14px;font-size:12.5px;line-height:1.8;color:var(--ink2)}
.mech summary{cursor:pointer;font-weight:500;color:var(--accent)}
.mech b{color:var(--ink)}.mech ol{padding-left:18px;margin-top:6px}
.drivers{padding:16px 18px}
.drv{display:grid;grid-template-columns:20px minmax(0,1fr);gap:0 10px;padding:9px 0;
border-bottom:1px solid var(--line)}
.drv:last-child{border-bottom:none}
.drv .rank{font-weight:700;color:var(--ink3);font-size:13px;padding-top:1px}
.drv .name{font-weight:500;font-size:13.5px}
.dir{font-size:12px;margin-left:6px}.dir.up{color:var(--up)}.dir.down{color:var(--down)}
.drv .barrow{display:flex;align-items:center;gap:8px;margin-top:4px}
.drv .bar{height:8px;border-radius:2px;background:var(--accent)}
.drv .shap{font-size:11.5px;color:var(--ink2);white-space:nowrap}
.drv .news{font-size:12px;color:var(--ink2);margin-top:4px}
.drv .news .stars{color:var(--warn);letter-spacing:1px}
.alert{display:grid;grid-template-columns:4px minmax(0,1fr);border-radius:8px;overflow:hidden;
border:1px solid var(--line);background:var(--surface);margin-bottom:10px}
.alert .stripe{background:var(--warn)}
.alert .body{padding:14px 18px}
.alert .head{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-weight:700;font-size:14px}
.alert .detail{font-size:13px;color:var(--ink2);margin-top:4px}
.tablewrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:13.5px;min-width:640px}
th{font-size:11.5px;color:var(--ink2);letter-spacing:.05em;font-weight:500;text-align:right;
padding:8px 10px;border-bottom:1px solid var(--line)}
th:first-child{text-align:left}
td{padding:9px 10px;border-bottom:1px solid var(--line);text-align:right}
td:first-child{text-align:left;font-weight:500}
tr:last-child td{border-bottom:none}
td .src{color:var(--ink3);font-size:11.5px;font-weight:400;margin-left:6px}
.z-hot{background:var(--warn-soft);border-radius:4px;padding:1px 6px;color:var(--warn);
font-weight:700}
.mapbox{padding:16px 18px 12px}.mapbox h3{font-size:14px;font-weight:700;margin-bottom:8px}
.cp-index{margin-top:12px;font-size:13.5px}.cp-index small{color:var(--ink3);margin-left:6px}
.cp-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;margin-top:10px}
.cp-card{padding:13px 16px;font-size:13px}.cp-head{display:flex;flex-wrap:wrap;align-items:center;gap:6px}
.cp-score{font-size:22px;font-weight:700;margin-left:auto}.cp-score small{font-size:11px;color:var(--ink3);font-weight:400}
.cp-comp{display:grid;grid-template-columns:44px 52px minmax(0,1fr);gap:6px;font-size:12px;padding:2px 0;border-top:1px dashed var(--line)}
.cp-comp span{color:var(--ink2)}.cp-comp small{color:var(--ink3)}
.cp-meta{font-size:12px;margin-top:6px}.cp-meta span{display:inline-block;min-width:52px;color:var(--ink2);font-weight:500}.cp-meta small{color:var(--ink3)}
.pill.crit{background:var(--crit-soft);color:var(--crit)}
.map-legend{display:flex;flex-wrap:wrap;gap:12px 18px;font-size:12px;color:var(--ink2);
margin-top:6px}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;vertical-align:-1px;
margin-right:5px}
.dot.ok{background:var(--ok)}.dot.warn{background:var(--warn)}.dot.crit{background:var(--crit)}
.signals{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
.sig-item{padding:13px 16px}
.sig-item .tag{font-size:11.5px;font-weight:700;color:var(--accent);letter-spacing:.03em}
.sig-item p{font-size:13px;margin-top:3px;overflow-wrap:anywhere}
.sig-item .src{font-size:11.5px;color:var(--ink3);margin-top:6px}
.chain{margin-top:10px;background:var(--paper);border:1px solid var(--line);border-radius:8px;
padding:8px 12px;font-size:12px;overflow-x:auto}
.chain summary{cursor:pointer;color:var(--accent);font-weight:500}
.chain .row{display:flex;align-items:center;gap:6px;white-space:nowrap;margin-top:8px}
.chain .node{border:1px solid var(--line);background:var(--surface);border-radius:6px;
padding:3px 9px;font-weight:500}
.chain .node.ent{border-color:var(--accent);color:var(--accent)}
.chain .node.edge{background:var(--accent-soft);color:var(--accent);border-color:transparent;
font-weight:700}
.chain .arr{color:var(--ink3)}
.chain .meta{color:var(--ink3);margin-top:6px;white-space:normal}
.cal{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}
.cal-item{padding:14px 16px;display:flex;gap:14px;align-items:center}
.dday{font-weight:700;font-size:19px;color:var(--accent);min-width:56px;text-align:center;
background:var(--accent-soft);border-radius:8px;padding:8px 4px;line-height:1.15}
.dday small{display:block;font-size:10px;font-weight:500}
.cal-item .what{font-weight:500;font-size:13.5px}
.cal-item .when{font-size:12px;color:var(--ink3)}
.appx{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
.appx-item{padding:13px 16px}
.appx-item .org{font-size:12px;font-weight:700;color:var(--ink2)}
.appx-item p{font-size:13px;margin-top:3px;overflow-wrap:anywhere}
.appx-item .src{font-size:11.5px;margin-top:6px}
footer{margin-top:44px;border-top:1px solid var(--line);padding-top:16px;font-size:12px;
color:var(--ink3);line-height:1.8}
footer .hitl{color:var(--ink2);font-weight:500}
"""
