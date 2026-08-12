# Nexus 후보 모델 포트폴리오

기준일: 2026-08-12  
대상: 대두유 원유·정제유의 한국 도착원가(CFR), 수급·가격·국경 간 교역, 구매 의사결정  
원칙: 외부 데이터만 사용(D-021), 시점 정합성(as-of) 보장, walk-forward 검증, 사람의 최종 승인

## 1. 권고 결론

현재의 최적 설계는 하나의 거대 모델이 아니라 다음 역할을 조합한 **champion–challenger 포트폴리오**다.

1. **G1 동인 분석:** Elastic Net과 LightGBM/XGBoost를 병행하고, SHAP·permutation importance·Granger/국소투영(local projections)으로 방향성과 지속기간을 검증한다.
2. **G2 가격·구간 예측:** SARIMAX, quantile LightGBM, EGARCH-X의 예측을 가중 결합하고 Ensemble Conformalized Quantile Regression(EnCQR)으로 구간을 보정한다.
3. **G3 국면·의사결정:** Markov-switching 또는 HMM으로 Bear/Neutral/Bull 국면 확률을 산출하고, G2 분포와 결합해 Buy/Hold를 제안한다.
4. **Challenger:** GRU/LSTM, N-BEATSx/N-HiTS, TFT, PatchTST, Chronos를 동일한 walk-forward 조건에서 비교한다. 데이터 양·정합성·설명력 기준을 통과한 모델만 승격한다.
5. **지식·인과 계층:** PDF 사건을 지식그래프에 적재하고, causal ML은 특정 충격의 조건부 효과와 시나리오 분석에 사용한다. LLM은 추출·요약·근거 연결을 담당하며 수치 예측기를 대체하지 않는다.

## 2. 모델군별 후보와 적용 판단

| 모델군 | Nexus에서의 역할 | 강점 | 주요 위험 | 현재 판단 |
|---|---|---|---|---|
| Seasonal naive / last value / ETS | 모든 목표의 최소 기준선 | 단순·재현 가능, 데이터 누수 탐지에 유용 | 복합 충격 반영 불가 | **필수 baseline** |
| SARIMAX / Dynamic Regression | 가격 수준·수익률, 외생변수 효과 | 해석 가능, 소표본에 비교적 강함 | 비선형·상호작용 한계 | **Champion 구성요소** |
| Elastic Net | G1 안정적 변수 선택 | 공선성 제어, 계수 방향 해석 | 비선형 효과 미흡 | **G1 핵심** |
| LightGBM / XGBoost | G1 중요도, G2 점·분위수 예측 | 비선형·결측·상호작용 처리 | 불안정한 중요도, 외삽 약함 | **Champion 구성요소** |
| GARCH-X / EGARCH-X | 조건부 변동성과 꼬리 위험 | 변동성 군집·비대칭 반영 | 평균 예측과 별도 설계 필요 | **G2 위험 계층** |
| Quantile regression + EnCQR | 50/80/95% 예측구간 | 이분산·분포 변화에 강건한 보정 | 급격한 구조 변화 시 재보정 필요 | **구간 산출 필수** |
| Markov-switching / HMM | Bear/Neutral/Bull 국면 확률 | 전환 확률과 지속기간 제공 | 국면 수 선택·라벨 해석 주의 | **G3 핵심** |
| VAR/VECM | 상호연결 시장의 동학·충격반응 | Granger·IRF 등 경제적 해석 | 차원·정상성·공적분 제약 | **해석용 challenger** |
| GRU/LSTM | 다변량 순차 패턴 | 복잡한 시차 학습 | 데이터량·튜닝·재현성 요구 | **조건부 challenger** |
| N-BEATSx / N-HiTS | 다중 수평선 예측 | 추세·계절 분해, 직접 다중 horizon | 외생변수 정렬과 표본량 필요 | **우선 challenger** |
| TFT | 다중 horizon·변수 선택·attention | 정적/관측/미래 변수 구분, 해석 도구 | 복잡도·과적합·attention 오해 위험 | **데이터 gate 이후** |
| PatchTST | 장기 의존성, 패치 기반 Transformer | 장기 예측 benchmark에서 강력 | 변수 간 결합 방식, 외생 사건 설명 한계 | **연구용 challenger** |
| Chronos 등 TS foundation model | zero/few-shot 기준선 | 빠른 전이·다양한 시계열 사전학습 | 외생변수·도메인 설명력·비용 통제 | **zero-shot baseline** |
| Causal Forest / DML / BSTS | 정책·날씨·분쟁 충격의 조건부 효과 | 예측과 인과 질문 분리 | 식별 가정, 처치·통제군 설계 필요 | **시나리오 전용** |
| Knowledge Graph + GNN | 국가–품목–항만–정책–사건 관계 | 다단계 공급망 전파와 근거 추적 | 검증된 edge와 충분한 그래프 규모 필요 | **KG 먼저, GNN 나중** |
| LLM + RAG + Structured Outputs | PDF 사건·수치·전망 추출, 근거 요약 | 비정형 자료를 구조화하고 인용 가능 | 환각·중복·시점 혼입 | **추출 계층; 예측기 아님** |

## 3. 목표별 권장 구조

### G1 — “무엇이, 어느 시차에서, 어느 방향으로 움직였는가?”

