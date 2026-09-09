# TGL_2023_temporal_edge_regression_UN_agriculture_trade

> 원본: `docs/research_desk/references/TGL_2023_temporal_edge_regression_UN_agriculture_trade.pdf` · SHA256 `d8e2b6bc7ce2162b…` · 12쪽 · 40,159자 · 변환 2026-09-09 (pdf_to_markdown.py)

## 목차(자동 복원)
  - Towards Temporal Edge Regression: A Case Study on (p.1)
  - Agriculture Trade Between Nations (p.1)
    - Abstract (p.1)
    - Introduction (p.1)
- arXiv:2308.07883v1  [cs.LG]  15 Aug 2023 (p.1)
    - Related Work (p.2)
    - Methodology (p.2)
    - Experiments (p.5)
    - Results (p.6)
    - Limitation and Future Work (p.8)
    - Conclusion (p.9)
    - Acknowledgements (p.9)
    - References (p.9)
    - A (p.11)
    - Dataset Information (p.11)
    - B (p.11)
    - Experimental Settings (p.11)
    - C (p.11)
    - More Results (p.11)

## 본문

<!-- page 1 -->


### Towards Temporal Edge Regression: A Case Study on


### Agriculture Trade Between Nations

Lekang Jiang1∗ Caiqi Zhang1∗ Farimah Poursafaei2,3 Shenyang Huang2,3 { lj408,cz391} @cam.ac.uk farimah.poursafaei@mila.quebec shenyang.huang@mail.mcgill.ca 1University of Cambridge, 2McGill University, 3Mila - Quebec AI Institute

#### Abstract

Recently, Graph Neural Networks (GNNs) have shown promising performance in tasks on dynamic graphs such as node classification, link prediction and graph regression. However, few work has studied the temporal edge regression task which has important real-world applications. In this paper, we explore the application of GNNs to edge regression tasks in both static and dynamic settings, focusing on predicting food and agriculture trade values between nations. We introduce three simple yet strong baselines and comprehensively evaluate one static and three dynamic GNN models using the UN Trade dataset. Our experimental results reveal that the baselines exhibit remarkably strong performance across various settings, highlighting the inadequacy of existing GNNs. We also find that TGN outperforms other GNN models, suggesting TGN is a more appropriate choice for edge regression tasks. Moreover, we note that the proportion of negative edges in the training samples significantly affects the test performance. The companion source code can be found at: https://github.com/scylj1/GNN_ Edge_Regression.
1

#### Introduction

Graph representation learning has gained significant attention in recent years due to its ability to model complex relationships and structures in various domains [1]. Graph Neural Networks (GNNs), as a core technique within this field, have shown remarkable success in various applications, ranging from social network analysis [2–4] to the biological field [5–7]. This growing interest has led to the development of various GNN architectures optimized for specific tasks and objectives.
Although most existing GNN models, such as GCN [8], GAT [9], GraphSAGE [10], and GIN [11], have been developed for static graphs, there is a growing interest in representation learning on dynamic graphs, where the graph structure changes over time. The temporal graph representation learning is particularly useful in modeling real-life dynamic systems, such as social networks, traffic networks, and biological systems, where the graph topology evolves as time passes [1]. Therefore, it is crucial to develop effective methods for modeling the dynamics of graph-structured data. Numerous works have focused on both discrete-time dynamic graphs [12–14] and continuous-time dynamic graphs [15–18].
However, there are few attempts on applying GNNs to edge regression tasks for dynamic net- works [19]. Most of the existing works have focused on node classification, link prediction, and graph classification tasks [1]. In this paper, we address this research gap by exploring the application of both static and dynamic GNNs to edge regression tasks on the UN Trade dataset [20], where food and agriculture trade values between nations are predicted. This real-life problem offers a unique opportunity to investigate the performance of GNNs in terms of edge regression, as the trade relationships between countries are naturally represented as a graph with time-varying edge weights.
Results of edge regression on this dataset not only improve the understanding of applying GNNs on edge regression but also assist in forecasting the future global food and agriculture market, which is crucial for policy making and resource allocation.
∗Equal contribution.

## arXiv:2308.07883v1  [cs.LG]  15 Aug 2023


<!-- page 2 -->

Towards Temporal Edge Regression One of the key observation is that among the GNN models, TGN achieves the best performance, indicating that temporal attention mechanisms and memory modules can better capture the evolving dynamics of the graph. Additionally, we observe that the percentage of negative edges in all training samples has a significant impact on the test performance. Overall, our work represents a step toward developing effective methods for modeling temporal edge regression tasks using GNNs.
Overall, this work has the following contributions:
• We propose three straightforward but strong baselines to compare the effectiveness of existing GNN models.
• We implement three normalization methods, three training strategies, and two evaluation criteria to optimize and measure the performance of the models.
• We conduct a thorough evaluation and analysis of one static and three dynamic GNN models using the UN Trade dataset. Our experiments demonstrate that the baselines achieve surprisingly strong performance across multiple settings, underscoring that existing GNNs are not sufficiently effective.
2

#### Related Work

