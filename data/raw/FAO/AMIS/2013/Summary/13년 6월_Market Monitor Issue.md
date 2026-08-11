# 비정형 요약 — 13년 6월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `13년 6월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2013` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 8 |
| 추출 문자 수 | 16,097 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 수출규제, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 22 · 하방어 10) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, Ukraine, Korea, Import Duty, Biodiesel Mandate, WASDE Surprise, ENSO Phase

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 수출규제, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market Monitor
Number 9 – June 2013
AMIS Crops: World Supply-Demand Outlook
First forecasts for 2013/14 marketing seasons
Early indications for world wheat, maize and rice production in 2013 point to record levels and
From previous season
an overall increase in supplies in the new 2013/14 marketing season. The recovery in maize Wheat
supplies is expected to help replenish maize inventories to more comfortable levels. Also for Maize
soybeans, early forecasts for the next season point to a further expansion in global production, Rice
which, combined with subdued consumption growth, could permit a recovery in global stock Soybeans
levels. Easing Neutral Tightening
million tonnes
USDA IGC FAO-AMIS  Wheat production in 2013 to hit a record, up 6.5% from 2012, mostly
WHEAT 2012/13 2013/142012/13 2013/14 2012/13 2013/14
est. f'cast est. f'cast est. f'cast on expectation of a rebound in Europe and Black Sea region
10-May 31-May 06-Jun  Utilization in 2013/14 to increase by 1.1% with feed use returning to
Production 656 701 655 682 659 702
more normal levels while food consumption keeps pace with the
Supply 855 881 852 860 842 866
population growth
Utilization 675 695 674 680 686 694  Trade in 2013/14 to contract by 2.5%, largely reflecting reduced
Trade 137 143 139 137 140 136
purchases in Asia and Europe because of higher domestic production
Ending Stocks 180 186 178 180 164 173
 Stocks (ending in 2014) to rebound by 5.4% with most of the increase
projected in China, the EU and 

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*