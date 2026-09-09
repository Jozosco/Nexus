# CIKM_2025_LLM_enhanced_BlackLitterman

> 원본: `docs/research_desk/references/CIKM_2025_LLM_enhanced_BlackLitterman.pdf` · SHA256 `bf262f13f348d2fc…` · 14쪽 · 53,266자 · 변환 2026-09-09 (pdf_to_markdown.py)

## 목차(자동 복원)
  - LLM-Enhanced Black-Litterman Portfolio Optimization (p.1)
    - Youngbin Lee∗ (p.1)
    - Yejin Kim∗ (p.1)
    - Juhyeong Kim (p.1)
    - Suin Kim (p.1)
    - Yongjae Lee† (p.1)
- arXiv:2504.14345v2  [q-fin.PM]  19 Oct 2025 (p.1)

## 본문

<!-- page 1 -->


### LLM-Enhanced Black-Litterman Portfolio Optimization


#### Youngbin Lee∗

youngandbin@elicer.com Elice AI Quant Lab, MODULABS Seoul, Republic of Korea

#### Yejin Kim∗

yejin.kim.ds@meritz.com Meritz Fire & Marine Insurance AI Quant Lab, MODULABS Seoul, Republic of Korea

#### Juhyeong Kim

juhyeong.kim@miraeasset.com nonconvexopt@gmail.com Mirae Asset Global Investments AI Quant Lab, MODULABS Seoul, Republic of Korea

#### Suin Kim

suin@elicer.com Elice Seoul, Republic of Korea

#### Yongjae Lee†

yongjaelee@unist.ac.kr Ulsan National Institute of Science and Technology Ulsan, Republic of Korea Abstract The Black-Litterman model addresses the sensitivity issues of tra- ditional mean-variance optimization by incorporating investor views, but systematically generating these views remains a key challenge. This study proposes and validates a systematic frame- work that translates return forecasts and predictive uncertainty from Large Language Models (LLMs) into the core inputs for the Black-Litterman model: investor views and their confidence lev- els. Through a backtest on S&P 500 constituents, we demonstrate that portfolios driven by top-performing LLMs significantly out- perform traditional baselines in both absolute and risk-adjusted terms. Crucially, our analysis reveals that each LLM exhibits a dis- tinct and consistent investment style which is the primary driver of performance. We found that the selection of an LLM is therefore not a search for a single best forecaster, but a strategic choice of an investment style whose success is contingent on its alignment with the prevailing market regime. The source code and data are available at https://github.com/youngandbin/LLM-BLM.
CCS Concepts • Computing methodologies →Natural language processing.
Keywords Portfolio Optimization, Black-Litterman Model, Large Language Models, Mean-Variance Optimization, Quantitative Investing, Deep Learning in Finance ACM Reference Format:
Youngbin Lee, Yejin Kim, Juhyeong Kim, Suin Kim, and Yongjae Lee. 2025.
LLM-Enhanced Black-Litterman Portfolio Optimization. In Proceedings of ∗These authors contributed equally to this work.
†Corresponding author CIKM’25 Workshop on FinAI, Seoul, Republic of Korea © 2025 Copyright held by the owner/author(s). Publication rights licensed to ACM.
This is the author’s version of the work. It is posted here for your personal use. Not for redistribution. The definitive Version of Record was published in Proceedings of the 34th ACM International Conference on Information and Knowledge Management (CIKM ’25), November 10–14, 2025, Seoul, Republic of Korea, https://doi.org/10.48550/ arXiv.2504.14345.
the 34th ACM International Conference on Information and Knowledge Man- agement (CIKM ’25), November 10–14, 2025, Seoul, Republic of Korea. ACM, New York, NY, USA, 14 pages. https://doi.org/10.48550/arXiv.2504.14345 1 Introduction Portfolio optimization is a fundamental problem in finance, tradi- tionally approached using mean-variance optimization [23]. How- ever, a well-known limitation of mean-variance optimization is its sensitivity to input parameters, such as expected returns and covariance estimates. The Black-Litterman asset allocation model [4] was introduced to mitigate these problems by incorporating in- vestor views into expected returns through a Bayesian framework.
Unlike traditional mean-variance optimization, which relies purely on historical data, the Black-Litterman model blends prior market equilibrium returns with subjective investor views, weighted by confidence levels. This approach not only stabilizes return estimates but also allows for a more flexible and systematic integration of ex- pert knowledge and quantitative signals. While theoretical research has extended the framework to complex dynamic, multi-period set- tings [2], our study utilizes the conventional single-period model to focus specifically on the novel challenge of generating views from LLMs.
Although the Black-Litterman model remains widely used in asset management industry, including Goldman Sachs, a key chal- lenge lies in how to define and quantify these views in a systematic and reliable manner. Traditionally, these views have been derived from qualitative assessments or ad hoc quantitative models, limiting scalability and objectivity.
This study proposes a systematic framework for integrating LLM-generated views into the Black-Litterman model. Our contri- bution lies not in developing a new time-series forecasting model with LLMs, but in establishing a structured methodology to translate LLM predictions into actionable portfolio views.
This framework systematically incorporates not only the LLM’s return predictions but also their inherent uncertainty, allowing for a data-driven and scalable generation of views while mitigating hu- man bias. Our experiments serve to illustrate how this framework operates in practice, demonstrating that the final portfolio perfor- mance becomes contingent on the quality of the views generated by the specific LLM employed.

## arXiv:2504.14345v2  [q-fin.PM]  19 Oct 2025


<!-- page 2 -->

