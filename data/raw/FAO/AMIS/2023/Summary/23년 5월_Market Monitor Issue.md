# 비정형 요약 — 23년 5월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `23년 5월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2023` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 18 |
| 추출 문자 수 | 91,650 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 수출규제, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 55 · 하방어 52) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, EU, Ukraine, Korea, Export Tax, ENSO Phase

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 수출규제, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 108 May 2023
While international wheat, maize and veg-
Contents
etable oil prices registered record highs and
Feature article:
El Niño is Likely Right Around the muchvolatilitylastyear,ricemarketskeptrel-
Corner 3
atively calm in view of large global supplies.
World supply-demand outlook 4
Over the past seven months, however, rice
Crop monitor 6
prices have been generally on a rise and in
Policy developments 9
some suppliers increased by more than 25
International prices 11
percent. The rapid emergence of El Niño, a
Futures markets 13 climate pattern that describes the unusual
Market indicators 14 warmingofsurfacewatersintheeasternPa-
Fertilizer outlook 16 cific Ocean, combined with a positive Indian
Ocean Dipole raises concerns about possi-
Ocean freight markets 17
ble impacts on rice production in South and
Explanatory notes 18
SoutheastAsia.Muchwilldependonthetim-
Markets at a glance
ing and strength of El Niño, especially as to
FROM FROM
Easing
Neutral PREVIOUS PREVIOUS
whetherornotnormalmonsoonpatternswill
Tightening FORECASTS SEASON
WHEAT beaffected.Overthenextcoupleofmonths,
MAIZE
these climatic developments will be closely
RICE
monitored by AMIS.
SOYBEANS
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy and other market drivers behind them. The analysis is a collective
assessmentofthe

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*