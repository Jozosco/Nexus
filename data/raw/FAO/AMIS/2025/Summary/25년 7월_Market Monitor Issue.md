# 비정형 요약 — 25년 7월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `25년 7월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2025` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 19 |
| 추출 문자 수 | 61,445 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 수출규제, 압착, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 73 · 하방어 39) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, EU, Ukraine, Export Tax, Black Sea Corridor, WASDE Surprise, ENSO Phase, Sunflower Oil

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 수출규제, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 130 July 2025
Contents
GlobalwheatpricesedgedupslightlyinJune,
Feature article:
Strategic grain reserves 2 despite seasonal harvest pressure. Maize
World supply-demand outlook 3 prices declined, driven by favourable crop
Crop monitor 5 conditionsintheUnitedStatesandstrongex-
Policy developments 8 port competition from South America. Rice
pricesfellamidsubduedglobaldemand.Soy-
International prices 10
bean prices rose, supported by firm demand.
Futures markets 12
Meanwhile, the EU reinstated import quotas
Market indicators 13
on Ukrainian grain, and India continued its
Fertilizer outlook 15
wheat export ban. Fertilizer markets also ex-
Vegetable oils 17
perienced volatility, largely due to instability in
Ocean freight markets 18
the Near East. Current forecasts suggest a
Explanatory notes 19
comfortable global supply outlook for AMIS
crops. However, heatwaves affecting parts of
Markets at a glance
Europe, India, and the United States could
Easing FROM FROM
Neutral PREVIOUS PREVIOUS
constrain the yield potential, particularly of
Tightening FORECASTS SEASON
WHEAT maize. While weather-related uncertainty re-
MAIZE
mains a constant feature of agricultural mar-
RICE
kets, its impacts are now compounded by
SOYBEANS
trade policy shifts and geopolitical tensions.
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and t

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*