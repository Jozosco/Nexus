# SCRIHN_2025_supply_chain_resilience_hypergraph_NN

> 원본: `docs/research_desk/references/SCRIHN_2025_supply_chain_resilience_hypergraph_NN.pdf` · SHA256 `7321b26f981b0800…` · 9쪽 · 41,569자 · 변환 2026-09-09 (pdf_to_markdown.py)

## 목차(자동 복원)
- Resilience Inference for Supply Chains with Hypergraph Neural Network (p.1)
  - Zetian Shen1*, Hongjun Wang2,4*, Jiyuan Chen3,4, Xuan Song1† (p.1)
  - Introduction (p.1)
  - Related Work (p.2)
  - Preliminaries (p.3)
  - The Proposed Method (p.3)
  - Experiments (p.5)
  - Conclusion (p.7)
  - Acknowledgments (p.8)
  - References (p.8)

## 표(자동 추출)
**표 p.1**

| ventory of products |  |  |
|---|---|---|
| 11 | 0 | 0 |
| 10 | 12 | 0 |
| 11 | 8 | 21 |
| 0 | 0 | 16 |
| ventory of products |  |  |
| 11 | 0 | 0 |
| 0 | 12 | 0 |
| 11 | 8 | 21 |

**표 p.4**

| Input st .. e . p s Output Feature Hypergraph Encoder Encoder ... Readout MLP or Historical State Supply Chain Trajectories |  |
|---|---|
| Input st .. e . p s Historical State Supply Chain Trajectories | Output ... Readout MLP or |

## 본문

<!-- page 1 -->


## Resilience Inference for Supply Chains with Hypergraph Neural Network


### Zetian Shen1*, Hongjun Wang2,4*, Jiyuan Chen3,4, Xuan Song1†

1School of Artiﬁcial Intelligence, Jilin University 2The University of Tokyo 3Hong Kong Polytechnic University 4Southern University of Science and Technology Abstract Supply chains are integral to global economic stability, yet disruptions can swiftly propagate through interconnected net- works, resulting in substantial economic impacts. Accurate and timely inference of supply chain resilience—the capa- bility to maintain core functions during disruptions—is cru- cial for proactive risk mitigation and robust network design.
However, existing approaches lack effective mechanisms to infer supply chain resilience without explicit system dynam- ics and struggle to represent the higher-order, multi-entity de- pendencies inherent in supply chain networks. These limita- tions motivate the deﬁnition of a novel problem and the de- velopment of targeted modeling solutions. To address these challenges, we formalize a novel problem: Supply Chain Re- silience Inference (SCRI), deﬁned as predicting supply chain resilience using hypergraph topology and observed inventory trajectories without explicit dynamic equations. To solve this problem, we propose the Supply Chain Resilience Inference Hypergraph Network (SC-RIHN), a novel hypergraph-based model leveraging set-based encoding and hypergraph mes- sage passing to capture multi-party ﬁrm-product interactions.
Comprehensive experiments demonstrate that SC-RIHN sig- niﬁcantly outperforms traditional MLP, representative graph neural network variants, and ResInf baselines across synthetic benchmarks, underscoring its potential for practical, early- warning risk assessment in complex supply chain systems.
Extended version — https://arxiv.org/abs/2511.06208

### Introduction

Supply chains are critical to the global economy, yet local- ized disruptions—such as production accidents, logistics de- lays, or extreme weather—can propagate through intercon- nected networks, resulting in massive economic losses and even posing serious risks to national security (Baumgartner, Malik, and Padhi 2020). However, supply chains differ sig- niﬁcantly in their resilience to such shocks, where resilience is deﬁned as the ability of a system to adapt and maintain core functions under disruption (Cohen et al. 2000; Gao, Barzel, and Barab´asi 2016; Liu et al. 2022). Figure 1 il- lustrates two similarly sized supply chains subjected to the *These authors contributed equally.
†Corresponding Author Copyright © 2026, Association for the Advancement of Artiﬁcial Intelligence (www.aaai.org). All rights reserved.
Inventory of products 11 0 0 10 12 0 11 8 21 0 0 16 Two Different Supply Chains Changes in the inventory of at Non-Resilience Resilience Inventory Inventory Time Step Time Step Inventory of products 11 0 0 0 12 0 11 8 21 0 0 16 Figure 1: Illustration of supply chain resilience. Two sup- ply chains with different topologies (left) experience the same disruption (a factory ﬁre). The inventory trajectory of a downstream store (right) shows recovery in the upper net- work (resilient) and persistent failure in the lower network (non-resilient).
same factory ﬁre, where differences in network topology and product dependencies result in rapid recovery for one and prolonged stagnation for the other. These observations raise a key question: can we achieve early inference of sup- ply chain resilience to support proactive risk mitigation and robust network design?
Traditional supply chain studies relied on deter- ministic network optimisation (Vidal and Goetschalckx 1997), system-dynamics simulation (Sterman 1989), and agent-based modelling (Wu et al. 2012), while resilience work examined buffering and redundancy through stochas- tic or queuing frameworks (Shefﬁand Rice Jr 2005; Ivanov et al. 2018). However, as global supply chains grow in complexity and scale, these mechanistic models struggle to ﬁt even highly aggregated measures like country-level production (Inoue and Todo 2019), motivating the adop- tion of data-driven approaches such as machine learning for risk assessment and disruption prediction (Baryannis, Dani, and Antoniou 2019; Brintrup et al. 2020). Moreover, graph neural networks (GNNs) have shown strong potential for representing ﬁrm interactions and capturing the struc- tural properties of supply chain networks, with applications The Fortieth AAAI Conference on Artificial Intelligence (AAAI-26) 39259

