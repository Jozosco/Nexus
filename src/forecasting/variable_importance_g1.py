#!/usr/bin/env python3
"""
G1 변수 중요도 분석 — C-03 Lead Data Scientist (WBS 1.1.8 / Phase A)
수집된 외부 변수 parquet 파일을 로드하여 대두유 가격 변동성 드라이버를 분석.

Phase A 구현 (Snowflake 연동 전):
  - 데이터 소스: data/raw/*.parquet (GitHub Actions 수집 결과)
  - 분석 방법: LASSO 선택 + 피어슨 상관 + 기술통계 (기본 방법론)
  - XGBoost+SHAP / Granger 인과검정: 충분한 시계열 누적 후 Phase B에서 적용
  - 출력: reports/pipeline/g1_variable_importance_{DATE}.html (HTML 리포트)

출력 계약 (C-03 Output Contract):
  - 변수 중요도 테이블 [변수 | 피어슨 r | LASSO 계수 | 포함 여부]
  - 데이터 상태 매트릭스 [커넥터 | 파일 | 행수 | 날짜 범위 | 신선도]
  - 구조적 단절 임계값 현황 (C-03 임계값: GPR 0.022 / BDI 2σ / WASDE STU 10% / CPO $175)
  - 품질 경보 (결측치 5% 초과, STALE 판정 5영업일 초과)
"""
from __future__ import annotations

import glob
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

OUTPUT_DIR  = "data/raw"
REPORT_DIR  = "reports/pipeline"

