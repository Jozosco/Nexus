# Feature Engineering & Selection Framework — Project Nexus
**작성일**: 2026-06-17  
**참여**: C-01 · C-03 · C-05 · C-06 · C-08 · P1-01 · P1-02 · P1-03 · P1-04  
**결정 ID**: D-014 (Feature Selection 기준), D-015 (최종 피처 집합)  
**참조**: CLAUDE.md §4 modeling.md, MEMORY D-006, D-013

---

## 1. 논의 배경

**C-01 (시스템 아키텍트):**  
G1·G2·G3 세 목표 모두 공통 피처 풀(pool)을 공유하지만, 각 목표마다 선택 기준의 무게가 다릅니다. G1은 인과성·해석성, G2는 예측력·공변량 커버리지, G3는 파시모니(parsimony)와 regime 구분력이 핵심입니다.  
결론적으로 **단일 선택 파이프라인**을 만들되, 목표별 후처리 단계에서 서로 다른 임계값을 적용하는 방식을 권장합니다.

**P1-01 (대두유 시장 전문가):**  
커머디티 트레이딩 경험상 가장 중요한 변수는 ① CBOT SBO 선물 가격, ② CPO-SBO 스프레드, ③ WASDE STU(재고사용비율), ④ BDI(운임지수)입니다. 나머지는 이 네 변수의 설명 보조입니다.

**P1-02 (거시경제 전문가):**  
FX(BRL/USD, CNY/USD)와 ENSO ONI는 6–18개월 선행 지표로서 구조적 단절 감지에 필수입니다. Granger 인과 검정 없이 단순 상관만으로 포함하면 허위 인과(spurious causality) 위험이 큽니다.

**P1-03 (지정학 리스크 전문가):**  
GPR 지수와 호르무즈 위협 레벨은 단기 충격(spike) 변수입니다. 연속형 예측에는 기여가 낮을 수 있으나, G3 regime 전환 탐지에서는 중요한 dummy 역할을 합니다.

**P1-04 (물류·공급망 전문가):**  
BDI 외에 미국 → 한국 수출량(GATS_US_SBO_EXPORT_KOREA)은 국내 조달 선행 지표입니다. 수출 계약 체결 후 약 T+45일 선행성이 있습니다.

---

## 2. 피처 선택 기준 (5단계 게이트)

```
단계 1: 데이터 품질 게이트 (C-08 DQSOps)
단계 2: 단변량 통계 스크리닝
단계 3: 다중공선성 제거
단계 4: ML 기반 중요도 순위
단계 5: 도메인 지식 최종 검토 (P1-01~04)
```

### 2.1 단계 1 — DQSOps 품질 게이트 (C-08)

**C-08 (데이터 품질 오퍼레이션):**  
모든 피처 후보는 DQSOps 5차원 점수 **≥ 0.70**을 충족해야 합니다. 이하 점수를 받은 변수는 모델 진입 불가.

| 차원 | 가중치 | 임계값 |
|---|---|---|
| 정확도 (Accuracy) | 0.30 | ≥ 0.70 |
| 완전성 (Completeness) | 0.25 | 결측률 ≤ 15% |
| 일관성 (Consistency) | 0.20 | 단위·스케일 표준화 확인 |
| 적시성 (Timeliness) | 0.15 | 수집 주기 준수 |
| 왜도 (Skewness) | 0.10 | |Skew| ≤ 3.0 (or log 변환 후) |

추가 요건:
- BACKFILL_MODE=true 시 실시간 전용 변수(AIS, Perplexity) 제외
- 2017–현재 연속성 검증 (결측 구간 > 3개월 연속 → 경고 플래그)

### 2.2 단계 2 — 단변량 스크리닝

**C-05 (ML/예측 모델링):**  
```python
# 기준 1: Pearson 상관계수 |r| ≥ 0.25 (CBOT SBO 가격 대비, 60일 이동평균 기준)
# 기준 2: Granger 인과 검정 p-value < 0.05 (lag 1~6개월, AIC 최적 lag 선택)
# 기준 3: 단변량 XGBoost 기여도 (permutation importance) > 임계값
```

