# 최고 성능 모델의 요구사항과 기대 인사이트

기준일: 2026-08-12

## 1. “최고 성능”의 정의

Nexus의 최고 성능은 단일 RMSE 최저가 아니다. 다음 목적함수를 동시에 만족하는 **Pareto 최적 운영 모델**을 뜻한다.

- 가격 오차와 방향 오차가 작다.
- 예측구간이 실제 변동을 정해진 비율로 포괄하며 과도하게 넓지 않다.
- 충격·국면·원산지별 성능이 안정적이다.
- 동인과 사건 근거가 설명되고 원문 페이지까지 추적된다.
- 데이터 누수 없이 재현되며, 실패 시 안전한 baseline으로 복귀한다.
- 한국 CFR 구매 의사결정에 필요한 horizon·운임·환율·국경 간 교역을 반영한다.

## 2. 명확한 분석 목표와 타깃

| 목표 | 질문 | 타깃 | 기본 horizon | 필수 출력 |
|---|---|---|---|---|
| G1 동인 | 무엇이 가격을 움직이는가? | 가격/수익률에 대한 변수별 영향 | 1·5·20·60일 | 방향, 크기, 시차, 안정성, 근거 |
| G2 예측 | 가격은 어디까지 움직이는가? | CBOT/FOB/CFR 수준·수익률 | 1·5·20·60일 및 3개월 | P50, 분위수, coverage, 상승확률 |
| G3 국면 | 지금은 어떤 시장인가? | Bear/Neutral/Bull | 당일·주간 | 국면확률, 전환확률, 지속기간 |
| 의사결정 | 지금 구매할 것인가? | Buy/Hold 제안 | 3개월 리드타임 중심 | 기대비용, regret, 신뢰도, 반대근거 |

`CFR 한국`은 공개 CBOT 가격 그 자체가 아니다. 가능한 경우 `CBOT + 원산지 basis/FOB + 해상운임 + 보험/비용 + FX`로 분해해 각 성분과 합성 가격을 모두 예측한다. 공개되지 않는 내부 계약 조건과 수량은 범위 밖이다.

## 3. 필요한 데이터 유형

### 시장·거시

- CBOT soybean oil 및 대두·대두박, CPO·팜유·원유 등 대체·연관 상품
- USD/KRW, BRL/USD, ARS 관련 환율, 금리·달러지수
- BDI/BCAA 등 해상운임, 항만 혼잡, 선박·항로 사건
- 선물 만기, roll, basis/FOB/CFR 구성요소와 거래일 달력

### 수급·교역

- USDA WASDE/PSD/GATS/FAS GAIN의 생산·crush·재고·수출입·stocks-to-use
- 원산지별 미국·브라질·아르헨티나·베트남→한국 교역량과 단가
- 한국 관세청 HS 코드, 수입량·금액·단가, 신고/정정 시점
- 바이오연료 혼합의무·세액공제·수출 제한·관세 등 정책

### 농업기상·원격탐사

- ENSO ONI, 강수·온도·가뭄·홍수·열파, 작황 진행
- NASA/NOAA 등 격자 자료를 주요 산지와 생육 단계에 맞춘 집계값
- 이상기후 사건의 시작·종료·강도와 정상 대비 편차

### 비정형 문서

- PDF/HTML/보고서의 문서일·사건일·적용일, 국가, 품목, 기관, 수치·단위
- 공급/수요/가격 영향 방향과 기간, 전망 조건, 불확실성, 근거 페이지
- 동일 사건의 중복 보도와 수정판/개정판 관계

## 4. 처리·정제·전처리 요구사항

### 시점 정합성

- 모든 관측값에 `event_time`, `published_at`, `available_at`, `ingested_at`, `revision_id`를 둔다.
- 훈련 fold의 예측 시점 이후 공개된 개정치·문구를 입력하지 않는다.
- 월간/분기 자료는 단순 forward fill 전에 실제 발표일을 반영한다.
- 정책은 발표일, 시행일, 종료/갱신일을 분리한다.

