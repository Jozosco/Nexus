# JEA_2026_who_sits_where_network_theory_global_production

> 원본: `docs/research_desk/references/JEA_2026_who_sits_where_network_theory_global_production.pdf` · SHA256 `37c4e9ebf789efac…` · 28쪽 · 74,076자 · 변환 2026-09-09 (pdf_to_markdown.py)

## 목차(자동 복원)
- Journal of Economic Analysis (p.1)
- Who Sits Where in the Chain? A Network-Based Theory of Global Production (p.1)
- Introduction (p.2)
- Synthesis of Results and Policy Implications (p.3)
    - Structural Insights from the Model (p.3)
    - Empirical Relevance and Policy Implications (p.4)
- Supply Chain Model (p.5)
    - General Environment (p.5)
    - Acyclical structures of global supply chains (p.8)
    - Linked Economies and Cascade Effects (p.10)
    - Illustrative Example: Six-Good, Five-Country Chain (p.11)
  - Equilibrium Prices by Good (6-good chain) (p.13)
  - Equilibrium Wages by Country (p.13)
- Conclusions (p.14)
- Glossary of Terms and Notation (p.14)
- Funding Statement (p.15)
- Acknowledgments (p.15)
- Conflict of interest (p.15)
- References (p.15)
- A (p.17)
- Mathematical Notation (p.17)
    - Vectors (p.17)
    - Matrices (p.17)
- B (p.18)
- Mathematical Proofs (p.18)
    - B.1 (p.18)
    - Lemmata (p.18)
    - B.2 (p.19)
    - Theorems (p.19)
    - B.3 (p.22)
    - Propositions (p.22)
    - B.4 (p.24)
    - Corollaries (p.24)
- C (p.25)
- Example code (p.25)

## 본문

<!-- page 1 -->

Journal of Economic Analysis 2026 5 (1) 133–160

## Journal of Economic Analysis

Homepage: https://www.anserpress.org/journal/jea

## Who Sits Where in the Chain? A Network-Based Theory of Global Production

Gustavo Nicolas Paez Salamancaa,* a Faculty of Economics, University of Cambridge, Cambridge CB3 9DD, United Kingdom ABSTRACT This paper develops a general equilibrium model of global supply chains in which production is struc- tured as a direct acyclical graph (DAG). This network-based formulation captures complex input–output linkages while remaining analytically tractable. It departs from standard trade models by embedding sup- ply chain topology directly into price, wage, and specialization outcomes. Equilibrium prices depend on production architecture—not geography—and countries sort endogenously into value chain positions based on revenue-maximizing comparative advantage. The framework explains how upstream shocks propagate through bottlenecks, why productivity and wage patterns may decouple, and how prices form recursively in interdependent economies. These dynamics are especially salient in the wake of global disruptions such as the U.S.–China trade war, the COVID-19 pandemic, and the war in Ukraine. By focusing on produc- tion structure rather than trade flows, the model offers a tractable lens to study structural transformation, systemic resilience, and the evolving geometry of global integration.
KEYWORDS General equilibrium theory; Production Networks; Direct acyclical Graphs; Comparative advantage theory JEL codes: F11, D85, D57 * Corresponding author: Gustavo Nicolas Paez Salamanca E-mail address: gnp24@cantab.ac.uk ISSN 2811-0943 doi: 10.58567/jea05010006 This is an open-access article distributed under a CC BY license (Creative Commons Attribution 4.0 International License) Received 8 October 2025; Accepted 10 December 2025; Available online 7 January 2026; Version of Record 15 March 2026

<!-- page 2 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 1

## Introduction

The fragility of global supply chains has become a defining concern of the world economy. In the wake of the COVID-19 pandemic (2020–2022), the semiconductor export restrictions imposed by the United States (from 2022 onward), and most recently, the sweeping tariff hikes introduced by the U.S. administration in early 2025, questions of resilience, redundancy, and strategic autonomy have re-entered the policy mainstream. These events exposed the limitations of canonical trade models, which typically treat production as geographically grounded, bilaterally transacted, and technologically homogeneous. A comprehensive survey by Antràs and Chor (2022) documents how the literature has moved toward network-based views of production and quantitative input-output approaches, underscoring the need for structural frameworks that link production architecture to equilibrium outcomes.
Yet global production today operates through complex networks in which intermediate goods cross borders multi- ple times and shocks reverberate through multiple layers of suppliers. These interdependencies between countries are not adequately captured by models that assume production occurs either within closed national economies or through simplified sequences of intermediate and final goods. In practice, the position of a country in a supply chain depends not just on comparative costs but on the structural incentives embedded in global production networks. As Antràs and Chor (2022) emphasize, a key open challenge is to retain theoretical transparency while accommodating realistic network structures—an objective addressed here by deriving closed-form equilibrium relationships that are explicitly topology-driven.
Theoretical attempts to understand global value chains have made major strides over the past two decades. Frag- mentation models (Antràs, 2004; Grossman and Helpman, 2002; Grossman and Rossi-Hansberg, 2008; Kohler, 2004) examine firms’ outsourcing and offshoring decisions, usually in a two-region world with parallel tasks. These models, while rich in institutional detail, limit supply chain complexity and underplay the endogenous economic forces that govern income distribution across countries. Others, like Costinot et al. (2012), have introduced sequential production into Ricardian trade theory, using an O-Ring-type logic (Kremer, 1993) to explain why low-productivity countries tend to produce early-stage inputs. However, these models assume linear supply chains and preclude joint production of the same good in multiple countries, limiting their ability to generalize to real-world networked production.
In parallel, a distinct body of literature has revived the study of production networks using input–output matrices.
Inspired by Leontief (1951), recent contributions such as Acemoglu et al. (2012) examine how microeconomic shocks propagate through production systems. Their models clarify how firm-level disruptions can have aggregate effects depending on the topology of the supply graph. However, these frameworks typically abstract from international trade and assume perfect factor mobility and price equalization—thus ruling out wage inequality, one of the most pressing features of the global economy. Relatedly, Antràs and Chor (2022) survey quantitative implementations that introduce substitution and rich frictions, but these often come at the cost of losing the kind of sharp, closed-form characterizations developed here.
This study develops a unified general equilibrium model that explicitly incorporates international trade, hetero- geneous country productivity, and arbitrary production networks. The model builds on the Ricardian foundations laid by Shiozawa (2007), who extended classical trade theory to accommodate input–output relationships. By embedding production in a direct acyclical graph (DAG), the framework introduces a recursive price and wage formation mech- anism that captures how productivity, network structure, and labor allocation jointly determine specialization and income. In contrast to the endogenous-link, CES-based approach of Dhyne et al. (2023), which studies firm-to-firm network formation (including cyclic and acyclic structures) and equilibrium selection in calibrated environments, the analysis here takes the production architecture as a primitive object and shows how a DAG structure delivers tractable, closed-form theorems that map topology directly into equilibrium prices, wages, and specialization patterns. The two approaches are complementary: Dhyne et al. (2023) emphasize link choice and quantitative fit, whereas the present framework provides structural identification and transparent comparative statics.
Three innovations set this model apart. First, it shows that prices depend not on geography but on production structure: goods with isomorphic input graphs command identical prices across countries. Second, it demonstrates that countries specialize according to revenue per worker, not physical position in the value chain—explaining the empirical coexistence of high-productivity upstream exporters and low-productivity final assemblers, a pattern that prior models like Costinot et al. (2012) cannot explain. Third, it formalizes how productivity shocks cascade through supply networks, triggering wage responses that attenuate with structural distance—unless they affect the set of active techniques, in which case upstream and downstream effects can both be substantial. Taken together, these results respond to the agenda articulated by Antràs and Chor (2022) by delivering general-equilibrium theorems that are explicitly network-topological, and they complement Dhyne et al. (2023) by offering a benchmark analytical environment in which the consequences of network structure can be derived without heavy calibration or bargaining assumptions.
These results contribute to a growing effort to build structural models that integrate network theory and interna- tional economics. In doing so, the model generalizes and complements existing contributions by Baldwin and Venables 134

<!-- page 3 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 (2013), Antràs (2020), Grossman and Rossi-Hansberg (2008), and Franke et al. (2024), while preserving tractability through a recursive solution algorithm. The framework also revives a Leontief-style input–output perspective, rein- terpreted for a globalized economy with endogenous specialization and limited labor mobility. Relative to the frontier surveyed by Antràs and Chor (2022) and the endogenous production-network formation in Dhyne et al. (2023), the contribution is to characterize (i) structure–price equalization on DAGs, (ii) revenue–interval specialization, and (iii) a constructive recursion for prices and wages that makes propagation and policy counterfactuals analytically transparent.
By clarifying how economic structure shapes equilibrium outcomes, the model provides analytical tools to study the effects of industrial policy, diversification, reshoring, and technological change. The recursive algorithm enables simulations that can evaluate how specific interventions—such as the 2025 U.S. tariff hikes—alter international spe- cialization, relative wages, and the global distribution of value added.
The remainder of the paper is organized as follows. Section 2 synthesizes these theoretical results of the model to present the reader a roadmap for the formalization sections and maps them to empirical patterns, while highlighting open directions for empirical validation and policy application. Once the utility of the model is defined, Section 3 introduces the general equilibrium model and defines the underlying production network as a direct acyclical graph.
Section 3.1 establishes the existence and efficiency of competitive equilibria, and derives the core results on wage determination and specialization. Section 3.2 adds structural assumptions on the production graph and examines how topological features shape prices, specialization, and international sorting. Section 3.3 introduces cascade dynamics and defines the conditions for recursive price and wage formation in linked economies. Finally, Section 4 summarizes the key findings and present natural extensions of the model.
2

