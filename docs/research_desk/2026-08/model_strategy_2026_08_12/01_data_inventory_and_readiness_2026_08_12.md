# Project Nexus 데이터 인벤토리·모델 준비도

작성일: 2026-08-12  
기준 브랜치: `main`

## 1. 저장소 데이터 스냅샷

GitHub recursive tree와 `data/raw/INDEX.md`를 교차확인한 결과다.

| 원천 | 파일 수 | 용량 | PDF | MD | XLSX | CSV | 주요 내용 |
|---|---:|---:|---:|---:|---:|---:|---|
| USDA | 4,333 | 1.313GB | 2,090 | 2,095 | 117 | 24 | GAIN Oilseeds/Biofuels, GATS, PSD, WASDE |
| FAO | 276 | 310.7MB | 137 | 138 | 0 | 0 | AMIS Market Monitor 및 요약 |
| 관세청 | 128 | 3.15MB | 0 | 2 | 120 | 0 | HS 1507 및 대체·보완 유지류 수입통계 |
| ICE | 55 | 6.41MB | 3 | 1 | 51 | 0 | 미국·EU 선물·옵션 거래량 |
| Trading Economics | 27 | 5.88MB | 0 | 1 | 26 | 0 | 상품·에너지·운임 시계열 |
| NASA POWER | 13 | 0.49MB | 0 | 1 | 12 | 0 | 주요 생산지역 기후자료 |
| 기타 | 5 | 13.15MB | 1 | 2 | 1 | 0 | KOSIS 가이드, 용어사전, 인덱스 |
| **합계** | **4,837** | **1.653GB** | **2,231** | **2,240** | **327** | **24** | — |

큰 하위 코퍼스:

- `USDA/FAS/GAIN/Oilseeds`: 3,159개 파일
- `USDA/FAS/GAIN/Biofuels`: 1,023개 파일
- `USDA/FAS/GATS/Oilseeds`: 122개 파일
- `FAO/AMIS`: 2012~2026 월간 보고서·요약
- 관세청: 대두유 HS 1507.10/1507.90 및 팜유·유채유·해바라기유·바이오디젤·대두·대두박

## 2. 처리 데이터·코드 준비도

| 영역 | 현재 GitHub 추적 상태 | 판단 |
|---|---|---|
| `data/processed` | 비정형 인덱스 CSV 2개, 약 0.9MB | 모델 입력 통합 테이블 부재 |
| `data/schemas` | 8개 YAML | 기본 계약 존재, release/vintage 필드 보강 필요 |
| `src/forecasting` | Python 3개 | G1·GPR 상관 기본 구현만 존재 |
| `src/risk` | 파일 없음 | G3 레짐·의사결정 미구현 |
| `notebooks` | 파일 없음 | 재현 가능한 EDA·모델 비교 노트북 부재 |
| 모델 입력 parquet | 코드·문서에서는 기대하지만 현재 GitHub tree에서 확인되지 않음 | 생성·보관 위치와 데이터 자산 버전 확정 필요 |

세션 문서에는 TE 34,118행, BDI 2,392행, ICE 5,332행, WASDE 1,554행, PSD 90행, GATS 80행의 생성 기록이 있다. 그러나 현재 저장소에 해당 통합 parquet가 보이지 않으므로 **문서상 완료와 재현 가능한 모델 입력 완료를 구분**해야 한다.

## 3. 데이터 특성

| 특성 | 모델링 영향 | 요구 대응 |
|---|---|---|
| 혼합 주기 | 일별 가격·환율·운임, 주별 CFTC, 월별 WASDE·GPR·무역, 연간 PSD | release-aware MIDAS 또는 일별 as-of join |
| 비정상성 | 가격 수준, 구조 변화, 정책·전쟁·기후 충격 | 로그수익률, 차분, 레짐·변화점 모델 |
| 이분산·두꺼운 꼬리 | 위기 시 변동성 군집, 평균오차 지표 왜곡 | EGARCH/GJR-GARCH, quantile·conformal interval |
| 작은 유효 표본 | 월별 10~15년이면 120~180개, 연간 자료는 10~15개 | 저복잡도 우선, 강한 정규화, 딥러닝 승격 게이트 |
| 다중공선성 | 유지류·에너지·환율·수급 지표 동행 | Elastic Net, 그룹 선택, 조건부 importance |
| 구조적 사건 | 2012 가뭄, 2018 미중 관세, 2020 코로나, 2022 러-우, 2025/26 호르무즈 | 사건을 이상치로 제거하지 않고 별도 holdout |
| 문서 중복·개정 | GAIN/AMIS PDF와 요약이 함께 존재, 전망치 개정 가능 | 문서 해시, canonical report, vintage 보존 |
| 목표와 계약 기준 차이 | CBOT 선물 vs 한국 CFR/CIF 조달비용 | 국제가격 목표와 한국 도착비용 프록시를 분리 |

