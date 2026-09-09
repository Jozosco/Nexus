# EDAI_2025_GAT_TCN_supply_chain_demand

> 원본: `docs/research_desk/references/EDAI_2025_GAT_TCN_supply_chain_demand.pdf` · SHA256 `1593839feeeeefb4…` · 6쪽 · 25,599자 · 변환 2026-09-09 (pdf_to_markdown.py)

## 목차(자동 복원)
  - Supply Chain Demand Forecasting via Graph Attention Networks (p.1)
- Integrated with Temporal Convolutional Networks (p.1)
    - Benli Li (p.1)

## 표(자동 추출)
**표 p.3**

| GATModule | Attentionheads | 8 | Multi-headattentionfordiversepatterns |
|---|---|---|---|
|  | Hiddendimension | 64 | Featureembeddingsize |
|  | Dropoutrate | 0.2 | Regularizationtopreventoverfitting |
| TCNModule | Dilationfactors | [1,2,4,8] | Exponentialreceptivefieldgrowth |
|  | Kernelsize | 3 | Convolutionfilterwidth |
|  | Numberoflayers | 4 | Networkdepth |
|  | Channels | 64 | Featurechannelsperlayer |
| FusionLayer | Gatedimension | 128 | Hiddensizeforgatingmechanism |
| Training | Optimizer | Adam | Adaptivelearningrateoptimizer |
|  | Learningrate | 0.001 | Initiallearningrate |
|  | Batchsize | 32 | Trainingbatchsize |
|  | Maxepochs | 100 | Maximumtrainingiterations |
|  | Lossweight𝜆 | 0.1 | BalancebetweenMAPEandL1 |

**표 p.4**

| ARIMA | 24.6 | 31.8 | 42.3 | 28.3 | 35.7 | 48.2 | 22.9 | 29.4 | 39.1 | -89.4% |
|---|---|---|---|---|---|---|---|---|---|---|
| XGBoost | 21.3 | 28.5 | 38.6 | 24.7 | 31.2 | 42.8 | 19.8 | 26.3 | 35.7 | -71.2% |
| LSTM | 18.7 | 24.9 | 34.2 | 21.5 | 27.8 | 38.4 | 17.2 | 23.6 | 32.1 | -58.3% |
| GRU | 18.2 | 24.3 | 33.5 | 20.9 | 27.1 | 37.6 | 16.8 | 23.1 | 31.4 | -56.1% |
| GCN-LSTM | 16.4 | 22.1 | 30.8 | 18.7 | 24.6 | 34.2 | 15.3 | 21.2 | 28.9 | -42.7% |
| DCRNN | 15.1 | 20.3 | 28.4 | 17.2 | 22.9 | 31.7 | 14.1 | 19.6 | 26.8 | -38.2% |
| GAT-TCN | 12.8 | 17.2 | 23.1 | 14.6 | 19.4 | 25.8 | 11.9 | 16.5 | 21.7 | Baseline |
| Improvement | 15.2% | 15.3% | 18.7% | 15.1% | 15.3% | 18.6% | 15.6% | 15.8% | 19.0% | 15.3%avg |

**표 p.5**

| GAT-only | 19.4 | 8.73 | 6.52 | 0.781 | 12.3 |
|---|---|---|---|---|---|
| TCN-only | 18.7 | 8.41 | 6.28 | 0.798 | 9.7 |
| FixedFusion(𝛼 =0.5) | 15.6 | 7.15 | 5.34 | 0.842 | 18.5 |
| NoAttention(GCN) | 16.2 | 7.48 | 5.61 | 0.829 | 15.2 |
| GAT-TCN(Full) | 12.8 | 5.92 | 4.37 | 0.891 | 18.9 |
| PerformanceDropw/oGAT | +46.1% | +47.5% | +43.7% | -12.3% | -48.7% |
| PerformanceDropw/oTCN | +51.6% | +42.0% | +49.2% | -10.4% | -35.2% |
| PerformanceDropw/oAdaptiveFusion | +21.9% | +20.8% | +22.2% | -5.5% | -2.1% |

## 본문

<!-- page 1 -->


### Supply Chain Demand Forecasting via Graph Attention Networks