## Synthesis of Results and Policy Implications

This section consolidates the theoretical contributions of the supply chain model (formalized in the following sections) and connects them to real-world evidence. It is organized into two parts: the first distills the model’s structural insights; the second translates those insights into plain language and maps them to concrete empirical patterns, with a focus on how the framework extends prior theoretical approaches.
2.1

#### Structural Insights from the Model

The supply chain model advances the theory of global value chains by providing a unified, tractable framework that accommodates arbitrary production topologies while endogenously generating equilibrium wages and prices. This fills a gap left by earlier approaches that either restrict attention to linear chains (Costinot et al., 2012) or impose strong assumptions about specialization (Grossman and Rossi-Hansberg, 2008). The model starts with four assumptions that basically state that countries produce goods by using explicit inputs in given proportions and that, without trade, countries can be self-sufficient in the production of final goods.
From this starting point, the model does not require further assumptions to prove that:
(i) Competitive equilibrium yields globally efficient allocations.
(ii) Wages equal the marginal contribution of labor to the final good.
(iii) Specialization follows revenue-maximizing comparative advantage.
(iv) Wage gaps are pinned down by prices of commonly produced goods, reflecting structural interdependence in global production.
If in addition the network follows a direct acyclical graph and standardize productivity within a country:
(v) Prices are uniquely determined by the structure of production; goods with isomorphic production graphs have identical prices.
(vi) Countries specialize according to output prices, not value-chain position, enabling high-productivity countries to allocate labor to whichever stage yields the greatest revenue per unit of effort.
(vii) The global production network sorts countries into endogenous price intervals, with less-productive economies concentrating in low-price raw materials.
(viii) Productivity shocks propagate across countries only when they shift the set of active techniques or alter relative price intervals.
135

<!-- page 4 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 If a final assumption is incorporated where the demand of automation increases with the complexity of the supply chain of the products:
(ix) Strict ordering of prices along the chain: each downstream good is priced above its immediate inputs.
(x) Endogenous vertical specialization, with more productive countries positioned upstream.
(xi) Recursive price and wage formation in linked economies, computable with a step-by-step algorithm.
(xii) Downstream propagation of productivity shocks, with wage effects that attenuate as distance from the origin increases.
2.2

#### Empirical Relevance and Policy Implications

The model’s predictions align with a broad range of empirical patterns in global production and complement the frontier summarized by Antràs and Chor (2022) while offering sharper, closed-form implications than endogenous link-formation approaches such as Dhyne et al. (2023). First, it clarifies the observed parity in prices across countries when production structures are identical. Semiconductor chips produced in Korea, Taiwan, and the United States with comparable design specifications command nearly identical prices (Jones et al., 2023), as do other standardized goods like auto parts and agricultural commodities (Constantinescu et al., 2020; Gereffi, 2014). This supports the insight that production structure—not geographic location—is the key determinant of prices. While Antràs and Chor (2022) survey evidence consistent with price equalization under standardized technologies, and Dhyne et al. (2023) allow for richer substitution and endogenous links in CES environments (where equalization can be blurred by intensive-margin adjustments), the DAG-based framework advanced here delivers a structure–price equalization theorem: isomorphic production graphs imply identical equilibrium prices across countries in theory, not only on average in data.
Second, the theory accounts for productivity-linked specialization in value chains. High-productivity countries consistently specialize in upstream or high-value-added tasks. Examples include Taiwan’s leadership in chip manufac- turing (Lee and Chen, 2016) or Switzerland’s exports of precision machinery (UNIDO, 2018). Unlike earlier models that required productivity sorting to follow a linear chain, the DAG-based model permits specialization based on revenue-maximization, regardless of position. Relative to the broad patterns reviewed by Antràs and Chor (2022) and the firm-to-firm network formation in Dhyne et al. (2023), the contribution here is to characterize specialization via price intervals (revenue per worker), providing a transparent mapping from productivity to value-chain roles without estimating link-formation frictions.
Third, the model explains the persistence of low-cost specialization as an efficient equilibrium. Countries like Bangladesh and Mexico, which focus on garments and assembly operations, remain competitive due to optimal match- ing between low productivity and labor-intensive tasks (Bergin et al., 2009; Rahman et al., 2008). The model em- phasizes that low output prices do not imply inefficiency. This provides an analytically tractable benchmark that complements the quantitative perspectives synthesized by Antràs and Chor (2022), clarifying when low-price segments arise endogenously from network structure rather than policy distortions.
Fourth, the framework captures the stability of wages across sectors with diverse technologies. Eastern European automotive hubs and Southeast Asian electronics manufacturers often exhibit limited wage dispersion despite produc- tion variety (Evenett et al., 2024; Bank, 2021a). This aligns with the result that structurally equivalent production techniques yield similar marginal returns to labor. Whereas calibrated CES models (e.g., Dhyne et al., 2023) can repli- cate wage patterns numerically, the present framework yields closed-form conditions under which wage equalization emerges across structurally equivalent techniques, offering testable restrictions that can discipline quantitative work surveyed by Antràs and Chor (2022).
Fifth, the model formalizes the observation that value accumulates along the depth of the production network.
Finished goods tend to command higher prices than their intermediate or raw counterparts. This is evident in food and industrial goods, where value increases with transformation—e.g., chocolate relative to cocoa, or machinery over metal parts (Organisation for Economic Co-operation and Development, 2024; Marcato and Baltar, 2020). Policymakers aiming to capture greater value can target midstream stages, not just final goods. The results provide a theoretical monotonicity (under standard regularity) linking depth in the DAG to prices, moving beyond descriptive patterns highlighted in Antràs and Chor (2022) to a constructive ordering result that holds without imposing estimated demand elasticities or bargaining shares.
Sixth, the endogenous structure of global trade predicted by the model corresponds to real-world co-specialization patterns. Regional clusters like the East Asian electronics network and the Mexican value chain specialization reflect countries aligning their roles based on productivity and compatibility (Timmer et al., 2014; Blyde, 2014).
These outcomes arise even without explicit coordination, reinforcing the idea of self-organized equilibrium. While Dhyne et al. (2023) endogenize link selection at the firm level and can match such clusters quantitatively, the present framework 136

<!-- page 5 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 shows analytically how price-interval sorting generates co-specialization across countries, delivering comparative statics that can be ported to calibrated settings.
Seventh, the recursive algorithm proposed in the model makes equilibrium prices and wages computable under realistic supply chain architectures. This is valuable for applied policy models, such as those used by the WTO and IMF to evaluate trade shocks and fiscal responses (Bouït et al., 2013; Lee, 2022). In contrast to the heavier calibration typically required in the quantitative literature surveyed by Antràs and Chor (2022) and in endogenous-network models like Dhyne et al. (2023), the step-by-step recursion yields fast, transparent computation and crisp comparative statics—useful both as a standalone tool and as a benchmark to validate larger-scale simulations.
Finally, the model’s cascade mechanism offers a theoretical foundation for the propagation of supply chain dis- ruptions. Events like the 2011 T¯ohoku earthquake, the COVID-19 pandemic, and the Suez Canal blockage triggered downstream effects with uneven global impacts (UNCTAD, 2020; Bank, 2021b). The model predicts such dynamics, showing that upstream countries experience attenuated and delayed wage effects, while downstream partners bear the brunt of shocks. This provides the closed-form network logic underlying propagation patterns discussed in Antràs and Chor (2022) and complements the empirical and calibrated propagation exercises in Dhyne et al. (2023).
Taken together, these empirical validations underscore the model’s relevance for policy design. By focusing on structural production features, the framework bridges theoretical gaps and provides clear guidance for interventions such as upgrading strategies, regional trade integration, and resilience planning, while furnishing benchmark theorems and an algorithmic apparatus that extend and discipline the broader literature reviewed by Antràs and Chor (2022) and the endogenous-network results in Dhyne et al. (2023).
3

## Supply Chain Model

This section develops a theoretical framework that integrates global supply chains with international trade in a gen- eral equilibrium setting. We begin by defining the structural assumptions that give rise to international specialization and relative income determination. We then characterize the equilibrium via a linear programming representation, highlighting a tractable mapping between the economic structure and the resulting distributional and allocative out- comes.For readers clarity, all notation is summarized in A and all proofs are in B.
3.1

#### General Environment

The global economy consists of C countries, indexed by c = {1, 2, . . . , C}, each endowed with a fixed labor supply qc.
There are M goods, indexed by m = {1, 2, . . . , M}, with good 1 designated as the final consumption good. Workers consume only the final good and supply labor inelastically. Labor is immobile across borders but fully mobile across sectors within countries.
Each country has one production technique per good, transforming intermediate inputs and labor into output.
We assume:
Assumption 1. Each production technique is Leontief and produces exactly one good.
Assumption 2. The final good is not used as input. All other goods are required (directly or indirectly) to produce the final good.
Assumption 3. In autarky, each country can produce the final good using only domestic techniques.
Assumption 4. Input bundles are identical across countries for each good, but productivity varies across countries.
Firms are profit-maximizing and operate under perfect competition. Each firm specializes in a single good using a country-specific technology, inducing a one-to-one mapping between firms and production techniques. Each production technique is represented by a vector τ ∈RM, where τi > 0 denotes the output good and τj < 0 the required inputs. Let C(τ) denote the country and G(τ) the output good associated with technique τ. The set of all available techniques is denoted by Ξ. For any subset γ ⊆Ξ, define A(γ) as the matrix of technique vectors and I(γ) as the vector of country identifiers. A labor allocation x applied to γ yields net output A(γ)T x and country-level employment I(γ)T x.
Under Assumptions 1–4, the set of feasible production relationships forms a directed graph, where an edge from good n to good m indicates that n is used as an input in the production of m. This induces a recursive architecture in which intermediate goods accumulate along the production chain toward final goods.
The resulting structure generalizes the neo-Ricardian framework to account for complex global value chains and supports a tractable analysis of specialization, price formation, inequality, and cross-country interdependence when technologies rely on fixed, non- substitutable input combinations.
137

