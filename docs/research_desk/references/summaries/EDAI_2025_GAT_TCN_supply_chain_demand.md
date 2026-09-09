# 요약 — EDAI_2025_GAT_TCN_supply_chain_demand

> 상태: **골격(자동)** — 서지·판독 메타·목차·키워드·수치 후보는 자동 생성. 아래 '핵심'부터는 세션이 `markdown/EDAI_2025_GAT_TCN_supply_chain_demand.md`를
> 읽고 채움. 원본 PDF는 직접 판독하지 않음(A-251). 정직 분류 어휘: 채용 / Challenger 검토 대기 / 배경 / 인용 주의 / 반면교사.

## 서지·판독 메타
- 원본: `docs/research_desk/references/EDAI_2025_GAT_TCN_supply_chain_demand.pdf` · SHA256 `1593839feeeeefb4…`
- 분량: 6쪽 · 25,599자 · 표 3개 · 스캔본 의심: 아니오
- 변환일: 2026-09-09 · 변환기: scripts/pdf_to_markdown.py

## 목차(자동)
  - Supply Chain Demand Forecasting via Graph Attention Networks (p.1)
- Integrated with Temporal Convolutional Networks (p.1)
    - Benli Li (p.1)

## 대두유 관련 키워드 적중(자동)
forecast(39), supply chain(31), RIN(22), CIF(2)

## 수치 후보(자동 — 검증 전)
- tive spare parts datasets demonstrate that GAT-TCN achieves 23.7% reduction in Mean Absolute Percentage Error (MAPE) compared
- baselines, with partic- ularly significant improvements of 46% in low-demand scenarios.
- Results demonstrate that our GAT-TCN model achieves 16.38% MAPE, reducing forecasting errors by 12.09% compared to Pro
- phet and 7.93% compared to DeepAR. Ablation studies and attention visualiz
- aseline ARIMA 24.6 31.8 42.3 28.3 35.7 48.2 22.9 29.4 39.1 -89.4% XGBoost 21.3 28.5 38.6 24.7 31.2 42.8 19.8 26.3 35.7 -71.2%
- LSTM 18.7 24.9 34.2 21.5 27.8 38.4 17.2 23.6 32.1 -58.3% GRU 18.2 24.3 33.5 20.9 27.1 37.6 16.8 23.1 31.4 -56.1% GCN
- -LSTM 16.4 22.1 30.8 18.7 24.6 34.2 15.3 21.2 28.9 -42.7% DCRNN 15.1 20.3 28.4 17.2 22.9 31.7 14.1 19.6 26.8 -38.2% G
- 7.2 23.1 14.6 19.4 25.8 11.9 16.5 21.7 Baseline Improvement 15.2% 15.3% 18.7% 15.1% 15.3% 18.6% 15.6% 15.8% 19.0% 15.3% avg N
- Figure 2: Multi-step Forecasting MAPE Comparison (70%/10%/20%) and evaluated on 1-step, 3-step, and 7-step ahead forecast
- GAT-TCN consistently outperforms baselines, achieving 15.3% av- erage MAPE reduction compared to the best baseline (DCR
- is most pronounced in long-term forecasting (7-step ahead: 18.7% MAPE reduction), demonstrating the effec- tiveness of adapt
- and TCN are essential: Removing either component causes 46-52% MAPE increase, confirming that spatial and temporal modelin
- Adaptive fusion outperforms fixed weighting: The 21.9% MAPE gap between fixed and adaptive fusion validates our hy
- (Full) 12.8 5.92 4.37 0.891 18.9 Performance Drop w/o GAT +46.1% +47.5% +43.7% -12.3% -48.7% Performance Drop w/o TCN +51.6%
- +42.0% +49.2% -10.4% -35.2% Performance Drop w/o Adaptive Fusion +21.9% +20.8% +22.2% -
- 5.5% -2.1% Note: ↓indicates lower is better, ↑indicates higher is bett
- s critical: Replacing GAT with simple GCN increases MAPE by 26.6%, demonstrating that different attention heads capture diver
- Minimal computational overhead: The full model adds only 2.1% inference time compared to fixed fusion, making adaptive ga
- 4.7 units (DCRNN), a 51% reduction. For high-demand items, both models perform well,
- troduced parts with <3 months of history, MAPE increases to 28.4% (vs. 12.8% overall), as the model lacks sufficient temporal

## 핵심 주장 (세션 작성)
- (미작성)

## 방법·데이터 (세션 작성)
- (미작성)

## Nexus 관련성 — G1 / G2 / G3 / 시맨틱 (세션 작성)
- (미작성)

## 정직 분류·인용 가능 문장 (세션 작성)
- 분류: (미작성)
- 인용 가능 문장·locator: (미작성)

## 온톨로지 반영 후보 (세션 작성)
- CE evidence / MP 등재 / 엔티티: (미작성)
