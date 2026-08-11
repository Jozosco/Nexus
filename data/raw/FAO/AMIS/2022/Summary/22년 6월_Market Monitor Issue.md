# 비정형 요약 — 22년 6월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `22년 6월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2022` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 17 |
| 추출 문자 수 | 90,199 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 수입관세, 수출규제, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 43 · 하방어 39) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, EU, Ukraine, Export Tax, Import Duty, ENSO Phase, Rapeseed Oil

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 수입관세, 수출규제, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 99 June 2022
Despite record nominal prices, FAO-AMIS
Contents
expects global production for maize and
Feature article:
Global food security consequences wheattofallin2022.Withoutputslikelybeing
of the war in Ukraine 2
lowerthanlastyearinAustralia,Moroccoand
World supply-demand outlook 3
India(wheat)andintheUnitedStates(maize)
Crop monitor 4
the loss of production in Ukraine might not
Policy developments 7
be offset by the rest of the world. This will
International prices 10
likely keep upward pressure on prices with
Futures markets 12 potentially devastating effects on the global
Market indicators 13 poor. Trade restrictions also remain a con-
Fertilizer outlook 15 cern. At the end of May, 23 countries have
implementedexportrestrictionsrangingfrom
Ocean freight markets 16
outrightbanstoexporttaxesaffectingalmost
Explanatory notes 17
18 percent of agricultural exports, on a kilo-
Markets at a glance
calorie basis. In this context, AMIS - through
FROM FROM
Easing
Neutral PREVIOUS PREVIOUS
a joint statement of the AMIS chairs - is call-
Tightening FORECASTS SEASON
WHEAT N/A ingonallcountriestorefrainfromimplement-
MAIZE N/A
ing trade restrictions, which will prolong the
RICE N/A
uncertaintyinmarketsandthreatenthemost
SOYBEANS N/A
vulnerable around the globe.
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*