Dynamic Graph Representation Learning. Aiming at learning node representations that evolve over time, dynamic graph representation learning is a rapidly developing field in recent years. Recently, several approaches have been proposed to address the challenge of dynamic graph representation learning, such as JODIE [15], DyRep [16], TGAT [17], and TGN [18]. Kazemi et al. [1] and Skarding et al. [21] provide detailed surveys of advances in representation learning on dynamic graphs and a detailed terminology of dynamic networks. However, according to the reported experiment results of the recent methods, they often achieve close to perfect performance for current link prediction tasks on dynamic graphs, which hinders researchers’ ability to evaluate if new models are superior [20, 22–24]. Therefore, to better compare the strengths and weaknesses of emergent dynamic graph neural networks, Poursafaei et al. [20] propose six new dynamic graph datasets in different domains with two more challenging negative sampling strategies. Our work thus focuses on the UN Trade dataset from [20] to investigate the existing temporal GNNs’ capabilities for edge regression tasks.
Edge Regression Tasks. According to the survey by Kazemi et al. [1], the main applications of dynamic graph representation learning include link prediction [15–18, 25], entity/relation prediction [15, 26, 27], recommender systems [28], time prediction [27], node classification [13, 29], and graph classification [30]. Despite the success of various models in achieving state-of-the-art results on the abovementioned tasks, to the best of our knowledge, there has been little research on the edge regression task. One reason for this is the added complexity of edge regression, which involves predicting a continuous value rather than a binary or categorical label. Additionally, there is few datasets available for the edge regression task, posing challenges in evaluating and comparing different algorithms for edge regression. Thus, our work aims to address the gap in the research on edge regression tasks by utilizing the UN Trade dataset [20].
3

#### Methodology

3.1 Task Formulation Temporal Edge Regression Task.
Following the definition from [20], a dynamic graph can be represented as timestamped edge streams - triplets of source, destination, times- tamp, i.e.
G = {(s0, d0, t0) , (s1, d1, t1) , . . . , (sT , dT , T)} where the timestamps are ordered (0 ≤t1 ≤t2 ≤. . . ≤tsplit ≤. . . ≤T) . We denote the set of all nodes in G at time tn by V(tn) and let E(tn) be the set of all edges in G at time tn. Consequently, E(sn, tn) is the set of all edges in E(tn) that originate from node sn at time tn. We investigate the task of predicting the exact weight of an edge between a node pair in the future, i.e. w(si, dj, tn). Figure 1 shows an example of our temporal edge regression task.
Temporal Edge Classification Task. Due to the inherent difficulty of the edge regression task, an alternative approach to predict the trading value is to convert it to a classification problem.
In this approach, the range of edge values is partitioned into n intervals, with each interval cor- responding to a class. For instance, the intervals could be defined as follows in the log space:
2

<!-- page 3 -->

Towards Temporal Edge Regression (0, 1], (1, 10], (10, 102], (102, 103], . . . , (10n−1, 10n]. By transforming the regression task to a mag- nitude classification task, the difficulty of the prediction task is reduced. The goal of the classification task is now to evaluate how well existing GNNs can estimate the order of magnitude of the edge weights (i.e. c(si, dj, tn)), rather than predicting the exact values of edges.
w(2, 4, t8) c(2, 4, t8) 1 3 2 4 5 t8 t1 t5 t3 t4 t2 t6 t7 z2(t8) z4(t8) GNN Decoder (MLP) Dynamic Graph Figure 1: Example of a GNN encoder ingesting a dynamic graph with seven visible edges (with timestamps t1 to t7), with the goal of predicting the future weight w(2, 4, t8) (or weight class c(2, 4, t8)) between nodes 2 and 4 at time t8. z2(t8) and z4(t8) are the embeddings for nodes 2 and 4 at time t8.
3.2 Normalization Normalization involves scaling the weights so that they fall within a specific range or have a particular statistical distribution. In the context of the UN Trade dataset, the trade values between countries vary significantly. Thus, normalizing the weights is beneficial for the performance of these models by ensuring that the input data falls within a fixed / expected range. We explore the following three normalization methods in this work:
Min-max normalization. It scales the values of a dataset from their natural range into a standard range (e.g. from a to b). The formula for min-max normalization can be expressed mathematically as:
w∗= a + (w −min(x))(b −a) max(w) −min(w) (1) where w is the original weight, wnorm is the normalized value, min(w) and max(w) are the minimum and maximum values in the dataset, respectively, and a and b are the lower and upper bounds of the desired range respectively.
Log normalization. In log normalization, it takes the logarithm of the values in a dataset. The formula for log normalization can be expressed simply as:
w∗= log(w) (2) Log normalization is commonly used when the data has a wide range of values or when the distribution of values is highly skewed. By taking the logarithm of the values, the range of values can be compressed, and the distribution can be transformed into a more symmetric shape.
Node degree normalization. While min-max and log normalization are applied across all timestamps, we introduce a novel normalization method named node degree normalization for each timestamp. For a given timestamp tn and node sn, the proposed normalization method divides all weights originating from node sn by their sum. Specifically, this method divides the weight w(sn, dm, tn) of each edge between node sn and destination node dm at time tn by the sum of the raw weights of all edges originating from sn at time tn. This results in the normalized weight wnorm(sn, dm, tn) for each edge, calculated as:
w∗(sn, dm, tn) = w(sn, dm, tn) P dk∈V(sn,tn) w(sn, dk, tn) (3) 3

