# IEEE_2025_MTGPR_soybean_oil_futures_forecasting

> 원본: `docs/research_desk/references/IEEE_2025_MTGPR_soybean_oil_futures_forecasting.pdf` · SHA256 `5464c19c8318cf24…` · 10쪽 · 42,186자 · 변환 2026-09-09 (pdf_to_markdown.py)

## 목차(자동 복원)
- Bayesian-Optimized Multi-Task Gaussian Process (p.1)
- Regression With Composite Kernels for (p.1)
- Soybean Oil Futures Forecasting (p.1)

## 본문

<!-- page 1 -->

Received 25 May 2025, accepted 14 June 2025, date of publication 19 June 2025, date of current version 27 June 2025.
Digital Object Identifier 10.1109/ACCESS.2025.3581288

## Bayesian-Optimized Multi-Task Gaussian Process


## Regression With Composite Kernels for


## Soybean Oil Futures Forecasting

HUI-DONG YIN AND YI-YANG LI School of Mathematics, Physics and Statistics, Shanghai University of Engineering Science, Shanghai 201620, China Corresponding author: Hui-Dong Yin (M440124120@sues.edu.cn) This work was supported by Vertical Scientific Research Development Special Project under Grant 0244-E2-6204-24-KYFZ033.
ABSTRACT Accurate forecasting of agricultural commodity prices is critical for economic stability and strategic decision-making, yet remains challenging owing to nonlinear dynamics and multifactorial volatility.
This study addresses the forecasting of soybean oil prices in China’s wholesale markets by developing a Bayesian-optimized Multi-Task Gaussian Process Regression (MTGPR) framework. Traditional econo- metric models and machine learning approaches often struggle with non-stationary data and uncertainty quantification, while existing Gaussian process applications in agricultural markets remain underexplored.
We propose a composite kernel architecture integrating Matérn 2.5 and Exponential Sine Squared (ESS) kernels to capture localized price trends, periodic cycles, and heteroskedastic volatility. The framework incorporates futures market indicators and employs spectral analysis with Reproducing Kernel Hilbert Space (RKHS) theory for feature alignment. Using a decade-long dataset (2015–2024) of daily soybean oil prices, the model undergoes rigorous validation via cross-validated Bayesian optimization, bootstrap error estimation, and posterior predictive intervals. Comparative evaluations against Long Short-Term Memory (LSTM), Gated Recurrent Unit (GRU), Support Vector Regression (SVR) and Extreme Gradient Boosting (XGBoost) demonstrate MTGPR’s superiority, achieving a mean absolute percentage error (MAPE) of 0.85% and R2 of 0.9313. Key innovations include adaptive kernel selection, probabilistic uncertainty bands for risk-aware strategies, and cross-market transferability analysis. Results confirm the model’s capacity to disentangle complex market patterns while maintaining computational tractability. This work advances agricultural price forecasting by bridging theoretical Bayesian methods with practical trading applications, offering policymakers and market participants a robust tool for hedging and supply chain optimization.
INDEX TERMS Bayesian methods, Gaussian processes, Mercer kernel functions, agricultural forecasting, commodity price forecasting.
I. INTRODUCTION Agricultural commodity price forecasting constitutes a criti- cal operational imperative for market participants and policy- makers, driven by the inherent strategic value of agricultural products in maintaining national economic stability and food security. This forecasting process serves as a multidimen- sional decision-support mechanism: enabling processors to The associate editor coordinating the review of this manuscript and approving it for publication was Jolanta Mizera-Pietraszko .
optimize pricing strategies through forward-looking sales projections, equipping traders with actionable intelligence for contractual risk mitigation, identifying arbitrage opportuni- ties across spot and futures markets, while simultaneously alerting regulatory bodies to systemic vulnerabilities in agri- cultural supply chains. The urgency of accurate forecasting stems from three interlocking market dynamics—pronounced price volatility amplified by geopolitical and environmental uncertainties, cascading impacts on cross-sectoral decision- making processes, and macroeconomic repercussions 107532 2025 The Authors. This work is licensed under a Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 License.
For more information, see https://creativecommons.org/licenses/by-nc-nd/4.0/ VOLUME 13, 2025

<!-- page 2 -->