<!-- page 2 -->

including hidden-link recovery, supplier risk ranking, and production-function estimation (Aziz et al. 2021; Kosasih and Brintrup 2022; Wasi, Islam, and Akib 2024; Chang et al. 2025). Despite these advances, data-driven approaches aimed speciﬁcally at supply chain resilience inference re- main limited.
Meanwhile, GBB (Gao, Barzel, and Barab´asi 2016) ex- tended resilience analysis from low-dimensional models to interacting complex networks, providing an important theoretical foundation for resilience prediction. More re- cently, GNN-based ResInf (Liu et al. 2022) inferred re- silience directly from graph structure and observed state trajectories, bypassing explicit modeling of system dynam- ics while demonstrating strong performance in mutualis- tic, gene regulatory, and neuronal networks. Nevertheless, supply chains differ fundamentally: they exhibit higher- order ﬁrm–product–ﬁrm structures where ﬁrms are linked through shared inputs and outputs (Carvalho and Tahbaz- Salehi 2019; Chang et al. 2025). Such higher-order depen- dencies are naturally modeled as hypergraphs, where a hy- peredge captures upstream–downstream relations via shared products. Standard GNNs, which operate on binary relations between nodes, are insufﬁcient to model these multi-party dependencies. Thus, it is necessary to develop models that can effectively capture higher-order dependencies inherent in hypergraph-structured supply chains.
Consequently, two open challenges remain for supply chain resilience inference. At the algorithmic level, exist- ing approaches lack a learnable mechanism to infer supply chain resilience directly from historical inventory trajecto- ries without explicit knowledge of the underlying system dy- namics. At the structural level, GNN-based models struggle to represent the higher-order dependencies and multi-entity interactions that are inherent in supply chain networks, lim- iting their applicability for resilience inference.
Motivated by these challenges, we identify a challeng- ing unexplored problem: Supply Chain Resilience Inference (SCRI), which aims to predict the resilience of a supply chain based on its hypergraph topology and observed state trajectories. SCRI focuses on predicting supply chain re- silience to enable early-warning capabilities, but is chal- lenged by the absence of explicit system dynamics and the complexity of the underlying hypergraph structure. To ad- dress SCRI, we propose the Supply-Chain Resilience Infer- ence Hypergraph Network (SC-RIHN), a model that lever- ages hypergraph message passing to learn higher-order in- teraction patterns from the supply chain structure and his- torical state trajectories, and integrates these representations into a resilience embedding for inference. Experiments on both synthetic shock scenarios and real-world datasets show that SC-RIHN consistently outperforms MLP, representative GNN variants, and the ResInf baseline across standard met- rics. In summary, our main contributions are:
1. We formalise Supply Chain Resilience Inference, a new problem of predicting supply chain resilience from hy- pergraph topology and historical state trajectories.
2. We propose SC-RIHN, a hypergraph network that cap- tures higher-order interactions through hypergraph mes- sage passing.
3. We provide a process for constructing a synthetic bench- mark and generating resilience labels to support repro- ducible evaluation.
4. The experimental results indicate that SC-RIHN outper- forms representative GNN baselines by more effectively capturing higher-order interactions, underscoring its po- tential for early-warning risk assessment.

### Related Work

Supply chains are often modeled as complex networks, where ﬁrms serve as nodes and supply or trade relation- ships form the edges. This network-based representation has facilitated quantitative analyses of systemic risk propaga- tion (Fujiwara and Aoyama 2010; Acemoglu et al. 2012; Zhao, Zuo, and Blackhurst 2019; Carvalho et al. 2021). In this context, resilience analysis typically employs system dynamics simulations or stochastic models to evaluate re- covery following disruptions (Hallegatte 2008; Guan et al.
2020; Shefﬁand Rice Jr 2005; Ivanov et al. 2018). How- ever, these methods frequently depend on extensive domain- speciﬁc assumptions and exhibit poor scalability in realistic, high-dimensional scenarios (Inoue and Todo 2019).
Graph neural networks (GNNs) have recently been em- ployed in supply chain systems, leveraging their inherent graph structure for tasks such as prediction and optimiza- tion (Aziz et al. 2021; Kosasih and Brintrup 2022; Ahn et al.
2024). The SUPPLYGRAPH benchmark (Wasi, Islam, and Akib 2024) addresses the lack of real-world datasets by pro- viding temporal supply chain data from a major FMCG ﬁrm, enabling GNN-based modeling of sales, production, and fac- tory issues. To address data privacy and distribution chal- lenges, a federated GNN framework (Qu et al. 2023) en- ables decentralized analysis of geospatial resilience in mul- ticommodity food ﬂow networks. Additionally, production function inference in ﬁrm–product networks has been en- hanced using GNNs equipped with temporal encoding and inventory-aware modules, leading to notable improvements in supply forecasting (Chang et al. 2025). While these ap- proaches advance task-speciﬁc prediction, they fall short of inferring system-level resilience or explicitly modeling higher-order supply chain dependencies.
To overcome the limitations of GNNs in modeling higher- order relationships, hypergraph neural networks (HGNNs) extend GNNs by introducing hyperedges that connect arbi- trary sets of nodes, enabling more expressive group-level representations (Feng et al. 2019; Gao et al. 2022; Li et al. 2025). For example, a neuromodulated small-world HGNN enhances trajectory prediction by capturing both lo- cal and long-range vehicle interactions, showcasing the ca- pability of HGNNs in modeling complex, higher-order sys- tems (Wang et al. 2025). Despite their potential, the appli- cation of hypergraph-based learning in supply chain sys- tems remains limited. Some initial efforts have explored ﬁrm–product–ﬁrm hypergraphs to encode higher-order re- lationships (Chang et al. 2025), but none have focused on resilience inference.
Classical complexity–stability theory (May 1972; Gao, 39260

<!-- page 3 -->

Barzel, and Barab´asi 2016) and its graph-neural exten- sion ResInf (Liu et al. 2022) estimate resilience di- rectly from standard graph structures. However, supply chains inherently form higher-order ﬁrm–product–ﬁrm hy- pergraphs (Carvalho and Tahbaz-Salehi 2019), underscoring the need for hypergraph-based resilience inference.