<!-- page 4 -->

Towards Temporal Edge Regression where V(sn, tn) is the set of all nodes at timestamp tn that originate from sn. This normalization method ensures that the weights of edges originating from node sn sum up to 1 at any given time, facilitating comparison of the relative strengths of different connections originating from that node.
By utilizing node degree normalization, the model does not predict the exact trade values anymore but rather predicts the proportion of the total trade value of a country exporting to another country in following years.
3.3 Models Baselines. In this study, we implement three baseline methods served as benchmarks to compare with different GNN models and evaluate their effectiveness.
• Mean/Most. The Mean baseline is applied in the edge regression task, which predicts all edges using the average value of all inputs.
w = 1 np p X j=1 n X i=1 wi(tj) (4) where t is the timestamp, tp is the last timestamp in the training set, and n is the number of positive edges at a given snapshot. In the classification task, a similar Most baseline is applied to predict the edge weights using the class which appears the most frequently in the training dataset.
c = mode(c1, c2, ..., cn) (5) • Persistence Forecast. It predicts each edge using the last seen value (class) of that edge in the training set.
w(i, j, tq) = w(i, j, tp) (6) where tq is the current timestamp and tp is the timestamp of the most recent record of the edge between node i and j.
• Historical Average. It predicts each edge’s weight by computing the average value of all the weights observed for that edge in the training set.
w(i, j, tq) = 1 p p X k=1 w(i, j, tk) (7) Static GNN. We implement GCN [8] as a representative static GNN model for comparison. As GCN cannot deal with temporal information, we construct collapsed static graphs for training and testing in the following steps. We first develop fully-connected graphs at each timestamp by filling the non-existing edges with the value zero. Second, compressing all training graphs from t1 to tp into a single static graph, where the node features are a list of timestamps (t1, t2, . . . , tp) and edge features are a list of edge values at each timestamp (w1, w2, . . . , wp), as shown in Figure 2. The same process is also applied to validation and test set. Then, we transform the node features and edge features of length p in the training set to match the length q of the test set using the following equation. We split the feature vectors of length p into q groups equally, and then calculate the average value of each group to obtain the transformed result. After pre-processing, we obtain 3 static graphs that have the same dimensions of features and outputs for training, validation and testing.
w =    1 m m X j=1 w(i−1)m+j | i ∈[1, p]    (8) where m is the number of elements in each group.
Dynamic GNNs. The three dynamic GNNs modified for the task of temporal edge regression are as follows:
4

<!-- page 5 -->

Towards Temporal Edge Regression 1 3 2 4 5 … 𝑡𝑝 1 3 2 4 5 (𝑡1, 𝑡2, … 𝑡𝑝) (𝑤1, 𝑤2, … 𝑤𝑝) 1 3 2 4 5 (𝑡1, 𝑡2, … 𝑡𝑞) (𝑤1, 𝑤2, … 𝑤𝑞) (a)                                                                   (b) (c) Figure 2: Illustration of transforming temporal graph to static graph for GCN training and testing; (a) fully-connected graph at each timestamp, (b) collapsed static graph with feature vectors of length p, (c) adjusted static graph with feature vectors of length q.
• JODIE [15]: It is designed for bipartite networks of instantaneous user-item interactions. It consists of an update operation and a projection operation. The update operation utilizes two coupled RNNs to recursively update the representation of the users and items. The projection operation predicts the future representation of a node while considering the elapsed time since its last interaction.
• DyRep [16]: It utilizes a specialized RNN to update node representations when a new edge is observed. To compute neighbor weights at each time step, DyRep employs a temporal attention mechanism that is parameterized on the recurrent architecture.
• TGN [18]: consists of five key modules: (1) Memory, which stores the historical data of each node and facilitates the retention of long-term dependencies; (2) Message function, which updates the memory of each node based on the messages generated when an event is observed; (3) Message aggregator, which combines multiple messages involving a single node; (4) Memory updater, which updates the memory of a node based on the aggregated messages; and (5) Embedding, which generates representations of nodes by considering the node’s memory and its associated edge and node features.
4

#### Experiments

4.1 Dataset The United Nations food and agriculture trade dataset is originally collected, processed, and dissemi- nated by the Food and Agriculture Organization of the United Nations [20]. The data is primarily provided by UNSD, Eurostat, and other national authorities as required. The trade data contains statistics on all food and agriculture products that are imported or exported annually by all countries worldwide. Specifically, in the UN Trade dataset, the graph G represents a weighted, directed food and agriculture trading graph among 181 nations, spanning from 1986 to 2017, with around 500,000 edges. The edge weights indicate the total sum of normalized agriculture import or export values between two countries. This dataset provides a valuable resource for studying global food and agriculture trade and can be used in a variety of applications, including graph neural network models for predicting future trade patterns. The distribution of edge weight values in UN Trade dataset is illustrated in Appendix A (Figure 4).
4.2 Training Strategies As few previous works have focused on edge regression tasks, it is unclear how to train models to achieve optimal results. Thus, we utilize the following three training strategies to compare their performance, which are demonstrated in Figure 3 respectively.
Training with negative sampling. Negative sampling refers to randomly selecting a negative edge for each positive edge during training. It reduces the computational complexity of training while still allowing the model to learn from negative samples. This is the standard training strategies used for link prediction task for GNNs [1, 16, 18, 24].
Training on positive edges. We refer positive edges to those edges that indeed exist between two nodes (i.e. with positive edge values). A negative edge is a node pair where an edge hasn’t been 5