### 가격·교역 자료

- 선물의 연속물 생성 규칙과 roll gap을 버전 관리한다.
- 통화·단위·품질·인코텀을 공통 기준으로 변환하고 원단위도 보존한다.
- HS 코드 개정과 국가명 변경을 유효기간이 있는 mapping으로 관리한다.
- 결측은 “미발표·비거래·수집실패·해당없음”을 구분한다.
- 극단값은 자동 삭제하지 않고 원자료 오류, 실제 시장 충격, 단위 오류를 구분한다.

### 다중 빈도·공간 자료

- 일/주/월 자료는 mixed-frequency lag 피처로 정렬한다.
- 원격탐사·기상은 산지 가중치와 생육 단계별 window로 집계한다.
- rolling 평균·변동성·spread·stocks-to-use·surprise는 각 fold 내부에서 계산한다.

### PDF/LLM 파이프라인

1. 원문 checksum과 문서 버전 등록
2. 텍스트/OCR 추출 및 표·페이지 좌표 보존
3. language/기관/보고서 유형 분류
4. JSON Schema 기반 사건·수치 추출
5. 날짜·단위·부호·페이지 인용 검증
6. 중복 사건 병합 및 출처별 provenance 유지
7. 사람 표본검수와 오류 taxonomy 기록

LLM의 구조화 출력은 형식 준수를 높이지만 내용의 진실성을 자동 보장하지 않는다. OpenAI 권고에 따라 명확한 key·description을 쓰고 대표적인 실데이터로 eval을 운영한다.

## 5. 모델 입력의 최소 품질 gate

| Gate | 요구사항 | 실패 시 조치 |
|---|---|---|
| Coverage | 핵심 피처의 시점별/국가별 결측률과 연속 구간 공개 | 피처 제외 또는 horizon 축소 |
| Freshness | 소스별 SLA와 지연 분포 측정 | stale flag, 이전 champion 유지 |
| Lineage | 원문/행→정제값→피처→예측 연결 | 배포 차단 |
| Leakage | as-of join, fold 내부 fit, revision vintage 검증 | 실험 폐기 |
| Unit | 단위·통화·incoterm·HS mapping 검증 | quarantine |
| Text extraction | 숫자·날짜·방향·인용의 표본 정확도 측정 | 사건 피처 사용 중단 |
| Sample | horizon별 유효 관측수와 국면별 사례수 공개 | 복잡 모델 승격 금지 |

고정된 “최소 24개월”은 통계 모델 fallback에는 유용하지만 deep model의 충분조건이 아니다. 복잡 모델은 월수보다 유효 시계열 길이, 독립적 충격 수, 피처 수 대비 표본 수, 국면별 사례 수로 판단한다.

## 6. 검증·평가 설계

### 분할

- Expanding 또는 sliding **walk-forward**만 사용한다.
- 모든 전처리, 변수 선택, scaling, decomposition, calibration을 fold 내부에서 다시 적합한다.
- 2018 무역갈등, 2020 팬데믹, 2022 전쟁·에너지 충격 등 사건 구간을 별도 stress slice로 둔다.
- 최신 기간은 최종 잠금 test로 유지한다. 2026 미완료 기간은 실시간 shadow/stress 평가로 구분한다.

### 지표

| 영역 | 지표 |
|---|---|
| 점 예측 | MAE, RMSE, sMAPE, MASE, median absolute error |
| 방향 | directional accuracy, MCC, 상승확률 Brier score |
| 확률·구간 | pinball loss, CRPS, empirical coverage, average interval width, calibration error |
| 국면 | macro-F1, balanced accuracy, Brier score, 전환·지속기간 안정성 |
| 동인 | fold별 rank correlation, sign stability, SHAP/permutation 일치도 |
| 의사결정 | market-cost proxy, regret, 임계가격 초과/미달 비용, turnover |
| 운영 | 추론 지연, 재학습 시간, 실패율, 비용, stale-data 비율 |