### Preliminaries

This section introduces key concepts and notations for sup- ply chain modeling, resilience, and the Supply Chain Re- silience Inference (SCRI) problem.
Supply Chain and Temporal States We represent the supply chain as a tripartite hypergraph H = (C, P, E), where C denotes the set of ﬁrm nodes, P is the set of product nodes, and E ✓C ⇥P ⇥C repre- sents the set of hyperedges. Each hyperedge (cup, p, cdown) indicates that the downstream ﬁrm cdown procures product p from the upstream ﬁrm cup. Additionally, each ﬁrm node c is associated with a time-dependent state vector x(t) c 2 Rd, capturing its operational status at time t. The dimensions of this vector may include key performance indicators such as inventory levels, production rates, and order volumes. In this work, we use inventory vectors to deﬁne node states:
x(t) c = !
I(t) c,p " p2P 2 R|P|, where I(t) c,p denotes the inventory level of product p held by ﬁrm c at time t. Stacking these vectors across all ﬁrms forms the supply chain state matrix Xt 2 R|C|⇥|P|.
Resilience Complex Network Resilience.
Consider a complex net- worked system G = (V, A), where A is the adjacency ma- trix, V is the set of nodes and each node i 2 V has a state xi. The system evolves according to the dynamics:
dxi dt = F(xi) + N X j=1 Aij G(xi, xj) (1) where F(xi) captures the intrinsic behavior of node i, and G(xi, xj) encodes the interaction between nodes i and j.
As deﬁned in GBB (Gao, Barzel, and Barab´asi 2016), the system is resilient if it has a unique and stable equilibrium x⇤6= 0 under the dynamics in Equation (1). In such systems, any bounded perturbation to the states xi will decay over time, leading the system to converge to x⇤. Conversely, a non-resilient system either fails to return to a desirable state or diverges entirely.
Supply chain Resilience.
Similar to the ResInf frame- work (Liu et al. 2024), we deﬁne supply chain resilience in terms of the convergence of ﬁrm-level states. Speciﬁcally, the primary concern lies in the operational states of ﬁrms, such as inventory levels and production capacities, rather than product-level dynamics. Formally, let Xt = {x(t) c }c2C denote the collection of ﬁrm states at time t. The supply chain is considered resilient if X(t) converges to a unique, non-zero equilibrium X⇤from any feasible initial condition.
Otherwise, the system is non-resilient if its dynamics remain unstable or fail to converge to a stable equilibrium.
Problem Deﬁnition We deﬁne Supply Chain Resilience Inference (SCRI) as the problem of inferring whether a supply chain is re- silient based on its network structure and historical in- ventory dynamics. Formally, given a supply chain hyper- graph H and a historical observation window WT = [X1, X2, . . . , XT −1] 2 RT ⇥|C|⇥Din, where Xt is the system state matrix at time t, T denotes the total number of time steps, and Din represents the dimension of node states. In this work, node states are represented by inventory vectors, so that Din = |P| denotes the number of products, poten- tially varying across supply chains. The task of the SCRI is to learn a parameterized mapping f✓: (WT , H) ! {0, 1} that predicts whether the system is resilient. This formula- tion infers resilience based on observed trajectories and the supply chain structure, without requiring explicit modeling of the underlying dynamics.

### The Proposed Method

We propose a novel framework, termed Supply Chain Re- silience Inference Hypergraph Network (SC-RIHN), to in- fer the resilience of supply chains by capturing higher-order interactions between ﬁrms and products. The overall ar- chitecture of SC-RIHN is illustrated in Figure 2. Given a supply chain hypergraph and corresponding historical state trajectories, a feature encoder ﬁrst transforms each ﬁrm’s variable-length state vector into a ﬁxed-dimensional em- bedding. This transformation ensures consistent represen- tation across heterogeneous supply chains while preserv- ing index-speciﬁc information essential for downstream in- ference. The resulting embeddings are then processed by a hypergraph encoder, which propagates information through the hypergraph to capture multi-party dependencies. At each time step, structural representations are obtained by apply- ing a pooling function over the updated embeddings of ﬁrm nodes. To obtain global system-level information, a global readout layer aggregates the sequence of structural embed- dings into a uniﬁed resilience representation, which is ﬁnally used for resilience inference via a multi-layer perceptron (MLP). Moreover, the model is trained end-to-end using a binary cross-entropy loss to optimize resilience inference.
Feature Encoder Firms are typically associated with feature sets whose di- mensionality can vary across different supply chain net- works. For instance, differences in the number of products handled by each supply chain result in inventory vectors of varying lengths. To address this variability, we employ a set- based feature encoder inspired by DeepSets (Zaheer et al.
2017), extending it with learnable positional embeddings to distinguish feature indices during aggregation. This design enables the model to process inputs of arbitrary dimension- ality while preserving information about the identity and po- sitional context of each feature.
Speciﬁcally, at each time step t, the feature encoder trans- forms the input feature vector x(t) c of ﬁrm c 2 C into a ﬁxed- dimensional representation h(t) c 2 RDhidden, ensuring that ﬁrm nodes across different supply chains are represented 39261