<!-- page 6 -->

Towards Temporal Edge Regression observed in the temporal graph. The advantage of training solely on positive edges is that it simplifies and accelerates the training process, and the model can better capture the features on positive edges to make precise predictions.
Training on all node pairs. To train on all node pairs, we construct a fully-connected graph for each snapshot, where each positive edge is of its original value, and negative edges are set to zero. The advantage of this training strategy is that the model can learn from the full range of relationships presented in the network. A potential risk is that this approach can be computationally expensive (with complexity O(|V(tn)|2) ) and memory-intensive, particularly for large networks.
1 3 2 4 5 1 3 2 4 5 1 3 2 4 5 (a)                                                   (b)                                                  (c) Figure 3: Three training strategies. Solid lines represent edges with positive values that actually exist in the data set (positive edges). Dashed lines represent virtual edges with a weight of zero (negative edges). (a) train on positive edges, (b) train on all edges, (c) train with negative sampling.
4.3 Evaluation Strategies Evaluation with negative sampling. For all positive edges in the test set, we randomly sample the same number of negative edges for evaluation, which is consistent with past papers [18, 20].
Evaluating on both positive and negative edges can assess the model’s overall performance, and we refer this type of evaluation to the Overall evaluation.
Evaluation on positive edges. We argue that in real-world edge regression applications, predicting negative edges is sometimes not as crucial as predicting positive edges. For example, people may be more concerned about the actual trade value between two countries rather than focusing on countries with no trade history. Therefore, we propose the Positive evaluation to focus on the more important and relevant edges in the graph, which is closer to real-life scenarios.
Old and new nodes. In temporal graphs, new nodes may emerge over time, like in social networks.
Following [18]’s experiments, we evaluate edges between both old and new nodes (unseen in the training set). Although the emergence of a new nation is rare in our case, we simulate this situation to provide a more comprehensive evaluation of the edge regression task.
5

#### Results

5.1 Temporal Edge Regression Task In this section, we discuss the experiment results on the temporal edge regression task. The predicted MSE losses on edges for old nodes are listed in Table 1. As the creation of new nations is rare, we report the results involving new nodes in Appendix C (Table 3). The observations and findings of new nodes are similar to old nodes.
Comparison with baselines. The results show that the Persistence Forecast baseline exhibits the best performance for most cases (4/6), and the Historical Averages baseline reaches the best outcome of 1.360 on Overall MSE loss using min-max normalization (1/6). This observation reveals that our baselines are strong and existing GNNs are not yet able to outperform the baselines, highlighting the research gap in edge regression tasks. There are several reasons for this result: first, the food and agriculture trade values between the countries are normally stable over time, leading to a strong performance of the Persistence Forecast baseline. Second, the test set only contains a relatively short period of time (4 years), and significant value fluctuations are unlikely to occur within this period.
Third, the training data (22 timestamps) may be insufficient for complex models to acquire a full understanding of the underlying patterns.
6

<!-- page 7 -->

