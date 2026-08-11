# 비정형 요약 — 20년 6월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `20년 6월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2020` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 16 |
| 추출 문자 수 | 44,893 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 48 · 하방어 43) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, Malaysia, India, China, Ukraine, Import Duty, WASDE Surprise, ENSO Phase, Palm Oil, Rapeseed Oil

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Contents
Feature article: Food commodity prices .................. 1
World supply-demand outlook .................................. 2
Crop monitor .................................................................... 3
Policy developments ...................................................... 6
International prices ........................................................ 8
Futures market ............................................................... 10
Market indicators .......................................................... 11
Fertilizer outlook ........................................................... 13
Ocean freight markets ................................................. 14
Explanatory Notes ........................................................ 15
M A R K E T
M O N I T O R
No. 79 – June 2020
Markets at a glance
While the outlook for global wheat production in 2020
has dampened somewhat since last month, early forecasts
point to record maize and rice outputs and a recovery in
From previous From previous
soybean production. Despite the many uncertainties forecast season
stemming from economic and health implications of the
Wheat
COVID-19 pandemic, stronger trade dynamics are
expected for all AMIS crops in the new season (2020/21) Maize N/A
along with generally improved demand prospects. With
Rice N/A
the exception of soybeans, inventories of all other AMIS
crops are also set to remain high or increase. Soybeans N/A
Easing Neutral Tightening
The Market Monitor is a

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*