<!-- page 4 -->

...
...
Pool Supply Chain Input Historical State Trajectories Feature Encoder Split + Position Embedding Hypergraph Encoder Initialization Convolution Aggregation Pool Output ...
or MLP Hypergraph Encoder ...
L layers Product Position Embedding Feature Encoder MLP Readout ...
steps Figure 2: Overview of the proposed Supply Chain Resilience Inference Hypergraph Network (SC-RIHN). At each time step, the Feature Encoder decomposes ﬁrm state vectors into individual feature dimensions and combines them with learnable positional embeddings. A multi-layer perceptron (MLP) followed by a pooling operation then projects these heterogeneous inputs from various supply chains into a uniﬁed latent space. Subsequently, the Hypergraph Encoder initializes product node features using positional embeddings and integrates them with ﬁrm node embeddings. After multiple hypergraph convolution layers capturing higher-order dependencies, the reﬁned ﬁrm node embeddings are pooled into a graph-level representation. Finally, the Global Readout layer aggregates these representations across all time steps into a single system-level resilience embedding, which an MLP uses to infer resilience.
within a consistent feature space. To achieve this, the input vector is initially split into individual feature dimensions, where each feature is combined with a learnable positional embedding that encodes its index. These representations are then passed through a shared multilayer perceptron (MLP), and the transformed vectors are aggregated to obtain the ﬁ- nal ﬁrm-level embedding. Formally, the feature encoder is deﬁned as:
h(t) c = Pool ⇣n φ ⇣ x(t) c,d, pos(d) ⌘ | d = 1, . . . , Din o⌘ (2) where x(t) c,d is the d-th feature of ﬁrm c at time t, pos(d) is a learnable positional embedding for feature index d, φ(·) is an MLP applied to each individual feature, and Pool(·) performs aggregation over the feature dimension (e.g., via summation or averaging) to produce a ﬁrm-level embedding.
Although feature vectors are aggregated as sets for aggre- gation purposes, we introduce learnable positional embed- dings pos(d) to distinguish feature indices d. This enables the model to capture structural patterns encoded in the fea- ture ordering, which may reﬂect domain-speciﬁc semantics, such as the prioritization of certain attributes in supply chain operations.
Hypergraph Encoder To capture higher-order dependencies, we adopt hypergraph convolution operations on the supply chain hypergraph H = (C, P, E). The module ﬁrst initializes node features for both ﬁrms and products, then propagates information through shared product nodes using hypergraph message passing, and ﬁnally aggregates ﬁrm embeddings to obtain a compact system-level representation. This design enables the model to capture complex interactions and multi-hop dependencies across different levels of the supply chain.
Node Feature Initialization.
At each time step t, we con- struct an augmented node feature space that includes both ﬁrm and product nodes. For each ﬁrm node c 2 C, we as- sign a dynamic embedding h(t) c generated by the feature encoder. In contrast, product nodes p 2 P are consid- ered static, lacking intrinsic temporal dynamics. To encode their identity and enable structure-aware learning within the hypergraph, each product node is assigned a learn- able positional embedding pos(p). Combining these repre- sentations, we deﬁne the initial feature matrix as Z(0) t = stack({h(t) c }c2C, {pos(p)}p2P), where stack(·) indicates vertical concatenation along the node dimension.
Hypergraph Convolution.
To model higher-order inter- actions between ﬁrms and products, we apply Hypergraph Neural Networks (HGNN) (Feng et al. 2019) for message passing over the supply chain hypergraph. Formally, the hy- pergraph convolution at the l-th layer is deﬁned as:
Z(l+1) t = σ ⇣ D−1/2 v HWeD−1 e H>D−1/2 v Z(l) t W(l)⌘ (3) where Z(l) t is the node feature matrix, H is the incidence matrix encoding node–hyperedge relationships, W(l) is a learnable weight matrix, and σ(·) denotes a nonlinear acti- vation function. The degree matrices Dv and De normalize 39262

<!-- page 5 -->

