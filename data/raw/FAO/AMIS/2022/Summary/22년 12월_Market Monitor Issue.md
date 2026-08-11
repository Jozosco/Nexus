# 비정형 요약 — 22년 12월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `22년 12월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2022` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 18 |
| 추출 문자 수 | 92,825 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 수입관세, 재고 |
| 방향성(SBO 가격 기준) | 하방 우세 (상방어 31 · 하방어 45) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Heatwave, Soil Moisture Percentile, Planted Area, Soybean, Spot Price, Crude Palm Oil, Neutral Regime, Geopolitical Conflict, Baltic Dry Index, Freight Rate

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 수입관세, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 104 December 2022
With northern hemisphere grain and oilseed
Contents
crops largely harvested, and the Black Sea
Feature article:
Is Speculation Driving Commodity Grain Initiative extended for another 120
Price Volatility? 2
days, market attention is shifting to grow-
World supply-demand outlook 3
ing conditions in the southern hemisphere.
Crop monitor 5
The third consecutive year of La Niña has
Policy developments 8
prolonged drought conditions in Argentina,
International prices 11
resulting in sharply reduced wheat produc-
Futures markets 13 tion prospects relative to last year. By con-
Market indicators 14 trast, La Niña has resulted in abnormally wet
Fertilizer outlook 16 conditionsinAustralia,whichexpectsabove-
averagewheatyields;however,concernsre-
Ocean freight markets 17
main over the quality of the crop, which
Explanatory notes 18
could impact prices for milling wheat. Plant-
Markets at a glance
ing progress for South American maize and
FROM FROM
Easing
Neutral PREVIOUS PREVIOUS
Tightening FORECASTS SEASON soybeans are on pace, but it is still too early
WHEAT to tell whether yields will return to more nor-
MAIZE
mal levels after last year's drought-reduced
RICE
production.
SOYBEANS
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy and other market drivers behind them. The analysis is 

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*