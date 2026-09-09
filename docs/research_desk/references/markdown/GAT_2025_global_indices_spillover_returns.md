# GAT_2025_global_indices_spillover_returns

> 원본: `docs/research_desk/references/GAT_2025_global_indices_spillover_returns.pdf` · SHA256 `98ad5a744728fc61…` · 6쪽 · 5,333자 · 변환 2026-09-09 (pdf_to_markdown.py)

## 목차(자동 복원)
- Close Price Data (p.4)
  - • (p.4)
  - 2004.01.01 ~ 2024.12.31 , crawling from “Investing.com” (p.4)
  - • (p.4)
  - Used for graph data generation (p.4)
- Volume Data (p.4)
  - • (p.4)
  - 2004.01.01 ~ 2024.12.31 , crawling from “Investing.com” (p.4)
  - • (p.4)
  - Used for selecting 15 indices on market capitalization (p.4)
- Graph Data (p.4)
  - • (p.4)
  - Total of 41 test sets, each with 6 months input and 6 months ou (p.4)
  - tput (p.4)
  - • (p.4)
  - The nodes of the graph are the global indices, and the edges ar (p.4)
  - e created based on the correlation between two indices (p.4)

## 본문

<!-- page 1 -->

1,*, 2,†,*, 3,† * Co-First Author † Corresponding Author Abstract • This study examines the applicability of graph neural networks, specifically Graph Attention Networks (GAT), for finan cial return prediction across 15 major global stock indices.
• By incorporating inter-market relationships, these models aim to capture spillover effects and nonlinear dependencie s that traditional machine learning models may overlook.
• Through 30 repeated time- series cross-validation experiments, GAT generally achieve lower RMSE and MAE compar ed to benchmark models such as XGBoost, MLP, and SVM, particularly during financial crises, post-crisis recoveries, and volatile periods.
• However, their advantage is less pronounced in stable markets. Model performance was evaluated across 30 experim ents, with statistical significance tested at 1%, 5%, and 10% levels. The findings highlight the potential of graph-based models in financial forecasting while underscoring the need for further research on interpretability and computational efficiency.
2 1

<!-- page 2 -->

Introduction • This study proposes a financial forecasting method using Graph Neural Networks (GNNs). GNNs can capture nonline ar dependencies between global financial markets by learning from relationships between nodes, making them well-s uited for modeling inter-market interactions.
• While previous studies have applied GNNs to stock markets, cryptocurrencies, or single-market indices, research on modeling global financial market interactions remains limited.
• Also, while many studies claim improved predictive accuracy, their validation processes are often insufficient, lacking rigorous statistical significance testing.
• To address these limitations, this study applies Graph Attention Networks (GATs) to predict the daily returns of 15 ma jor global financial indices.
• Unlike traditional approaches, our method does not rely on external macroeconomic indicators or sentiment-based d ata. Instead, it leverages intrinsic market data, enhancing data efficiency and minimizing potential biases.
3 2 Literature Review • Xiang et al. (2023) demonstrated that GNNs effectively capture temporal dependencies in stock market prediction, o utperforming traditional ML and DL models.
• Chen et al. (2023) integrated natural language processing (NLP) with GNNs to incorporate sentiment analysis into fin ancial forecasting.
• Cheng et al. (2022), Choi & Kim (2024), and Das et al. (2024) attempted to apply graph-based models to financial risk prediction.
4 3

<!-- page 3 -->

Methodology This study aims to predict financial returns by measuring the spillover effects among global indices by examining wheth er utilizing graph-based embeddings improves predictive performance compared to benchmark models that rely solely o n raw data.
1. Graph Attention Networks (GAT) The Graph Attention Network (GAT) enhances Graph Neural Networks by incorporating an attention mechanism, allowin g the model to assign different weights to neighboring nodes.
• Calculating the Attention Coefficient ௜௝= LeakyReLU (்ܽ ℎ௜ ℎ௝ whereܽ is the attention vector and is the trainable weight matrix.
5 4 Methodology • Normalize Attention Coefficient ௜௝= softmax(݁௜௝) • Aggregate The Features of Neighbor Nodes ℎ௜ ᇱ= ߪ ෍ ௝∈ே௜ ߙ௜௝ ℎ௝ The heads are aggregated by using the multi-head attention method.
2. Benchmark Models Five benchmark models are used as a comparison to the graph-based model (GAT).
• Random Forest Regressor (RF) • Gradient Boost Regressor (XGB) • Multi-Layer Perceptron Regressor (MLP) • K-Nearest Neighbors Regressor (KNN) • Support Vector Regressor (SVM) 6 4

<!-- page 4 -->

Dataset 7 5

## Close Price Data


### •


### 2004.01.01 ~ 2024.12.31 , crawling from “Investing.com”


### •


### Used for graph data generation


## Volume Data


### •


### 2004.01.01 ~ 2024.12.31 , crawling from “Investing.com”


### •


### Used for selecting 15 indices on market capitalization


## Graph Data


### •


### Total of 41 test sets, each with 6 months input and 6 months ou


### tput


### •


### The nodes of the graph are the global indices, and the edges ar


### e created based on the correlation between two indices

Results & Conclusion 8 6

<!-- page 5 -->

Results & Conclusion • In Test 10 (period 2008 ~ 2009), following the collapse of Lehman Brothers, GAT outperformed XGB(p = 0.0011) and MLP (p = 0.0169), highlighting its ability to capture systemic market shocks.
• In Test 16 (period 2011 ~ 2012), covering heightened uncertainty surrounding Greece and EU bailout negotiations, G AT again outperformed XGB (p = 0.0298), MLP (p = 0.0265), and KNN (p = 0.0172) • In Test 31 (period 2019 ~ 2020, covering the sharp downturn in the early COVID-19 pandemics), demonstrated GAT’s exceptional capability, outperforming MLP in RMSE (p < 0.0001). In Test 33 (period 2021), GAT further distinguished i tself by outperforming MLP (p = 0.0029) and SVM (p = 0.0034) in MAE.
In conclusion, the superiority of the graph models mostly stands out during the financial crisis periods.
9 6 References 10 6 • Xiang, S., Cheng, D., Shang, C., Zhang, Y., & Liang, Y. (2023). Temporal and Heterogeneous Graph Neural Network for Fi nancial Time Series Prediction. arXiv preprint arXiv:2305.08740.
• Yin, W., Chen, Z., Luo, X., & Kirkulak-Uludag, B. (2024). Forecasting cryptocurrencies’ price with the financial stress ind ex: a graph neural network prediction strategy. Applied Economics Letters, 31(7), 630-639.
• Cheng, D., Yang, F., Xiang, S., & Liu, J. (2022). Financial time series forecasting with multi-modality graph neural netw ork. Pattern Recognition, 121, 108218.

<!-- page 6 -->

Thank you.
