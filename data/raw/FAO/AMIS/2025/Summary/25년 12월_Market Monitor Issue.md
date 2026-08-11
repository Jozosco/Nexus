# 비정형 요약 — 25년 12월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `25년 12월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2025` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 19 |
| 추출 문자 수 | 63,504 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 48 · 하방어 48) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, Malaysia, India, China, EU, Ukraine, ENSO Phase, Sunflower Oil, Rapeseed Oil

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 134 December 2025
Contents
Aswecloseout2025,globalagriculturalmar-
Feature article:
Managing commodity supply in a
kets remain well supplied, while price move-
fragmented world 2
ments across key commodities have been
World supply-demand outlook 3
mixed throughout the year: rice and wheat
Crop monitor 5
fell below their year earlier levels, maize held
Policy developments 8
steady, and soybeans strengthened. Much
International prices 10
of the year was shaped by uncertainty sur-
Futures markets 12
rounding trade policies, though November
Market indicators 13
broughtrenewedoptimism,especiallyregard-
Fertilizer outlook 15
ing for trade prospects between China and
Vegetable oils 17
the United States. Fertilizer prices eased, yet
Ocean freight markets 18
the widening gap between input costs and
Explanatory notes 19
crop values continues to weigh on demand.
Markets at a glance With the end of the US federal government
Easing FROM FROM shutdown, several reports essential for mar-
Neutral PREVIOUS PREVIOUS
Tightening FORECASTS SEASON
ket transparency were restored.
WHEAT
MAIZE
The next edition of the Market Monitor will be
RICE
published on Friday, 6 February. With best
SOYBEANS
wishesforasuccessfulandprosperous2026!
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy and other market drivers behind the

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*