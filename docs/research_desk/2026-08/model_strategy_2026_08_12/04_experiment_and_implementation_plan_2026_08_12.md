# 실험·구현 계획

기준일: 2026-08-12  
목표: 현재 원자료를 재현 가능한 feature mart로 전환하고, 동일 평가판에서 모델 포트폴리오를 공정하게 비교한다.

## 1. 단계별 실행 순서

### Phase 0 — 계약·범위 고정

- G1/G2/G3의 target, horizon, cut-off time, 한국 CFR 합성식을 데이터 계약으로 고정한다.
- D-021 외부 데이터 전용 경계를 테스트와 문서에 명시한다.
- 국가·품목·HS 코드·단위·통화·incoterm dictionary의 유효기간을 관리한다.
- 모델 승격 지표, stress slice, rejection rule을 결과를 보기 전에 고정한다.

완료 조건: 목표변수 사전, as-of 규칙, 평가 protocol, 데이터 사용 허용목록이 승인됨.

### Phase 1 — 원자료 audit와 bronze 등록

- `data/raw`의 checksum, source URL, 수집시각, 문서일, 라이선스, 파서 버전을 inventory에 적재한다.
- 저장소에는 PDF 2,231개, Markdown 2,240개, XLSX 327개, CSV 24개가 있으나 모델 입력용 추적 Parquet은 확인되지 않았다. 먼저 “파일 존재”와 “학습 가능”을 분리한다.
- Databento, 관세청 템플릿, GDELT 등 세션 노트의 미반영 수집 결과를 재실행·검증한다.

완료 조건: 모든 핵심 source가 `available_at`과 revision 정책을 가짐.

### Phase 2 — silver/gold feature mart

- 가격, 환율, 운임, 수급, 교역, 기상, 사건 table을 공통 calendar에 정렬한다.
- `event_time/published_at/available_at/ingested_at`를 유지한다.
- 1·5·20·60일 lag, rolling, surprise, spread, basis, volatility, stocks-to-use를 fold-safe 함수로 생성한다.
- 모델별 별도 CSV 복제가 아니라 versioned feature view를 사용한다.

완료 조건: 동일 snapshot에서 baseline부터 deep challenger까지 재현 가능.

### Phase 3 — PDF 사건 추출과 평가

- 구조화 schema를 고정하고 GAIN, Biofuels, Oilseeds, FAO 문서에서 층화 표본을 뽑는다.
- 사람 정답셋에 국가·품목·날짜·수치·단위·영향 방향·근거 페이지를 표시한다.
- exact match/F1뿐 아니라 숫자·날짜·인용의 치명 오류율을 별도 측정한다.
- 추출 성능 gate 이전에는 텍스트 사건을 모델 피처로 사용하지 않는다.

완료 조건: 대표 표본 eval, 오류 taxonomy, provenance link가 운영됨.

### Phase 4 — 모델 benchmark

동일 fold·피처 snapshot으로 아래 실험을 순서대로 실행한다.

| ID | 실험 | 목적 | 주요 산출물 |
|---|---|---|---|
| E0 | last value, seasonal naive, ETS | 최소 기준·누수 감지 | baseline scorecard |
| E1 | Elastic Net, SARIMAX | 해석 가능한 선형 기준 | 계수·시차·잔차 진단 |
| E2 | LightGBM/XGBoost, quantile GBM | 비선형·분위수 | SHAP, P10/P50/P90 |
| E3 | GARCH-X/EGARCH-X | 변동성·꼬리 | 조건부 변동성, VaR형 지표 |
| E4 | HMM/Markov-switching | 국면·전환 | 국면확률, duration |
| E5 | ensemble + EnCQR | 확률예측 안정화 | calibrated intervals |
| E6 | GRU/LSTM, N-BEATSx/N-HiTS, TFT | deep challenger | horizon별 비교 |
| E7 | PatchTST, Chronos | Transformer/foundation benchmark | zero/few-shot 비교 |
| E8 | 국소투영, DML/causal forest | 충격·정책 효과 | event-study/HTE |
| E9 | KG reasoning, 이후 GNN | 공급망 사건 전파 | 경로·근거·위험점수 |

### Phase 5 — shadow 운영과 승격

- champion과 상위 challenger를 같은 날 동일 데이터로 실행한다.
- 예측값뿐 아니라 데이터 freshness, drift, coverage, 실패·fallback을 기록한다.
- 최소 한 번의 월간/분기 데이터 발표주기와 주요 이벤트를 관찰한 뒤 승격한다.
- Buy/Hold는 Human gate 이전에 외부로 자동 실행하지 않는다.

## 2. walk-forward 설계

예시 구조:

1. 학습: 시작일~T, 검증: T+1~T+h
2. T를 고정 간격으로 전진
3. 각 fold에서 scaling·imputation·feature selection·decomposition·calibration 재적합
4. 1·5·20·60일 target을 각각 직접 생성
5. 최신 완전 기간을 lockbox test로 보존

권장 stress slice:

- 2012 미국 가뭄
- 2018 미·중 무역갈등
- 2020 팬데믹·물류 충격
- 2022 러시아–우크라이나 전쟁·에너지/식용유 충격
- 2025 데이터가 완결되면 최신 구조 변화 구간
- 2026은 미완료 데이터와 실시간 availability를 명시한 shadow slice

