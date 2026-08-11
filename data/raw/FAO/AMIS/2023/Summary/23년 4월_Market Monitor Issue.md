# 비정형 요약 — 23년 4월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `23년 4월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2023` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 17 |
| 추출 문자 수 | 89,451 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 수출규제, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 40 · 하방어 52) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Inflation, Export Volume, Flood, Planted Area, Soybean, Neutral Regime, Geopolitical Conflict, Freight Rate, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 수출규제, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 107 April 2023
Over the past 10 months, world prices of
Contents
most grains and oilseeds have fallen back to
Feature article:
Renewal of the Black Sea Grain levels prior to the war in Ukraine. Likewise,
Initiative 2
volatilityinpriceshasalsodeclinedconsider-
World supply-demand outlook 3
ably from recent highs. With the extension of
Crop monitor 5
the Black Sea Grain Initiative, there is hope
Policy developments 8
that the world is recovering from the price
International prices 10
shocks of the past year. Yet, while prices
Futures markets 12 havefallenininternationalmarkets,theyhave
Market indicators 13 frequently remained high at local level, par-
Fertilizer outlook 15 ticularly in net food importing developping
countries reflecting the weakening of their
Ocean freight markets 16
currencies against the US dollar. As a result,
Explanatory notes 17
food price inflation is still a serious concern
Markets at a glance
in many countries, also because post-farm
FROM FROM
Easing
Neutral PREVIOUS PREVIOUS
Tightening FORECASTS SEASON gate costs for shipping and processing re-
WHEAT main subject to inflationary pressures.
MAIZE
RICE
SOYBEANS
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy and other market drivers behind them. The analysis is a collective
assessmentofthemarketsituationandoutlookbythet

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*