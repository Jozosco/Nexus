# 비정형 요약 — 26년 3월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `26년 3월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2026` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 19 |
| 추출 문자 수 | 64,700 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 57 · 하방어 40) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Soil Moisture Percentile, Planted Area, Production Volume, Marketing Year, Soybean, Soybean Oil, Crude Palm Oil, Canola Oil, Neutral Regime, Freight Rate

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 136 March 2026
Contents
InFebruary,wheatpricesfirmedamidadverse
Feature article:
Wheat: 2026 forecasts point to a weather, logistics constraints, and geopoliti-
reduced sown area 2
cal tensions, despite globally ample supplies.
World supply-demand outlook 3
FAO’s initial forecast for 2026 points to a 3
Crop monitor 5
percent production decline due to reduced
Policy developments 8
sowings and a return to average yields, with
International prices 10
cold spells in parts of Europe and dryness in
Futures markets 12
North America posing additional risks. Maize
Market indicators 13
prices remained broadly stable, as strong de-
Fertilizer outlook 15 mand for US supplies offset weaker mar-
Vegetable oils 17 ket conditions in South America. Rice prices
Ocean freight markets 18 were mostly steady amid soft import demand
Explanatory notes 19 and improving supplies across Asia. Soybean
prices rose moderately on tighter US supplies
Markets at a glance
and firmer Argentine markets despite mount-
Easing FROM FROM
Neutral PREVIOUS PREVIOUS
ing trade uncertainty. Escalating conflict in the
Tightening FORECASTS SEASON
WHEAT Near East could further amplify risks to global
MAIZE
agriculture by pushing up energy and fertil-
RICE
izer prices, thereby increasing production and
SOYBEANS
transport costs for farmers worldwide.
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giv

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*