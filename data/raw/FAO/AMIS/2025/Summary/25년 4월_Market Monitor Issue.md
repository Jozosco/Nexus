# 비정형 요약 — 25년 4월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `25년 4월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2025` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 20 |
| 추출 문자 수 | 64,919 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 수출규제, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 55 · 하방어 52) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, Ukraine, Export Tax, ENSO Phase, Palm Oil, Sunflower Oil, Rapeseed Oil

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 수출규제, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 127 April 2025
Contents
Winter wheat crops in the northern hemi-
Feature article:
Trade policy uncertainty 2 spherearebreakingdormancy,andmaizeand
World supply-demand outlook 3 soybean harvesting continues in the southern
Crop monitor 5 hemisphere. In March 2025, average grains
Policy developments 8 andsoybeansexportpricesexhibitedamostly
weaker tone, attributed to easing concerns
International prices 11
about crop conditions in major producing
Futures markets 13
countries and geopolitical developments, in-
Market indicators 14
cludingescalatinginternationaltradetensions.
Fertilizer outlook 16
These tensions and trade policy changes cre-
Vegetable oils 18
ate uncertainties for producers, traders, and
Ocean freight markets 19
consumers; risk retaliatory measures; and af-
Explanatory notes 20
fect markets with implications for food secu-
rity. Well-functioning markets are crucial for
Markets at a glance
meeting food demand and ensuring access.
Easing FROM FROM
Neutral PREVIOUS PREVIOUS
As in past episodes of volatility and uncer-
Tightening FORECASTS SEASON
WHEAT tainty, AMIS strives to maintain and improve
MAIZE
transparencyand easeaccess toinformation,
RICE
benefiting market actors and policy-makers
SOYBEANS
alike.
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy and other market drivers behi

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*