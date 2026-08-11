# 비정형 요약 — 19년 10월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `19년 10월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2019` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 19 |
| 추출 문자 수 | 47,204 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 53 · 하방어 42) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, Ukraine, Korea, ENSO Phase, Rapeseed Oil

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

AMIS Market Monitor No.72 – October 2019 1
Feature article
Towards a more transparent rice market
Although government policies continue to play an translates aspects of voyage costs (such as vessel
influential role in all aspects of the global rice hire rates, fuel costs and port charges) and route
economy, world import demand is also being parameters (such as the distance between the port
driven by population growth and changing dietary of origin and arrival), into a per tonne value
preferences. This is particularly evident in sub- (voyage rate).
Saharan Africa, where a growing number of
consumers are switching away from traditional Utilizing the IGC’s trade database, key routes and
staples and towards rice. While supportive grades of rice have been identified as part of the
government policies could underpin increased tool’s methodological components, for example,
production in sub-Saharan Africa, consumption Nigeria’s preference for parboiled rice and
gains in that region are anticipated to outstrip Senegal’s preference for 100 percent broken rice.
improved production at least for the next five However, challenges remain on identifying parts of
years. The ensuing expansion in African imports the delivered costs, such as charges and loading
will likely raise the region’s food security and rural rates at some key ports.
economy links especially with Asia, at a time when
climatic risks to production may only increase. As Given the need for improved transparency in rice
a cons

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*