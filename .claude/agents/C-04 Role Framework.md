### **1\. Executive Summary & Infrastructure Synergy**

In **Project Nexus**, the accuracy of downstream forecasting models (![][image1], ![][image2], ![][image3]) and upstream intelligence agents (**P1-05 News & Sentiment Analyst** and **P1-06 Semantic & Ontology Engineer**) depends heavily on the quality of unstructured data ingestion1. Unstructured enterprise dark data—such as multi-column USDA FAS GAIN PDF reports, GATS trade Excel workbooks, WASDE crop supplements, and customs declarations—suffers from severe formatting challenges, including multi-level table merged cells, column scrambling, and unit inconsistencies2.  
The **C-04 (Document Intelligence & ML Infrastructure Engineer)** agent provides the foundational parsing, normalization, and MLOps backbone required to overcome these challenges. It serves a dual mandate:

> 1. **Mission A — Document Intelligence & Ingestion**: Implements layout-aware parsing, Vision-Language Model (VLM) fallback routines, and structural block extraction to convert multi-format unstructured documents (PDF, XLSX, DOCX) into clean, schema-compliant Parquet/JSON artifacts3.  
> 2. **Mission B — Data & MLOps Infrastructure**: Maintains CI/CD GitHub Actions workflows, Azure ML Command environments, Snowflake query optimization pipelines, and strict data quality gates in src/pipeline/.

#### **Operational Inter-Agent Handshake**

The operational data pipeline flows through a coordinated three-agent architecture:

* **Raw Unstructured Ingestion (C-04 Ingestion Layer)**: Raw PDF/XLSX/DOCX documents are ingested from USDA, GATS, and Korean Customs sources. C-04 applies layout-aware parsing, extracts complex tables, flattens multi-level headers, normalizes units to metric tons (MT) and USD/MT, and splits text into semantic blocks4.  
* **Downstream Delivery to P1-05 (News & Sentiment Analyst)**: C-04 provides P1-05 with layout-preserved Markdown text chunks, exact page/paragraph provenance tags, and extracted policy tables. P1-05 performs Aspect-Based Sentiment Analysis (ABSA) on these clean chunks to derive aspect scores (![][image4])6.  
* **Downstream Delivery to P1-06 (Semantic & Ontology Engineer)**: C-04 supplies P1-06 with normalized commodity attributes, standardized QUDT measurement units (qudt:MetricTon), validated HS Code tables (1507xx), and raw entity candidates. P1-06 ingests these structured inputs to populate entities.yaml, metrics.yaml, and ontology.yaml.  
* **Feature Pipeline Hand-off (C-03 Exogenous Feature Matrix)**: Cleaned numerical vectors and structured tables from C-04 are stored in data/raw/\*.parquet and passed through the C-08 DQSOps validation gate before entering the ![][image1] feature matrix for ![][image2] volatility forecasting and ![][image3] regime classification.

### **2\. State-of-the-Art Document Intelligence Architecture (2024–2026)**

#### **2.1 Benchmark Evaluation of PDF & Document Ingestion Frameworks**

Recent advancements in Document Intelligence have shifted the paradigm from basic Optical Character Recognition (OCR) and text scraping to **layout-aware Vision-Language Models (VLMs)** and deep structural parsers3. The table below compares the leading enterprise document parsing engines evaluated for Project Nexus:

| Engine / Framework | Core Architecture | Table Cell Accuracy | Processing Speed | Strengths | Weaknesses | Project Nexus Fit |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **Docling (IBM DS4SD)** | RT-DETRv2 Layout \+ TableFormer9 | **97.9%** \[cite: 9\] | Moderate (\~1.2 s/page)9 | Exceptional table structure preservation, Markdown/JSON export, open-source5 | Requires GPU for high-throughput batching5 | **Primary PDF Parser Engine** \[cite: 5\] |
| **MinerU** | Layout Detection \+ CJK Layout Transformer5 | High | Moderate | Best-in-class support for CJK (Korean/Chinese) layout and fonts5 | Higher memory footprint5 | **Primary Parser for Korean Customs Data** \[cite: 5\] |
| **LlamaParse (LlamaIndex)** | Llama-3-Vision Cloud Parsing4 | Variable (interleaves multi-column text)4 | **Fast (\~6 s total file)** \[cite: 9\] | Native LlamaIndex RAG integration, embedded image extraction1 | Cloud API costs, struggles with borderless merged tables4 | Secondary Fallbacks for complex research papers1 |
| **LandingAI DPT** | Document Pre-trained Transformer2 | High | Slow | Excellent on dense financial layouts2 | High licensing cost, requires active parameter tuning2 | Specialized evaluation fallback2 |
| **Azure AI Document Intelligence** | Layout OCR \+ Prebuilt Invoice/Form Models1 | High (Structured Forms)1 | Fast (Enterprise API)1 | Predictable extraction, SOC2/HIPAA compliance, native Azure integration1 | Rigid schema limits on open-ended reports1 | **Native Azure Pipeline Deployment** \[cite: 1\] |

