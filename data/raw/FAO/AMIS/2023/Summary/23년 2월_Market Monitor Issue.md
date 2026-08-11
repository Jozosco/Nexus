# 비정형 요약 — 23년 2월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `23년 2월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2023` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 17 |
| 추출 문자 수 | 88,122 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 재고 |
| 방향성(SBO 가격 기준) | 하방 우세 (상방어 46 · 하방어 63) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, EU, Ukraine, ENSO Phase, Palm Oil

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 105 February 2023
Fertilizer prices have declined by more than
Contents
40 percent since hitting record (nominal)
Feature article:
Is food price inflation really subsiding? 2 highs last spring, especially due to recent
World supply-demand outlook 3 drops in natural gas prices and fertilizer
plants reopening in Europe. Though prices
Crop monitor 5
remain almost twice the level of two years
Policy developments 8
ago, this development is welcome news
International prices 10
for producers making input purchases this
Futures markets 12
spring and should improve profitability mar-
Market indicators 13
gins for many crops. With the price de-
Fertilizer outlook 15
cline most prominent for nitrogenous fertiliz-
Ocean freight markets 16
ers,thiscouldmakenitrogen-intensivecrops
Explanatory notes 17
such as wheat and maize more attractive
planting choices than they were last spring.
Markets at a glance
Lower prices could also encourage higher
FROM FROM
Easing
Neutral PREVIOUS PREVIOUS
Tightening FORECASTS SEASON application rates, particularly in developing
WHEAT countries where fertilizer use is relatively low
MAIZE
andwhererecenthighpriceshavefurtherre-
RICE
duced application rates.
SOYBEANS
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy and other market drivers behind them. The analysis is a collect

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*