사건 연도는 자동으로 “처치”가 되지 않는다. 각 causal 실험에서 발생일·노출국가·대상품목·대조군과 사전 추세를 별도 정의한다.

## 3. 실험 카드 필수 항목

각 run은 다음 metadata를 저장한다.

- experiment/run ID, git commit, environment, random seed
- raw snapshot과 feature-view version
- target, horizon, cut-off, train/validation/test dates
- 사용 피처와 `available_at` 검사 결과
- hyperparameter search space와 budget
- 전체·horizon·regime·country·event slice 지표
- calibration plot, residual diagnostic, error examples
- SHAP/permutation/계수와 fold 안정성
- 추론 비용·시간, 모델 크기, fallback
- 알려진 한계와 배포 여부 결정

## 4. 산출물 구조 제안

```text
data/
  bronze/                 # 원자료 registry·checksum·vintage
  silver/                 # 정제된 source별 table
  gold/                   # as-of feature views와 targets
schemas/
  document_event.schema.json
  feature_contract.yaml
  target_contract.yaml
src/
  data_quality/
  features/
  forecasting/
  regimes/
  causal/
  knowledge_graph/
  evaluation/
configs/
  experiments/
reports/
  model_cards/
  evals/
  stress_tests/
```

실제 디렉터리는 기존 저장소 구조와 합치되, `data/raw`를 직접 변형하지 않고 파생 data의 lineage를 유지한다.

## 5. 주간 실행안

### 1–2주차: 학습 가능한 데이터 기반

- 수집 결과 재현, schema/단위/시점 audit
- CBOT·FX·운임·WASDE/PSD/GATS·관세청의 core table 구축
- seasonal naive/ETS baseline과 walk-forward evaluator 완료

### 3–4주차: Champion v0

- Elastic Net/SARIMAX/LightGBM/EGARCH-X/HMM
- quantile·EnCQR 구간과 G1 driver table
- 최초 통합 scorecard·오류분석

### 5–6주차: 문서·사건 계층

- GAIN/Biofuels/Oilseeds 대표 표본 정답셋
- 구조화 추출 eval과 KG node/edge 적재
- gate 통과 사건만 시차 피처로 연결

### 7–8주차: Challenger·의사결정

- N-BEATSx/N-HiTS, GRU/LSTM, TFT 우선 비교
- PatchTST/Chronos zero-shot/fine-tune 가능성 평가
- 한국 CFR 시나리오와 market-cost regret, Buy/Hold Human gate

일정은 인력 약속이 아니라 dependency 순서다. 데이터 계약·as-of 검증이 실패하면 이후 모델 단계는 시작하지 않는다.

## 6. 모델 선택 의사결정표

| 조건 | 우선 모델 |
|---|---|
| 정형 표본이 짧고 설명력이 중요 | SARIMAX + Elastic Net + GBM |
| 변동성 군집·비대칭이 큼 | EGARCH-X 추가 |
| 예측구간 undercoverage | Quantile GBM + EnCQR 재보정 |
| 국면 전환이 명확 | HMM/Markov-switching gating |
| 충분한 다변량 장기 표본 | N-BEATSx/N-HiTS, TFT, PatchTST challenger |
| 외생변수 정렬이 불완전 | foundation model은 참고 baseline만 |
| 정책/충격의 효과가 질문 | DML/causal forest/국소투영; 예측 모델과 분리 |
| 문서 관계가 풍부하나 edge가 적음 | KG 검색·규칙 추론; GNN 보류 |

## 7. 주요 위험과 완화

| 위험 | 징후 | 완화 |
|---|---|---|
| 미래 정보 누수 | 비현실적 점수, 최신 개정치 사용 | `available_at`, vintage, fold 내부 fit |
| PDF 중복·수정본 | 같은 사건 과대계수 | checksum, canonical event, provenance |
| 복잡 모델 과적합 | fold·seed별 순위 급변 | nested tuning, 단순 baseline, regularization |
| 구간 과신 | coverage 급락 | EnCQR, regime별 monitoring |
| 설명 오독 | SHAP을 인과로 표현 | causal 분석 분리, 반대 근거 표시 |
| D-021 경계 침범 | 내부 지표 proxy 생성 | allowlist, schema test, model card 명시 |
| 유료 소스 종속 | 재현 불가·비용 급증 | 라이선스 registry, 공개 대체재 benchmark |

## 8. 완료 정의

- [ ] 원자료에서 최종 예측까지 재현 가능한 lineage
- [ ] 모든 모델이 같은 walk-forward fold와 baseline 사용
- [ ] G1/G2/G3 및 한국 관점의 통합 scorecard
- [ ] PDF 추출의 대표 정답셋과 근거 페이지 검증
- [ ] 충격·국면·horizon별 성능과 실패 사례 공개
- [ ] champion/challenger 승격 기록과 fallback 테스트
- [ ] 비용·라이선스·유료 문헌/데이터 의존성 기록
- [ ] Human gate가 포함된 Buy/Hold 보고서