## Integrated with Temporal Convolutional Networks


#### Benli Li

Chongqing College of Architecture and Technology Chongqing, China 272847738@qq.com Abstract Spare parts demand forecasting is critical for supply chain manage- ment, yet remains challenging due to intermittent demand patterns and complex spatial-temporal dependencies across distribution networks. Traditional statistical methods and conventional deep learning approaches often fail to capture the heterogeneous rela- tionships among spare parts and their geographical correlations.
This paper proposes a novel Graph Attention Network with Tempo- ral Convolutional Network (GAT-TCN) framework that integrates multi-head attention mechanisms for modeling diverse part rela- tionships with temporal convolutional layers for capturing long- range temporal dependencies. We construct a heterogeneous graph incorporating geographical proximity, functional similarity, and de- mand correlation, enabling the model to learn adaptive importance weights for different relationship types. Extensive experiments on real-world automotive spare parts datasets demonstrate that GAT-TCN achieves 23.7% reduction in Mean Absolute Percentage Error (MAPE) compared to state-of-the-art baselines, with partic- ularly significant improvements of 46% in low-demand scenarios.
Ablation studies validate the contribution of each component, while interpretability analysis reveals that different attention heads spe- cialize in distinct relationship patterns. The proposed framework provides an effective and interpretable solution for spare parts demand forecasting in complex supply chain networks.
CCS Concepts • Networks →Network architectures; Network design principles.
Keywords Spare parts forecasting, graph attention networks, temporal convo- lutional networks, supply chain management, intermittent demand, spatial-temporal modeling, deep learning, inventory optimization ACM Reference Format:
Benli Li. 2025. Supply Chain Demand Forecasting via Graph Attention Networks Integrated with Temporal Convolutional Networks. In 2025 2nd International Conference on Economic Data Analytics and Artificial Intelli- gence (EDAI 2025), November 14–16, 2025, Changsha, China. ACM, New York, NY, USA, 6 pages. https://doi.org/10.1145/3789297.3789408 This work is licensed under a Creative Commons Attribution 4.0 International License.
EDAI 2025, Changsha, China © 2025 Copyright held by the owner/author(s).
ACM ISBN 979-8-4007-1966-0/2025/11 https://doi.org/10.1145/3789297.3789408 1 Introduction 1.1 Background and Motivation The rapid expansion of cross-border e-commerce has fundamen- tally transformed global supply chain management, introducing unprecedented complexity in demand forecasting. Modern supply chains now span multiple countries, involve hundreds of intercon- nected nodes (suppliers, warehouses, logistics centers), and must respond to highly volatile consumer behavior [1]. Accurate demand forecasting is critical for optimizing inventory levels, reducing op- erational costs, and maintaining service quality in this dynamic environment [2].
Traditional demand forecasting methods, such as ARIMA and exponential smoothing, rely on univariate time series analysis and assume independence between supply chain entities. Prophet com- bines decomposable time series models with flexible trend and sea- sonality components [3]. However, modern supply chains exhibit complex interdependencies where demand fluctuations at one node propagate through the network, creating cascading effects. These spatial dependencies, coupled with multi-scale temporal patterns (daily fluctuations, weekly cycles, seasonal trends), pose significant challenges that conventional statistical models cannot adequately address [4].
Recent advances in deep learning have shown promise in cap- turing non-linear temporal dependencies. Models like DeepAR have demonstrated improved performance by learning probabilis- tic forecasts from historical data through autoregressive recurrent networks [5]. Long Short-Term Memory (LSTM) networks have been widely applied to capture long-range temporal dependencies [6]. However, these approaches treat each supply chain node as an isolated entity, failing to leverage the rich structural information embedded in the supply chain network topology. This limitation be- comes particularly critical during disruptions, where understanding node relationships is essential for accurate prediction.
1.2 Research Objectives and Contributions To address these challenges, this paper proposes a novel demand forecasting framework that integrates Graph Attention Networks (GATs) with Temporal Convolutional Networks (TCNs). Our ap- proach simultaneously models the spatial dependencies among supply chain nodes and the multi-scale temporal patterns in de- mand data. GAT captures the complex dependencies between sup- ply chain nodes through learnable attention weights [7], while TCN extracts multi-scale temporal features using dilated convolu- tions with exponentially increasing receptive fields [8]. The key innovation lies in an adaptive fusion mechanism that dynamically 722

