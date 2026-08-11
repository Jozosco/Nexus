# 비정형 요약 — 17년 11월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `17년 11월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2017` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 15 |
| 추출 문자 수 | 39,009 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 46 · 하방어 35) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, EU, Ukraine, Korea, Import Duty, ENSO Phase

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

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
No. 53 – November 2017
Roundup Markets at a glance
Wheat, maize, rice and soybeans are heading for a
comfortable market situation in 2017/18. Even for crops From previous From previous
where production is forecast to fall below last year’s level, forecast season
supplies are expected to remain sufficient, which may explain
Wheat
some of the downward pressure on prices witnessed in recent
weeks. For major cereals, the market focus will soon be Maize
shifting to planting and growing conditions in the new
season. In this context, the 2018/19 outlook will critically Rice
depend on weather and expected returns based on price
prospects. In the case of soybeans, planting progress and
Soybeans
weather developments in the southern hemisphere will likely
Easing Neutral Tightening
influence prices in the coming weeks.
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice and
soybeans, giving a synopsis of major market developments and the policy and other market drivers behind them. The analysis is a collective assessment
of the market situation and outlook by the eleven international organizations and entities that form the AMIS Secretariat.
Visit us at: www.amis-outl

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*