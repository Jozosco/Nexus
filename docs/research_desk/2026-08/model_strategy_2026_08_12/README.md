# Project Nexus 모델 후보·성능요건 조사 패키지

작성일: 2026-08-12  
저장 대상: `docs/research_desk/2026-08/model_strategy_2026_08_12/`  
범위: 대두유(Soybean Oil) 외부 데이터 기반 G1·G2·G3 분석

## 1. 결론

Project Nexus에 가장 적합한 접근은 하나의 거대 모델을 미리 확정하는 방식이 아니라, 목표별 전문 모델을 결합한 **Champion–Challenger 앙상블**이다.

권장 Champion 구조:

1. **G1 가격동인**: Elastic Net + XGBoost/LightGBM + SHAP·Permutation Importance + Granger/Local Projection
2. **G2 가격밴드**: SARIMAX + Quantile LightGBM + EGARCH-X의 예측을 조합하고 EnCQR로 구간 보정
3. **G3 레짐·Buy/Hold**: Markov Switching/HMM으로 Bull·Bear·Neutral 상태를 추정하고 G2 분포와 결합
4. **비정형 데이터**: LLM·NER·관계추출로 사건을 구조화하되, 원문 근거가 검증된 사건 신호만 시계열 피처로 투입
5. **의사결정**: 실제 구매 실행은 자동화하지 않고, 예측구간·상위 동인·시나리오·불확실성을 포함해 사람이 승인

TFT, N-BEATSx/N-HiTS, PatchTST, GRU/LSTM, Chronos 같은 딥러닝·시계열 파운데이션 모델은 폐기하지 않는다. 충분한 `as-of` 정렬 관측치와 반복 레짐이 확보된 후 동일한 walk-forward 검증에서 Champion을 이긴 경우에만 승격한다.

## 2. 현재 데이터의 핵심 판단

- `data/raw`에는 4,837개 파일, 약 1.653GB가 있다.
- 주요 형식은 PDF 2,231개, Markdown 요약 2,240개, XLSX 327개, CSV 24개다.
- USDA GAIN Oilseeds/Biofuels와 FAO AMIS 문서가 비정형 데이터의 중심이다.
- GitHub에 추적된 `data/processed`는 비정형 인덱스 CSV 2개뿐이며, 모델이 기대하는 통합 parquet는 현재 트리에서 확인되지 않는다.
- 따라서 첫 모델 학습보다 **release-aware 통합 데이터셋과 기준선 재현**이 우선이다.
- 내부 S&OP·ERP·조달원가는 D-021에 따라 학습·검증·피처에서 제외한다.

## 3. 파일 구성

| 파일 | 내용 |
|---|---|
| [01_data_inventory_and_readiness_2026_08_12.md](./01_data_inventory_and_readiness_2026_08_12.md) | 원시·처리 데이터 현황, 목표변수, 전처리, 모델 준비도 |
| [02_candidate_model_portfolio_2026_08_12.md](./02_candidate_model_portfolio_2026_08_12.md) | 후보 모델 비교, 권장 앙상블, 승격 조건 |
| [03_peak_performance_requirements_and_insights_2026_08_12.md](./03_peak_performance_requirements_and_insights_2026_08_12.md) | 최고 성능 요건, 평가 지표, 획득 인사이트 |
| [04_experiment_and_implementation_plan_2026_08_12.md](./04_experiment_and_implementation_plan_2026_08_12.md) | 실험 순서, 승인 게이트, 구현 산출물 |
| [05_academic_evidence_and_paid_sources_2026_08_12.md](./05_academic_evidence_and_paid_sources_2026_08_12.md) | 최근 연구, 인용·이용 순위, DBpia·유료자료 |

## 4. 프로젝트 기준 문서

- [Project Nexus README](https://github.com/Jozosco/Nexus/blob/main/README.md)
- [원시 데이터 인덱스](https://github.com/Jozosco/Nexus/blob/main/data/raw/INDEX.md)
- [Phase 1 Guide](https://github.com/Jozosco/Nexus/blob/main/.claude/skills/phase1/00_phase1_guide.md)
- [Modeling Rules](https://github.com/Jozosco/Nexus/blob/main/.claude/rules/modeling.md)
- [C-03 Data Scientist](https://github.com/Jozosco/Nexus/blob/main/.claude/agents/c03-data-scientist.md)
- [C-06 EDA Expert](https://github.com/Jozosco/Nexus/blob/main/.claude/agents/c06-eda-expert.md)
- [C-08 Data Quality Validator](https://github.com/Jozosco/Nexus/blob/main/.claude/agents/c08-data-quality-validator.md)
- [P1-06 Semantic & Ontology Engineer](https://github.com/Jozosco/Nexus/blob/main/.claude/agents/p106-semantic-ontology.md)
- [Semantic Layer & Ontology ERD](https://github.com/Jozosco/Nexus/blob/main/.claude/agents/Semantic%20Layer%20%26%20Ontology_ERD_v1.0.md)

## 5. 하드 제약

| 항목 | 적용 규칙 |
|---|---|
| 품목 | 대두유 원유·정제유만 최종 예측 대상. 다른 유지류는 대체재·보완재 피처로만 사용 |
| 원산지 | 미국·아르헨티나·브라질·베트남 중심 |
| 계약 기준 | CFR, 한국 도착비용은 관세청 CIF 단가와 환율·운임으로 외부 프록시 구성 |
| 예측 지평 | 1·5·20·60 거래일; 60일을 약 3개월 조달 의사결정 지평으로 사용 |
| 출력 | G1 동인 순위, G2 확률 가격밴드, G3 Bull/Bear/Neutral 및 Buy/Hold |
| 데이터 | 외부 데이터만 사용. D-021에 따라 내부 데이터 투입 금지 |
| 검증 | 무작위 분할 금지. Walk-forward 및 충격사건 holdout 필수 |
| 자동화 | AI는 추천만 제공. 구매 실행은 사람 승인 필수 |

## 6. 즉시 의사결정

모델 선택보다 먼저 다음을 완료해야 한다.

1. CBOT 대두유 목표가격의 2010~2025 일별 연속 시계열을 저장소 또는 버전 데이터 자산으로 확정한다.
2. 모든 피처에 `event_time`, `release_time`, `available_at`, `source_vintage`를 추가한다.
3. 월·분기·연간 자료는 기간 말이 아니라 실제 발표 시점 이후에만 모델이 보도록 정렬한다.
4. PDF 사건 신호는 `문서→페이지→정확 인용→엔터티→원인→메커니즘→결과` provenance를 통과한 건만 사용한다.
5. Seasonal naive·last value·ETS·SARIMAX 기준선을 재현하고, 이후 후보의 추가가치를 검증한다.

## 7. OpenAI 기반 비정형 추출 적용 경계

[Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)는 LLM 출력이 정의한 JSON Schema를 따르게 하는 데 사용한다. 이는 필드 누락·잘못된 enum을 줄이는 구조 계약이며, 문서 의미·수치·페이지 근거의 정확성을 자동 보장하지 않는다. [OpenAI Evals](https://developers.openai.com/api/docs/guides/evals)의 대표 샘플·human ground truth 원칙을 적용해 엔터티, 관계, 가격방향, 페이지 인용을 별도로 평가한다.

## 8. 상태

이 패키지는 모델을 확정하는 승인서가 아니라, 동일 데이터·동일 검증창에서 후보를 공정하게 비교하기 위한 설계 기준이다. 실제 Champion은 실험 결과와 사람 검토를 거쳐 결정한다.
