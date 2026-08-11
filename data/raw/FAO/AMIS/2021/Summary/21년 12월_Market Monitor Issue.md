# 비정형 요약 — 21년 12월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `21년 12월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2021` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 15 |
| 추출 문자 수 | 37,346 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 생산변동, 수입관세, 수출규제, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 31 · 하방어 33) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, Malaysia, India, China, EU, Ukraine, Import Duty, ENSO Phase

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 생산변동, 수입관세, 수출규제, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Contents
World supply-demand outlook .................................... 1
Crop monitor ......................................................................... 3
Policy developments .......................................................... 6
International prices ............................................................. 7
Futures market (US) ............................................................ 9
Market indicators.............................................................. 10
Fertilizer outlook ............................................................... 12
Ocean freight markets.................................................... 13
Explanatory notes
............................................................. 14
M A R K E T
M O N I T O R
No. 94 – December 2021
Markets at a glance
The year 2021 has not been easy for food markets given an
abundance of uncertainties, from production to distribution
From previous From previous
and consumption. Prices kept climbing and even reached forecast season
record highs for some crops, turning food inflation into a
Wheat
major concern, even in developed countries. Overall,
markets continued to show their resilience, with global Maize
supplies remaining adequate and logistical bottlenecks
Rice
proving short-lived. As pressures on global food security
keep mounting, markets will hopefully enter more stable Soybeans
waters in the coming year in order to ensure adequate
access to food for the most vulnerable. Easing Neutral

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*