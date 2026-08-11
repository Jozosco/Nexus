# 비정형 요약 — 18년 12월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `18년 12월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2018` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 19 |
| 추출 문자 수 | 48,985 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 수출규제, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 42 · 하방어 47) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Planted Area, Production Volume, Soybean, Bear Regime, Neutral Regime, Baltic Dry Index, Freight Rate, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 수출규제, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Contents
Feature article –China’s revised production estimates 1
World supply-demand outlook 3
Crop monitor 5
Policy developments 8
International prices 9
Futures markets 11
Market indicators 12
Monthly US ethanol update 14
Fertilizer outlook 15
Ocean freight market update 16
Explanatory notes 17
M A R K E T
M O N I T O R
No. 64 – December 2018
Markets at a glance
This year has been eventful in many ways for most
agricultural commodities; beyond the usual supply and
demand factors shaping markets there has been an
From previous From previous
increasing level of uncertainty stemming from unexpected
forecast season
shifts in trade policies. Among the AMIS crops, maize and
soybeans have been at the forefront of these policy
Wheat
changes, while global wheat and rice markets have been
Maize
little affected. The other important feature, also central to
the work of AMIS, is the recent revelation of drastically Rice
higher cereal production levels in China with potentially
important implications, which is the main focus of this Soybeans
month’s editorial.
Easing Neutral Tightening
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice and
soybeans, giving a synopsis of major market developments and the policy and other market drivers behind them. The analysis is a collective assessment
of the market situation and outlook by ten international organizations and entities that form the AMIS Secretariat

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*