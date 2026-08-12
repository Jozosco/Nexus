# 학술 근거 및 유료 자료 목록

기준일: 2026-08-12

## 1. 조사·순위 원칙

- 최근 3–5년(주로 2022–2026) 논문을 우선하되, Nexus와의 직접 관련성·방법론적 기여·재현 가능성을 함께 평가했다.
- 아래 국제 논문의 인용 수는 **Consensus가 2026-08-12에 표시한 snapshot**이다. Google Scholar의 실시간 인용 수와 동일하다고 주장하지 않는다.
- DBpia의 `이용` 수는 페이지에 표시된 이용 지표이며 PDF 다운로드 수와 동일하다는 근거가 없으므로 별도 표기한다.
- 인용 수는 품질의 단일 척도가 아니다. 농산물 가격, 확률예측, 국면, 공급망 인과·지식그래프라는 Nexus의 용도에 맞춰 우선순위를 정했다.
- Consensus 응답에서 DOI가 제공되지 않은 항목은 DOI를 추정하지 않고 `미확인`으로 적었다.

## 2. 국제 학술 근거 — 인용 수 참고 순

| 순위 | 연구 | 연도·학술지 | Consensus 인용 | Nexus 적용 | 접근 |
|---:|---|---|---:|---|---|
| 1 | Nie et al., “A Time Series is Worth 64 Words: Long-term Forecasting with Transformers” | 2022, arXiv | 4,137 | PatchTST 장기 challenger; 외생변수·국면 설명은 별도 검증 | 공개 |
| 2 | Ansari et al., “Chronos: Learning the Language of Time Series” | 2024, arXiv | 903 | zero/few-shot foundation baseline | 공개 |
| 3 | Wu, Wang & Zeng, “Interpretable wind speed prediction with multivariate time series and temporal fusion transformers” | 2022, *Energy* | 216 | TFT의 다변량 multi-horizon·해석 구조 참고 | 초록/메타데이터 공개; 본문 조건 확인 |
| 4 | Kosasih et al., “Towards knowledge graph reasoning for supply chain risk management” | 2022, *International Journal of Production Research* | 130 | 공급망 KG/GNN과 위험 전파 | 본문 조건 확인 |
| 5 | Yang et al., “Supply chain risk management with machine learning: a review and future research directions” | 2022, *Computers & Industrial Engineering* 175, 108859 | 129 | 모델·데이터·위험관리 연구지도 | 본문 조건 확인 |
| 6 | Ray et al., “An ARIMA-LSTM model for predicting volatile agricultural price series with random forest technique” | 2023, *Applied Soft Computing* 149, 110939 | 105 | 통계+DL hybrid와 농산물 변동성 benchmark | 본문 조건 확인 |
| 7 | Jensen, Bianchi & Anfinsen, “Ensemble Conformalized Quantile Regression for Probabilistic Time Series Forecasting” | 2022, *IEEE TNNLS* 35, 9014–9025 | 84 | 비정상·이분산 시계열의 예측구간 보정 | 본문 조건 확인 |
| 8 | Avinash et al., “Hidden Markov guided Deep Learning models for forecasting highly volatile agricultural commodity prices” | 2024, *Applied Soft Computing* 158, 111557 | 50 | 국면/HMM + DL 결합 challenger | 본문 조건 확인 |
| 9 | Manogna, Dharmaji & Sarang, “Enhancing agricultural commodity price forecasting with deep learning” | 2025, *Scientific Reports* 15 | 49 | 23개 농산물·다수 모델 비교; 기상 외생변수 확장 근거 | 공개 저널 |
| 10 | AlMahri, Xu & Brintrup, “Enhancing supply chain visibility with knowledge graphs and large language models” | 2024, *International Journal of Production Research* 64, 2178–2209 | 39 | LLM→KG 추출과 공급망 가시성 | 본문 조건 확인 |
| 11 | Wyrembek, Baryannis & Brintrup, “Causal machine learning for supply chain risk prediction and intervention evaluation” | 2024, *International Journal of Production Research* 63, 5629–5648 | 34 | 정책·위험 개입의 인과 추정 | 본문 조건 확인 |
| 12 | Nayak et al., “N-BEATS Deep Learning Architecture for Agricultural Commodity Price Forecasting: A Comparative Study” | 2024, *Potato Research* 68, 1437–1457 | 32 | N-BEATS 농산물 challenger | 본문 조건 확인 |
| 13 | Kakade et al., “Forecasting commodity market returns volatility: A hybrid GARCH-LSTM approach” | 2022, *Intelligent Systems in Accounting, Finance and Management* 29, 103–117 | 28 | GARCH-X/EGARCH-X + DL 변동성 실험 | 본문 조건 확인 |

## 3. 우선 읽을 논문과 판단

### A. 직접 모델 benchmark