H.-D. Yin, Y.-Y. Li: Bayesian-Optimized MTGPR With Composite Kernels affecting resource allocation efficiency. Despite these oper- ational imperatives, agricultural price prediction remains methodologically intractable due to the inherent nonlinearity and structural complexity embedded within commodity time- series data, necessitating advanced analytical frameworks that transcend conventional econometric approaches.
The evolution of commodity forecasting methodologies has progressed through two distinct epochs. Early research predominantly employed time-series models (Auto Regres- sive Integrated Moving Average, ARIMA; Vector Error Cor- rection Model, VECM), leveraging their mathematical rigor in capturing linear dependencies. The computational revo- lution of the past decade catalyzed a paradigm shift toward machine learning techniques, with neural networks, ensem- ble methods, and deep learning architectures demonstrating superior predictive accuracy in modeling nonlinear price dynamics. Recent advancements in Bayesian machine learn- ing have further addressed fundamental limitations through three transformative capabilities: (1) probabilistic uncertainty quantification via posterior distributions, (2) intrinsic reg- ularization mechanisms for overfitting mitigation [1], and (3) dynamic knowledge integration through sequential Bayesian updating [2]. These theoretical breakthroughs underpin Gaussian process regression (GPR), a non- parametric Bayesian framework whose mathematical foun- dations originate from Neal’s seminal work on infinite-width neural networks [3]. GPR’s operational superiority stems from two distinct attributes: exact Bayesian inference enabled by kernel covariance structures, and empirically validated robustness across diverse data environments—from noise- free theoretical scenarios [4] to real-world noisy obser- vations [5]. Building upon Brahim-Belhouari’s pioneering demonstrations of GPR’s dominance over traditional neural networks in agricultural forecasting [6], [7], contemporary research has developed adaptive covariance optimization techniques capable of handling non-stationary time-series through ensemble-GPR frameworks. Nevertheless, a critical research gap persists in applying these advanced Bayesian methodologies to agricultural commodities, particularly for economically strategic products like soybean oil where high-frequency price fluctuations demand specialized mod- eling approaches.
Soybean oil markets epitomize the forecasting chal- lenges and strategic significance of agricultural commodities.
Their tripartite economic role encompasses: (1) bioenergy feedstock production driving renewable energy transitions, (2) financial derivatives deeply integrated into global trading systems, and (3) essential inputs for both culinary consump- tion and industrial food processing.
We bridge the gap between theoretical and applied research by making three key contributions. First, we develop a Bayesian-optimized GPR framework specifically designed for non-stationary agricultural commodity price series. This framework integrates futures market indicators with compos- ite kernel functions, where kernel compatibility is addressed through spectral analysis and Reproducing Kernel Hilbert Space (RKHS) theory, ensuring optimal feature space align- ment while maintaining computational tractability. Second, leveraging a decade-long dataset of daily wholesale prices in China’s soybean market, we validate prediction accuracy with over 3,600 high-frequency observations. Comparative analy- sis against benchmarks—including Long Short-Term Mem- ory (LSTM), Gated Recurrent Unit (GRU), Support Vector Regression (SVR), Extreme Gradient Boosting (XGBoost), and hybrid deep learning models—demonstrates the supe- rior performance of GPR. Robustness is further confirmed through confidence intervals, cross-validation variability metrics, bootstrap error estimation, and posterior predictive intervals. Third, we extend the framework to multivariate settings to uncover interdependencies among data features and discuss scalable implementations for cross-commodity forecasting.
Methodologically, the framework introduces four inno- vations:(1) multi-source feature engineering incorporat- ing macroeconomic indicators and market fundamentals, (2) adaptive kernel selection via Bayesian hyperparameter optimization, (3) probabilistic uncertainty bands enabling risk-aware trading strategies, and (4) cross-market transfer- ability validation through commodity covariance analysis.
Empirical results demonstrate GPR’s dual capability in technical forecasting and policy applications. These advance- ments directly support dynamic hedging ratio optimization and supply chain stabilization strategically vital soybean oil sector, while the modular architecture permits seamless inte- gration into existing trading systems and risk management platforms.
II. LITERATURE REVIEW The evolution of agricultural price forecasting has transi- tioned from traditional econometric models like ARIMA to advanced machine learning frameworks, driven by the need to address nonlinear market dynamics and multifacto- rial influences. While ARIMA models demonstrated initial success in commodities forecasting through historical pattern analysis [8], [9], [10], their limitations in handling volatil- ity from climatic, geopolitical, and supply chain disruptions necessitated methodological innovations [12], [19]. LSTM networks emerged as superior alternatives, achieving over 80% trend accuracy in soybean futures prediction by focus- ing on high/low price boundaries with reduced noise [12].
Modified Transformer architectures further enhanced tem- poral feature extraction through multi-scale time decompo- sition and isolation forest-based data refinement, reducing grain price errors by 15-20% compared to conventional models [14]. Hybrid optimization strategies proved partic- ularly effective, exemplified by Genetic Simulated Anneal- ing Algorithm-Backpropagation Neural Network Model (GSAA-BP model) combining genetic algorithms and simu- lated annealing to optimize neural network weights, yielding 1.5% Mean Absolute Error (MAE) in potato price fore- casts [15]. Comparative analyses reveal machine learning’s superiority, as demonstrated by particle swarm-optimized VOLUME 13, 2025 107533

<!-- page 3 -->

