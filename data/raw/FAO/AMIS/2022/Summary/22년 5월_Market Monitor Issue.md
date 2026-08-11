# 비정형 요약 — 22년 5월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `22년 5월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2022` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 18 |
| 추출 문자 수 | 93,833 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 수입관세, 수출규제, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 54 · 하방어 33) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, EU, Ukraine, Export Tax, ENSO Phase, Palm Oil, Sunflower Oil, Rapeseed Oil

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 수입관세, 수출규제, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 98 May 2022
Spring planting in the Northern Hemisphere
Contents
isunderwayamidhighcommoditypricesbut
Feature article:
AMIS efforts to monitor export high input costs as well. Early indications for
restrictions 2
the United States and the European Union
World supply-demand outlook 3
suggest that higher prices for soybeans and
Crop monitor 5
other oilseeds will encourage producers to
Policy developments 8
increase oilseed plantings. For wheat, in-
International prices 11
creased acreage in Canada might help fill
Futures markets 13 some of the global deficit in supplies. How-
Market indicators 14 ever, the outlook is less favourable for India
Fertilizer outlook 16 andtheUnitedStates.Duetothetightnessin
global stocks and the uncertainty caused by
Ocean freight markets 17
the conflict in Ukraine, price volatility is likely
Explanatory notes 18
toremainhighthisyearasmarketswillfocus
Markets at a glance
on weather, crop conditions of fall-planted
FROM FROM
Easing
Neutral PREVIOUS PREVIOUS
Tightening FORECASTS SEASON wheat and progress for spring planting and
WHEAT development later this summer. Of increas-
MAIZE
ingconcernareexportrestrictions,whichfur-
RICE
therexacerbatepricevolatilityandjeopardize
SOYBEANS
global supplies.
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy and other market drivers 

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*