1. **Manogna et al. (2025):** ARIMA, SVR, XGBoost, MLP, RNN, LSTM, GRU, ESN을 23개 농산물에 비교한다. Nexus에서는 동일한 단일 승자를 복제하기보다 가격·상품·horizon별 champion이 달라지는지 확인하는 benchmark 설계에 활용한다. 논문도 날씨 등 외생변수 확장을 제안하므로 현재 기상·수급·교역 통합 방향과 맞는다. DOI: 미확인.  
   링크: https://consensus.app/papers/enhancing-agricultural-commodity-price-forecasting-with-manogna-dharmaji/56b3ecde808a51e29c684bfe0ddc45db/?utm_source=chatgpt

2. **Avinash et al. (2024):** HMM으로 고변동 농산물 가격의 숨은 국면을 안내하고 deep learning과 결합한다. Nexus G3의 HMM 확률을 G2 challenger gating에 연결할 후보 근거다. DOI: 미확인.  
   링크: https://consensus.app/papers/hidden-markov-guided-deep-learning-models-for-forecasting-avinash-ramasubramanian/88181b4a32ee5ee7a376c68109b30970/?utm_source=chatgpt

3. **Ray et al. (2023):** ARIMA–LSTM과 Random Forest 결합은 통계적 선형 구조와 비선형 잔차를 분리하는 hybrid benchmark의 근거다. 동일한 구성의 우월성을 가정하지 않고 SARIMAX+GBM 및 단일 모델과 비교한다. DOI: 미확인.  
   링크: https://consensus.app/papers/an-arimalstm-model-for-predicting-volatile-agricultural-ray-lama/a0e02f768da15862bea7727a3dc4c2e5/?utm_source=chatgpt

4. **Jensen et al. (2022):** EnCQR은 generic quantile model 위에 approximate distribution-free calibration을 제공하며 비정상·이분산 시계열의 구간 안정화에 적합하다. Nexus의 P10/P50/P90와 80/95% coverage에 직접 적용할 우선순위가 높다. DOI: 미확인.  
   링크: https://consensus.app/papers/ensemble-conformalized-quantile-regression-for-jensen-bianchi/253bf8d55a095fdaaf2ee1001123c54e/?utm_source=chatgpt

### B. Transformer·foundation challenger

5. **Nie et al. (2022), PatchTST:** 패치 단위 입력과 channel-independent 설계의 장기 시계열 benchmark다. 단, Nexus의 외생 사건·교역 관계 설명은 별도 계층이 필요하다. DOI: 미확인.  
   링크: https://consensus.app/papers/a-time-series-is-worth-64-words-longterm-forecasting-with-nie-nguyen/7425f108b08556ce919a01fa9d1376ac/?utm_source=chatgpt

6. **Ansari et al. (2024), Chronos:** 시계열 값을 token화한 pretrained probabilistic model로 zero/few-shot 기준선을 빠르게 제공한다. 운영 champion으로 채택하기 전에 외생변수, calibration, 비용, 재현성을 검증한다. DOI: 미확인.  
   링크: https://consensus.app/papers/chronos-learning-the-language-of-time-series-ansari-stella/04f1c2d3ae6f55028b63f01a5f7ed500/?utm_source=chatgpt

7. **Wu et al. (2022), TFT:** 다변량·multi-horizon·변수 중요도라는 구조가 G1/G2 연결에 유용하다. attention weight를 인과효과로 해석하지 않는다. DOI: 미확인.  
   링크: https://consensus.app/papers/interpretable-wind-speed-prediction-with-multivariate-wu-wang/c7d3083d7ab65874a9c159dc00354645/?utm_source=chatgpt

### C. 공급망 인과·지식 계층

8. **Wyrembek et al. (2024):** 공급망 위험의 예측과 개입 평가를 causal ML로 분리한다. 관세·바이오연료·항만 충격의 “무슨 일이 일어날까”와 “그 사건 때문에 얼마나 변했나”를 구분하는 근거다. DOI: 미확인.  
   링크: https://consensus.app/papers/causal-machine-learning-for-supply-chain-risk-prediction-wyrembek-baryannis/747712947c0f59fe9fe47ea74624e6ba/?utm_source=chatgpt

9. **Kosasih et al. (2022):** 지식그래프 reasoning을 공급망 위험에 적용한다. Nexus에서는 국가–품목–항만–정책–사건 관계와 근거 추적에 먼저 쓰고, edge 규모와 품질이 확보된 뒤 GNN을 비교한다. DOI: 미확인.  
   링크: https://consensus.app/papers/towards-knowledge-graph-reasoning-for-supply-chain-risk-kosasih-margaroli/c81d54e3233f5496a2eceb1bdb05c631/?utm_source=chatgpt

10. **AlMahri et al. (2024):** LLM과 KG를 결합해 공급망 visibility를 높이는 사용례다. PDF 추출 결과를 스키마와 provenance로 제약해야 한다는 Nexus 설계와 연결된다. DOI: 미확인.  
    링크: https://consensus.app/papers/enhancing-supply-chain-visibility-with-knowledge-graphs-almahri-xu/e72ff229af6a51d48819bd2118ce6153/?utm_source=chatgpt

## 4. 국내·DBpia/KCI 우선 검토 자료

