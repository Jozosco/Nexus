# 비정형 요약 — 23년 12월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `23년 12월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2023` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 17 |
| 추출 문자 수 | 57,408 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 압착, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 42 · 하방어 27) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Export Volume, Flood, Planted Area, Marketing Year, Soybean, Bull Regime, Bear Regime, Geopolitical Conflict, Baltic Dry Index, Freight Rate, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 114 December 2023
As the year draws to a close, commodity
Contents
markets have quieted down from the more
Feature article:
Fertilizer crisis and global food volatile price movements that have charac-
production 2
terized the past two years. With the ex-
World supply-demand outlook 3
ception of rice, prices for most grains and
Crop monitor 5
oilseeds are 15 to 20 percent below Jan-
Policy developments 8
uary 2022 levels. Yet, even rice prices have
International prices 10
fallen back from recent highs as global pro-
Futures markets 12 duction prospects look more favorable than
Market indicators 13 they did in late summer. Despite a slow-
Fertilizer outlook 15 ing global economy, demand for agricultural
products remains strong and is expected to
Ocean freight markets 16
hit record levels in the 2023/24 marketing
Explanatory notes 17
season. Lower prices mean reduced prof-
Markets at a glance
itability for grain and oilseed farmers though
Easing FROM FROM
Neutral PREVIOUS PREVIOUS
lower costs for fuel and fertilizer will help mit-
Tightening FORECASTS SEASON
WHEAT igate that impact.
MAIZE
RICE
SOYBEANS
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy and other market drivers behind them. The analysis is a collective
assessmentofthemarketsituationandoutlookbytheteninternationalorganizationsandent

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*