Towards Temporal Edge Regression Table 1: Loss with standard deviation (old nodes). Numbers in red indicate the best results for all methods, and numbers in bold are the best results among GNNs.
Log normalization Min-max normalization (10−2) Node degree normalization (10−3) Positive MSE Overall MSE Positive MSE Overall MSE Positive MSE Overall MSE Baselines Mean 2.762 5.504 3.933 1.979 2.644 1.429 Persistence Forecast 0.608 4.135 0.104 2.125 1.267 0.943 Historical Average 0.833 3.634 0.959 1.360 1.667 1.224 Static GNN GCN 6.774 (0.56) 4.041 (0.41) 106.1 (39.3) 67.18 (26.1) 1025 (406.) 656.0 (261.) Dynamic GNNs Train on all node pairs TGN 9.014 (0.05) 4.773 (0.12) 3.974 (0.00) 1.988 (0.00) 2.687 (0.00) 1.344 (0.00) JODIE 8.446 (0.18) 4.580 (0.07) 12.92 (10.6) 364.8 (464.) 41.41 (36.7) 51.75 (28.8) DyRep 8.875 (0.10) 4.777 (0.04) 3.972 (0.00) 1.988 (0.00) 2.600 (0.00) 1.360 (0.00) Train on positive edges TGN 1.810 (0.05) 4.241 (0.20) 3.960 (0.00) 1.983 (0.00) 2.479 (0.03) 1.355 (0.03) JODIE 2.808 (0.11) 24.09 (22.3) 8.250 (5.98) 910.1 (128.) 7.519 (4.06) 169.5 (105.) DyRep 3.061 (0.22) 3.831 (0.16) 3.961 (0.01) 1.994 (0.01) 2.894 (0.19) 2.002 (0.30) Train with negative sampling TGN 3.802 (0.09) 2.959 (0.03) 3.965 (0.00) 1.982 (0.00) 2.522 (0.07) 1.342 (0.05) JODIE 5.009 (0.11) 4.815 (0.33) 4.157 (0.19) 31.48 (25.2) 11.87 (3.62) 29.07 (5.38) DyRep 5.292 (0.21) 3.637 (0.07) 4.022 (0.07) 2.115 (0.09) 2.832 (0.01) 3.234 (0.79) Comparisons among GNNs. Regarding the performance of GNN models, TGN trained with negative sampling demonstrates the best Overall MSE loss of 2.959 compared to all the other models. This may be because TGN trained with an appropriate number of negative edges, can better differentiate negative edges, resulting in lower Overall MSE loss. It suggests that TGN is a feasible approach for temporal edge regression tasks as it can learn temporal dependencies and graph structure to improve predictions. Another possible reason is that TGN employs temporal attention mechanisms and specialized memory modules, which capture the evolving relationships and dynamics of the network over time more effectively. This may result in more accurate predictions and a deeper insight of the underlying temporal patterns.
Notably, although JODIE is effective in predicting future interactions [15], it may not be suitable for edge regression tasks because its performance is much worse and more unstable than other models in some situations. For example, it results in the Overall MSE loss of 910.1 with a standard deviation of 128 when training on positive edges. It is worth mentioning that dynamic GNNs typically exhibit superior performance compared to static GCN because of their ability to leverage the temporal characteristics of the graph effectively.
Influence of training strategies. Our findings show that no GNN model trained on all edges achieves optimal results on Positive and Overall MSE loss. We hypothesize that this is due to the sparsity of the graph, making it challenging for models to learn meaningful representations from training on all edges, resulting in worse performance. In contrast, we observe that TGN trained on positive edges achieves the best Positve MSE loss in all three normalization methods, and TGN trained with negative sampling demonstrates the best Overall MSE loss.
Furthermore, we note a trade-off between the Overall MSE loss and Positive MSE loss when different numbers of negative edges engaged in training. Training with more negative edges leads to a lower Overall MSE loss and a higher Positive MSE loss. For instance, when using log normalization, training with negative sampling can reduce the Overall MSE loss from 4.241 to 2.959, while increasing the Positive MSE loss from 1.810 to 3.802. One future research direction is to determine the optimal percentage of negative edges used during training to achieve a balanced regression performance between positive and negative edges.
Influence of normalization methods. Although both log and min-max normalization scale the original edge values to a standard range to facilitate fast and effective training of GNNs, we argue that log normalization is more suitable for training GNNs for two reasons. Firstly, the loss values using log normalization are more sensible, as GCN and JODIE perform poorly and unstably when 7

<!-- page 8 -->

Towards Temporal Edge Regression Table 2: Accuracy and F1 score (%) with standard deviation (old nodes). Numbers in red indicate the best results for all methods, and numbers in bold are the best results among GNNs.
Positive Accuracy Overall Accuracy Positive F1 Overall F1 Baselines Most 22.14 11.07 8.21 2.27 Persistence forecast 60.97 50.00 62.31 50.68 Dynamic GNNs Train on postive edges TGN 32.19 (0.85) 16.10 (0.43) 29.95 (1.04) 10.53 (0.40) JODIE 22.03 (1.32) 11.01 (0.66) 14.02 (2.73) 4.61 (1.12) DYREP 23.04 (0.96) 11.52 (0.48) 16.20 (2.17) 5.28 (0.84) Train with negative sampling TGN 12.91 (0.98) 50.37 (0.24) 14.81 (0.81) 43.01 (0.51) JODIE 0.38 (0.01) 49.47 (0.67) 0.33 (0.01) 33.39 (0.33) DYREP 0.07 (0.08) 50.01 (0.01) 0.04 (0.04) 33.38 (0.06) using min-max normalization, producing loss values that are hundreds of times larger than the baselines. Secondly, TGN outperforms the baselines in terms of Overall MSE loss only when using log normalization. A possible explanation is that log normalization can create a more uniform data distribution with less skewness and fewer outliers, facilitating effective training on edge regression tasks.
Unlike log and min-max normalization, node degree normalization enables the model to predict a percentage value of the trade flow between countries, rather than an absolute value. The purpose of this novel normalization approach is to demonstrate that specialized normalization based on graphs can offer another perspective on the dataset. We encourage researchers to explore other normalization methods that could improve the model’s performance in edge regression tasks.
5.2 Temporal Edge Classification Task Table 2 reports the accuracy and F1 scores of the temporal edge classification task involving only old nodes. The classification results containing new nodes are reported in Appendix C (Table 4), which is similar to the results with old nodes. In this task, we focus only on dynamic GNNs trained on positive edges or with negative sampling, because we find that in the regression task, dynamic GNNs outperform static GCN, and training on all edges often leads to unsatisfactory results. Note that historical average is not applicable in this classification task.
Compared to the regression task, the classification task is inherently easier, and the evaluation metrics (i.e. accuracy and F1 score) are also more intuitive. The Persistence Forecast baseline remains powerful, outperforming GNNs in Positive accuracy (60.97%), Positive F1 (62.31%), and Overall F1 score (50.68%). Moreover, TGN performs much better than JODIE and DyRep, especially in terms of Positive accuracy and F1, with more than 10% absolute improvement in average. This indicates that TGN is more effective at capturing temporal dependencies and evolving patterns of dynamic graphs.
Consistent with the regression results, sampling more negative edges for training TGN can enhance the overall accuracy from 16.10% to 50.37%, but diminish the ability to classify positive edges, reducing it from 32.19% to 12.91%. Hence, selecting appropriate sampling methods is crucial to achieve a balance between positive and overall performance.
6