Granger 검정 구현:
```python
from statsmodels.tsa.stattools import grangercausalitytests
# 사전 조건: ADF 단위근 검정으로 정상성 확인 → 차분 적용
# 최대 시차: 12개월 (연간 계절성 커버)
# 유의 수준: α = 0.05, Bonferroni 보정 적용 (30개 후보 → α* = 0.05/30 ≈ 0.0017)
```

### 2.3 단계 3 — 다중공선성 제거

```python
# VIF (Variance Inflation Factor) 임계값: VIF < 5
from statsmodels.stats.outliers_influence import variance_inflation_factor

# VIF ≥ 5인 쌍에서 Granger p-value가 더 큰 변수 제거
# LASSO를 보조 수단으로 사용 (λ는 5-fold time-series CV로 선택)
from sklearn.linear_model import LassoCV
```

### 2.4 단계 4 — ML 기반 중요도 순위

**C-05:**  
LASSO + XGBoost + SHAP 3중 검증:

```
LASSO L1 정규화:
  - 계수 ≠ 0 → 후보 통과
  - λ: 5-fold TimeSeriesSplit CV

XGBoost Feature Importance:
  - MDI (Mean Decrease in Impurity) 순위
  - 동시에 SHAP value (mean |SHAP|) 산출

최종 중요도 점수 = 0.4 × LASSO_rank + 0.3 × SHAP_rank + 0.3 × Granger_rank
(순위 역수의 가중 평균)
```

### 2.5 단계 5 — 도메인 검토 (P1-01~04)

- P1-01 최종 승인: 시장 논리와 일치 여부
- P1-02 검토: 거시 인과 구조 일관성
- P1-03 검토: 지정학 변수 포함 여부 적절성
- P1-04 검토: 물류 선행성 확인

---

## 3. 최종 피처 집합 (D-015)

### 3.1 피처 풀 전체 목록 (30개 후보)

| # | 변수 코드 | 설명 | 주기 | 출처 |
|---|---|---|---|---|
| 1 | CBOT_SBO_FUTURES | CBOT 대두유 선물 (BO=F) | 일별 | yfinance |
| 2 | CPO_PROXY_FCPOC1 | 팜유 선물 (Bursa FCPOc1) | 일별 | stooq/FRED |
| 3 | CPO_SBO_SPREAD | CPO-SBO 스프레드 (파생) | 일별 | 파생 |
| 4 | BDI | 발틱 운임지수 | 일별 | Baltic/stooq |
| 5 | FX_BRL_USD | 브라질 헤알/달러 | 일별 | FRED |
| 6 | FX_CNY_USD | 위안/달러 | 일별 | FRED |
| 7 | ENSO_ONI | 엘니뇨 ONI 지수 | 월별 | NOAA CPC |
| 8 | GPR_INDEX | 지정학적 리스크 지수 | 월별 | Caldara-Iacoviello |
| 9 | WASDE_SBO_PRODUCTION | WASDE 대두유 생산량 | 월별 | USDA WASDE |
| 10 | WASDE_SBO_ENDING_STOCKS | WASDE 대두유 기말재고 | 월별 | USDA WASDE |
| 11 | WASDE_SBO_STU | WASDE 재고사용비율 (파생) | 월별 | 파생 |
| 12 | WASDE_SOY_PRODUCTION | WASDE 대두 생산량 | 월별 | USDA WASDE |
| 13 | PSD_SBO_EXPORTS | PS&D 대두유 수출량 | 연간/분기 | USDA FAS |
| 14 | PSD_SBO_ENDING_STOCKS | PS&D 대두유 기말재고 | 연간/분기 | USDA FAS |
| 15 | PSD_SBO_STU | PS&D 재고사용비율 (파생) | 연간/분기 | 파생 |
| 16 | PSD_SOY_CRUSH | PS&D 대두 압착량 | 연간/분기 | USDA FAS |
| 17 | PSD_SBM_PRODUCTION | PS&D 대두박 생산량 | 연간/분기 | USDA FAS |
| 18 | GATS_US_SBO_EXPORT_TOTAL | 미국 대두유 총수출량 | 월별 | USDA GATS |
| 19 | GATS_US_SBO_EXPORT_KOREA | 미국→한국 수출량 | 월별 | USDA GATS |
| 20 | GATS_US_SBO_EXPORT_CHINA | 미국→중국 수출량 | 월별 | USDA GATS |
| 21 | GATS_US_SBO_REEXPORT_TOTAL | 미국 대두유 재수출 | 월별 | USDA GATS |
| 22 | SBO_CRUSH_MARGIN | 압착 마진 = SBO + SBM - SOY (파생) | 월별 | 파생 |
| 23 | CFTC_COT_NET | CFTC Commitments of Traders (net long) | 주별 | CFTC |
| 24 | FAO_AMIS_VEGEOIL_PRICE | FAO AMIS 식물성유지 가격지수 | 월별 | FAO AMIS PDF |
| 25 | FAO_AMIS_VEGEOIL_STOCKS | FAO AMIS 식물성유지 재고 | 월별 | FAO AMIS PDF |
| 26 | BRAZIL_SOYBEAN_EXPORT_PACE | 브라질 대두 수출 속도 (월누적) | 월별 | ANEC/SECEX |
| 27 | HORMUZ_THREAT_LEVEL | 호르무즈 위협 레벨 (0–3) | 일별 | AIS proxy |
| 28 | GEOINTEL_RISK_COMPOSITE | GeoIntel 복합 리스크 | 일별 | USGS/NOAA/GDELT |
| 29 | INDIA_IMPORT_DUTY | 인도 수입 관세 (변경 이벤트) | 이벤트 | 뉴스/USDA |
| 30 | EU_BIODIESEL_MANDATE | EU 바이오디젤 정책 레벨 | 분기 | EC 정책 |