the aggregation to ensure training stability. The hyperedge weight matrix We is initialized as the identity matrix, as- signing equal weights to all hyperedges.
Conceptually, the operation consists of two message- passing steps: nodes ﬁrst send information to their connected hyperedges, which then aggregate and redistribute this in- formation back to their constituent nodes. This bidirectional ﬂow enables the model to capture group-level dependencies that cannot be represented by pairwise interactions alone.
Such modeling capability is especially important in sup- ply chains involving shared products. After L layers, the model generates reﬁned ﬁrm node embeddings {z(t) c }c2C that capture both product-level associations and the hierar- chical structure of the supply chain. Although HGNN is used in our implementation, the architecture remains ﬂexible and can be extended with more advanced hypergraph convolu- tion methods such as UniGNN (Huang and Yang 2021), ED- HNN (Wang et al. 2022), or KHGNN (Xie et al. 2025).
Graph-Level Aggregation.
To obtain a compact system- level representation at time t, we aggregate the embeddings of all ﬁrm nodes using a permutation-invariant function:
st = Pool ⇣n z(t) c | c 2 C o⌘ (4) where Pool(·) can be instantiated as summation or averag- ing over ﬁrm nodes. The resulting st represents the struc- tural embedding of the supply chain at time t, capturing both node-level features and the global hypergraph structure. No- tably, product node embeddings are excluded from this ag- gregation because they do not represent intrinsic dynamic states. Instead, they function as intermediaries that facilitate information exchange among ﬁrms during hypergraph con- volution.
Resilience Inference and Optimization For the resilience inference, we apply a global readout layer that aggregates the structural embeddings over the temporal window:
˜s = Readout ({st | t = 0, 1, . . . , T −1}) (5) where Readout(·) may refer to any pooling function or temporal modeling technique, such as a Transformer En- coder (Vaswani et al. 2017). In this study, we employ sim- ple mean pooling to emphasize the formulation of the re- silience inference task and to demonstrate the effectiveness of the hypergraph-based framework, without introducing ad- ditional complexity from advanced temporal models. Subse- quently, the aggregated representation ˜s is transformed by an MLP to generate the ﬁnal resilience prediction. Finally, the entire model is optimized in an end-to-end manner using the binary cross-entropy loss.

### Experiments

Datasets We evaluate our approach on two datasets: a real-world sup- ply chain network centered on Tesla (denoted TESLA) and a collection of synthetic networks (denoted SCR) generated Tesla SCR Train Val Test Train Val Test #Res.
246 59 57 195 29 41 #Non-Res.
434 61 63 180 40 45 #Total 680 120 120 375 69 86 Avg. #Nodes 96 98 111 55 57 53 Avg. #Edges 43 43 51 366 362 358 Table 1: Dataset statistics for TESLA and SCR.
using the publicly available SupplySim simulator (Chang et al. 2025). Key dataset statistics are presented in Table 1, with detailed construction procedures provided in the Ap- pendix.
TESLA.
We collect all U.S. import bills of lading from the ImportYeti platform that list Tesla, Inc. as the consignee, covering the period from January 1, 2015 to June 15, 2025.
Each shipment record contains a Harmonized System (HS) commodity code, which we categorize based on the ﬁrst two digits to capture high-level commodity classiﬁcations. For each HS category, we identify the direct suppliers of Tesla from the shipment data. We then extend the network by trac- ing downstream demand connections: initially identifying the customers of Tesla’s suppliers, and subsequently identi- fying the customers of those customers. This process yields a three-tier, demand-centric network, with Tesla positioned as a key downstream entity. Although the dataset lacks do- mestic transaction records and contains incomplete maritime shipping data, it still enables a meaningful approximation of Tesla’s extended supply-demand network structure.
SCR.
To support reproducible research and evaluate model performance on complex benchmark networks, we employ the SupplySim simulator (Chang et al. 2025), which replicates the topological and transactional charac- teristics of real-world supply chains. We generate approxi- mately 500 synthetic networks exhibiting diverse structural patterns. To simulate scenarios of data incompleteness and evaluate model robustness under such conditions, we cre- ate perturbed variants of test networks by applying random removals with ﬁxed probability p = 0.15. Speciﬁcally, we consider: (i) Node Removal (SCR-NR), where each ﬁrm or product node is independently dropped with probability p, along with all incident edges; and (ii) Edge Removal (SCR- ER), in which each edge is independently removed with probability p while retaining all nodes.
Resilience Label Generation.
We simulate inventory dy- namics by combining the inventory–production feedback loop from Forrester’s system dynamics framework (For- rester 1997) with Sterman’s exponential-smoothing demand forecast and bullwhip effect formulation (Sterman 2002).
Following the ResInf (Liu et al. 2024), we sample n = 12 random initial inventory vectors for each network and simu- late 200 discrete time steps. A binary label y 2 {0, 1} is as- signed based on whether all trajectories converge to a com- mon equilibrium.
39263

<!-- page 6 -->