<!-- page 6 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 Assumption 1 captures the essence of production: each firm operates according to a fixed recipe that specifies the exact quantities of inputs required to produce one unit of output. For instance, to manufacture a bicycle, a frame, two tires, and a set of screws are needed in predetermined proportions. There are two reasons for adopting the Leontief specification. First, it accurately represents short-term production within firms, when substitution among inputs is technologically infeasible—the recipe is fixed, and firms differ only in their efficiency, i.e., in how fast or how well they can execute the same process. Second, a first-order Taylor expansion of a CES production function around the equilibrium input mix yields a locally fixed-coefficient (Leontief) representation, since marginal productivities collapse to a common shadow value.1 In this sense, a Leontief is a natural short-run approximation: for small deviations around the operating point, input ratios remain constant, and output varies only with proportional changes in all inputs.
Assumption 2 serves as a normalization that focuses attention on the final good, which aggregates consumption.
It does not imply that consumers can only enjoy a single good; rather, it means that in each period, the representative agent’s desired consumption basket is fixed, and that basket itself constitutes the “final good” of the model.
Assumption 3 ensures that, in principle, any country can be self-sufficient in producing the final good. This assumption establishes a benchmark in which all countries possess the complete set of production techniques necessary for autarky, allowing the analysis to isolate how market integration and comparative efficiency drive specialization beyond this baseline of potential self-sufficiency.
Assumption 4 complements Assumption 1 by stating that, to produce any given good, all countries require the same input bundle—the same recipe—but differ in their efficiency parameters. This captures the idea that the structure of production is globally common, while productivity varies by country. For example, two firms producing tables may both require identical inputs—wood, screws, and varnish—but one uses a cutting board and hand saw while another employs industrial tools. The resulting tables are equivalent, yet the hand-cut process yields less output from the same material. In this sense, Assumption 4 highlights that international differences arise from efficiency in execution, not from variation in the input composition itself.
Example 5 (Bicycle Assembly Supply Chain). Consider 3 goods: Bicycle (1), Frame (2), and Tires (3), and two countries: Japan and Mexico.
Production techniques:
• Good 1: requires 1 Frame, 2 Tires, 1 unit labor.
• Good 2: requires 1 labor.
• Good 3: requires 1 labor.
Let A(γ) for Japan be:
A(γ) =   1 −1 −2 0 1 0 0 0 1   Suppose Japan is more productive in intermediate goods, while Mexico is more productive in bicycles.
This illustrates Assumption 4.
The DAG has edges: 2 →1, 3 →1.
Example 6 (Chocolate Production Chain). Consider 4 goods: Chocolate (1), Cocoa Paste (2), Sugar (3), Cocoa Beans (4), and three countries: Ghana, Brazil, Switzerland.
Production techniques:
• Good 1: requires 1 Paste, 1 Sugar, 1 labor.
• Good 2: requires 1 Bean, 1 labor.
• Goods 3, 4: require 1 labor.
1Let F(x) = (P i αixρ i )1/ρ, where ρ = (σ −1)/σ. A first-order Taylor expansion around an interior point x0 gives F(x) ≈ F(x0) + P i ∂F ∂xi x0(xi −x0 i ). Since ∂F ∂xi x0 = λ αρ i (x0 i )ρ−1, when σ is small (ρ →−∞) the smallest ratio xi/αi dominates the variation in F(x). Thus, near x0, F(x) ≃mini{xi/ai}, where ai = x0 i /F(x0). Hence, the first-order expansion yields a locally fixed-coefficient (Leontief) representation because marginal productivities converge to a common shadow value.
138

<!-- page 7 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 Assume Ghana excels in Beans, Brazil in Paste and Sugar, and Switzerland in assembly.
A(γ) =   1 −1 −1 0 0 1 0 −1 0 0 1 0 0 0 0 1   The DAG: 4 →2 →1; 3 →1.
These assumptions allow us to characterize general equilibrium under perfect competition. Let p and w denote the vectors of prices and wages. The profit vector is A(Ξ)p −I(Ξ)w. Equilibrium is defined as:
Definition 1 (Equilibrium). A general equilibrium consists of labor allocation x ∈R|Ξ|, prices p ∈RM, and wages w ∈RC such that:
A(Ξ)p −I(Ξ)w ≤O|Ξ|×1 (No positive profits) (1) xi > 0 ⇒A(Ξ)i.p = I(Ξ)i.w (Zero profits for active firms) (2) A(Ξ)T .−1x = O(M−1)×1 (Intermediate goods market clears) (3) xT A(Ξ)p = qT w (Final good market clears) (4) I(Ξ)T x = q (Labor market clears) (5) These conditions define an efficient and competitive outcome. Theorem 7 establishes a dual characterization:
Theorem 7 (General equilibrium). Define R = −A(Ξ)T .−1 I(Ξ)T  . Then the following linear program yields the equilibrium:
Ω= max x≥0 A(Ξ)T .1x s.t.
Rx ≤ O(M−1)×1 q  The dual variables p and w (shadow prices) correspond to equilibrium prices and wages, with normalization p1 = 1.
The linear program describes an allocation that maximizes output of the final good subject to feasibility. It yields a set of binding constraints—the basic techniques—that define active firms.
Proposition 1. In equilibrium:
(a) The wage of a country equals the marginal product of its workers in the final good.
(b) Given the set of basic techniques, wage levels are independent of population size.
Theorem 7 and proposition 1 demonstrate that general equilibrium in supply chains is efficient, transparent, and tractable. Income levels emerge directly from the set of active production techniques. This formulation extends neoclassical marginal productivity logic to multi-stage, globally fragmented production.
Theorem 8 (Income ranking and interdependency). Let γ be the set of basic techniques. For any τ(m, c), τ(m′, c′) ∈γ:
(a) If τ(m, c′)m > τ(m, c)m, then wc′ > wc.
(b) The ratio of price-weighted productivity differences satisfies:
pm′(τ(m′, c′)m′ −τ(m′, c)m′) pm(τ(m, c′)m −τ(m, c)m) ≥1.
(c) If both techniques are active, then:
wc′ = wc + pm(τ(m, c′)m −τ(m, c)m).
Theorem 8 formalizes cross-country income interdependence. Wages reflect both domestic productivity and the prices of goods shared across countries. Comparative advantage in this setting is revenue-based: countries specialize in sectors offering the highest relative gains.
139

<!-- page 8 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 3.2

#### Acyclical structures of global supply chains

The previous subsection introduced the general environment of global supply chains under a direct acyclical graph (DAG) structure.
While previous results allowed the general understanding of efficiency and salary definition in markets, this section adds two more assumptions to provide analytical prescriptive results of the model.
Assumption 9. The production network is a direct acyclicalal graph.
Assumption 10. The productivity of a country is constant between sectors.
Assumption (A5) imposes a direct acyclical graph (DAG) structure on production, excluding cycles and ensuring that all inputs are physically embedded in the final good. This reflects the material character of industrial supply chains, where components such as fabric, semiconductors, or steel parts become constituent elements of the output, and aligns with empirical and theoretical treatments of input–output linkages (Baldwin and Venables, 2013; Ostrovsky, 2008). In this framework, a link between two goods in the network implies a direct transformation: one good becomes part of another through an embodied flow of matter or energy. The DAG thus represents input chains, not broader technological dependencies—each edge exists because the upstream item is literally incorporated into the downstream product.
The notion of “input” therefore differs from that of a facilitating technology. A microchip used inside a computer is a genuine input, because it is materially embedded in the final product and its quantity determines the bill of materials. By contrast, a computer used to control assembly machines or to simulate designs is not an input but part of the production technology. It enhances productivity—workers could in principle assemble the product manually with basic tools, albeit more slowly—but it does not alter the composition or number of physical inputs required.
Such devices, together with design software, automation systems, or maintenance protocols, belong to the technology set that determines efficiency (kc) rather than the topology of the input network.
The boundary becomes even more intriguing for non-physical goods. Software and digital codes can indeed be used to produce other software, forming what would appear to be feedback loops. Yet these interactions operate under a distinct logic: software is a non-rival, non-exclusive asset—the use of code by one agent does not preclude simultaneous use by another, nor does it consume the original resource. The framework here abstracts from that domain and restricts attention to rival and exclusive goods, where production necessarily transforms and embeds scarce, material inputs. This restriction keeps the graph acyclic and the equilibrium results in Sections 3.2 and 3.3 well-defined.
Within this framework, a good is classified as a raw material if it requires only labor (i.e., has zero in-degree), and its production structure, denoted Prod(m), is the subgraph of all goods with a path leading to m. Figure 1 illustrates these definitions: the node labeled “Final Good” depends on a hierarchy of intermediates and raw materials. For example, Prod(6) = 1, 2, 3, 4, 5, 6 includes all nodes that contribute directly or indirectly to the production of good 6. Raw materials such as nodes 1, 2, 3, and 5 appear without predecessors, indicating pure labor-based production, while intermediate goods (e.g., node 4) synthesize inputs and pass complexity downstream.
140