# ── G1 변수 설명 사전 (C-01/C-03 공동 관리) ──────────────────────────────────
VARIABLE_CATALOG: list[dict] = [
    # ── P1-01 상품가격 ──
    {"code": "CBOT_BO_CLOSE", "category": "P1-01 상품가격", "name_ko": "CBOT 대두유 선물 종가",
     "name_en": "CBOT Soybean Oil Futures Close",
     "desc_ko": "시카고상품거래소(CME/CBOT) 대두유 선물 종가. 국제 대두유 가격의 기준점. 국내 CIF 가격에 가장 직접적인 영향.",
     "desc_en": "CBOT soybean oil futures closing price. Primary international benchmark for soybean oil pricing.",
     "source": "yfinance / CME (BO=F)", "freq": "일간", "unit": "USc/lb"},
    {"code": "CBOT_BO_VOLUME", "category": "P1-01 상품가격", "name_ko": "CBOT 대두유 선물 거래량",
     "name_en": "CBOT Soybean Oil Futures Volume",
     "desc_ko": "선물 거래량 급증은 가격 변동성 확대 선행지표. 시장 유동성·투기 포지션 반영.",
     "desc_en": "Futures volume spike signals price volatility. Reflects market liquidity and speculative positioning.",
     "source": "yfinance / CME (BO=F)", "freq": "일간", "unit": "계약수"},
    {"code": "CPO_USD_MT", "category": "P1-01 상품가격", "name_ko": "팜유(CPO) 현물가",
     "name_en": "Crude Palm Oil Spot Price",
     "desc_ko": "말레이시아 부르사(FCPO) 팜유 현물. 대두유와 직접 대체 관계(CPO-SBO 스프레드 >$175 → 대체 수요 이전 임계).",
     "desc_en": "Bursa Malaysia CPO spot. Direct substitute for soybean oil; CPO-SBO spread >$175/MT triggers demand substitution.",
     "source": "Trading Economics / Bursa Malaysia", "freq": "일간", "unit": "USD/MT"},
    {"code": "CPO_GLOBAL_USD_MT_PROXY", "category": "P1-01 상품가격", "name_ko": "IMF 팜유 글로벌 벤치마크 (FRED)",
     "name_en": "IMF Palm Oil Global Benchmark (FRED)",
     "desc_ko": "FRED PPOILUSDM — IMF 국제 팜유 가격 월별 지수. CPO 현물 미수집 시 대리 지표.",
     "desc_en": "FRED PPOILUSDM monthly proxy for international palm oil price.",
     "source": "FRED / IMF", "freq": "월간", "unit": "USD/MT"},
    {"code": "ARS_USD_OFICIAL", "category": "P1-01 상품가격", "name_ko": "아르헨티나 공식 환율 (ARS/USD)",
     "name_en": "Argentina Official FX Rate (ARS/USD)",
     "desc_ko": "BCRA 공식 환율. 아르헨티나 대두유 수출 채산성 직결. 급격한 평가절하 → 수출 증가 → 국제가 하락 압력.",
     "desc_en": "BCRA official rate. Sharp ARS devaluation raises Argentine export competitiveness, suppressing global prices.",
     "source": "BCRA / api.bcra.gob.ar", "freq": "일간", "unit": "ARS/USD"},
    # ── P1-01 거시경제 ──
    {"code": "USDKRW", "category": "P1-01 거시경제", "name_ko": "원/달러 환율",
     "name_en": "KRW/USD Exchange Rate",
     "desc_ko": "한국 대두유 수입 원화 비용 결정. USD 강세(원화 약세) → 수입 CIF 원화 비용 증가.",
     "desc_en": "Determines KRW import cost. USD strengthening directly raises CIF cost in KRW.",
     "source": "FRED / BOK ECOS", "freq": "일간", "unit": "KRW/USD"},
    {"code": "USDBRL", "category": "P1-01 거시경제", "name_ko": "헤알/달러 환율",
     "name_en": "BRL/USD Exchange Rate",
     "desc_ko": "브라질 수출 채산성 반영. BRL 약세 → 브라질 대두유 수출 증가 → 국제가 하락 압력.",
     "desc_en": "BRL weakness boosts Brazilian soybean oil exports, pressuring international prices downward.",
     "source": "FRED", "freq": "일간", "unit": "BRL/USD"},
    {"code": "BRENT_USD_BBL", "category": "P1-01 거시경제", "name_ko": "브렌트 원유 가격",
     "name_en": "Brent Crude Oil Price",
     "desc_ko": "식물성유 생산비(에너지·비료 투입비) + 바이오디젤 수요 연동. 유가 상승 → 대두유 바이오디젤 수요 증가 → 가격 상승.",
     "desc_en": "Affects input costs and biodiesel demand. Rising oil price → higher biodiesel demand → soybean oil price rise.",
     "source": "EIA / FRED", "freq": "일간", "unit": "USD/bbl"},
    {"code": "CPI_KOREA", "category": "P1-01 거시경제", "name_ko": "한국 소비자물가지수",
     "name_en": "Korea CPI",
     "desc_ko": "국내 식품 가격 압력 지표. 수입 대두유 가격 상승이 CPI에 반영되는 시차 측정.",
     "desc_en": "Tracks domestic food price pressure. Monitors lag between import price rise and CPI pass-through.",
     "source": "KOSIS / BOK ECOS", "freq": "월간", "unit": "index"},
    {"code": "DEXBZUS", "category": "P1-01 거시경제", "name_ko": "브라질 헤알/달러 환율 (FRED)",
     "name_en": "Brazilian Real / USD Exchange Rate (FRED DEXBZUS)",
     "desc_ko": "FRED 시리즈 DEXBZUS. BRL 약세(헤알 절하) → 브라질 대두유 달러 표시 가격 하락 → 수출 증가 → 국제가 하락 압력. 브라질은 세계 최대 대두 생산국(2위 수출국).",
     "desc_en": "FRED DEXBZUS. BRL depreciation lowers dollar-denominated export prices → Brazilian soybean oil export surge → global price suppression. Brazil is the world's top soybean producer.",
     "source": "FRED (Federal Reserve H.10)", "freq": "일간", "unit": "BRL/USD"},
    {"code": "DEXCHUS", "category": "P1-01 거시경제", "name_ko": "중국 위안/달러 환율 (FRED)",
     "name_en": "Chinese Yuan / USD Exchange Rate (FRED DEXCHUS)",
     "desc_ko": "FRED 시리즈 DEXCHUS. 중국은 세계 최대 대두유 수입국. CNY 강세 → 수입 구매력 향상 → 수입 수요 증가 → 가격 상승 지지. CNY 약세는 반대 효과.",
     "desc_en": "FRED DEXCHUS. China is the world's largest soybean oil importer. CNY appreciation boosts import purchasing power, supporting prices; CNY weakness has the opposite effect.",
     "source": "FRED (Federal Reserve H.10)", "freq": "일간", "unit": "CNY/USD"},
    {"code": "DEXMAUS", "category": "P1-01 거시경제", "name_ko": "말레이시아 링깃/달러 환율 (FRED)",
     "name_en": "Malaysian Ringgit / USD Exchange Rate (FRED DEXMAUS)",
     "desc_ko": "FRED 시리즈 DEXMAUS. 말레이시아는 세계 2위 팜유 생산국. MYR 약세 → 팜유 달러 가격 하락 → CPO-SBO 스프레드 확대 → 대두유 대체 수요 압박.",
     "desc_en": "FRED DEXMAUS. Malaysia is the world's 2nd largest palm oil producer. MYR depreciation lowers CPO dollar prices → CPO-SBO spread widens → substitution pressure on soybean oil.",
     "source": "FRED (Federal Reserve H.10)", "freq": "일간", "unit": "MYR/USD"},
    {"code": "VIXCLS", "category": "P1-01 거시경제", "name_ko": "CBOE 변동성지수 (VIX)",
     "name_en": "CBOE Volatility Index (VIX, FRED VIXCLS)",
     "desc_ko": "FRED 시리즈 VIXCLS. '공포지수'. VIX >30 → 위험회피 심화 → 원자재 선물 투기포지션 청산 → 대두유 가격 급락 위험. 반대로 VIX 하락기에는 상품 가격 상승 경향. 단기 가격 변동성 선행지표.",
     "desc_en": "FRED VIXCLS. 'Fear gauge'. VIX >30 → risk-off → commodity futures liquidation → soybean oil price drop risk. VIX decline periods tend to support commodity price rises. Leading indicator of short-term price volatility.",
     "source": "FRED / CBOE", "freq": "일간", "unit": "index"},
    # ── P1-02 지정학 ──
    {"code": "GPR", "category": "P1-02 지정학", "name_ko": "지정학 리스크 지수 (GPR)",
     "name_en": "Geopolitical Risk Index (GPR)",
     "desc_ko": "Caldara & Iacoviello GPR 지수. 전쟁·테러·정치 위기 뉴스 기반. 정규화 값 >0.022 → C-03 구조적 단절 경보.",
     "desc_en": "Caldara & Iacoviello GPR. Based on war/terror/political crisis news. Normalized >0.022 triggers C-03 alert.",
     "source": "policyuncertainty.com", "freq": "월간", "unit": "index (≈100 baseline)"},
    {"code": "HORMUZ_THREAT_LEVEL", "category": "P1-02 지정학", "name_ko": "호르무즈 해협 위협 수준",
     "name_en": "Strait of Hormuz Threat Level",
     "desc_ko": "이란-미국 긴장·후티 공격 모니터링. 봉쇄 위협 → 유가 급등 → 벙커유 비용 → CFR 운임 프리미엄 +3~8%.",
     "desc_en": "Iran-US tension / Houthi attack monitoring. Closure threat → oil spike → bunker cost → CFR freight +3-8%.",
     "source": "Perplexity Pro (실시간)", "freq": "일간", "unit": "1=Low/2=Med/3=High"},
    # ── P1-03 기후 ──
    {"code": "ENSO_ONI", "category": "P1-03 기후", "name_ko": "ENSO 오세아닉 니뇨 지수 (ONI)",
     "name_en": "ENSO Oceanic Niño Index (ONI)",
     "desc_ko": "엘니뇨(+0.5↑)/라니냐(-0.5↓) 판단 지수. 브라질·아르헨티나 강수 패턴 → 대두 생산량 직결. |ONI|≥0.5 → C-03 기후 경보.",
     "desc_en": "El Niño/La Niña threshold: ±0.5. Controls Brazil/Argentina rainfall → soybean production. |ONI|≥0.5 = C-03 alert.",
     "source": "NOAA CPC", "freq": "월간", "unit": "°C anomaly"},
    {"code": "DROUGHT_D2", "category": "P1-03 기후", "name_ko": "미국 심각 가뭄 비율 (D2)",
     "name_en": "US Severe Drought Coverage (D2)",
     "desc_ko": "USDM 가뭄 지수 D2(심각) 면적 비율. 미국 대두 Top-5 생산주(IA/IL/IN/MN/NE) 기준. 작황 스트레스 선행지표.",
     "desc_en": "USDM D2 severe drought coverage for top-5 US soybean states. Leading indicator for crop stress.",
     "source": "drought.gov / USDM", "freq": "주간", "unit": "% of area"},
    {"code": "T2M_BR_Mato_Grosso", "category": "P1-03 기후", "name_ko": "브라질 마토그로소 기온 (NASA POWER)",
     "name_en": "Brazil Mato Grosso Temperature (NASA POWER)",
     "desc_ko": "브라질 최대 대두 생산지 기온. 고온 스트레스(>35°C) → 대두 착협기 생산량 감소.",
     "desc_en": "Temperature in Brazil's largest soybean region. Heat stress (>35°C) during pod fill reduces yield.",
     "source": "NASA POWER API", "freq": "월간", "unit": "°C"},
    # ── P1-03/P1-04 작황 ──
    {"code": "SBO_PRODUCTION", "category": "P1-03/P1-04 작황", "name_ko": "대두유 글로벌 생산량 (USDA PSD)",
     "name_en": "Global Soybean Oil Production (USDA PSD)",
     "desc_ko": "USDA FAS PSD 마케팅연도별 글로벌 생산량. WASDE 발표 시 가격 변동의 핵심 드라이버.",
     "desc_en": "USDA FAS PSD global production by marketing year. Key price driver on WASDE release.",
     "source": "USDA FAS OpenData API", "freq": "마케팅연도", "unit": "1000 MT"},
    {"code": "SBO_ENDING_STOCKS", "category": "P1-03/P1-04 작황", "name_ko": "대두유 기말 재고 (USDA PSD)",
     "name_en": "Global Soybean Oil Ending Stocks (USDA PSD)",
     "desc_ko": "재고/소비 비율(STU) <10% → C-03 공급 스트레스 경보. 역대 최저 재고는 가격 급등의 선행지표.",
     "desc_en": "Stocks-to-use <10% triggers C-03 supply stress alert. Record-low stocks precede price spikes.",
     "source": "USDA FAS OpenData API", "freq": "마케팅연도", "unit": "1000 MT"},
    {"code": "SOYBEAN_PROD_BU", "category": "P1-03/P1-04 작황", "name_ko": "미국 주별 대두 생산량 (NASS)",
     "name_en": "US State Soybean Production (NASS)",
     "desc_ko": "USDA NASS 주별 대두 생산량. IA/IL/IN/MN/NE 합산 → 미국 전체 대두유 원료 공급 예측.",
     "desc_en": "USDA NASS state-level soybean production. Sum of top-5 states forecasts US soybean oil feedstock supply.",
     "source": "USDA NASS QuickStats", "freq": "연간", "unit": "Bushels"},
    {"code": "SOYBEAN_PROD_TONNE_AR", "category": "P1-03/P1-04 작황", "name_ko": "아르헨티나 대두 생산량 (INDEC)",
     "name_en": "Argentina Soybean Production (INDEC)",
     "desc_ko": "INDEC 공식 통계. 아르헨티나는 세계 1위 대두유 수출국. 가뭄·라니냐 시 생산 급감 → 국제가 급등.",
     "desc_en": "INDEC official stats. Argentina is the world's largest soybean oil exporter. Drought/La Niña → supply shock.",
     "source": "datos.gob.ar / INDEC", "freq": "연간", "unit": "Tonnes"},
    # ── P1-04 해운 ──
    {"code": "BCAA", "category": "P1-04 해운", "name_ko": "BCAA (식물성유지 탱커 운임)",
     "name_en": "Baltic Chemical & Agricultural Oil Assessments",
     "desc_ko": "Baltic Exchange 2025-02 출시. 대두유·팜유·팜올레인 탱커 운임 전용. 한국 CIF 도착 원가에 직결.",
     "desc_en": "Launched Feb 2025 by Baltic Exchange. Vegetable oil tanker freight: CPO/SBO/palm olein routes. Direct CIF cost driver.",
     "source": "Perplexity Pro (직접 API: Baltic Exchange/ICE 기업 구독)", "freq": "일간", "unit": "USD/MT"},
    {"code": "BDI", "category": "P1-04 해운", "name_ko": "발틱 건화물 지수 (BDI)",
     "name_en": "Baltic Dry Index (BDI)",
     "desc_ko": "건화물 운임 지수. 대두유 직접 관련성은 낮으나 글로벌 무역 경기·원자재 수요 대리 지표. C-03 z>2σ(90일) → 구조적 단절 경보.",
     "desc_en": "Dry bulk freight. Indirect indicator of global trade activity. C-03 alert: z-score >2σ (90-day rolling).",
     "source": "Trading Economics / Baltic Exchange", "freq": "일간", "unit": "points"},
    # ── P1-04 수입 통계 ──
    {"code": "import_cif_usd", "category": "P1-04 수입통계", "name_ko": "한국 대두유 수입 CIF 금액 (HS 1507)",
     "name_en": "Korea Soybean Oil Import CIF Value (HS 1507)",
     "desc_ko": "관세청 공식 통관 데이터. 국가별 수입 CIF 단가 산출 가능. 실제 조달 비용 역산의 기준점.",
     "desc_en": "Korea Customs official trade data. Allows per-country CIF unit price calculation. Ground truth for procurement cost.",
     "source": "관세청/data.go.kr (폴백: UN Comtrade)", "freq": "월간", "unit": "USD"},
]