Model SCR SCR-NR SCR-ER TESLA MLP 0.684(0.006) 0.664(0.010) – 0.655(0.009) ResInf 0.499(0.176) 0.467(0.173) 0.463(0.165) 0.666(0.118) GIN 0.644(0.122) 0.572(0.101) 0.656(0.036) 0.679(0.051) GraphSAGE 0.714(0.033) 0.694(0.010) 0.713(0.026) 0.806(0.036) SC-RIHN 0.770(0.014)⇤⇤ 0.709(0.007)⇤ 0.811(0.016)⇤⇤ 0.856(0.017)⇤⇤ w/o Positional Embeddings 0.727(0.005) 0.663(0.010) 0.744(0.009) 0.736(0.009) w/ product nodes 0.737(0.005) 0.653(0.009) 0.771(0.016) 0.820(0.031) Table 2: Mean F1-score (standard deviation in parentheses) over 10 random runs. SCR-ER is not applicable to MLP, which does not utilize edge information. A statistically signiﬁcant improvement over the best-performing baseline is indicated with a star (⇤, p < 0.05; ⇤⇤, p < 0.005) according to two-sided paired t-tests.
Experimental Setup To maximize data efﬁciency, each supply chain network generates 12 distinct trajectory samples that share the same underlying network topology but differ in temporal dynam- ics. Similar to ResInf (Liu et al. 2024), only the ﬁrst T = 5 inventory states are used to construct the historical obser- vation window, emphasizing early-stage dynamics. We per- form a disjoint split at the supply chain level, assigning all associated samples exclusively to the training, validation, or test set in proportions of approximately 70%, 15%, and 15%, respectively, to prevent information leakage. Models are trained for 20 epochs, and the checkpoint with the high- est validation macro-F1 on the validation set is selected for ﬁnal testing. Training is conducted using the Adam (Kingma and Ba 2014) optimizer with a learning rate of 0.001 and batch size of 64. All models use a hidden dimension of 64. The number of layers L is tuned over {2, 3, 4, 5}, and the pooling function is set to mean pooling. Experiments are performed on a machine running Ubuntu 22.04.1 with 4 NVIDIA RTX 4090 GPUs.
Baselines We compare SC-RIHN against both structure-unaware method and representative GNN-based models to evaluate the beneﬁts of hypergraph modeling: (1) MLP: Processes each ﬁrm independently without utilizing structural infor- mation; (2) ResInf (Liu et al. 2024): Combines GCN (Kipf and Welling 2016) and Transformer (Vaswani et al. 2017), adapted via hyperedge-to-clique expansion; (3) GIN (Xu et al. 2018): A highly expressive GNN based on injec- tive aggregation, applied to clique-expanded graphs; and (4) GraphSAGE (Hamilton, Ying, and Leskovec 2017): An in- ductive GNN that enables representation generalization via sampled neighbor aggregation.
Main Results Table 2 shows that SC-RIHN consistently outperforms all baselines on both synthetic (SCR) and real-world (TESLA) datasets, conﬁrming the effectiveness of explicit hypergraph modeling for supply chain resilience inference. SC-RIHN remains robust under network perturbations and even im- proves slightly in edge removal scenarios, suggesting that pruning noisy or irrelevant links can enhance resilience estimation. On the dense SCR dataset, ResInf and GIN underperform relative to MLP, highlighting their limita- tions in capturing complex multi-party interactions. Graph- SAGE achieves better results, due to its sampling-based local aggregation that reduces sensitivity to noisy or re- dundant edges. For the cleaner TESLA dataset, all GNN models surpass MLP, demonstrating their strength under well-structured graphs. However, the elevated variance ob- served in ResInf and GIN indicates sensitivity to structural perturbations, which may result from information loss dur- ing the hypergraph-to-graph conversion.
Additionally, removing positional embeddings from the feature encoder signiﬁcantly degrades performance, under- scoring their critical role in preserving feature-index iden- tity. Similarly, including product nodes in graph-level pool- ing degrades performance, suggesting they function best as intermediaries for message propagation rather than as con- tributors to the ﬁnal prediction.
Ablation Studies Limitations of GNNs via Hypergraph Reduction.
To evaluate whether standard GNNs can substitute for hyper- graph modeling in supply chain resilience inference, we ap- ply three reduction heuristics: (1) Clique, which fully con- nects all nodes in a hyperedge; (2) Bipartite, which re- tains only ﬁrm–product edges; and (3) Firm-only, which re- moves product nodes entirely. We evaluate ResInf, GIN, and GraphSAGE on the resulting graphs. As shown in Figure 3, all reduced models perform worse than SC-RIHN, conﬁrm- ing that ﬂattening higher-order interactions leads to loss of structural information critical for resilience inference.
Among the three methods, Clique and Bipartite perform similarly, as both preserve ﬁrm–product links that support indirect inter-ﬁrm communication. Firm-only performs no- tably worse, highlighting the importance of product nodes in preserving structural pathways and enabling multi-party message exchange. A slight exception occurs with GIN on TESLA, possibly due to noise from sparse product links.
GraphSAGE beneﬁts from product-mediated patterns but still trails behind SC-RIHN.
Prediction Behavior across Resilience Classes.
To eval- uate the ability of each model to distinguish resilient from 39264

<!-- page 7 -->

(a) SCR dataset (b) TESLA dataset Figure 3: Performance of GNN baselines with different hy- pergraph reduction strategies on (a) SCR and (b) TESLA.
non-resilient supply chains in realistic settings, we visual- ize the predicted positive-class probabilities on the TESLA test set (Figure 4). All models reliably assign high scores to resilient cases, indicating their shared capacity to de- tect strong resilience signals. However, distinguishing non- resilient cases remains challenging. SC-RIHN more effec- tively suppresses scores for these samples, while Graph- SAGE shows overconﬁdence on a few non-resilient samples despite its overall competitiveness. In contrast, MLP, ResInf, and GIN exhibit signiﬁcant overlap between the two classes, leading to higher false positives and reduced interpretabil- ity. These results underscore the difﬁculty of calibrated pre- diction in real-world supply chains and suggest that while hypergraph-based models offer improvement, there remains room for more precise uncertainty estimation.
Sensitivity to Window Length and Layer Depth.
We evaluate the impact of temporal context and model depth on SC-RIHN by varying the observation window length T and the number of hypergraph layers L. As shown in Fig- ure 5, even with a single-step observation (T = 1), SC- RIHN achieves an F1-score around 0.75, demonstrating its ability to infer resilience from static supply chain structures by exploiting higher-order relational patterns. Performance improves with longer windows and peaks at T = 5, beyond which it declines due to accumulated noise and the absence of explicit temporal modeling. We thus set T = 5 as the de- Figure 4: Distribution of predicted resilience probabilities on the TESLA test set.
Figure 5: F1-score (mean over 10 random runs) on SCR un- der varying window length T and SC-RIHN layer depth L.
fault. Structurally, increasing the number of layers improves performance up to a point, underscoring the value of multi- hop message passing. A four-layer conﬁguration provides the best trade-off between accuracy and complexity, while ﬁve layers occasionally degrade results due to oversmooth- ing.