<!-- page 9 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 Figure 1: Direct acyclicalal graph illustration.
Key to the model, only the topology of the production structure matters. If another good—say good 12—has a subgraph with the same connectivity as Prod(6), then Prod(12) is said to be isomorphic to Prod(6). In what follows, this isomorphism is treated as an equivalence relation; hence, Prod(6) = Prod(12) defines an equivalence class of goods with structurally identical production logic. This abstraction allows the theory to compare production structures across sectors and countries independently of specific labels.
The concept of raw distance, rd(m) := max d(m, n) : n ∈Nodes(Prod(m)), measures the longest path from any raw material to m. In the figure, rd(6) = 2, capturing that while some inputs (e.g., node 5) are one stage away, others (e.g., nodes 1–3) lie two steps upstream. This measure proxies the technological layering embedded in a good and highlights heterogeneity in structural complexity within a DAG-based supply chain.
Assumption (A6) simplifies cross-country heterogeneity by assuming sector-invariant productivity, i.e., τ(m, c)m = τ(m′, c)m′ = kc. This approach, inspired by Kremer (1993) and Costinot et al. (2012), isolates the impact of supply chains without confounding it with sectoral variation.
Countries are ordered by productivity, k1 > k2 > · · · > kC, which implies w1 > w2 > · · · > wC by Theorem 8.
The focus thus shifts from wage determination to production allocation and the propagation of productivity shocks.
Normalizing the ideal productivity to one unit of output per unit of labor, kc is interpreted as relative efficiency.
The following results characterize how these assumptions shape specialization and price formation:
Theorem 11 (Prices and structures). Let p, w be the price and income vectors of an equilibrium. Let γ be a set of basic techniques and {τ(m, c), τ(m′, c′)} ⊆γ. Then, (a) Structure-Price Equalization: If Prod(m) = Prod(m′), then pm = pm′.
(b) Price Specialization: If c′ < c, then pm′ ≥pm.
Theorem 11 identifies the fundamental mechanisms that govern equilibrium prices and specialization in global supply chains, offering a significant advance over existing theoretical frameworks. Part (a) extends Samuelson’s factor price equalization result (Samuelson, 1948) by proving that isomorphic production structures generate identical prices, 141

<!-- page 10 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 regardless of the producing country, since prices are uniquely determined by input composition. More importantly, part (b) corrects a limitation in earlier models—such as Costinot et al. (2012)—which assume that countries sort strictly along the supply chain based on productivity. That formulation fails to account for observed configurations where high-productivity countries specialize in upstream intermediates while less productive economies perform final assembly, as seen in the maquiladora industry (Bergin et al., 2009). This model generalizes the underlying logic by showing that countries specialize by price range rather than by position in the value chain. When upstream goods yield greater revenue per unit of labor, more productive countries rationally allocate resources to their production. In doing so, the model provides a unified framework that captures both theoretical consistency and empirical relevance.
Corollary 1. Let p, w be the price and income vectors of an equilibrium characterized by the set of basic techniques γ.
(a) Let c > c′′ > c′ such that pT τ(m, c) −wc = pT τ(m, c′) −wc′ = 0. If τ(n, c′′) ∈γ, then pn = pm.
(b) If pT τ(m′, c) = pT τ(m, c) = wc and pm ≤pm′, then for any good n with pm ≤pn ≤pm′, it holds that pT τ(n, c) = wc.
(c) Suppose all τ(m, c) ∈γ satisfy pm = α > 0 and that kc increases without changing the basic techniques. Then only wc changes.
Corollary 2. Let p, w be the price and income vectors of an equilibrium characterized by the set of basic techniques γ. Then there exist prices PC ≤PC−1 ≤· · · ≤P0 such that P0 = 1, PC = 0, and pT τ(m, c) −wc = 0 if and only if pm ∈[Pc, Pc−1].
These corollaries formalize the stratification of countries into distinct price intervals.
Low-income countries specialize in raw materials with lower prices, consistent with empirical patterns observed by Felipe et al. (2012).
Proposition 2. Consider an equilibrium with a unique labor allocation x but multiple sets of basic techniques. Let γ, γ′ be such sets with associated price and wage vectors p, w and p′, w′, respectively.
(a) If {pm : τ ′(m, c) ∈γ′} ⊆{pn : τ(n, c) ∈γ} for all c, then p = p′ and w = w′.
(b) If γ \ γ′ = {τ(m, c)} and γ′ \ γ = {τ ′(m′, c′)}, then w′ c = wc + βc for some β ∈RC such that βT q = 0.
This proposition demonstrates that wage shifts arise only when price specialization patterns change. If the price sets are preserved, the income distribution remains unchanged. Otherwise, income effects appear as mean-preserving spreads.
3.3

#### Linked Economies and Cascade Effects

We now introduce a final assumption that aligns the model with literature on linear supply chains and highlights cascade dynamics.
Assumption 12. Increasing standardization of processes: ∀i : τi < 0 ⇒|τi| ≥1.
Assumption (A7), used by Grossman and Rossi-Hansberg (2008), ensures that productivity increases along the chain. It provides sufficient structure for analyzing price propagation.
Theorem 13 (Price ordering). Let p, w be the price and income vectors of an equilibrium characterized by the set of basic techniques γ.
(a) If m →m′, then pm′ > pm.
(b) If {τ(m, c), τ(m′, c′)} ⊆γ and m →m′, then c ≥c′.
This result confirms that vertical specialization emerges under A7, even in complex DAGs. It extends the insight of Costinot et al. (2012) beyond linear chains.
Definition 2 (Linked economy). An equilibrium is a linked economy if for each country c, there exists a good m and a country c′̸ = c such that pT τ(m, c) −wc = pT τ(m, c′) −wc′ = 0.
Corollary 3. Consider an economy satisfying assumptions (A1) to (A7) where ∀m < M, the inputs to produce m are m + 1 and labor. Then, any basic set of techniques defines a linked economy.
142

<!-- page 11 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 Linked economies are stylized environments where multiple producers coexist for a given good at zero profit. This captures residual production and overlaps common in observed supply chains (Timmer et al., 2014).
Definition 3 (Price-adjusting algorithm). Let γ be a basic set of techniques. Initialize with wC = α > 0 and let s = C.
1. For all m with τ(m, s) ∈γ and n →m with pn defined, set:
pm = 1 ks ws + X n→m |A(τ(m, s))n|pn !
2. If m is a raw material, set pm = 1 ks ws.
3. Iterate until all pm for τ(m, s) ∈γ are defined.
4. Let Ps = max{pm : τ(m, s) ∈γ} and set ws−1 = ws + Ps(ks−1 −ks).
5. Repeat from step 1 with s = s −1 until s = 1.
Theorem 14. Consider an economy that satisfies assumptions (A1) to (A7).
(a) The price-adjusting algorithm is well defined.
(b) If γ defines a linked economy, the algorithm determines prices and wages. The Pc values correspond to Corol- lary 2.
The algorithm offers a constructive solution to equilibrium prices and incomes. It implies that productivity shocks propagate downstream, as in Acemoglu et al. (2012).
Proposition 3. Consider a linked economy defined by γ. Let k′ c = βkc for c̸ = C with unchanged basic techniques.
Denote the equilibria before and after the change as p, w and p′, w′, normalized by wC = 1.
(a) If ∃m, n with {τ(m, c), τ(n, c)} ⊆γ and pm̸ = pn:
i w′ c′ = wc′ for c′ > c.
ii w′ c = wc + (1 −β)kc.
iii For c′ < c′′ < c, w′ c′ < wc′ and |w′ c′ −wc′| > |w′ c′′ −wc′′|.
(b) If the shock occurs in c = C, then for c′ < c′′ < C, w′ c′ < wc′ and |w′ c′ −wc′| > |w′ c′′ −wc′′|.
In linked economies, productivity shocks do not always alter the equilibrium set of techniques. When they do, wages adjust across upstream countries in a coordinated way, leading to discrete shifts in inequality.
3.4

#### Illustrative Example: Six-Good, Five-Country Chain

To make the algorithm concrete, consider a linear supply chain of six goods, 1 →2 →3 →4 →5 →6, where good 6 is the final good. There are five countries indexed by productivity k1 > k2 > k3 > k4 > k5, and we take unit Leontief coefficients (Assumption A7). Initialize the recursion with w5 = α = 1. In the baseline calibration we set k1 = 1.60, k2 = 1.35, k4 = 1.05, k5 = 0.88, and take the midpoint k3 = k2+k4 2 = 1.20.
143

