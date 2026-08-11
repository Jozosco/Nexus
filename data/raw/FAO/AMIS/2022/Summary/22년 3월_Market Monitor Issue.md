# 비정형 요약 — 22년 3월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `22년 3월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2022` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 16 |
| 추출 문자 수 | 84,221 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 수출규제, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 46 · 하방어 24) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Inflation, Import Volume, Export Volume, Planted Area, Production Volume, Soybean, Neutral Regime, Freight Rate, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 수출규제, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 96 March 2022
The events currently unfolding in Ukraine
Contents
have sent shockwaves through global mar-
Feature article:
The Ukraine conflict and global food kets. The crisis comes at a moment when
price scares 2
food markets are already struggling with
World supply-demand outlook 3
soaring prices and the fallout from the
Crop monitor 5
COVID-19 pandemic. While AMIS supply
Policy developments 8
and demand forecasts are little changed
International prices 9
compared to February expectations, condi-
Futures markets 11 tions are evolving rapidly. The AMIS Secre-
Market indicators 12 tariat will continue monitoring developments
Fertilizer outlook 14 closely and work with its partners to help
minimize any adverse effects on global food
Ocean freight markets 15
markets.
Explanatory notes 16
Markets at a glance
FROM FROM
Easing
Neutral PREVIOUS PREVIOUS
Tightening FORECASTS SEASON
WHEAT
MAIZE
RICE
SOYBEANS
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy and other market drivers behind them. The analysis is a collective
assessmentofthemarketsituationandoutlookbytheteninternationalorganizationsandentitiesthatformtheAMISSecretariat.
2 AMISMarketMonitor No.96March2022
Feature article
The Ukraine conflict and global food price scares
The escalating tensions in the Black Sea region have Inthenearterm,f

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*