### Conclusion

In this paper, we introduced the Supply Chain Resilience In- ference (SCRI) problem, aiming to predict supply chain re- silience based on hypergraph structures and historical state trajectories. We proposed the Supply Chain Resilience In- ference Hypergraph Network (SC-RIHN), a novel model de- signed to capture complex multi-party interactions inherent to supply chains by leveraging hypergraph convolutions. Ex- periments conducted on synthetic and real-world datasets, including perturbation scenarios, demonstrate SC-RIHN’s superior performance over traditional graph-based models and standard machine learning baselines. Our ﬁndings high- light the critical importance of explicitly modeling higher- order dependencies, showcasing SC-RIHN’s practical value for proactive risk management and robust supply chain de- sign. Future directions include extending our framework to dynamic temporal modeling and exploring applications across broader real-world supply chain scenarios.
39265

<!-- page 8 -->


### Acknowledgments

This work was partially supported by the grants of Jilin Provincial International Cooperation Key Laboratory for Su- per Smart City and Jilin Provincial Key Laboratory of In- telligent Policing, and the Research Institute of Trustworthy Autonomous Systems at Southern University of Science and Technology.

### References

Acemoglu, D.; Carvalho, V. M.; Ozdaglar, A.; and Tahbaz- Salehi, A. 2012. The network origins of aggregate ﬂuctua- tions. Econometrica, 80(5): 1977–2016.
Ahn, H.-i.; Song, Y. C.; Olivar, S.; Mehta, H.; and Tewari, N. 2024.
Gnn-based probabilistic supply and inventory predictions in supply chain networks.
arXiv preprint arXiv:2404.07523.
Aziz, A.; Kosasih, E. E.; Grifﬁths, R.-R.; and Brin- trup, A. 2021.
Data considerations in graph representa- tion learning for supply chain networks.
arXiv preprint arXiv:2107.10609.
Baryannis, G.; Dani, S.; and Antoniou, G. 2019. Predicting supply chain risks using machine learning: The trade-off be- tween performance and interpretability. Future Generation Computer Systems, 101: 993–1004.
Baumgartner, T.; Malik, Y.; and Padhi, A. 2020. Reimag- ining industrial supply chains.
McKinsey & Com- pany.
https://www.
mckinsey.
com/industries/advance d-electronics/our-insights/reimagining-industrial-supply- chains.
Brintrup, A.; Pak, J.; Ratiney, D.; Pearce, T.; Wichmann, P.; Woodall, P.; and McFarlane, D. 2020. Supply chain data analytics for predicting supplier disruptions: a case study in complex asset manufacturing. International Journal of Pro- duction Research, 58(11): 3330–3341.
Carvalho, V. M.; Nirei, M.; Saito, Y. U.; and Tahbaz-Salehi, A. 2021. Supply chain disruptions: Evidence from the great east japan earthquake. The Quarterly Journal of Economics, 136(2): 1255–1321.
Carvalho, V. M.; and Tahbaz-Salehi, A. 2019. Production networks: A primer. Annual Review of Economics, 11(1):
635–663.
Chang, S.; Lin, Z.; Yan, B.; Bembde, S.; Xiu, Q.; Wong, C. H.; Qin, Y.; Kloster, F.; Luo, X.; Palleti, R.; et al. 2025.
Learning production functions for supply chains with graph neural networks. In Proceedings of the AAAI Conference on Artiﬁcial Intelligence, volume 39, 27878–27886.
Cohen, R.; Erez, K.; Ben-Avraham, D.; and Havlin, S. 2000.
Resilience of the internet to random breakdowns. Physical review letters, 85(21): 4626.
Feng, Y.; You, H.; Zhang, Z.; Ji, R.; and Gao, Y. 2019. Hy- pergraph neural networks. In Proceedings of the AAAI con- ference on artiﬁcial intelligence, volume 33, 3558–3565.
Forrester, J. W. 1997. Industrial dynamics. Journal of the Operational Research Society, 48(10): 1037–1041.
Fujiwara, Y.; and Aoyama, H. 2010. Large-scale structure of a nation-wide production network. The European Physical Journal B, 77(4): 565–580.
Gao, J.; Barzel, B.; and Barab´asi, A.-L. 2016.
Universal resilience patterns in complex networks. Nature, 530(7590):
307–312.
Gao, Y.; Feng, Y.; Ji, S.; and Ji, R. 2022. Hgnn+: General hypergraph neural networks. IEEE Transactions on Pattern Analysis and Machine Intelligence, 45(3): 3181–3199.
Guan, D.; Wang, D.; Hallegatte, S.; Davis, S. J.; Huo, J.; Li, S.; Bai, Y.; Lei, T.; Xue, Q.; Coffman, D.; et al. 2020. Global supply-chain effects of COVID-19 control measures. Nature human behaviour, 4(6): 577–587.
Hallegatte, S. 2008.
An adaptive regional input-output model and its application to the assessment of the economic cost of Katrina. Risk Analysis: An International Journal, 28(3): 779–799.
Hamilton, W.; Ying, Z.; and Leskovec, J. 2017. Inductive representation learning on large graphs. Advances in neural information processing systems, 30.
Huang, J.; and Yang, J. 2021. UniGNN: a Uniﬁed Frame- work for Graph and Hypergraph Neural Networks. In Pro- ceedings of the Thirtieth International Joint Conference on Artiﬁcial Intelligence, 2563–2569. International Joint Con- ferences on Artiﬁcial Intelligence Organization.
Inoue, H.; and Todo, Y. 2019.
Firm-level propagation of shocks through supply-chain networks. Nature Sustainabil- ity, 2(9): 841–847.
Ivanov, D.; et al. 2018. Structural dynamics and resilience in supply chain risk management, volume 265. Springer.
Kingma, D. P.; and Ba, J. 2014.
Adam: A method for stochastic optimization. arXiv preprint arXiv:1412.6980.
Kipf, T. N.; and Welling, M. 2016. Semi-supervised classi- ﬁcation with graph convolutional networks. arXiv preprint arXiv:1609.02907.
Kosasih, E. E.; and Brintrup, A. 2022. A machine learning approach for predicting hidden links in supply chain with graph neural networks. International Journal of Production Research, 60(17): 5380–5393.
Li, M.; Fang, Y.; Wang, Y.; Feng, H.; Gu, Y.; Bai, L.; and Lio, P. 2025. Deep hypergraph neural networks with tight framelets. In Proceedings of the AAAI Conference on Artiﬁ- cial Intelligence, volume 39, 18385–18392.
Liu, C.; Xu, F.; Gao, C.; Wang, Z.; Li, Y.; and Gao, J. 2024.
Deep learning resilience inference for complex networked systems. Nature Communications, 15(1): 9203.
Liu, X.; Li, D.; Ma, M.; Szymanski, B. K.; Stanley, H. E.; and Gao, J. 2022. Network resilience. Physics Reports, 971:
1–108.
May, R. M. 1972. Will a large complex system be stable?
Nature, 238(5364): 413–414.
Qu, Y.; Rao, J.; Gao, S.; Zhang, Q.; Chao, W.-L.; Su, Y.; Miller, M.; Morales, A.; and Huber, P. R. 2023. FLEE-GNN:
a federated learning system for edge-enhanced graph neural network in analyzing geospatial resilience of multicommod- ity food ﬂows. In Proceedings of the 6th ACM SIGSPATIAL 39266