<!-- page 12 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 Stage-by-stage pricing (country-by-country) At each stage s ∈{5, 4, 3, 2, 1}, holding (ws, ks) fixed, prices along the chain are computed recursively as p(s) 1 = ws ks , p(s) m = ws + p(s) m−1 ks (m = 2, . . . , 6), and we define Ps := maxm p(s) m = p(s) 6 . Wages update upstream according to ws−1 = ws + Ps (ks−1 −ks) (s = 5, 4, 3, 2), producing a linked economy per Definition 2. Evaluated at the midpoint calibration:
Stage s = 5 (k5 = 0.88, w5 = 1):
(p(5) 1 , . . . , p(5) 6 ) ≈(1.14, 2.43, 3.90, 5.56, 7.45, 9.61), P5 = 9.61.
Update w4 = 1 + P5(1.05 −0.88) = 2.63.
Stage s = 4 (k4 = 1.05, w4 = 2.63):
(p(4) 1 , . . . , p(4) 6 ) ≈(2.51, 4.89, 7.19, 9.54, 11.66, 13.37), P4 = 13.37.
Update w3 = 2.63 + P4(1.20 −1.05) = 4.64.
Stage s = 3 (k3 = 1.20, w3 = 4.64):
(p(3) 1 , . . . , p(3) 6 ) ≈(3.87, 7.09, 9.76, 12.09, 13.78, 15.43), P3 = 15.43.
Update w2 = 4.64 + P3(1.35 −1.20) = 6.95.
Stage s = 2 (k2 = 1.35, w2 = 6.95):
(p(2) 1 , . . . , p(2) 6 ) ≈(5.15, 8.98, 11.67, 13.74, 15.10, 16.58), P2 = 16.58.
Update w1 = 6.95 + P2(1.60 −1.35) = 11.10.
Stage s = 1 (k1 = 1.60, w1 = 11.10): The final prices are (p1, . . . , p6) ≈(6.94, 11.27, 13.98, 15.68, 16.73, 17.40), with P1 = 17.40. The corresponding wage vector is (w1, w2, w3, w4, w5) ≈(11.10, 6.95, 4.64, 2.63, 1.00).
Comparative statics with respect to k3 The next two figures show how prices and wages evolve as country 3’s productivity k3 moves strictly between k2 and k4, never coinciding with either. The code to reproduce the graphs is in C.
Figure 2 shows how changes in productivity can generate non-linear effects on prices. At the beginning of the transition, prices of some goods even rise, as higher productivity in country 3 increases demand for its upstream inputs.
This in turn pushes up prices throughout the lower stages of the chain before downstream adjustments reduce them again.
Figure 3 shows that productivity growth in country 3 has a clear positive effect on its own wage, while exerting downward pressure on the most productive countries as competition intensifies. At the early stages, however, the more productive countries temporarily benefit from the initial rise in prices; it is only later, as competitive effects dominate, that their relative wages decline. Overall, the wage distribution becomes more compressed, illustrating how productivity gains in middle-income economies can reshape inequality along the global supply chain.
144

<!-- page 13 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 9 12 15 1.05 1.10 1.15 1.20 1.25 1.30 1.35 Country 3 productivity  (k3) Price Good Good_1 Good_2 Good_3 Good_4 Good_5 Good_6

### Equilibrium Prices by Good (6-good chain)

Figure 2: Evolution of prices.
3 6 9 1.05 1.10 1.15 1.20 1.25 1.30 1.35 Country 3 productivity  (k3) Wage Country Country_1 Country_2 Country_3 Country_4 Country_5

### Equilibrium Wages by Country

Figure 3: Evolution of wages.
145

<!-- page 14 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 4

## Conclusions

This paper presents a general equilibrium model of global supply chains that advances the theoretical understanding of production networks. By modeling production as a direct acyclical graph (DAG), the framework captures the hierarchical and interdependent nature of modern supply chains, overcoming the linear or factor-based simplifications common in previous models. The formulation remains analytically tractable while permitting complex intersectoral and cross-country linkages.
The model yields several novel insights. First, equilibrium prices are determined solely by the structure of produc- tion rather than by geographical origin, shifting the analytical focus from location to topology. Second, specialization patterns emerge endogenously from revenue-based comparative advantage, allowing productive countries to specialize upstream or downstream depending on price structures. Third, productivity shocks propagate asymmetrically through the network, clarifying the heterogeneous impact of global disruptions. Finally, the model permits robust wage and price outcomes even under multiple production techniques, contributing to a more general and flexible theory of trade and income distribution.
These mechanisms produce empirically testable predictions that are consistent with observed patterns in global value chains. The model explains price equalization across standardized goods, the wage stability in sectors with diverse production technologies, and the stratification of countries by production roles. It also accounts for the propagation of shocks across interconnected economies, offering a unified explanation for stylized facts that previous models treated in isolation.
Beyond its theoretical contributions, the model offers practical implications. It introduces a recursive pricing algorithm that enables counterfactual simulations and policy analysis, providing a foundation for evaluating upgrading strategies, supply chain resilience, and the design of trade interventions.
This aligns with growing demands for structural frameworks that are both theoretically sound and computationally tractable.
Two promising directions emerge for future work. First, the model could be extended to incorporate dynamic accumulation of production capabilities and sector-specific know-how.
In this respect, the literature on economic complexity—particularly the work of Hidalgo and Hausmann (2009)—offers a compelling path. Embedding capability- based proximity into the DAG framework would enable the analysis of how countries with similar technological profiles exhibit correlated productivity levels and how adjacency in the product space facilitates endogenous learning and upgrading. This extension would link static network models with dynamic trajectories of industrial development.
Second, the model can be applied to empirical case studies to evaluate how political decisions, institutional constraints, and trade frictions generate deviations from the theoretical equilibrium. By simulating observed distortions as departures from the model’s baseline predictions, the framework can serve as a diagnostic tool to distinguish structural inefficiencies from policy-induced misalignments. Such applications would bridge the gap between abstract theoretical models and the design of real-world industrial and trade policy.
In summary, this model establishes a new benchmark for the structural analysis of global supply chains, combining theoretical rigor with empirical relevance and providing a flexible foundation for both future theoretical inquiry and applied policy design.

## Glossary of Terms and Notation

m Index for goods in the production network.
c Index for countries.
τ(m, c) Production technique: the set of inputs (including labor) required to produce good m in country c.
kc Productivity of country c; higher kc implies greater efficiency in transforming inputs into outputs.
wc Wage rate in country c.
pm Price of good m.
γ Set of active (selected) production techniques used in equilibrium.
m →m′ Good m′ is produced using good m as an input.
Prod(m) Production structure of good m: the subgraph of all goods with a path leading to m.
Raw material A good with no input dependencies (zero in-degree); produced using only labor.
146

<!-- page 15 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 Intermediate good A good that combines two or more inputs; used to produce other goods.
Final good A good with no output dependencies (zero out-degree); consumed directly.
Linked economy A set of countries connected through shared goods in a supply chain network.
Isomorphic input graph A production subgraph that is structurally identical (up to relabeling) across countries.
Revenue per worker Total value of output per unit of labor input; used to determine specialization decisions.
Price-adjusting algorithm A recursive procedure to determine equilibrium prices across the DAG.

## Funding Statement

This research received no external funding.

## Acknowledgments

The author would like to thank the editor and the reviewers who reviewed this article.

## Conflict of interest

The author claims that the manuscript is completely original. The author also declares no conflict of interest.

## References

Acemoglu, D., Carvalho, V.M., Ozdaglar, A., Tahbaz-Salehi, A., 2012. The network origins of aggregate fluctuations.
Econometrica 80, 1977–2016.
Antràs, P., 2004. Global sourcing. Journal of Political Economy 112, 552–580.
Antràs, P., 2020. Conceptual aspects of global value chains. World Bank Economic Review 34, 551–574.
Antràs, P., Chor, D., 2022. Global Value Chains. volume 5. Elsevier.
Arrow, K., 1951. Proofs of substitution theorem: General case, in: Koopmans, T. (Ed.), Activity Analysis of Produc- tion and Allocation. Yale University Press, pp. 155–164.
Baldwin, R., Venables, A.J., 2013. Spiders and snakes: Offshoring and agglomeration in the global economy. Journal of International Economics 90, 245–254.
Bank, A.D., 2021a. Asian Development Outlook 2021: Financing a Green and Inclusive Recovery. Asian Development Bank.
Bank, W., 2021b. Global Economic Prospects, June 2021. World Bank, Washington, DC.
Bergin, P.R., Feenstra, R.C., Hanson, G.H., 2009. Offshoring and volatility: Evidence from mexico’s maquiladora industry. American Economic Review 99, 1664–1671.
Blyde, J.S., 2014. The participation of mexico in global supply chains: The challenge of adding mexican value. Applied Economics Letters 21, 501–504. May.
Bouït, A., Estrades, C., Laborde, D., 2013. A global assessment of the economic effects of export taxes. The World Economy 36, 1333–1354.
Bradley, S., Hax, A., Magnanti, T., 1977. Applied Mathematical Programming. Addison Wesley.
147