<!-- page 2 -->

EDAI 2025, November 14–16, 2025, Changsha, China Benli Li balances graph-based and temporal features according to different forecasting scenarios.
The main contributions of this work are threefold:
First, we design a dual-stream architecture that enables the model to learn both ”who affects whom” (spatial) and ”when affects what” (temporal) simultaneously. This architecture addresses the limita- tions of existing methods that treat nodes independently.
Second, we develop an adaptive gated fusion mechanism that dynamically adjusts the contribution of graph features and temporal features based on node characteristics and temporal context. Unlike fixed-weight fusion strategies, our approach learns to emphasize graph information during supply chain disruptions and temporal patterns during promotional events, enhancing model robustness across diverse scenarios.
Third, we conduct comprehensive experiments on a real-world cross-border e-commerce dataset spanning 750 nodes and 3.25 years.
Results demonstrate that our GAT-TCN model achieves 16.38% MAPE, reducing forecasting errors by 12.09% compared to Prophet and 7.93% compared to DeepAR. Ablation studies and attention visualization further validate the effectiveness of each component and provide interpretable insights into supply chain dynamics.
1.3 Related Work Existing research in supply chain demand forecasting can be cate- gorized into three main streams: statistical methods, deep learning approaches, and graph-based models.
Statistical Methods: Traditional time series forecasting methods have been widely adopted due to their interpretability and computa- tional efficiency. However, these methods struggle with non-linear patterns and cannot capture inter-node dependencies in supply chain networks, limiting their effectiveness in complex modern supply chains.
Deep Learning Approaches: Deep learning models have shown superior performance in capturing temporal dependencies in demand forecasting.
Temporal Convolutional Networks have emerged as powerful alternatives, offering parallelizable training and long-range dependency modeling through dilated convolutions.
Yet these models still treat nodes independently, ignoring spatial relationships in supply chain networks.
Graph-Based Models: Recent work has explored graph neural networks for spatiotemporal forecasting, demonstrating the value of modeling spatial relationships. Spatio-Temporal Graph Con- volutional Networks combine graph convolutions with temporal convolutions for traffic forecasting [9]. However, the application of graph attention mechanisms combined with temporal convolu- tions remains largely unexplored in supply chain contexts, where both adaptive spatial weighting and multi-scale temporal modeling are crucial for handling diverse disruption scenarios and demand patterns .
2 Methodology 2.1 Problem Formulation and Overall Architecture Problem Definition: Consider a supply chain network repre- sented as a graphG = (V, E), where V = {v1, v2, . . . , vN} denotes N nodes (warehouses, distribution centers) and E represents their relationships (supplier-customer connections, geographical prox- imity). For each node vi, we observe historical demand sequences Xi = {x1 i , x2 i , . . . , xT i } over T time steps. Our objective is to predict future demand ˆYi = {yT+1 i , yT+2 i , ..., yT+H i } for the next H time steps across all nodes simultaneously.
Architecture Overview: Our proposed GAT-TCN framework integrates spatial and temporal modeling through a dual-stream architecture, as illustrated in Figure 1. The framework consists of three core components working in parallel and synergy:
Graph Attention Network (GAT) Module: Captures spatial dependencies by learning adaptive attention weights between con- nected nodes, enabling the model to identify which supply chain partners most influence each node’s demand.
Temporal Convolutional Network (TCN) Module: Extracts multi-scale temporal patterns through dilated causal convolutions, capturing both short-term fluctuations and long-term seasonal trends without recurrent connections.
Adaptive Fusion Mechanism: Dynamically combines graph- based spatial features and temporal features using learned gating weights, allowing the model to emphasize different information sources based on context (e.g., prioritizing graph signals during disruptions).
Figure 1 Overall architecture of the proposed GAT-TCN frame- work. The model processes input demand sequences through par- allel GAT and TCN modules, then adaptively fuses their outputs for final prediction.
The architecture processes input sequences through both mod- ules simultaneously, then fuses their outputs before generating final predictions through a fully connected layer. Table 1 summarizes the key hyperparameters of each component.
2.2 Spatial-Temporal Feature Extraction Graph Attention Module: Traditional graph convolutions assign fixed weights to neighbors, but supply chain influence varies dy- namically (e.g., a key supplier matters more during stockouts). Our GAT module computes node-specific attention coefficients 훼ij to capture these adaptive relationships [7]:
훼ij = exp(LeakyReLU(aT[Whi||Whj])) Í k∈Ni exp(LeakyReLU(aT[Whi||Whk])) (1) where hi represents node i’s feature vector, W is a learnable weight matrix, a is the attention vector, and Ni denotes node i’s neighbors.
The aggregated spatial feature becomes:
hi′ = 휎©­ « Õ j∈Ni 훼ijWhjª® ¬ (2) We employ multi-head attention with 8 heads to enhance repre- sentation capacity by learning diverse dependency patterns across different subspaces.
Temporal Convolutional Module: Unlike RNNs that process sequences sequentially, TCN employs dilated causal convolutions for parallel computation and exponentially growing receptive fields [8]. For dilation factor d at layer l, the receptive field size becomes 2l −1. Our 4-layer TCN with dilations {1,2,4,8}captures patterns 723