H.-D. Yin, Y.-Y. Li: Bayesian-Optimized MTGPR With Composite Kernels Backpropagation (BP) networks reducing training errors by 30% in vegetable price predictions compared to baseline models [17]. Emerging approaches integrate multivariable analysis, such as decision tree regression models incor- porating climatic and market data for crop-specific fore- casting [18], while structural vector autoregression (SVAR) methods expose asymmetric international price transmis- sion mechanisms requiring policy interventions [19]. These innovations collectively establish machine learning as the dominant paradigm for balancing computational efficiency with multifactorial accuracy in agricultural markets.
Vegetable oil price forecasting exemplifies the method- ological transition from conventional to data-driven approaches. Initial studies on crude palm oil (CPO), soybean oil, and rapeseed oil relied on ARIMA variants, with Tham- biah demonstrating Multivariate Autoregressive Moving Average (MARMA)’s superiority over VECM and ARIMA in Malaysian CPO markets through cross-commodity variable integration (Root Mean Squared Error, RMSE reduction:
18-22%) [20]. Subsequent innovations addressed nonlinear patterns through machine learning, as Kanchymalay et al.
achieved SVR-based CPO predictions with 0.92 RMSE by incorporating energy market variables [21], while Karia et al. showed neural networks’ adaptability to daily CPO volatility (Mean Absolute Percentage Error, MAPE:
1.2% vs. Autoregressive Fractionally Integrated Moving Average, ARFIMA’s 2.1%) [22]. Hybrid architectures com- bining signal processing and Machine Learning (ML) further enhanced performance—Li et al. improved soybean oil futures directional accuracy to 87% through wavelet-based noise reduction [23], and Rahim et al. reduced CPO fore- casting errors to 2.3% MAPE via fuzzy time series-sliding window integration [24]. Contemporary frameworks increas- ingly incorporate external market drivers, with Tang et al.
achieving 12% RMSE reduction in Chinese palm oil futures through spatiotemporal modeling of price spillovers [25], while text mining innovations like An et al.’s Temporal Sparse Hierarchical LSTM(TSH-LSTM) demonstrated sub- 1.5% MAPE by fusing social media sentiment analysis with historical prices [26].
China’s strategic position as both the world’s largest vegetable oil consumer and a top producer intensifies the practical demand for accurate forecasting frameworks. The market’s complexity stems from three unique characteristics:
(1) High import dependency (e.g., 65% palm oil imports), (2) Domestic production volatility (soybean/rapeseed yield fluctuations up to ±15% annually), and (3) Energy-market coupling through biofuel policies. These factors amplify price volatility, necessitating models that simultaneously address nonlinear trends, cross-commodity dependencies, and exter- nal shocks. Recent attempts to model China’s vegetable oil markets have yielded mixed results—Xu and Zhang’s Nonlinear Autoregressive Recurrent Neural Network with exogenous inputs (NARNN–X) achieved 1.695% RMSE for soybean oil through cross-price variable integration [27], yet struggled with interpretability challenges common to neural architectures [28]. This underscores the critical need for frameworks balancing predictive accuracy, computational efficiency, and decision-support transparency—a gap our study systematically addresses via Bayesian-optimized Gaus- sian process regression.
III. METHODS A. GAUSSIAN PROCESS REGRESSION GPR constitutes a Bayesian non-parametric framework for regression, providing probabilistic predictions with intrinsic uncertainty quantification through kernel-based modeling.
Unlike deterministic methods like linear regression, which assume fixed parametric relationships (e.g., y = xTβ + ϵ), GPR generalizes multivariate Gaussian distributions to infinite-dimensional function spaces, enabling flexible mod- eling of nonlinear patterns via latent variables governed by joint Gaussian distributions. This framework leverages kernel functions k  x, x ′|θ  —such as radial basis functions (RBF) or Matérn kernels—to encode prior assumptions about function smoothness and input-output interactions, while basis functions b (x) project inputs into nonlinear feature spaces. The predictive posterior distribution, derived from hyperparameters θ, noise variance σ 2, and basis coefficients β, delivers mean estimates with variance bounds criti- cal for risk-sensitive applications like financial forecasting.
While GPR avoids underfitting/overfitting trade-offs through adaptive complexity, its O   n3 computational scaling with dataset size n limits big-data applicability, necessitating strategic hyperparameter tuning for optimal performance.
Multi-Task Gaussian Process Regression (MTGPR) extends the conventional GPR framework by integrating shared latent structures across correlated tasks through block-structured covariance kernels, effectively capturing cross-task dependencies via a multivariate Gaussian dis- tribution over outputs Y =  yT 1,yT 2 , · · · ,yT T T. This approach employs two principal paradigms: the Intrinsic Coregionalization Model (ICM), which simplifies cross-task covariance as Kinter  x, x ′ = B ⊗kintra  x, x ′ , where B = WWT   W ∈RT×r reduces computational overhead while preserving task correlations, and the Linear Model of Coregionalization (LMC), which generalizes ICM by combining multiple base kernels PQ q=1 Bq ⊗kq  x, x ′ to hierarchically model complex task interactions. However, its computational complexity scales with task count T, neces- sitating sparse approximations or variational inference for scalability.
B. CONSTRUCTION OF KERNEL FUNCTIONS 1) KERNEL FUNCTIONS Kernel function design plays a pivotal role in GPR, as real- world data often exhibits multifaceted patterns that sin- gle kernels inadequately capture. Building on Rasmussen and Williams foundational work in Gaussian Processes for Machine Learning [29], composite kernels constructed via 107534 VOLUME 13, 2025

<!-- page 4 -->