CIKM’25 Workshop on FinAI, November 14, 2025, Seoul, Republic of Korea Lee et al.
The primary objective of this research is to empirically demon- strate our proposed framework. We apply it to generate portfolios based on views from several state-of-the-art LLMs, using S&P 500 constituents as the asset universe. We use a dedicated validation period to tune the Black-Litterman model’s key hyperparameter, 𝜏, which governs the confidence in market equilibrium returns versus LLM-generated views. The optimized portfolio is then backtested on an unseen test period against traditional benchmarks. The analysis focuses not on crowning a superior forecasting model, but on illus- trating how the characteristics of different LLM-generated views, when systematically integrated via our framework, lead to distinct portfolio performance outcomes. Performance is assessed using standard metrics such as the Sharpe ratio, providing a clear picture of how each model’s predictive patterns translate into investment results.
2 Related Works 2.1 The Black-Litterman Model and the Challenge of View Generation The Black-Litterman model [4] offered a novel approach to portfolio optimization by systematically blending market equilibrium returns with investor-specific views. A key advantage of this model is that it produces more intuitive and stable portfolios than traditional mean-variance optimization [9, 24].
However, the practical application of the model has always been limited by its most critical input: the generation of investor views.
Historically, these views were based on the subjective judgments of human experts [11]. This process is difficult to scale and is prone to cognitive biases, such as overconfidence and herding, which are widely studied in behavioral finance [3, 14]. The challenge of converting expert opinions into a quantitative format while avoiding human error has led to a long search for a more systematic and data-driven approach to view generation.
To address the subjectivity of human views, researchers turned to machine learning, which has shown significant success in empirical asset pricing [8]. Early approaches employed quantitative models to forecast returns based on historical patterns, using techniques like temporal relational ranking or multi-graph convolutional networks [7, 28].
More sophisticated methods have been developed to systemati- cally generate views. For instance, machine learning has been used to systematically generate views based on established asset pricing factors [16]. Other studies have integrated advanced deep learn- ing architectures like Transformers and Generative Adversarial Networks (GANs) to capture complex, non-linear market dynam- ics and refine predictions [35]. Beyond prediction, some research has explored deep reinforcement learning to directly learn optimal trading policies [12]. While these methods are a significant step towards objectivity, they share a common limitation: they are pri- marily designed for structured inputs. This means that processing unstructured information, such as natural language, requires ex- tensive feature engineering. Consequently, their ability to adapt to new information sources or changing market regimes remains limited.
2.2 LLMs in Finance Recent advances in LLMs have created new opportunities in fi- nance, particularly due to their ability to understand and reason with unstructured text data. This has led to the development of spe- cialized financial models like BloombergGPT [29] and open-source initiatives like FinGPT [21]. As a result, LLMs are being applied to a wide range of fianncial tasks, as surveyed by [20].
The application of LLMs in finance now extends far beyond sim- ple text summarization. For example, studies have used LLMs to generate qualitative evaluations for asset pricing models [5], ana- lyze news sentiment for return forecasting [22], and create special- ized financial asset representations to overcome the limitations of general-purpose embeddings [18]. These diverse capabilities high- light the potential of LLMs to serve as powerful signal generators for portfolio optimization [10, 34].
Another key application area is return forecasting. Studies have explored using LLMs for return forecasting [13], with techniques like retrieval-augmented generation (RAG) further improving pre- diction accuracy [30]. However, a critical gap remains: these studies often focus on the accuracy of the forecast itself, rather than on the crucial subsequent step of how to systematically integrate these powerful, yet inherently uncertain, predictions into a robust port- folio construction framework. Simply using raw LLM outputs can lead to unstable portfolios, as LLMs possess their own inherent biases that can distort recommendations if left unchecked [19]. A separate line of research even bypasses optimization frameworks entirely, designing fully autonomous trading agents where the LLM is the sole decision-maker [31, 33].
Our work bridges the gap between unstructured LLM insights and structured portfolio optimization. We move beyond merely generating forecasts and propose a systematic framework that translates not only the return predictions from LLMs but also their inherent uncertainty into the core inputs of the Black-Litterman model. By quantifying this uncertainty, our approach automatically calibrates the confidence in LLM-generated views, mitigating the risk of overweighting biased or unstable predictions. To our knowl- edge, this is the first study to establish a structured methodology for integrating both the predictive power and the predictive uncer- tainty of various LLMs into a proven portfolio optimization model, thereby addressing the challenge of systematic view generation in a novel and scalable manner.
3 Method We first describe the financial dataset, then explain how LLMs are prompted to generate predictive views. Finally, we formalize the integration of these views and their underlying uncertainty into the Black-Litterman portfolio optimization framework.
3.1 Data Description We use historical stock price data from the largest 50 S&P 500 con- stituents by market capitalization as of March 26, 2025, sourced from Yahoo Finance. The total dataset spans 13 months, from June 2024 to June 2025. To ensure a robust evaluation and avoid overfit- ting, we divide the data into two distinct periods:

<!-- page 3 -->

LLM-Enhanced Black-Litterman Portfolio Optimization CIKM’25 Workshop on FinAI, November 14, 2025, Seoul, Republic of Korea Stock prices in lookback period Stock prices in evaluation period Make Views Estimate parameters Optimize portfolio LLM Black- Litterman Invest Repeat steps at next rebalancing period Figure 1: The Proposed Framework for Integrating LLM Views into Black-Litterman Model • Validation Period (3 months): From June 2024 to August 2024. This period is used exclusively for tuning the hyperpa- rameter 𝜏of the Black-Litterman model.
• Test Period (10 months): From September 2024 to June 2025. This unseen data is used for the final performance evaluation of the portfolios.
The portfolio is rebalanced every two weeks. At each rebalancing date, the LLM is provided with the past two weeks of stock price data and company metadata to generate return predictions for the subsequent two weeks. This iterative process ensures that each portfolio construction is based on the most recent information available.
3.2 Large Language Models We use LLMs to generate forward-looking views for the Black- Litterman model in an automated and scalable way. We detail this process, covering the selection of specific LLMs, our structured prompting technique for eliciting quantitative forecasts, and the method for measuring the uncertainty of these predictions.
3.2.1 Selection of Large Language Models. To incorporate predic- tive views, we employ four state-of-the-art models. Crucially, the knowledge cutoff for all selected models predates our entire eval- uation period (Jun 2024–Jun 2025). This ensures that the models’ internal knowledge does not contain information about future stock performance, thereby preventing any form of look-ahead bias. We use instruction-tuned models to ensure consistency in the generated return predictions, and use vLLM [17] for optimized inference.
Model Size Release Developer Gemma-7B [27] 7B Feb 2024 Google DeepMind Qwen-2-7B [32] 7B Jun 2024 Alibaba Cloud LLaMA-3.1-8B [6] 8B Jul 2024 Meta GPT-4o-mini [25] ∼8B Jul 2024 OpenAI Although the exact size of GPT-4o-mini has not been officially disclosed, [1] estimate it to be within the 8 billion parameter range, making it comparable to the open-source models used in our study.
Table 1: Summary of LLMs used in this study.
3.2.2 Structured Prompting for Predictive Views. To elicit predic- tive views from the LLMs, we developed a structured prompting strategy that combines a detailed system prompt with a concise user prompt. This two-part structure is designed to guide the mod- els toward generating quantitative, data-driven return forecasts while minimizing narrative or qualitative output. The full prompt structure is detailed in Appendix A.
The system prompt sets the context, defines the task, and speci- fies the output format. It instructs the model to act as a financial analyst tasked with predicting the average daily return for a stock over the upcoming two-week period. It outlines the required ana- lytical steps: analyzing the provided time-series data, considering the broader sector and market context, and incorporating company- specific information. Crucially, it constrains the output to a single floating-point number to ensure the response can be directly inte- grated into our quantitative framework.
The user prompt supplies the specific data for each stock at each rebalancing date. It includes four key pieces of information:
• Stock Daily Returns: The stock’s own daily returns from the past two weeks.
• Sector and Market Returns: The corresponding daily returns for the stock’s GICS sector and the S&P 500 index.
• Company Information: Metadata including the ticker, com- pany name, GICS sector, and sub-industry.
3.3 Integration with the Black-Litterman Model The overall workflow for integrating the predictive views and their uncertainty, generated by the LLMs, into the Black-Litterman frame- work is summarized in Figure 1. Our portfolio strategy adheres to a two-week rebalancing cycle.
At each rebalancing date, we first utilize the stock price data from the preceding two weeks (the lookback period). This data is fed into the LLM using the structured prompting technique detailed in Section 3.2.2 to generate predictive views for the subsequent two- week period. These resulting views, along with their corresponding confidence levels, are then integrated with the market equilibrium returns within the Black-Litterman model.
The model combines these inputs to estimate the posterior ex- pected returns. Based on this updated estimation, portfolio opti- mization is performed to determine the new optimal asset alloca- tion weights. This portfolio is then invested (held) according to these weights for the duration of the two-week evaluation period,