## 4. 목표변수 설계

### 4.1 G1 — 가격동인

주 목표:

```text
y_return_h = log(CBOT_SBO_t+h / CBOT_SBO_t)
h ∈ {1, 5, 20, 60 거래일}
```

보조 목표:

- 실현변동성: 5·20·60일 로그수익률의 표준편차
- 한국 CIF 단가 프록시: `import_cif_usd / import_weight_kg × 1000`
- 원화 도착비용 프록시: CIF 단가 × KRW/USD(T+2)

가격 수준 하나만 목표로 삼으면 비정상성과 추세를 모델이 외워 성능을 과대평가할 수 있다. 수익률·변동성·한국 단가를 분리한다.

### 4.2 G2 — 확률 가격밴드

| 지평 | 사용 목적 | 출력 |
|---|---|---|
| 1일 | 일일 경보 | P10·P50·P90 또는 80/90% 구간 |
| 5일 | 단기 구매창 | 방향확률 + 가격밴드 |
| 20일 | 월간 계약 검토 | 분위수·구간·상위 동인 |
| 60일 | 약 3개월 조달 | 시나리오별 밴드와 누적위험 |

### 4.3 G3 — 레짐·의사결정

레짐 라벨은 사후 전체 표본으로 생성하지 않는다. 시점 $t$까지의 정보만 사용해 rolling 기준으로 정의한다.

예시:

- Bull: 미래 지평의 상승확률과 기대상승폭이 임계값 초과
- Bear: 하락확률과 기대하락폭이 임계값 초과
- Neutral: 두 조건 미충족 또는 예측구간이 넓어 방향 불명확
- Buy/Hold: 레짐만으로 결정하지 않고 예상 regret·구간폭·한국 도착비용을 함께 사용

내부 구매가격이 제외돼 있으므로 실제 P&L이 아니라 공개 시장가격 대비 상대 regret를 우선 사용한다.

## 5. 구조화 데이터 전처리

### 5.1 수집·표준화

1. UTC 원본 시각과 현지 발표 시각을 함께 저장한다.
2. `event_time`, `period_end`, `release_time`, `available_at`, `source_vintage`, `ingested_at`을 분리한다.
3. 품목·원산지·HS 코드·Incoterm·단위·통화를 용어사전과 Semantic Layer ID로 매핑한다.
4. 원값·원단위와 정규화 값은 함께 보존한다.
5. 관세청·USDA 개정값은 덮어쓰지 않고 vintage별로 적재한다.

### 5.2 시점 정렬

```text
모델의 t일 입력값 = available_at <= t를 만족하는 가장 최근 값
```

- WASDE는 대상월 값이 아니라 실제 발표일 이후에만 사용한다.
- PSD 연간 값은 전망 연도 시작일이 아니라 공개·개정일 기준으로 사용한다.
- 정책은 발표일·시행일을 분리하고, 예상 가능성과 실제 효력을 별도 피처로 만든다.
- 환율은 프로젝트의 T+2 결제 규칙을 적용하되 원시 환율과 T+2 파생값을 함께 둔다.
- 월·연간 자료의 일별 변환은 단순한 기간초 forward-fill이 아니라 발표일 이후 as-of fill을 사용한다.

### 5.3 결측·이상치

| 유형 | 처리 |
|---|---|
| 거래일 불일치 | 공통 시장 캘린더로 정렬, 휴장일 표시 |
| 정상적 공시 간격 | 발표 시점 이후 값 유지 + `days_since_release` 생성 |
| MCAR | 제한적 보간 또는 모델 내 결측 처리, 결측 indicator 추가 |
| MAR | 관측 변수와 누락 원인을 기록하고 다중 대치 후보 비교 |
| MNAR | 보간 금지, 사람 검토·불확실성 확대 |
| 데이터 오류 | 원천 확인 후 수정 또는 제외 |
| 검증된 시장 충격 | 원값 유지, event flag·regime feature 생성 |