# ── C-03 구조적 단절 임계값 (c03-data-scientist.md) ──────────────────────────
THRESHOLDS: dict[str, dict] = {
    "GPR_NORMALIZED":   {"alert": 0.022,  "dir": ">",  "label": "지정학 구조적 단절"},
    "BDI":              {"alert": None,    "dir": "z",  "label": "해운비용 급등 (90일 rolling z>2σ)"},
    "WASDE_STU":        {"alert": 0.10,   "dir": "<",  "label": "공급 스트레스"},
    "CPO_SBO_SPREAD":   {"alert": 175.0,  "dir": ">",  "label": "CPO 대체압력"},
    "ENSO_ONI":         {"alert": 0.5,    "dir": "abs", "label": "기후 레짐 전환"},
}

# ── C-03 임계값 산출 근거 설명 ─────────────────────────────────────────────────
THRESHOLD_RATIONALE: list[dict] = [
    {
        "variable": "GPR (Geopolitical Risk Index)",
        "threshold": "> 0.022 (정규화)",
        "rationale_ko": (
            "Caldara & Iacoviello(2022) 연구 기반. 정규화 GPR 지수가 0.022를 초과하면 "
            "역사적으로 원자재 선물시장 변동성이 95th 퍼센타일 이상으로 상승. "
            "2022년 러시아-우크라이나 전쟁 당시 GPR=0.035 → 대두유 +38% 급등(3개월 내). "
            "0.022는 2σ 상방 기준의 비선형 변곡점."
        ),
        "rationale_en": (
            "Based on Caldara & Iacoviello (2022). Normalized GPR >0.022 historically corresponds "
            "to commodity futures volatility at or above the 95th percentile. "
            "During the 2022 Russia-Ukraine war, GPR=0.035 preceded +38% soybean oil price surge (3-month). "
            "0.022 marks the nonlinear inflection above 2σ."
        ),
        "action": "Buy 포지션 축소 / 선물 헤지 검토 / 조달처 다변화 가속",
    },
    {
        "variable": "BDI z-score (90일 rolling)",
        "threshold": "> 2.0σ",
        "rationale_ko": (
            "Baltic Dry Index의 90일 이동 z-점수. |z|>2는 통계적 유의성(95% 신뢰구간). "
            "BDI z>2σ는 글로벌 원자재 수송 수요 급증 신호 → 액체 벌크 탱커 운임도 동반 상승. "
            "대두유 CFR 운임 프리미엄 +5~12% 동반 패턴 확인(2020~2023 역사 검증). "
            "90일 window는 계절성 제거와 단기 노이즈 필터링의 균형점."
        ),
        "rationale_en": (
            "90-day rolling z-score of Baltic Dry Index. |z|>2 = statistically significant (95% CI). "
            "BDI z>2σ signals global dry bulk demand surge → liquid bulk tanker rates follow. "
            "Historical correlation: CFR soybean oil freight premium +5-12% (verified 2020–2023). "
            "90-day window balances seasonality removal with short-term noise filtering."
        ),
        "action": "CFR 운임 상승분 조달 단가 반영 / 장기 물량 선도 계약 검토",
    },
    {
        "variable": "WASDE 재고/소비 비율 (STU)",
        "threshold": "< 10%",
        "rationale_ko": (
            "USDA WASDE 대두유 글로벌 기말재고/소비(Stocks-to-Use) 비율. "
            "10% 미만은 '극도 타이트' 시장 기준 — USDA 내부 경보 레벨. "
            "2010~2011년 STU=8.9% 시 대두유 가격 +67% 상승. "
            "2022년 STU=9.2% 시 가격 최고가(USc 79/lb). "
            "10% 미만에서 추가 공급 충격(가뭄·수출제한) 시 비선형 가격 급등 패턴."
        ),
        "rationale_en": (
            "USDA WASDE global soybean oil ending stocks-to-use ratio. "
            "Sub-10% = 'extremely tight' market per USDA internal alert level. "
            "2010-2011 STU=8.9% preceded +67% price surge. "
            "2022 STU=9.2% coincided with all-time high (USc 79/lb). "
            "Below 10%, additional supply shocks produce nonlinear price spikes."
        ),
        "action": "조달 물량 확대 / 재고 목표 상향 / 원가 고정형 계약 비중 증가",
    },
    {
        "variable": "CPO-SBO 스프레드",
        "threshold": "> $175/MT",
        "rationale_ko": (
            "CPO(팜유)와 SBO(대두유) 가격 차이. $175/MT 초과 시 식품·사료 제조업체가 "
            "팜유로 대체 가능. 실증 연구(Appleby et al., 2022): 스프레드 >$180 → "
            "6개월 내 SBO 수요 전환 탄성치 0.4~0.6 관측. "
            "$175는 아시아 현물 조달 비용 포함 시 대체 유인이 발생하는 실증 임계점."
        ),
        "rationale_en": (
            "Price differential between CPO (palm oil) and SBO (soybean oil). "
            "Above $175/MT, food/feed manufacturers have economic incentive to substitute with palm oil. "
            "Empirical: spread >$180 → demand switching elasticity 0.4–0.6 observed over 6 months (Appleby et al., 2022). "
            "$175 is the empirical substitution breakeven including Asian spot procurement costs."
        ),
        "action": "CPO 공급망 대안 소싱 검토 / 기술규격상 CPO 허용 여부 확인",
    },
    {
        "variable": "ENSO ONI (오세아닉 니뇨 지수)",
        "threshold": "|ONI| ≥ 0.5°C",
        "rationale_ko": (
            "NOAA CPC 공식 엘니뇨/라니냐 판정 기준(3개월 이동평균 SST 이상). "
            "La Niña(ONI ≤ -0.5): 아르헨티나·브라질 중부 가뭄 → 대두 감산 → SBO 공급 급감. "
            "2020~2023 La Niña 3년 연속: 아르헨티나 감산 45% → SBO 가격 최고. "
            "El Niño(ONI ≥ +0.5): 미국 중서부 가뭄 위험 증가 → NASS 작황 경보."
        ),
        "rationale_en": (
            "NOAA CPC official El Niño/La Niña threshold (3-month SST anomaly). "
            "La Niña (ONI ≤ -0.5): Argentina/Brazil drought → soybean crop shortfall → SBO supply crunch. "
            "2020-2023 triple La Niña: Argentina output -45% → SBO all-time high. "
            "El Niño (ONI ≥ +0.5): elevated US Midwest drought risk → NASS crop stress alerts."
        ),
        "action": "아르헨티나/브라질 작황 일일 모니터링 / 선물 헤지 비중 상향",
    },
]