<!-- page 4 -->

CIKM’25 Workshop on FinAI, November 14, 2025, Seoul, Republic of Korea Lee et al.
at which point the cycle repeats. This entire process is executed iteratively at every rebalancing date throughout the test period.
3.3.1 Overview of the Black-Litterman Model. The Black-Litterman model is a portfolio optimization framework that combines mar- ket equilibrium returns derived from the Capital Asset Pricing Model (CAPM) [26] with investor views to generate more stable and intuitive asset allocations. Unlike traditional mean-variance optimization, which is highly sensitive to input parameters, the Black-Litterman model integrates external views by adjusting equi- librium returns in a Bayesian manner [15].
In the standard Black-Litterman framework, the equilibrium re- turn vector 𝝅is derived from market capitalization weights and serves as a prior estimate of expected returns for each stocks. Views on specific assets, denoted by a view vector q and the correspond- ing confidence matrix 𝛀, are incorporated to adjust 𝝅and compute the posterior expected returns 𝝁, which, along with the covariance matrix 𝚺of the stocks, are then used as input for portfolio opti- mization to get optimal weights w∗for stocks [11], as detailed in Appendix B.
That is, we solve for the posterior expected returns 𝝁from the Equation 1:
y = X𝝁+ 𝜺, 𝜺∼N (0, V) (1) y = 𝝅 q  , X = I P  , V = 𝜏Σ 0 0 Ω  (2) where 𝜏is a hyperparameter to balance confidence between the market equilibrium and the LLM-generated views. Σ is the covariance matrix of stock returns.
Our framework defines the remaining components using LLM outputs as described in Table 2.
3.3.2 Incorporating LLM-Generated Views. In this study, we extend the Black-Litterman model by leveraging LLM-generated predictive views instead of human-defined views. These views, extracted from multiple queries to LLMs, represent the expected average daily return for each asset and are incorporated into the model alongside their confidence levels.
When calculating the posterior expected returns 𝝁, we can deter- mine the equilibrium return vector 𝝅and the covariance matrix 𝚺of the stocks from historical return data. To integrate LLM-generated predictive views into the Black-Litterman model, we now define the view expectation vector q, the picking matrix P, and the confidence matrix 𝛀based on the LLM output. This process is described in Figure 1. By structuring the LLM outputs in this manner, we system- atically integrate them into the Black-Litterman framework. The resulting posterior expected returns are then used in the portfolio optimization process.
View Vector (q ∈R𝑘). The vector q contains the expected return for each of the 𝑘views. For each stock, the LLM is queried 𝑁= 100 times, and the mean of these repeated responses constitutes the view for that stock.
Picking matrix (P ∈R𝑘×𝑛). In our framework, we formulate one absolute view for each individual stock, rather than relative views between assets. The picking matrix specifies which of the Component Symbol Description View vector q ∈R𝑘 A vector containing the spe- cific expected return forecasts for each of the k views.
Picking matrix P ∈R𝑘×𝑛 A matrix that maps the k views to the corresponding n assets in the portfolio.
Confidence matrix 𝛀∈R𝑘×𝑘 A diagonal matrix quantifying the level of uncertainty for each of the k views.
Table 2: LLM-generated inputs for the Black-Litterman model 𝑛stocks correspond to each of the 𝑘views. Since we generate an independent view for each of the 𝑛stocks, the picking matrix P is an identity matrix (𝑘= 𝑛), linking each view directly to a single asset.
Confidence Matrix (𝛀∈R𝑘×𝑘). This diagonal matrix captures the uncertainty of each view. The diagonal elements are populated with the variance of the 𝑁repeated predictions for each stock. A higher variance signals greater uncertainty, automatically down-weighting that view’s influence in the final blended return calculation.
4 Experiment We conduct an empirical backtest to evaluate the performance of our proposed framework, which integrates LLM-generated views into the Black-Litterman model (BLM). To structure our analysis, we address the following key research questions:
RQ1 (Performance) How does the investment performance of port- folios constructed using our LLM-BLM framework compare to traditional benchmarks like EW and MVO in terms of absolute and risk-adjusted returns?
RQ2 (Style) Do different LLMs exhibit distinct and characterizable ‘investment styles’ in their predictive view distributions, and if so, how do they differ in terms of bias, dispersion, and conviction?
RQ3 (Attribution) What is the relationship between an LLM’s overarching predictive sentiment and its portfolio perfor- mance, and how does this relationship depend on the market regime?
The subsequent sections are structured to answer each of these questions in turn. Our evaluation follows a two-stage process: first, we optimize the model’s key hyperparameter, 𝜏, which was intro- duced in Equation 2. Second, we assess the final portfolio perfor- mance on an unseen test period to address our research questions.
4.1 Experimental Setup To ensure a comprehensive analysis, we evaluate four distinct LLM- enhanced Black–Litterman portfolios, each driven by views from a different model: BLM-Gemma, BLM-Qwen, BLM-Llama, and BLM-GPT.
We compare their performance against three standard baselines:
• S&P 500 Index (Market): A market-capitalization-weighted index that serves as the overall market benchmark.

<!-- page 5 -->