#### Limitation and Future Work

We acknowledge several limitations of our work. Firstly, we did not conduct hyper-parameter searches to optimize the performance of the GNNs. Instead, we used default values for the hyper-parameters, which may not be optimal for all datasets and models. Future work can investigate the effect of different hyper-parameters on the performance of GNN models. Secondly, we did not explore enough model structures to compare their performance, such as temporal GNNs like TGAT [17] and static 8

<!-- page 9 -->

Towards Temporal Edge Regression GNNs like GIN [31]. Additionally, we only evaluated the models on the UN Trade dataset due to the lack of publicly available dynamic graph datasets. Therefore, the generalizability of the GNN models to other dynamic graphs remains to be investigated in future work. Another limitation of the UN Trade dataset is that it only covers a period of around 30 years, which limits the number of timestamps available for training and evaluation. Future work could evaluate the effectiveness of the proposed methods with more timestamps to provide more comprehensive findings and analysis. It is worth noting that a concurrent work [24] provides more relevant datasets.
7

#### Conclusion

This work evaluates the performance of existing GNNs on edge regression tasks. We formulate the temporal edge regression task, predicting the actual edge weight or its magnitude in the graph. Three normalization methods are designed and applied to scale the original inputs for smooth training. We propose three simple but powerful baselines, which outperform most GNNs, indicating the research gap in leveraging GNNs for edge regression tasks. We apply both static and dynamic GNNs to this task to make a comprehensive evaluation. It shows that TGN outperforms the other GNN models, indicating its superiority in modeling temporal dynamics and dependencies of graph structures.
Additionally, our analysis reveals that the proportion of negative edges in the training samples has a significant impact on test performance. Our work represents a step forward in modeling edge regression in dynamic graphs, and we call for future research to explore the potential of GNNs in addressing more complex temporal edge regression tasks.

#### Acknowledgements

We would like to thank Prof. Pietro Liò and Dr. Petar Veliˇckovi´c for their kind support on this project.
This study would not have been possible without their generous help.

#### References

[1] Seyed Mehran Kazemi, Rishab Goel, Kshitij Jain, Ivan Kobyzev, Akshay Sethi, Peter Forsyth, and Pascal Poupart. Representation learning for dynamic graphs: A survey. The Journal of Machine Learning Research, 21(1):2648–2720, 2020. 1, 2, 5 [2] Rex Ying, Ruining He, Kaifeng Chen, Pong Eksombatchai, William L Hamilton, and Jure Leskovec. Graph convolutional neural networks for web-scale recommender systems. In Proceedings of the 24th ACM SIGKDD international conference on knowledge discovery & data mining, pages 974–983, 2018. 1 [3] Federico Monti, Fabrizio Frasca, Davide Eynard, Damon Mannion, and Michael M Bron- stein. Fake news detection on social media using geometric deep learning. arXiv preprint arXiv:1902.06673, 2019.
[4] Fabrizio Frasca, Emanuele Rossi, Davide Eynard, Ben Chamberlain, Michael Bronstein, and Federico Monti.
Sign: Scalable inception graph neural networks.
arXiv preprint arXiv:2004.11198, 2020. 1 [5] Marinka Zitnik, Monica Agrawal, and Jure Leskovec. Modeling polypharmacy side effects with graph convolutional networks. Bioinformatics, 34(13):i457–i466, 2018. 1 [6] Xiaoxiao Li, Yuan Zhou, Nicha Dvornek, Muhan Zhang, Siyuan Gao, Juntang Zhuang, Dustin Scheinost, Lawrence H Staib, Pamela Ventola, and James S Duncan. Braingnn: Interpretable brain graph neural network for fmri analysis. Medical Image Analysis, 74:102233, 2021.
[7] Yongxiang Huang and Albert CS Chung. Edge-variational graph convolutional networks for uncertainty-aware disease prediction. In Medical Image Computing and Computer Assisted Intervention–MICCAI 2020: 23rd International Conference, Lima, Peru, October 4–8, 2020, Proceedings, Part VII 23, pages 562–572. Springer, 2020. 1 [8] Thomas N Kipf and Max Welling. Semi-supervised classification with graph convolutional networks. arXiv preprint arXiv:1609.02907, 2016. 1, 4 [9] Petar Veliˇckovi´c, Guillem Cucurull, Arantxa Casanova, Adriana Romero, Pietro Lio, and Yoshua Bengio. Graph attention networks. arXiv preprint arXiv:1710.10903, 2017. 1 9