<!-- page 9 -->

International Workshop on AI for Geographic Knowledge Discovery, 63–72.
Shefﬁ, Y.; and Rice Jr, J. B. 2005. A supply chain view of the resilient enterprise. MIT Sloan management review.
Sterman, J. 2002. System Dynamics: systems thinking and modeling for a complex world.
Sterman, J. D. 1989. Misperceptions of feedback in dynamic decision making. Organizational behavior and human deci- sion processes, 43(3): 301–335.
Vaswani, A.; Shazeer, N.; Parmar, N.; Uszkoreit, J.; Jones, L.; Gomez, A. N.; Kaiser, Ł.; and Polosukhin, I. 2017. At- tention is all you need. Advances in neural information pro- cessing systems, 30.
Vidal, C. J.; and Goetschalckx, M. 1997.
Strategic production-distribution models: A critical review with em- phasis on global supply chain models. European journal of operational research, 98(1): 1–18.
Wang, C.; Liao, H.; Wang, B.; Guan, Y.; Rao, B.; Pu, Z.; Cui, Z.; Xu, C.-Z.; and Li, Z. 2025. Nest: A neuromodulated small-world hypergraph trajectory prediction model for au- tonomous driving. In Proceedings of the AAAI Conference on Artiﬁcial Intelligence, volume 39, 808–816.
Wang, P.; Yang, S.; Liu, Y.; Wang, Z.; and Li, P. 2022. Equiv- ariant hypergraph diffusion neural operators. arXiv preprint arXiv:2207.06680.
Wasi, A. T.; Islam, M.; and Akib, A. R. 2024. Supplygraph:
A benchmark dataset for supply chain planning using graph neural networks. arXiv preprint arXiv:2401.15299.
Wu, T.; Huang, S.; Blackhurst, J.; Zhang, X.; and Wang, S.
2012. Supply chain risk management: an agent-based simu- lation to study the impact of retail stockouts. IEEE Transac- tions on Engineering Management, 60(4): 676–686.
Xie, L.; Gao, S.; Liu, J.; Yin, M.; and Jin, T. 2025. K-hop hypergraph neural network: A comprehensive aggregation approach. In Proceedings of the AAAI Conference on Artiﬁ- cial Intelligence, volume 39, 21679–21687.
Xu, K.; Hu, W.; Leskovec, J.; and Jegelka, S. 2018.
How powerful are graph neural networks? arXiv preprint arXiv:1810.00826.
Zaheer, M.; Kottur, S.; Ravanbakhsh, S.; Poczos, B.; Salakhutdinov, R. R.; and Smola, A. J. 2017.
Deep sets.
Advances in neural information processing systems, 30.
Zhao, K.; Zuo, Z.; and Blackhurst, J. V. 2019.
Mod- elling supply chain adaptation for disruptions: An empiri- cally grounded complex adaptive systems approach. Journal of operations Management, 65(2): 190–212.
39267