H.-D. Yin, Y.-Y. Li: Bayesian-Optimized MTGPR With Composite Kernels summation, multiplication, or convolution of base kernels enable enhanced adaptability to complex data structures. For instance, Palar et al. demonstrated that kernel performance is problem-dependent across four engineering case studies, with composite kernels often outperforming intuitive selec- tions [30]. This study evaluates five base kernels:(where σ 2 f , l, and p govern amplitude, smoothness, and periodicity.) RBF k   x, x′ = σ 2 f e−∥x−x′∥2 2l2 The RBF kernel captures short-term trend continuity in futures price dynamics, where adjacent time points exhibit strong correlation coefficients, while distant intervals show exponentially decaying dependencies. This mechanism effec- tively models localized price momentum driven by transient supply-demand imbalances, such as consecutive intraday price surges triggered by speculative trading activities.
FIGURE 1. RBF kernel: Prior samples (wide uncertainty) vs. posterior samples (reduced uncertainty) around sample data.
FIGURE 2. Matérn 1.5 kernel: Prior samples (wide uncertainty) vs.
posterior samples (reduced uncertainty) around sample data.
Matérn 1.5 k   x, x′ = σ 2 f 1 + √ 3 x −x′ l !
e− √ 3∥x−x′∥ l Matérn 2.5 k   x, x′ = σ 2 f 1 + √ 5 x −x′ l + 5 x −x′2 3l2 !
e− √ 5∥x−x′∥ l The Matérn kernel, quantifies mid-term market fluctuations characterized by non-stationary heteroskedasticity—evident in agricultural futures where seasonal climatic anomalies (e.g., prolonged droughts) induce discrete price jumps rather than smooth transitions.
Periodic Quadratic (PQ) k   x, x′ = σ 2 f 1 + x −x′2 2αl2 !−α For cyclical patterns, the pq kernel explicitly encodes seasonal oscillations, as exemplified by soybean futures governed by biannual planting-harvest cycles, where fixed-period spectral components align with empirical price recurrence intervals.
FIGURE 3. Matérn 2.5 kernel: Prior samples (wide uncertainty) vs.
posterior samples (reduced uncertainty) around sample data.
FIGURE 4. PQ kernel: Prior samples (wide uncertainty) vs. posterior samples (reduced uncertainty) around sample data.
Exponential Sine Squared (ESS) k   x, x′ = σ 2 f e− 2 sin2 π∥x−x′∥ p l2 To address complex aperiodic cycles, the ess kernel dynam- ically adapts its harmonic parameters, thereby facilitating robust modeling of ‘‘elastic periodicity’’ phenomena.
VOLUME 13, 2025 107535

<!-- page 5 -->

H.-D. Yin, Y.-Y. Li: Bayesian-Optimized MTGPR With Composite Kernels FIGURE 5. ESS kernel: Prior samples (wide uncertainty) vs. posterior samples (reduced uncertainty) around sample data.
TABLE 1. Qualitative comparative analysis of kernel functions.
Thirty additive/multiplicative composite kernels are tested, though preliminary trials revealed prohibitive computational costs and over smoothing in complex combinations, prompt- ing a focus on balanced simplicity and efficacy.
2) SPECTRAL ANALYSIS Spectral analysis, a cornerstone of modern signal process- ing, decomposes signals into frequency components via fourier transforms or wavelet techniques, enabling precise identification of periodic patterns and transient anomalies.
By converting time-domain data into frequency-domain rep- resentations (e.g., energy spectra or power spectral density), it quantifies signal characteristics such as harmonic dom- inance and noise interference thresholds. Recent advances integrate machine learning for automated frequency band selection, enhancing robustness in non-stationary environ- ments.
3) REPRODUCING KERNEL HILBERT SPACE RKHS provide a rigorous mathematical framework for kernel-based learning by embedding functions into infinite- dimensional hilbert spaces where point evaluation is contin- uous. A kernel k   x, x′ satisfying the reproducing property ⟨f , k (·, x)⟩H = f (x) induces an RKHS, enabling mercer’s theorem-based decomposition into orthogonal eigenfunc- tions. This underpins kernel trick efficacy in support vector machines (SVMS) and GPR, where high-dimensional inner products are computed implicitly via kernel evaluations.
The Mercer expansion k   x, x′ = P∞ i=1 λiφi (x) φi   x′ , with eigenvalues λi and eigenfunctions φi, ensures univer- sal approximation capabilities for radial basis and Matérn kernels.
C. BAYESIAN OPTIMIZATION Model parameter estimation employs five-fold cross- validation integrated with Bayesian optimization using the Expected Improvement Per Second Plus (EIPSP) framework.
A Gaussian Process (GP) surrogate model f (x) is initial- ized by evaluating yi = f (xi) at Ns = 10 randomly sampled points within variable boundaries, ensuring robust- ness against evaluation faults until Ns successful trials are obtained. The algorithm iteratively updates f (x) to derive posterior distributions Q   f |xi,yi  for i = 1, · · · , T, while selecting new points x to minimize the acquisition function a (x). This process, capped at 100 iterations, leverages the expected improvement (EI) criterion:
EI (x, Q) = EQ  max   0, µQ (xbest) −f (x)  , where µQ (xbest) denotes the posterior mean at the opti- mal point xbest. To address heterogeneous evaluation times, EIPSP incorporates temporal weighting via a secondary GP timing model µS (x), defining time-adjusted improvement as:
EIPS (x) =EIQ (x) µS (x) .
Exploration-exploitation balance is enhanced by moni- toring posterior deviations σ F (x) and noise σ PN. If σ F (x) < tσ PN σ PN, the kernel hyperparameter θ is scaled iteratively to avoid local minima, with a tenfold increase per- mitted for up to five attempts to resolve overexploitation. This adaptive mechanism ensures efficient global optimization by prioritizing regions with high uncertainty or temporal gains.
D. DATA AND PREPROCESSING 1) DATA DESCRIPTION This study investigates the daily wholesale price indices of soybean oil in the Chinese market. The dataset was sourced from historical trading records of the Zhengzhou Commodity Exchange and Dalian Commodity Exchange. The dataset comprises eight core features: date, opening price, high price, low price, closing price, trading volume, open inter- est, and dynamic settlement price. Additionally, nine futures technical indicators were integrated to enhance predictive modeling:5-day, 10-day, and 20-day moving averages (MA5, MA10, MA20),7-day and 14-day relative strength indices (RSI7, RSI14), Bollinger Bands, Moving Average Conver- gence Divergence (MACD), On-Balance Volume (OBV), Momentum (MOM).
2) PREPROCESSING Gaussian processes demonstrate robust capability in handling multidimensional inputs; however, attention must be directed toward inter-dimensional correlations and redundancy to mit- igate potential high linear interdependencies. This can be systematically addressed through feature selection via Prin- cipal Component Analysis (PCA), which effectively reduces dimensional redundancy while preserving critical covariance structures.
107536 VOLUME 13, 2025