LLM-Enhanced Black-Litterman Portfolio Optimization CIKM’25 Workshop on FinAI, November 14, 2025, Seoul, Republic of Korea Figure 2: Comparative Analysis of Cumulative Returns for BLM and Benchmark Portfolios. The results highlight the significant outperformance of the BLM-Qwen and BLM-Llama strategies, which consistently generated higher returns compared to both the market index and conventional quantitative models.
• Equally Weighted (EW): A simple yet robust baseline strat- egy that allocates equal capital to each asset, representing naive diversification.
• Mean-Variance Optimization (MVO): The classic Markowitz portfolio model, which relies solely on historical return and covariance estimates and serves as a traditional quantitative benchmark.
The performance of each strategy is measured using a compre- hensive suite of standard financial metrics. These include return indicators such as the Cumulative Annual Growth Rate (CAGR) alongside both daily (mean) and annualized (mean ann.) average re- turns; corresponding volatility (std); risk-adjusted returns (Sharpe); and key downside risk measures, including Maximum Drawdown (MDD), 95% Value at Risk (VaR 95%), and 95% Conditional Value at Risk (CVaR 95%).
Furthermore, to more realistically reflect the actual investment environment, transaction costs are incorporated into the backtest.
Costs are calculated as 0.1% of the portfolio weight changes at each rebalancing and are factored into the final performance. This setup allows us to rigorously test the practical value of integrating LLM-generated insights into a structured portfolio optimization framework.
4.2 Hyperparameter Tuning The primary hyperparameter in our framework is 𝜏, which, as intro- duced in the variance-covariance matrix V in Equation (2), balances the confidence between the market equilibrium prior and the LLM- generated views. A higher value of 𝜏indicates less confidence in the prior (market equilibrium returns), thus placing more weight on the LLM’s views. Instead of relying on a fixed, arbitrary value, we tune 𝜏on the validation dataset. This is a crucial step to find the optimal balance between market priors and the specific characteristics of each LLM’s views for our asset universe. We employ a two-step process for this tuning.
4.2.1 Step 1: Heuristic Estimation of Initial 𝜏. First, we derive a heuristic initial estimate for 𝜏, denoted as 𝜏init. This value is de- signed to dynamically ground our model’s confidence based on the relative uncertainty between the LLM’s views and the market’s historical volatility. We calculate 𝜏init by averaging the ratio of these uncertainties across all rebalancing periods (𝑡) in the validation set (𝑇𝑣𝑎𝑙):
𝜏init = 1 |𝑇𝑣𝑎𝑙| ∑︁ 𝑡∈𝑇𝑣𝑎𝑙 mean(𝛀𝑡) mean(𝚺𝑡) (3) where 𝛀𝑡is the confidence matrix of the LLM views and 𝚺𝑡is the covariance matrix of asset returns at rebalancing period 𝑡. The mean(·) function computes the mean of all elements in the given matrix. This approach ensures our initial hyperparameter is di- rectly informed by the relative uncertainties observed during the validation period.
4.2.2 Step 2: Grid Search for Optimal 𝜏. Using 𝜏init as a center point, we perform a grid search over a range of values, T, defined as:
T = {0.5𝜏init, 0.75𝜏init,𝜏init, 1.25𝜏init, 1.5𝜏init} For each 𝜏∈T, we run a full backtest on the validation period and calculate the resulting Sharpe ratio. The 𝜏value that yields the highest Sharpe ratio is selected as the optimal hyperparameter, 𝜏∗.
The optimal hyperparameter, 𝜏∗, found during the validation phase is then used for the final evaluation. We run a single backtest over the test period (Sep 2024-Jun 2025), rebalancing the portfolio every two weeks using this fixed 𝜏∗.

<!-- page 6 -->

CIKM’25 Workshop on FinAI, November 14, 2025, Seoul, Republic of Korea Lee et al.
4.3 RQ1: Portfolio Performance Metric EW MVO BLM-Gemma BLM-Qwen BLM-Llama BLM-GPT CAGR ↑ 0.1907 0.0607 0.1590 0.2811 0.2751 0.0768 mean ↑ 0.0008 0.0004 0.0007 0.0011 0.0010 0.0004 std ↓ 0.0122 0.0179 0.0156 0.0152 0.0124 0.0132 Sharpe ↑ 0.0563 0.0176 0.0402 0.0669 0.0774 0.0228 mean (ann.) ↑ 0.1932 0.0994 0.1784 0.2763 0.2627 0.0958 std (ann.) ↓ 0.1938 0.2841 0.2481 0.2413 0.1975 0.2093 Sharpe (ann.) ↑ 0.8937 0.2793 0.6386 1.0624 1.2286 0.3619 MDD ↑ −0.1688 −0.1620 −0.1551 −0.1375 -0.1383 −0.1649 VaR95% ↑ −0.0171 −0.0259 -0.0168 −0.0182 −0.0169 −0.0157 CVaR95% ↑ −0.0280−0.0448 −0.0372 −0.0320 -0.0283 −0.0312 Table 3: Out-of-sample Investment Performance of Portfolios Table 3 and Figure 2 summarize the comparative performance analysis of four proposed BLM-based models (BLM-Gemma, BLM-Qwen, BLM-Llama, and BLM-GPT) against two traditional benchmarks: the EW and MVO portfolios. The evaluation encompasses various met- rics, including absolute returns, risk-adjusted returns, and downside risk.
The analysis reveals a strong performance from the BLM-based models, particularly BLM-Qwen and BLM-Llama. BLM-Qwen achieved the highest CAGR of 0.2811, closely followed by BLM-Llama at 0.2751. Both significantly outperformed the traditional benchmarks, EW (0.1907) and MVO (0.0607).
In terms of risk-adjusted returns, measured by the annualized Sharpe Ratio, Sharpe (ann.), BLM-Llama delivered the top perfor- mance with a ratio of 1.2286. BLM-Qwen secured the second-highest position at 1.0624. This indicates that both models generated supe- rior excess returns per unit of risk, far exceeding the benchmarks EW (0.8937) and MVO (0.2793).
Regarding volatility, std (ann.), the EW portfolio was the most stable with a value of 0.1938, underscoring the benefits of sim- ple diversification. However, BLM-Llama was a very close second with a volatility of 0.1975, indicating effective risk management.
In downside risk, the BLM models also excelled. BLM-Qwen posted the lowest MDD at -0.1375, with BLM-Llama following closely at -0.1383, both demonstrating significantly better capital preservation than the benchmarks during downturns.
The other LLM-based strategies showed mixed results. The BLM-Gemma model delivered a modest positive CAGR of 0.1590, while the BLM-GPT model lagged with a CAGR of 0.0768, performing similarly to the MVO benchmark in terms of returns.
In conclusion, the framework successfully translated LLM-generated views into high-performing portfolios. The BLM-Qwen and BLM-Llama models, in particular, demonstrated exceptional and distinct strengths:
BLM-Qwen excelled in generating the highest absolute returns (CAGR), while BLM-Llama delivered the best risk-adjusted performance (Sharpe) and showcased strong risk control. Both models decisively outper- formed traditional benchmarks and other LLM strategies, highlight- ing the framework’s effectiveness.
4.4 RQ2: Investment Styles To further investigate how LLMs formulated asset views, we ana- lyzed the distribution of their individual return predictions. In our setup, each LLM repeatedly generated predictions per stock at each rebalancing point. Figure 3 displays a time-series of these distribu- tions. Specifically, each individual boxplot on the chart represents the entire population of views (𝑁predictions × 𝑛assets) generated by a model for that single rebalancing period. This visualization method reveals how the overall distribution of views—encompassing both cross-sectional differences across assets and the inherent un- certainty within the predictions—evolves over time. The y-axis is clipped to a range of -3% to 3% for clarity, and the summary statis- tics in Table 4 provide details on the aggregate distribution across all periods.
The most striking characteristic is the distribution of views from BLM-Llama. The boxplots and summary statistics reveal an excep- tionally wide dispersion of predictions (Std: 0.6903) with extreme outliers (Min: -57.99%, Max: 91.70%). This indicates that BLM-Llama generated highly differentiated and high-conviction views, confi- dently identifying both strong positive and strong negative return Figure 3: LLM-generated Views Over Time at Rebalancing Intervals. The figure visualizes the distribution of all generated return forecasts for each LLM at every two-week rebalancing interval.

