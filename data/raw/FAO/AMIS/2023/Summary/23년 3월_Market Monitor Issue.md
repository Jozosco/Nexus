# 비정형 요약 — 23년 3월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `23년 3월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2023` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 16 |
| 추출 문자 수 | 83,965 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 41 · 하방어 38) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Export Volume, Soil Moisture Percentile, Production Volume, Soybean, Crude Palm Oil, Bear Regime, Neutral Regime, Geopolitical Conflict, Freight Rate, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 106 March 2023
With no end in sight to the war in Ukraine
Contents
and threats of further escalation, uncer-
Feature article:
Ukraine One Year After 2 tainty continues to hang over agricultural
World supply-demand outlook 3 markets. Supplies are tight. Reduced plant-
ings in Ukraine mean that other countries
Crop monitor 5
will need to produce additional grains and
Policy developments 8
oilseeds to help rebuild global stocks and
International prices 9
moderate price levels. The world has so far
Futures markets 11
been relatively fortunate: a combination of
Market indicators 12
good weather and strong producer supply
Fertilizer outlook 14
response has kept market prices from re-
Ocean freight markets 15
bounding back to the high levels of early
Explanatory notes 16
2022. However, tight stocks will mean in-
creasedpricevolatility,particularlyduringpe-
Markets at a glance
riods of uncertainty such as planting times
FROM FROM
Easing
Neutral PREVIOUS PREVIOUS
Tightening FORECASTS SEASON and the Northern Hemisphere growing sea-
WHEAT sons.Inaddition,uncertaintyovereventslike
MAIZE
the renewal of the Black Sea Grain Initiative
RICE
will continue to roil markets.
SOYBEANS
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy and other market drivers behind them. The analysis is a collective
assessmentofth

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*