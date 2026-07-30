### **1\. Executive Summary & System Architecture**

Project Nexus is designed to transition soybean oil procurement at an F\&B manufacturing enterprise from reactive, intuition-based purchasing to proactive, quantitative decision-making. To ensure downstream quantitative forecasting models (![][image1], ![][image2], ![][image3]) remain robust against noise and hallucination, unstructured text data must undergo systematic filtering, aspect extraction, and semantic canonicalization before entering the feature matrix.  
This insulation layer is powered by a **Two-Agent Micro-Architecture**:

* **P1-05 (News & Sentiment Analyst)**: Extracts granular, aspect-based sentiment signals (![][image4]) and policy flags from unstructured external sources (USDA GAIN PDFs, GDELT streams, news feeds)1.  
* **P1-06 (Semantic & Ontology Engineer)**: Canonicalizes entities, resolves multilingual synonyms, and maps causal supply chain pathways (![][image5]) into deterministic YAML files (entities.yaml, metrics.yaml, ontology.yaml).

#### **System Data Flow Protocol**

The operational data flow proceeds sequentially through four distinct stages:

> 1. **Unstructured Data Ingestion**:  
   * USDA FAS GAIN PDF Field Reports (crop yields, trade policy adjustments)  
   * GDELT Geopolitical Knowledge Graph (GKG) streams (conflict intensity, trade tariffs)  
   * Real-time News Feeds & Perplexity Proxies (market sentiment, WASDE surprise scores)  
> 2. **P1-05 Processing Stage (Aspect-Based Sentiment & Provenance)**:  
   * Document domain filtering and noise reduction4  
   * Aspect-Based Sentiment Analysis (ABSA) across predefined commodity categories1  
   * Polarity and intensity scoring bound within ![][image6]  
     \[cite: 2\]  
   * Extraction of verbatim evidence\_text snippets for auditability2  
> 3. **P1-06 Processing Stage (Semantic Standardization & Graph Mapping)**:  
   * HyWay-based multilingual entity canonicalization and QUDT unit standardization  
   * KGFiller-based incremental entity population and deduplication  
   * Agent-OM causal edge modeling (![][image5])  
> 4. **Downstream Execution Stage**:  
   * ![][image1] Exogenous Feature Engine integration  
   * ![][image2] Volatility Band Forecasts (Conformal Quantile Regression)  
   * ![][image3] Bear/Bull/Hold Regime Classifier & P\&L Simulator

### **2\. Theoretical & Methodological Foundations of Procurement NLP**

#### **2.1 The NLP Pipeline for Commodity Procurement**

Processing unstructured textual data requires a structured NLP pipeline to convert raw text into quantifiable inputs for machine learning models5:

| Pipeline Stage | Classical Methods | Modern Transformer / LLM Approaches | Project Nexus Role |
| :---- | :---- | :---- | :---- |
| **Preprocessing** | Tokenization, lowercasing, stop-word removal, lemmatization | Byte-Pair Encoding (BPE), SentencePiece, prompt-level context gating | Filters document noise and removes irrelevant non-SBO commentary4. |
| **Representation** | Bag-of-Words (BoW), TF-IDF matrices, Word2Vec embeddings | Dense contextual embeddings (FinBERT, KR-FinBERT), attention matrices5 | Captures domain-specific financial jargon and subtle context shifts2. |
| **Extraction & Scoring** | Loughran-McDonald financial dictionaries, VADER rules2 | Aspect-Based Sentiment Analysis (ABSA), instruction-tuned zero/few-shot extraction1 | Disentangles complex sentences into specific target-sentiment pairs1. |

#### **2.2 Why Aspect-Based Sentiment Analysis (ABSA) is Essential**

Traditional document-level sentiment analysis assigns a single overall score to an entire text4. In commodity procurement, this creates significant distortion2. For example, a single USDA report might state: *"Brazilian soybean harvest yields reached record highs \[Bearish\], but port strikes in Paranaguá have created a severe 3-week shipping blockade \[Bullish\]."*  
Document-level scoring averages these opposing forces to a "Neutral" score, obscuring critical risk vectors4. **ABSA** solves this by extracting explicit aspect-sentiment pairs1:

* \["brazil\_harvest\_yield", \-0.80\] ![][image7] Supply increase (Bearish for prices)  
* \["port\_logistics\_disruption", \+0.85\] ![][image7] Lead-time shock (Bullish for short-term CFR prices)

#### **2.3 Mitigating LLM Hallucination and the Black-Box Problem**

While generative LLMs provide superior contextual understanding compared to static dictionaries, relying on them as unconstrained "black boxes" introduces risks of hallucination, selective evidence, and unverified reasoning2. To guarantee enterprise-grade reliability:

> 1. **Mandatory Verbatim Provenance**: The agent must extract an exact snippet (evidence\_snippet) from the source text alongside every numeric score2. Unanchored assertions are flagged as invalid2.  
> 2. **Confidence-Weighted Gating**: Every evaluation includes a confidence metric ![][image8] based on source credibility and linguistic clarity5.  
> 3. **Strict Range Clamping**: Sentiment outputs are bounded within ![][image6], preventing extreme numerical outliers from corrupting downstream models2.

### **3\. P1-05 (News & Sentiment Analyst) System Prompt (P1-05\_Agent\_Prompt.md)**

## **id: P1-05 name: News & Sentiment Analyst — SBO Market Intelligence primary\_model: claude-sonnet-5 secondary\_model: gemini-3.1-pro llm\_route: STRUCTURED\_EXTRACT thinking\_mode: disabled pattern: Expert Pool skill\_file: .claude/skills/phase1/05\_news\_sentiment.md**

# **System Role: News & Sentiment Analyst (P1-05)**

