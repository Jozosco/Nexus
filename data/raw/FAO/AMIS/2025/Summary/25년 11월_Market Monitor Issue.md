# 비정형 요약 — 25년 11월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `25년 11월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2025` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 19 |
| 추출 문자 수 | 61,607 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 수출규제, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 47 · 하방어 48) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Planted Area, Marketing Year, Soybean, Crude Palm Oil, Bull Regime, Neutral Regime, Geopolitical Conflict, Trade War, Baltic Dry Index, Freight Rate

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 수출규제, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
12cm
Monitor
No. 133 November 2025
Contents
Markets for wheat, maize, rice and soy-
Feature article:
Latest trends in export restrictions 2 beans remain well supplied as of November.
World supply-demand outlook 3 Global crop conditions remain generally fa-
Crop monitor 5 vorable, though localized challenges persist.
Policy developments 8 Early-seasondroughtisaffectingwinterwheat
sowing in China, the European Union, and
International prices 10
Ukraine, while excessive rains are hamper-
Futures markets 12
ing maize harvesting in China and the United
Market indicators 13
States.Inaddition,tropicalstormsinVietNam
Fertilizer outlook 15
and Thailand have damaged rice crops. De-
Vegetable oils 17
spite these disruptions, prices declined for
Ocean freight markets 18
all major crops except soybeans, which saw
Explanatory notes 19
slight gains. Fertilizer prices also eased but
remain high relative to crop values, weighing
Markets at a glance
on fertilizer demand. The outlook is clouded
Easing FROM FROM
Neutral PREVIOUS PREVIOUS
by the US government shutdown, which has
Tightening FORECASTS SEASON
WHEAT been disrupting the release of crucial market
MAIZE
reports, coupled with policy uncertainty and
RICE
evolving trade policies.
SOYBEANS
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy and other market drivers behind

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*