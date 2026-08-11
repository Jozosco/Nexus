# 비정형 요약 — 24년 4월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `24년 4월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2024` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 17 |
| 추출 문자 수 | 55,603 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 수출규제, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 42 · 하방어 34) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, Ukraine, Export Tax, Palm Oil

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 수출규제, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 117 April 2024
Theeasingofmaizeandwheatexportprices
Contents
is helping to mitigate rising freight and in-
Feature article:
Trading in Agriculture After the WTO's surance costs associated with shipping dis-
Ministerial Conference 2
ruptions for importers. Conversely, farmers
World supply-demand outlook 3
have adapted to reduced profit margins by
Crop monitor 5
transitioning to alternative crops. As a result,
Policy developments 8
winter wheat plantings for harvest in 2024
International prices 10
decreased in Ukraine (areas under Govern-
Futures markets 12 ment control), and the United States. Spring
Market indicators 13 plantingsmightmakeupthedeclineinsome
Fertilizer outlook 15 countries. Similarly, there is a likelihood of
a shift away from maize toward soybeans,
Ocean freight markets 16
made more attractive by increasing crude
Explanatory notes 17
oil prices which improve prospects for bio-
Markets at a glance
fuels demand. Although overall crop condi-
Easing FROM FROM
Neutral PREVIOUS PREVIOUS
tions at the end of March do not raise alarm,
Tightening FORECASTS SEASON
WHEAT market-driven adjustments to planting areas
MAIZE
could impact sentiment on the global mar-
RICE
kets should significant weather events occur
SOYBEANS
during the rest of the season.
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and t

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*