<!-- page 3 -->

Supply Chain Demand Forecasting via Graph Attention Networks Integrated with Temporal Convolutional Networks EDAI 2025, November 14–16, 2025, Changsha, China Figure 1: GAT-TCN Framework Architecture Table 1: Key Hyperparameters of the GAT-TCN Framework Component Parameter Value Description GAT Module Attention heads 8 Multi-head attention for diverse patterns Hidden dimension 64 Feature embedding size Dropout rate 0.2 Regularization to prevent overfitting TCN Module Dilation factors [1, 2, 4, 8] Exponential receptive field growth Kernel size 3 Convolution filter width Number of layers 4 Network depth Channels 64 Feature channels per layer Fusion Layer Gate dimension 128 Hidden size for gating mechanism Training Optimizer Adam Adaptive learning rate optimizer Learning rate 0.001 Initial learning rate Batch size 32 Training batch size Max epochs 100 Maximum training iterations Loss weight 휆 0.1 Balance between MAPE and L1 spanning 15 time steps while maintaining causality:
FTCN = Conv1Dd=8 (Conv1Dd=4 (Conv1Dd=2 (Conv1Dd=1 (X)))) (3) Residual connections and layer normalization stabilize train- ing across deep layers, preventing gradient vanishing in deeper networks.
2.3 Adaptive Fusion and Prediction Gated Fusion Mechanism: Fixed-weight fusion (e.g., simple concate- nation) fails when spatial or temporal signals dominate in different scenarios. We introduce a learnable gating mechanism that dynam- ically balances contributions based on input features:
g = 휎 Wg [FGAT∥FTCN] + bg  Ffused = g ⊙FGAT + (1 −g) ⊙FTCN (4) where 휎is the sigmoid function, ⊙denotes element-wise multi- plication, and g ∈[0, 1]d represents learned gates. Wheng →1, the model emphasizes graph features (useful during supply dis- ruptions); when g →0, temporal patterns dominate (e.g., during regular seasonal cycles).
Loss Function and Training: We optimize mean absolute per- centage error (MAPE) combined with smooth L1 loss for robust training:
L = 1 NH N Õ i=1 H Õ t=1 yt i −ˆyt i yt i + 휆· SmoothL1  yt i, ˆyt i  (5) where 휆=0.1 balances the two terms. The model is trained end-to- end using Adam optimizer with learning rate 0.001 for 100 epochs, with early stopping based on validation MAPE. As detailed in Table 1, we carefully tune hyperparameters to balance model capacity and generalization.All architectural and training hyperparameters are detailed in Table 1, which were selected through systematic grid search to optimize the trade-off between model expressiveness and generalization.
3 Results and Analysis 3.1 Overall Performance Comparison We evaluate GAT-TCN against six baseline methods on three datasets: Aircraft (120 nodes, 36 months), Automotive (85 nodes, 24 months), and Electronics (200 nodes, 48 months). Baselines in- clude traditional methods (ARIMA, XGBoost), deep learning models (LSTM, GRU), and graph-based approaches (GCN-LSTM, DCRNN).
All models are trained with identical train/validation/test splits 724

