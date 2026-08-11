# 비정형 요약 — 25년 10월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `25년 10월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2025` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 19 |
| 추출 문자 수 | 62,769 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 수출규제, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 51 · 하방어 49) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Planted Area, Production Volume, Marketing Year, Soybean, Canola Oil, Neutral Regime, Trade War, Baltic Dry Index, Freight Rate, US Gulf

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 수출규제, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 132 October 2025
Contents
In October, wheat harvesting wraps up and
Feature article:
Low-carbon ammonia 2 the harvesting of maize and soybeans begins
World supply-demand outlook 3 acrossthenorthernhemisphere.Inthesouth-
Crop monitor 5 ern hemisphere, wheat crop is developing,
Policy developments 8 and farmers are starting to plant maize and
soybeans. Rice harvests are ongoing in China
International prices 10
and Southeast Asia. Overall, crop prospects
Futures markets 12
are good. In September, wheat, maize, and
Market indicators 13
rice prices generally declined, owing to ample
Fertilizer outlook 15
supplies and strong competition among ex-
Vegetable oils 17
porters. However, soybean prices stayed firm
Ocean freight markets 18
in Brazil and the United States, balancing out
Explanatory notes 19
price drops in Argentina caused by changes
in export taxes. Despite these positive trends,
Markets at a glance
ongoing trade tensions have triggered adjust-
Easing FROM FROM
Neutral PREVIOUS PREVIOUS
ments in trade flows of some commodities,
Tightening FORECASTS SEASON
WHEAT with potential implications on farmers' mar-
MAIZE
gins in producing countries and consequently
RICE
future planting decisions.
SOYBEANS
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy and other market drivers behind them. The anal

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*