# 비정형 요약 — 22년 7월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `22년 7월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2022` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 17 |
| 추출 문자 수 | 89,445 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 수입관세, 수출규제, 재고 |
| 방향성(SBO 가격 기준) | 하방 우세 (상방어 31 · 하방어 50) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Gross Domestic Product, Import Volume, Export Volume, Flood, Production Volume, Soybean, Vegetable Oil, Crude Palm Oil, Neutral Regime, Hold Recommendation, Geopolitical Conflict, Baltic Dry Index

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 수입관세, 수출규제, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 100 July 2022
The wheat harvest is underway in the north-
Contents
ern hemisphere, with hot and dry conditions
Feature article:
WTO MC12 charts a new way impedingwinterwheatyieldsinseveralmajor
forward 2
producing regions, which further confirm an
World supply-demand outlook 3
expected decline in global wheat production
Crop monitor 5
in 2022. While maize production prospects
Policy developments 8
improved this month, global maize output is
International prices 10
also forecast to fall below last year's level.
Futures markets 12 Against this background, and with exports
Market indicators 13 from Ukraine still largely constrained, inter-
Fertilizer outlook 15 national wheat and maize markets are ex-
pected to stay tight. This means prices will
Ocean freight markets 16
remainvolatileandcontinuetobehighlysen-
Explanatory notes 17
sitive to daily news on crop development,
Markets at a glance
weather conditions and policy changes. By
FROM FROM
Easing
Neutral PREVIOUS PREVIOUS
contrast, global rice production prospects
Tightening FORECASTS SEASON
WHEAT appearstrongdespitehighinputpriceswhile
MAIZE
soybean output could hit a new record.
RICE
SOYBEANS
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy and other market drivers behind them. The analysis is a collective
assessmentofthemarketsituationandou

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*