<!-- page 4 -->

EDAI 2025, November 14–16, 2025, Changsha, China Benli Li Table 2: Performance Comparison on Multi-step Forecasting (Lower is Better) Model Aircraft (MAPE %) Automotive (MAPE %) Electronics (MAPE %) Avg.
Improvement 1-step 3-step 7-step 1-step 3-step 7-step 1-step 3-step 7-step vs Best Baseline ARIMA 24.6 31.8 42.3 28.3 35.7 48.2 22.9 29.4 39.1 -89.4% XGBoost 21.3 28.5 38.6 24.7 31.2 42.8 19.8 26.3 35.7 -71.2% LSTM 18.7 24.9 34.2 21.5 27.8 38.4 17.2 23.6 32.1 -58.3% GRU 18.2 24.3 33.5 20.9 27.1 37.6 16.8 23.1 31.4 -56.1% GCN-LSTM 16.4 22.1 30.8 18.7 24.6 34.2 15.3 21.2 28.9 -42.7% DCRNN 15.1 20.3 28.4 17.2 22.9 31.7 14.1 19.6 26.8 -38.2% GAT-TCN 12.8 17.2 23.1 14.6 19.4 25.8 11.9 16.5 21.7 Baseline Improvement 15.2% 15.3% 18.7% 15.1% 15.3% 18.6% 15.6% 15.8% 19.0% 15.3% avg Note: Improvement calculated relative to DCRNN (best baseline). Bold indicates best performance.
Figure 2: Multi-step Forecasting MAPE Comparison (70%/10%/20%) and evaluated on 1-step, 3-step, and 7-step ahead forecasts.
Table 2 presents the quantitative comparison across all datasets.
GAT-TCN consistently outperforms baselines, achieving 15.3% av- erage MAPE reduction compared to the best baseline (DCRNN).
The improvement is most pronounced in long-term forecasting (7-step ahead: 18.7% MAPE reduction), demonstrating the effec- tiveness of adaptive fusion in handling complex spatiotemporal dependencies. Notably, GAT-TCN maintains stable performance across different forecast horizons, while baseline methods show significant degradation beyond 3-step predictions.
Figure 2 visualizes the forecasting accuracy across different hori- zons using a grouped bar chart. The consistent gap between GAT- TCN and baselines demonstrates the robustness of our approach.
Particularly, the widening gap at 7-step forecasts highlights the advantage of temporal convolutional networks in capturing long- range dependencies, while the adaptive fusion mechanism prevents error accumulation that plagues sequential models like LSTM.
3.2 Ablation Study and Component Analysis To validate the contribution of each component, we conduct ab- lation experiments by systematically removing or replacing key modules. Table 3 reports results on the Aircraft dataset (similar patterns observed on other datasets). We compare five variants: (1) GAT-only: removes TCN, uses only graph attention; (2) TCN-only:
removes GAT, uses only temporal convolutions; (3) Fixed Fusion:
replaces adaptive gating with fixed 0.5 weights; (4) No Attention:
replaces multi-head attention with simple GCN; (5) Full Model: our complete GAT-TCN framework.
Key findings from the ablation study:
Both GAT and TCN are essential: Removing either component causes 46-52% MAPE increase, confirming that spatial and temporal modeling are complementary. GAT-only fails to capture temporal trends, while TCN-only cannot leverage supply chain network structure.
Adaptive fusion outperforms fixed weighting: The 21.9% MAPE gap between fixed and adaptive fusion validates our hypothesis that optimal spatial-temporal balance varies across scenarios. During 725

<!-- page 5 -->

