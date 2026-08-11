# 비정형 요약 — 25년 9월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `25년 9월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2025` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 20 |
| 추출 문자 수 | 68,798 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 수입관세, 수출규제, 압착, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 77 · 하방어 57) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Planted Area, Marketing Year, Soybean, Crude Palm Oil, Canola Oil, Bear Regime, Geopolitical Conflict, Freight Rate, Import Tariff, Export Tax

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 수입관세, 수출규제, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 131 September 2025
Contents
In August, wheat and rice export prices
Feature article:
Agricultural Outlook 2025-2034 2 dropped to their lowest levels in years, largely
World supply-demand outlook 3 duetoabundantglobalsuppliesandweakde-
Crop monitor 5 mand. Meanwhile, maize and soybean prices
Policy developments 8 found support from higher export premiums
and robust international buying interest. Veg-
International prices 11
etable oil prices remained strong, because of
Futures markets 13
increased palm oil quotes driven by steady
Market indicators 14
global import needs. Nitrogen fertilizer prices
Fertilizer outlook 16
climbed, especially with strong demand from
Vegetable oils 18
India during what is usually a quiet season,
Ocean freight markets 19
while prices for phosphorus and potassium
Explanatory notes 20
fertilizers stayed mostly steady. However, fer-
tilizer is becoming less affordable compared
Markets at a glance
to crop prices in many regions, which could
Easing FROM FROM
Neutral PREVIOUS PREVIOUS
lead farmers to adjust their application rates.
Tightening FORECASTS SEASON
WHEAT Although the outlook for AMIS commodities
MAIZE
remainsgenerallypositive,ongoinguncertain-
RICE
ties in trade and biofuel policies continue to
SOYBEANS
pose risks for market participants.
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market d

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*