<!-- page 16 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 Constantinescu, I.C., Mattoo, A., Ruta, M., 2020. The global trade slowdown: Cyclical or structural?
The World Bank Economic Review 34, 121–142.
Costinot, A., Vogel, J., Wang, S., 2012. An elementary theory of global supply chains. The Review of Economic Studies 80.0, 109–144.
Dhyne, E., Kikkawa, A.K., Kong, X., Mogstad, M., Tintelnot, F., 2023. Endogenous production networks with fixed costs. Journal of International Economics 145, 103841.
Evenett, S., Jakubik, A., Martín, F., Ruta, M., 2024. The return of industrial policy in data. The World Economy 47, 2762–2788. DOI: 10.1111/twec.13608.
Felipe, J., Kumar, U., Abdon, A., Bacate, M., 2012. Product complexity and economic development. Structural Change and Economic Dynamics 23, 36–68.
Franke, H., Chae, S., Foerstl, K., 2024. Toward a configurational understanding of global supply chain complexity.
Journal of Business Logistics 45, e12371.
Gereffi, G., 2014. Global value chains in a post-washington consensus world. Review of International Political Economy 21.0, 9–37.
Grossman, G.M., Helpman, E., 2002. Integration versus outsourcing in industry equilibrium. Quarterly Journal of Economics 117, 85–120.
Grossman, G.M., Rossi-Hansberg, E., 2008. Trading tasks: A simple theory of offshoring. American Economic Review 98.0, 1978–97.
Hidalgo, C.A., Hausmann, R., 2009. The building blocks of economic complexity. Proceedings of the National Academy of Sciences (PNAS) 106.0, 10570–10575.
Jones, L., Krulikowski, S., Lotze, N., Schreiber, S., 2023. U.S. Exposure to the Taiwanese Semiconductor Industry.
Economics Working Paper 2023–11–A. U.S. International Trade Commission.
Kohler, W., 2004. Aspects of international fragmentation. Review of International Economics 12, 793–816.
Kremer, M., 1993. The o-ring theory of economic development. The Quarterly Journal of Economics 108.0, 551–575.
Lee, C., 2022. Global Supply-Chain Reform and Taiwan: Implications for Economic Security and Industry Strategy.
Technical Report. French Institute of International Relations (IFRI).
Lee, C., Chen, W., 2016. A value-added analysis of trade in taiwan and korea’s ict industries. Journal of Knowledge Management 20, 1153–1169.
Leontief, W., 1951. Input-output economics, in: The Structure of American Economy, 1919–1939. Oxford University Press, pp. 19–85.
Marcato, M.B., Baltar, C.T., 2020. Economic upgrading in global value chains: Concepts and measures. Revista Brasileira de Inovação 19, 1–25.
Organisation for Economic Co-operation and Development, 2024. OECD Statistics and Data Outputs. Technical Report. OECD.
Ostrovsky, M., 2008. Stability in supply chain networks. American Economic Review 98.0, 897–923.
Rahman, M., Bhattacharya, D., Moazzem, K.G., 2008. Bangladesh Apparel Sector in Post MFA Era: A Study on the Ongoing Restructuring Process. Centre for Policy Dialogue, Dhaka, Bangladesh.
Samuelson, P.A., 1948. International trade and the equalisation of factor prices. The Economic Journal 58.0, 163–184.
Shiozawa, Y., 2007. A new construction of ricardian trade theory — a many-country, many-commodity case with inter- mediate goods and choice of production techniques, in: Nishibe, B., Shiozawa, Y. (Eds.), Evolutionary Controversies in Economics. Springer, pp. 57–106.
Timmer, M.P., Erumban, A.A., Los, B., Stehrer, R., de Vries, G.J., 2014. Slicing up global value chains. Journal of Economic Perspectives 28.0, 99–118.
148

<!-- page 17 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 UNCTAD, 2020. World Investment Report 2020: International Production Beyond the Pandemic. United Nations Conference on Trade and Development, Geneva.
UNIDO, 2018. Industrial Development Report 2018: Demand for Manufacturing: Driving Inclusive and Sustainable Industrial Development. United Nations Industrial Development Organization, Vienna.

## A


## Mathematical Notation

This appendix defines the mathematical notation used throughout the main text and proofs. Notation introduced directly in B and not repeated here is defined locally within that section.

#### Vectors

Let x, y ∈Rn:
• All vectors are column vectors unless otherwise stated.
• xi denotes the i-th component of vector x.
• x−i is a vector in Rn−1 formed by removing the i-th component of x.
• x ≪y means ∀i : xi < yi.
• x < y means ∀i : xi ≤yi and ∃j : xj < yj.
• x ≤y means either x < y or x = y.
• e(i) is the i-th canonical basis vector: e(i)i = 1, and e(i)j = 0 for all j̸ = i.
• I denotes a vector of ones.
• O denotes a vector of zeros.

#### Matrices

Let A ∈Rn×m:
• AT is the transpose of matrix A.
• Aij denotes the element at row i and column j.
• Ai. is the i-th row of A, and A.j is the j-th column.
• A−i. is the matrix in R(n−1)×m obtained by removing the i-th row. Similarly, A.−j is the matrix with the j-th column removed.
• I denotes the identity matrix of appropriate dimension.
• Let B ∈Rn×k. Then, A B ∈Rn×(m+k) is a matrix whose first m columns are those of A, and last k columns are those of B.
• If B ∈Rk×m, then the vertical stacking A B  ∈R(n+k)×m is defined as   AT BT T .
149

<!-- page 18 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160

## B


## Mathematical Proofs


#### B.1


#### Lemmata

Lemma 1. Let Ξ be the set of production techniques in the economy. Define the production set:
P(q) := n y ∃x ∈R|Ξ|, x ≥O, y = A(Ξ)T x, q ≥I(Ξ)T x o and the efficient frontier:
E(q) := {y ∈P(q) | ∄y′ ∈P(q) : y′ > y} .
Then the following properties hold:
(a) P(q) is a strict superset of OM×1.
(b) P(q) is convex.
(c) P(q) is compact.
(d) If y ∈E(q), then ∃x ≥O such that A(Ξ)T x = y and I(Ξ)T x = q.
(e) There exists y ∈E(q) such that ∀x ∈E(q), y1 ≥x1 and y−1 = O.
Proof (a) Define ξc := {τ(1, c), . . . , τ(M, c)} as the set of techniques in country c. By assumption (A3), for every c there exists xc > O such that A(ξc)T xc ≫O. Construct:
xT := h q1 xT 1 IxT 1 · · · qC xT CIxT C i Reordering A(Ξ) as A(Ξ) =   A(ξ1) ...
A(ξC)  , we find:
x ≥O, I(Ξ)T x = q, A(Ξ)T x ≫O ⇒A(Ξ)T x ∈P(q) Also, OM×1 ∈P(q) trivially.
(b) If y, y′ ∈P(q), then ∃x, x′ ≥O such that A(Ξ)T x = y, A(Ξ)T x′ = y′. Then, for all α ∈[0, 1]:
αx + (1 −α)x′ ≥O, I(Ξ)T (αx + (1 −α)x′) ≤q ⇒αy + (1 −α)y′ ∈P(q) (c) Define Q = qT I. P(q) lies in a compact hypercube bounded above by Q and the maximum input coefficients.
To prove closedness, let yi →y with yi ∈P(q). Then xi →x with A(Ξ)T x = y, x ≥O, I(Ξ)T x ≤q ⇒y ∈P(q).
(d) If y ∈P(q) and I(Ξ)T x < q, then slack labor exists. By (A3), this can produce more without net loss, violating Pareto efficiency. Hence I(Ξ)T x = q ⇒y ∈E(q).
(e) From (a)–(c) and Weierstrass, E(q) attains a maximum in y1. Suppose y−1̸ = O. Then a reduction in non-1 goods reallocates labor to raise y1 (by A3), contradicting maximality. Thus y−1 = O.
■ Lemma 2. The matrix R, as defined in Theorem 7, has full row rank.
150

<!-- page 19 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 Proof Step 1: The first M −1 rows are linearly independent.
Let ξc be defined as in the proof of Lemma 1. By the results of Arrow (1951) and assumption (A3), there does not exist y̸ = O(M−1)×1 such that:
y⊤A(Ξ)⊤ .−1 = O⊤ |Ξ|×1 and A(ξc) 0 y  = OM×1.
This implies that A(Ξ) is invertible.
Step 2: The last C rows of R are linearly independent.
Each column of I(Ξ) is a canonical vector, so the rows of I(Ξ)⊤are linearly independent.
Step 3: The first M −1 rows are linearly independent from the last C rows.
Assume, for contradiction, that there exists y̸ = O(M−1)×1 such that:
y⊤A(Ξ)⊤ .−1 = I(Ξ)⊤ .c.
This implies:
A(ξc).−1y = IM×1.
Since A(ξc) is invertible, define t = A(ξc)−1IM×1 ≫0 (by Arrow, 1951). Therefore:
IM×1 = M X i=1 tiA(ξc).i = M X i=2 yiA(ξc).i, which implies:
A(ξc).1 = pi −yi p1 M X i=2 A(ξc).i.
This contradicts the invertibility of A(ξc). Hence, no such y exists, and the first M −1 rows are linearly independent from the last C rows.
Step 4: Conclusion.
From Steps 1–3, the total M −1 + C rows of R are linearly independent. Thus, R has full row rank.
■

#### B.2


#### Theorems

Proof of Theorem 7 From Lemma 1 parts (a) and (c), there exists a vector x that maximizes the production of the final good. Moreover, parts (d) and (e) imply that A(Ξ)T .−1x = O(M−1)×1 and I(Ξ)T x = q, meaning all the constraints of the linear program bind at the optimum.
By the Karush-Kuhn-Tucker (KKT) conditions, x solves the linear program if and only if there exist:
• a vector of shadow prices λT =  pT wT  ≫0, • a vector of reduced costs s ≥0, such that:
Rx =  O(M−1)×1 q  , RT λ + s = A(Ξ).1, x ≥O, s ≥O, x⊤s = 0.
151