<!-- page 6 -->

H.-D. Yin, Y.-Y. Li: Bayesian-Optimized MTGPR With Composite Kernels TABLE 2. The PCA graph after feature screening.
FIGURE 6. PCA score plot of price trend and momentum intensity relationships: Distribution colored by close price (4000-12000), showing a progression from lower prices (purple, bottom-left) to higher prices (yellow, top-right) along the principal components (PC1: 64.1%, PC2: 26.7%).
FIGURE 7. Key PCA drivers: Price & MAs drive PC1. Heatmap: Significant feature loadings (|λ| > 0.3) for PC1 & PC2. Deep blue = strong association.
Principal Component 1 (PC1), identified as the price trend factor, integrates foundational market indicators including opening, high, low, and closing prices, alongside mov- ing averages (MA5, MA10, MA20), collectively capturing directional price dynamics. Principal Component 2 (PC2), characterized as the momentum-volatility factor, synthesizes technical oscillators (RSI14, MOM) and MACD compo- nents (MACD, MACD-hist), effectively quantifying kinetic market transitions and volatility regimes. The cumula- tive contribution rate of PC1 and PC2 reaches 90.8%, demonstrating comprehensive coverage of dataset variance.
PC1 serves as a robust proxy for trend directionality, while PC2 isolates short-term volatility patterns, thereby FIGURE 8. Proportion of variance explained by principal components:
PC1 (64.12%) and PC2 (26.7%) contributing to 90.8% cumulative variance, highlighting efficient data representation.
synergistically enabling trend-following and mean-reversion strategies. Threshold-based operationalization—PC1 >5 (strong trend) and PC2 >1.5 (overbought conditions)— provides quantifiable parameters directly applicable to algo- rithmic trading systems, ensuring alignment with systematic investment frameworks.
IV. RESULTS A. DETERMINATION OF KERNEL FUNCTIONS Our study employs soybean oil futures data, with the train- ing set spanning January 1, 2020, to December 31, 2023, and the test set covering January 1 to December 31, 2024, to validate a Bayesian-optimized GPR framework incorpo- rating futures market indicators. The framework’s robustness is demonstrated through confidence intervals, cross-validated variability metrics, bootstrap error estimation, and posterior predictive intervals, supported by spectral analysis and the RKHS methodology. This systematic validation ensures the selection of composite kernel functions optimally suited for modeling soybean oil futures dynamics under the proposed framework.
To mitigate stochastic perturbations originating from model initialization randomness, optimization process vari- ability, non-deterministic kernel matrix computations, and likelihood function approximations, the model underwent five consecutive independent training trials. Evaluations demonstrated that the composite kernel configuration Matérn 2.5 × ESS achieved superior performance metrics. (Since only the fitting effect of the model needs to be evaluated, the standardized data are directly used to calculate MAE and RMSE) The model demonstrates robust predictive performance, with MAE values maintained between 5.3 and 5.9 percentage points across all trials, accompanied by a minimal stan- dard deviation of 0.0023 over five independent experiments, indicating exceptional stability in absolute error control.
While RMSE exhibits higher sensitivity to outliers, it remains within a stable range overall. MAPE consistently falls below 1.1% in all experimental configurations, achieving VOLUME 13, 2025 107537

<!-- page 7 -->

H.-D. Yin, Y.-Y. Li: Bayesian-Optimized MTGPR With Composite Kernels TABLE 3. Performance comparison across six evaluation metrics.
precision levels considered advanced within financial fore- casting applications. All trials yield the coefficient of deter- mination (R2) values exceeding 0.89, confirming the model’s capacity to explain approximately 90% of the observed variance. Notably, the coverage probability and effective dimensionality metrics demonstrate complete stability, ver- ifying structural invariance under stochastic perturbations during both training and inference phases.
To demonstrate the proposed model’s superiority over contemporary benchmarks, soybean oil futures data span- ning January 1, 2015, to December 31, 2022, were selected as the training set, while data from January 1, 2023, to December 31, 2024, served as the testing cohort. This temporal partitioning aligns with computational finance conventions for evaluating time-series forecasting robust- ness, ensuring rigorous validation against both pre- and post-pandemic market regimes. The 80/20 split ratio mitigate temporal overfitting risks while preserving seasonality pat- terns inherent to agricultural commodity cycles.
FIGURE 9. Eigenvalue decay: Exponential decline (index < 20) followed by asymptotic convergence, indicating concentrated energy and low-rank structure.
Fig. 9 demonstrates the kernel matrix exhibits a low effec- tive rank, with a minimal number of principal components required to account for the majority of data variance. The model autonomously regulates complexity through kernel FIGURE 10. Composite kernel matrix heatmap (64 × 64). Colors show pairwise similarity (0.02-0.06), revealing clustering patterns and symmetry. Axes: Selected indices.
FIGURE 11. Multi-target price forecasts (open/highest/lowest) with 95% CI (Nov 2023–Jan 2025)(a) Open, (b) Highest, (c) Lowest prices: True (blue solid), Predicted (red dashed), and confidence intervals (yellow shading).
function selection, effectively capturing critical patterns such as periodicity and localized trends while mitigating overfit- ting to noise, thereby enhancing generalization capabilities.
Fig. 10 confirms kernel effectiveness: smooth color gra- dients in the matrix illustrate balanced local sensitivity and global periodicity, circumventing limitations inherent to 107538 VOLUME 13, 2025