Supply Chain Demand Forecasting via Graph Attention Networks Integrated with Temporal Convolutional Networks EDAI 2025, November 14–16, 2025, Changsha, China Table 3: Ablation Study Results on Aircraft Dataset Model Variant MAPE (%) ↓ RMSE ↓ MAE ↓ R2 ↑ Inference Time (ms) GAT-only 19.4 8.73 6.52 0.781 12.3 TCN-only 18.7 8.41 6.28 0.798 9.7 Fixed Fusion (훼=0.5) 15.6 7.15 5.34 0.842 18.5 No Attention (GCN) 16.2 7.48 5.61 0.829 15.2 GAT-TCN (Full) 12.8 5.92 4.37 0.891 18.9 Performance Drop w/o GAT +46.1% +47.5% +43.7% -12.3% -48.7% Performance Drop w/o TCN +51.6% +42.0% +49.2% -10.4% -35.2% Performance Drop w/o Adaptive Fusion +21.9% +20.8% +22.2% -5.5% -2.1% Note: ↓indicates lower is better, ↑indicates higher is better. Performance drop calculated as (Variant - Full) / Full.
Figure 3: Multi-Head Attention Heatmap for Turbine Blade ComponentThe attention diversity validates our multi-head design:
different heads specialize in different dependency types, which are then aggregated for robust predictions. Interestingly, during a documented supply disruption event (Month 18-20 in Aircraft dataset), Head 4 automatically increased attention to alternative suppliers (weight increased from 0.12 to 0.47), demonstrating the model’s adaptive behavior.
supply disruptions, the model automatically increases GAT weight (avg. gate value: 0.68), while in stable periods it favors TCN (avg.
gate value: 0.34).
Multi-head attention is critical: Replacing GAT with simple GCN increases MAPE by 26.6%, demonstrating that different attention heads capture diverse dependency patterns (e.g., geographical prox- imity vs. functional similarity).
Minimal computational overhead: The full model adds only 2.1% inference time compared to fixed fusion, making adaptive gating highly efficient in practice.
3.3 Model Interpretability and Error Analysis Understanding why the model makes certain predictions is crucial for deployment in safety-critical spare parts management. We analyze two aspects: (1) attention weight patterns to reveal learned spatial dependencies, and (2) error distribution to identify failure modes.
Attention Mechanism Visualization: Figure 3 displays the at- tention heatmap for a critical aircraft component (turbine blade) across 8 attention heads. Each cell (i, j) represents the attention weight from node i to node j, with darker colors indicating stronger dependencies. We observe three key patterns:
Heads 1-3 (Geographical): Focus on spatially proximate nodes (e.g., same maintenance hub), forming block-diagonal structures.
This captures regional demand correlations due to shared environ- mental factors.
Heads 4-6 (Functional): Attend to functionally related compo- nents regardless of location (e.g., all hydraulic system parts), shown as scattered high-weight entries. This reflects cascading failure patterns.
Heads 7-8 (Temporal): Show time-varying attention that shifts during maintenance cycles, indicating the model learns seasonal dependencies through spatial attention.
726

<!-- page 6 -->

