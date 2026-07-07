# P1-05 뉴스·감성 시맨틱 레이어 설계 (Semantic Layer)

**작성일**: 2026-07-01 · **대상 역할**: `.claude/agents/p105-news-sentiment.md` (News & Sentiment Analyst)  
**참여**: P1-05(주도) · C-02(시장조사) · C-03(데이터) · C-04(문서 인텔) · P1-01~04  
**목적**: 현재 수집 중인 비정형 데이터(기사·리포트)에서 **핵심 키워드를 선별**해 LLM이 일관되게
소비하는 **시맨틱 레이어**를 구축하여 `SOYBEAN_OIL_SENTIMENT_SCORE`·`NEWS_POLICY_FLAG` 산출의
정밀도·재현성을 높인다.

**참조**
- arXiv 2503.07584 *Talking to GDELT Through Knowledge Graphs* — GDELT 뉴스에 대한 지식그래프 RAG
  (벡터스토어 RAG vs LLM 지식그래프 구축+서브그래프 검색 비교). P1-05 상류 입력이 GDELT라 직접 적용.
- "Building a Semantic Layer for LLMs — Five Types" (Medium, visrow) — 시맨틱 레이어 5유형 프레임.
- arXiv 2604.25149 — **본 환경에서 조회 불가(미래 게시일/접근 403)**. 확보 시 반영 예정.

---

## 1. 시맨틱 레이어 5유형 → P1-05 매핑

| 유형 | 정의 | P1-05 적용 | 산출물 |
|---|---|---|---|
| ① Metrics(지표) 레이어 | 비즈니스 지표의 표준 정의 | 감성 지표 정의 표준화(`SBO_NEWS_SENTIMENT` 등 6종, 범위 −1~+1) | `semantic/metrics.yaml` |
| ② Ontology/지식그래프 | 엔티티+관계 그래프 | 국가·정책·상품·기업 엔티티와 "수출세→공급→가격" 관계 그래프(arXiv 2503.07584 방식) | `semantic/ontology.yaml` |
| ③ Entity/Dimension | 정규 엔티티+동의어 | "Argentina/아르헨티나/ARG", "B35/biodiesel mandate" 동의어 사전 | `semantic/entities.yaml` |
| ④ Query/Translation | 자연어→구조화 질의 | Perplexity 쿼리 템플릿 ↔ indicator_code 매핑(카테고리별) | `semantic/query_templates.yaml` |
| ⑤ Retrieval/Embedding | 벡터/RAG 검색 | GAIN PDF·기사 임베딩 → 서브그래프/청크 검색(FinBERT 전처리) | `semantic/retrieval.md` |

> **핵심(arXiv 2503.07584 시사점)**: 순수 벡터 RAG보다 **지식그래프 기반 서브그래프 검색**이
> 다단계 인과("엘니뇨→감산→압착↓→SBO↑") 질의에서 우수. P1-05는 ②+⑤ 하이브리드를 채택한다.

---

## 2. 키워드 → 시맨틱 엔티티 선별 (semantic keyword layer)

현재 수집 비정형 소스(GAIN PDF·GDELT·Perplexity)에서 다음 **엔티티 클래스**로 키워드를 구조화한다.
(원천: `keywords_geopolitical_biodiesel_sources.md` 확장)

### 2.1 엔티티 클래스와 대표 키워드
| 엔티티 클래스 | 정규 엔티티 | 동의어/변형(키워드) | 연결 지표 |
|---|---|---|---|
| 국가/주체 | Argentina | Argentina, 아르헨티나, ARG, retenciones | `ARG_EXPORT_TAX_SENTIMENT` |
| 정책 이벤트 | Export Tax | export tax/duty/ban, 수출세, retención | ↑ |
| 정책 이벤트 | Biodiesel Mandate | B35, B40, RVO, RED III, blending mandate | `BIODIESEL_POLICY_SENTIMENT` |
| 무역 조치 | Import Duty | import duty/tariff, 수입관세, MFN | `INDIA_DUTY_SENTIMENT` |
| 지정학 | Shipping Chokepoint | Red Sea, Houthi, Hormuz, Suez, 흑해 | `SBO_STRAIT_RISK`(P1-04 연계) |
| 수급 이벤트 | WASDE Surprise | WASDE, ending stocks, consensus, surprise | `WASDE_CONSENSUS_SCORE` |
| 기상 | ENSO Phase | El Niño, La Niña, drought, 가뭄 | `ENSO_ONI`(P1-03 연계) |
| 대체재 | Palm/Sunflower | CPO, palm oil, sunflower oil, spread | `CPO_SBO_SPREAD`(P1-01 연계) |

### 2.2 선별 규칙 (C-02·P1-05)
1. **빈도×영향도**: GDELT 톤·언급빈도 상위 + P1-01~04 도메인 영향도 가중 → 상위 키워드 유지.
2. **동의어 병합**: 표기 변형을 정규 엔티티로 정규화(다국어 포함) → 중복 신호 제거.
3. **관계 부여**: 각 엔티티를 인과 그래프의 노드로 등록, "원인→메커니즘→가격방향" 엣지 연결.
4. **폐기 기준**: 3개월 무언급 + 영향도 하위 → 후보 강등(완전 삭제 아님, 재출현 대비).

---

## 3. 산출 구조 (repo 반영 제안)

```
src/semantic/                     # (신설 제안)
├── metrics.yaml                  # ① 감성 지표 정의(코드·범위·단위)
├── ontology.yaml                 # ② 엔티티+인과 관계(그래프 시드)
├── entities.yaml                 # ③ 정규 엔티티↔동의어 사전(다국어)
├── query_templates.yaml          # ④ 카테고리별 Perplexity 쿼리↔indicator_code
└── retrieval.md                  # ⑤ 임베딩·서브그래프 검색 절차(FinBERT 연계)
```

- **Phase A(현재)**: ①③④를 우선 구축(정적 사전·템플릿). Perplexity 쿼리에 동의어·도메인 필터 주입.
- **Phase A+(권장)**: ②⑤ 도입 — GAIN PDF·GDELT를 지식그래프화(arXiv 2503.07584), 서브그래프 검색으로
  다단계 인과 질의 지원. FinBERT 감성 점수를 노드 속성으로 부착.
- **내부 데이터 제외(D-021)**: 감성 레이어도 외부 소스 전용. 내부 텍스트 미투입.

---

## 4. P1-05 역할 강화 효과

| 강화 포인트 | Before | After(시맨틱 레이어) |
|---|---|---|
| 신호 일관성 | 쿼리별 표기 변동 | 정규 엔티티로 통일 → 재현성↑ |
| 인과 해석 | 단건 감성 점수 | 지식그래프 경로로 "왜"까지 설명(해석가능성 요구 충족) |
| 커버리지 | 키워드 하드코딩 | 동의어·다국어 확장 → 누락↓ |
| 다운스트림 | G2 exogenous 단일값 | 엔티티별 감성 + 정책 플래그 다차원 |

---

## 5. 확정 요청
1. `src/semantic/` 신설 + ①③④ 정적 레이어 우선 구축 승인.
2. ②⑤ 지식그래프·RAG(arXiv 2503.07584 방식) 도입 시점(Phase A+ vs G2 착수 후) 지정.
3. arXiv 2604.25149 원문 공유 가능 여부(현재 접근 불가) — 확보 시 설계 보강.

*참고: [arXiv 2503.07584 Talking to GDELT Through Knowledge Graphs](https://arxiv.org/abs/2503.07584)*