<!-- page 8 -->

H.-D. Yin, Y.-Y. Li: Bayesian-Optimized MTGPR With Composite Kernels FIGURE 12. Residual plot showing random scatter. Residuals are uniformly distributed around zero across the predicted value range (0 to 1), suggesting well-fitted model assumptions.
FIGURE 13. Bootstrap MSE distribution: Concentration near 0.045(Histogram with KDE showing consistent error estimates from bootstrap resampling).
single-kernel configurations. The symmetric distribution of the composite kernel matrix further ensures stable similarity representation, eliminating pathological covariance condi- tions.As shown in Fig. 11, the blue prediction trajectory aligns closely with the red ground-truth values, indicat- ing successful modeling of nonlinear trends and cyclical fluctuations in soybean oil futures. This validates that the composite kernel—combining short-term volatility smooth- ing via the Matérn kernel and periodic regularity via the Exponential Sine Squared kernel—enables robust characteri- zation of complex market behaviors. Fig. 12 reveals residuals (−0.2–0.2) exhibit no systematic bias or heteroscedasticity, confirming the absence of underfitting (e.g., model mis- specification) or overfitting (e.g., variance amplification).
Residual stability across normalized price intervals (0.2–1.0) demonstrates adaptability to diverse market regimes. The model successfully disentangles latent market dynamics (e.g., trend-noise separation), validating its applicability to real-world trading strategies. Fig. 13 displays boot- strapped errors following a unimodal Gaussian distribution (peak Mean Squared Error, MSE = 0.045 ± 0.003), with frequency decaying exponentially beyond ±2σ, signify- ing consistent performance across data subsets and strong generalization robustness—critical for high-volatility finan- cial environments.
TABLE 4. Performance comparison across six evaluation metrics.
V. DISCUSSION A. COMPARISON MODEL: LSTM, GRU, SVR, XGBOOST A shared LSTM layer was employed to extract common tem- poral features, forming a multi-task architecture with three independent output layers for distinct prediction targets. Dual normalizers were applied independently to features and labels to prevent information leakage during preprocessing. The model’s temporal scope was configured with a 60-day histor- ical window to capture medium-to-long-term trend patterns.
Early stopping regularization was implemented to mitigate overfitting, while the Adam optimizer (Adaptive Moment Estimation) dynamically adjusted learning rates during train- ing. Performance metrics including MAE, RMSE, MAPE, and R2 were systematically calculated.
The shared GRU encoder layer captures temporal patterns from sequential data, while task-specific output layers handle multi-task variations through parallel processing branches.
To enhance sequential modeling capabilities, we adopt a two-layer cascaded GRU architecture where the output of the first layer feeds into the subsequent layer. Feature nor- malization ensures distributional consistency across input dimensions, with time-series sliding window generation strengthening temporal correlations in the data streams. Dur- ing loss function design, we implement a composite loss combining MAE and MSE through weighted fusion coef- ficients, where α controls the balance between linear and quadratic error terms. For final evaluation, the three predic- tion targets’ outputs are flattened into a unified dimensional space.
Multi-task SVR and XGBoost framework ware imple- mented to achieve joint prediction of multiple objectives.
Feature normalization was applied to eliminate scale dis- crepancies among input variables, thereby enhancing model performance. The predictions of the three target variables were flattened into a single vector, and a global error metric was caculated.
B. RESULT COMPARISON See Table 4.
VOLUME 13, 2025 107539

<!-- page 9 -->

