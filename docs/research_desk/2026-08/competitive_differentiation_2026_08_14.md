# 경쟁 차별화 및 대두유 운영구조 조사 (C-01×C-02×P1-04)

작성일: 2026-08-14 · 작성 주체: 조정자 지시 조사 세션
관련 문서: `model_strategy_2026_08_12/` (모델 전략) · `src/semantic/causal_chains.md` (인과 온톨로지)
※ 지시문이 참조한 `domain_mechanisms_sbo_2026_08_13.md`는 현재 저장소에 없음 — 본 문서 §3이 해당 도메인 노트의 역할을 겸함.

---

## §1 경쟁 지형

| 구분 | 업체/플랫폼 | 대상 시장 | 핵심 데이터 | 방법 | Nexus와의 겹침 |
|---|---|---|---|---|---|
| 국내 | Barka **LexoEye** | 국내 농산물(양파 등 노지작물) 작황·가격 | 기상 + 현장 실사 | 작황 방향성 예측 | 낮음 (국내 농산물, 수입 유지류 비대상) |
| 국내 | Impactive AI **Deepflow** | B2B 원자재 가격예측 (철강 등, 포스코 공급) | 거시지표·환율·수급 | 시계열 DL + "블랙스완 방법론" | **중간~높음** (범용 원자재 가격예측 SaaS) |
| 국내 | **새팜**(SaeFarm) | 국내 농가·식품기업 작황 모니터링 | 위성영상(농림위성·미국 고해상도) | 필지 단위 생육 AI 진단 | 낮음 (재배 가이드, 가격·조달 신호 아님) |
| 해외 | **Cropin** (인도) | 글로벌 농기업·정부 (10억+ 에이커) | 위성·기후·작물지식그리드 | Cropin Sage (Gemini 기반 GenAI) | 중간 (작황 강함, 조달의사결정 약함) |
| 해외 | **McKinsey ACRE** | 식품·원료 제조사 조달팀 | 농경·기상·위성 다층 데이터 | ML 가격·수급 예측 + 컨설팅 | **높음** (조달 고정 시점 최적화 직접 경쟁) |
| 해외 | **Octopusbot** (호주) | 곡물·유지작물 트레이더·수출업체 | 100년 기상·위성·수급·가격 | 1.5k 연결 AI 모델, 수급·가격 시나리오 | **높음** (유지작물 수급·가격) |
| 해외 | **Layers** | (실체 불확실 — 아래 참조) | — | — | 판단 보류 |

### 업체별 상세

