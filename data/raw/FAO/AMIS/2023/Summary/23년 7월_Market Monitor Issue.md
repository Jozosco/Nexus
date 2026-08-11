# 비정형 요약 — 23년 7월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `23년 7월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2023` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 18 |
| 추출 문자 수 | 90,218 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 수입관세, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 44 · 하방어 54) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Heatwave, Planted Area, Soybean, Crude Palm Oil, Bear Regime, Neutral Regime, Geopolitical Conflict, Baltic Dry Index, Freight Rate, Import Tariff

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 수입관세, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 110 July 2023
The fate of the Black Sea Grain Initiative is
Contents
again in jeopardy. The collapse of the Nova
Feature article:
Destruction of Kakhovka Dam 3 Kakhovkadamlastmonthhasfloodedcrop-
World supply-demand outlook 4 land along the Dnipro River and disrupted
irrigation. Meanwhile, the ammonia pipeline
Crop monitor 6
from the Russian Federation to the Ukrainian
Policy developments 9
port of Pivdennyi has also been damaged.
International prices 11
The pipeline has not been in operation since
Futures markets 13
the start of the war; however, its reopening
Market indicators 14
has been a key demand of the Russian Fed-
Fertilizer outlook 16
eration to renew the grain deal. While these
Ocean freight markets 17
eventsarenotlikelytohavemajorimpactson
Explanatory notes 18
grain supplies in the short term, they further
increasetensionsthatcouldresultinatermi-
Markets at a glance
nationoftheagreementlaterthismonth.This
FROM FROM
Easing
Neutral PREVIOUS PREVIOUS
Tightening FORECASTS SEASON would reduce Black Sea exports and further
WHEAT reduce Ukraine production incentives.
MAIZE
RICE
SOYBEANS
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy and other market drivers behind them. The analysis is a collective
assessmentofthemarketsituationandoutlookbytheteninternationalorganizationsandentitiestha

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*