H.-D. Yin, Y.-Y. Li: Bayesian-Optimized MTGPR With Composite Kernels VI. CONCLUSION This study addresses the challenge of forecasting soybean oil price indices in China’s wholesale markets. Utilizing daily data from January 1, 2020, to December 31, 2024, we developed a MTGPR forecasting model. We employed a cross-validated Bayesian optimization approach and sys- tematically evaluated 30 composite kernel functions. Our analysis demonstrated that the Matérn 2.5 × ESS kernel outperformed other simple composite kernels (to ensure practical applicability in financial scenarios) in capturing diverse characteristics of soybean oil markets. Comparative analyses with benchmark models—including LSTM, GRU, SVR, and XGBoost—validated the superiority of our frame- work using extended datasets spanning January 1, 2015, to December 31, 2024. Methodologically, the integration of PCA, spectral analysis, RKHS theory, heteroscedasticity measures, bootstrap error estimation, posterior predictive intervals, and model evaluation metrics ensured compatibil- ity, reliability, and robustness. The proposed model serves as a valuable tool for market participants and policymak- ers to refine analytical capabilities in soybean oil wholesale markets.
Three limitations warrant attention. First, while GPR was selected due to its underutilization in agricultural price fore- casting, alternative machine learning techniques (e.g., hybrid architectures combining LSTM and XGBoost) could be explored for similar tasks. Second, the optimization strat- egy (Expected Improvement per Second algorithm) could be compared with gradient-based or evolutionary approaches.
Third, although soybean oil holds economic significance in China’s agricultural sector, extending this framework to other edible oils (e.g., palm oil, rapeseed oil) and broader agricul- tural commodities may enhance generalizability.
REFERENCES [1] J. A. Hoeting, D. Madigan, A. E. Raftery, and C. T. Volinsky, ‘‘Bayesian model averaging: A tutorial,’’ Stat. Sci., vol. 14, no. 4, pp. 382–401, 1999.
[Online]. Available: http://www.jstor.org/stable/2676803 [2] J.
F.
G.
Freitas, M.
Niranjan, and A.
H.
Gee, ‘‘Hierarchical Bayesian models for regularization in sequential learning,’’ Neural Comput., vol. 12, no. 4, pp. 933–953, Apr. 2000, doi: 10.1162/ 089976600300015655.
[3] R. M. Neal, ‘‘Bayesian learning for neural networks,’’ IEEE Trans.
Neural Netw., vol. 8, no. 2, p. 456, Mar. 1997, doi: 10.1109/TNN.
1997.557706.
[4] R. M. Neal, ‘‘Monte Carlo implementation of Gaussian process models for Bayesian regression and classification,’’ 1997, arXiv: physics/9701026.
[5] C. E. Rasmussen and C. K. I. Williams, ‘‘Further issues and conclusions,’’ in Gaussian Processes for Machine Learning. Cambridge, MA, USA: MIT Press, 2005, pp. 189–198.
[6] S. Brahim-Belhouari and J. M. Vesin, ‘‘Bayesian learning using Gaussian process for time series prediction,’’ in Proc. 11th IEEE Signal Process.
Workshop Stat. Signal Process., Singapore, Aug. 2001, pp. 433–436, doi:
10.1109/SSP.2001.955315.
[7] S. Brahim-Belhouari and A. Bermak, ‘‘Gaussian process for nonstation- ary time series prediction,’’ Comput. Statist. Data Anal., vol. 47, no. 4, pp. 705–712, Nov. 2004, doi: 10.1016/j.csda.2004.02.006.
[8] R. Dharavath and E. Khosla, ‘‘Seasonal ARIMA to forecast fruits and vegetable agricultural prices,’’ in Proc. IEEE Int. Symp. Smart Electron. Syst. (iSES), Rourkela, India, Dec. 2019, pp. 47–52, doi:
10.1109/iSES47678.2019.00023.
[9] S. F. Asnhari, P. H. Gunawan, and Y. Rusmawati, ‘‘Predicting sta- ple food materials price using multivariables factors (Regression and Fourier models with ARIMA),’’ in Proc. 7th Int. Conf. Inf. Commun.
Technol. (ICoICT), Kuala Lumpur, Malaysia, Jul. 2019, pp. 1–5, doi:
10.1109/ICoICT.2019.8835193.
[10] C. Sharma, P. Jha, P. Anand, and M. Sharma, ‘‘Prediction and time series analysis of wheat, Rice and maize yields using ARIMA models,’’ in Proc. 3rd Int. Conf. Technolog. Advancements Comput.
Sci. (ICTACS), Tashkent, Uzbekistan, Nov. 2023, pp. 1055–1061, doi:
10.1109/ICTACS59847.2023.10389919.
[11] M. N. Rasyad and R. Tyasnurita, ‘‘Gum rosin price forecasting using a hybrid ARIMA—LSTM model,’’ in Proc. Int. Conf. Electr.
Inf. Technol. (IEIT), Malang, Indonesia, Sep. 2022, pp. 392–397, doi:
10.1109/IEIT56384.2022.9967805.
[12] C. Wang and Q. Gao, ‘‘High and low prices prediction of soybean futures with LSTM neural network,’’ in Proc. IEEE 9th Int. Conf. Softw. Eng.
Service Sci. (ICSESS), Beijing, China, Nov. 2018, pp. 140–143, doi:
10.1109/ICSESS.2018.8663896.
[13] K. Dhanasekaran, M. Ramprasath, V. Sathiyamoorthi, N. Poornima, and I.
A.
Jayaraj, ‘‘Meta-learning based adaptive crop price prediction for agriculture application,’’ in Proc.
5th Int.
Conf.
Electron., Commun.
Aerosp.
Technol.
(ICECA), Coimbatore, India, Dec.
2021, pp. 396–402, doi:
10.1109/ICECA52323.2021.
9675891.
[14] B. Mao, Y. Cao, and B. Li, ‘‘Grain price prediction model based on TimeF- iForest-Transformer,’’ in Proc. 12th Int. Conf. Adv. Cloud Big Data (CBD), Dec. 2024, pp. 37–41, doi: 10.1109/CBD65573.2024.00017.
[15] F. Gan and J. Wang, ‘‘Research on the price prediction of agricultural products based on GSAA-BP neural network,’’ in Proc. 2nd Int. Conf.
Artif. Intell., Big Data Algorithms (CAIBDA), Nanjing, China, Jun. 2022, pp. 1–5.
[16] E. Gothai, R. R. Rajalaxmi, R. Thamilselvan, and S. M. Harshath, ‘‘Forecasting price prediction for vegetables and fruits using recurrent neural network,’’ in Proc. 5th Int. Conf. Electron. Sustain. Commun. Syst.
(ICESC), Aug. 2024, pp. 1889–1896, doi: 10.1109/ICESC60852.2024.
10689876.
[17] Y. Lu, L. Yuping, L. Weihong, S. Qidao, L. Yanqun, and Q. Xiaoli, ‘‘Vegetable price prediction based on PSO-BP neural network,’’ in Proc.
8th Int. Conf. Intell. Comput. Technol. Autom. (ICICTA), Nanchang, China, Jun. 2015, pp. 1093–1096, doi: 10.1109/ICICTA.2015.274.
[18] C. Sharma, R. Misra, M. Bhatia, and P. Manani, ‘‘Price prediction model of fruits, vegetables and pulses according to weather,’’ in Proc.
13th Int. Conf. Cloud Comput., Data Sci. Eng. (Confluence), Noida, India, Jan. 2023, pp. 347–351, doi: 10.1109/Confluence56041.2023.
10048880.
[19] Y. Zhao, Y. Zhang, and C. Qi, ‘‘The interaction between Chinese export price and world import price of tangerines,’’ in Proc. Int. Asia Conf. Infor- mat. Control, Autom. Robot., Bangkok, Thailand, Feb. 2009, pp. 393–397, doi: 10.1109/CAR.2009.36.
[20] A. A. Khin, Z. Mohamed, C. A. Malarvizhi, and S. Thambiah, ‘‘Price forecasting methodology of the Malaysian palm oil market,’’ Int. J. Appl.
Econ. Finance, vol. 7, no. 1, pp. 23–36, Jan. 2013, doi: 10.3923/ijaef.
2013.23.36.
[21] K. Kanchymalay, N. Salim, A. Sukprasert, R. Krishnan, and U. R. Hashim, ‘‘Multivariate time series forecasting of crude palm oil price using machine learning techniques,’’ IOP Conf. Ser., Mater. Sci. Eng., vol. 226, Aug. 2017, Art. no. 012117, doi: 10.1088/1757-899x/226/1/012117.
[22] A. A. Karia, I. Bujang, and I. Ahmad, ‘‘Forecasting on crude palm oil prices using artificial intelligence approaches,’’ Amer. J. Oper. Res., vol. 3, no. 2, pp. 259–267, 2013, doi: 10.4236/ajor.2013.32023.
[23] G. Li, W. Chen, D. Li, D. Wang, and S. Xu, ‘‘Comparative study of short-term forecasting methods for soybean oil futures based on LSTM, SVR, ES and wavelet transformation,’’ J. Phys., Conf. Ser., vol. 1682, no. 1, Nov. 2020, Art. no. 012007, doi: 10.1088/1742-6596/ 1682/1/012007.
[24] N. F. Rahim, M. Othman, and R. Sokkalingam, ‘‘A comparative review on various method of forecasting crude palm oil prices,’’ J. Phys., Conf. Ser., vol. 1123, Nov. 2018, Art. no. 012043, doi: 10.1088/1742- 6596/1123/1/012043.
[25] D. Tang, Q. Cai, T. Nie, Y. Zhang, and J. Wu, ‘‘Agricultural price forecasting based on the spatial and temporal influences factors under spillover effects,’’ Kybernetes, vol. 54, no. 3, pp. 1321–1343, Feb. 2025, doi: 10.1108/k-09-2023-1724.
107540 VOLUME 13, 2025