기존 IQR 캡핑은 데이터 오류와 정상 시계열 노이즈에만 적용한다. 2020·2022 같은 실제 충격을 일괄 캡핑하면 G2/G3가 가장 중요한 꼬리위험을 학습하지 못하므로, 원본·robust 변환·캡핑 버전을 모두 실험하고 사건 검증 결과로 선택한다.

### 5.4 피처 엔지니어링

- 가격·환율·운임: log return, 1/5/20/60일 변화율, realized volatility, z-score
- 수급: STU, 생산·수출 전망 revision surprise, crush margin, oil share
- 대체재: CPO-SBO spread, rapeseed/sunflower relative price, cross-price elasticity proxy
- 기후: 생육단계별 누적강수, GDD, 고온일수, 토양수분 percentile, ENSO phase interaction
- 물류: BCAA/BDI, route-risk, 항만대기, 유가×거리, 위협수준 interaction
- 교역: 원산지별 한국 수입량·CIF 단가·점유율·집중도(HHI), 1·3·6개월 변화
- 정책: 발표·시행 dummy, 세율·혼합의무의 연속값, 국가·품목 interaction
- 문서: 사건 유형, 방향, 심각도, 국가, 품목, 관계 confidence, novelty, source diversity

## 6. 비정형 PDF 처리

```text
PDF/문서
 → OCR·레이아웃·표 추출
 → 문서·페이지·bbox·정확 인용 보존
 → 엔터티·수치·기간·국가·품목 추출
 → Dictionary·Ontology 매핑
 → Cause → Market Mechanism → Outcome 관계 검증
 → 사건 중복제거·문서 간 교차확인
 → 일별 event feature 생성
```

필수 필드:

| 그룹 | 필드 |
|---|---|
| 출처 | document_id, title, publisher, published_at, source_url, content_hash |
| 근거 | page_no, bbox, exact_quote, table_cell, evidence_id |
| 사건 | event_type, actor, country, commodity, start/end, severity |
| 인과 | cause, mechanism, outcome, direction, horizon |
| 품질 | extraction_confidence, semantic_confidence, relation_confidence, review_status |

LLM Structured Outputs는 JSON Schema 준수를 보장하는 구조 도구로 사용한다. 값·관계·근거의 사실성은 300~500개 대표 span의 human ground truth로 따로 평가한다.

## 7. 모델 진입 게이트

| 게이트 | 최소 조건 | 미충족 시 |
|---|---|---|
| 목표가격 | 2010~2025 거래일의 ≥98% 존재 | 모델 학습 중지 |
| 핵심 피처 | 분석창 커버리지 ≥85%, 3개월 연속 결측 없음 | 후보 제외 또는 저주기 모델 분리 |
| DQSOps | 종합 ≥0.70 | C-03 전달 차단 |
| 시점 정확성 | 모든 외생변수에 `available_at` 존재 | 예측모델 투입 금지 |
| 단위 | 통화·중량·Incoterm 검증 100% | 계산 피처 차단 |
| PDF 근거 | 핵심 사건의 evidence 연결률 100% | 시계열 피처화 금지 |
| 이벤트 품질 | entity/relation F1 목표 ≥0.85, 방향 정확도 ≥0.90 | 사람 검토 강화 |
| 레짐 표본 | 각 레짐 최소 50개 거래일 블록과 3개 이상 독립 사건 | 복잡 레짐 모델 보류 |
| 재현성 | dataset·feature·code·model version 기록 | 성능 비교 무효 |

## 8. 현재 준비도 판정

| 영역 | 판정 | 이유 |
|---|---|---|
| 문서 코퍼스 | 🟢 충분 | 2,231 PDF와 대응 요약 축적 |
| 소스 다양성 | 🟢 충분 | 수급·교역·기후·정책·물류·가격 포함 |
| 목표가격 | 🟡 재실행 필요 | Databento 수집 성공 기록은 있으나 현재 모델 입력 자산 확인 필요 |
| 통합 시계열 | 🔴 미완료 | processed feature matrix 미확인 |
| release-aware 정렬 | 🔴 미완료 | 스키마에 vintage/available_at 부족 |
| 비정형 구조화 | 🟡 부분 | 요약 다수, 정밀 event table·eval 미완료 |
| 기준선 비교 | 🟡 코드 일부 | LASSO·상관 구현, G2/G3 기준선 결과 미확인 |

**종합 판정: 데이터는 풍부하지만 모델 학습 테이블은 아직 준비 중이다.** 첫 성능 목표는 복잡 모델 도입이 아니라 누수 없는 데이터셋과 기준선의 재현이다.
