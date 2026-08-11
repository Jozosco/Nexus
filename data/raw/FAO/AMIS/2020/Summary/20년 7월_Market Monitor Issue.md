# 비정형 요약 — 20년 7월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `20년 7월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2020` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 18 |
| 추출 문자 수 | 45,182 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 생산변동, 압착, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 49 · 하방어 24) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, Ukraine, Korea, ENSO Phase

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 생산변동, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

AMIS Market Monitor No. 80 – July 2020 1
Feature article
Is there a need to refocus AMIS?
The creation of AMIS in 2011 was the response to a significant part of the population worldwide, with
supply shock. In the years that followed, this unique possible repercussions also for the supply side or
inter-agency platform of international organisations trade.
and members proved its worth by fulfilling its
The consistency, transparency and quality of market
mandate to assess global food supplies (focusing on
information provided by AMIS played an important
wheat, maize, rice and soybeans) and to provide a
role in shaping the global response to the health crisis
platform to coordinate policy action in times of
by providing policy makers and markets with reliable
market uncertainty. Yet, the unique demand shock
and timely data on four main agricultural
stemming from COVID-19 may demonstrate the need
commodities. However, the central role of wheat and
for AMIS to broaden its role.
rice in food as well as maize and soybeans in feed
The world food system has shown its resilience demand make these crops an integral part of a much
during COVID-19, despite the numerous challenges it more complex food system. To capture this
faced, especially in logistics. Resilience of course complexity, AMIS needed to expand beyond its
does not imply absence of problems; on the contrary, regular activities during the exceptional discussions
climate change and the environmental footprint of the related to 

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*