# 비정형 요약 — 26년 7월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `26년 7월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2026` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 19 |
| 추출 문자 수 | 63,712 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 수입관세, 수출규제, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 54 · 하방어 62) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Planted Area, Soybean, Crude Palm Oil, Canola Oil, Bear Regime, Neutral Regime, Geopolitical Conflict, Freight Rate, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 수입관세, 수출규제, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 140 July 2026
Contents
Agricultural markets are moving through
Feature article:
Modelling the impact of the Hormuz a generally steady period, supported by
crisis on agricultural markets 2
favourable conditions across AMIS crops.
World supply-demand outlook 3
Seasonal progress has been broadly encour-
Crop monitor 5
aging, although pockets of dryness and the
Policy developments 8
emergence of El Niño are beginning to shape
International prices 10
expectations. Policy developments continue
Futures markets 12
influencing market dynamics, with adjust-
Market indicators 13
ments to trade measures and domestic sup-
Fertilizer outlook 15 port. Fertilizer markets have shown signs of
Vegetable oils 17 easing, as improved flows through the Strait
Ocean freight markets 18 of Hormuz and softer energy prices have re-
Explanatory notes 19 ducedsupplypressures.Whilefertilizerafford-
ability improved in some regions, it remains
Markets at a glance
a constraint in others. Against this back-
Easing FROM FROM
Neutral PREVIOUS PREVIOUS
drop, staple food commodity prices show
Tightening FORECASTS SEASON
WHEAT mixed movements, with harvest pressure in
MAIZE
the northern hemisphere and ample supply
RICE
prospects balancing localized tightness, leav-
SOYBEANS
ing sentiment cautious but broadly stable.
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major 

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*