<!-- page 20 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 The fundamental theorem of linear programming states that the solution lies either at an extreme point of the feasible region or on a face of it. Thus, at most M + C −1 variables in x are non-zero—the so-called basic variables—corresponding to a subset of techniques γ, referred to as the basic techniques.
Since R is full row rank (Lemma 2), we can partition its columns into:
B :=  −A(γ)T .−1 I(γ)T  , N :=  −A(Ξ \ γ)T .−1 I(Ξ \ γ)T  , where B is invertible.
Then, based on the KKT conditions:
x = xB xN  , s = sB sN  , R = B N , xB = B−1 O(M−1)×1 q  , xN = O, sB = O, sN = A(Ξ \ γ).1 −N T λ, λ = (BT )−1A(γ).1.
Since all constraints bind at the optimum, intermediate goods and labor markets clear, satisfying equilibrium conditions (3), (4), and (5). By Walras’ Law, the final good market also clears.
Regarding prices: from BT λ = A(γ).1, we obtain:
−A(γ).−1 I(γ) p w  = A(γ).1, which implies:
A(γ)p = I(γ)w.
Thus, all basic techniques—a superset of active techniques—earn zero profit, satisfying equilibrium condition (2).
For non-basic techniques:
N T λ + sN = A(Ξ \ γ).1 ⇒ A(Ξ \ γ)p + sN = I(Ξ \ γ)w ⇒ A(Ξ \ γ)p ≤I(Ξ \ γ)w, implying that all inactive techniques earn non-positive profit, satisfying equilibrium condition (1).
Therefore, the vectors x, p, and w define an equilibrium in quantities, prices, and wages that satisfy all conditions.
To prove the converse, note that if x, p, and w satisfy the equilibrium conditions, then they also satisfy the KKT conditions. Hence, x solves the corresponding linear program.
■ Proof of Theorem 8 Part (a):
Assume τ(m, c) ∈γ. Then pT τ(m, c) = wc and pT τ(m, c′) ≤wc′. Therefore, pT (τ(m, c′) −τ(m, c)) ≤wc′ −wc.
By assumption (A4), pT (τ(m, c′) −τ(m, c)) = pm(τ(m, c′)m −τ(m, c)m), so wc′ −wc ≥pm(τ(m, c′)m −τ(m, c)m).
Part (b):
Suppose pm(τ(m, c′)m −τ(m, c)m) ≤wc′ −wc and pm′(τ(m′, c′)m′ −τ(m′, c)m′) ≥wc′ −wc.
152

<!-- page 21 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 Then, pm(τ(m, c′)m −τ(m, c)m) ≤pm′(τ(m′, c′)m′ −τ(m′, c)m′).
If τ(m, c′)m > τ(m, c)m, then 1 ≤pm′(τ(m′, c′)m′ −τ(m′, c)m′) pm(τ(m, c′)m −τ(m, c)m) .
Part (c):
If both τ(m, c), τ(m, c′) ∈γ, then pT τ(m, c) = wc, pT τ(m, c′) = wc′.
Subtracting yields:
pT (τ(m, c′) −τ(m, c)) = wc′ −wc = pm(τ(m, c′)m −τ(m, c)m).
■ Proof of Theorem 11 Part (a):
Let m, m′ be raw materials with {τ(m, c), τ(m′, c′)} ⊆γ. Assume pm > pm′. Then, from equilibrium conditions:
kcpm = wc, kc′pm′ = wc′.
It follows that kc′pm −wc′ > 0, which contradicts equilibrium condition (1). Hence, pm = pm′.
Part (b):
Let a, b be goods with isomorphic production graphs. Consider m ∈arg min x∈Nodes(a){rd(x) | px̸ = px′}, where x′ ∈Nodes(b) satisfies Prod(x) = Prod(x′), and assume pm > pm′.
Since all inputs n →m have rd(n) < rd(m), their prices must be equal. Now, since {τ(m, c), τ(m′, c′)} ⊆γ, we have:
pT τ(m, c) = wc, pT τ(m′, c′) = wc′.
Replacing pm with pm′ in the cost of τ(m′, c′) results in a lower cost, violating profit-maximization. Hence, pm = pm′.
Part (c):
If kc′ ≥kc, then from Theorem 8:
1 ≤pm′(kc′ −kc) pm(kc′ −kc) = pm′ pm , implying pm ≤pm′.
■ Proof of Theorem 13 Part (a):
Let τ(m′, c′) ∈γ and suppose m →m′. Then:
pm′ = 1 kc′   −pT −m′τ(m′, c′)−m′ + wc′ > pm|τ(m′, c′)m| kc′ ≥pm.
Part (b):
If m →m′, then pm′ > pm. From Theorem 11, this implies c ≥c′. If there exists a path:
m →ma1 →· · · →man →m′, with each τ(mai, cai) ∈γ, then c ≥ca1 ≥· · · ≥can ≥c′.
■ 153

<!-- page 22 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 Proof of Theorem 14 Part (a): Well-definedness of the algorithm.
Let A be the set of goods not yet priced. Let m′ ∈arg min{rd(m) | m ∈A}. Suppose τ(m′, C) ∈γ. Then m′ must use some unpriced input n with rd(n) < rd(m′), a contradiction. Thus, all C-produced goods are priced, and wC−1 is defined.
By induction, if all pn for n used in country c + 1 are defined, then wc is defined. If any m ∈A remains unpriced, then it either uses an unpriced n (contradicting minimal rd) or wc is undefined (contradicting the assumption). Hence, A = ∅, and the algorithm is well-defined.
Part (b): Correctness of the algorithm.
Let w′, p′ be equilibrium wages and prices. Normalize wC = w′ C = α.
Base Case: For country C: All pm = p′ m by recursive computation since inputs have rd(n) < rd(m) and equal prices.
Inductive Step: Assume wc′ = w′ c′ and pm = p′ m for all c′ > c. Since the economy is linked, there exists m such that:
(p′)T τ(m, c + 1) −w′ c+1 = (p′)T τ(m, c) −w′ c = 0.
Then:
w′ c = w′ c+1 + p′ m(kc −kc+1) = wc.
Let m′ ∈arg min{rd(m) | τ(m, c) ∈γ, pm̸ = p′ m}. Then:
pm′ = 1 kc wc + X n→m′ |A(τ(m′, c))n|pn !
= p′ m′.
Hence, by induction, w = w′ and p = p′. The computed prices and wages match the equilibrium and satisfy Corollary 2.
■

#### B.3


#### Propositions

Proof of Proposition 1 This proof uses the notation of the proof of Theorem 7.
Part (a): Given the optimization program, λi = ∂Ω ∂bi , where b = O(M−1)×1 q  .
By definition, λ = p w  , so wc = ∂Ω ∂qc .
Part (b): By the KKT conditions, λ = p w  = −A(γ).−1 I(γ)−1 A(γ).1 Hence, given a set of basic techniques, the prices are uniquely determined and are independent of the labour quantities.
■ 154

<!-- page 23 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 Proof of Proposition 2 Both parts of the proof rely on the simplex algorithm for dynamic programming, using terminology from the pivoting technique in Bradley et al. (1977).
Part (a): The inclusion {pm : τ ′(m, c) ∈γ′} ⊆{pn : τ(n, c) ∈γ} implies that for every τ ′(m, c) ∈γ′, there exist τ(m′, c), τ(m′′, c) ∈γ such that pm′ ≤pm ≤pm′′. By Corollary 1, this means pT τ ′(m, c) −wc = 0 for all τ ′(m, c) ∈γ′.
From Theorem 7, p and w are the price and income vectors of γ′.
Part (b): Let τ(m, c) be the first basic vector in γ. Since the optimal worker schedule x is unique, x1 = 0. Then:
e(1)T B−1 O(M−1)×1 q  = 0 Let z ∈RC be the last C components of [B−1]1.. Then zT q = 0.
The reduced costs under γ are:
s =  0 A(Ξ).1N −N T λ  =   A(γ) 1 p  −I(γ)w A(Ξ \ γ) 1 p  −I(Ξ \ γ)w   Let s(m′,c′) = pT τ ′(m′, c′) −wc′. Upon pivoting, the new reduced costs are:
s′ = s −s(m′,c′) U1 [V1.]T where:
U = B−1 A(τ ′(m′, c′)) I(τ ′(m′, c′))  , V = B−1R Therefore, the updated shadow prices are:
p′ w′  = p w  −s(m′,c′) U1 [(B−1)1.]T Hence, β = − s(m′,c′) U1 z, and:
βT q = −s(m′,c′) U1 zT q = 0 ■ Proof of Proposition 3 Part (a): Given that the basic techniques are unchanged, points (i) and (ii) follow directly from the pricing algorithm and step 3 of the updating algorithm.
For (iii), we use induction on goods and countries.
Base case (Country c): Let τ(m, c) ∈γ with pm > max{pj : τ(j, c + 1) ∈γ}. Then, if m is updated in the first iteration:
p′ m = 1 βkc wc + (1 −β)kc + X n→m |A(τ(m, c))n|pn !
= (1 −β)kc β + pm β < pm And for all inputs, |p′ n −pn| = 0 < |p′ m −pm|.
Induction step (Good level): Assume for all prices updated up to iteration i in c that j →k ⇒|pk −p′ k| > |pj −p′ j| and pk > p′ k. Then in iteration i + 1:
p′ m = 1 βkc wc + (1 −β)kc + X n→m |A(τ(m, c))n|p′ n !
< pm And:
pm −p′ m = 1 kc X n→m |A(τ(m, c))n|(pn −p′ n) !
+ β −1 βkc wc + kc + X n→m |A(τ(m, c))n|p′ n !
155

<!-- page 24 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 Since all terms are positive, |pm −p′ m| > |pn −p′ n|. Thus, the property holds by induction.
Now consider country c −1. From the price adjustment step:
w′ c−1 −wc−1 = w′ c −wc + p′ m(kc−1 −βkc) −pm(kc−1 −kc) = (1 −β)kc + (p′ m −pm)kc−1 + pmkc −p′ mβkc < 0 Induction step (Country level): Assume that if k is updated at any iteration between country C and the i-th of c′, we have j →k ⇒|pk −p′ k| > |pj −p′ j| and p′ k < pk, and also w′ c′ < wc′.
Let m′ be updated in iteration i + 1 of c′. Then:
pm′ −p′ m′ = 1 kc′ wc −w′ c + X n→m |A(τ(m, c))n|(pn −p′ n) !
> 0 As all terms are positive, ∀j →m: |pm −p′ m| > |pj −p′ j|. The condition thus holds throughout c′. Also:
wc′−1 −w′ c′−1 = wc′ −w′ c′ + (PC′ −P ′ C′)(kc−1 −kc) > 0 Hence, by induction, ∀c′ < c, w′ c′ < wc′, and:
(wc′−1 −w′ c′−1) −(wc′ −w′ c′) = (PC′ −P ′ C′)(kc−1 −kc) > 0 ⇒|wc′−1 −w′ c′−1| > |wc′ −w′ c′| Thus, part (iii) is proven via double induction.
Part (b): Repeat the argument in (a), noting that wC −w′ C = 0 due to the normalization condition.
■

