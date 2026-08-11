# 비정형 요약 — 24년 9월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `24년 9월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2024` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 20 |
| 추출 문자 수 | 67,383 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 수출규제, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 44 · 하방어 57) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Soil Moisture Percentile, Planted Area, Production Volume, Marketing Year, Soybean, Canola Oil, Bear Regime, Neutral Regime, Freight Rate, Subsidy

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 수출규제, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 121 September 2024
Contents
With 2024 likely to rank among the warmest
Feature article:
Resilience of fertilizer markets 2 years on record, weather continued to dom-
World supply-demand outlook 3 inate commodity market news in recent
Crop monitor 5 weeks, in both positive and negative ways.
Policy developments 8 While the forecast for 2024 global maize
output was trimmed as heat constrained
International prices 11
yields in parts of the European Union, Mex-
Futures markets 13
ico and Ukraine, global soybean production
Market indicators 14
forecast was lifted on account of favourable
Fertilizer outlook 16
weather in the United States. Crossings in
Vegetable oils 18
the Panama Canal are approaching their
Ocean freight markets 19
usuallevels,whileshipping disruptionsinthe
Explanatory notes 20
RedSeacontinue.Thecurrenteditionbroad-
ens the coverage of developments in the fer-
Markets at a glance
tilizermarketsandintroducesnewindicators.
Easing FROM FROM
Neutral PREVIOUS PREVIOUS
Although easing from their peaks, fertilizer
Tightening FORECASTS SEASON
WHEAT costindicesandfertilizercroppriceratiosre-
MAIZE
mained above their 2019 average in almost
RICE
allregions.Apageonvegetableoilswasalso
SOYBEANS
added,coveringmainmarketdevelopments.
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy and other mar

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*