<!-- page 10 -->

Towards Temporal Edge Regression [10] Will Hamilton, Zhitao Ying, and Jure Leskovec. Inductive representation learning on large graphs. Advances in neural information processing systems, 30, 2017. 1 [11] Keyulu Xu, Weihua Hu, Jure Leskovec, and Stefanie Jegelka. How powerful are graph neural networks? arXiv preprint arXiv:1810.00826, 2018. 1 [12] Wenchao Yu, Wei Cheng, Charu C Aggarwal, Kai Zhang, Haifeng Chen, and Wei Wang.
Netwalk: A flexible deep embedding approach for anomaly detection in dynamic networks. In Proceedings of the 24th ACM SIGKDD international conference on knowledge discovery & data mining, pages 2672–2681, 2018. 1 [13] Aldo Pareja, Giacomo Domeniconi, Jie Chen, Tengfei Ma, Toyotaro Suzumura, Hiroki Kaneza- shi, Tim Kaler, Tao Schardl, and Charles Leiserson. Evolvegcn: Evolving graph convolutional networks for dynamic graphs. In Proceedings of the AAAI conference on artificial intelligence, volume 34-04, pages 5363–5370, 2020. 2 [14] Aravind Sankar, Yanhong Wu, Liang Gou, Wei Zhang, and Hao Yang. Dysat: Deep neural representation learning on dynamic graphs via self-attention networks. In Proceedings of the 13th international conference on web search and data mining, pages 519–527, 2020. 1 [15] Srijan Kumar, Xikun Zhang, and Jure Leskovec. Predicting dynamic embedding trajectory in temporal interaction networks. In Proceedings of the 25th ACM SIGKDD international conference on knowledge discovery & data mining, pages 1269–1278, 2019. 1, 2, 5, 7 [16] Rakshit Trivedi, Mehrdad Farajtabar, Prasenjeet Biswal, and Hongyuan Zha. Dyrep: Learning representations over dynamic graphs. In International conference on learning representations, 2019. 2, 5 [17] Da Xu, Chuanwei Ruan, Evren Korpeoglu, Sushant Kumar, and Kannan Achan. Inductive representation learning on temporal graphs. arXiv preprint arXiv:2002.07962, 2020. 2, 8 [18] Emanuele Rossi, Ben Chamberlain, Fabrizio Frasca, Davide Eynard, Federico Monti, and Michael Bronstein. Temporal graph networks for deep learning on dynamic graphs. arXiv preprint arXiv:2006.10637, 2020. 1, 2, 5, 6 [19] Kartik Sharma, Mohit Raghavendra, Yeon Chang Lee, Srijan Kumar, et al. Representation learning in continuous-time dynamic signed networks. arXiv e-prints, pages arXiv–2207, 2022.
1 [20] Farimah Poursafaei, Shenyang Huang, Kellin Pelrine, and Reihaneh Rabbany. Towards better evaluation for dynamic link prediction. arXiv preprint arXiv:2207.10128, 2022. 1, 2, 5, 6, 11 [21] Joakim Skarding, Bogdan Gabrys, and Katarzyna Musial. Foundations and modeling of dynamic networks using dynamic graph neural networks: A survey. IEEE Access, 9:79143–79168, 2021.
2 [22] Amauri Souza, Diego Mesquita, Samuel Kaski, and Vikas Garg. Provably expressive temporal graph networks. Advances in Neural Information Processing Systems, 35:32257–32269, 2022.
2 [23] Weilin Cong, Si Zhang, Jian Kang, Baichuan Yuan, Hao Wu, Xin Zhou, Hanghang Tong, and Mehrdad Mahdavi. Do we really need complicated model architectures for temporal networks?
In The Eleventh International Conference on Learning Representations, 2022.
[24] Shenyang Huang, Farimah Poursafaei, Jacob Danovitch, Matthias Fey, Weihua Hu, Emanuele Rossi, Jure Leskovec, Michael Bronstein, Guillaume Rabusseau, and Reihaneh Rabbany. Tempo- ral graph benchmark for machine learning on temporal graphs. arXiv preprint arXiv:2307.01026, 2023. 2, 5, 9 [25] Jinyin Chen, Jian Zhang, Xuanheng Xu, Chenbo Fu, Dan Zhang, Qingpeng Zhang, and Qi Xuan.
E-lstm-d: A deep learning framework for dynamic network link prediction. IEEE Transactions on Systems, Man, and Cybernetics: Systems, 51(6):3699–3712, 2019. 2 [26] Julien Leblay and Melisachew Wudage Chekol. Deriving validity time in knowledge graph. In Companion proceedings of the the web conference 2018, pages 1771–1776, 2018. 2 [27] Shib Sankar Dasgupta, Swayambhu Nath Ray, and Partha P Talukdar. Hyte: Hyperplane-based temporally aware knowledge graph embedding. In EMNLP, pages 2001–2011, 2018. 2 [28] Srijan Kumar, Xikun Zhang, and Jure Leskovec. Learning dynamic embeddings from temporal interactions. arXiv preprint arXiv:1812.02289, 2018. 2 10

