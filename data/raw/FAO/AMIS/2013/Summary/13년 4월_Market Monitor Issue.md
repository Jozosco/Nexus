# 비정형 요약 — 13년 4월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `13년 4월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2013` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 9 |
| 추출 문자 수 | 16,522 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 물류충격, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 23 · 하방어 26) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Soybean, Bull Regime, Neutral Regime, Baltic Dry Index, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 물류충격, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market Monitor
Number 7 – April 2013
AMIS Crops: World Supply-Demand Balances in 2012/13
The market focus is shifting to the outcome of harvests in 2013
From previous From previous
which will determine the supply outlook for the 2013/14 season.
month f’cast season (2011/12)
Favourable prospects for all AMIS crops have set the stage for Wheat
weaker world prices, barring any unfavourable weather in major Maize
producing regions in the coming months. Recent reports from the Rice
USDA indicating the largest planned maize area since 1936 and Soybeans
higher than expected quarterly stocks, contributed to a pronounced
Easing Neutral Tightening
decline in grain prices*.
million tonnes
USDA IGC FAO-AMIS  Wheat production estimates in 2012, now firmer, pointing to a 5.6%
WHEAT 2011/12 2012/13 2011/12 2012/13 2011/12 2012/13
contraction from 2011, driven by lower crops in Europe.
est. f'cast est. f'cast est. f'cast
10-Apr 21-Mar 07-Mar 11-Apr  Utilization to decline in 2012/13, reflecting reductions in the EU,
Production 697 655 696 656 701 662 661
China and the CIS, mostly for feed.
Supply 896 855 889 853 881 840 840
 Trade in 2012/13 to contract, in spite of recent upward adjustments
Utilization 696 673 692 676 696 683 684
to imports by the CIS, EU and Iran
Trade 157 136 145 138 147 139 140
 Stocks (ending in 2013) falling, mainly on large drawdowns in Europe.
Ending Stocks 199 182 197 177 179 163 162
 Maize production in 2012 falling by 1.7%, as reductions in the US and
USDA IG

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*