<!-- page 7 -->

LLM-Enhanced Black-Litterman Portfolio Optimization CIKM’25 Workshop on FinAI, November 14, 2025, Seoul, Republic of Korea opportunities. Despite the extreme negative outliers, the overall dis- tribution maintained the highest positive mean (0.1786), suggesting its positive views were particularly impactful. This "sharp" differ- entiation between assets appears to be a key driver of its strong portfolio performance.
In stark contrast, BLM-Gemma and BLM-Qwen represent two oppo- site poles of view generation. BLM-Gemma consistently exhibited a strong pessimistic bias; its median view was almost always nega- tive, a fact confirmed by its negative overall mean of -0.3847. This persistent negative outlook on the market likely led to suboptimal asset selection. Conversely, BLM-Qwen adopted a cautiously opti- mistic stance. Its views were the most tightly clustered around a stable, slightly positive median, reflected in the lowest standard deviation (0.2872) among all models. This suggests a consistent, low-conviction strategy that avoids extreme bets.
The BLM-GPT model can be characterized as a middle ground.
Its view distribution was more dispersed than BLM-Qwen’s but less biased than BLM-Gemma’s, with a moderately positive mean (0.1347) and standard deviation (0.4805). Its predictions were less stable than Qwen’s but avoided the persistent pessimism of Gemma.
In conclusion, these results clearly show that the "style" of view generation is critical. The final portfolio outcomes are a direct re- flection of the distinct characteristics of each model’s predictive dis- tribution. BLM-Llama’s high-conviction differentiation, BLM-Qwen’s stable and cautious optimism, and BLM-Gemma’s pervasive pessimism are not just statistical artifacts but are the fundamental drivers that explain their divergent investment performance.
4.5 RQ3: Performance Attribution to Predictive Sentiment Figure 4 visualizes the cumulative returns of each portfolio model, with the background color illustrating the proportion of positive views among all generated predictions at each rebalancing point.
The color scale ranges from pessimistic (red, a low proportion of positive views) to optimistic (green, a high proportion). This anal- ysis reveals a direct link between a model’s overarching market sentiment and its investment performance, contingent on the mar- ket conditions of the test period.
(1) Alignment of Optimism with Market Trend in Top Performers: The top-performing models, BLM-Llama and BLM-Qwen, both demonstrate a clear synchronization be- tween a consistently optimistic market outlook and strong portfolio returns. Their backgrounds remain predominantly green, indicating a high proportion of positive views. During the observed test period, which featured a generally upward market trend (as indicated by the S&P500 benchmark), this stable, bullish conviction proved to be the correct strategic stance. It allowed the models to effectively participate in market updrafts and generate significant alpha.
(2) Misaligned Sentiment in Underperformers: In stark con- trast, BLM-Gemma’s underperformance is clearly linked to a persistent pessimistic bias. Its background is dominated by red and yellow shades, signifying a low proportion of positive views. This consistently bearish outlook was fundamentally misaligned with the market’s overall upward trajectory dur- ing the period, causing the model to miss key appreciation opportunities and leading to a decline in cumulative return.
Separately, BLM-GPT’s mediocre performance appears driven by an unstable market view. Its frequent vacillation between bullish and bearish sentiment suggests an inability to com- mit to the prevailing market trend, resulting in performance that failed to meaningfully outperform the benchmarks.
(3) Alignment with Market Regime as the Key Differentia- tor: In summary, this visual analysis confirms that a model’s performance is critically linked to how well its overarching sentiment aligns with the market regime of the test period.
The success of BLM-Llama and BLM-Qwen was rooted in their stable, optimistic view-generation process, which was the appropriate stance for the generally bullish environment observed. Conversely, BLM-Gemma’s failure can be attributed to its pervasive pessimism being out of sync with the market, while BLM-GPT’s middling results were a product of its incon- sistent outlook. This highlights that for this framework to succeed, the underlying LLM must generate a consistent and, crucially, correctly calibrated conviction about the overall market direction for a given period.
5 Conclusion This study proposed and validated a systematic framework for translating LLM predictions and their inherent uncertainty into actionable views for the Black-Litterman model. Our empirical backtest demonstrated that this approach generates portfolios, par- ticularly from BLM-Llama and BLM-Qwen, that significantly outper- form traditional benchmarks. Crucially, our analysis revealed that performance is a direct consequence of each LLM’s distinct view generation ‘style’—such as BLM-Llama’s high-conviction differentia- tion versus BLM-Qwen’s stable optimism. The key implication is that the choice of an LLM is akin to selecting an investment manager with a specific bias, whose success is contingent on its alignment with the prevailing market regime. Future research could extend this work by incorporating financial text into the view generation process or by developing methods to dynamically select models based on expected market conditions.
Acknowledgments This research was supported by Brian Impact Foundation, a non- profit organization dedicated to the advancement of science and technology for all.
References [1] Asma Ben Abacha, Wen-wai Yim, Yujuan Fu, Zhaoyi Sun, Meliha Yetisgen, Fei Xia, and Thomas Lin. 2024. Medec: A benchmark for medical error detection and correction in clinical notes. arXiv preprint arXiv:2412.19260 (2024).
[2] Anas Abdelhakmi and Andrew EB Lim. 2025. Dynamic Black-Litterman. Opera- tions Research (2025).
[3] Nicholas Barberis and Richard Thaler. 2003. A survey of behavioral finance.
Handbook of the Economics of Finance 1 (2003), 1053–1128.
[4] Fischer Black and Robert Litterman. 1992. Global portfolio optimization. Financial analysts journal 48, 5 (1992), 28–43.
[5] Junyan Cheng and Peter Chin. 2024. Empirical Asset Pricing with Large Language Model Agents. arXiv preprint arXiv:2409.17266 (2024).
[6] Abhimanyu Dubey, Abhinav Jauhri, Abhinav Pandey, Abhishek Kadian, Ahmad Al-Dahle, Aiesha Letman, Akhil Mathur, Alan Schelten, Amy Yang, Angela Fan, et al. 2024. The llama 3 herd of models. arXiv preprint arXiv:2407.21783 (2024).
[7] Fuli Feng, Xiangnan He, Xiang Wang, Cheng Luo, Yiqun Liu, and Tat-Seng Chua.
2019. Temporal relational ranking for stock prediction. ACM Transactions on Information Systems (TOIS) 37, 2 (2019), 1–30.