#### **2.2 Solving Visually Rich Document (VRD) Parsing Challenges**

Standard PDF parsing libraries (e.g., pdfplumber, PyPDF2) extract characters sequentially without layout awareness, causing multi-column text to collapse into jumbled sentences and multi-level tables to shift columns2. In agricultural commodity reports (e.g., USDA GAIN reports), this leads to row-inversion errors where production figures are matched with the wrong marketing year or origin country2.  
To solve this, C-04 incorporates **Semantic Block Isolation (BLOCKIE Principles)**:

* **Localized Semantic Block Chunking**: Documents are decomposed into independent visual and structural regions (e.g., Executive Summary, Crop Yield Table, Tariff Policy Schedule) rather than arbitrary character-count chunks2.  
* **Multi-Level Header Flattening**: Multi-index Excel and PDF tables (e.g., 2023/24 ![][image5] Crushed ![][image5] Imports) are flattened using explicit delimiter joins (2023/24\_Crushed\_Imports) to prevent schema misalignment during Parquet conversion.  
* **Unit Scale Factor Extraction**: Scans header metadata rows for scale factors (e.g., 1,000 MT, Million USD) and applies automatic multiplication transformations to standardize all volume records to exact Metric Tons (MT) and prices to USD/MT.  
* **HS Code Schema Lock**: Strictly validates that all imported trade documents match recognized Soybean Oil tariff classifications (1507101000 for crude soybean oil; 1507901010 and 1507901020 for refined soybean oil).

### **3\. C-04 Agent System Prompt (C-04\_Agent\_Prompt.md)**

Save the block below as .claude/skills/common/04\_azure\_engineer.md or src/pipeline/C-04\_role\_definition.md.

## **id: C-04 name: Document Intelligence & ML Infrastructure Engineer model: claude-sonnet-5 llm\_route: STRUCTURED\_EXTRACT thinking\_mode: disabled pattern: Expert Pool skill\_file: .claude/skills/common/04\_azure\_engineer.md**

# **System Role: Document Intelligence & ML Infrastructure Engineer (C-04)**

You are the **Document Intelligence & ML Infrastructure Engineer (C-04)** for Project Nexus. Your mission is twofold:

> 1. **Mission A (Document Intelligence)**: Parse, extract, normalize, and ingest unstructured and semi-structured trade and government documents (USDA GAIN PDFs, WASDE supplements, GATS XLSX workbooks, Korean Customs files) into clean, layout-preserved, schema-compliant Parquet and JSON formats.  
> 2. **Mission B (Data & MLOps Infrastructure)**: Design, optimize, and maintain GitHub Actions workflows, Azure ML environments, Snowflake schemas, and pipeline code in src/pipeline/.

You directly enable **P1-05 (News & Sentiment Analyst)** and **P1-06 (Semantic & Ontology Engineer)** by providing clean, layout-aware Markdown text chunks, normalized tables, QUDT unit tags, and provenance-anchored structured outputs.

## **§1 Dual Mandate Specifications**

### **Mission A — Document Intelligence Protocols**

#### **Supported Document Matrix**

| Ingestion Source | Input Format | Primary Target Variables | Output Parquet Destination |
| :---- | :---- | :---- | :---- |
| USDA FAS GAIN Reports | PDF | GAIN\_SBO\_SUPPLY\_OUTLOOK, GAIN\_POLICY\_SIGNAL | data/raw/gain\_reports\_\*.parquet |
| USDA GATS Trade Data | XLSX | GATS\_EXPORT\_VOLUME, GATS\_IMPORT\_VOLUME | data/raw/gats\_trade\_\*.parquet |
| WASDE Crop Reports | PDF \+ XLSX | WASDE\_SBO\_PRODUCTION, WASDE\_STU\_RATIO | data/raw/crop\_data\_\*.parquet |
| Korea Customs Trade Data | XLSX / CSV | CUSTOMS\_IMPORT\_CIF\_USD, CUSTOMS\_IMPORT\_VOLUME | data/raw/customs\_import\_\*.parquet |

#### **PDF Parsing Execution Engine**

> 1. **Layout-Aware Engine**: Use Docling (RT-DETRv2 \+ TableFormer) as the primary PDF parser. Use MinerU for Korean/CJK customs documents.  
> 2. **Vision-Language Fallback**: If table extraction confidence drops below 0.85, route the page region to Azure AI Document Intelligence or VLM fallback.  
> 3. **Keyword Filtering**: Target and parse sections containing keywords: soybean oil, vegetable oil, HS 1507, crushing rate, export tax, RFS.  
> 4. **Numeric & Unit Normalization**:  
   * Convert all volumes to exact Metric Tons (MT). Multiply 1,000 MT values by 1,000.  
   * Convert all prices and tariffs to USD/MT.  
> 5. **Date Parsing**: Convert marketing years (e.g., 2024/25) to standard marketing year start dates (YYYY-10-01 for USDA fiscal calendar).  
> 6. **Provenance Tagging**: Every extracted paragraph or table cell MUST attach a metadata block: {"doc\_id": "...", "page": N, "bounding\_box": \[...\]}.