<!-- page 10 -->

H.-D. Yin, Y.-Y. Li: Bayesian-Optimized MTGPR With Composite Kernels [26] W. An, L. Wang, and Y.-R. Zeng, ‘‘Text-based soybean futures price forecasting:
A two-stage deep learning approach,’’ J.
Forecasting, vol. 42, no. 2, pp. 312–330, Mar. 2023, doi: 10.1002/ for.2909.
[27] X. Xu and Y. Zhang, ‘‘Soybean and soybean oil price forecasting through the nonlinear autoregressive neural network (NARNN) and NARNN with exogenous inputs (NARNN–X),’’ Intell. Syst. Appl., vol. 13, Jan. 2022, Art. no. 200061, doi: 10.1016/j.iswa.2022.200061.
[28] X. Xu and Y. Zhang, ‘‘Edible oil wholesale price forecasts via the neu- ral network,’’ Energy Nexus, vol. 12, Dec. 2023, Art. no. 100250, doi:
10.1016/j.nexus.2023.100250.
[29] C. E. Rasmussen and C. K. I. Williams, Gaussian Processes for Machine Learning, 3rd ed., Cambridge, MA, USA: MIT Press, 2006.
[30] P. S. Palar, L. Parussini, L. Bregant, K. Shimoyama, and L. R. Zuhal, ‘‘On kernel functions for bi-fidelity Gaussian process regressions,’’ Struct. Multidisciplinary Optim., vol. 66, no. 2, p. 37, Feb. 2023, doi:
10.1007/s00158-023-03487-y.
HUI-DONG YIN received the B.S.
degree in mathematics and applied mathematics from Shanghai Lixin University of Accounting and Finance, China, in 2024. He is currently pursuing the Ph.D. degree in statistics with Shanghai Uni- versity of Engineering Science.
His research interests include Gaussian pro- cesses, with a focus on their applications in machine learning and probabilistic modeling.
YI-YANG LI received the B.S. degree in math- ematics and applied mathematics from Ludong University, Yantai, China, in 2002, and the M.S.
and Ph.D. degrees in pure mathematics from East China Normal University, Shanghai, China, in 2005 and 2008, respectively.
From 2008 to 2014, he was a Lecturer with Shanghai University of Engineering Science, Shanghai. He became an Associate Professor, in 2014, and has been a Professor with Shanghai University of Engineering Science, since 2022. His research interests include Lie algebras and representation theory and applied statistics.
VOLUME 13, 2025 107541