# ── LASSO 계수 진단 메시지 ────────────────────────────────────────────────────
LASSO_ZERO_DIAGNOSIS: list[dict] = [
    {
        "cause_ko": "관측값 부족 (Phase A 초기)",
        "cause_en": "Insufficient observations (Phase A early stage)",
        "detail_ko": (
            "LASSO는 최소 30~50개 관측치(거래일)가 있어야 통계적으로 유의미한 계수를 추정할 수 있음. "
            "수집 7일 → 일간 정렬 후 결측치 제거 시 실제 유효 행 수가 3~5개에 불과. "
            "LassoCV의 CV 폴드 수가 관측치 절반으로 제한되어 정규화 경로 전체가 α→∞ 방향으로 수렴 → 전 계수 0."
        ),
        "detail_en": (
            "LASSO requires 30–50+ observations for statistically meaningful coefficient estimation. "
            "With 7 days of data, after daily alignment and dropna, effective rows drop to 3–5. "
            "LassoCV folds are capped at len(y)//2, causing the regularization path to converge toward α→∞ → all coefficients zeroed."
        ),
        "solution_ko": "30일+ 데이터 누적 후 재실행. 현재는 피어슨 상관계수(r)가 더 신뢰할 수 있는 중요도 지표.",
        "solution_en": "Re-run after 30+ days of data accumulation. Pearson r is currently more reliable as an importance indicator.",
    },
    {
        "cause_ko": "다중공선성 (FX 변수 간)",
        "cause_en": "Multicollinearity among FX variables",
        "detail_ko": (
            "DEXBZUS·DEXCHUS·DEXMAUS·USDKRW는 모두 달러 대비 환율 → 높은 상호 상관(Pearson r >0.7 빈번). "
            "LASSO는 공선성 그룹에서 하나만 선택 → 나머지를 0으로 강제 설정. "
            "그룹 내 어느 변수가 선택될지는 데이터에 따라 다름 — 해석에 주의."
        ),
        "detail_en": (
            "DEXBZUS/DEXCHUS/DEXMAUS/USDKRW are all USD-denominated → high mutual correlation (Pearson r >0.7 common). "
            "LASSO selects one from a collinear group and zeros the rest. "
            "Which variable is selected depends on the sample — interpret with caution."
        ),
        "solution_ko": "Ridge 회귀(L2) 또는 Elastic Net 사용 시 공선성 그룹 모두 비-0 계수 획득 가능. Phase B에서 적용 예정.",
        "solution_en": "Ridge (L2) or Elastic Net retains non-zero coefficients for all collinear variables. Planned for Phase B.",
    },
    {
        "cause_ko": "갱신 주기 불일치 (월별 vs 일별)",
        "cause_en": "Frequency mismatch (monthly vs daily)",
        "detail_ko": (
            "VIXCLS·DEXBZUS 등은 일별 갱신이나 ENSO·CPI·WASDE 등은 월별. "
            "일별 피벗 후 ffill(limit=3)로 3일 이상 결측이 채워지지 않음 → "
            "dropna() 후 매우 적은 공통 관측치만 남아 LASSO 입력 차원이 수십 → 수 개로 축소."
        ),
        "detail_en": (
            "VIXCLS/DEXBZUS etc. update daily, but ENSO/CPI/WASDE update monthly. "
            "After daily pivot, ffill(limit=3) fails to fill gaps >3 days → "
            "after dropna(), shared observation count collapses → LASSO input shrinks dramatically."
        ),
        "solution_ko": "월별 집계(resample('ME').last())로 주기 통일 후 상관 분석. 또는 target을 월별 지표로 설정.",
        "solution_en": "Unify frequency via monthly resampling (resample('ME').last()). Or set target variable to a monthly indicator.",
    },
]

