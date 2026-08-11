# 비정형 요약 — 13년 3월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `13년 3월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2013` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 9 |
| 추출 문자 수 | 18,094 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 물류충격, 바이오연료수요, 수입관세, 압착, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 22 · 하방어 16) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, EU, Ukraine, Import Duty, Biodiesel Mandate, WASDE Surprise

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 물류충격, 바이오연료수요, 수입관세, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market Monitor
Number 6 – March 2013
AMIS Crops: World Supply-Demand Balances in 2012/13
In recent weeks wheat and maize crops benefitted from
From previous From previous
generally positive weather conditions, improving the month f’cast season (2011/12)
prospects for the US wheat and the first maize crops in Wheat
southern America, to be harvested soon. While the outlook Maize
for soybeans in South America deteriorated slightly, early Rice
prospects are still encouraging given larger plantings. Rice Soybeans
markets remain well supplied while expectations for the
Easing Neutral Tightening
2013 crops in Asia and South America are so far positive.
million tonnes
USDA IGC FAO-AMIS  Wheat production in 2012 fell below the record in 2011 but
WHEAT 2011/12 2012/13 2011/12 2012/13 2011/12 2012/13
favourable returns combined with generally good weather likely to
est. f'cast est. f'cast est. f'cast
08-Feb 21-Feb 07-Feb 07-Mar lead to a rebound in 2013.
Production 697 654 696 656 700 662 662
 Utilization to decline in 2012/13, largely on reduced usage for animal
Supply 895 850 890 853 880 838 840
feed purposes.
Utilization 698 673 693 677 696 685 683
 Trade in 2012/13 to reach a higher level than previously forecast due
Trade 157 132 145 137 147 137 139
to larger imports by the CIS countries.
Ending Stocks 197 177 197 176 178 159 163
 Stocks (ending 2013) to decrease less than anticipated in February,
reflecting upward revisions in Russia and Ukraine.
USDA IGC FAO-AMIS  Maize prod

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*