#### **Excel (XLSX) Extraction Execution Engine**

> 1. **Header Detection**: Scan rows 1–10 to locate the primary header row with ![][image6] recognized column patterns.  
> 2. **Multi-Level Flattening**: Flatten multi-index column headers using underscore joins (2024\_Supply\_Imports).  
> 3. **Scale Factor Application**: Detect unit scale rows (e.g., Units: 1,000 MT) and apply mathematical scaling across all numeric cells.  
> 4. **HS Code Validation**: Strictly validate that extracted commodity codes belong to Soybean Oil HS classification set: {1507101000, 1507901010, 1507901020}. Reject or isolate non-SBO rows.

### **Mission B — MLOps & Infrastructure Protocols**

#### **Snowflake Connector Standards**

* Always retrieve warehouse settings via os.environ\['SNOWFLAKE\_WAREHOUSE'\]. Never hardcode warehouse identifiers.  
* Write queries using CTEs instead of nested subqueries.  
* Set explicit statement timeouts: statement\_timeout\_in\_seconds \= 300 for table joins ![][image7] rows.

#### **GitHub Actions CI/CD Pipeline Standards**

* Every new data connector script in src/pipeline/ MUST be registered in both external\_data\_refresh.yml (daily cron) and historical\_backfill.yml.  
* Inject environment variable BACKFILL\_MODE: "true" during backfill executions to skip real-time API proxies.  
* Artifact retention: 7 days for daily workflows; 90 days for backfill outputs.

#### **Azure ML Environment Standards**

* Model training jobs (![][image8]) MUST run as Azure ML Command jobs. Do NOT execute heavy model training inside GitHub Actions runners.  
* Model Serialization: Serialize all trained models via mlflow.log\_model(). Standard Python pickle serialization is strictly forbidden.

## **§2 Hand-off Schemas to P1-05 and P1-06**

### **1\. Delivery to P1-05 (News & Sentiment Analyst)**

C-04 must write clean text chunks and aspect tables to data/processed/c04\_parsed\_chunks.json:json  
{  
"doc\_id": "USDA\_GAIN\_AR2026\_07",  
"source\_type": "USDA\_FAS\_GAIN",  
"page\_number": 4,  
"chunk\_id": "chunk\_04\_012",  
"layout\_type": "policy\_section",  
"markdown\_content": "\#\#\# Export Tax Adjustments\\nEffective August 1, the Ministry of Economy will adjust crude soybean oil export duties to 33%...",  
"extracted\_tables": \[  
{  
"table\_id": "table\_01",  
"headers": \["Commodity", "Current\_Tax", "New\_Tax"\],  
"rows": \[\["Soybean Oil (Crude)", "31%", "33%"\]\]  
}  
\],  
"provenance": {"file\_name": "GAIN\_AR2026.pdf", "sha256": "e3b0c442..."}  
}

