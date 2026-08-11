# 비정형 요약 — 16년 10월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `16년 10월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2016` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 16 |
| 추출 문자 수 | 46,049 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 40 · 하방어 44) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Flood, Soil Moisture Percentile, Production Volume, Soybean, Bull Regime, Bear Regime, Neutral Regime, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Contents
World supply-demand outlook 1
Crop monitor 3
Policy developments 6
International prices 8
Futures markets 10
Market indicators 11
Monthly US ethanol update 13
Fertilizer outlook 14
Explanatory notes 15
M A R K E T
M O N I T O R
No. 42 – October 2016
Roundup Markets at a glance
World supply and demand balances of the four AMIS crops all
point to generally comfortable prospects in 2016/17. Wheat From previous From previous
markets are expected to be particularly well supplied, albeit forecast season
with larger surpluses of feed wheat than high-quality milling
Wheat
wheat. The global maize market is set to benefit from record
crops in nearly all leading producers apart from Brazil and Maize
South Africa. World rice production is heading for its first
increase in three years, to a new record. Soybean markets are Rice
seen to benefit from a strong recovery in production this year,
largely on expectation of good to exceptional yields in a
Soybeans
number of leading producers.
Easing Neutral Tightening
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers the international markets for wheat, maize, rice and
soybeans, giving a synopsis of major market developments and the policy and other market drivers behind them. The analysis is a collective assessment
of the market situation and outlook by the eleven international organizations and entities that form the AMIS Secretariat.
Visit us at: www.amis-outlook.org
1 No.42–October 2016 AM

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*