<!-- page 8 -->

CIKM’25 Workshop on FinAI, November 14, 2025, Seoul, Republic of Korea Lee et al.
Figure 4: Correlation Between LLM Predictive Sentiment and Portfolio Performance. This figure compares the cumulative return of each LLM-driven portfolio (line graphs) with the underlying sentiment of the LLM’s views at each rebalancing point (background color).
[8] Shihao Gu, Bryan Kelly, and Dacheng Xiu. 2020. Empirical asset pricing via machine learning. The Review of Financial Studies 33, 5 (2020), 2223–2273.
[9] Guangliang He and Robert Litterman. 2002. The intuition behind Black-Litterman model portfolios. Available at SSRN 334304 (2002).
[10] Yoontae Hwang, Yaxuan Kong, Stefan Zohren, and Yongjae Lee. 2025. Decision- informed Neural Networks with Large Language Model Integration for Portfolio Optimization. arXiv preprint arXiv:2502.00828 (2025).
[11] Thomas Idzorek. 2007. A step-by-step guide to the Black-Litterman model:
Incorporating user-specified confidence levels. In Forecasting expected returns in the financial markets. Elsevier, 17–38.
[12] Zhengyao Jiang, Dixing Xu, and Jinjun Liang. 2017. A deep reinforcement learning framework for the financial portfolio management problem. arXiv preprint arXiv:1706.10059 (2017).
[13] Ming Jin, Shiyu Wang, Lintao Ma, Zhixuan Chu, James Y Zhang, Xiaoming Shi, Pin-Yu Chen, Yuxuan Liang, Yuan-Fang Li, Shirui Pan, et al. 2023. Time-llm:
Time series forecasting by reprogramming large language models. arXiv preprint arXiv:2310.01728 (2023).
[14] Mahmut Kara, Aydin Ulucan, and Kazim Baris Atici. 2019. A hybrid approach for generating investor views in Black–Litterman model. Expert Systems with Applications 128 (2019), 256–270.
[15] Jang Ho Kim, Yongjae Lee, Woo Chang Kim, Taehyeon Kang, and Frank J Fabozzi.
2024. An Overview of Optimization Models for Portfolio Management. Journal of Portfolio Management 51, 2 (2024).
[16] Hyungjin Ko and Jaewook Lee. 2025. Portfolio management transformed: An enhanced black–litterman approach integrating asset pricing theory and machine learning. Computational Economics (2025), 1–47.

<!-- page 9 -->

LLM-Enhanced Black-Litterman Portfolio Optimization CIKM’25 Workshop on FinAI, November 14, 2025, Seoul, Republic of Korea [17] Woosuk Kwon, Zhuohan Li, Siyuan Zhuang, Ying Sheng, Lianmin Zheng, Cody Hao Yu, Joseph Gonzalez, Hao Zhang, and Ion Stoica. 2023. Efficient memory management for large language model serving with pagedattention. In Proceedings of the 29th Symposium on Operating Systems Principles. 611–626.
[18] Hoyoung Lee, Wonbin Ahn, Suhwan Park, Jaehoon Lee, Minjae Kim, Sungdong Yoo, Taeyoon Lim, Woohyung Lim, and Yongjae Lee. 2025. THEME: Enhancing Thematic Investing with Semantic Stock Representations and Temporal Dynam- ics. arXiv preprint arXiv:2508.16936 (2025).
[19] Hoyoung Lee, Junhyuk Seo, Suhwan Park, Junhyeong Lee, Wonbin Ahn, Chanyeol Choi, Alejandro Lopez-Lira, and Yongjae Lee. 2025. Your AI, Not Your View: The Bias of LLMs in Investment Analysis. arXiv preprint arXiv:2507.20957 (2025).
[20] Jean Lee, Nicholas Stevens, Soyeon Caren Han, and Minseok Song. 2024. A survey of large language models in finance (finllms). arXiv preprint arXiv:2402.02315 (2024).
[21] Xiao-Yang Liu, Guoxuan Wang, Hongyang Yang, and Daochen Zha. 2023. Fingpt:
Democratizing internet-scale data for financial large language models. arXiv preprint arXiv:2307.10485 (2023).
[22] Alejandro Lopez-Lira. 2024. Can ChatGPT forecast stock price movements?
(2024).
[23] Harry Markowitz. 1952. Portfolio Selection. The Journal of Finance 7, 1 (1952), 77–91. doi:10.1111/j.1540-6261.1952.tb01525.x [24] Attilio Meucci. 2010. The black-litterman approach: Original model and ex- tensions. Shorter version in, The Encyclopedia of Quantitative Finance, Wiley (2010).
[25] OpenAI. 2024. GPT-4o. https://platform.openai.com/docs/models#gpt-4o-mini.
Accessed: 2025-02-09.
[26] William F Sharpe. 1964. Capital asset prices: A theory of market equilibrium under conditions of risk. The journal of finance 19, 3 (1964), 425–442.
[27] Gemma Team, Thomas Mesnard, Cassidy Hardin, Robert Dadashi, Surya Bhupati- raju, Shreya Pathak, Laurent Sifre, Morgane Rivière, Mihir Sanjay Kale, Juliette Love, et al. 2024. Gemma: Open models based on gemini research and technology.
arXiv preprint arXiv:2403.08295 (2024).
[28] Changhai Wang, Hui Liang, Bo Wang, Xiaoxu Cui, and Yuwei Xu. 2022. Mg-conv:
A spatiotemporal multi-graph convolutional neural network for stock market index trend prediction. Computers and Electrical Engineering 103 (2022), 108285.
[29] Shijie Wu, Ozan Irsoy, Steven Lu, Vadim Dabravolski, Mark Dredze, Sebas- tian Gehrmann, Prabhanjan Kambadur, David Rosenberg, and Gideon Mann.
2023.
Bloomberggpt: A large language model for finance.
arXiv preprint arXiv:2303.17564 (2023).
[30] Mengxi Xiao, Zihao Jiang, Lingfei Qian, Zhengyu Chen, Yueru He, Yijing Xu, Yuecheng Jiang, Dong Li, Ruey-Ling Weng, Min Peng, et al. 2025. Retrieval- augmented large language models for financial time series forecasting. arXiv preprint arXiv:2502.05878 (2025).
[31] Yijia Xiao, Edward Sun, Di Luo, and Wei Wang. 2024. TradingAgents: Multi- agents LLM financial trading framework. arXiv preprint arXiv:2412.20138 (2024).
[32] An Yang, Baosong Yang, Binyuan Hui, Bo Zheng, Bowen Yu, Chang Zhou, Cheng- peng Li, Chengyuan Li, Dayiheng Liu, Fei Huang, Guanting Dong, Haoran Wei, Huan Lin, Jialong Tang, Jialin Wang, Jian Yang, Jianhong Tu, Jianwei Zhang, Jianxin Ma, Jianxin Yang, Jin Xu, Jingren Zhou, Jinze Bai, Jinzheng He, Jun- yang Lin, Kai Dang, Keming Lu, Keqin Chen, Kexin Yang, Mei Li, Mingfeng Xue, Na Ni, Pei Zhang, Peng Wang, Ru Peng, Rui Men, Ruize Gao, Runji Lin, Shijie Wang, Shuai Bai, Sinan Tan, Tianhang Zhu, Tianhao Li, Tianyu Liu, Wenbin Ge, Xiaodong Deng, Xiaohuan Zhou, Xingzhang Ren, Xinyu Zhang, Xipin Wei, Xuancheng Ren, Xuejing Liu, Yang Fan, Yang Yao, Yichang Zhang, Yu Wan, Yunfei Chu, Yuqiong Liu, Zeyu Cui, Zhenru Zhang, Zhifang Guo, and Zhihao Fan. 2024.
Qwen2 Technical Report.
arXiv:2407.10671 [cs.CL] https://arxiv.org/abs/2407.10671 [33] Yangyang Yu, Haohang Li, Zhi Chen, Yuechen Jiang, Yang Li, Jordan W Suchow, Denghui Zhang, and Khaldoun Khashanah. 2025. Finmem: A performance- enhanced llm trading agent with layered memory and character design. IEEE Transactions on Big Data (2025).
[34] Huaqin Zhao, Zhengliang Liu, Zihao Wu, Yiwei Li, Tianze Yang, Peng Shu, Shaochen Xu, Haixing Dai, Lin Zhao, Gengchen Mai, et al. 2024. Revolutionizing finance with llms: An overview of applications and insights. arXiv preprint arXiv:2401.11641 (2024).
[35] Enmin Zhu and Jerome Yen. 2024.
Enhancing portfolio optimization with transformer-GAN integration: A novel approach in the Black-Litterman frame- work. arXiv preprint arXiv:2404.02029 (2024).