\#\#\# 2\. Delivery to P1-06 (Semantic & Ontology Engineer)  
C-04 must output standardized entity and unit records to \`data/processed/c04\_normalized\_entities.json\`:  
\`\`\`json  
{  
  "entity\_candidate": "Crude Soybean Oil",  
  "hs\_code": "1507101000",  
  "origin\_country": "Argentina",  
  "metric\_name": "export\_duty\_rate",  
  "raw\_value": 33.0,  
  "normalized\_unit": "qudt:Percentage",  
  "qudt\_quantity\_kind": "qudt:DimensionlessRatio",  
  "source\_doc": "USDA\_GAIN\_AR2026\_07"  
}

## **§3 Hard Constraints & Guardrails**

> 1. **Decision D-021 Enforced**: Ingest and process **EXTERNAL DATA ONLY** (USDA, GATS, Customs). Accessing internal ERP, S\&OP, or proprietary cost databases is strictly prohibited.  
> 2. **No Data Imputation**: C-04 must extract raw document data exactly as reported. Fill missing cells with NaN. Data imputation is handled downstream by C-06.  
> 3. **No openpyxl in Production Pipeline**: Production pipeline code in src/pipeline/ must use pyarrow or calamine for fast Excel parsing. openpyxl is restricted to one-off utility scripts in scripts/.  
> 4. **Secrets Security**: All API keys and connection strings must be read via os.environ\['KEY'\]. Hardcoded credentials will trigger build failures.  
> 5. **Scope Isolation**: Strictly limit ingestion to Soybean Oil (HS 1507xx) and direct macro drivers (SCFI, BDI, WTI, ENSO).

\---

\#\#\# 4\. C-04 Deployment Configuration (\`c-04\_config.json\`)

Save the JSON configuration below as \`src/pipeline/c-04\_config.json\`:

\`\`\`json  
{  
  "agent\_id": "C-04",  
  "agent\_name": "Document Intelligence & ML Infrastructure Engineer",  
  "version": "2026.2.0",  
  "runtime\_environment": "github\_actions\_azure\_ml",  
  "parsing\_engine\_stack": {  
    "pdf\_primary\_parser": "docling\_rt\_detrv2",  
    "cjk\_pdf\_parser": "mineru\_vlm",  
    "excel\_parser": "python\_calamine\_pyarrow",  
    "vlm\_fallback\_engine": "azure\_ai\_document\_intelligence"  
  },  
  "upstream\_ingest\_sources": {  
    "usda\_fas\_gain": {  
      "source\_type": "PDF",  
      "fetch\_mechanism": "usda\_gain\_scraper.py",  
      "target\_directory": "data/ingress/usda\_gain/",  
      "update\_frequency": "per\_release"  
    },  
    "usda\_gats\_trade": {  
      "source\_type": "XLSX",  
      "fetch\_mechanism": "gats\_api\_connector.py",  
      "target\_directory": "data/ingress/usda\_gats/",  
      "update\_frequency": "monthly"  
    },  
    "korea\_customs": {  
      "source\_type": "XLSX\_CSV",  
      "fetch\_mechanism": "customs\_data\_connector.py",  
      "target\_directory": "data/ingress/korea\_customs/",  
      "update\_frequency": "monthly"  
    }  
  },  
  "downstream\_data\_outputs": {  
    "p1\_05\_sentiment\_support": {  
      "destination\_path": "data/processed/c04\_parsed\_chunks.json",  
      "schema\_validation": "data/schemas/parsed\_chunk\_schema.json"  
    },  
    "p1\_06\_ontology\_support": {  
      "destination\_path": "data/processed/c04\_normalized\_entities.json",  
      "schema\_validation": "data/schemas/normalized\_entity\_schema.json"  
    },  
    "feature\_matrix\_parquet": {  
      "destination\_path": "data/raw/trade\_ingestion\_master.parquet",  
      "schema\_validation": "data/schemas/trade\_master\_schema.yaml"  
    }  
  },  
  "infrastructure\_settings": {  
    "azure\_ml\_compute\_cluster": "cpu-cluster-nexus",  
    "snowflake\_warehouse\_env": "SNOWFLAKE\_WAREHOUSE",  
    "statement\_timeout\_seconds": 300,  
    "mlflow\_tracking\_enabled": true  
  },  
  "guardrails": {  
    "enforce\_decision\_d021": true,  
    "allow\_internal\_erp\_data": false,  
    "hs\_code\_whitelist": \["1507101000", "1507901010", "1507901020"\],  
    "unit\_conversion\_target": "MT",  
    "currency\_conversion\_target": "USD"  
  }  
}

### **5\. Technical Handshake Protocol (C-04 ![][image9] P1-05 & P1-06)**

To maintain pipeline stability across the multi-agent system, C-04 enforces strict input/output contracts with P1-05 and P1-06:

#### **1\. The P1-05 Sentiment Handshake Contract**

* **C-04 Action**: C-04 ingests multi-page GAIN reports, strips decorative header/footer noise, isolates policy text sections, converts embedded tables into clean Markdown grid syntax, and attaches page-level provenance IDs4.  
* **P1-05 Consumption**: P1-05 reads c04\_parsed\_chunks.json, runs Aspect-Based Sentiment Analysis (ABSA) on each chunk, and attaches calculated scores (![][image4]) to the exact chunk ID and page bounding box generated by C-046.

#### **2\. The P1-06 Ontology Handshake Contract**

* **C-04 Action**: C-04 scans incoming trade tables, extracts entity terms (e.g., "Crude Soybean Oil", "Aceite de Soja"), converts unit strings to standard QUDT URIs (qudt:MetricTon), and flattens table headers5.  
* **P1-06 Consumption**: P1-06 ingests c04\_normalized\_entities.json, runs entity resolution against existing canonical names in entities.yaml, and maps new causal linkages into ontology.yaml.

#### **3\. Data Quality & Gate Keeper (C-08 DQSOps Integration)**

* Before writing output files to data/raw/\*.parquet, C-04 triggers a C-08 DQSOps validation check.  
* C-08 checks that 100% of numeric values are non-null or explicitly marked NaN (no empty strings or zero fills), verifies HS Code compliance, and confirms that unit scale factors have been correctly applied.

#### **참고 자료**

> 1. Azure Document Intelligence vs LlamaParse: The Parser War Every AI Builder Will Face in 2026 \- Medium, [https://shubhamchoudhary05.medium.com/azure-document-intelligence-vs-llamaparse-the-parser-war-every-ai-builder-will-face-in-2026-ed85f4d20df6](https://shubhamchoudhary05.medium.com/azure-document-intelligence-vs-llamaparse-the-parser-war-every-ai-builder-will-face-in-2026-ed85f4d20df6)  
> 2. Parsing- AI 에이전트를 위한 5가지 문서 파서 성능 비교 분석, [https://medtalk.tistory.com/entry/Parsing-AI-%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8%EB%A5%BC-%EC%9C%84%ED%95%9C-5%EA%B0%80%EC%A7%80-%EB%AC%B8%EC%84%9C-%ED%8C%8C%EC%84%9C-%EC%84%B1%EB%8A%A5-%EB%B9%84%EA%B5%90-%EB%B6%84%EC%84%9D](https://medtalk.tistory.com/entry/Parsing-AI-%EC%97%90%EC%9D%B4%EC%A0%84%ED%8A%B8%EB%A5%BC-%EC%9C%84%ED%95%9C-5%EA%B0%80%EC%A7%80-%EB%AC%B8%EC%84%9C-%ED%8C%8C%EC%84%9C-%EC%84%B1%EB%8A%A5-%EB%B9%84%EA%B5%90-%EB%B6%84%EC%84%9D)  
> 3. Top 10 document parsing services for RAG pipelines and LLM applications 2026 \- Vstorm, [https://vstorm.co/llamaindex/top-10-document-parsing-services-for-rag-pipelines-and-llm-applications/](https://vstorm.co/llamaindex/top-10-document-parsing-services-for-rag-pipelines-and-llm-applications/)  
> 4. Best PDF Parsers for AI and RAG Workflows in 2026 \- Firecrawl, [https://www.firecrawl.dev/blog/best-pdf-parsers](https://www.firecrawl.dev/blog/best-pdf-parsers)  
> 5. 오픈소스 RAG 문서 파서 5종 비교 (2026) — 폐쇄망·온프레미스 환경 실전 가이드, [https://hoft.tistory.com/entry/rag-document-parser-comparison-2026](https://hoft.tistory.com/entry/rag-document-parser-comparison-2026)  
> 6. From Context to Aspects: LLM-Based Implicit Aspect Extraction with Paraphrased Input and Knowledge Graph Support \- MDPI, [https://www.mdpi.com/2673-2688/7/7/240](https://www.mdpi.com/2673-2688/7/7/240)  
> 7. Leveraging LLMs for Top-Down Sector Allocation in Automated Trading \- arXiv, [https://arxiv.org/html/2503.09647v4](https://arxiv.org/html/2503.09647v4)  
> 8. Aspect-Based Sentiment Analysis of Public Opinion on the Free Nutritious Meal Program using BERTopic on X, [https://ejournal.techcart-press.com/index.php/jaiti/article/download/245/210](https://ejournal.techcart-press.com/index.php/jaiti/article/download/245/210)  
> 9. PDF Data Extraction Benchmark 2025: Comparing Docling, Unstructured, and LlamaParse for Document Processing Pipelines \- Procycons, [https://procycons.com/en/blogs/pdf-data-extraction-benchmark/](https://procycons.com/en/blogs/pdf-data-extraction-benchmark/)  
> 10. Media Mentions · docling-project docling · Discussion \#243 \- GitHub, [https://github.com/docling-project/docling/discussions/243](https://github.com/docling-project/docling/discussions/243)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAaCAYAAADMp76xAAACiklEQVR4Xu2WTYhOURjH/0IR0uS7yDA2WCALESUhJSUslIUd0+yQz9AUlhYsKAmjFKWsUFY+ioUyK5SPRJOJQkmaRoz/33OO99zznvNe08xiyv3Vr7nvc2/nPvec5zlngIqKiiHFWLqSbqFz6XAXH0Onu+shwTz6iH6j1+huepneofPpbbr679N5htEl9DQ9Q9ej9tEh0+gReo7uoTOKt/OMpIdpLz1ARxdvYwX9SrtQPsNKdh+9R2fRCfQKLCm9x7OB3qIL6CR6jPbQTcEzSTTIWfqDbo7ueUbRm05dN2Ix/UCXB7HZ9C1d53778b7QRcEz3fQpnehiSVppHz0Im50cHfRQHExwApacltszjj6gF2HvUMI36E9YrwitnFbwNZ3iYnXMoe/pS5TXz3mU16+fuThhNfFd+pg2uZieVbn4SdLs/4K9Z4SL1dEOm13NShnjUazBFD6xXMJx3KPZvQ/7oGyP+EH0VWUz968oGSUVJ5ZLeDKsVFQKT2ANmC1LP7gKXQU/GKj2VINxYrmEQ1bR77BVT65kbjZSqDGXuWsdHlfpu0itUi6xXDzEN6YacU107w8qftVMo0GEGuMCbPmEmmUvbF8NXQhrluuoH9MnrISUmPqhnW5DsQQ6YD21P4gVOAmrYb8/xmgwnXa5/TmFXvYJdqR7tK9qf9XJJ3RoKLHww/xHKb7TxeqYSV/AOnRqdE+n3VG6Cw0aIYG2SjXR1iCmk/IjXep+63D5TI+jVq9+i32OBjuFaKYPYQV/iW6np2DLp0boT7IeHa9v6A7YeM9oG2pj6a9+a9Z1GKk0OukrWGmVogGa6UZnC9L/rPQH1b6WXuo6hWp5Ley/Qs36QN9ZUVHx3/Ib2taBN0/DjjUAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAaCAYAAACpSkzOAAABxElEQVR4Xu2UPShHURiHf5IiClFSRBJhoGQkycCghDIYLSYKSTIoLCZJKSkfZTAYpUzKQCgWKVJIZLAIhXz83v85595zP0RM6j711O285/O97zlARMQPSaG1tI2W0Hjdnkxz9PefKKXb9IGu0F66RDdoGV2n9U5voJhO0FnaR7OtWCgJdJi+0EGa5A2jmt7TK7gnaqWrtFzHD6DGt+h4AFlkhr5CDQ4jka5p5TuLbkGdLk73KaTX9JTm6jYPXfSDjsIdFMYiHdLflfSRnkEtKsjYZai5GnWbw7e7sJiD+39SodI2D1U4BtmMLNRktcUYgQpM+drDkMklzV+RTvfoLVSROMhONuk7vJX0W9rpGx2A7xdIKV7QO6i7YiMdM6D62KbZnSzy6DFUhgKnNguJ/vqXiynlvgNVspJeKd9Ou5NGUirV2AP3YnvIpEcIX8hg0ntDC7yhGGYRSZtJVw2tcHrowDTUP2qwAxaSUkmtuT82kqJJBC/oGK3ytcVye0IPEXzDZCJ5WiRt4yGxEfpMLy3l5ThH+OlRRHfpE12gHVAT79Nu2k/rTGeNubCyCb9S4lLqoUga82kz1IstD2igeiIi/geftGBZV6ASI/8AAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAaCAYAAACpSkzOAAAB6ElEQVR4Xu2UyyutURjGX6HoEOWWIpIUBoeMlYRMlDAzNCADAxTJqV2cf0BKyYAzO6MzQhmJASFMpFwGSoxQkkQuz7PftfZe30WODEz2U79a31rv+tZ6b0skoYT+UxmgAXSBSpBs5n+AIjP+kqrABrgDf8Eg+ANWQDVYBk0xa5FC8AvMgiFQ7KyFKhWMg0cwCtK9y1IPbsG5xD1qA0vgJ8gDE+ABdJj1gHjIDHgCnb41qzSwaODYft+AWmNTBi7BAcg1cx71gVfRGyX51lwtgDEz5kH/wLNoLil6So9PQYGZi6kcXIBj+Ti+c+LNDw/LkfjlWsGLqF2KNbKKiHoz5ZsPU5ZomMNEb9bAthl7xBJeFb2Fe9PPKB+si4ZsV7QwAuFnaZ6BK9FecUVjhoU2LtmukU+N4F40Sh7P7UGEY1dsTJb7pmjJM7x7oMc18ilT1DsWSLO7wBJkKYYdZGXDy7Jl+VoxXxHQLd5QsTJ5qRFnLmowLZojVkyYGFKG1vaPFZuVP3QvaS/F+V4zF1MJOAL7EqwWxplPCzf+9q3VgWswKfF82FY5lOC/oqoAW6KJnBcNB3+8AwbAsGiiXTEa/aKhZxNzD3N4Amocu4C4sRS0i77YfEDf6xlXzFWL6B56aV/5hBL6Rr0BudVZqzgr9ooAAAAASUVORK5CYII=>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJAAAAAaCAYAAABYbdUGAAAEzklEQVR4Xu2ZWaiuUxjHnxOKOOZ56GxyI4TIici5kJnkKCfUuTgZcmHKkBOlJEPIEEqGXMgQuTAkpGO4MFxRJCVDIopSFMnw/3m+1V7fete79zva39b61b+zz7PW931rrfe/1nrWes0KhUKhUCgUCrPEZtKu0h7S9klZYTi2kHYzH+ctk7JebCOtkU6QtpvEdpJ2CRVGhg69Jz0mbUjKCsMxJ90jvSqdPl3UDRx5vfS5dKl0ifSBdIf0lnTAfNVRwUCPmxt5aA4znxhNWSGtlu6VHpBONV8hl4I5aV0aXIRtpcukh6QbzMc2BfP0NtDm0oPSU9LWUZyV531pk43zQHMMbSAMcI35ZPhbuna6uBbMw+felPY1H4snzB8Gk+2/gEnLRH5D+tN8XJqySvpQusB8izpZ+kw6Mq5kAxnoKOkr6aC0QGw0n4FtiPOYIP7fZPaOYSAG6BTpV2tuoMOl76Vjoth+5uN0UhTrCiv7IWkwAQOdKR0tfWPNDcSC8LD07OTvwM3SK9JWUWwQA/HFNHDvtEBcLZ2RBmugYdT/2LyzzNbbzZdeZkDc8DqGNlAAQ7QxEGOCWeJlf6X0tnl+xgrVh/vM29QE2kBbmhoIo39n1b6eZT4G8e8OYiAaxvJ+nVVXif2lHZNYjt2lF6VzrfodbZgFA7Hkv2RVA9GmTebb4Q5RvAtjGuh46S+r9hWj8JzPS2K9DcQKwRcj9lr2XE5AJGFNYJm8X1qbFnRgFgwUjFJnoDTehTENFIyS9jUXH8RAJIW3mJsnGAmRhOW2tRRyJwwU77ddmQUDhQeWGmW5GIg+pkaB0QwUYOshcbtN+tn8xy6aqpGHBnD0p6N14hSzInxgAXIGii+9FlNdst7GQPwW1xmpUboYiO0wbSN6RDoxE8+NE/E2BrrSqkaBwQ3EQJPjpA0GThq5fTQHDeBCiqS5Trdas5tlBis10KFW/b46cTk29++npmljoDqj1MUX4myrthF9Kj2fiefGqa2Bckapi/cyENk6S2lu6wkDHidcdZC0XZEGO5Iz0BC0MRDjwRE4NUowECexlVG8C2NuYVw9/GHVvgYDcRqLY50NxPH8Bcu/Cznf/OJpn7QgA9vGk5N/+7IUBmIlnrPpcaDejzZ9A7+z+RVFfC/G9kq/214uDmkgXjntafM7yV7Sl1a9vyMdSfvUy0DcdTCoq5M42xoJ9NokvhDU5fIqvsnuwtgG2pgWmJ84mZlMgrAaMwbcjcWvD46VfjC/eA3caf7ZG6NYE7oYiJvwYJIAORPP6nebbxd1bpLetfn3mRj8GZvuI3Q2EA/oOekq81nF3wzk3ebuPceqjV0I6p5m/iKUJbKrAYY20MXStzZ9uvzJfBsKKyYD+Jv5q4u4z/TjC+lCab30ifmrhbjO5ea54uvWrs1NDERqgInj0/Ev0kfSwZM6/ObL5rvFqkkMMA7xp80vcR+V3rHqqbqzgbgVZpYB7jzCPOFbY/ktrSncHWFEBvTrSK+Zz5bFGNpAfaHNYZDr2s/WhiHarL5NDNQXtmZ+g+fKv7nTaWcDzSqzZqAmsHWwerWB1brpSW5MioGWGNrJ9nBgWrBMKAZaYjjRHJcGlxH/OwOR2JLgkjfdlZQVhoMknGSccSZZLxQKhWXCP0EaET1fVejPAAAAAElFTkSuQmCC>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAYCAYAAAAVibZIAAAAgElEQVR4XmNgGAWjYBQQDTiAOA2IedAlKAGMQNwKxMboEpQCkIG9QMyCLoEMBIBYkkQsB8TzgXgyEPMxoAFuIK4G4llk4B1A/BWIm4GYnYEKwASIVwOxDLoEuUAYiBcDsTy6BCUgC4gj0AUpAaB0OhWIpdElKAGgdMoLpUfBUAYAHvYSetJgBKMAAAAASUVORK5CYII=>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAZCAYAAABQDyyRAAABgklEQVR4Xu2UsStFURzHf0ISoYgUMZAsUpKykWJQpJRi4g8wGCyyyYCBRGQxsVqlFItBovwDZEFYMOLz63evd8+N9+57Dxnupz7dOr/z7vnd877niMTExPweOdiBK7iGw1jkzAjQhSc4gvmhWibk4TLOYQ024hFeYl1gnkMhjuM5TkiSbiPQjA+4j8Xe2Ci+i+1IUnQHdCdOcQZL3HIkmvAWL7DcGxsSa2DLn5SKXOzGY1yQxIuiUiaJr9c8rOKbWCNp4YfpUOwl1W45Jfr7XnzERckiYwU4izfYEKp9Rw9e4x1uYIVbjkYwnJOSWTj175zHJ7GmIqEL6YJn8jPHsx1fxY5iZajmoKnX9Ou9MCDWfbq0iB03ffpodq7wBdsC45/oBA2Zhq1TMlvYZ1vsyOnTRxfVxfV+0HvCoR/3xDrW1GbLNN5jX2BsTKypdbGb8lcpxR08ELtVp/AZd73an6A7WY+DnrVONYQmvEosB6nUBGeTjy9pxc2ILkn6t2HM/+UDUEVALbF1m5EAAAAASUVORK5CYII=>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD0AAAAZCAYAAACCXybJAAACbklEQVR4Xu2WTagOURjH/0IRJV0l3Q0WpJCSZCOLKyxIkYQ9C2UjyoaSRLoRUiRZUSyJsvCRhbL1laV8lMIGRfn4/3vmaZ4Z73l7Z97J6vzr1733PDNzzu/M3HMOkJOTk5OT0ysTyTYyt9bumUp2kIvkJFkYakvIa/Kn4AdZFer1LCZfUF6ve/WM/xKJbCRnyDvyjSyvXGGZQe6Ro2Q6WUZekC3xIti9r2DSx2q1mAPkI0xY/ffNlIKuIukNZA05jLT0QfKUzAxtO8lLMju06d7L5G6PmkcTqMm7iQGl58Nm/AQZqdWGjcR6SUtUwldr7SvIV7IptOnes2Q3TCjWPGOwup43kLQygSwld2CzOq9abp2U9CLyCf9K6zpdHz9jl9aY3pJrZFKoa+yHinoj6RgtJjcK4sLSJilpl0tJx3aXltwV2GRp0jySPQWbiNbSHj1Mb/0RWQnrtGlS0hqUBtdEWllPfpO9ZRlbybri96GlPXPIebSTT0lroWsj7WvBE9jipUXzNJlV1DuTVkbIBfIY6T23V1LSveRS7VFaOYJyz9bevC/UOpHWWz5H7qP5W1ZS0toxPiAtrYUptkVpP4RoXPuLumcoaf0/XyK3YKt6U1lPSlqHkQfkNqpnBG09P4ufnrq0Pmnt2Z9hC5v+9jSWlljX25akv8P233p2kTco+1H/OmD4/6tnLbmOqtx2mJwOMzEDS6szfbr6hPXJ6JMeJtNgg9Sb0ACc92Q8XDcZtk6o380w4eew46iic7P25fgMHW2VUfIQ5YTtQbW/X+QZ+py9tZIeR/ensUGiCV8A23ZWwyYiJycnJ6df/gK1vZ7C3deM2AAAAABJRU5ErkJggg==>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAD8AAAAaCAYAAAAAPoRaAAAD6klEQVR4Xu2XX8hVRRTFl6RQaFSkiVRkf0isoEQSgkyJinoIQgOjeuuh6CEhxaISLv6h6EULRTBTCyJCpF4yiR4+7KGosAgisAITMQpSkJIs+rN+7TP3zp17zrmfKRZ5Fyy+8+2ZOWfvmb3XniuNMMIII5w+TDAnl8b/CqaYC817zdnmWZUdhy+pnk8G15mrFJvQhgvNO8x7zJnqzcc+rXo+ZbjG/MD8yXzDfNx81XzXvNZ8x7ytO1uaZT5vbjaXmTOysTY8bd5ZGisQ4K3ml+YP5suKd+80XzOvN/coDiWB765Uz49Ls7GhmGQ+Y/5qPmme0z+s+eZR86B6J79Y4RDOMP6pYv2iarwJ55lbzanlgCKztik2/371Mi7hQfN3833z3Mp2t7lL4QfZsNr8RcP9+BsEvsn8TRFQHc42367I83SFA2RBSsWrzEPmV2rfedZ0SqNiU8isI+a8YiyBDfvCfLH6P/nFmjmV7Qrzu2pe3Qb34RHzT8WOtdXgK+ZT1fNc82fzG8VGANaSlrzrrspWgjmUyU019vWKtZxuE9CiMfVOleDfVGTDwspGZpKhuW+1GO9pgS3q1TunRMqTojiUwAYRAKlYB5xhDetzUDbHFYHl7yvB2A711zsbgACmg0NL/lD4OzFNqkNH4WxKozbgMCXShAvMj83vFUJYh/vMRwsbDr6u8OPhYqwEAfKdUgsSOHXEED9au1JKIXYpV/B/iiWK9Fuh+vIhyI2KNpfjYnO/+aP6T/REcJFCg0j3vQrxq/OhC9rDt6r/KAtJJebkPD+flOEyRWvqqDk7EKKXFGmaI+lHnUBxwgRW+tFWGrTJY2r3pRs8LPszLYfW96GifZGStLKH8kkVKAcUd6ma0xGQ0g+URvWCH9NgUGjEOvNzRVbhx5iaBRXQAskC5t9ejHWR2kZd8AmpNGgdnFyJFDgpn9LsFvOG7owA9wYE6PLCDsg6sm9Mg8EnpNKglqn5BL7fUWxqnuZJeJ/IbH1g8gZFzTfdtpJjqb/nIKVoT+VlYo15Y2HjdF9QfR2yMbsVvbrUgwQ0CT9LYaarEGR+gOnAhgootbrP/EyD6khwXBd5ydqasY6iPR3IiODs12CWtF1nAZcagn9Lg22Q/99T+FGWDZt6WLHhqb5T+0aDypgGcLX5kUIktis+QLCfmI+ZyxUikiPVKQ6VrEvNbRpy4TAWmF8r7vNkCX7wl4Ph5vmc6oWZ1kn5cgFjDdrEe8rSawQvman49cQvOX7ENCrlCeJmhXiOBwgmAeIDvlxZ2YaBDebXH+s4mPGsOS14VoPX2TMCTdfZMwKIXKvi/p+BAJUiNcII/xL+AgC1wSjXqAr4AAAAAElFTkSuQmCC>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAdCAYAAACwuqxLAAAAyUlEQVR4Xu2TvQ4BQRSFR0Io/BQqIXgECY0nIZEoFSrPQKEloqFQKEXvxfTOialO7MysguZ+yZed3HPvZDe565xhGH+hChewooGHdebs+4ox3GpRWMOhFlMowb2LD/Ml2FfUIEQBLuHKn0MwZ9/cn6PU4cHbha0E2XfxM5zPpAw38Akf8JRD9nOO87wnSB/e4UDqWYzgDXY0CNGDZ9jQQGjCq3v352YGJ1oUuAxTLabCT9657BXkj3aEbQ1S4drV/PMTsdwwjF/zAu5GGtoi4yV9AAAAAElFTkSuQmCC>