| 연구 | 서지 | 페이지 지표 | 방법·시사점 | 접근·비용 상태 |
|---|---|---:|---|---|
| “A Design and Implement of Efficient Agricultural Product Price Prediction Model” | 임정주 외, 2022.5, *한국컴퓨터정보학회논문지* 27(5), 29–36 | DBpia 이용 75 | 소규모 농산물 자료에서 XGBoost/CatBoost 비교; 정확도와 학습시간 trade-off | **기관/개인 구독 확인 필요**, 개별 가격 미표시 |
| “머신러닝 기법을 활용한 감귤 가격 예측 연구” | 주현정·임상수, 2026.3, *한국산학기술학회논문지* 27(3), 947–956, DOI 10.5762/KAIS.2026.27.3.947 | DBpia 이용 46, 피인용 0 | 최근 국내 농산물 ML 가격예측 비교 | **기관/개인 구독 확인 필요**, 개별 가격 미표시 |
| “중장기 농산물 가격 예측을 위한 다단계 시계열 예측 모델” | Park et al., 2023, *한국컴퓨터정보학회논문지* 28(2), 201–207, DOI 10.9708/jksci.2023.28.02.201 | KCI 조회 201 | LightGBM, MLP, LSTM, GRU 및 hybrid multi-step 비교 | KCI PDF 링크 확인 가능 |
| “우리나라 양파 가격 안정화를 위한 관측사업 및 계약재배의 효과 분석” | 홍성민, 2022, 강원대학교 학위논문 | DBpia 이용 5, 피인용 0 | VAR/Granger/LSTM; 국내 수급·정책 맥락 | **보호/외부링크·구독 확인 필요** |

링크:

- 임정주 외: https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE11067162
- 주현정·임상수: https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE12729703
- Park et al.: https://www.kci.go.kr/kciportal/landing/article.kci?arti_id=ART002934622
- 홍성민: https://www.dbpia.co.kr/journal/detail?nodeId=T16362429

## 5. 유료 구매·구독 확인 목록

현재 공개 페이지에서 확인된 상태만 기록했으며 금액은 추정하지 않았다.

| 항목 | 필요한 이유 | 확인된 상태 | 다음 조치 |
|---|---|---|---|
| DBpia 임정주 외 (2022) 본문 | 국내 소규모 농산물 XGB/CatBoost 비교 | 기관/개인 구독 안내, 개별 가격 미표시 | 소속기관 로그인 후 원문 가능 여부 확인; 불가 시 DBpia 개별 구매 문의 |
| DBpia 주현정·임상수 (2026) 본문 | 최신 국내 감귤 ML 예측 | 기관/개인 구독 안내, 개별 가격 미표시 | DOI/학회 공개본 우선 확인 후 필요 시 구매 |
| DBpia 홍성민 (2022) 학위논문 | 국내 수급·정책과 VAR/Granger/LSTM | 보호/외부 링크 상태 | 대학 리포지터리·RISS 공개본 우선 확인 후 필요 시 원문복사 |
| *Applied Soft Computing*, *Energy*, *IJPR*, IEEE 등 일부 국제 본문 | hybrid, TFT, causal/KG 세부 구현 | 출판사/기관별 접근 조건 미확정 | DOI/저자 공개본/arXiv 우선; 기관 접근 실패 항목만 구매 견적 |
| Baltic Exchange BCAA/BDI 직접 데이터 | 한국 CFR 운임 신호와 라이선스 안정성 | 저장소 문서상 구독/견적 필요 | 빈도·재배포·과거기간 범위로 공식 견적 요청 |

논문은 제목·DOI로 arXiv, 저자 원고, 기관 저장소, KCI/RISS를 먼저 확인한다. 합법적 공개본이 없고 구현 세부가 실제 모델 결정에 필요한 경우에만 유료 구매 대상으로 확정한다.

## 6. OpenAI 구현 참고

- Structured Outputs는 지정한 JSON Schema에 대한 형식 준수를 높이므로 PDF 사건 추출에 적합하다. 다만 내용 검증은 별도 eval이 필요하다.  
  https://developers.openai.com/api/docs/guides/structured-outputs
- Evals는 사람이 만든 ground truth와 대표적인 실제 입력 집합을 바탕으로 설계해야 한다. 문서 유형·국가·언어·스캔 품질을 층화한 표본을 사용한다.  
  https://developers.openai.com/api/docs/guides/evals

## 7. 재현 시 주의사항

- 인용·이용 수는 시간이 지나면 바뀌므로 다시 조회할 때 날짜와 플랫폼을 함께 기록한다.
- “인용 수 상위”와 “Nexus에 가장 적합”을 구분한다. PatchTST/Chronos의 높은 인용은 challenger 가치가 높다는 뜻이지 외생변수 중심의 champion임을 의미하지 않는다.
- paywall 여부는 계정·기관 구독에 따라 달라질 수 있다. 본 표는 2026-08-12 비로그인/연결 환경에서 확인한 상태다.
- 논문 구현을 그대로 복제하지 말고 동일 walk-forward, as-of feature, baseline, stress slice에서 재평가한다.