<!-- page 10 -->

CIKM’25 Workshop on FinAI, November 14, 2025, Seoul, Republic of Korea Lee et al.
A Prompt Design Details To clarify the temporal context for the return prediction task, we include an explicit reference date in the system prompt. This date represents the point in time at which the LLM is expected to provide its analysis—positioned between the past time series data and the future return period. By anchoring the prediction task to a specific date, we help the model better interpret the directionality of the input data and generate temporally coherent forecasts.
To ensure consistent and parseable responses from the LLMs, we adopt a structured output format using the JSON schema supported by the chat completions API endpoint. This approach standardizes the outputs across all LLMs and ensures that each model provides consistently structured responses across repeated queries, reducing the likelihood of formatting errors and facilitating reliable down- stream processing.
To enhance the models’ numerical sensitivity, all daily return inputs are scaled by 100 (i.e., presented in percentage terms). For instance, a daily return of -0.0036 is provided as -0.36. This scal- ing prevents issues arising from the small magnitude of raw daily returns, which can be difficult for LLMs to differentiate and pro- cess effectively. This approach is analogous to using basis points in finance to handle small numerical values. By providing a rich, multi-faceted data context and clear instructions, the prompts en- able the LLMs to generate informed, quantitative views for portfolio construction.
B Portfolio Optimization In this study, we implement two distinct portfolio optimization approaches: one based on the views generated by LLMs and the other using traditional mean-variance optimization as a baseline.
The objective is to compare the performance of LLM-based portfo- lios against a benchmark portfolio optimized using conventional techniques.
B.1 LLM-Enhanced Black-Litterman Portfolio The first approach utilizes the posterior returns derived from the views generated by the LLMs and covariance matrix 𝚺. The portfolio optimization problem is formulated as a mean-variance optimiza- tion problem, where the goal is to maximize the expected return of the portfolio while minimizing its risk.
The optimization problem is expressed as:
min w  w𝑇Σw −𝜆· w𝑇r  where:
• w is the vector of portfolio weights, • r is the vector of expected returns (posterior returns) from the LLM views, • Σ is the covariance matrix of returns, • 𝜆is the risk aversion parameter, which determines the trade- off between return and risk.
In this formulation, w𝑇r represents the portfolio return, and w𝑇Σw represents the portfolio risk (variance). The objective is to maximize portfolio return while minimizing the risk, adjusted by the risk aversion parameter 𝜆, which we set as 0.1. The optimization is subject to the constraints:
System Prompt You are providing analysis on {{DATE}}. Predict the average daily return for the next two weeks based on the information provided about a stock’s past performance.
You will receive the following inputs:
• Daily Returns: The stock’s daily returns, a time-series from the past two weeks.
• Company Sector: The company’s GICS sector classifica- tion.
• Sector Returns: The company sector’s daily returns, a time-series from the past two weeks.
• Market Returns: The S&P 500’s daily returns, a time- series from the past two weeks.
• Company Information:
– Ticker: The stock symbol.
– Company Name: The name of the company.
– GICS Sector: The Global Industry Classification Stan- dard sector.
– GICS Sub-Industry: The sub-industry classification.
# Steps (1) Analyze the Time-Series Data: Review the historical daily returns to identify patterns, trends, or anomalies that may affect future performance.
(2) Consider Sector Performance: Analyze how the market and the sector’s performance might influence the stock’s future returns.
(3) Incorporate Company Information: Use the details from the GICS sector and sub-industry, along with the company symbol and name, to contextualize the predicted performance within its industry.
(4) Predict Future Returns: Estimate the average daily re- turns for the next two weeks based on the analysis of available data.
# Output Format Return a single float value that represents the pre- dicted average daily return for the stock over the next two weeks, without any additional commen- tary or explanation.
# Notes • Ensure the prediction considers the quantified data from the time-series.
• Make calculations based on statistical trends from daily returns data.
• Pay attention to the trends within both the stock’s daily returns and the market’s return data.
• Consider the relevance of the company’s sector to refine your predictions.
• Make calculations without additional interpretation or commentary.
Figure 5: The structure of the system prompt used to elicit return forecasts from the LLMs.
• The sum of the portfolio weights equals 1 (Í𝑤𝑖= 1), • No shorting is allowed, meaning each weight is non-negative (𝑤𝑖≥0 for all 𝑖).