EDAI 2025, November 14–16, 2025, Changsha, China Benli Li GAT-TCN shows significantly tighter error distributions com- pared to DCRNN, especially for low-demand items which are no- toriously difficult to forecast due to intermittency. The median absolute error for low-demand items is 2.3 units (GAT-TCN) vs.
4.7 units (DCRNN), a 51% reduction. For high-demand items, both models perform well, but GAT-TCN exhibits fewer outliers (95th percentile error: 8.2 vs. 12.6 units), indicating better robustness to sudden demand spikes.
Failure Mode Analysis: We identify two primary failure scenar- ios: (1) Cold-start problem: For newly introduced parts with <3 months of history, MAPE increases to 28.4% (vs. 12.8% overall), as the model lacks sufficient temporal patterns. Transfer learning from similar components could mitigate this. (2) Black swan events:
Unpredictable disruptions (e.g., factory fire, geopolitical embargo) cause temporary MAPE spikes to 35-40%. However, GAT-TCN re- covers faster (2.1 months to baseline performance) than DCRNN (3.8 months) due to its ability to reroute attention to alternative supply paths.
Computational Efficiency: On a single NVIDIA V100 GPU, GAT- TCN processes 120 nodes with 36-month history in 18.9ms (Table 3), enabling real-time forecasting for networks up to 5,000 nodes.
Training converges in 45 minutes (100 epochs), making it practical for weekly model retraining in production environments.
3.4 Summary of Key Results This chapter demonstrates that GAT-TCN achieves state-of-the-art performance through three synergistic mechanisms: (1) Graph at- tention networks capture complex spatial dependencies beyond simple geographical proximity, (2) Temporal convolutional net- works efficiently model long-range temporal patterns with linear complexity, and (3) Adaptive fusion dynamically balances spatial and temporal signals based on input characteristics. The ablation study confirms that all components are essential, while attention visualization reveals interpretable dependency patterns that align with domain knowledge. Error analysis identifies specific failure modes (cold-start, black swan events) that point to future research directions, such as meta-learning for new parts and anomaly-aware forecasting.
4 Conclusion and Future Work 4.1 Conclusion This study presents a novel GAT-TCN framework for spare parts demand forecasting that effectively addresses the challenges of intermittent demand patterns and complex spatial-temporal de- pendencies in supply chain networks. Through comprehensive experiments on real-world datasets, our approach demonstrates significant improvements over traditional statistical methods and state-of-the-art deep learning baselines. The multi-head graph atten- tion mechanism successfully captures heterogeneous relationships among spare parts, including geographical proximity, functional similarity, and temporal correlations. Combined with temporal convolutional networks, the model achieves 23.7% MAPE reduction compared to the best baseline DCRNN, with particularly notable performance in low-demand scenarios where conventional meth- ods struggle. The interpretability analysis reveals that different attention heads specialize in distinct relationship types, providing valuable insights for inventory management decisions. These re- sults validate the effectiveness of integrating graph neural networks with temporal modeling for supply chain forecasting tasks.
4.2 Future Work Despite promising results, several directions warrant further inves- tigation. First, incorporating external factors such as equipment age, maintenance schedules, and seasonal patterns could enhance prediction accuracy. Second, extending the framework to handle multi-echelon supply chain networks with hierarchical structures represents an important research direction. Third, developing on- line learning mechanisms to adapt to evolving demand patterns in real-time would improve practical applicability. Fourth, inte- grating uncertainty quantification through probabilistic forecasting could provide confidence intervals for inventory planning. Finally, exploring federated learning approaches to enable collaborative forecasting across multiple organizations while preserving data privacy presents both technical challenges and significant practi- cal value. These extensions would advance both the theoretical foundations and practical deployment of AI-driven supply chain management systems.
References [1] Tien, N. H., Anh, D. B. H., & Thuc, T. D. (2019). Global supply chain and logistics management.
[2] Verma, P. (2024). Transforming Supply Chains Through AI: Demand Forecasting, Inventory Management, and Dynamic Optimization. Integrated Journal of Science and Technology, 1(3).
[3] Guo, L., Fang, W., Zhao, Q., & Wang, X. (2021). The hybrid PROPHET-SVR ap- proach for forecasting product time series demand with seasonality. Computers & Industrial Engineering, 161, 107598.
[4] Qiu, B., Wang, Z., Tang, Z., Liu, Z., Lu, D., Chen, C., & Chen, N. (2016). A multi- scale spatiotemporal modeling approach to explore vegetation dynamics patterns under global climate change. GIScience & Remote Sensing, 53(5), 596-613.
[5] Salinas, D., Flunkert, V., Gasthaus, J., & Januschowski, T. (2020). DeepAR: Proba- bilistic forecasting with autoregressive recurrent networks. International journal of forecasting, 36(3), 1181-1191.
[6] Huang, L., Huang, J., Chen, P., Li, H., & Cui, J. (2023). Long-term sequence depen- dency capture for spatiotemporal graph modeling. Knowledge-Based Systems, 278, 110818.
[7] Luo, S. (2022). RTS-GAT: Spatial Graph Attention-Based Spatio-Temporal Flow Prediction for Big Data Retailing. IEEE Access, 10, 133232-133243.
[8] Li, F., Guo, S., Han, F., Zhao, J., & Shen, F. (2024). Multi-scale dilated convolution network for long-term time series forecasting. arXiv preprint arXiv:2405.05499.
[9] Zheng, C., Fan, X., Pan, S., Jin, H., Peng, Z., Wu, Z., … & Yu, P. S. (2023). Spatio- temporal joint graph convolutional networks for traffic forecasting. IEEE Transac- tions on Knowledge and Data Engineering, 36(1), 372-385.
727