<!-- page 11 -->

Towards Temporal Edge Regression [29] Koya Sato, Mizuki Oka, Alain Barrat, and Ciro Cattuto. Dyane: dynamics-aware node embed- ding for temporal networks. arXiv preprint arXiv:1909.05976, 2019. 2 [30] Aynaz Taheri, Kevin Gimpel, and Tanya Berger-Wolf. Learning to represent the evolution of dynamic graphs with recurrent models. In Companion proceedings of the 2019 world wide web conference, pages 301–307, 2019. 2 [31] Keyulu Xu, Weihua Hu, Jure Leskovec, and Stefanie Jegelka. How powerful are graph neural networks?
In International Conference on Learning Representations, 2019. URL https:
//openreview.net/forum?id=ryGs6iA5Km. 9

#### A


#### Dataset Information

The distribution of UN Trade dataset is illustrated in Figure 4.
0 1 E1 E2 E3 E4 E5 E6 E7 E8 E9 0 2 4 6 8 10 12 Number of edges (E4) Figure 4: The distribution of edge weights in the UN Trade dataset.

#### B


#### Experimental Settings

We use the default hyper-parameters in the original paper [20], which uses dynamic GNNs for link predictions in the UNTrade dataset. The Adam optimizer with a learning rate of 10−4 and a batch size of 200 is used. The number of epochs is set to 50, and an early stopping method is adopted with patience of 5. The dropout rate is configured to 0.1, and two attention heads are used. To eliminate randomness, we conduct all experiments with three random seeds to report the average values and standard deviations. Dynamic GNNs take approximately 30 minutes for each run on a single A100 GPU, while static GCN can finish one round in a minute on CPU.

#### C


#### More Results

The experimental results including new nodes are reported below for the readers to have a more comprehensive understanding of GNNs on edge regression tasks.
11

<!-- page 12 -->

Towards Temporal Edge Regression Table 3: Loss with standard deviation (new nodes). Numbers in red mean the best results for all methods, and numbers in bold are the best results for GNNs.
Log normalization Min-max normalization (10−2) Node degree normalization (10−3) Positive MSE Overall MSE Positive MSE Overall MSE Positive MSE Overall MSE Baselines Mean 2.785 5.516 3.880 1.952 3.218 1.716 Persistence forecast 0.546 4.833 0.129 1.690 1.402 1.069 Historical average 0.678 4.344 1.167 1.167 1.536 1.097 Dynamic GNNs Train on all node pairs TGN 9.043 (0.33) 4.881 (0.01) 3.958 (0.00) 1.980 (0.00) 3.055 (0.00) 1.530 (0.00) JODIE 9.169 (0.07) 5.146 (0.09) 37.19 (40.6) 144.6 (105.) 144.8 (128.) 117.2 (90.3) DyRep 9.488 (0.20) 5.082 (0.07) 3.960 (0.00) 1.981 (0.00) 2.975 (0.01) 1.558 (0.02) Train on positive edges TGN 1.834 (0.04) 4.972 (0.42) 3.944 (0.00) 1.978 (0.00) 2.867 (0.04) 1.522 (0.03) JODIE 3.059 (0.46) 5.376 (0.04) 20.12 (22.7) 31.21 (21.9) 18.70 (12.7) 96.81 (2.90) DyRep 3.146 (0.20) 4.067 (0.07) 3.945 (0.01) 1.984 (0.01) 3.193 (0.23) 1.929 (0.24) Train with negative sampling TGN 3.593 (0.59) 3.389 (0.07) 3.947 (0.00) 1.977 (0.00) 2.914 (0.04) 1.506 (0.03) JODIE 5.369 (0.15) 3.724 (0.03) 4.531 (0.64) 2.803 (0.75) 33.65 (11.5) 35.33 (13.4) DyRep 5.738 (0.30) 3.898 (0.08) 4.154 (0.24) 2.177 (0.24) 3.731 (0.28) 2.663 (0.67) Table 4: Accuracy and F1 score (%) with standard deviation (new nodes). Numbers in red mean the best results for all methods, and numbers in bold are the best results for GNNs.
Positive Accuracy Overall Accuracy Positive F1 Overall F1 Baselines Most 22.73 11.37 8.56 2.37 Persistence forecast 63.64 47.18 64.81 46.56 Dynamic GNNs Train on positive edges TGN 29.01 (1.04) 14.50 (0.52) 26.66 (1.01) 9.24 (0.28) JODIE 21.37 (1.45) 10.69 (0.73) 13.88 (3.09) 4.44 (1.27) DyRep 23.13 (1.69) 11.57 (0.85) 17.05 (3.04) 5.56 (1.18) Train with negative sampling TGN 8.16 (2.50) 50.52 (0.71) 10.41 (2.75) 40.21 (2.06) JODIE 1.19 (0.02) 50.09 (0.48) 1.06 (0.04) 34.38 (0.26) DyRep 0.24 (0.3) 50.00 (0.02) 0.14 (0.16) 33.48 (0.15) 12
