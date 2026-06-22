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

# ── Granger 인과검정 설정 ──────────────────────────────────────────────────────
GRANGER_MIN_OBS = 30                                    # 검정 최소 관측치
GRANGER_MAX_LAG = 4                                     # 최대 시차 (분기 기준)
GRANGER_ALPHA   = 0.05                                  # 유의수준
GRANGER_YEARS   = list(range(2017, date.today().year))  # 2017 ~ 작년

# ── G1 변수 설명 사전 (C-01/C-03 공동 관리) ──────────────────────────────────
VARIABLE_CATALOG: list[dict] = [
    # ── 상품가격 ──
    {"code": "CBOT_BO_CLOSE", "category": "상품가격", "name_ko": "CBOT 대두유 선물 종가",
     "name_en": "CBOT Soybean Oil Futures Close",
     "desc_ko": "시카고상품거래소(CME/CBOT) 대두유 선물 종가. 국제 대두유 가격의 기준점. 국내 CIF 가격에 가장 직접적인 영향.",
     "desc_en": "CBOT soybean oil futures closing price. Primary international benchmark for soybean oil pricing.",
     "source": "yfinance / CME (BO=F)", "freq": "일간", "unit": "USc/lb"},
    {"code": "CBOT_BO_VOLUME", "category": "상품가격", "name_ko": "CBOT 대두유 선물 거래량",
     "name_en": "CBOT Soybean Oil Futures Volume",
     "desc_ko": "선물 거래량 급증은 가격 변동성 확대 선행지표. 시장 유동성·투기 포지션 반영.",
     "desc_en": "Futures volume spike signals price volatility. Reflects market liquidity and speculative positioning.",
     "source": "yfinance / CME (BO=F)", "freq": "일간", "unit": "계약수"},
    {"code": "CPO_USD_MT", "category": "상품가격", "name_ko": "팜유(CPO) 현물가",
     "name_en": "Crude Palm Oil Spot Price",
     "desc_ko": "말레이시아 부르사(FCPO) 팜유 현물. 대두유와 직접 대체 관계(CPO-SBO 스프레드 >$175 → 대체 수요 이전 임계).",
     "desc_en": "Bursa Malaysia CPO spot. Direct substitute for soybean oil; CPO-SBO spread >$175/MT triggers demand substitution.",
     "source": "Trading Economics / Bursa Malaysia", "freq": "일간", "unit": "USD/MT"},
    {"code": "CPO_GLOBAL_USD_MT_PROXY", "category": "상품가격", "name_ko": "IMF 팜유 글로벌 벤치마크 (FRED)",
     "name_en": "IMF Palm Oil Global Benchmark (FRED)",
     "desc_ko": "FRED PPOILUSDM — IMF 국제 팜유 가격 월별 지수. CPO 현물 미수집 시 대리 지표.",
     "desc_en": "FRED PPOILUSDM monthly proxy for international palm oil price.",
     "source": "FRED / IMF", "freq": "월간", "unit": "USD/MT"},
    {"code": "ARS_USD_OFICIAL", "category": "상품가격", "name_ko": "아르헨티나 공식 환율 (ARS/USD)",
     "name_en": "Argentina Official FX Rate (ARS/USD)",
     "desc_ko": "BCRA 공식 환율. 아르헨티나 대두유 수출 채산성 직결. 급격한 평가절하 → 수출 증가 → 국제가 하락 압력.",
     "desc_en": "BCRA official rate. Sharp ARS devaluation raises Argentine export competitiveness, suppressing global prices.",
     "source": "BCRA / api.bcra.gob.ar", "freq": "일간", "unit": "ARS/USD"},
    # ── 거시경제 ──
    {"code": "USDKRW", "category": "거시경제", "name_ko": "원/달러 환율",
     "name_en": "KRW/USD Exchange Rate",
     "desc_ko": "한국 대두유 수입 원화 비용 결정. USD 강세(원화 약세) → 수입 CIF 원화 비용 증가.",
     "desc_en": "Determines KRW import cost. USD strengthening directly raises CIF cost in KRW.",
     "source": "FRED / BOK ECOS", "freq": "일간", "unit": "KRW/USD"},
    {"code": "USDBRL", "category": "거시경제", "name_ko": "헤알/달러 환율",
     "name_en": "BRL/USD Exchange Rate",
     "desc_ko": "브라질 수출 채산성 반영. BRL 약세 → 브라질 대두유 수출 증가 → 국제가 하락 압력.",
     "desc_en": "BRL weakness boosts Brazilian soybean oil exports, pressuring international prices downward.",
     "source": "FRED", "freq": "일간", "unit": "BRL/USD"},
    {"code": "BRENT_USD_BBL", "category": "거시경제", "name_ko": "브렌트 원유 가격",
     "name_en": "Brent Crude Oil Price",
     "desc_ko": "식물성유 생산비(에너지·비료 투입비) + 바이오디젤 수요 연동. 유가 상승 → 대두유 바이오디젤 수요 증가 → 가격 상승.",
     "desc_en": "Affects input costs and biodiesel demand. Rising oil price → higher biodiesel demand → soybean oil price rise.",
     "source": "EIA / FRED", "freq": "일간", "unit": "USD/bbl"},
    {"code": "CPI_KOREA", "category": "거시경제", "name_ko": "한국 소비자물가지수",
     "name_en": "Korea CPI",
     "desc_ko": "국내 식품 가격 압력 지표. 수입 대두유 가격 상승이 CPI에 반영되는 시차 측정.",
     "desc_en": "Tracks domestic food price pressure. Monitors lag between import price rise and CPI pass-through.",
     "source": "KOSIS / BOK ECOS", "freq": "월간", "unit": "index"},
    {"code": "DEXBZUS", "category": "거시경제", "name_ko": "브라질 헤알/달러 환율 (FRED)",
     "name_en": "Brazilian Real / USD Exchange Rate (FRED DEXBZUS)",
     "desc_ko": "FRED 시리즈 DEXBZUS. BRL 약세(헤알 절하) → 브라질 대두유 달러 표시 가격 하락 → 수출 증가 → 국제가 하락 압력. 브라질은 세계 최대 대두 생산국(2위 수출국).",
     "desc_en": "FRED DEXBZUS. BRL depreciation lowers dollar-denominated export prices → Brazilian soybean oil export surge → global price suppression. Brazil is the world's top soybean producer.",
     "source": "FRED (Federal Reserve H.10)", "freq": "일간", "unit": "BRL/USD"},
    {"code": "DEXCHUS", "category": "거시경제", "name_ko": "중국 위안/달러 환율 (FRED)",
     "name_en": "Chinese Yuan / USD Exchange Rate (FRED DEXCHUS)",
     "desc_ko": "FRED 시리즈 DEXCHUS. 중국은 세계 최대 대두유 수입국. CNY 강세 → 수입 구매력 향상 → 수입 수요 증가 → 가격 상승 지지. CNY 약세는 반대 효과.",
     "desc_en": "FRED DEXCHUS. China is the world's largest soybean oil importer. CNY appreciation boosts import purchasing power, supporting prices; CNY weakness has the opposite effect.",
     "source": "FRED (Federal Reserve H.10)", "freq": "일간", "unit": "CNY/USD"},
    {"code": "DEXMAUS", "category": "거시경제", "name_ko": "말레이시아 링깃/달러 환율 (FRED)",
     "name_en": "Malaysian Ringgit / USD Exchange Rate (FRED DEXMAUS)",
     "desc_ko": "FRED 시리즈 DEXMAUS. 말레이시아는 세계 2위 팜유 생산국. MYR 약세 → 팜유 달러 가격 하락 → CPO-SBO 스프레드 확대 → 대두유 대체 수요 압박.",
     "desc_en": "FRED DEXMAUS. Malaysia is the world's 2nd largest palm oil producer. MYR depreciation lowers CPO dollar prices → CPO-SBO spread widens → substitution pressure on soybean oil.",
     "source": "FRED (Federal Reserve H.10)", "freq": "일간", "unit": "MYR/USD"},
    {"code": "VIXCLS", "category": "거시경제", "name_ko": "CBOE 변동성지수 (VIX)",
     "name_en": "CBOE Volatility Index (VIX, FRED VIXCLS)",
     "desc_ko": "FRED 시리즈 VIXCLS. '공포지수'. VIX >30 → 위험회피 심화 → 원자재 선물 투기포지션 청산 → 대두유 가격 급락 위험. 반대로 VIX 하락기에는 상품 가격 상승 경향. 단기 가격 변동성 선행지표.",
     "desc_en": "FRED VIXCLS. 'Fear gauge'. VIX >30 → risk-off → commodity futures liquidation → soybean oil price drop risk. VIX decline periods tend to support commodity price rises. Leading indicator of short-term price volatility.",
     "source": "FRED / CBOE", "freq": "일간", "unit": "index"},
    # ── 지정학 ──
    {"code": "GPR", "category": "지정학", "name_ko": "지정학 리스크 지수 (GPR)",
     "name_en": "Geopolitical Risk Index (GPR)",
     "desc_ko": "Caldara & Iacoviello GPR 지수. 전쟁·테러·정치 위기 뉴스 기반. 정규화 값 >0.022 → C-03 구조적 단절 경보.",
     "desc_en": "Caldara & Iacoviello GPR. Based on war/terror/political crisis news. Normalized >0.022 triggers C-03 alert.",
     "source": "policyuncertainty.com", "freq": "월간", "unit": "index (≈100 baseline)"},
    {"code": "HORMUZ_THREAT_LEVEL", "category": "지정학", "name_ko": "호르무즈 해협 위협 수준",
     "name_en": "Strait of Hormuz Threat Level",
     "desc_ko": "이란-미국 긴장·후티 공격 모니터링. 봉쇄 위협 → 유가 급등 → 벙커유 비용 → CFR 운임 프리미엄 +3~8%.",
     "desc_en": "Iran-US tension / Houthi attack monitoring. Closure threat → oil spike → bunker cost → CFR freight +3-8%.",
     "source": "Perplexity Pro (실시간)", "freq": "일간", "unit": "1=Low/2=Med/3=High"},
    # ── 기후 ──
    {"code": "ENSO_ONI", "category": "기후", "name_ko": "ENSO 오세아닉 니뇨 지수 (ONI)",
     "name_en": "ENSO Oceanic Niño Index (ONI)",
     "desc_ko": "엘니뇨(+0.5↑)/라니냐(-0.5↓) 판단 지수. 브라질·아르헨티나 강수 패턴 → 대두 생산량 직결. |ONI|≥0.5 → C-03 기후 경보.",
     "desc_en": "El Niño/La Niña threshold: ±0.5. Controls Brazil/Argentina rainfall → soybean production. |ONI|≥0.5 = C-03 alert.",
     "source": "NOAA CPC", "freq": "월간", "unit": "°C anomaly"},
    {"code": "DROUGHT_D2", "category": "기후", "name_ko": "미국 심각 가뭄 비율 (D2)",
     "name_en": "US Severe Drought Coverage (D2)",
     "desc_ko": "USDM 가뭄 지수 D2(심각) 면적 비율. 미국 대두 Top-5 생산주(IA/IL/IN/MN/NE) 기준. 작황 스트레스 선행지표.",
     "desc_en": "USDM D2 severe drought coverage for top-5 US soybean states. Leading indicator for crop stress.",
     "source": "drought.gov / USDM", "freq": "주간", "unit": "% of area"},
    {"code": "T2M_BR_Mato_Grosso", "category": "기후", "name_ko": "브라질 마토그로소 기온 (NASA POWER)",
     "name_en": "Brazil Mato Grosso Temperature (NASA POWER)",
     "desc_ko": "브라질 최대 대두 생산지 기온. 고온 스트레스(>35°C) → 대두 착협기 생산량 감소.",
     "desc_en": "Temperature in Brazil's largest soybean region. Heat stress (>35°C) during pod fill reduces yield.",
     "source": "NASA POWER API", "freq": "월간", "unit": "°C"},
    # ── 작황 ──
    {"code": "SBO_PRODUCTION", "category": "작황", "name_ko": "대두유 글로벌 생산량 (USDA PSD)",
     "name_en": "Global Soybean Oil Production (USDA PSD)",
     "desc_ko": "USDA FAS PSD 마케팅연도별 글로벌 생산량. WASDE 발표 시 가격 변동의 핵심 드라이버.",
     "desc_en": "USDA FAS PSD global production by marketing year. Key price driver on WASDE release.",
     "source": "USDA FAS OpenData API", "freq": "마케팅연도", "unit": "1000 MT"},
    {"code": "SBO_ENDING_STOCKS", "category": "작황", "name_ko": "대두유 기말 재고 (USDA PSD)",
     "name_en": "Global Soybean Oil Ending Stocks (USDA PSD)",
     "desc_ko": "재고/소비 비율(STU) <10% → C-03 공급 스트레스 경보. 역대 최저 재고는 가격 급등의 선행지표.",
     "desc_en": "Stocks-to-use <10% triggers C-03 supply stress alert. Record-low stocks precede price spikes.",
     "source": "USDA FAS OpenData API", "freq": "마케팅연도", "unit": "1000 MT"},
    {"code": "SOYBEAN_PROD_BU", "category": "작황", "name_ko": "미국 주별 대두 생산량 (NASS)",
     "name_en": "US State Soybean Production (NASS)",
     "desc_ko": "USDA NASS 주별 대두 생산량. IA/IL/IN/MN/NE 합산 → 미국 전체 대두유 원료 공급 예측.",
     "desc_en": "USDA NASS state-level soybean production. Sum of top-5 states forecasts US soybean oil feedstock supply.",
     "source": "USDA NASS QuickStats", "freq": "연간", "unit": "Bushels"},
    {"code": "SOYBEAN_PROD_TONNE_AR", "category": "작황", "name_ko": "아르헨티나 대두 생산량 (INDEC)",
     "name_en": "Argentina Soybean Production (INDEC)",
     "desc_ko": "INDEC 공식 통계. 아르헨티나는 세계 1위 대두유 수출국. 가뭄·라니냐 시 생산 급감 → 국제가 급등.",
     "desc_en": "INDEC official stats. Argentina is the world's largest soybean oil exporter. Drought/La Niña → supply shock.",
     "source": "datos.gob.ar / INDEC", "freq": "연간", "unit": "Tonnes"},
    # ── 해운 ──
    {"code": "BCAA", "category": "해운", "name_ko": "BCAA (식물성유지 탱커 운임)",
     "name_en": "Baltic Chemical & Agricultural Oil Assessments",
     "desc_ko": "Baltic Exchange 2025-02 출시. 대두유·팜유·팜올레인 탱커 운임 전용. 한국 CIF 도착 원가에 직결.",
     "desc_en": "Launched Feb 2025 by Baltic Exchange. Vegetable oil tanker freight: CPO/SBO/palm olein routes. Direct CIF cost driver.",
     "source": "Perplexity Pro (직접 API: Baltic Exchange/ICE 기업 구독)", "freq": "일간", "unit": "USD/MT"},
    {"code": "BDI", "category": "해운", "name_ko": "발틱 건화물 지수 (BDI)",
     "name_en": "Baltic Dry Index (BDI)",
     "desc_ko": "건화물 운임 지수. 대두유 직접 관련성은 낮으나 글로벌 무역 경기·원자재 수요 대리 지표. C-03 z>2σ(90일) → 구조적 단절 경보.",
     "desc_en": "Dry bulk freight. Indirect indicator of global trade activity. C-03 alert: z-score >2σ (90-day rolling).",
     "source": "Trading Economics / Baltic Exchange", "freq": "일간", "unit": "points"},
    # ── 수입통계 ──
    {"code": "import_cif_usd", "category": "수입통계", "name_ko": "한국 대두유 수입 CIF 금액 (HS 1507)",
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
    "economic_indicators": "거시경제(Fed/CPI/FX/Brent)",
    "shipping_indices":    "해운지수(BCAA/BDI)",
    "crop_data":           "작황(WASDE/PSD API)",
    "wasde_historical":    "작황(WASDE 수동 업로드)",
    "psd_historical":      "작황(PS&D 수동 업로드)",
    "climate_data":        "기후(ONI/기상이상)",
    "geopolitical_indices":"지정학(GPR/호르무즈)",
    "production_data":     "생산량(NASS/FAOSTAT/NASA)",
    "commodity_data":      "상품가격(CBOT/CPO/ARS/가뭄)",
    "customs_import":      "수입통계(관세청 HS1507)",
    "gats_quantity_historical": "무역통계(GATS 미국 수출량)",
    "gats_value_historical":    "무역통계(GATS 미국 수출액)",
    "fao_amis_historical": "수급전망(FAO AMIS)",
    "geointel":            "지정학 인텔리전스(USGS/NOAA/GDELT/FIRMS)",
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


def _data_integrity_flag(df: pd.DataFrame) -> str:
    """데이터 무결성(완전성) 판정: value 비결측 비율 기반.

    완전성 = 비결측 value / 전체 행. ≥0.95 PASS · ≥0.80 WARN · 그 외 LOW.
    indicator_code/value 스키마가 아니면 numeric 컬럼 평균 비결측률 사용.
    """
    if "value" in df.columns:
        total = len(df)
        non_null = int(pd.to_numeric(df["value"], errors="coerce").notna().sum())
    else:
        num = df.select_dtypes(include="number")
        if num.empty or len(df) == 0:
            return "N/A"
        total = num.size
        non_null = int(num.notna().sum().sum())
    if total == 0:
        return "N/A"
    pct = non_null / total * 100
    flag = "✅" if pct >= 95 else ("⚠️" if pct >= 80 else "🚨")
    return f"{flag} {pct:.0f}%"


def _indicator_count(df: pd.DataFrame) -> int:
    """수집된 변수(지표) 항목 수."""
    if "indicator_code" in df.columns:
        return int(df["indicator_code"].nunique())
    num = [c for c in df.select_dtypes(include="number").columns
           if c not in ("ingested_at", "rows")]
    return len(num)


def _build_data_status(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """커넥터별 데이터 현황 테이블 (변수항목·행수·날짜범위·무결성·신선도)."""
    rows = []
    for key, label in FILE_PATTERNS.items():
        if key not in frames:
            rows.append({"커넥터": label, "변수항목": 0, "행수": 0,
                         "날짜범위": "미수집", "무결성": "N/A",
                         "신선도": "❌ 데이터 없음"})
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
            "변수항목": _indicator_count(df),
            "행수":     len(df),
            "날짜범위": date_range,
            "무결성":   _data_integrity_flag(df),
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


def _check_granger_conditions(
    wide: pd.DataFrame, target_col: str,
) -> pd.DataFrame:
    """각 변수의 Granger 인과검정 선결 조건을 변수별로 분류한다.

    조건 1 — 관측치: 비결측 관측치 ≥ GRANGER_MIN_OBS (30개)
    조건 2 — 결측률: < 20%
    조건 3 — 정상성: ADF p < 0.05 (원 시리즈 또는 1차 차분 후)

    Returns:
        DataFrame: [변수|전체관측치|결측률(%)|ADF_p(원)|ADF_p(차분)|정상성|상태|비고]
        내부 컬럼: _ready (bool), _needs_diff (bool)
    """
    try:
        from statsmodels.tsa.stattools import adfuller
    except ImportError:
        print("[경고] statsmodels 미설치 — Granger 조건 점검 건너뜀")
        return pd.DataFrame()

    rows: list[dict] = []
    for col in wide.columns:
        if col == target_col:
            continue

        s_full  = wide[col]
        s_clean = s_full.dropna()
        total_obs = len(s_clean)
        null_pct  = round(s_full.isnull().mean() * 100, 1)

        obs_ok  = total_obs >= GRANGER_MIN_OBS
        null_ok = null_pct < 20.0

        adf_p: float | None = None
        adf_p_diff: float | None = None
        stationary = False
        stat_after_diff = False

        if obs_ok and null_ok:
            try:
                adf_r = adfuller(s_clean, autolag="AIC", maxlag=min(12, len(s_clean) // 4))
                adf_p = round(float(adf_r[1]), 4)
                stationary = adf_p < 0.05
            except Exception:
                pass
            if not stationary and len(s_clean) >= GRANGER_MIN_OBS + 1:
                try:
                    diff = s_clean.diff().dropna()
                    adf_d = adfuller(diff, autolag="AIC", maxlag=min(12, len(diff) // 4))
                    adf_p_diff = round(float(adf_d[1]), 4)
                    stat_after_diff = adf_p_diff < 0.05
                except Exception:
                    pass

        ready      = obs_ok and null_ok and (stationary or stat_after_diff)
        needs_diff = ready and not stationary

        if not obs_ok:
            status = "⚠️ 관측치 부족"
            note   = f"비결측 관측치 {total_obs}개 (최소 {GRANGER_MIN_OBS}개 필요)"
        elif not null_ok:
            status = "⚠️ 결측 과다"
            note   = f"결측률 {null_pct}% (허용 상한 20%)"
        elif not (stationary or stat_after_diff):
            status = "⚠️ 비정상 시계열"
            note   = f"ADF p={adf_p}(원), p={adf_p_diff}(차분) — 단위근 제거 불가"
        else:
            diff_note = "1차 차분 후 정상" if needs_diff else "정상 시계열"
            status = "✅ 조건 충족"
            note   = f"ADF p={adf_p_diff if needs_diff else adf_p} ({diff_note})"

        rows.append({
            "변수":        col,
            "전체관측치":  total_obs,
            "결측률(%)":   null_pct,
            "ADF_p(원)":   adf_p,
            "ADF_p(차분)": adf_p_diff,
            "정상성":      "✅" if stationary else ("✅(1차차분)" if stat_after_diff else "❌"),
            "상태":        status,
            "비고":        note,
            "_ready":      ready,
            "_needs_diff": needs_diff,
        })

    return pd.DataFrame(rows) if rows else pd.DataFrame()


def _granger_causality_by_year(
    wide: pd.DataFrame,
    target_col: str,
    conditions_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """2020~작년 연도별 + 전체 기간 Granger 인과검정을 실행한다.

    분석 대상: conditions_df에서 _ready=True 인 변수만 실행.
    반환 컬럼: [변수|연도|관측치수|F통계량|p값|최적시차|인과성]
    인과성 해석: X → Y 방향 (X가 Y의 과거값보다 Y 예측에 추가 정보 제공).
    """
    try:
        from statsmodels.tsa.stattools import grangercausalitytests, adfuller
    except ImportError:
        print("[경고] statsmodels 미설치 — Granger 인과검정 건너뜀")
        return pd.DataFrame()

    if wide.empty or target_col not in wide.columns:
        return pd.DataFrame()

    if conditions_df is not None and not conditions_df.empty and "_ready" in conditions_df.columns:
        ready_vars = conditions_df[conditions_df["_ready"]]["변수"].tolist()
        needs_diff = set(conditions_df[conditions_df["_needs_diff"]]["변수"].tolist())
    else:
        ready_vars = [c for c in wide.columns if c != target_col]
        needs_diff = set()

    if not ready_vars:
        return pd.DataFrame()

    # 타깃 정상성 확인
    t_series = wide[target_col].dropna()
    target_needs_diff = False
    if len(t_series) >= GRANGER_MIN_OBS:
        try:
            adf_t = adfuller(t_series, autolag="AIC", maxlag=min(12, len(t_series) // 4))
            target_needs_diff = adf_t[1] >= 0.05
        except Exception:
            pass

    # 분석 기간 정의: 연도별 + 전체
    last_year = date.today().year - 1
    periods: list[tuple[str, str, str | int]] = [
        (f"{yr}-01-01", f"{yr}-12-31", yr) for yr in GRANGER_YEARS if yr <= last_year
    ]
    periods.append(("2017-01-01", f"{last_year}-12-31", f"전체(2017~{last_year})"))

    rows: list[dict] = []
    for p_start, p_end, period_label in periods:
        wide_p   = wide.loc[p_start:p_end].copy()
        target_p = wide_p[target_col].dropna()

        if len(target_p) < GRANGER_MIN_OBS:
            for var in ready_vars:
                rows.append({"변수": var, "연도": period_label,
                             "관측치수": len(target_p), "F통계량": None,
                             "p값": None, "최적시차": None,
                             "인과성": f"⚠️ 타깃 관측치 부족 ({len(target_p)}개)"})
            continue

        for var in ready_vars:
            if var not in wide_p.columns:
                rows.append({"변수": var, "연도": period_label, "관측치수": 0,
                             "F통계량": None, "p값": None, "최적시차": None,
                             "인과성": "❌ 해당 기간 변수 없음"})
                continue

            x_p = wide_p[var].dropna()
            common = target_p.index.intersection(x_p.index)
            if len(common) < GRANGER_MIN_OBS:
                rows.append({"변수": var, "연도": period_label,
                             "관측치수": len(common), "F통계량": None,
                             "p값": None, "최적시차": None,
                             "인과성": f"⚠️ 공통 관측치 부족 ({len(common)}개)"})
                continue

            y_s = target_p.loc[common]
            x_s = x_p.loc[common]
            if target_needs_diff:
                y_s = y_s.diff().dropna()
                x_s = x_s.loc[y_s.index]
            if var in needs_diff:
                x_s = x_s.diff().dropna()
                y_s = y_s.loc[x_s.index]

            data = pd.concat([y_s.rename(target_col), x_s.rename(var)], axis=1).dropna()
            if len(data) < GRANGER_MIN_OBS:
                rows.append({"변수": var, "연도": period_label,
                             "관측치수": len(data), "F통계량": None,
                             "p값": None, "최적시차": None,
                             "인과성": f"⚠️ 차분 후 관측치 부족 ({len(data)}개)"})
                continue

            try:
                max_lag = max(1, min(GRANGER_MAX_LAG, len(data) // 5))
                result  = grangercausalitytests(
                    data[[target_col, var]], maxlag=max_lag, verbose=False,
                )
                best_lag = min(result, key=lambda lg: result[lg][0]["ssr_ftest"][1])
                f_stat   = round(float(result[best_lag][0]["ssr_ftest"][0]), 4)
                p_val    = round(float(result[best_lag][0]["ssr_ftest"][1]), 4)
                causal   = "✅ 인과관계 있음" if p_val < GRANGER_ALPHA else "— 기각불가"
                rows.append({"변수": var, "연도": period_label,
                             "관측치수": len(data), "F통계량": f_stat,
                             "p값": p_val, "최적시차": best_lag, "인과성": causal})
            except Exception as e:
                rows.append({"변수": var, "연도": period_label, "관측치수": len(data),
                             "F통계량": None, "p값": None, "최적시차": None,
                             "인과성": f"⚠️ 오류: {e}"})

    return pd.DataFrame(rows) if rows else pd.DataFrame()


def _check_structural_breaks(frames: dict[str, pd.DataFrame]) -> list[dict]:
    """C-03 구조적 단절 임계값 현황 점검.

    주의: 커넥터 수집 실패 시 해당 임계값 항목은 '데이터 미수집' 상태로 표시됨.
    동일 값이 반복되면 원인 1순위: 커넥터 수집 실패 → 새 parquet 미생성.
    원인 2순위: 월별 지표(GPR/ENSO)의 갱신 주기 — 한 달에 한 번만 변경 정상.
    """
    alerts = []
    today = date.today().isoformat()

    def _is_fresh(df: pd.DataFrame, stale_days: int = 5) -> bool:
        if "ingested_at" not in df.columns:
            return False
        max_ts = pd.to_datetime(df["ingested_at"], utc=True, errors="coerce").max()
        return pd.notna(max_ts) and np.busday_count(max_ts.date(), date.today()) <= stale_days

    # GPR 지수 (normalized)
    if "geopolitical_indices" in frames:
        gpr_df = frames["geopolitical_indices"]
        if "indicator_code" in gpr_df.columns:
            gpr = gpr_df[gpr_df["indicator_code"] == "GPR_NORMALIZED"]
        else:
            gpr = pd.DataFrame()
        if not gpr.empty and "value" in gpr.columns and not gpr["value"].dropna().empty:
            latest_gpr = float(gpr["value"].dropna().iloc[-1])
            fresh = _is_fresh(gpr_df)
            alerts.append({
                "변수": "GPR_NORMALIZED",
                "현재값": round(latest_gpr, 4),
                "임계값": THRESHOLDS["GPR_NORMALIZED"]["alert"],
                "상태": "🚨 임계초과" if latest_gpr > 0.022 else "✅ 정상",
                "설명": THRESHOLDS["GPR_NORMALIZED"]["label"],
                "데이터신선도": "✅ 최신" if fresh else "⚠️ STALE — 커넥터 수집 실패 의심",
            })
        else:
            alerts.append({
                "변수": "GPR_NORMALIZED",
                "현재값": "N/A",
                "임계값": THRESHOLDS["GPR_NORMALIZED"]["alert"],
                "상태": "❓ 데이터 미수집",
                "설명": THRESHOLDS["GPR_NORMALIZED"]["label"],
                "데이터신선도": "❌ parquet 없음",
            })
    else:
        alerts.append({
            "변수": "GPR_NORMALIZED", "현재값": "N/A",
            "임계값": 0.022, "상태": "❓ 데이터 미수집",
            "설명": "지정학 리스크 지수 — geopolitical_indices 커넥터 수집 실패",
            "데이터신선도": "❌ parquet 없음",
        })

    # ENSO ONI
    if "climate_data" in frames:
        oni_df = frames["climate_data"]
        oni = oni_df[oni_df["indicator_code"] == "ONI"] if "indicator_code" in oni_df.columns else pd.DataFrame()
        if not oni.empty and "value" in oni.columns and not oni["value"].dropna().empty:
            latest_oni = float(oni["value"].dropna().iloc[-1])
            fresh = _is_fresh(oni_df)
            alerts.append({
                "변수": "ENSO_ONI",
                "현재값": round(latest_oni, 2),
                "임계값": "±0.5",
                "상태": "🚨 임계초과" if abs(latest_oni) >= 0.5 else "✅ 정상",
                "설명": THRESHOLDS["ENSO_ONI"]["label"],
                "데이터신선도": "✅ 최신" if fresh else "⚠️ STALE (월별 갱신 정상)",
            })
        else:
            alerts.append({
                "변수": "ENSO_ONI", "현재값": "N/A", "임계값": "±0.5",
                "상태": "❓ 데이터 미수집",
                "설명": "ENSO ONI — climate_data 커넥터 수집 실패",
                "데이터신선도": "❌ parquet 없음",
            })
    else:
        alerts.append({
            "변수": "ENSO_ONI", "현재값": "N/A", "임계값": "±0.5",
            "상태": "❓ 데이터 미수집",
            "설명": "기후 레짐 전환 — climate_data 커넥터 수집 실패",
            "데이터신선도": "❌ parquet 없음",
        })

    # BDI z-score (90일 rolling)
    if "shipping_indices" in frames:
        bdi_df = frames["shipping_indices"]
        bdi = bdi_df[bdi_df["indicator_code"] == "BDI"] if "indicator_code" in bdi_df.columns else pd.DataFrame()
        if not bdi.empty and "value" in bdi.columns and len(bdi) > 3:
            vals = pd.to_numeric(bdi["value"], errors="coerce").dropna()
            if len(vals) >= 5:
                roll_mean = vals.rolling(min(90, len(vals))).mean().iloc[-1]
                roll_std  = vals.rolling(min(90, len(vals))).std().iloc[-1]
                z = (vals.iloc[-1] - roll_mean) / roll_std if roll_std > 0 else 0.0
                fresh = _is_fresh(bdi_df)
                alerts.append({
                    "변수": "BDI_ZSCORE",
                    "현재값": round(z, 2),
                    "임계값": "2.0σ",
                    "상태": "🚨 임계초과" if z > 2.0 else "✅ 정상",
                    "설명": THRESHOLDS["BDI"]["label"],
                    "데이터신선도": "✅ 최신" if fresh else "⚠️ STALE — 커넥터 수집 실패 의심",
                })
            else:
                alerts.append({
                    "변수": "BDI_ZSCORE", "현재값": f"{len(vals)}건(부족)",
                    "임계값": "2.0σ", "상태": "⚠️ 데이터 부족 (90일 미만)",
                    "설명": "BDI — z-score 계산 최소 5건 필요",
                    "데이터신선도": "⚠️ 데이터 부족",
                })
        else:
            alerts.append({
                "변수": "BDI_ZSCORE", "현재값": "N/A", "임계값": "2.0σ",
                "상태": "❓ 데이터 미수집",
                "설명": "해운비용 급등 — shipping_indices 커넥터 수집 실패",
                "데이터신선도": "❌ parquet 없음",
            })
    else:
        alerts.append({
            "변수": "BDI_ZSCORE", "현재값": "N/A", "임계값": "2.0σ",
            "상태": "❓ 데이터 미수집",
            "설명": "해운비용 급등 — shipping_indices 커넥터 수집 실패",
            "데이터신선도": "❌ parquet 없음",
        })

    return alerts


def _build_category_summary(importance_df: pd.DataFrame, frames: dict) -> dict:
    """카테고리별 변수 중요도 요약 생성.

    VARIABLE_CATALOG 기준으로 변수를 P-카테고리로 그룹화하고,
    |Pearson r| > 0.3 유의 변수 수와 평균 |r|을 카테고리별로 집계.

    Returns:
        {"거시경제": {"count": N, "sig_count": N, "mean_abs_r": 0.XX, "top_var": "DEXBZUS"}, ...}
    """
    code_to_category: dict[str, str] = {v["code"]: v["category"] for v in VARIABLE_CATALOG}

    summary: dict[str, dict] = {}

    if importance_df.empty:
        return summary

    for _, row in importance_df.iterrows():
        var_code = str(row["변수"])
        cat = code_to_category.get(var_code, "기타")
        abs_r = abs(float(row["피어슨_r"])) if pd.notna(row["피어슨_r"]) else 0.0

        if cat not in summary:
            summary[cat] = {"count": 0, "sig_count": 0, "_abs_r_sum": 0.0, "_top_r": 0.0, "top_var": var_code}

        summary[cat]["count"] += 1
        summary[cat]["_abs_r_sum"] += abs_r
        if abs_r > 0.3:
            summary[cat]["sig_count"] += 1
        if abs_r > summary[cat]["_top_r"]:
            summary[cat]["_top_r"] = abs_r
            summary[cat]["top_var"] = var_code

    for cat, data in summary.items():
        n = data["count"]
        data["mean_abs_r"] = round(data["_abs_r_sum"] / n, 3) if n > 0 else 0.0
        del data["_abs_r_sum"]
        del data["_top_r"]

    return summary


def _render_executive_summary(
    alerts: list[dict],
    category_summary: dict,
    run_ts: str,
    lang: Literal["ko", "en"] = "ko",
) -> str:
    """C-레벨 임원 요약 HTML 대시보드 렌더링.

    Signal banner 색상:
      GREEN  — 임계값 위반 없음
      AMBER  — 1~2개 위반
      RED    — 3개 이상 위반
    """
    breach_count = sum(1 for a in alerts if "🚨" in a.get("상태", ""))
    total_vars = sum(d["count"] for d in category_summary.values()) if category_summary else 0
    total_alerts = len(alerts)

    # 최고 상관 변수
    top_var_name = "N/A"
    top_var_r = 0.0
    for data in category_summary.values():
        if data.get("mean_abs_r", 0.0) > top_var_r:
            top_var_r = data["mean_abs_r"]
            top_var_name = data.get("top_var", "N/A")

    # 시그널 배너
    if breach_count == 0:
        signal_class = "signal-green"
        signal_text = "✅ 정상 — 현재 구조적 임계값 위반 없음" if lang == "ko" else "✅ NORMAL — No structural threshold breaches"
    elif breach_count <= 2:
        signal_class = "signal-amber"
        signal_text = f"⚠️ 주의 — {breach_count}개 임계값 위반 감지. 모니터링 강화 필요." if lang == "ko" else f"⚠️ CAUTION — {breach_count} threshold breach(es) detected. Increase monitoring."
    else:
        signal_class = "signal-red"
        signal_text = f"🚨 긴급 — {breach_count}개 임계값 위반. C-03 진행 전 인간 검토 필요." if lang == "ko" else f"🚨 URGENT — {breach_count} threshold breaches. Human review required before C-03 proceeds."

    # KPI 카드
    lbl_vars   = "수집 변수"       if lang == "ko" else "Variables Collected"
    lbl_alerts = "임계값 경보"     if lang == "ko" else "Threshold Alerts"
    lbl_top    = "최고 상관 변수"  if lang == "ko" else "Top Correlated Variable"

    kpi_html = f"""<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-num">{total_vars}</div>
    <div class="kpi-lbl">{lbl_vars}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-num">{breach_count}/{total_alerts}</div>
    <div class="kpi-lbl">{lbl_alerts}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-num" style="font-size:18px">{top_var_name}</div>
    <div class="kpi-lbl">{lbl_top} (|r|={top_var_r:.2f})</div>
  </div>
</div>"""

    # 카테고리 요약 테이블
    cat_title = "카테고리별 중요도 요약" if lang == "ko" else "Category-Level Importance Summary"
    if category_summary:
        cat_rows = ""
        for cat, data in sorted(category_summary.items()):
            cat_rows += (
                f"<tr><td>{cat}</td>"
                f"<td style='text-align:center'>{data['count']}</td>"
                f"<td style='text-align:center'>{data['sig_count']}</td>"
                f"<td style='text-align:center'>{data['mean_abs_r']:.3f}</td>"
                f"<td><code>{data['top_var']}</code></td></tr>"
            )
        cat_table = f"""<h3 style="color:#3949ab;margin-top:18px">{cat_title}</h3>
<table class="tbl">
<thead><tr>
  <th>{'카테고리' if lang == 'ko' else 'Category'}</th>
  <th>{'변수수' if lang == 'ko' else 'Variables'}</th>
  <th>{'유의변수(|r|>0.3)' if lang == 'ko' else 'Significant (|r|>0.3)'}</th>
  <th>{'평균 |r|' if lang == 'ko' else 'Mean |r|'}</th>
  <th>{'대표 변수' if lang == 'ko' else 'Top Variable'}</th>
</tr></thead>
<tbody>{cat_rows}</tbody>
</table>"""
    else:
        no_data = "데이터 부족 — 카테고리 요약 생성 불가" if lang == "ko" else "Insufficient data — category summary unavailable"
        cat_table = f"<p>{no_data}</p>"

    # C-레벨 핵심 메시지
    if category_summary:
        top_cat = max(category_summary, key=lambda c: category_summary[c]["mean_abs_r"])
        top_r_val = category_summary[top_cat]["mean_abs_r"]
        if lang == "ko":
            clevel_msg = (
                f"현재 {top_cat}이 대두유 가격 변동성에 가장 높은 영향을 미치고 있습니다 "
                f"(평균 |r|={top_r_val:.2f}). "
                f"{breach_count}개 구조적 임계값이 활성화됨."
            )
        else:
            clevel_msg = (
                f"{top_cat} currently exerts the highest influence on soybean oil price volatility "
                f"(mean |r|={top_r_val:.2f}). "
                f"{breach_count} structural threshold(s) active."
            )
    else:
        clevel_msg = (
            "데이터 수집 진행 중 — 30일 이상 시계열 누적 후 카테고리별 영향도 분석이 가능합니다."
            if lang == "ko" else
            "Data collection in progress — category-level analysis available after 30+ days of accumulation."
        )

    note_label = "핵심 내용"

    return f"""<div class="{signal_class}">{signal_text}</div>
{kpi_html}
{cat_table}
<div class="note"><strong>{note_label}:</strong> {clevel_msg}</div>"""


_CAUSAL_CHAINS: list[dict[str, str]] = [
    # ── 정책·규제 ─────────────────────────────────────────────────────────────────
    {
        "driver_ko": "Clean Fuel 생산 세액공제 (45Z)",
        "driver_en": "Clean Fuel Production Tax Credit (45Z)",
        "chain_ko": "45Z 세액공제 시행 → 미국 내 SBO 바이오디젤 수요 증가 → 미국 수출 물량 감소·한국 수입 경쟁 심화 → 국제 대두유 가격 상승",
        "chain_en": "45Z tax credit enacted → US domestic SBO biodiesel demand rises → US export volume falls, Korean import competition intensifies → global SBO price increase",
        "direction": "up",
        "category_ko": "정책·규제",
        "category_en": "Policy & Regulation",
    },
    {
        "driver_ko": "인도네시아 B35→B40 바이오디젤 의무 확대",
        "driver_en": "Indonesia B35→B40 Biodiesel Mandate Expansion",
        "chain_ko": "B40 의무 시행 → CPO 내수 소비 증가 → CPO 수출 감소 → CPO-SBO 스프레드 축소 → SBO 대체 수요 감소 → 가격 하락 압력",
        "chain_en": "B40 mandate enacted → CPO domestic consumption rises → CPO export falls → CPO-SBO spread narrows → SBO substitution demand falls → downward price pressure",
        "direction": "down",
        "category_ko": "정책·규제",
        "category_en": "Policy & Regulation",
    },
    {
        "driver_ko": "아르헨티나 대두유 수출세 인상",
        "driver_en": "Argentina SBO Export Tax Hike",
        "chain_ko": "아르헨티나 수출세 인상 → 수출 채산성 악화 → 글로벌 공급 감소 → 대두유 가격 상승",
        "chain_en": "Argentina raises export tax → export profitability deteriorates → global supply contracts → SBO price rises",
        "direction": "up",
        "category_ko": "정책·규제",
        "category_en": "Policy & Regulation",
    },
    {
        "driver_ko": "EU 탈삼림 규정(EUDR) 팜유 규제 강화",
        "driver_en": "EU Deforestation Regulation (EUDR) Palm Oil Restrictions",
        "chain_ko": "EUDR 발효 → EU 팜유 시장 접근 차단 → EU 내 SBO 대체 수요 증가 → 글로벌 SBO 가격 상승",
        "chain_en": "EUDR enacted → palm oil EU market access blocked → EU SBO substitution demand rises → global SBO price rises",
        "direction": "up",
        "category_ko": "정책·규제",
        "category_en": "Policy & Regulation",
    },
    {
        "driver_ko": "인도 식용유 수입관세 인하",
        "driver_en": "India Edible Oil Import Duty Cut",
        "chain_ko": "인도 수입관세 인하 → CPO/SBO 수입 증가(세계 최대 식용유 수입국) → 글로벌 SBO 수요 증가 → 가격 상승",
        "chain_en": "India cuts import duty → CPO/SBO imports surge (world's largest edible oil importer) → global SBO demand rises → price increase",
        "direction": "up",
        "category_ko": "정책·규제",
        "category_en": "Policy & Regulation",
    },
    # ── 기후·작황 ─────────────────────────────────────────────────────────────────
    {
        "driver_ko": "ENSO 라니냐 — 남미 가뭄",
        "driver_en": "ENSO La Niña — South America Drought",
        "chain_ko": "ENSO 라니냐 발생 → 브라질·아르헨티나 강우량 감소(가뭄) → 대두 작황 감소 → 대두유 생산량 감소 → 가격 상승",
        "chain_en": "La Niña develops → rainfall deficit in Brazil & Argentina → soybean crop failure → SBO production decline → price rise",
        "direction": "up",
        "category_ko": "기후·작황",
        "category_en": "Climate & Crop",
    },
    {
        "driver_ko": "브라질 파종기 토양 수분 이상 (9~11월)",
        "driver_en": "Brazil Planting Season Soil Moisture Anomaly (Sep–Nov)",
        "chain_ko": "파종기 가뭄(9~11월) → 대두 발아율 저하 → 재배 면적 축소 우려 → 선물 가격 선반영 상승",
        "chain_en": "Planting season drought (Sep–Nov) → lower soybean germination rate → acreage reduction risk → futures price pre-rally",
        "direction": "up",
        "category_ko": "기후·작황",
        "category_en": "Climate & Crop",
    },
    {
        "driver_ko": "WASDE 대두유 재고사용비율(STU) 하락",
        "driver_en": "WASDE SBO Stocks-to-Use Ratio (STU) Decline",
        "chain_ko": "WASDE STU < 10% 발표 → 글로벌 공급 부족 신호 → 투기 세력 순매수 포지션 증가(COT) → 선물 가격 급등",
        "chain_en": "WASDE STU < 10% released → global supply deficit signal → speculative long position surge (COT) → futures price spike",
        "direction": "up",
        "category_ko": "기후·작황",
        "category_en": "Climate & Crop",
    },
    # ── 지정학·무역 ───────────────────────────────────────────────────────────────
    {
        "driver_ko": "호르무즈/말라카 해협 위기",
        "driver_en": "Hormuz / Malacca Strait Crisis",
        "chain_ko": "해협 봉쇄 위기 → 탱커 운임 급등(BDI 연동) → CIF 비용 증가 → 한국 수입 가격 상승",
        "chain_en": "Strait closure risk → tanker freight rates spike (BDI correlated) → CIF cost increase → Korean import price rises",
        "direction": "up",
        "category_ko": "지정학·무역",
        "category_en": "Geopolitics & Trade",
    },
    {
        "driver_ko": "미·중 무역 관세 에스컬레이션",
        "driver_en": "US–China Tariff Escalation",
        "chain_ko": "미·중 관세 부과 → 중국의 미국산 SBO 수입 급감 → 미국 수출 여력 과잉 → 단기 가격 하락 압력 → 이후 글로벌 공급망 재편 중기 혼란",
        "chain_en": "US-China tariffs → China reduces US SBO imports sharply → US export surplus builds → short-term downward pressure → mid-term supply chain disruption",
        "direction": "down",
        "category_ko": "지정학·무역",
        "category_en": "Geopolitics & Trade",
    },
    {
        "driver_ko": "중국 정부 SBO 비축 발표",
        "driver_en": "China Government SBO Strategic Reserve Announcement",
        "chain_ko": "중국 비축 발표 → 대규모 수입 기대감 형성 → 글로벌 재고 감소 우려 → 선물 가격 단기 급등",
        "chain_en": "China announces strategic reserve build → large import expectation forms → global inventory draw concern → short-term futures price spike",
        "direction": "up",
        "category_ko": "지정학·무역",
        "category_en": "Geopolitics & Trade",
    },
    # ── 시장 구조 ─────────────────────────────────────────────────────────────────
    {
        "driver_ko": "CPO-SBO 스프레드 확대 (>$175/MT)",
        "driver_en": "CPO-SBO Spread Widening (>$175/MT)",
        "chain_ko": "CPO-SBO 스프레드 > $175/MT → 식품업계 팜유로 대체 → SBO 수요 감소 → 가격 하락 압력",
        "chain_en": "CPO-SBO spread exceeds $175/MT → food manufacturers switch to palm oil → SBO demand falls → downward price pressure",
        "direction": "down",
        "category_ko": "시장 구조",
        "category_en": "Market Structure",
    },
    {
        "driver_ko": "발틱운임지수(BDI) 급등",
        "driver_en": "Baltic Dry Index (BDI) Surge",
        "chain_ko": "BDI 급등 → 해운비 상승 → 남미발 대두유 수출 채산성 악화 → 수출 감소 → 국제가 상승",
        "chain_en": "BDI surges → shipping costs rise → South American SBO export margins compress → exports fall → global price rises",
        "direction": "up",
        "category_ko": "시장 구조",
        "category_en": "Market Structure",
    },
    {
        "driver_ko": "CFTC COT 투기 세력 순매수 증가",
        "driver_en": "CFTC COT Speculative Net Long Position Surge",
        "chain_ko": "헤지펀드·CTA 순매수 포지션 급증 → 선물 가격 모멘텀 강화 → 현물·선도 가격 상승 견인",
        "chain_en": "Hedge fund / CTA net long position surges → futures price momentum builds → spot and forward prices pulled higher",
        "direction": "up",
        "category_ko": "시장 구조",
        "category_en": "Market Structure",
    },
    {
        "driver_ko": "대두 압착 마진(Crush Margin) 축소",
        "driver_en": "Soybean Crush Margin Compression",
        "chain_ko": "SBO가 + SBM가 < 대두가 (압착 마진 마이너스) → 압착 가동률 감소 → SBO 생산 감소 → 공급 축소 → 가격 상승",
        "chain_en": "SBO + SBM < soybean price (negative crush margin) → crushing capacity utilization falls → SBO output declines → supply contracts → price rises",
        "direction": "up",
        "category_ko": "시장 구조",
        "category_en": "Market Structure",
    },
    # ── 지정학·무역 (추가) ────────────────────────────────────────────────────────
    {
        "driver_ko": "수에즈·홍해 후티 공격 — 탱커 우회",
        "driver_en": "Suez / Red Sea Houthi Attacks — Tanker Diversion",
        "chain_ko": "홍해 후티 미사일·드론 공격 → 탱커·컨테이너선 수에즈 우회 불가 → 희망봉 우회(+10~14일) → 벙커유 소비 증가 → 운임 급등(BDI·BCAA 연동) → 남미발 한국 수입 CIF 비용 상승",
        "chain_en": "Houthi attacks in Red Sea → tankers divert from Suez → Cape of Good Hope re-routing (+10–14 days) → bunker fuel surcharge → freight rate spike (BDI/BCAA correlated) → South American SBO CIF cost rises for Korea",
        "direction": "up",
        "category_ko": "지정학·무역",
        "category_en": "Geopolitics & Trade",
    },
    {
        "driver_ko": "우크라이나 흑해 곡물 회랑 붕괴",
        "driver_en": "Ukraine Black Sea Grain Corridor Breakdown",
        "chain_ko": "러-우 전쟁 확전 / 흑해 회랑 협정 파기 → 우크라이나 해바라기유 수출 차단 → 글로벌 식물성유지 공급 부족 → SBO·CPO 대체 수요 급증 → 가격 상승",
        "chain_en": "Russia-Ukraine escalation / Black Sea grain deal collapses → Ukrainian sunflower oil exports blocked → global vegetable oil supply deficit → SBO & CPO substitution demand surges → price spike",
        "direction": "up",
        "category_ko": "지정학·무역",
        "category_en": "Geopolitics & Trade",
    },
    # ── 기후·작황 (추가) ─────────────────────────────────────────────────────────
    {
        "driver_ko": "브라질 대두 수확기 이상 기후 (1~3월)",
        "driver_en": "Brazil Soybean Harvest Anomaly (Jan–Mar)",
        "chain_ko": "라니냐·엘니뇨 전환기 폭우 → 수확 지연·품질 손실 → 브라질산 SBO 공급 차질 → 수출 일정 지연 → 선물 가격 선반영 상승 → 한국 CFR 운임 프리미엄 확대",
        "chain_en": "La Niña/El Niño transition rainfall → harvest delay and quality loss → Brazilian SBO supply disruption → export schedule delays → futures price pre-rally → Korean CFR premium widening",
        "direction": "up",
        "category_ko": "기후·작황",
        "category_en": "Climate & Crop",
    },
]


def _render_feature_selection_methodology(lang: str = "ko") -> str:
    """피처 엔지니어링·선택 방법론 섹션 HTML 렌더링 (D-014/D-015 기준).

    5단계 게이트:
      1단계 DQSOps 품질 게이트 (C-08)
      2단계 단변량 스크리닝 (Pearson r, Granger)
      3단계 다중공선성 제거 (VIF, LASSO L1)
      4단계 ML 중요도 순위 (LASSO+SHAP+Granger 가중 합산)
      5단계 도메인 검토 (P1-01~04)

    Phase A 핵심 피처 8개 (D-015):
      CBOT_SBO_FUTURES, CPO_SBO_SPREAD, WASDE_SBO_STU, BDI,
      FX_BRL_USD, ENSO_ONI, PSD_SOY_CRUSH, GATS_US_SBO_EXPORT_KOREA
    """
    # ── 5단계 게이트 표 ─────────────────────────────────────────────────────────
    if lang == "ko":
        title    = "피처 엔지니어링 및 선택 방법론"
        subtitle = "의사결정 D-014 (5단계 게이트) · D-015 (Phase A 핵심 피처 8개)"
        gate_hdr = ["단계", "게이트명", "기준 / 도구", "임계값", "담당"]
        gate_rows = [
            ("1단계", "DQSOps 품질 게이트",     "C-08 5차원 가중합산 점수",           "≥ 0.70 PASS",           "C-08"),
            ("2단계", "단변량 스크리닝",          "Pearson |r| · Granger 인과검정",    "|r|≥0.25, p<0.05 (Bonferroni 보정)", "C-03/C-06"),
            ("3단계", "다중공선성 제거",          "VIF < 5 · LASSO L1 정규화",         "VIF 임계값 5.0",        "C-03"),
            ("4단계", "ML 중요도 순위 합산",      "0.4×LASSO_rank + 0.3×SHAP_rank + 0.3×Granger_rank", "종합 순위 상위 선택", "C-03"),
            ("5단계", "도메인 전문가 검토",       "P1-01~04 정성 평가 + 상품 논리 검증", "합의 승인",            "P1-01~04"),
        ]
        hdr_var = "피처 코드"
        hdr_cat = "카테고리"
        hdr_ratio = "D-015 핵심 선정 근거"
        hdr_stat  = "Phase A 수집 상태"
        core_title = "Phase A 핵심 피처 8개 (D-015)"
        note_txt = (
            "피처 선택 기준은 AIC/BIC/F1-Score 단일 지표가 아닌, "
            "데이터 품질(DQSOps) → 통계적 유의성(Pearson/Granger) → 공선성 제거(VIF/LASSO) → "
            "ML 중요도(SHAP) → 도메인 검토(P1-01~04) 5단계 게이트를 순차 적용합니다. "
            "Phase A에서는 8개 핵심 피처를 우선 확보하며, G1/G2/G3 별 최종 피처 수는 "
            "G1=12~15개(SHAP 상위), G2=10~14개(시계열 CV), G3=6~10개(Markov 파시모니)로 목표합니다."
        )
        status_collected  = "✅ 수집 중"
        status_partial    = "⚠️ 일부 수집"
        status_missing    = "❌ 미구현"
    else:
        title    = "Feature Engineering & Selection Methodology"
        subtitle = "Decision D-014 (5-Stage Gate) · D-015 (Phase A Core 8 Features)"
        gate_hdr = ["Stage", "Gate Name", "Criteria / Tools", "Threshold", "Owner"]
        gate_rows = [
            ("Stage 1", "DQSOps Quality Gate",     "C-08 5-dimension weighted score",             "≥ 0.70 PASS",              "C-08"),
            ("Stage 2", "Univariate Screening",    "Pearson |r| · Granger causality test",        "|r|≥0.25, p<0.05 (Bonferroni)", "C-03/C-06"),
            ("Stage 3", "Multicollinearity Removal","VIF < 5 · LASSO L1 regularization",          "VIF threshold 5.0",        "C-03"),
            ("Stage 4", "ML Importance Ranking",   "0.4×LASSO_rank + 0.3×SHAP_rank + 0.3×Granger_rank", "Top-ranked selected", "C-03"),
            ("Stage 5", "Domain Expert Review",    "P1-01~04 qualitative review + commodity logic", "Consensus approval",      "P1-01~04"),
        ]
        hdr_var  = "Feature Code"
        hdr_cat  = "Category"
        hdr_ratio = "D-015 Core Selection Rationale"
        hdr_stat  = "Phase A Collection Status"
        core_title = "Phase A Core Features — 8 Selected (D-015)"
        note_txt = (
            "Feature selection does NOT rely on a single criterion (AIC/BIC/F1-Score). "
            "Instead, a sequential 5-stage gate is applied: "
            "data quality (DQSOps) → statistical significance (Pearson/Granger) → "
            "collinearity removal (VIF/LASSO) → ML importance (SHAP) → domain review (P1-01~04). "
            "Phase A targets 8 core features first. Final feature counts by model: "
            "G1=12–15 (SHAP top-N), G2=10–14 (time-series CV), G3=6–10 (Markov parsimony)."
        )
        status_collected  = "✅ Collecting"
        status_partial    = "⚠️ Partial"
        status_missing    = "❌ Not Implemented"

    # 게이트 테이블 HTML
    gate_rows_html = "".join(
        f"<tr><td style='font-weight:bold;color:#1565c0'>{r[0]}</td>"
        f"<td>{r[1]}</td><td style='font-size:11px'>{r[2]}</td>"
        f"<td style='color:#c62828;font-weight:bold'>{r[3]}</td>"
        f"<td style='font-size:11px'>{r[4]}</td></tr>"
        for r in gate_rows
    )
    gate_table = (
        f"<table class='tbl'><thead><tr>"
        + "".join(f"<th>{h}</th>" for h in gate_hdr)
        + f"</tr></thead><tbody>{gate_rows_html}</tbody></table>"
    )

    # Phase A 핵심 피처 8개 테이블
    core_features = [
        ("CBOT_SBO_FUTURES",          "상품가격",   "대두유 선물 가격 — G1/G2/G3 타깃 변수. 피어슨 r 최고.",          status_collected),
        ("CPO_SBO_SPREAD",            "상품가격",   "CPO-SBO 스프레드 — 대체재 전환 임계값(>$175/MT). 비선형 효과.",  status_missing),
        ("WASDE_SBO_STU",             "작황",       "WASDE 재고사용비율 — 공급 타이트니스 핵심. Granger p<0.01.",      status_partial),
        ("BDI",                       "해운",       "발틱건화물지수 z-score 90일 — 운임 충격 선행지표.",              status_partial),
        ("FX_BRL_USD",                "거시경제",   "헤알/달러 환율 — 브라질 수출 채산성 직결. 월간 Pearson r=0.42.", status_collected),
        ("ENSO_ONI",                  "기후",       "ENSO ONI — 남미 작황 선행 6~9개월. |ONI|≥0.5 경보.",           status_collected),
        ("PSD_SOY_CRUSH",             "작황",       "글로벌 대두 압착량 — SBO 공급의 직접 원료. USDA FAS PSD.",      status_partial),
        ("GATS_US_SBO_EXPORT_KOREA",  "수입통계",  "미국→한국 대두유 수출 — 한국 조달 비용 직접 지표. GATS 수동업로드.", status_partial),
    ] if lang == "ko" else [
        ("CBOT_SBO_FUTURES",          "Commodity",    "SBO futures — target variable for G1/G2/G3. Highest Pearson r.",       status_collected),
        ("CPO_SBO_SPREAD",            "Commodity",    "CPO-SBO spread — substitution threshold (>$175/MT). Nonlinear effect.", status_missing),
        ("WASDE_SBO_STU",             "Crop",         "WASDE stocks-to-use — supply tightness. Granger p<0.01.",              status_partial),
        ("BDI",                       "Shipping",     "BDI 90-day z-score — freight shock leading indicator.",                status_partial),
        ("FX_BRL_USD",                "Macro",        "BRL/USD — Brazil export profitability. Monthly Pearson r=0.42.",        status_collected),
        ("ENSO_ONI",                  "Climate",      "ONI — South America crop leading indicator (6-9 months). |ONI|≥0.5.",  status_collected),
        ("PSD_SOY_CRUSH",             "Crop",         "Global soybean crush — direct SBO feedstock. USDA FAS PSD.",           status_partial),
        ("GATS_US_SBO_EXPORT_KOREA",  "Trade Stats",  "US→Korea SBO export — direct Korean procurement cost indicator.",      status_partial),
    ]

    core_rows_html = "".join(
        f"<tr><td><code>{r[0]}</code></td><td>{r[1]}</td>"
        f"<td style='font-size:11px'>{r[2]}</td><td>{r[3]}</td></tr>"
        for r in core_features
    )
    core_table = (
        f"<table class='tbl'><thead><tr>"
        f"<th>{hdr_var}</th><th>{hdr_cat}</th><th>{hdr_ratio}</th><th>{hdr_stat}</th>"
        f"</tr></thead><tbody>{core_rows_html}</tbody></table>"
    )

    return f"""<h2 style="color:#283593">{title}</h2>
<div class="note" style="margin-bottom:10px">
  <strong>{subtitle}</strong><br>{note_txt}
</div>
{gate_table}
<h3 style="color:#3949ab;margin-top:18px">{core_title}</h3>
{core_table}"""


def _render_causal_chains(
    lang: str = "ko",
    extra_chains: list[dict[str, str]] | None = None,
) -> str:
    """대두유 가격에 영향을 주는 인과관계 체인을 HTML로 렌더링.

    extra_chains: 런타임에 추가할 체인 목록 (동일 스키마).
                  예: [{"driver_ko": "...", "driver_en": "...", "chain_ko": "...",
                         "chain_en": "...", "direction": "up/down",
                         "category_ko": "...", "category_en": "..."}]
    """
    all_chains = _CAUSAL_CHAINS + (extra_chains or [])

    # 카테고리별 그룹화
    by_cat: dict[str, list[dict]] = {}
    for c in all_chains:
        cat = c.get("category_ko" if lang == "ko" else "category_en", "기타")
        by_cat.setdefault(cat, []).append(c)

    title = "주요 가격 영향 인과관계" if lang == "ko" else "Key Causal Chains Affecting SBO Price"
    hdr_driver = "주요 동인" if lang == "ko" else "Driver"
    hdr_chain  = "인과관계 경로" if lang == "ko" else "Causal Chain"
    hdr_dir    = "가격 방향" if lang == "ko" else "Price Direction"

    sections_html = ""
    for cat, chains in by_cat.items():
        rows = ""
        for c in chains:
            driver = c["driver_ko"] if lang == "ko" else c["driver_en"]
            chain  = c["chain_ko"]  if lang == "ko" else c["chain_en"]
            arrow  = "▲ 상승" if c["direction"] == "up" else "▼ 하락"
            color  = "#c62828" if c["direction"] == "up" else "#1565c0"
            rows += (
                f"<tr>"
                f"<td style='font-weight:bold;white-space:nowrap'>{driver}</td>"
                f"<td style='font-size:12px'>{chain}</td>"
                f"<td style='color:{color};font-weight:bold;white-space:nowrap'>{arrow}</td>"
                f"</tr>"
            )
        sections_html += (
            f"<tr><td colspan='3' style='background:#e8eaf6;font-weight:bold;padding:4px 8px'>"
            f"{cat}</td></tr>{rows}"
        )

    note_txt = (
        "위 목록은 현재까지 식별된 주요 인과관계입니다. "
        "GPR·기후·무역 환경 변화에 따라 추가 동인이 지속적으로 갱신됩니다."
        if lang == "ko" else
        "The above represents identified causal chains to date. "
        "Additional drivers are continuously identified as GPR, climate, and trade dynamics evolve."
    )

    return f"""<h2>{title}</h2>
<table class="tbl"><thead>
<tr><th>{hdr_driver}</th><th>{hdr_chain}</th><th>{hdr_dir}</th></tr>
</thead><tbody>{sections_html}</tbody></table>
<div class="note" style="margin-top:6px;font-size:11px">{note_txt}</div>"""


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


_TOP5_SELECTION_CRITERIA: dict[str, dict[str, str]] = {
    "CBOT_SBO_FUTURES": {
        "criteria_ko": "피어슨 r 최고 · LASSO 비영 · Granger p<0.01 · D-015 확정",
        "criteria_en": "Highest Pearson r · LASSO non-zero · Granger p<0.01 · D-015 confirmed",
        "causal_ko":   "선물 가격 = 시장의 대두유 공급·수요 기대값 집약 → G1/G2/G3 공통 타깃",
        "causal_en":   "Futures = market's aggregated SBO supply/demand expectation → G1/G2/G3 shared target",
    },
    "CPO_SBO_SPREAD": {
        "criteria_ko": "대체재 임계값 >$175/MT · 비선형 전환 효과 · P1-01~04 도메인 승인",
        "criteria_en": "Substitute threshold >$175/MT · nonlinear switching effect · P1-01~04 approved",
        "causal_ko":   "CPO 가격 하락 → 대두유 수요 이탈(바이오디젤·식품업체) → SBO 가격 하락 압력",
        "causal_en":   "CPO price drop → SBO demand substitution (biodiesel/food) → SBO price downward pressure",
    },
    "WASDE_SBO_STU": {
        "criteria_ko": "Granger p<0.01 · USDA 발표 서프라이즈 효과 검증 · D-015 확정",
        "criteria_en": "Granger p<0.01 · USDA release surprise effect verified · D-015 confirmed",
        "causal_ko":   "WASDE STU < 10% → 공급 타이트니스 신호 → 투기 세력 순매수 → 선물 가격 급등",
        "causal_en":   "WASDE STU <10% → supply tightness signal → speculative long build → futures spike",
    },
    "BDI": {
        "criteria_ko": "90일 z-score 2σ 임계값 · 해운 비용 선행 3~6주 · D-015 확정",
        "criteria_en": "90-day z-score 2σ threshold · freight cost lead 3–6 weeks · D-015 confirmed",
        "causal_ko":   "BDI 급등 → 대두유 CFR 운임 상승 → 한국 수입 원가 직결",
        "causal_en":   "BDI spike → SBO CFR freight premium → Korean import cost direct impact",
    },
    "FX_BRL_USD": {
        "criteria_ko": "월간 피어슨 r=0.42 · 브라질 공급 선행 T+2 · D-015 확정",
        "criteria_en": "Monthly Pearson r=0.42 · Brazil supply lead T+2 · D-015 confirmed",
        "causal_ko":   "헤알 약세 → 브라질 수출 채산성 개선 → 미국 경쟁 심화 → 미국 SBO 가격 하락",
        "causal_en":   "BRL weakens → Brazil export profitability improves → US competition intensifies → US SBO price drops",
    },
    "ENSO_ONI": {
        "criteria_ko": "|ONI| ≥ 0.5 이벤트 선행 6~9개월 · 남미 작황 영향 Granger 유의",
        "criteria_en": "|ONI| ≥ 0.5 events lead 6–9 months · South America crop Granger significant",
        "causal_ko":   "라니냐 강화 → 브라질·아르헨티나 강수 편차 → 대두 수확 감소 → SBO 공급 위축",
        "causal_en":   "La Niña intensifies → Brazil/Argentina rainfall deficit → soy harvest loss → SBO supply contraction",
    },
    "PSD_SOY_CRUSH": {
        "criteria_ko": "SBO 공급 직접 원료 · USDA FAS PSD 연간 · D-015 확정",
        "criteria_en": "Direct SBO feedstock supply · USDA FAS PSD annual · D-015 confirmed",
        "causal_ko":   "압착량 감소 → 대두유 생산 감소 → 공급 부족 → SBO 가격 상승",
        "causal_en":   "Crush volume decline → SBO production decline → supply deficit → SBO price rise",
    },
    "GATS_US_SBO_EXPORT_KOREA": {
        "criteria_ko": "한국 직접 조달 비용 지표 · 미국 수출 물량 선행 1~2개월",
        "criteria_en": "Direct Korean procurement cost indicator · US export volume lead 1–2 months",
        "causal_ko":   "미국→한국 수출량 감소 → 조달 대안 탐색 → 한국 CIF 프리미엄 확대",
        "causal_en":   "US→Korea export volume drop → alternative sourcing needed → Korea CIF premium widens",
    },
}


def _build_current_values(frames: dict[str, pd.DataFrame]) -> dict[str, str]:
    """parquet 데이터에서 각 지표의 최신값을 추출. {indicator_code: 표시값} 반환."""
    result: dict[str, str] = {}
    for _df in frames.values():
        if "indicator_code" not in _df.columns or "value" not in _df.columns:
            continue
        date_col = "price_date" if "price_date" in _df.columns else None
        for code, grp in _df.groupby("indicator_code"):
            if date_col:
                grp = grp.sort_values(date_col)
            latest_val = pd.to_numeric(grp["value"].iloc[-1], errors="coerce")
            if pd.notna(latest_val):
                unit = grp["unit"].iloc[-1] if "unit" in grp.columns else ""
                result[str(code)] = f"{latest_val:,.4g} {unit}".strip()
    return result


def _render_top5_variables(
    importance_df: pd.DataFrame,
    current_values: dict[str, str],
    lang: str = "ko",
) -> str:
    """상위 5개 핵심 변수 카드 섹션 HTML 렌더링.

    importance_df에 LASSO 결과가 있으면 순위 기준, 없으면 D-015 Phase A 설계 순위 사용.
    """
    D015_ORDER = [
        "CBOT_SBO_FUTURES", "CPO_SBO_SPREAD", "WASDE_SBO_STU",
        "BDI", "FX_BRL_USD",
    ]

    if not importance_df.empty and "변수" in importance_df.columns:
        top_vars = importance_df.head(5)["변수"].tolist()
    else:
        top_vars = D015_ORDER

    if lang == "ko":
        section_title = "상위 5개 핵심 변수"
        note_text = (
            "LASSO 분석 결과 기준 상위 5개 변수. "
            "데이터 미수집 시 D-015 Phase A 설계 순위 표시. "
            "선택 기준: D-014 5단계 게이트(DQSOps → Pearson/Granger → VIF/LASSO → ML 순위 → 도메인 검토)."
        )
        col_rank  = "순위"
        col_var   = "변수 코드"
        col_crit  = "선택 기준"
        col_val   = "최근값"
        col_chain = "인과 메커니즘"
        no_data   = "수집 중"
    else:
        section_title = "Top 5 Key Variables"
        note_text = (
            "Top 5 variables by LASSO ranking. "
            "Falls back to D-015 Phase A design order if no data collected. "
            "Selection criteria: D-014 5-stage gate (DQSOps → Pearson/Granger → VIF/LASSO → ML rank → domain review)."
        )
        col_rank  = "Rank"
        col_var   = "Variable Code"
        col_crit  = "Selection Criteria"
        col_val   = "Latest Value"
        col_chain = "Causal Mechanism"
        no_data   = "Collecting"

    rows_html = ""
    for i, var_code in enumerate(top_vars, 1):
        meta   = _TOP5_SELECTION_CRITERIA.get(var_code, {})
        crit   = meta.get("criteria_ko" if lang == "ko" else "criteria_en", "—")
        chain  = meta.get("causal_ko"   if lang == "ko" else "causal_en",   "—")
        val    = current_values.get(var_code, f"⚠ {no_data}")
        rank_color = "#c62828" if i <= 3 else "#1565c0"
        rows_html += (
            f"<tr>"
            f"<td style='font-weight:bold;color:{rank_color};text-align:center'>{i}</td>"
            f"<td><code style='font-size:12px'>{var_code}</code></td>"
            f"<td style='font-size:11px'>{crit}</td>"
            f"<td style='font-size:12px;font-weight:bold'>{val}</td>"
            f"<td style='font-size:11px'>{chain}</td>"
            f"</tr>"
        )

    return f"""<h2 style="color:#283593">{section_title}</h2>
<div class="note" style="margin-bottom:10px">{note_text}</div>
<table class="tbl">
<thead><tr>
  <th style="width:40px">{col_rank}</th>
  <th style="width:200px">{col_var}</th>
  <th>{col_crit}</th>
  <th style="width:120px">{col_val}</th>
  <th>{col_chain}</th>
</tr></thead>
<tbody>{rows_html}</tbody>
</table>"""


def _render_html(
    status_df: pd.DataFrame,
    importance_df: pd.DataFrame,
    alerts: list[dict],
    run_id: str,
    run_ts: str,
    days: int,
    data_period: str = "",
    lang: Literal["ko", "en"] = "ko",
    granger_conditions: pd.DataFrame | None = None,
    granger_results: pd.DataFrame | None = None,
    current_values: dict[str, str] | None = None,
) -> str:
    """G1 분석 보고서 HTML 렌더링 (한국어 + 영어 이중언어)."""
    font_import = (
        "@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');"
        if lang == "ko" else ""
    )
    # weasyprint(PDF)는 @import 웹폰트를 오프라인 CI에서 받지 못함 → 시스템 설치 폰트명을
    # 1순위로 둬야 한국어 글리프가 '?'로 깨지지 않음. apt fonts-noto-cjk = 'Noto Sans CJK KR'.
    # (A-056: 'Noto Sans KR'는 웹폰트명이라 CI 미설치 → 폴백 실패 → notdef '?' 발생)
    font_family = (
        "'Noto Sans CJK KR', 'Noto Sans KR', 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif"
        if lang == "ko" else
        "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
    )
    title  = "대두유 가격 핵심 영향 인자 분석 보고서" if lang == "ko" else "Key Variable Analysis Report"
    sub    = f"{data_period} 데이터 기준" if (lang == "ko" and data_period) else (f"Based on {data_period} data" if data_period else (f"최근 {days}일 데이터 기준" if lang == "ko" else f"Based on last {days} days"))

    # executive summary
    category_summary = _build_category_summary(importance_df, {})
    exec_html = _render_executive_summary(alerts, category_summary, run_ts, lang)

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

    # feature engineering & selection methodology
    feature_selection_html = _render_feature_selection_methodology(lang=lang)

    # top 5 variables
    top5_html = _render_top5_variables(importance_df, current_values or {}, lang=lang)

    # causal chains
    causal_chains_html = _render_causal_chains(lang=lang)

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
    thr_title = "구조적 단절 임계값 산출 근거" if lang == "ko" else "Structural Break Threshold Rationale"
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

    # Granger 인과검정 조건 섹션
    gc_title = "Granger 인과검정 선결 조건 분류 (변수별)" if lang == "ko" else "Granger Causality — Pre-Condition Check (per Variable)"
    gc_note  = (
        "조건 미충족 변수는 Granger 검정에서 제외됩니다. "
        "⚠️ 관측치 부족: 커넥터 수집 후 재실행 필요. "
        "⚠️ 비정상: 추가 차분 또는 공적분 검정 필요."
        if lang == "ko" else
        "Variables failing conditions are excluded from Granger tests. "
        "⚠️ Insufficient obs: re-run after data accumulation. "
        "⚠️ Non-stationary: requires higher-order differencing or cointegration test."
    )
    if granger_conditions is not None and not granger_conditions.empty:
        gc_display = granger_conditions.drop(columns=[c for c in ["_ready", "_needs_diff"] if c in granger_conditions.columns])
        gc_html    = gc_display.to_html(index=False, border=0, classes="tbl")
    else:
        gc_html = (
            "<p>Granger 조건 점검 미실행 — 수집된 parquet 데이터 없음. 커넥터 재실행 후 확인하세요.</p>"
            if lang == "ko" else
            "<p>Granger condition check not run — no parquet data available. Re-run connectors first.</p>"
        )
    granger_conditions_section = f"""<h2>{gc_title}</h2>
<div class="note" style="margin-bottom:8px">{gc_note}</div>
{gc_html}"""

    # Granger 인과검정 결과 섹션
    gr_title = f"Granger 인과검정 결과 — 연도별 (α={GRANGER_ALPHA})" if lang == "ko" else f"Granger Causality Results — By Year (α={GRANGER_ALPHA})"
    gr_note  = (
        f"귀무가설: X는 Y(대두유 가격)의 Granger 원인이 아니다. p < {GRANGER_ALPHA} → 귀무가설 기각 = 인과관계 있음. "
        "방향: X → Y (X의 과거값이 Y 예측에 추가 정보를 제공). 최적시차: 최소 p-값을 가진 시차."
        if lang == "ko" else
        f"H0: X does not Granger-cause Y (soybean oil price). p < {GRANGER_ALPHA} → reject H0 = causal. "
        "Direction: X → Y (past values of X improve Y forecast). Best lag: lag with minimum p-value."
    )
    if granger_results is not None and not granger_results.empty:
        gr_html = granger_results.to_html(index=False, border=0, classes="tbl")
    else:
        gr_html = (
            "<p>Granger 검정 미실행 — 선결 조건 충족 변수 없음. 수집 기간 2017~작년 데이터 누적 후 재실행하세요.</p>"
            if lang == "ko" else
            "<p>Granger test not run — no variables met pre-conditions. Accumulate data from 2017 to last year and re-run.</p>"
        )
    granger_results_section = f"""<h2>{gr_title}</h2>
<div class="note" style="margin-bottom:8px">{gr_note}</div>
{gr_html}"""

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
  .kpi-row {{ display: flex; gap: 16px; margin: 16px 0; }}
  .kpi-card {{ flex: 1; background: #e3f2fd; border-radius: 10px; padding: 14px 18px; text-align: center; }}
  .kpi-num {{ font-size: 28px; font-weight: bold; color: #1565c0; }}
  .kpi-lbl {{ font-size: 11px; color: #546e7a; margin-top: 4px; }}
  .signal-green {{ background: #e8f5e9; border-left: 6px solid #2e7d32; padding: 12px 18px; border-radius: 6px; margin: 16px 0; font-size: 14px; font-weight: bold; }}
  .signal-amber {{ background: #fff8e1; border-left: 6px solid #f57f17; padding: 12px 18px; border-radius: 6px; margin: 16px 0; font-size: 14px; font-weight: bold; }}
  .signal-red {{ background: #ffebee; border-left: 6px solid #c62828; padding: 12px 18px; border-radius: 6px; margin: 16px 0; font-size: 14px; font-weight: bold; }}
</style>
</head>
<body>
<h1>{title}<br><small style="font-size:14px;color:#5c6bc0">{sub}</small></h1>

<div class="meta">
  <strong>{'생성 시각 (UTC)' if lang == 'ko' else 'Generated (UTC)'}:</strong> {run_ts} &nbsp;│&nbsp;
  <strong>{'활용 데이터 양' if lang == 'ko' else 'Data Range'}:</strong> {data_period if data_period else (f"{'최근' if lang == 'ko' else 'Last'} {days}{'일' if lang == 'ko' else ' days'}") }
</div>

<div class="note">
  <strong>Phase A 분석 구성:</strong>
  기술통계·LASSO 상관분석·Granger 인과검정(2017~작년 연도별) 수행.
  XGBoost+SHAP, TCN-XGBoost 하이브리드는 Phase B(Snowflake 연동 후) 적용 예정.
</div>

{exec_html}

<h2>{'활용 데이터' if lang == 'ko' else 'Data Collection Status'}</h2>
{status_html}

<h2>{'변수 중요도 (LASSO 기반)' if lang == 'ko' else 'Variable Importance (LASSO-based)'}</h2>
{imp_html}

{feature_selection_html}

{top5_html}

<h2>{lasso_title}</h2>
{lasso_html}

<h2>{'구조적 단절 임계값 현황' if lang == 'ko' else 'Structural Break Status'}</h2>
{alerts_html}

<div class="note">
  임계값 정의 (C-03): GPR &gt; 0.022 (지정학) · BDI z &gt; 2σ (해운) · WASDE STU &lt; 10% (공급) · CPO-SBO spread &gt; $175/MT (대체)
</div>

<h2>{thr_title}</h2>
{threshold_rationale_html}

<h2>{catalog_title}</h2>
<div class="note" style="margin-bottom:8px">{catalog_note}</div>
{catalog_html}

{granger_conditions_section}

{granger_results_section}

{causal_chains_html}

<div class="footer">
  Project Nexus · 대두유 가격 핵심 영향 인자 분석 보고서 · Branch: claude/setup-nexus-llm-tools-RX4aS · {run_ts} UTC
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

    status_df     = _build_data_status(frames)

    # 실제 수집 데이터 범위 계산
    _all_dates = []
    for _df in frames.values():
        if "price_date" in _df.columns:
            _dates = pd.to_datetime(_df["price_date"], errors="coerce").dropna()
            if len(_dates) > 0:
                _all_dates.extend([_dates.min(), _dates.max()])
    if _all_dates:
        _start_yr = min(_all_dates).year
        _end_yr   = max(_all_dates).year
        data_period = f"{_start_yr}~{_end_yr}년"
    else:
        _sy = os.environ.get("HISTORICAL_START_YEAR", "2017")
        _ey = os.environ.get("HISTORICAL_END_YEAR", "2025")
        data_period = f"{_sy}~{_ey}년"

    wide          = _pivot_for_correlation(frames)
    importance_df = _lasso_importance(wide)
    alerts        = _check_structural_breaks(frames)

    print(f"[C-03] 상관 분석 변수 수: {wide.shape[1] if not wide.empty else 0}")
    print(f"[C-03] 구조적 단절 임계값 초과: {sum(1 for a in alerts if '🚨' in a.get('상태', ''))}/{len(alerts)}")

    # ── Granger 인과검정: 전체 히스토리 parquet 사용 (2020~작년) ──────────────────
    print("[C-03] Granger 인과검정 선결 조건 점검 중 (2017~작년 연도별)...")
    hist_frames = _load_all_parquets(days=2000)   # 보관된 전체 parquet 로드
    hist_wide   = _pivot_for_correlation(hist_frames)
    granger_target = next(
        (c for c in ["CBOT_BO_CLOSE", "BRENT_USD_BBL", "CPO_USD_MT"]
         if not hist_wide.empty and c in hist_wide.columns),
        None,
    )
    if granger_target and not hist_wide.empty:
        print(f"[C-03] Granger 타깃: {granger_target}")
        granger_conditions = _check_granger_conditions(hist_wide, granger_target)
        granger_results    = _granger_causality_by_year(hist_wide, granger_target, granger_conditions)
        n_ready  = granger_conditions["_ready"].sum() if not granger_conditions.empty else 0
        n_causal = (granger_results["인과성"] == "✅ 인과관계 있음").sum() if not granger_results.empty else 0
        print(f"[C-03] Granger 조건 충족: {n_ready}개 변수 / 유의 인과관계: {n_causal}건 (α={GRANGER_ALPHA})")
    else:
        granger_conditions = pd.DataFrame()
        granger_results    = pd.DataFrame()
        print("[C-03] Granger 건너뜀 — 타깃 변수(CBOT_BO_CLOSE / BRENT_USD_BBL) 없음")

    current_values = _build_current_values(frames)
    print(f"[C-03] 최신값 추출 완료: {len(current_values)}개 지표")

    for lang in ("ko", "en"):
        html_path = f"{REPORT_DIR}/g1_variable_importance_{tag}_{lang}.html"
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(_render_html(
                status_df, importance_df, alerts, run_id, run_ts, days,
                data_period=data_period,
                lang=lang,  # type: ignore[arg-type]
                granger_conditions=granger_conditions,
                granger_results=granger_results,
                current_values=current_values,
            ))
        print(f"[완료] G1 리포트 ({lang.upper()}) → {html_path}")

        # HTML → PDF 변환 (weasyprint 설치 시)
        pdf_path = f"{REPORT_DIR}/g1_variable_importance_{tag}_{lang}.pdf"
        try:
            from weasyprint import HTML as WeasyprintHTML  # type: ignore
            WeasyprintHTML(filename=html_path).write_pdf(pdf_path)
            print(f"[완료] G1 PDF ({lang.upper()}) → {pdf_path}")
        except ImportError:
            print(f"[정보] weasyprint 미설치 — PDF 건너뜀 ({lang.upper()})")
        except Exception as e:
            print(f"[경고] G1 PDF 변환 실패 ({lang.upper()}): {e}")

    # Markdown 요약 (기계 판독용 + generate_research_pdf.py 입력)
    breach = [a for a in alerts if "🚨" in a.get("상태", "")]
    md_lines = [
        f"# 대두유 가격 핵심 영향 인자 분석 보고서 — {run_ts[:10]}",
        f"**활용 데이터 양**: {data_period if data_period else f'최근 {days}일'}  |  **생성**: {run_ts} UTC",
        "",
        "## 구조적 단절 임계값 현황",
    ]
    if breach:
        for a in alerts:
            icon = "🚨" if "🚨" in a.get("상태", "") else "✅"
            md_lines.append(f"- {icon} **{a['변수']}**: {a['현재값']} (임계값 {a['임계값']}) — {a['설명']}")
    else:
        md_lines.append("- ✅ 모든 구조적 단절 임계값 정상 범위 내")
    md_lines += [
        "",
        "## 변수 중요도 TOP 10",
        "| 변수 | 피어슨 r | LASSO 계수 |",
        "|---|---|---|",
    ]
    if not importance_df.empty:
        top10 = importance_df.head(10)
        for _, row in top10.iterrows():
            r_val = f"{row.get('피어슨_r', 'N/A'):.3f}" if isinstance(row.get('피어슨_r'), float) else "N/A"
            lasso = f"{row.get('LASSO_계수', 'N/A'):.4f}" if isinstance(row.get('LASSO_계수'), float) else "N/A"
            md_lines.append(f"| {row.get('변수', '?')} | {r_val} | {lasso} |")
    md_lines += [
        "",
        "## 활용 데이터",
        "| 커넥터 | 변수항목 | 행수 | 날짜범위 | 무결성 | 신선도 |",
        "|---|---|---|---|---|---|",
    ]
    if not status_df.empty:
        for _, row in status_df.iterrows():
            md_lines.append(
                f"| {row.get('커넥터', '?')} | {row.get('변수항목', '?')} | "
                f"{row.get('행수', '?')} | {row.get('날짜범위', '?')} | "
                f"{row.get('무결성', '?')} | {row.get('신선도', '?')} |"
            )
    md_lines += [
        "",
        "---",
        "*Project Nexus · 핵심 변수 분석 보고서*",
        f"*HITL 게이트: 조달 결정은 CLAUDE.md §6 HITL 프로세스 필요*",
    ]
    md_path = f"{REPORT_DIR}/g1_variable_importance_{tag}_ko.md"
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md_lines))
    print(f"[완료] G1 Markdown 요약 → {md_path}")

    # 구조적 단절 경보 콘솔 출력
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