**Barka LexoEye** (lexoeye.io) — 한국 스타트업. 기상 데이터와 현장 실사로 제주 조생양파 감산을 방향성 수준에서 적중시킨 사례가 보도됨. 창업자 스스로 "우리의 강점은 예측이지 실행이 아님(prediction, not execution)"이라고 밝혀, 소싱·물류·재고 등 실행 계층은 비대상임을 자인함. 국내 노지 농산물 중심으로 수입 유지류 국제가격·조달은 다루지 않는 것으로 보임. 사이트 직접 확인은 못 했으며 검색 결과 기반임.
근거: [KoreaTechDesk 인터뷰](https://koreatechdesk.com/ai-predictions-fail-real-world-execution-korea-case)

**Impactive AI Deepflow** (impactive-ai.com) — 국내 경쟁사 중 Nexus와 가장 유사한 포지션. 포스코에 원자재 가격예측 솔루션을 공급하며(2026-02 보도), 2026-06 '딥플로우 머터리얼즈'를 정식 출시함. 거시지표·환율·수급 데이터를 통합하고 단기~중장기 구매전략 수립을 지원하며, 급변 이벤트 대응용 '블랙스완 방법론'을 내세움. 강점: 국내 대기업 레퍼런스, 수요예측+가격예측 통합 SaaS. 약점(추정): 멀티 원자재 범용 플랫폼으로 대두유 도메인 메커니즘(압착마진·대체유지 스프레드·바이오연료 정책)·한국 수입 실무(관세청 HS·CFR 조건) 계층은 확인되지 않음.
근거: [서울경제](https://www.sedaily.com/article/20004254) · [출시 보도](https://news.nate.com/view/20260611n13952?mid=n1101) · [공식 사이트](https://www.impactive-ai.com/en)

**새팜(SaeFarm)** (saefarm.com) — 2022년 설립 위성 AI 농업 스타트업. 위성영상으로 국내 35개 작물의 필지 단위 생육·스트레스를 진단하고 수확량을 예측함. 풀무원 전략 투자, 노바벤처스 Pre-A, CES 2026 혁신상 수상. 강점: 국내 위성 작황 정밀 진단. 약점: 농가 재배 가이드가 주력으로, 국제 상품가격 예측이나 수입 조달 의사결정과는 시장이 다름 — 경쟁자라기보다 잠재적 작황 데이터 공급자에 가까움.
근거: [saefarm.com](https://saefarm.com/ko/introduce) · [풀무원 투자 보도](https://v.daum.net/v/KYIeTdLxy1?f=p) · [CES 2026 혁신상](https://www.chuksannews.co.kr/news/article.html?no=268823)

**Cropin** — 인도 기반 글로벌 agri-intelligence 플랫폼. 10억 에이커 이상 계산 경험, 위성(약 40개 원시 지수)·기후·작물지식그리드를 결합하고, Google Gemini 기반 GenAI 플랫폼 'Cropin Sage'로 수확량 예측·지역 벤치마킹을 제공함. 강점: 글로벌 위성·작황 커버리지와 엔터프라이즈 실적. 약점: 농장 운영·작황 인텔리전스 중심 — 확률 가격밴드나 조달 Buy/Hold 신호는 핵심 상품이 아님.
근거: [Cropin Sage](https://www.cropin.com/intelligent-agriculture-cloud-cropin-intelligence-cropin-sage/) · [위성 모니터링](https://www.cropin.com/blogs/satellite-farming/)

**McKinsey ACRE** (Agriculture Commodity Research Engine) — 농경학자·데이터과학자 결합 애널리틱스 센터. ML로 수확량·품질·**가격** 변동을 예측하고, 식품 제조사 조달팀에 "언제, 얼마나 멀리 가격을 고정할지(when and how far forward to fix)"를 최적화하는 맞춤 분석을 제공함 — Nexus G3와 문제 정의가 가장 유사함. 강점: 조달 의사결정 직결 + 도메인 전문가 결합. 약점: 컨설팅 결합형 고비용 모델로 표준 SaaS가 아니며, 사내 상시 운영 체계(일별 파이프라인)로의 이식성이 낮음.
근거: [ACRE 소개](https://www.mckinsey.com/industries/agriculture/how-we-help-clients/acre) · [식품 제조사 대상](https://www.mckinsey.com/industries/agriculture/how-we-help-clients/acre/food-and-ingredient-manufacturers)

**Octopusbot** (octopusbot.ai) — **실체 확인됨.** 호주 agtech 스타트업(US$1M 시드 조달 보도). 곡물·유지작물 대상 SaaS로, 1,500개+ 연결 AI 모델·100년 기상기록·위성·수급 데이터를 사용해 지역 단위 수확량·글로벌 수급 추정·가격 시나리오 모델링을 제공함. 트레이더·브로커·수출업체·금융기관 대상. 강점: 곡물·유지작물 특화 글로벌 수급 예측. 약점: ">96% 정확도, 6개월 선행" 등 자사 주장의 외부 검증이 없고, 수입국 조달 실무(무역조건·관세·운임 전가) 계층이 없음.
근거: [octopusbot.ai](https://octopusbot.ai/) · [Startup Daily](https://www.startupdaily.net/topic/funding/agtech-startup-using-ai-to-predict-grain-crops-plants-1-million-first-raise/) · [FAO 등재](https://dvi-ke.fao.org/digital_solutions_details.php?id=770)

**Layers** — **실체 불확실.** 검색에서 확인된 것은 스페인 마드리드 기반 LAYERS(2012년 설립, HEMAV 계열로 추정되는 농업 AI SaaS — 작물 생산 예측, 플랜테이션·식품기업·금융기관 대상)뿐임. 조정자가 지칭한 "Layers"가 이 업체인지, 별개의 곡물 트레이딩 플랫폼인지 확정하지 못함 — 후속 확인 필요. 한국 기반 동명 업체는 검색되지 않음.
근거: [CB Insights — HEMAV/LAYERS](https://www.cbinsights.com/company/hemav)

**시사점**: 경쟁 지형은 ①작황·위성 계층(새팜·Cropin·Octopusbot·LexoEye)과 ②가격예측 SaaS 계층(Deepflow·Octopusbot), ③조달 컨설팅 계층(ACRE)으로 나뉨. **"수입국 조달 실무자의 매입 의사결정"을 일별 파이프라인으로 상시 지원하는 포지션은 공백**이며, 이것이 Nexus의 표적임.

---

## §2 차별화 포지셔닝 — 보유 자산 vs 로드맵

> 원칙: 저장소에 실재하는 자산만 "보유"로 분류함. 설계·규칙만 있고 실증이 없는 항목은 그렇게 표기함.

### 2.1 보유 (실자산 근거)

| # | 차별화 지점 | 실자산 근거 | 경쟁사 대비 |
|---|---|---|---|
| ① | **as-of 시점정합 규칙 체계** | CLAUDE.md §1 as-of rule + `modeling.md` Cross-Goal: `event_time`~`available_at`~`ingested_at` 6필드 분리, WASDE 실제 발표일 이후 사용, vintage별 적재, 발표일 이후 as-of fill, `duckdb` ASOF JOIN 채택 | 업계 백테스트의 흔한 look-ahead 오염(월간 보고서를 대상월 초에 안 것처럼 취급)을 규칙 수준에서 차단. 단 **"백테스트 실증 완료"는 아직 주장 불가** — 규칙·설계 확립 단계임 |
| ② | **한국 조달 실무자 특화 데이터** | 관세청 GW: 대두유 HS 6단위(150710/150790) + **대체·보완재 9품목 11개 HS코드**(팜유 1511, 해바라기유 1512.11/.19, 유채유 1514.11/.19, 팜핵유 1513.21, 대두 1201.90, 대두박 2304, 바이오디젤 3826) × 10개국 × 2010~2026 (`ingest_customs_gw_xlsx.py`, 교차검증 4기준 A-072) · USDA FAS ESR 한국(국가코드 5800) 수출성약 · TE 상품 14종 9개년 34,118행 · BDI/BCAA 운임 체인 | 글로벌 플랫폼(Octopusbot·Cropin)은 수입국 관세·원산지별 CIF 실측이 없음. ※ 지시문의 "대체유지 16종"은 실자산과 다름 — 현재 9품목 11개 HS가 정확한 수치 |
| ③ | **시맨틱 온톨로지 기반 근본원인 설명** | `src/semantic/causal_chains.md` **인과 체인 18건** (Cause→Mechanism→Price 3단 DAG 강제, 직접 Cause→Price 금지) · `ontology.yaml` 관계타입 정의 + S1 게이트(미검증 인과 엣지 자동 승인 금지 — P1-01~04 도메인 검증 필수) · `provenance.yaml` 출처 보존 | 블랙박스 예측(Deepflow·Octopusbot)과 달리 "왜"를 검증된 인과 경로로 설명. ※ 지시문의 "validated 인과엣지 21건"은 실자산과 다름 — 18체인 + 검증 게이트 보유가 정확한 표현 |
| ④ | **비정형 코퍼스 + 구조화 파이프라인** | USDA GAIN PDF 4,100여 건(Oilseeds 3,159 + Biofuels 1,023) · FAO AMIS 137건 전량 요약 완료(A-079, 신호 태그 8종·방향성·근거 발췌) · P1-05 ABSA 스펙(aspect 7종, evidence_snippet 의무) | 15년치 정책·수급 정성 신호의 시계열화 기반. 원문 발췌(evidence) 의무화로 환각 차단 |
| ⑤ | **검증 방법론 차별화** | Champion–Challenger 포트폴리오(사전 등록 승격 규칙) · stress slice 별도 보고(2012·2018·2020·2022·2025) · lockbox test · 레짐×호라이즌별 지표 표 | "평균 정확도 96%"류 단일 점수 마케팅과 대비되는, 위기 구간 성능을 분리 보고하는 정직한 검증 체계 |

### 2.2 로드맵 (아직 없음 — 과장 금지)

| 항목 | 현황 | 목표 |
|---|---|---|
| as-of 백테스트 실증 수치 | 규칙만 존재, 모델 입력 통합 테이블 부재(01_data_inventory §2) | G2 walk-forward에서 as-of 적용/미적용 성능 차이를 정량 제시 |
| G2 확률 가격밴드 | 미구현 (`src/forecasting` 3개 파일, 기본 G1만) | 9/10 Preview (WBS_0730) |
| G3 레짐/Buy·Hold | **미구현** (`src/risk/` 파일 없음) | Markov 레짐 + Monte Carlo P&L |
| 비정형 **일별 다이제스트** | 월간 코퍼스 요약까지 완료, 일별 상품화 없음 | P1-05 ABSA 게이트 통과 신호의 일별 브리핑 |
| 대체유지 스프레드 **파생 피처** | 원천 수입통계·TE 시계열은 보유, CPO-SBO 외 스프레드 지표화 미완 | 유지류 대체 탄력성 스프레드 세트 |
| Incoterms 동적 전환 시뮬레이션 | 본 문서 §3d 스케치가 최초 | G3 확장 (§4) |

---

## §3 대두유 운영구조 (도메인 노트)

### 3a. ABCD + COFCO·Wilmar의 대두유 사업 구조

**압착·정제 거점**
- **아르헨티나 로사리오(Rosario) 일대**: 미주 최대 대두 압착 허브 — 파라나 강변에 22개 플랜트, 일일 압착 능력 157,500톤. Bunge 단독으로 로사리오 권역 일 18,000톤. 아르헨티나는 내수가 작아 압착품(대두유·대두박)의 수출 비중이 세계 최고 — "Up River"(파라나 상류) FOB가 남미 대두유 수출가격의 기준점. LDC는 Bahía Blanca 심수항 기존 인프라에 해바라기·대두 압착 플랜트를 증설함.
- **미국**: 중서부(일리노이 등) 압착 벨트 + 걸프 수출 체계. ADM은 노스다코타 Spiritwood 신규 압착·정제 플랜트(일 150,000부셸), 일리노이 Quincy 압착·정제 증설. 미국은 45Z 등 바이오연료 정책으로 내수 소비가 늘어 수출 여력이 정책 변수에 민감함(→ causal_chains '정책·규제').
- **브라질**: 내륙 압착 + Santos 등 항만 수출. CME는 FOB Santos 대두 선물을 상장할 만큼 Santos FOB가 독립 기준가로 자리잡음.
- **COFCO**: 장자강(Zhangjiagang) East Ocean Oils & Grains — 아시아 최대급 통합 압착·정제 단지. 중국은 대두를 수입해 자국에서 압착하는 구조라, 중국 압착 수요가 원료 대두 무역과 대두유 국제수급 양쪽에 영향을 줌.
- **Wilmar**: 중국·인도·베트남·말레이시아 등지의 압착 플랜트 + 세계 최대급 정제·유통망(팜 바이오디젤·올레오케미컬 포함). 아시아 역내 정제 대두유(RBD) 공급의 핵심 채널.

**한국향 공급 경로** (관세청 GW 실측과 정합): 조대두유(150710)는 미국·아르헨티나·브라질에서 탱커로 수입 후 국내 정제, 정제 대두유(150790)는 역내 정제업체 경유분 포함. Nexus 관세청 데이터의 국가 축(US/BR/AR/CN + 확대 원산지)이 이 경로를 그대로 계측함.

근거: [Western Producer — Rosario 압착 허브](https://www.producer.com/news/bunges-coveted-argentina-plants-lure-adm-takeover-approach/) · [World Grain — 설비 투자](https://www.world-grain.com/articles/23092-slideshow-companies-invest-in-grain-oilseeds-facilities) · [TipRanks — ADM Spiritwood](https://www.tipranks.com/news/buoyed-by-demand-adm-to-build-soybean-crushing-plant-in-north-dakota) · [COFCO 장자강](http://www.chinaagri.com/en/BusinessBrand/c-160.html) · [Wilmar 연혁·사업](https://www.wilmar-international.com/about-us/history-milestones) · [CME FOB Santos](https://www.cmegroup.com/markets/agriculture/oilseeds/fob-santos-soybeans-financially-settled-platts.html)

### 3b. 무역 조건 — 가격 구성·규격·결제

**Incoterms 관행**: 수출측 기준가는 **FOB Gulf**(미국)·**FOB Up River**(아르헨티나 파라나)·**FOB Santos/Paranaguá**(브라질). 아시아 수입측 실계약은 **CFR/CIF 도착항**(한국항·인도항 등)이 일반적 — Fastmarkets의 Soyoil **CFR India** 평가가 CME 신규 선물의 기초가 될 만큼 CFR 아시아가 표준 벤치마크임.

**가격 구성** (분해 가능한 4개 층):
```
CFR 한국항 가격 ≈ CBOT ZL 선물(플랫프라이스 축)
                + basis(원산지 FOB 차 — Platts가 CBOT 대비 差로 고시)
                + 해상운임(MR/파슬 탱커 — BCAA 식물성유지 40,000mt 기준)
                + 보험·부대비(CIF 시)
```
2026-07 S&P Global 보도가 실증하듯 **CBOT 급변동을 basis가 흡수**해 남미 FOB가 상대적으로 안정되는 구조 — 즉 CBOT 예측(G2)만으로는 조달가 예측이 불완전하며 basis·운임 층의 독립 모니터링이 필요함(→ §5 지원 항목).

**품질 규격** (크루드/RBD 구분):
| 등급 | 규격 기준 | 핵심 항목 |
|---|---|---|
| Crude Degummed (수출 표준) | NOPA Trading Rules(수출용)·ANEC(브라질) | **FFA max 0.75%**(전형 0.66%), 인(P) max 0.02%, 수분·휘발분 max 0.10%, 인화점 min 121°C |
| Crude (FOSFA 계약) | FOSFA 51 | FFA max 1% (oleic 분자량 282 기준) |
| RBD (정제·표백·탈취) | 별도 완제품 규격 | FFA 대폭 낮음, 색도(Lovibond) 기준 추가 — 조유 대비 프리미엄 |

**결제·선적 주기**: 성약 후 선적까지 통상 수 주~수 개월의 선도 포지션(월 단위 선적 window 지정), 결제는 L/C 또는 CAD·B/L 기준이 관행. basis 계약은 선적 전 futures fixation(가격 확정 시점 분리)이 수반됨. ※ 세부 결제 관행은 계약별 편차가 커 브로커 확인 필요(§5).

근거: [S&P Global — 남미 FOB basis](https://www.spglobal.com/energy/en/news-research/latest-news/agriculture/070126-south-american-fob-soybean-oil-values-remain-resilient-as-basis-absorbs-cbot-futures-volatility) · [Platts 곡물·유지 방법론](https://www.spglobal.com/content/dam/spglobal/ci/en/documents/platts/en/our-methodology/methodology-specifications/agriculture/grains-oilseeds-specifications.pdf) · [CME — 남아시아 식용유 선물(Fastmarkets CFR India 기초)](https://www.prnewswire.com/news-releases/cme-group-to-launch-four-south-asia-edible-oil-futures-contracts-302685292.html) · [NOPA SBO Trading Rules](https://www.nopa.org/wp-content/uploads/2023/10/SBO-Rules-and-Appendices-MY2023-24_FINAL100123.pdf) · [ANEC 브라질 디검드 규격](https://anec.com.br/uploads/clpmxj3aq000gihtxeuncbpp5.pdf)

### 3c. 예외 상황의 선매입(advance buying) — 2021~22 사례

**실수요자 행동 (보도 실증)**:
- 2021년 초 캘리포니아 바이오연료 정책 + 작황 우려로 유지류 가격이 선행 상승했고, 2022-02 러-우 전쟁으로 우크라이나 해바라기유(세계 최대 생산) 공급이 차단되며 위기가 정점에 달함.
- 제조사들은 ①**커버리지(선매입 개월수) 연장** ②**대체유 전환**(해바라기→유채·대두, "soybean and/or canola and/or cottonseed" 복수유지 라벨로 사전 유연화) ③공급선 다변화로 대응함. Unilever는 해바라기유 부족 시 유채유로 전환함.
- 가격 신호: SBO-팜유 프리미엄이 2021년 $500/MT까지 급등(장기추세의 2배 이상) — **대체유지 스프레드가 선매입·전환 판단의 핵심 지표**였음을 보여줌. Nexus의 관세청 대체재 9품목 수입통계 + TE 유지류 시계열이 정확히 이 지표의 원천임.

**시뮬레이션 필요 파라미터** (G3 확장 입력):
| 파라미터 | 값 범위(초기 가정) | 데이터 원천 |
|---|---|---|
| 물리 리드타임 | 남미→한국 항해 30~45일 + 성약→선적 2~8주 | AIS·선사 스케줄, 관세청 월별 도착 실측 역산 |
| 계약 유형 | spot(당월~익월 선적) vs term(분기~연간 물량 약정) | 사내 계약 관행(외부 데이터 아님 — 파라미터로만 입력받음, D-021 준수) |
| 가격 고정 방식 | flat price(전액 확정) vs **basis 고정 + futures 추후 fixation** | CBOT ZL + basis 고시 |
| 커버리지 개월수 | 평시 1~2개월 → 위기 3~6개월+ | 2021~22 보도 사례 |
| 대체 전환 임계 | CPO-SBO 스프레드 >$175/MT(기존 체인) 외 유채·해바라기 스프레드 임계 추가 | 관세청 9품목 + TE |

근거: [Food Dive — 제조사 대응](https://www.fooddive.com/news/food-manufacturers-tactics-edible-oils-supply/624000/) · [IFPRI — 우크라이나 위기와 식물성유지](https://www.ifpri.org/blog/impact-ukraine-crisis-global-vegetable-oil-market/) · [CME OpenMarkets — 2022 공급 크런치](https://www.cmegroup.com/openmarkets/agriculture/2022/Edible-Oils-are-Facing-a-Supply-Crunch.html) · [FoodNavigator — 대체유 전환](https://www.foodnavigator.com/Article/2022/04/07/from-palm-oil-to-gmo-feed-how-is-europe-s-sunflower-shortage-changing-up-food-production/)

### 3d. Incoterms 동적 전환 시뮬레이션 — 설계 스케치 (G3 확장 후보)

**비용·리스크 이전 구조**:
| 조건 | 운임 부담 | 해상 리스크 | 운임 급등기 노출 |
|---|---|---|---|
| **FOB** | 매수인(우리) | 본선 인도 시점부터 매수인 | **직접 노출** — 탱커 스팟 운임 상승분 전액 부담. 단, 자체 COA(장기운송계약) 보유 시 헤지 가능 |
| **CFR/CIF** | 매도인 | 위험은 선적 시 이전, **운임 리스크만 매도인** | 기존 체결분은 보호. 신규 호가에는 매도인이 운임 리스크 프리미엄을 가산 |

**판정 로직 초안** (G3 레짐 신호와 결합):
```
운임 레짐 판별: BDI/BCAA z-score(90일) 기준 — 평시(<1σ) / 상승(1~2σ) / 급등(>2σ)

급등 레짐 진입 시:
  기존 CFR term 계약 → 유지 (운임 상승분이 매도인 부담으로 고정됨)
  신규 계약 → CFR 호가의 운임 프리미엄 vs FOB+스팟운임 실측 비교
              (급등 초기: CFR 호가가 운임 반영에 후행하면 CFR 유리
               급등 지속: 매도인 프리미엄 과다 가산 → FOB+COA 협상 우위)
평시 복귀 시:
  FOB + 운임 직접 계약 → basis·운임 각층 최저가 조합으로 절감
```
- 판정에는 **BCAA(식물성유지 탱커 40,000mt 실측)**가 BDI(드라이벌크)보다 정확한 지표임 — 현재 Perplexity 프록시 수집이라 §5 유료 항목의 1순위 근거.
- Monte Carlo P&L(G3 기존 설계)에 **운임 시나리오 축**을 추가: 가격 경로 × 운임 경로 × 조건(FOB/CFR) 3차원에서 조달 총원가 분포를 산출함.
- 주의: 실제 Incoterms 선택은 매도인 협상·항만 사정 등 비가격 요인이 커, 산출물은 "조건별 기대비용 차이"의 **참고 정보**로 한정하고 HITL 게이트(§6)를 통과시킴.

근거: [Baltic Exchange — BCAA 도입](https://www.balticexchange.com/en/news-and-events/news/press-releases-/2025/Baltic-Exchange-enters-the-Chemical-Tanker-Market-with-New-Chemical-and-Agricultural-Oil-Freight-Assessments.html) · [BCAA 상품 페이지](https://www.balticexchange.com/en/data-services/market-information0/chemical-and-agricultural-oil-assessments-.html) · [EIA — 2022 클린탱커 운임 급등](https://www.eia.gov/todayinenergy/detail.php?id=55039)

---

## §4 시뮬레이션 요건의 G3 반영 계획

1. **G3 output contract 확장(로드맵)**: 기존 `Regime · Confidence · P&L · Buy/Hold`에 **조달 실행 파라미터 권고**(커버리지 개월수 · spot/term 비중 · basis 고정 여부 · FOB/CFR 조건)를 참고 정보로 추가함. 모든 출력은 HITL 게이트 유지(CLAUDE.md §6).
2. **입력 확장**: §3c 파라미터 표를 G3 Monte Carlo의 시나리오 축으로 편입 — 가격(G2 밴드) × 운임(BDI/BCAA 레짐) × 대체유지 스프레드(관세청 9품목 + TE) 3축.
3. **as-of 정합 유지**: 운임·basis·스프레드 피처도 `available_at` 규칙 동일 적용(BCAA 주간 발표 시점 기준 — 미래 정보 누수 금지).
4. **검증**: 2021~22 위기 구간을 stress slice로 사용해 "선매입 권고를 언제 냈을 것인가"를 사후 재현 — 단 as-of 데이터 완비 이후에만 주장 가능함(§2.2).
5. **순서**: G2 Preview(9/10) → G3 기본 레짐 → Incoterms 확장 순. Incoterms 시뮬레이션은 BCAA 실측 확보(§5) 전에는 프록시 기반 프로토타입에 한정함.

---

## §5 지원 필요 항목 (무료/유료)

| 필요 데이터 | 무료 대안 (현황) | 유료 대안 | 우선순위·비고 |
|---|---|---|---|
| ABCD·COFCO·Wilmar 거점/터미널/설비 능력 | USDA FAS **GAIN 보고서**(보유 코퍼스 4,100건) · 기업 연차보고서(ADM/Bunge/LDC/Wilmar IR) · World Grain 보도 | S&P Global Commodity Insights · Fastmarkets 설비 DB | 중 — 무료 조합으로 초기 구축 가능 |
| **FOB/CFR basis 호가** (Gulf·Up River·Santos·CFR 아시아) | 없음 (Perplexity 프록시 — 정밀도 한계) | **S&P Global Platts** 곡물·유지 평가 · **Fastmarkets** Soyoil CFR India(CME 선물 기초) · 물리 브로커 호가 | **상** — §3b 가격 4층 분해의 핵심 결측. CBOT만으로는 조달가 예측 불완전 |
| **식물성유지 탱커 운임 실측** | BDI(TE, 보유 — 드라이벌크라 부정확) · Perplexity BCAA 프록시(보유) | **Baltic Exchange BCAA**(주간, veg oil 40,000mt 기준) 구독 | **상** — §3d Incoterms 판정 로직의 전제 |
| CBOT ZL 정식 시세 | yfinance BO=F(보유 — 429 차단 리스크, A-071) | **Databento** GLBX.MDP3 ZL ohlcv-1d 종량제(C-011 기승인 사양) | 상 — 소액으로 안정성 확보 |
| 위성 작황 | **Sentinel-2/MODIS 직접**(무료) · NASA POWER(보유) · Open-Meteo ERA5-Land 12개 지역(보유) | 새팜·Cropin·EarthDaily·Helios 류 가공 서비스 | 하 — 기후 원천 보유, 가공 위성은 G2 안정화 후 검토 |
| CFTC COT 포지셔닝 | **CFTC 공식 무료**(D-002 이래 미구현 갭) | — | 중 — 무료인데 미수집. 커넥터 추가만 필요 |
| 무역 규격·계약 표준 | **NOPA Trading Rules PDF 무료** · ANEC 무료 | FOSFA 계약서 전문(멤버십) | 하 — 무료로 충분 |
| 한국향 성약·통관 실측 | USDA FAS ESR 한국(보유) · 관세청 GW(보유) | KITA K-stat(무료 가입) 보조 | 완료 수준 — 유지 |
| 결제·선적 관행 검증 (§3b) | — | 물리 브로커·포워더 인터뷰(비용보다 네트워크) | 중 — 조정자 지원 요청 항목 |

---

## 부록 — 본 조사의 한계

- WebSearch 결과 기반이며 lexoeye.io·impactive-ai.com 등 일부 사이트는 직접 열람하지 못함(검색 결과 표기 원칙 준수).
- "Layers" 실체 미확정(§1) — 조정자 재확인 필요.
- §3b 결제 관행·§3d 판정 로직은 공개 자료 + 도메인 추론이 섞여 있음 — 브로커 검증 전 실무 적용 금지.
- 지시문의 "대체유지 16종"·"validated 인과엣지 21건"은 저장소 실자산(9품목 11개 HS·인과 체인 18건)과 달라 실측값으로 정정 기재함.