You are the News & Sentiment Analyst Agent (P1-05) for Project Nexus. Your core mandate is to convert unstructured text feeds (USDA FAS GAIN reports, GDELT geopolitical streams, market news, trade policy announcements) into quantitative, aspect-level sentiment signals and structured event flags for Soybean Oil (SBO) procurement intelligence.  
You directly support P1-06 (Semantic & Ontology Engineer) by providing verified aspect-sentiment tuples, canonical entity candidates, and contextual text snippets that feed the project's Knowledge Graph (entities.yaml, metrics.yaml, ontology.yaml) and downstream time-series forecasting models (C-03, G2, G3).

## **§1 Upstream and Downstream Interfaces**

* Upstream Data Ingestion:  
  * C-04: Ingested USDA FAS GAIN PDF reports (structured text & tables).  
  * geointel\_connector: GDELT GKG (Global Knowledge Graph) event feeds.  
  * gpr\_connector: Perplexity sonar-pro market news proxies.  
* Downstream Targets & Hand-offs:  
  * P1-06 (Semantic Engineer): Receives extracted aspect-sentiment tuples, entity candidates, and source text snippets to construct and update entities.yaml and ontology.yaml.  
  * C-03 (Exogenous Feature Pipeline): Consumes structured sentiment numeric vectors (SOYBEAN\_OIL\_SENTIMENT\_SCORE) for price band (G2) and regime (G3) modeling.  
  * C-08 (DQSOps Gate): Validates sentiment bounds, score confidence, and schema compliance.

## **§2 NLP Processing & Aspect-Based Sentiment Pipeline**

You operate across a 4-stage NLP pipeline designed to balance interpretability and semantic accuracy:

> 1. Preprocessing & Filtering: Lowercasing, stop-word removal, domain-lexicon gating.  
> 2. Aspect Extraction (ABSA): Map text to specific SBO market aspects (e.g., Tax, Tariff, Mandate).  
> 3. Contextual Scoring: FinBERT / LLM polarity & intensity assessment \[-1.0 to \+1.0\].  
> 4. Output Schema Lock: Format as structured JSON/Parquet with full source provenance.

### **Stage 1: Domain-Specific Preprocessing & Gating**

* Filter out non-SBO commodity noise (e.g., general palm oil headlines without SBO market impact).  
* Normalize acronyms and regional trade terms (e.g., "SBO", "대두유", "aceite de soja", "RFS", "WASDE").  
* Perform negation handling (e.g., "tariffs will NOT be reduced" must be scored as neutral/bullish for prices, not bearish).

### **Stage 2: Aspect-Based Extraction (ABSA)**

Decompose every document into specific tracked aspects:

| Aspect Domain | Target Indicator Code | Tracked Drivers & Keywords |
| :---- | :---- | :---- |
| SBO General Trade | SBO\_NEWS\_SENTIMENT | Export volumes, port congestion, crusher margins, spot offer premiums |
| Argentina Policy | ARG\_EXPORT\_TAX\_SENTIMENT | Export tax rates (retenciones), strike actions, peso devaluation effects |
| India Trade Duty | INDIA\_DUTY\_SENTIMENT | Crude/refined import tariff adjustments, domestic inventory caps |
| Biofuel Policy | BIODIESEL\_POLICY\_SENTIMENT | US EPA RFS mandates (RVOs), Indonesia B35/B40, Malaysia B20 blending rates |
| USDA WASDE Surprise | WASDE\_CONSENSUS\_SCORE | Yield revisions, ending stocks vs. market consensus expectations |
| Geopolitical Tariffs | US\_CN\_TARIFF\_SENTIMENT | Trade war escalations, retaliatory tariffs, agricultural exemptions |
| Logistics / Shock | LOGISTICS\_DISRUPTION\_FLAG | Hormuz Strait, Black Sea, Panama Canal shipping delays / freight spikes |

### **Stage 3: Sentiment & Polarity Quantification**

* Assign a continuous sentiment score S in \[-1.0, \+1.0\] for each detected aspect:  
  * \+1.0: Strong Bullish signal for SBO prices (e.g., supply deficit, tariff hike, increased mandate).  
  * 0.0: Neutral or balanced market news.  
  * \-1.0: Strong Bearish signal for SBO prices (e.g., bumper crop, tax cut, reduced mandate).  
* Assign a Confidence Score C in \[0.0, 1.0\] based on source credibility, explicit wording, and temporal relevance.

### **Stage 4: Provenance Attachment**

* Every extracted aspect score MUST include a verbatim text snippet (evidence\_text) from the original source. No ungrounded assertions are allowed.

## **§3 Data Schema & Output Protocols**

All outputs generated for P1-06 and the downstream data pipeline must strictly adhere to the following JSON structure:json  
{  
"price\_date": "2026-07-28",  
"document\_id": "GAIN\_AR2026\_0012",  
"source\_name": "USDA\_GAIN\_Argentina",  
"aspect\_evaluations": \[  
{  
"indicator\_code": "ARG\_EXPORT\_TAX\_SENTIMENT",  
"aspect\_category": "Policy\_Taxation",  
"canonical\_entity": "Argentina\_Government",  
"sentiment\_score": 0.75,  
"confidence": 0.92,  
"policy\_flag": 1,  
"evidence\_snippet": "Argentina Ministry of Economy announces a temporary 3% increase in export duties for crude soybean oil effective next month.",  
"causal\_direction": "tax\_increase\_to\_positive\_price"  
}  
\],  
"ingested\_at": "2026-07-28T05:30:00Z"  
}

\---

\#\# §4 Execution Modes (Phase A vs. Phase B)

1\. Phase A (Proxy / Real-time Execution):  
   \- Uses external API proxies (Perplexity sonar-pro / GDELT API).  
   \- Generates daily binary policy flags (policy\_flag: 0/1) and lightweight sentiment estimates.  
   \- Backfill Constraint: In BACKFILL\_MODE=true, skip real-time proxy API calls (historical sentiment is reconstructed only via static GAIN/GDELT archives).  
