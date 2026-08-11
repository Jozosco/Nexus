# 비정형 요약 — 13년 2월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `13년 2월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2013` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 9 |
| 추출 문자 수 | 17,857 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 21 · 하방어 19) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, World Agricultural Supply and Demand Estimates, Soybean, Bull Regime, Bear Regime, Baltic Dry Index, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market Monitor
Number 5 – February 2013
AMIS Crops: World Supply-Demand Balances in 2012/13
From December to mid-January reduced trade activity and
From previous From previous
optimism over improved supply prospects helped in
month f’cast season (2011/12)
easing international prices. However, prices have risen Wheat
again since mid-January due to concerns over weather in Maize
South America (affecting maize and soybeans) and the US Rice
(wheat). While the early outlook for 2013 remains Soybeans
favourable, weather will be a major determinant of prices
Easing Neutral Tightening
over the coming months.
million tonnes
USDA IGC FAO-AMIS  Wheat production in 2012 fell to below the 2011 record. Early
WHEAT 2011/12 2012/13 2011/12 2012/13 2011/12 2012/13
prospects for 2013 point to a larger crop in spite of a possible decline
est. f'cast est. f'cast est. f'cast
11-Jan 17-Jan 06-Dec 07-Feb in the US production.
Production 696 654 696 656 700 659 662
 Utilization to decline below 2011/12 levels, driven by a 7%
Supply 894 850 890 852 880 843 838
contraction in feed use, mostly in China and the EU.
Utilization 698 673 693 678 697 686 685
 Trade down sharply in 2012/13 on lower imports by several countries
Trade 158 133 145 137 147 136 137
in Africa and Asia. This forecast increased from December on higher
Ending Stocks 196 177 196 174 176 163 159
purchases by China and Iran.
 Stocks (ending 2013) to fall, with a further cut in the forecast this
month reflecting lower inventories in 

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*