권장 파이프라인:

`시점 정합 feature store → Elastic Net 안정성 선택 → LightGBM/XGBoost → SHAP·permutation → Granger/국소투영 확인 → horizon×regime 동인표`

- Elastic Net과 트리 모델 모두에서 반복 선택되는 변수를 **핵심 동인**으로 둔다.
- 중요도는 전체 기간 하나가 아니라 1·5·20·60 영업일 horizon, Bear/Neutral/Bull, 원산지별로 계산한다.
- SHAP은 예측 기여도이지 인과효과가 아니다. 정책·날씨 충격은 causal ML/국소투영에서 별도 확인한다.
- 기존 핵심 8개 변수(CBOT, CPO–SBO spread, WASDE stocks-to-use, BDI, BRL/USD, ENSO ONI, 대두 crush, 미국→한국 GATS)는 초기 후보일 뿐 고정 정답으로 간주하지 않는다.

### G2 — “가격은 어디까지 움직일 수 있는가?”

권장 ensemble:

`SARIMAX 평균 경로 + quantile LightGBM 비선형 분위수 + EGARCH-X 변동성 → horizon별 가중 결합 → EnCQR 보정`

- 예측 대상은 가격 수준과 로그수익률을 병행한다. 수준 예측의 장기 누적 오류와 수익률 예측의 해석 난점을 서로 보완한다.
- horizon은 1·5·20·60 영업일을 **직접 예측**한다. 재귀 예측은 보조 실험으로만 둔다.
- 산출물은 점 예측뿐 아니라 P10/P25/P50/P75/P90, 50/80/95% 구간, 상승 확률, 임계가격 초과 확률이다.
- 구간은 rolling calibration window로 보정하고, 국면별 coverage를 따로 보고한다.

### G3 — “현재 국면과 행동은 무엇인가?”

권장 파이프라인:

`HMM 또는 Markov-switching 국면 확률 + G2 예측분포 + 비용·리드타임 제약 → Buy/Hold 제안 → Human gate`

- 국면은 Bear/Neutral/Bull 확률로 출력한다. 하드 라벨만 저장하지 않는다.
- Buy/Hold는 단순 방향 예측이 아니라 한국 CFR 관점의 기대비용, 불확실성, 3개월 리드타임, 오판 비용을 포함한다.
- D-021 때문에 실제 내부 P&L 최적화는 할 수 없다. 공개 운임·환율·선물 기반의 **market-cost proxy와 regret**만 산출하고, 내부 구매량·재고·마진을 추정하거나 대체하지 않는다.

## 4. PDF·사건·지식그래프 모델

비정형 문서는 다음의 이중 경로로 사용한다.

1. **정형 사건 피처:** 문서에서 국가, 품목, 사건 유형, 발생/발표/적용일, 방향, 규모, 단위, 공급·수요·가격 영향, horizon, 신뢰도, 근거 페이지를 추출한다.
2. **지식그래프:** `Country–produces/exports/imports–Commodity`, `Event–affects–Supply/Demand/Price`, `Policy–applies_to–Country/Commodity`, `Shipment–uses–Route/Port` 관계를 저장한다.

예측 입력에는 문서 발행일보다 늦게 알려진 정보를 넣지 않는다. 같은 사건을 여러 보고서가 반복 보도할 때는 event fingerprint로 병합하되, 출처별 근거는 보존한다. LLM 출력은 JSON Schema로 제한하고 숫자·단위·날짜·페이지 인용 검증을 통과해야 한다.

## 5. 승격·폐기 기준

후보 모델은 다음 조건을 모두 통과해야 champion이 될 수 있다.

- 동일한 as-of snapshot과 walk-forward fold를 사용한다.
- seasonal naive 및 현재 champion보다 핵심 지표가 일관되게 낫다.
- 1개 평균 점수가 아니라 horizon·국면·충격 기간별 열화를 공개한다.
- 예측구간 coverage, calibration, 방향성, 거래비용 proxy를 함께 통과한다.
- 주요 변수의 부호·순위가 fold 간 지나치게 뒤집히지 않는다.
- 원자료→피처→예측→문서 근거의 lineage가 재현된다.
- 추론 지연·비용·재학습 시간과 운영 장애 시 fallback이 명시된다.

VMD/EMD 계열 분해는 전체 시계열을 한 번에 분해하면 미래 정보가 과거로 유입될 수 있으므로 기본 구성에서 제외한다. 사용할 경우 각 fold의 학습 창 안에서만 one-sided/rolling 방식으로 다시 적합해야 한다.

## 6. 최종 권장 우선순위

1. baseline + SARIMAX/Elastic Net 구축
2. quantile LightGBM + EGARCH-X + EnCQR
3. HMM/Markov-switching과 의사결정 계층
4. N-BEATSx/N-HiTS, GRU/LSTM challenger
5. TFT/PatchTST/Chronos benchmark
6. causal shock library
7. 검증된 KG 확장 후 GNN 검토

이 순서는 “단순 모델을 선호한다”는 뜻이 아니라, 현재 저장소의 정형 feature mart가 아직 완성되지 않았다는 사실을 반영한다. 데이터 gate를 통과하면 복잡한 challenger를 같은 평가판에 올려 성능으로 결정한다.