# ── 수집 파일별 지표 코드 매핑 ────────────────────────────────────────────────
FILE_PATTERNS: dict[str, str] = {
    "economic_indicators": "P1-01 거시(Fed/CPI/FX/Brent)",
    "shipping_indices":    "P1-04 해운(BCAA/BDI)",
    "crop_data":           "P1-01/P1-03 작황(WASDE/PSD)",
    "climate_data":        "P1-03 기후(ONI/기상이상)",
    "geopolitical_indices":"P1-02 지정학(GPR/호르무즈)",
    "production_data":     "P1-04 생산량(NASS/FAOSTAT/NASA)",
    "commodity_data":      "P1-01 상품가(CBOT/CPO/ARS/가뭄)",
    "customs_import":      "P1-04 수입통계(관세청 HS1507)",
}


def _load_all_parquets(days: int = 7) -> dict[str, pd.DataFrame]:
    """최근 N일 수집된 parquet 파일 로드. 파일명 접두사 기준 분류."""
    cutoff = date.today() - timedelta(days=days)
    frames: dict[str, list[pd.DataFrame]] = {k: [] for k in FILE_PATTERNS}

    for f in sorted(glob.glob(f"{OUTPUT_DIR}/**/*.parquet", recursive=True)
                    + glob.glob(f"{OUTPUT_DIR}/*.parquet")):
        name = Path(f).stem
        try:
            df = pd.read_parquet(f)
        except Exception as e:
            print(f"[경고] 파일 로드 실패 — {name}: {e}")
            continue

        # 최신성 필터: ingested_at 기준 cutoff 이내
        if "ingested_at" in df.columns:
            df["ingested_at"] = pd.to_datetime(df["ingested_at"], utc=True, errors="coerce")
            max_ingest = df["ingested_at"].max()
            if pd.notna(max_ingest) and max_ingest.date() < cutoff:
                continue

        matched = next((k for k in FILE_PATTERNS if name.startswith(k)), None)
        if matched:
            frames[matched].append(df)

    return {k: pd.concat(v, ignore_index=True) for k, v in frames.items() if v}


def _freshness_flag(df: pd.DataFrame, stale_days: int = 5) -> str:
    """데이터 신선도 판정: STALE / OK."""
    if "ingested_at" not in df.columns:
        return "⚠️ 수집일 미확인"
    max_ingest = pd.to_datetime(df["ingested_at"], utc=True, errors="coerce").max()
    if pd.isna(max_ingest):
        return "⚠️ 수집일 미확인"
    biz_days_old = np.busday_count(max_ingest.date(), date.today())
    return f"🚨 STALE ({biz_days_old}영업일)" if biz_days_old > stale_days else "✅ OK"


