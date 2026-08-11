# 비정형 요약 — 26년 5월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `26년 5월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2026` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 19 |
| 추출 문자 수 | 65,322 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 수입관세, 압착, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 75 · 하방어 29) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Planted Area, Production Volume, Marketing Year, Soybean, Crude Palm Oil, Canola Oil, Bull Regime, Neutral Regime, Hold Recommendation, Geopolitical Conflict

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 수입관세, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 138 May 2026
Contents
Global markets faced renewed pressures in
Feature article:
Hormuz shock and fertilizer markets 2 April as the effective closure of the Strait of
World supply-demand outlook 3 Hormuz continued to disrupt fertilizer supply,
Crop monitor 5 pushing urea and phosphate prices higher
Policy developments 8 and further eroding fertilizer affordability. Sup-
ply chain disruptions, combined with higher
International prices 10
energyandlogisticscosts,intensifiedproduc-
Futures markets 12
tionchallenges.Policyresponsesincludedex-
Market indicators 13
portrestrictionsonkeyfertilizerinputs,revised
Fertilizer outlook 15
trade measures, and adjustments to biofuel
Vegetable oils 17
mandates. Against this backdrop, crop con-
Ocean freight markets 18
ditions remained broadly favourable: wheat
Explanatory notes 19
and maize benefited from generally good
weather although rainfall is needed in some
Markets at a glance
parts, rice harvests progressed across Asia
Easing FROM FROM
Neutral PREVIOUS PREVIOUS
and South America, and soybean harvest-
Tightening FORECASTS SEASON
WHEAT ing in the southern hemisphere advanced.
MAIZE
However, rising input costs highlight growing
RICE
risks for future agricultural production, includ-
SOYBEANS
ing shifting area to less input-intensive crops.
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major m

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*