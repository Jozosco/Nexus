# 비정형 요약 — 13년 5월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `13년 5월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2013` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 9 |
| 추출 문자 수 | 17,126 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 생산변동, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 20 · 하방어 24) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, EU, Ukraine, Biodiesel Mandate, WASDE Surprise, ENSO Phase

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 생산변동, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market Monitor
Number 8 – May 2013
AMIS Crops: World Supply-Demand Balances in 2012/13
World cereal supply situation is expected to improve in 2013/14
From previous From previous
on higher production and larger than previously projected stocks. month f’cast season (2011/12)
However, unfavorable weather is causing some delays in maize Wheat
plantings in the US and undermining wheat growing conditions in Maize
the US and parts of Europe. The forecast for soybean production Rice
in 2012/13 remains unchanged, with South America leading a Soybeans
marked increase from the previous season.
Easing Neutral Tightening
million tonnes
USDA IGC FAO-AMIS  Wheat production down by 6.0% in 2012 on reduced estimates for
WHEAT 2011/12 2012/13 2011/12 2012/13 2011/12 2012/13
Europe and Black Sea countries.
est. f'cast est. f'cast est. f'cast
10-Apr 25-Apr 11-Apr 09-May  Utilization in 2012/13 to fall from previous season due to a likely
Production 697 655 696 655 702 661 660
reduction in feed use in China and the EU, more than offsetting
Supply 896 855 889 853 887 840 843
record feed use in the US.
Utilization 696 673 692 674 697 684 685
 Trade in 2012/13 adjusted down slightly from the previous month,
Trade 157 136 145 138 147 140 139
now pointing to a 4% contraction from the record in 2011/12.
Ending Stocks 199 182 197 179 183 162 164
 Stocks (ending in 2013) to drop slightly less than previously
anticipated, mostly on higher inventories in Ukraine.
USDA IGC FAO-AMIS  Maize production i

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*