#### B.4


#### Corollaries

Proof of Corollary 1 Part (a): From Theorem 11, price specialisation implies pm ≤pn (with respect to c) and pn ≤pm (with respect to c′). Therefore, pm = pn.
Part (b): Assume pT τ(n, c) −wc < 0. Then, in equilibrium, there exists c′ such that pT τ(n, c′) −wc′ = 0.
If c′ > c, then:
pm(kc′ −kc) ≤wc′ −wc and pn(kc −kc′) < wc −wc′ which implies:
pn(kc −kc′) < wc −wc′ ≤pm(kc −kc′) ⇒pn > pm But by Theorem 11, pn = pm′. Contradiction. The case for c′ < c is symmetric.
Part (c): Define p′, w′ such that p = p′, w−c = w′ −c, and w′ c = wc + α(kc′ −kc) > wc. By direct calculation, p′, w′ satisfy the new equilibrium conditions. Therefore, the only value that changed after the shock was wc.
■ 156

<!-- page 25 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 Proof of Corollary 2 Define:
P ′ c = min{pm | pT τ(m, c) −wc = 0}, P ′′ c = max{pm | pT τ(m, c) −wc = 0} Theorem 11 implies P ′′ c ≤P ′ c−1. If P ′′ c = P ′ c−1, then set Pc−1 = P ′ c−1; otherwise, define:
Pc−1 = P ′′ c + P ′ c−1 2 From Corollary 1:
pm ∈[P ′ c, P ′′ c ] ⇒pT τ(m, c) −wc = 0 and by Theorem 11:
pm ∈R \ [P ′ c, P ′′ c ] ⇒pT τ(m, c) −wc < 0 ■ Proof of Corollary 3 From Theorem 13, all goods in the economy have different prices.
Consider c < c′ and a good m such that {τ(m, c), τ(m, c′)} ⊆γ.
From Corollary 1, for all c < c′′ < c′ and for all m′̸ = m, it holds that pT τ(m′, c′′) −wc′′ < 0.
Since each country must produce something to clear its labor market in equilibrium, this implies τ(m, c′′) ∈γ for all c < c′′ < c′.
Moreover, assumption (A7) and Theorem 8 imply that there do not exist m, m′, c, c′ such that {τ(m, c), τ(m, c′), τ(m′, c), τ(m γ. Hence, for each country c, at most two goods are produced by another country—one shared with c + 1, and one with c −1. Countries 1 and C are exceptions, sharing only one good with a neighbor.
Finally, Theorem 7 asserts that there are exactly M + C −1 basic techniques. Thus, this structure must be realized, and:
∀c, ∃!m : {τ(m, c), τ(m, c + 1)} ⊆γ ■

## C


## Example code

Listing 1: R code for the six goods five countries example # ============================================ # Prices & Wages Only --- Publication -ready (BW) # Model: linear chain 1->2->...->M, unit coeffs # ============================================ # install.packages(c(" dplyr ","tidyr "," ggplot2 ")) # if needed library(dplyr) library(tidyr) library(ggplot2) # ------------------------------- # Model settings # ------------------------------- M <- 6 goods <- as.character (1:M) # "1" ... "6" f <- as.character(M) # final good = "6" C <- 5 countries <- as.character (1:C) # "1"( most productive) ... "5"( least) # (Optional helper from your original; unused here) 157

<!-- page 26 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 parents_of <- function(m) if (m == "1") character (0) else as.character(as.integer (m) - 1L) # ------------------------------- # Price -wage recursion (algorithm only) # Chain with unit coefficients (A7) # ------------------------------- price_wage_algorithm <- function(k, alpha = 1) { # accept any naming/order; enforce canonical order stopifnot(setequal(names(k), countries)) k <- k[countries] topo <- goods w <- setNames(rep(NA_real_, C), countries) P <- setNames(rep(NA_real_, C), countries) # kept for clarity; not used downstream p_stage <- vector("list", C) # Normalize least -productive wage w[C] <- alpha # Iterate from least productive (C) to most (1) for (si in C:1) { s <- as.character(si) p_s <- setNames(rep(NA_real_, M), goods) for (m in topo) { if (m == "1") { p_s[m] <- w[s] / k[s] # raw: labor only } else { prev <- as.character(as.integer(m) - 1L) p_s[m] <- (w[s] + p_s[prev ]) / k[s] # p_m = (w_s + p_{m -1})/k_s } } p_stage [[si]] <- p_s P[s] <- max(p_s) if (si > 1) { s_prev <- as.character(si - 1L) w[s_prev] <- w[s] + P[s] * (k[s_prev] - k[s]) # wage recursion } } list(p = p_stage [[1]] , w = w) } # ------------------------------- # Productivities: vary k3 strictly between k2 and k4 # ------------------------------- k1 <- 1.60 k2 <- 1.35 k4 <- 1.05 k5 <- 0.88 n_steps <- 25 k3_path <- seq(k2 - 0.01, k4 + 0.01, length.out = n_steps) stopifnot(all(k3_path < k2), all(k3_path > k4)) # ------------------------------- # Run scenarios (algorithm only) # ------------------------------- prices_ts <- vector("list", n_steps) wages_ts <- vector("list", n_steps) 158

<!-- page 27 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 for (t in seq_len(n_steps)) { k3 <- k3_path[t] k <- c("1" = k1 , "2" = k2 , "3" = k3 , "4" = k4 , "5" = k5) alg <- price_wage_algorithm(k, alpha = 1) p_final <- alg$p w <- alg$w prices_ts[[t]] <- data.frame( k3 = k3 , good = as.integer(names(p_final)), price = as.numeric(p_final) ) wages_ts[[t]] <- data.frame( k3 = k3 , country = as.integer(names(w)), wage = as.numeric(w) ) } prices_df <- bind_rows(prices_ts) wages_df <- bind_rows(wages_ts) # ------------------------------- # BW -friendly , publication theme # ------------------------------- theme_pub <- function(base_size = 12) { theme_bw(base_size = base_size) + theme( panel.grid.major = element_line(linewidth = 0.25, linetype = "dotted"), panel.grid.minor = element_blank (), legend.position = "right", legend.title = element_text(size = base_size), legend.text = element_text(size = base_size - 1), plot.title = element_text(face = "bold", hjust = 0, size = base_size + 2), axis.title = element_text(size = base_size), axis.text = element_text(size = base_size - 1) ) } # Line/shape sets (grayscale -safe) good_levels <- paste0("Good_", 1:M) linetypes_good <- c("solid","dashed","dotted","dotdash","longdash","twodash") shapes_good <- c(16, 1, 17, 15, 7, 8) country_levels <- paste0("Country_", 1:C) linetypes_cty <- c("solid","dashed","dotted","dotdash","longdash") shapes_cty <- c(16, 1, 17, 15, 7) # ------------------------------- # Figure 1: Prices by good (x = k3) # ------------------------------- prices_df_bw <- prices_df %>% mutate(good_f = factor(paste0("Good_", good), levels = good_levels)) p_prices <- ggplot( prices_df_bw , aes(x = k3 , y = price , group = good_f, linetype = good_f, shape = good_f) ) + 159

<!-- page 28 -->

Salamanca Journal of Economic Analysis 2026 5 (1) 133–160 geom_line(linewidth = 0.8) + geom_point(size = 2) + scale_linetype_manual(values = linetypes_good , name = "Good") + scale_shape_manual(values = shapes_good , name = "Good") + labs( title = "Equilibrium␣Prices␣by␣Good␣(6-good␣chain)", x = expression(paste("Country␣3␣productivity␣␣(", k[3], ")")), y = "Price" ) + theme_pub() # ------------------------------- # Figure 2: Wages by country (x = k3) # ------------------------------- wages_df_bw <- wages_df %>% mutate(country_f = factor(paste0("Country_", country), levels = country_levels) ) p_wages <- ggplot( wages_df_bw , aes(x = k3 , y = wage , group = country_f, linetype = country_f, shape = country_ f) ) + geom_line(linewidth = 0.9) + geom_point(size = 2.2) + scale_linetype_manual(values = linetypes_cty , name = "Country") + scale_shape_manual(values = shapes_cty , name = "Country") + labs( title = "Equilibrium␣Wages␣by␣Country", x = expression(paste("Country␣3␣productivity␣␣(", k[3], ")")), y = "Wage" ) + theme_pub() # ------------------------------- # SAVE FIGURES (PDF & PNG) to ./Figures/ # ------------------------------- dir.create("Figures", showWarnings = FALSE) save_both <- function(plot , filename_base , width = 7, height = 4.8, dpi = 320) { pdf_path <- file.path("Figures", paste0(filename_base , ".pdf")) png_path <- file.path("Figures", paste0(filename_base , ".png")) if (capabilities("cairo")) { ggsave(pdf_path , plot , width = width , height = height , units = "in", device = cairo_pdf) } else { ggsave(pdf_path , plot , width = width , height = height , units = "in", device = "pdf") } ggsave(png_path , plot , width = width , height = height , units = "in", dpi = dpi) } save_both(p_prices , "prices_bw_6goods") save_both(p_wages , "wages_bw_6goods") # Also print to screen print(p_prices) print(p_wages) 160