### 3.2 목표별 최종 선택 피처 수

**P1-01 의견:** 너무 많은 피처는 GARCH/LSTM 모델에서 과적합 위험. G2에서 15개 초과는 위험.

**C-05 결론:**

| 목표 | 선택 피처 수 | 근거 |
|---|---|---|
| **G1 (변수 중요도)** | 30개 전체 분석 → 상위 **12–15개** 보고 | SHAP bar chart 기준 |
| **G2 (가격밴드 예측)** | **10–14개** | TimeSeriesSplit 5-fold CV 최적화 |
| **G3 (레짐 감지)** | **6–10개** | Markov 모델 파시모니, 과적합 방지 |

### 3.3 Phase A 즉시 적용 확정 피처 (8개 핵심)

**C-01 최종 결론:** Phase A에서 DQSOps PASS 보장 가능한 핵심 8개:

| 순위 | 코드 | 선택 근거 |
|---|---|---|
| 1 | CBOT_SBO_FUTURES | 목표 변수와 동일 계열. 선물 커브 활용 |
| 2 | CPO_SBO_SPREAD | 대체재 가격 차이. SBO 가격 수렴 트리거 |
| 3 | WASDE_SBO_STU | 재고사용비율 → SBO 가격의 가장 강력한 기본적 동인 |
| 4 | BDI | 운임 → CIF 가격 직접 반영 (T+2~3주 선행) |
| 5 | FX_BRL_USD | 브라질 공급 비용 → 글로벌 SBO 원가 |
| 6 | ENSO_ONI | 기후 선행 지표 (6–18개월). 작황 예측 |
| 7 | PSD_SOY_CRUSH | 압착량 → SBO 공급 결정 요인 |
| 8 | GATS_US_SBO_EXPORT_KOREA | 국내 수요 선행 지표 (T+45일) |

### 3.4 Phase B 추가 후보 (데이터 확보 후)

| 코드 | 비고 |
|---|---|
| CFTC_COT_NET | CFTC API 미구현 (WBS 추가 필요) |
| SBO_CRUSH_MARGIN | PSD SBM 데이터 품질 확인 후 |
| BRAZIL_SOYBEAN_EXPORT_PACE | ANEC/SECEX API 연동 필요 |
| FAO_AMIS_VEGEOIL_PRICE | PDF 추출 파이프라인 완성 후 (→ scripts/ingest_fao_amis_pdf.py) |
| INDIA_IMPORT_DUTY | 이벤트 인코딩 방식 결정 필요 |
| EU_BIODIESEL_MANDATE | 분기 데이터 → 보간 로직 필요 |

---

## 4. 피처 엔지니어링 규칙