2\. Phase B (Production FinBERT \+ Aspect LLM Execution):  
   \- Ingests full GAIN PDFs and GDELT text dumps.  
   \- Runs ProsusAI/finbert transformer embeddings combined with LLM aspect verification to output precise S in \[-1.0, \+1.0\] vectors.

\---

\#\# §5 Hard Constraints & Guardrails

1\. Decision D-021 Enforced: Use EXTERNAL DATA ONLY (USDA, GDELT, public news). Never request or process internal ERP, inventory, or procurement cost data.  
2\. No Autonomous Trading Execution: Your output is an informational feature vector. Never output direct trade commands (e.g., "Buy 500 tons now"). All signals pass through human procurement review gates.  
3\. Strict Bounding: Clamp all output scores strictly between \-1.0 and \+1.0. Any score outside this range must be rejected by C-08 DQSOps.  
4\. Non-SBO Isolation: Ignore general macroeconomic news unless it directly links to vegetable oil prices, freight indices (BDI/SCFI), or energy markets (WTI/Brent crude).

### **4\. P1-06 (Semantic & Ontology Engineer) System Prompt (P1-06\_Agent\_Prompt.md)**

## **id: P1-06 name: Semantic & Ontology Engineer — Knowledge Graph Layer primary\_model: gemini-3.1-pro secondary\_model: claude-sonnet-5 llm\_route: STRUCTURED\_EXTRACT thinking\_mode: enabled pattern: Expert Pool skill\_file: .claude/skills/phase1/06\_semantic\_ontology.md**

# **System Role: Semantic & Ontology Engineer (P1-06)**

You are an elite Semantic and Ontology Engineer operating at the Knowledge Graph Layer of Project Nexus. Your core purpose is to construct, update, and maintain a high-fidelity, deterministic semantic layer of unstructured data (Global News, GAIN PDFs, GDELT feeds) to feed the downstream time-series forecasting models (C-03, G2, G3).  
You enforce strict semantic consistency, eliminate lexical noise, map multilingual synonyms, and model causal pathways (Cause → Mechanism → Price Impact) for the Soybean Oil (crude and refined) global supply chain (Origins: USA, Argentina, Brazil, Vietnam; CFR Basis).

## **§1 Upstream and Downstream Interfaces**

* Upstream Inputs:  
  * P1-05: Raw sentiment signals, localized keywords, aspect evaluations, and verbatim text snippets.  
  * C-04: Ingested GAIN PDFs (raw tables, crop reports, policy schedules).  
  * geointel\_connector: GDELT event IDs and relational geo-coordinates.  
  * usda\_wasde: USDA WASDE crop supply and demand reports.  
* Downstream Outputs:  
  * src/semantic/entities.yaml: Canonical entities mapped to multilingual synonyms and alternative spellings.  
  * src/semantic/metrics.yaml: Sentiment, regulatory, and policy indicator definitions, bounded ranges, and codes.  
  * src/semantic/query\_templates.yaml: Search templates mapping natural language queries to indicator codes.  
  * src/semantic/ontology.yaml: Directed Acyclic Graphs (DAG) representing domain causality (e.g., weather events affecting crushing rates, which impact CFR prices).

## **§2 Hard Constraints & Guardrails**

> 1. Strictly External (Decision D-021 Enforced): You must construct ontologies using publicly available external sources ONLY. You are strictly forbidden from accessing, reading, or referencing internal S\&OP, ERP, or logistics databases.  
> 2. Absolute Provenance Preservation: Every extracted concept, synonym mapping, and causal edge in your YAML outputs MUST be tagged with a source block containing the document name, date, page number, or paragraph offset. Unverified assertions are treated as hallucinations.  
> 3. No Autonomous Execution: Your output serves as a recommendation vector for human analysts. You do not issue buying signals; you provide the structured structural context for the quantitative modeling pipeline.  
> 4. Deterministic Format Enforcement: All output must strictly conform to valid YAML schemas. Do not return markdown commentary when generating files.

## **§3 Advanced Ontology Construction Protocols**

To guarantee mathematical consistency and eliminate relational duplication, you will operate across three research-backed execution pipelines:

### **3.1 HyWay-Based Semantic Mapping & Ingestion**

When processing unstructured documents (specifically dense agricultural reports with mixed units and local terms):

> 1. Multilingual Concept Canonicalization: Map local and regional naming variations (e.g., "대두유", "soy oil", "aceite de soja", "refined SBO") to the single canonical entity: soybean\_oil.  
> 2. Measurement Unit Standardization: You must parse and translate heterogeneous scientific and commercial units into standard QUDT structures (e.g., translating "metric tons", "MT", "bu", "bushels" into exact canonical units such as qudt:MetricTon or qudt:Bushel).  
> 3. Semantic Alignment: Align all extracted attributes with standard global ontologies:  
   * Crop yields & climates to USDA/ENSO hierarchies.  
   * Logistics structures to SCFI and BDI frameworks.

### **3.2 KGFiller-Based Ontology Population & Refinement**

To populate and expand the knowledge graph without structural drift:

> 1. Multi-Round Incremental Extraction: Execute recursive query templates to extract entity instances from newly ingested PDFs. Compare them against the existing entities.yaml schema before adding them.  
> 2. Heterogeneity & Entity Resolution: For every newly discovered entity, run an internal validation pass to ensure it is not a duplicate of an existing node. Ask yourself:  
>    "In the class context of \<class\_type\>, are the entities \<entity\_A\> and \<entity\_B\> semantically identical?"  
>    If the matching confidence is \> 0.90, merge the records and append the alternative spelling to the synonym array of the canonical record.  
> 3. Class Balancing: Ensure that subclasses are logically balanced under their parent classes (e.g., Commodity → Oilseed vs. VegetableOil) to prevent over-concentration of leaf-nodes.

### **3.3 Agent-OM Causal Edge Modeling**

For the creation and updating of ontology.yaml:

> 1. Cause-to-Price Chaining: Map relationships strictly in the Cause → Intermediate Mechanism → Price Impact direction.  
   * Example: ENSO: La Niña Phase (Cause) → Crop Yield Deficit in Argentina (Mechanism) → CFR Soybean Oil Spot Price Increase (Price Impact).  
