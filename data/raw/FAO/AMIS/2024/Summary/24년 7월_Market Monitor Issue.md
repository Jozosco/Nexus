# 비정형 요약 — 24년 7월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `24년 7월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2024` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 17 |
| 추출 문자 수 | 57,012 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 수출규제, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 38 · 하방어 43) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Heatwave, Soil Moisture Percentile, Planted Area, Marketing Year, Soybean, Canola Oil, Neutral Regime, Geopolitical Conflict, Freight Rate, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 수출규제, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 120 July 2024
Contents
Wheat prices are ebbing under the har-
Feature article:
Price insulation policies 2
vest pressure from the northern hemisphere.
World supply-demand outlook 3 Freshsuppliesfromthesouthernhemisphere
Crop monitor 5 aredoingthesameformaizeprices,evenas
Policy developments 8 harvests in Argentina and Brazil are likely to
International prices 10 fall short of expectations. Exceptionally wet
Futures markets 12 weatherinpartsoftheEuropeanUnioncould
Market indicators 13 bring up quality concerns for wheat. May
Fertilizer outlook 15 2024 was the 12th consecutive month of
Ocean freight markets 16 record-breakingglobaltemperatures.Should
this trend persist, there will likely be neg-
Explanatory notes 17
ative impacts on agriculture from extreme
heat, particularly if heat occurs during peri-
Markets at a glance ods of moisture stress or the key reproduc-
Easing FROM FROM tive stages that determine final yields.
Neutral PREVIOUS PREVIOUS
Tightening FORECASTS SEASON
WHEAT AMIS Market Monitor will return with fresh
MAIZE
features and on a new publication schedule
RICE
on Friday, 6 September.
SOYBEANS
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy and other market drivers behind them. The analysis is a collective
assessmentofthemarketsituationandoutlookbytheteninternationalorganizatio

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*