# 비정형 요약 — 22년 11월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `22년 11월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2022` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 17 |
| 추출 문자 수 | 87,333 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 36 · 하방어 41) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Soybean, Neutral Regime, Geopolitical Conflict, Freight Rate, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 103 November 2022
Concerns are mounting regarding the exten-
Contents
sion of the United Nations Black Sea Grain
Feature article:
Black Sea Grain Initiative 2 Initiative beyond the 18 November dead-
World supply-demand outlook 3 line, especially after Russia's recent - al-
beit temporary - withdrawal from the agree-
Crop monitor 5
ment. Through this initiative, Ukraine has
Policy developments 8
been able to ship over 9 million tonnes
International prices 10
of grains and oilseeds via its Black Sea
Futures markets 12
ports. While the volume of exports remains
Market indicators 13
below year-ago levels, importers benefitted
Fertilizer outlook 15
from larger supplies, especially those who
Ocean freight markets 16
depend on Ukraine's agricultural products,
Explanatory notes 17
while consumers worldwide have gained
through lower market prices. Unfortunately,
Markets at a glance
the pace of exports slowed in recent weeks
FROM FROM
Easing
Neutral PREVIOUS PREVIOUS
Tightening FORECASTS SEASON as inspections could not keep up with the
WHEAT number of shipments; and now the possible
MAIZE
termination of the deal threatens to re-ignite
RICE
market prices and further exacerbate global
SOYBEANS
food security concerns.
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy and other market drivers behind them. T

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*