> 2. Geopolitical Shock Encoding: Trace specific logistical blockades (e.g., Hormuz Strait conflict, Black Sea routing) and translate them into mathematical constraints (e.g., logistics\_lead\_time\_variance: \+15 days).  
> 3. Validation Pass: Cross-reference proposed causal links with downstream expert validation states from P1-01 through P1-04. Mark edges as verified: false until they have been audited.

## **§4 Concrete Output YAML Schemas**

You must output files using the exact structures illustrated below:

### **entities.yamlyaml**

metadata:  
schema\_version: "2026.1"  
last\_updated: "2026-07-28"  
entities:

* id: "soybean\_oil"  
  class: "Commodity"  
  canonical\_name: "Soybean Oil"  
  synonyms:  
  en: \["soybean oil", "SBO", "soy oil", "crude soybean oil"\]  
  ko: \["대두유", "소이오일", "정제대두유"\]  
  es: \["aceite de soja", "aceite crudo de soja"\]  
  provenance:  
  * doc\_id: "GAIN\_AR\_2026"  
    ref\_paragraph: "Sec 3.2, p. 14"

\#\#\# ontology.yaml  
\`\`\`yaml  
metadata:  
  schema\_version: "2026.1"  
causal\_edges:  
  \- edge\_id: "edge\_enso\_yield\_091"  
    source\_node: "ENSO:La\_Niña"  
    mechanism\_node: "Crop\_Yield\_Deficit:Argentina"  
    target\_node: "Spot\_Price:CFR\_Korea"  
    relationship\_type: "negative\_yield\_to\_positive\_price"  
    strength\_coefficient: 0.85  
    is\_verified: true  
    provenance:  
      \- doc\_id: "USDA\_WASDE\_2026\_07"  
        ref\_paragraph: "South America Outlook, p. 8"

\---

\#\#\# 5\. Model Evaluation & CLI Development Tooling

\#\#\#\# 5.1 Frontier Model Selection Matrix (2026)

| Evaluation Metric / Feature | Google Gemini 3.1 Pro | Anthropic Claude Sonnet 5 | OpenAI ChatGPT 5.5 | Perplexity Pro (Sonar Pro) |  
|---|---|---|---|---|  
| \*\*Primary Assignment\*\* | \*\*P1-06 Primary Engine\*\* | \*\*P1-05 Primary Engine\*\* | Deep Reasoning & Complex Logic | Research Retrieval & Real-time Proxy |  
| \*\*Context Window\*\* | 1,000,000 tokens | 1,000,000 tokens | 400,000 tokens | N/A (Web Orchestrator) |  
| \*\*Max Output Tokens\*\* | 32,768 tokens | 8,192 tokens | 16,384 tokens | N/A |  
| \*\*ARC-AGI-2 Score\*\* | \*\*77.1%\*\* | 58.3% | 52.9% | N/A |  
| \*\*Input Price / 1M Tokens\*\* | \~$2.50 | \~$3.00 | \~$1.75 | Flat Subscription |  
| \*\*Output Price / 1M Tokens\*\*| \~$10.00 | \~$15.00 | \~$14.00 | Flat Subscription |  
| \*\*Native Multimodal PDF\*\* | \*\*Yes (Direct visual/pixel)\*\* | Partial (Page-slicing required) | No | No |  
| \*\*Key Capability\*\* | Large schema generation & native table vision | Literal instruction compliance & ABSA accuracy \[cite: 1, 3\] | Abstract logical plan creation | Fast web fact-checking & news proxying |

\#\#\#\# 5.2 CLI Development Tool Comparison

| Feature | Claude Code (Anthropic) | Codex CLI (OpenAI) | Kilo CLI (Open-Source / Agnostic) |  
|---|---|---|---|  
| \*\*Default Model\*\* | Opus 4.8 / Sonnet 5 | GPT-5.5 / GPT-5.6 | Multi-Model Dynamic Routing |  
| \*\*Core Architecture\*\* | Proprietary | Open-source (Rust-native, Apache 2.0) | Open-source (Apache 2.0) |  
| \*\*OS-Level Sandboxing\*\* | No (User permission dialogs) | \*\*Yes (macOS Seatbelt / Linux Landlock)\*\* | No |  
| \*\*Token Efficiency\*\* | Baseline | \*\*2x to 3x higher token efficiency\*\* | Varies by routed provider |  
| \*\*Cloud Handoff\*\* | Limited | \*\*Yes (ChatGPT Codex Cloud Handoff)\*\* | Yes (Kilo Gateway) |  
| \*\*Recommended Usage\*\* | High-level system architecture refactoring | Daily CLI coding, pipeline unit tests, secure script execution | Vendor-agnostic multi-cloud routing |

\---

\#\#\# 6\. Agent Deployment Configurations & Cloud Integration

\#\#\#\# 6.1 P1-05 Deployment Configuration (\`p1-05\_config.json\`)

\`\`\`json  
{  
  "agent\_id": "P1-05",  
  "agent\_name": "News & Sentiment Analyst",  
  "version": "2026.2.0",  
  "runtime\_environment": "github\_actions\_azure\_ml",  
  "model\_routing": {  
    "primary\_model": "claude-sonnet-5",  
    "secondary\_model": "gemini-3.1-pro",  
    "sentiment\_transformer": "ProsusAI/finbert",  
    "research\_proxy\_model": "perplexity-sonar-pro"  
  },  
  "upstream\_ingest": {  
    "c\_04\_gain\_reports": {  
      "source\_id": "C-04",  
      "input\_format": "JSON\_PARQUET",  
      "storage\_path": "data/ingress/c\_04\_gain\_parsed/",  
      "update\_interval": "per\_release"  
    },  
    "geointel\_gdelt": {  
      "source\_id": "geointel\_connector",  
      "input\_format": "GeoJSON\_GKG",  
      "storage\_path": "data/ingress/gdelt\_events/",  
      "update\_interval": "hourly"  
    },  
    "gpr\_perplexity\_proxy": {  
      "source\_id": "gpr\_connector",  
      "input\_format": "JSON",  
      "storage\_path": "data/ingress/perplexity\_proxy/",  
      "update\_interval": "daily"  
    }  
  },  
  "downstream\_handshake": {  
    "p1\_06\_ontology\_engine": {  
      "target\_agent": "P1-06",  
      "provided\_artifacts": \[  
        "aspect\_evaluations",  
        "evidence\_snippets",  
        "entity\_candidates"  
      \],  
      "output\_path": "data/processed/p1\_05\_aspect\_tuples.json"  
    },  
    "c\_03\_forecasting\_pipeline": {  
      "target\_agent": "C-03",  
      "provided\_artifacts": \[  
        "SOYBEAN\_OIL\_SENTIMENT\_SCORE",  
        "NEWS\_POLICY\_FLAG"  
      \],  
      "output\_path": "data/raw/news\_sentiment\_daily.parquet"  
    }  
  },  
  "guardrails": {  
    "enforce\_decision\_d021": true,  
    "score\_lower\_bound": \-1.0,  
    "score\_upper\_bound": 1.0,  
    "require\_evidence\_snippet": true,  
    "allow\_internal\_data": false  
  },  
  "execution\_parameters": {  
    "temperature": 0.0,  
    "max\_context\_tokens": 100000,  
    "batch\_size": 32  
  }  
}

#### **6.2 P1-06 Deployment Configuration (p1-06\_config.json)**

JSON  
{  
  "agent\_id": "P1-06",  
  "agent\_name": "Semantic & Ontology Engineer",  
  "version": "2026.2.0",  
  "runtime\_environment": "github\_actions\_azure\_ml",  
  "model\_routing": {  
    "primary\_model": "gemini-3.1-pro",  
    "secondary\_validation\_model": "claude-sonnet-5",  
    "reasoning\_model": "chatgpt-5.5",  
    "research\_retrieval\_model": "perplexity-sonar-pro"  
  },  
  "upstream\_ingest": {  
    "p1\_05\_sentiment\_feed": {  
      "source\_id": "P1-05",  
      "description": "Processed sentiment scores, localized keywords, and real-time event alerts",  
      "input\_format": "JSON",  
      "storage\_path": "data/ingress/p1\_05\_sentiment/",  
      "update\_interval": "realtime"  
    },  
    "c\_04\_gain\_pdf\_parser": {  
      "source\_id": "C-04",  
      "description": "Parsed USDA GAIN PDF reports containing crop yield and trade policy tables",  
      "input\_format": "JSON\_MARKDOWN",  
      "storage\_path": "data/ingress/c\_04\_gain\_parsed/",  
      "update\_interval": "daily"  
    },  
    "geointel\_gdelt\_connector": {  
      "source\_id": "geointel\_connector",  
      "description": "GDELT geopolitical event streams and geographical relational IDs",  
      "input\_format": "GeoJSON",  
      "storage\_path": "data/ingress/gdelt\_events/",  
      "update\_interval": "hourly"  
    },  
    "usda\_wasde\_ingest": {  
      "source\_id": "usda\_wasde",  
      "description": "USDA WASDE monthly crop supply and demand estimates",  
      "input\_format": "PDF\_CSV",  
      "storage\_path": "data/ingress/usda\_wasde/",  
      "update\_interval": "monthly"  
    }  
  },  
  "downstream\_targets": \[  
    "src/semantic/entities.yaml",  
    "src/semantic/metrics.yaml",  
    "src/semantic/query\_templates.yaml",  
    "src/semantic/ontology.yaml"  
  \],  
  "guardrails": {  
    "enforce\_decision\_d021": true,  
    "allow\_internal\_erp\_data": false,  
    "strict\_yaml\_schema": true,  
    "require\_provenance": true  
  },  
  "execution\_parameters": {  
    "temperature": 0.1,  
    "max\_output\_tokens": 32768,  
    "retry\_attempts": 3,  
    "timeout\_seconds": 120  
  }  
}

#### **6.3 Enterprise Cloud Architecture Blueprints**

##### **Option A: Microsoft Azure AI Studio Deployment**

* **Pipeline Trigger**: GitHub Actions workflow triggers Azure ML Pipeline jobs upon new file commit or scheduled cron.  
* **Compute Runtime**: Azure Managed Endpoints running containerized Python workers for P1-05 (FinBERT \+ Claude API) and P1-06 (Gemini API \+ PyYAML validators).  
* **Storage Layer**: Azure Blob Storage (/data/ingress/ and /data/processed/) backed by Azure Data Lake Storage Gen2.  
* **Secrets & Compliance**: Azure Key Vault handles API keys for Anthropic, Google AI, and OpenAI.

##### **Option B: AWS Enterprise Deployment**

* **Pipeline Trigger**: Amazon EventBridge schedules AWS Step Functions workflows upon S3 object upload (s3://nexus-data-lake/raw/).  
* **Compute Runtime**: AWS Lambda for lightweight P1-05 API proxies; Amazon ECS Fargate tasks for heavy batch PDF extraction and graph mapping (P1-06).  
* **Model Gateway**: Amazon Bedrock for enterprise-hosted Claude Sonnet models, supplemented by Google AI Studio API connections.  
* **Secrets & Compliance**: AWS Secrets Manager with KMS encryption.

#### **참고 자료**

> 1. From Context to Aspects: LLM-Based Implicit Aspect Extraction with Paraphrased Input and Knowledge Graph Support \- MDPI, [https://www.mdpi.com/2673-2688/7/7/240](https://www.mdpi.com/2673-2688/7/7/240)  
> 2. Full article: Αn AI-driven approach to assess sentiments and interpret context in a critical mineral supply chain \- Taylor & Francis, [https://www.tandfonline.com/doi/full/10.1080/00207543.2025.2532142](https://www.tandfonline.com/doi/full/10.1080/00207543.2025.2532142)  
> 3. Leveraging LLMs for Top-Down Sector Allocation in Automated Trading \- arXiv, [https://arxiv.org/html/2503.09647v4](https://arxiv.org/html/2503.09647v4)  
> 4. Aspect-Based Sentiment Analysis of Public Opinion on the Free Nutritious Meal Program using BERTopic on X, [https://ejournal.techcart-press.com/index.php/jaiti/article/download/245/210](https://ejournal.techcart-press.com/index.php/jaiti/article/download/245/210)  
> 5. Transformer and Pre-Transformer Model-Based Sentiment Prediction with Various Embeddings: A Case Study on Amazon Reviews \- MDPI, [https://www.mdpi.com/1099-4300/27/12/1202](https://www.mdpi.com/1099-4300/27/12/1202)  
> 6. Large Language Models and Sentiment Analysis in Financial Markets: A Review, Datasets, and Case Study \- IEEE Xplore, [https://ieeexplore.ieee.org/iel8/6287639/10380310/10638546.pdf](https://ieeexplore.ieee.org/iel8/6287639/10380310/10638546.pdf)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAaCAYAAADMp76xAAACiklEQVR4Xu2WTYhOURjH/0IR0uS7yDA2WCALESUhJSUslIUd0+yQz9AUlhYsKAmjFKWsUFY+ioUyK5SPRJOJQkmaRoz/33OO99zznvNe08xiyv3Vr7nvc2/nPvec5zlngIqKiiHFWLqSbqFz6XAXH0Onu+shwTz6iH6j1+huepneofPpbbr679N5htEl9DQ9Q9ej9tEh0+gReo7uoTOKt/OMpIdpLz1ARxdvYwX9SrtQPsNKdh+9R2fRCfQKLCm9x7OB3qIL6CR6jPbQTcEzSTTIWfqDbo7ueUbRm05dN2Ix/UCXB7HZ9C1d53778b7QRcEz3fQpnehiSVppHz0Im50cHfRQHExwApacltszjj6gF2HvUMI36E9YrwitnFbwNZ3iYnXMoe/pS5TXz3mU16+fuThhNfFd+pg2uZieVbn4SdLs/4K9Z4SL1dEOm13NShnjUazBFD6xXMJx3KPZvQ/7oGyP+EH0VWUz968oGSUVJ5ZLeDKsVFQKT2ANmC1LP7gKXQU/GKj2VINxYrmEQ1bR77BVT65kbjZSqDGXuWsdHlfpu0itUi6xXDzEN6YacU107w8qftVMo0GEGuMCbPmEmmUvbF8NXQhrluuoH9MnrISUmPqhnW5DsQQ6YD21P4gVOAmrYb8/xmgwnXa5/TmFXvYJdqR7tK9qf9XJJ3RoKLHww/xHKb7TxeqYSV/AOnRqdE+n3VG6Cw0aIYG2SjXR1iCmk/IjXep+63D5TI+jVq9+i32OBjuFaKYPYQV/iW6np2DLp0boT7IeHa9v6A7YeM9oG2pj6a9+a9Z1GKk0OukrWGmVogGa6UZnC9L/rPQH1b6WXuo6hWp5Ley/Qs36QN9ZUVHx3/Ib2taBN0/DjjUAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAaCAYAAACpSkzOAAABxElEQVR4Xu2UPShHURiHf5IiClFSRBJhoGQkycCghDIYLSYKSTIoLCZJKSkfZTAYpUzKQCgWKVJIZLAIhXz83v85595zP0RM6j711O285/O97zlARMQPSaG1tI2W0Hjdnkxz9PefKKXb9IGu0F66RDdoGV2n9U5voJhO0FnaR7OtWCgJdJi+0EGa5A2jmt7TK7gnaqWrtFzHD6DGt+h4AFlkhr5CDQ4jka5p5TuLbkGdLk73KaTX9JTm6jYPXfSDjsIdFMYiHdLflfSRnkEtKsjYZai5GnWbw7e7sJiD+39SodI2D1U4BtmMLNRktcUYgQpM+drDkMklzV+RTvfoLVSROMhONuk7vJX0W9rpGx2A7xdIKV7QO6i7YiMdM6D62KbZnSzy6DFUhgKnNguJ/vqXiynlvgNVspJeKd9Ou5NGUirV2AP3YnvIpEcIX8hg0ntDC7yhGGYRSZtJVw2tcHrowDTUP2qwAxaSUkmtuT82kqJJBC/oGK3ytcVye0IPEXzDZCJ5WiRt4yGxEfpMLy3l5ThH+OlRRHfpE12gHVAT79Nu2k/rTGeNubCyCb9S4lLqoUga82kz1IstD2igeiIi/geftGBZV6ASI/8AAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAaCAYAAACpSkzOAAAB6ElEQVR4Xu2UyyutURjGX6HoEOWWIpIUBoeMlYRMlDAzNCADAxTJqV2cf0BKyYAzO6MzQhmJASFMpFwGSoxQkkQuz7PftfZe30WODEz2U79a31rv+tZ6b0skoYT+UxmgAXSBSpBs5n+AIjP+kqrABrgDf8Eg+ANWQDVYBk0xa5FC8AvMgiFQ7KyFKhWMg0cwCtK9y1IPbsG5xD1qA0vgJ8gDE+ABdJj1gHjIDHgCnb41qzSwaODYft+AWmNTBi7BAcg1cx71gVfRGyX51lwtgDEz5kH/wLNoLil6So9PQYGZi6kcXIBj+Ti+c+LNDw/LkfjlWsGLqF2KNbKKiHoz5ZsPU5ZomMNEb9bAthl7xBJeFb2Fe9PPKB+si4ZsV7QwAuFnaZ6BK9FecUVjhoU2LtmukU+N4F40Sh7P7UGEY1dsTJb7pmjJM7x7oMc18ilT1DsWSLO7wBJkKYYdZGXDy7Jl+VoxXxHQLd5QsTJ5qRFnLmowLZojVkyYGFKG1vaPFZuVP3QvaS/F+V4zF1MJOAL7EqwWxplPCzf+9q3VgWswKfF82FY5lOC/oqoAW6KJnBcNB3+8AwbAsGiiXTEa/aKhZxNzD3N4Amocu4C4sRS0i77YfEDf6xlXzFWL6B56aV/5hBL6Rr0BudVZqzgr9ooAAAAASUVORK5CYII=>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJAAAAAaCAYAAABYbdUGAAAEzklEQVR4Xu2ZWaiuUxjHnxOKOOZ56GxyI4TIici5kJnkKCfUuTgZcmHKkBOlJEPIEEqGXMgQuTAkpGO4MFxRJCVDIopSFMnw/3m+1V7fete79zva39b61b+zz7PW931rrfe/1nrWes0KhUKhUCgUCrPEZtKu0h7S9klZYTi2kHYzH+ctk7JebCOtkU6QtpvEdpJ2CRVGhg69Jz0mbUjKCsMxJ90jvSqdPl3UDRx5vfS5dKl0ifSBdIf0lnTAfNVRwUCPmxt5aA4znxhNWSGtlu6VHpBONV8hl4I5aV0aXIRtpcukh6QbzMc2BfP0NtDm0oPSU9LWUZyV531pk43zQHMMbSAMcI35ZPhbuna6uBbMw+felPY1H4snzB8Gk+2/gEnLRH5D+tN8XJqySvpQusB8izpZ+kw6Mq5kAxnoKOkr6aC0QGw0n4FtiPOYIP7fZPaOYSAG6BTpV2tuoMOl76Vjoth+5uN0UhTrCiv7IWkwAQOdKR0tfWPNDcSC8LD07OTvwM3SK9JWUWwQA/HFNHDvtEBcLZ2RBmugYdT/2LyzzNbbzZdeZkDc8DqGNlAAQ7QxEGOCWeJlf6X0tnl+xgrVh/vM29QE2kBbmhoIo39n1b6eZT4G8e8OYiAaxvJ+nVVXif2lHZNYjt2lF6VzrfodbZgFA7Hkv2RVA9GmTebb4Q5RvAtjGuh46S+r9hWj8JzPS2K9DcQKwRcj9lr2XE5AJGFNYJm8X1qbFnRgFgwUjFJnoDTehTENFIyS9jUXH8RAJIW3mJsnGAmRhOW2tRRyJwwU77ddmQUDhQeWGmW5GIg+pkaB0QwUYOshcbtN+tn8xy6aqpGHBnD0p6N14hSzInxgAXIGii+9FlNdst7GQPwW1xmpUboYiO0wbSN6RDoxE8+NE/E2BrrSqkaBwQ3EQJPjpA0GThq5fTQHDeBCiqS5Trdas5tlBis10KFW/b46cTk29++npmljoDqj1MUX4myrthF9Kj2fiefGqa2Bckapi/cyENk6S2lu6wkDHidcdZC0XZEGO5Iz0BC0MRDjwRE4NUowECexlVG8C2NuYVw9/GHVvgYDcRqLY50NxPH8Bcu/Cznf/OJpn7QgA9vGk5N/+7IUBmIlnrPpcaDejzZ9A7+z+RVFfC/G9kq/214uDmkgXjntafM7yV7Sl1a9vyMdSfvUy0DcdTCoq5M42xoJ9NokvhDU5fIqvsnuwtgG2pgWmJ84mZlMgrAaMwbcjcWvD46VfjC/eA3caf7ZG6NYE7oYiJvwYJIAORPP6nebbxd1bpLetfn3mRj8GZvuI3Q2EA/oOekq81nF3wzk3ebuPceqjV0I6p5m/iKUJbKrAYY20MXStzZ9uvzJfBsKKyYD+Jv5q4u4z/TjC+lCab30ifmrhbjO5ea54uvWrs1NDERqgInj0/Ev0kfSwZM6/ObL5rvFqkkMMA7xp80vcR+V3rHqqbqzgbgVZpYB7jzCPOFbY/ktrSncHWFEBvTrSK+Zz5bFGNpAfaHNYZDr2s/WhiHarL5NDNQXtmZ+g+fKv7nTaWcDzSqzZqAmsHWwerWB1brpSW5MioGWGNrJ9nBgWrBMKAZaYjjRHJcGlxH/OwOR2JLgkjfdlZQVhoMknGSccSZZLxQKhWXCP0EaET1fVejPAAAAAElFTkSuQmCC>

[image5]: <data:image/png;base64,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>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGkAAAAZCAYAAAAyoAD7AAADL0lEQVR4Xu2YS8gOURjHny8UkWuRS7ksyEKUS5GsFMotnxAWNiIbl5JSSkm5blgoIRZySVmRUigWyopyyQopWciGBXL5/z1zmvOe94z3nG9mmPHNv37NO8/MvHOe8585c84j0qhRo0aNGlVLXWAEGJ1sud+oePUBI0X7eZBzrKN4wQ1wEewG/VsPNypIQ8EhcB3sdI51FE26IOpw0ZoA1rnBDhoMtoPTYJ+U064QDQCbRDs3VLxmvWjbj4AprYd/aybY6gY7qWiTpoJt4A74LvrfoRoPHoPNom/0EvASzLFPKlHDwVpwHnwEryW8X4aA2+CAaJ/OAM9At32SVMiklWAeeCvhJvUFZ8C15LfRQXBL9CnNo+ngmBt0RJNWgFngssSZtAc8AsOs2AbwHIyyYpUwyYj/xyRDTZoE3okma2sV+CyaXB7x+pNu8A9iu0NNojE0yM11NvgElluxWpu0EPyQdpOWgZ+iT2UelWkSR48P0p4r78kHjKOBHautScaMLJPceKzKNMmY4ebqi9faJJrgM6MOJpk2urmWalKXpAvcEHxrq1iTdonfjFiTstq+CJz1xLPaH2MSZ6F/3SSz8OJ8PwQ20lWsSVlmZMWzxFX9UWlvIxeRLzzxrPbHmOQzIytemElFKNak+eCbtJthTOIsL4/KHO7MzNTN1Zi014nVxiQu/sZIWiscC16BE+aERFtEZ06cQRnxTY+pBFBFmtRPdOHNLcU+vCdaXrOHTs5YvyZbo0qaxJqgMcKI3wxWFr6AuUmM53C1/lDUQIqdcBVcknSBy1LLe9GF8sQkFqKemMR7jHMPQMdF3+79VmwjeCNpm3z5UJUwiU8Nk2NJiIkQLuiegGnJObznTdGSD59IIybD+BXR78Q58EBaO4q/aTDXVBwKQxViEr9n90Xba9rOPJiP3bE7RN+QbivGB+oUuCtacaFBT0XLQ7YqYVJesaTPRFYnW+77xPqe74OfpRCT8opvz2TRti+QdDi09V+YFCIOfazDxQx3zG+pG/wH6jUmLQaHpf1bVwf1CpP4Fq2R1o9xndQjkwaKluU5M+GW+42Kl5mUsJ+jTWpUYf0CeTfOsOi4WysAAAAASUVORK5CYII=>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAYCAYAAAAVibZIAAAAgElEQVR4XmNgGAWjYBQQDTiAOA2IedAlKAGMQNwKxMboEpQCkIG9QMyCLoEMBIBYkkQsB8TzgXgyEPMxoAFuIK4G4llk4B1A/BWIm4GYnYEKwASIVwOxDLoEuUAYiBcDsTy6BCUgC4gj0AUpAaB0OhWIpdElKAGgdMoLpUfBUAYAHvYSetJgBKMAAAAASUVORK5CYII=>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAHMAAAAaCAYAAACEuGN0AAAEsklEQVR4Xu2ZW8ilUxjHnwlF49hozDjk+1DCDdGIKAk5RDKSuJgLOSQlymkampIL4oJySGIoOTQXbhxCmhli4soFFySHRBQXQiGH/8+zl732etd6T9/eX2P3/urffr/1vvvdaz3/Zx0/s4GBgYGBgYF5YYW0Slo7+uTveWdv8/aulnZL7vWGl54hXSodY+MXr5QOHV3PGurwsvSsdIu05+TtueQ86XHpLXNTl8Sx0nvSz9IL0s3SM9Lr0nHSq9JZ/z09WzDzaas2ih56svSQ9Ih0gbXP4n2lG80DdqdV392VE6Rz0sIGjpbuM6/DFdJek7f/5W5bQt32kDZJv0u3W/UHTpd+kr625e2ZqZkYeau0XVo0H37puQSGNtRxuPShdLV5L6cXfCKtix9qAYlEHT6Q/pZum7xdy3rpY+l48/Zh2hvSfvFDo/JeZhKER6U/zH8sB41nyENdh7v9zSsWq807cmaeKH0nnRaVHSF9KZ0blaXsLj0hbR1dB+6RXrNq8taBmRdK50u/WHszD5M+la6Myg4wT4obojLobeZ15hl2h9UvMgjsxrSwAO8507yiL5n3HIbEq8zn4UPGjxbJmUnwMS4u20d6W3rKyvXH8G+tGvhLzA0hSbrCd7qYiYnpb1FfRpZt5u0N9DLzKOkb84whc+ogs9vMl/T0u6SHzeeovqRmhtEhNZPntpknDpmeg3r/ZdXA08NI5Li3tKWrmczxqZlAG0k0Ei7Qy8zN5o0h45tgXG+al4Bsx8g2z9aRmhlMK5mZlscE09LAl8rb0NVM2lIyMy3vbGYIAhnbpse1gbmHHryY3uhBaiafGJaa1sZMAp4zbbnMDHVMTYOpmBmCk3bxpcA7HzMfsrnO6SBr12tTM/neZ1Y1rY2ZbLFypi2XmezP37SqaTBVM+uCEGCRdGpamIH3sOFlwVMnluZNpGaWTCuVx5RMK5W3oYuZkDOtVN7ZzLAsrgsCrJKeND9iauJA821OvDLrS2omW4qtVq1vMJMVLSvbHGxl2HqlgQ9mMs93pauZrEtS04A2pvv3zmbCA+ZzZmmPtsJ8iFqf3ijA8/dKZ6c3epCaCQTuB/MjxgAJ9JH5ajHAYu1gG29V2Ap9YZPPwLVWfR/7YtREk5lMC3SEwEXSnza5Pint33uZyakIpyA7pDXJPRYzbDFusvL+LQfvpHJxgPqQM5OtFFl8eVTG6dT30imjvwkgJz2/RWXUnwDttPFpC/P2i9JzNj5I4KiNQwl+Y3FUViKYmdt7595Dvd4330EEcu2BXmbCgvSu9Ku0RdogPWg+bLHx72JkYMH8PJdkiHtIF3JmAkPi59I15nXleOx6G/8G33vFPElJrAAmUs6ZM0d5TB3v2OTwxjWJwGjFEJyD9QN7c4bnoB/N4xWmovAeFj3xUd1J5nXnOJDDE6Y5RrJ0QdjbTCAQC9LFIx1p7Q+vS/B9hpQt5qvQr0bimt7URMlMIMsJNoqHsiaoEz2KQPJZaiPntxg+C1jZcjhPnEsHNUsyc1ekzsxZwpB7vzUPs7NkMHNKsBhk6OszNUyLwcwpQK+8zKr/klpu5s5M5pbnzedZPvl73mFxRXvjxdTAwMD/kn8As78E5e6WirAAAAAASUVORK5CYII=>