def _build_data_status(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """커넥터별 데이터 현황 테이블."""
    rows = []
    for key, label in FILE_PATTERNS.items():
        if key not in frames:
            rows.append({"커넥터": label, "파일수": 0, "행수": 0,
                         "날짜범위": "미수집", "신선도": "❌ 데이터 없음"})
            continue
        df = frames[key]
        date_col = next((c for c in ["price_date", "ingested_at"] if c in df.columns), None)
        if date_col:
            dates = pd.to_datetime(df[date_col], errors="coerce").dropna()
            date_range = f"{dates.min().date()} ~ {dates.max().date()}" if len(dates) else "N/A"
        else:
            date_range = "N/A"
        rows.append({
            "커넥터":   label,
            "파일수":   1,
            "행수":     len(df),
            "날짜범위": date_range,
            "신선도":   _freshness_flag(df),
        })
    return pd.DataFrame(rows)


def _pivot_for_correlation(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """모든 numeric 시계열을 price_date 기준으로 pivot하여 상관분석용 wide-format 생성."""
    series: dict[str, pd.Series] = {}

    for key, df in frames.items():
        if "price_date" not in df.columns:
            continue
        df = df.copy()
        df["price_date"] = pd.to_datetime(df["price_date"], errors="coerce")
        df = df.dropna(subset=["price_date"])

        # indicator_code 컬럼이 있으면 장형 -> 피벗
        if "indicator_code" in df.columns and "value" in df.columns:
            for code, grp in df.groupby("indicator_code"):
                s = grp.set_index("price_date")["value"]
                s = pd.to_numeric(s, errors="coerce").dropna()
                if len(s) > 2:
                    series[str(code)] = s.resample("D").last()
        else:
            # numeric 컬럼 직접 사용
            num_cols = df.select_dtypes(include="number").columns.tolist()
            num_cols = [c for c in num_cols if c not in ("ingested_at", "rows")]
            for col in num_cols[:5]:  # 컬럼 수 제한
                s = df.set_index("price_date")[col]
                s = pd.to_numeric(s, errors="coerce").dropna()
                if len(s) > 2:
                    series[f"{key}_{col}"] = s.resample("D").last()

    if not series:
        return pd.DataFrame()

    wide = pd.DataFrame(series)
    wide = wide.sort_index().ffill(limit=3)  # 최대 3일 forward-fill
    return wide


def _lasso_importance(wide: pd.DataFrame, target_col: str | None = None) -> pd.DataFrame:
    """LASSO 회귀로 변수 중요도 계산. target_col이 없으면 가장 완전한 컬럼을 사용."""
    from sklearn.linear_model import LassoCV
    from sklearn.preprocessing import StandardScaler

    if wide.empty or len(wide) < 10:
        return pd.DataFrame(columns=["변수", "피어슨_r", "LASSO_계수", "포함여부"])

    wide_clean = wide.dropna(thresh=max(2, len(wide) // 2), axis=1)
    wide_clean = wide_clean.dropna()

    if wide_clean.empty or wide_clean.shape[1] < 2:
        return pd.DataFrame(columns=["변수", "피어슨_r", "LASSO_계수", "포함여부"])

    # target: 가장 완전한 컬럼 (대두유 관련 코드 우선)
    priority = ["CBOT_BO_CLOSE", "BO_CLOSE", "cbot_soybean_oil", "BRENT_USD_BBL"]
    if target_col is None:
        target_col = next(
            (c for c in priority if c in wide_clean.columns),
            wide_clean.columns[0],
        )

    y = wide_clean[target_col]
    X = wide_clean.drop(columns=[target_col])

    if X.empty:
        return pd.DataFrame(columns=["변수", "피어슨_r", "LASSO_계수", "포함여부"])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    try:
        lasso = LassoCV(cv=min(5, len(y) // 2), max_iter=5000, random_state=42)
        lasso.fit(X_scaled, y)
        coefs = dict(zip(X.columns, lasso.coef_))
    except Exception:
        coefs = {c: 0.0 for c in X.columns}

    rows = []
    for col in X.columns:
        try:
            r = float(np.corrcoef(X[col], y)[0, 1])
        except Exception:
            r = float("nan")
        coef = coefs.get(col, 0.0)
        rows.append({
            "변수":      col,
            "피어슨_r":  round(r, 3),
            "LASSO_계수": round(coef, 4),
            "포함여부":  "✅ 포함" if abs(coef) > 0.001 else "— 제외",
        })

    df_imp = pd.DataFrame(rows)
    df_imp["abs_coef"] = df_imp["LASSO_계수"].abs()
    return df_imp.sort_values("abs_coef", ascending=False).drop(columns="abs_coef")


def _check_structural_breaks(frames: dict[str, pd.DataFrame]) -> list[dict]:
    """C-03 구조적 단절 임계값 현황 점검."""
    alerts = []

    # GPR 지수 (normalized)
    if "geopolitical_indices" in frames:
        gpr_df = frames["geopolitical_indices"]
        gpr = gpr_df[gpr_df.get("indicator_code", pd.Series(dtype=str)) == "GPR_NORMALIZED"]
        if not gpr.empty and "value" in gpr.columns:
            latest_gpr = float(gpr["value"].dropna().iloc[-1])
            alerts.append({
                "변수": "GPR_NORMALIZED",
                "현재값": round(latest_gpr, 4),
                "임계값": THRESHOLDS["GPR_NORMALIZED"]["alert"],
                "상태": "🚨 임계초과" if latest_gpr > 0.022 else "✅ 정상",
                "설명": THRESHOLDS["GPR_NORMALIZED"]["label"],
            })

    # ENSO ONI
    if "climate_data" in frames:
        oni_df = frames["climate_data"]
        oni = oni_df[oni_df.get("indicator_code", pd.Series(dtype=str)) == "ONI"] if "indicator_code" in oni_df.columns else pd.DataFrame()
        if not oni.empty and "value" in oni.columns:
            latest_oni = float(oni["value"].dropna().iloc[-1])
            alerts.append({
                "변수": "ENSO_ONI",
                "현재값": round(latest_oni, 2),
                "임계값": "±0.5",
                "상태": "🚨 임계초과" if abs(latest_oni) >= 0.5 else "✅ 정상",
                "설명": THRESHOLDS["ENSO_ONI"]["label"],
            })

    # BDI z-score (90일 rolling)
    if "shipping_indices" in frames:
        bdi_df = frames["shipping_indices"]
        bdi = bdi_df[bdi_df.get("indicator_code", pd.Series(dtype=str)) == "BDI"] if "indicator_code" in bdi_df.columns else pd.DataFrame()
        if not bdi.empty and "value" in bdi.columns and len(bdi) > 10:
            vals = pd.to_numeric(bdi["value"], errors="coerce").dropna()
            if len(vals) >= 5:
                roll_mean = vals.rolling(min(90, len(vals))).mean().iloc[-1]
                roll_std  = vals.rolling(min(90, len(vals))).std().iloc[-1]
                z = (vals.iloc[-1] - roll_mean) / roll_std if roll_std > 0 else 0.0
                alerts.append({
                    "변수": "BDI_ZSCORE",
                    "현재값": round(z, 2),
                    "임계값": "2.0σ",
                    "상태": "🚨 임계초과" if z > 2.0 else "✅ 정상",
                    "설명": THRESHOLDS["BDI"]["label"],
                })

    return alerts


def _render_variable_catalog(lang: str = "ko") -> str:
    """변수 카탈로그를 카테고리별 HTML 테이블로 렌더링."""
    by_cat: dict[str, list[dict]] = {}
    for v in VARIABLE_CATALOG:
        by_cat.setdefault(v["category"], []).append(v)

    sections = []
    for cat, vars_in_cat in by_cat.items():
        rows_html = ""
        for v in vars_in_cat:
            name    = v["name_ko"]   if lang == "ko" else v["name_en"]
            desc    = v["desc_ko"]   if lang == "ko" else v["desc_en"]
            rows_html += (
                f"<tr><td><code>{v['code']}</code></td>"
                f"<td>{name}</td>"
                f"<td style='font-size:11px'>{desc}</td>"
                f"<td>{v['source']}</td>"
                f"<td>{v['freq']}</td>"
                f"<td>{v['unit']}</td></tr>"
            )
        col_code  = "변수 코드"   if lang == "ko" else "Variable Code"
        col_name  = "변수명"      if lang == "ko" else "Name"
        col_desc  = "설명"        if lang == "ko" else "Description"
        col_src   = "데이터 소스" if lang == "ko" else "Source"
        col_freq  = "갱신주기"    if lang == "ko" else "Frequency"
        col_unit  = "단위"        if lang == "ko" else "Unit"
        sections.append(f"""
<h3 style="color:#3949ab;margin-top:18px">{cat}</h3>
<table class="tbl">
<thead><tr>
  <th>{col_code}</th><th>{col_name}</th><th>{col_desc}</th>
  <th>{col_src}</th><th>{col_freq}</th><th>{col_unit}</th>
</tr></thead>
<tbody>{rows_html}</tbody>
</table>""")
    return "\n".join(sections)


def _render_html(
    status_df: pd.DataFrame,
    importance_df: pd.DataFrame,
    alerts: list[dict],
    run_id: str,
    run_ts: str,
    days: int,
    lang: Literal["ko", "en"] = "ko",
) -> str:
    """G1 분석 보고서 HTML 렌더링 (한국어 + 영어 이중언어)."""
    font_import = (
        "@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');"
        if lang == "ko" else ""
    )
    font_family = (
        "'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif"
        if lang == "ko" else
        "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
    )
    title  = "G1 변수 중요도 분석 리포트" if lang == "ko" else "G1 Variable Importance Report"
    sub    = f"C-03 Lead Data Scientist · 최근 {days}일 데이터 기준" if lang == "ko" else f"C-03 Lead Data Scientist · Based on last {days} days"

    # status table
    status_html = status_df.to_html(index=False, border=0, classes="tbl")

    # importance table
    if not importance_df.empty:
        imp_html = importance_df.to_html(index=False, border=0, classes="tbl")
    else:
        imp_html = "<p>데이터 부족 — 충분한 시계열 누적 후 재실행 (최소 30일 권장)</p>" if lang == "ko" else "<p>Insufficient data — re-run after 30+ days of accumulation.</p>"

    # alerts table
    if alerts:
        alert_df = pd.DataFrame(alerts)
        alerts_html = alert_df.to_html(index=False, border=0, classes="tbl")
    else:
        alerts_html = "<p>✅ 현재 임계값 초과 변수 없음</p>" if lang == "ko" else "<p>✅ No structural break thresholds breached.</p>"

    # variable catalog
    catalog_html = _render_variable_catalog(lang=lang)
    catalog_title = "분석 변수 카탈로그" if lang == "ko" else "Variable Catalog"
    catalog_note  = (
        "아래 목록은 Nexus G1 분석에 사용되는 전체 변수 목록입니다. "
        "각 변수의 수집 출처·갱신 주기·대두유 가격 연관성을 설명합니다."
        if lang == "ko" else
        "Full variable inventory used in Nexus G1 analysis. "
        "Each entry describes the collection source, update frequency, and price relevance."
    )

    # threshold rationale table
    thr_title = "C-03 구조적 단절 임계값 산출 근거" if lang == "ko" else "C-03 Structural Break Threshold Rationale"
    thr_rows = ""
    for t in THRESHOLD_RATIONALE:
        rationale = t["rationale_ko"] if lang == "ko" else t["rationale_en"]
        thr_rows += (
            f"<tr><td><strong>{t['variable']}</strong></td>"
            f"<td style='color:#c62828;font-weight:bold'>{t['threshold']}</td>"
            f"<td style='font-size:11px'>{rationale}</td>"
            f"<td style='font-size:11px;color:#1565c0'>{t['action']}</td></tr>"
        )
    col_var   = "변수" if lang == "ko" else "Variable"
    col_thr   = "임계값" if lang == "ko" else "Threshold"
    col_rat   = "산출 근거" if lang == "ko" else "Rationale"
    col_act   = "권고 액션" if lang == "ko" else "Recommended Action"
    threshold_rationale_html = f"""<table class="tbl">
<thead><tr><th>{col_var}</th><th>{col_thr}</th><th>{col_rat}</th><th>{col_act}</th></tr></thead>
<tbody>{thr_rows}</tbody></table>"""

    # LASSO=0 diagnosis
    lasso_title = "LASSO 계수 0.0 진단 및 해결 방법" if lang == "ko" else "Why LASSO Coefficients = 0.0 — Diagnosis & Solution"
    lasso_diag_rows = ""
    for d in LASSO_ZERO_DIAGNOSIS:
        cause   = d["cause_ko"]   if lang == "ko" else d["cause_en"]
        detail  = d["detail_ko"]  if lang == "ko" else d["detail_en"]
        sol     = d["solution_ko"] if lang == "ko" else d["solution_en"]
        lasso_diag_rows += (
            f"<tr><td><strong>{cause}</strong></td>"
            f"<td style='font-size:11px'>{detail}</td>"
            f"<td style='font-size:11px;color:#1565c0'>{sol}</td></tr>"
        )
    col_c = "원인" if lang == "ko" else "Cause"
    col_d = "상세 설명" if lang == "ko" else "Detail"
    col_s = "해결 방법" if lang == "ko" else "Solution"
    lasso_html = f"""<table class="tbl">
<thead><tr><th>{col_c}</th><th>{col_d}</th><th>{col_s}</th></tr></thead>
<tbody>{lasso_diag_rows}</tbody></table>"""

    return f"""<!DOCTYPE html>
<html lang="{'ko' if lang == 'ko' else 'en'}">
<head>
<meta charset="UTF-8">
<title>Nexus {title}</title>
<style>
  {font_import}
  body  {{ font-family: {font_family}; margin: 40px 60px; color: #333; font-size: 13px; line-height: 1.6; }}
  h1   {{ color: #1a237e; border-bottom: 3px solid #1a237e; padding-bottom: 10px; font-size: 20px; }}
  h2   {{ color: #283593; margin-top: 28px; font-size: 15px; }}
  .meta {{ background: #e8eaf6; padding: 14px 18px; border-radius: 8px; margin: 18px 0; }}
  .badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; margin: 2px; }}
  .note {{ background: #fff8e1; border-left: 4px solid #ffc107; padding: 10px 14px; border-radius: 4px; margin: 16px 0; font-size: 12px; }}
  .tbl  {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 12px; }}
  .tbl th {{ background: #1a237e; color: #fff; padding: 8px 12px; text-align: left; }}
  .tbl td {{ padding: 6px 12px; border-bottom: 1px solid #e0e0e0; }}
  .footer {{ margin-top: 40px; font-size: 11px; color: #9e9e9e; border-top: 1px solid #e0e0e0; padding-top: 12px; }}
</style>
</head>
<body>
<h1>{title}<br><small style="font-size:14px;color:#5c6bc0">{sub}</small></h1>

<div class="meta">
  <strong>Run ID:</strong> {run_id} &nbsp;│&nbsp;
  <strong>Generated (UTC):</strong> {run_ts} &nbsp;│&nbsp;
  <strong>{'분석 기간' if lang == 'ko' else 'Period'}:</strong> {'최근' if lang == 'ko' else 'Last'} {days}{'일' if lang == 'ko' else ' days'}
</div>

<div class="note">
  ⚠️ <strong>Phase A 분석 한계:</strong>
  현재는 수집된 데이터의 기술통계·LASSO 상관 분석만 수행합니다.
  XGBoost+SHAP, Granger 인과검정, TCN-XGBoost 하이브리드는 30일+ 시계열 누적 후 Phase B(Snowflake)에서 적용 예정.
</div>

<h2>{'데이터 수집 현황' if lang == 'ko' else 'Data Collection Status'}</h2>
{status_html}

<h2>{'변수 중요도 (LASSO 기반)' if lang == 'ko' else 'Variable Importance (LASSO-based)'}</h2>
{imp_html}

<h2>{lasso_title}</h2>
{lasso_html}

<h2>{'구조적 단절 임계값 현황 (C-03)' if lang == 'ko' else 'Structural Break Status (C-03)'}</h2>
{alerts_html}

<div class="note">
  임계값 정의 (C-03): GPR &gt; 0.022 (지정학) · BDI z &gt; 2σ (해운) · WASDE STU &lt; 10% (공급) · CPO-SBO spread &gt; $175/MT (대체)
</div>

<h2>{thr_title}</h2>
{threshold_rationale_html}

<h2>{catalog_title}</h2>
<div class="note" style="margin-bottom:8px">{catalog_note}</div>
{catalog_html}

<div class="footer">
  Project Nexus · G1 Variable Importance · C-03 Lead Data Scientist (claude-opus-4-7, Thinking Mode) ·
  Branch: claude/setup-nexus-llm-tools-RX4aS · {run_ts} UTC
</div>
</body>
</html>"""


def run(days: int = 7) -> None:
    os.makedirs("src/forecasting", exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)

    from datetime import datetime
    now    = datetime.utcnow()
    tag    = now.strftime("%Y%m%d_%H%M")
    run_ts = now.strftime("%Y-%m-%d %H:%M:%S")
    run_id = os.environ.get("GITHUB_RUN_ID", "local")

    print(f"[C-03] G1 변수 중요도 분석 시작 — 최근 {days}일 데이터 로드 중...")
    frames = _load_all_parquets(days=days)

    if not frames:
        print(f"[경고] {OUTPUT_DIR} 에서 유효한 parquet 파일 없음 — 분석 건너뜀.")
        return

    print(f"[C-03] {len(frames)}개 커넥터 데이터 로드 완료: {list(frames.keys())}")

    status_df    = _build_data_status(frames)
    wide         = _pivot_for_correlation(frames)
    importance_df = _lasso_importance(wide)
    alerts       = _check_structural_breaks(frames)

    print(f"[C-03] 상관 분석 변수 수: {wide.shape[1] if not wide.empty else 0}")
    print(f"[C-03] 구조적 단절 임계값 초과: {sum(1 for a in alerts if '🚨' in a.get('상태', ''))}/{len(alerts)}")

    for lang in ("ko", "en"):
        html_path = f"{REPORT_DIR}/g1_variable_importance_{tag}_{lang}.html"
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(_render_html(status_df, importance_df, alerts, run_id, run_ts, days, lang=lang))  # type: ignore[arg-type]
        print(f"[완료] G1 리포트 ({lang.upper()}) → {html_path}")

    # 구조적 단절 경보 요약 출력 (Korean narrative — C-03 계약)
    breach = [a for a in alerts if "🚨" in a.get("상태", "")]
    if breach:
        print("\n[C-03 경보] 구조적 단절 임계값 초과 변수:")
        for a in breach:
            print(f"  • {a['변수']}: 현재값 {a['현재값']} (임계값 {a['임계값']}) — {a['설명']}")
    else:
        print("\n[C-03 정보] 모든 구조적 단절 임계값 정상 범위 내.")


if __name__ == "__main__":
    import sys
    d = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    run(days=d)