### 승격 규칙 예시

아래는 성능을 미리 약속하는 수치가 아니라 실험 전에 잠그는 acceptance rule이다.

- 4개 핵심 horizon 중 최소 3개에서 strongest baseline 대비 주 지표가 개선된다.
- 80/95% 구간의 empirical coverage 부족이 각각 목표 대비 5%p를 넘지 않는다.
- 평균 개선만으로 승격하지 않으며, 핵심 충격 slice에서 catastrophic failure가 없어야 한다.
- bootstrap 신뢰구간 또는 Diebold–Mariano 계열 검정으로 우연한 개선 가능성을 제시한다.
- 의사결정 모델은 거래·운송 proxy 비용을 포함한 regret가 champion보다 나빠지지 않아야 한다.

## 7. 최고 성능을 위한 모델·운영 요건

- **다중 목적 학습:** 점·분위수·방향·국면을 별도로 학습하되 공통 feature lineage를 쓴다.
- **국면 적응:** 고정 가중치와 regime-conditioned gating을 모두 시험한다.
- **확률 보정:** conformal calibration window를 모니터링하고 drift 시 재보정한다.
- **설명 안정성:** SHAP 하나가 아니라 계수, permutation, 국소투영과 삼각검증한다.
- **OOD 탐지:** 입력 범위·결측 패턴·embedding drift를 감시하고 낮은 신뢰도를 표시한다.
- **재현성:** 데이터 snapshot, 코드 commit, 환경, random seed, 모델·schema version을 기록한다.
- **실패 안전:** 소스 장애 시 마지막 정상 champion 또는 seasonal naive로 fallback한다.
- **Human gate:** Buy/Hold에는 핵심 근거, 반대 근거, confidence, 데이터 freshness를 함께 보여준다.

## 8. 구체적으로 얻어야 할 인사이트

1. **동인 지도:** horizon·국면별 상위 동인과 양/음의 방향, 반응이 시작·소멸하는 시차
2. **국가·원산지 비교:** 미국·브라질·아르헨티나·베트남의 생산·정책·환율·수출 충격이 한국 CFR에 전달되는 경로
3. **수급 민감도:** 생산, crush, 재고, stocks-to-use, 수출입 변화가 가격 분포에 미치는 영향
4. **대체재 전이:** CPO·대두·대두박·원유·바이오연료 정책 간 spread와 교차탄력성
5. **물류 전달:** BDI/BCAA, 항만 혼잡, 항로 차질이 원산지별 도착원가와 리드타임에 미치는 영향
6. **사건 효과:** 극한기상·분쟁·관세·혼합의무가 발생 전후와 국면별로 남긴 조건부 효과
7. **확률 시나리오:** 3개월 CFR의 P10/P50/P90, 임계가격 초과확률, Bull/Bear 전환확률
8. **한국 관점 해석:** 원산지 전환, 조달 시점, 운임·환율 hedge 필요성을 공개 데이터 범위 안에서 설명
9. **반대 증거:** 전망을 무효화할 수 있는 데이터, 아직 확인되지 않은 가정, 정보 신선도
10. **데이터 가치:** 예측 불확실성을 가장 크게 줄일 다음 데이터 소스와 수집 우선순위

## 9. 금지해야 할 해석

- SHAP 또는 Granger 결과를 곧바로 인과효과로 표현하지 않는다.
- 문서의 전망 문장을 실제 발생한 사건처럼 학습하지 않는다.
- 개정된 WASDE/교역 수치를 당시 알 수 있었던 값으로 간주하지 않는다.
- PDF 수가 많다는 이유로 독립 표본이 많다고 해석하지 않는다.
- 내부 재고·계약·마진이 없는 상태에서 실제 회사 P&L 최적이라고 주장하지 않는다.
- 단일 최근 구간의 우수성으로 구조 변화에 강하다고 결론 내리지 않는다.