### 4.1 시계열 전처리 표준

```python
# 1. 로그 변환 (가격·물량 계열)
df['CBOT_LOG'] = np.log(df['CBOT_SBO_FUTURES'])

# 2. 1차 차분 (정상성 확보)
df['CBOT_DIFF'] = df['CBOT_LOG'].diff(1)

# 3. 이상치 캡핑 (IQR 방법) — MEMORY M-003 적용
Q1, Q3 = df[col].quantile([0.25, 0.75])
IQR = Q3 - Q1
df[col] = df[col].clip(Q1 - 1.5*IQR, Q3 + 1.5*IQR)

# 4. 이동평균 (노이즈 제거): 7일, 30일, 90일
for w in [7, 30, 90]:
    df[f'{col}_MA{w}'] = df[col].rolling(w).mean()

# 5. FX T+2 오프셋 — MEMORY M-002 필수 적용
df['FX_BRL_USD_T2'] = df['FX_BRL_USD'].shift(2)
```

### 4.2 파생 변수 계산

```python
# CPO-SBO 스프레드
df['CPO_SBO_SPREAD'] = df['CPO_PROXY_FCPOC1'] - df['CBOT_SBO_FUTURES']

# 재고사용비율 (WASDE 기반)
df['WASDE_SBO_STU'] = (df['WASDE_SBO_ENDING_STOCKS'] / df['WASDE_SBO_TOTAL_USE']) * 100

# 압착 마진 근사 (단위 통일 필수: 1,000MT 기준)
# SBO 가격($/MT) × 압착량 + SBM 가격($/MT) × 압착량 - SOY 가격($/MT) × 원두량
# Phase B 구현 예정
```

### 4.3 주기 정렬 (Frequency Alignment)

월별/연간 데이터를 일별로 정렬 시:

```python
# 방법: forward fill (발표 시점부터 다음 발표 직전까지 동일값 유지)
# WASDE: 매월 10~12일 발표 → 발표일 이후 forward fill
df_monthly = df_monthly.resample('D').ffill()

# FX T+2 오프셋 후 일별로 재정렬
```

---

## 5. 구현 계획

| 단계 | 파일 | 담당 | 상태 |
|---|---|---|---|
| 피처 품질 게이트 | `src/pipeline/feature_quality_gate.py` | C-08 | 미구현 |
| Granger 검정 모듈 | `src/forecasting/variable_importance_g1.py` | C-05 | 구현됨 (2017~) |
| LASSO 피처 선택 | `src/forecasting/feature_selector.py` | C-05 | 미구현 |
| SHAP 중요도 출력 | `src/forecasting/variable_importance_g1.py` | C-05 | 구현됨 |
| 피처 스토어 스키마 | `data/schemas/feature_store.yaml` | C-01 | 미구현 |
| CPO 피처 추가 | `src/pipeline/connectors/commodity_connector.py` | C-03 | 부분 구현 |
| FAO AMIS 추출 | `scripts/ingest_fao_amis_pdf.py` | C-04 | 미구현 |

---

## 6. 결론 요약 (C-01)

**결정 D-014:** Feature Selection 5단계 게이트 확정  
(DQSOps 품질 → 단변량 스크리닝 → VIF 제거 → LASSO+SHAP 순위 → 도메인 검토)

**결정 D-015:** Phase A 핵심 피처 8개 확정  
CBOT_SBO_FUTURES, CPO_SBO_SPREAD, WASDE_SBO_STU, BDI, FX_BRL_USD, ENSO_ONI, PSD_SOY_CRUSH, GATS_US_SBO_EXPORT_KOREA

**피처 수 기준:**
- G1: 30개 후보 → 12–15개 (SHAP 보고)
- G2: 10–14개 (CV 최적화)
- G3: 6–10개 (Markov 파시모니)

**다음 액션:**
1. `src/pipeline/feature_quality_gate.py` 구현 (WBS 1.1.8 연계)
2. `data/schemas/feature_store.yaml` 스키마 정의
3. CPO FCPOc1 피처 `commodity_connector.py`에 추가
4. FAO AMIS PDF → 피처 파이프라인 구축

*결정 기록 → MEMORY.md D-014, D-015로 갱신 예정*