<!-- page 11 -->

LLM-Enhanced Black-Litterman Portfolio Optimization CIKM’25 Workshop on FinAI, November 14, 2025, Seoul, Republic of Korea User Prompt Daily Returns: [-1.17, -0.92, -2.31, -0.36, -3.02, 2.53, 0.1, -0.23, 0.45] Company Sector: Information Technology Sector Returns: [-0.14, -0.38, -1.88, 0.03, -1.1, 2.38, -0.41, 0.17, -0.31] Market Returns: [0.09, -0.39, -1.61, -0.04, -0.67, 2.05, -0.56, 0.4, -0.01] Company Information:
Ticker: AAPL Company Name: Apple Inc.
GICS sector: Information Technology GICS sub-industry: Technology Hardware, Storage & Peripherals Figure 6: An example user prompt providing data for Apple Inc. (AAPL) on a specific rebalancing date.
The optimal portfolio weights are obtained by minimizing the ob- jective function.
B.2 Baseline Portfolio For comparison, MVO is optimized using the traditional mean- variance framework, which is based on historical returns and the covariance matrix of asset returns. The mean-variance optimization problem aims to maximize the expected return while minimizing the portfolio’s risk.
The optimization problem is formulated as:
min w  w𝑇Σw −𝜆· w𝑇r  where:
• w𝑇Σw represents the portfolio risk (variance), • w𝑇r represents the portfolio return, The portfolio risk (variance) and portfolio return are defined similarly in both optimization problems, with w𝑇Σw representing risk and w𝑇r representing return. The optimization problem is subject to the same constraints:
• The sum of the portfolio weights equals 1 (Í𝑤𝑖= 1), • No shorting is allowed, meaning each weight is non-negative (𝑤𝑖≥0 for all 𝑖).
The result of this optimization provides the portfolio weights for the baseline portfolio.
B.3 Detailed Model-Level Statistics B.3.1 View Statistics. Table 4 provides the summary statistics for the entire population of raw views generated by each LLM through- out the test period. These statistics reveal the distinct predictive "styles" of the models that were discussed in the main analysis. For instance, BLM-Llama is characterized by the highest mean return but also the largest standard deviation and the widest min-max range, indicating a high-conviction, high-dispersion approach. In contrast, BLM-Qwen shows the lowest standard deviation, reflecting a more cautious and stable view generation process, while BLM-Gemma is notable for its negative mean, confirming a persistent pessimistic bias. These underlying statistical properties are the root cause of the performance differences analyzed in the main text.
Table 4: Summary Statistics of LLM-Generated Views Metric BLM-Gemma BLM-Qwen BLM-Llama BLM-GPT Count 100000 100000 100000 100000 Mean −0.3847 0.1007 0.1786 0.1347 Std 0.9711 0.2872 0.6903 0.4805 Min −22.3000 −4.7500 −57.9913 −6.9250 25% −1.1200 0.0100 0.0075 −0.0244 Median −0.6600 0.0300 0.0270 0.1000 75% 0.3200 0.1200 0.2000 0.3190 Max 4.8100 3.1400 91.6982 6.1140 B.3.2 Analysis of Forecasting Errors. Table 5 presents an analysis of the forecasting accuracy for the views generated by each LLM and for the traditional estimate used by the MVO benchmark. The table quantifies the prediction error by comparing the expected returns—either generated by an LLM or, in the case of MVO, es- timated from the historical average of past returns—against the actual realized returns of the subsequent period. This error is mea- sured using three standard metrics where lower values are better:
Mean Squared Error (MSE), Root Mean Squared Error (RMSE), and Mean Absolute Error (MAE).
The results reveal a strong correspondence between a model’s forecasting accuracy and its ultimate portfolio performance, as de- tailed in Table 3. BLM-Qwen and BLM-Llama, which demonstrated the highest predictive accuracy by achieving the lowest errors across all three metrics, also generated the portfolios with the best absolute and risk-adjusted returns (CAGR and Sharpe Ratio respec- tively). This provides direct evidence that their outperformance was rooted in a superior underlying ability to forecast market returns.
Conversely, the MVO benchmark, relying on naive historical av- erages, exhibited high prediction errors and correspondingly poor investment results. Interestingly, while BLM-Gemma also showed high forecasting errors—even worse than MVO’s—its final portfo- lio outperformed both MVO and BLM-GPT in terms of CAGR. This suggests that within the Black-Litterman framework, the nature of the views can be as important as their raw accuracy; the consistent (though pessimistic) bias of Gemma may have provided a more stable, albeit flawed, signal for the optimizer to work with.
Table 5: Comparison of Prediction Errors Metric MVO BLM-Gemma BLM-Qwen BLM-Llama BLM-GPT MSE ↓ 0.9376 1.2373 0.5125 0.5288 0.6505 RMSE ↓ 0.9683 1.1123 0.7159 0.7272 0.8066 MAE ↓ 0.6989 0.8608 0.5168 0.5281 0.5702

<!-- page 12 -->

CIKM’25 Workshop on FinAI, November 14, 2025, Seoul, Republic of Korea Lee et al.
B.4 Analysis of Portfolio Allocation Dynamics Figures 7 and 8 illustrate the temporal evolution of portfolio alloca- tions for the LLM-driven and baseline strategies, respectively.
Figure 7 details the asset weights at each rebalancing date for the portfolios constructed using our proposed framework. The allocations shown are dynamically adjusted based on the predictive views generated by each respective LLM. For comparison, Figure 8 displays the allocations for the baseline portfolios. These include the static, uniformly distributed EW strategy and the MVO portfolio, whose weights are derived solely from historical data.

<!-- page 13 -->

LLM-Enhanced Black-Litterman Portfolio Optimization CIKM’25 Workshop on FinAI, November 14, 2025, Seoul, Republic of Korea Figure 7: Time-series of Asset Allocation Weights for BLM Portfolios

<!-- page 14 -->

CIKM’25 Workshop on FinAI, November 14, 2025, Seoul, Republic of Korea Lee et al.
Figure 8: Time-series of Asset Allocation Weights for Baseline Portfolios
