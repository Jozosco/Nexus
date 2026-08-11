# 비정형 요약 — 23년 6월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `23년 6월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2023` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 17 |
| 추출 문자 수 | 89,310 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 수출규제, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 52 · 하방어 62) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, Ukraine, Export Tax, Palm Export Levy, Black Sea Corridor, ENSO Phase

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 수출규제, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 109 June 2023
While agricultural prices have declined over
Contents
the past 12 months, food price inflation re-
Feature article:
Food price inflation continues putting mains high. FAO's food price index, a mea-
people's food security at risk 3
sure of the monthly change in international
World supply-demand outlook 4
prices of a basket of food commodities, is
Crop monitor 5
down 20 percent from year-ago levels. Yet,
Policy developments 8
double-digit food inflation rates are reported
International prices 10
inmanycountriesaroundtheworld.Foodin-
Futures markets 12 flation remains elevated in part because of
Market indicators 13 the strong US dollar, which has kept com-
Fertilizer outlook 15 modity prices high in local currencies, and
because post-farmgate costs such as en-
Ocean freight markets 16
ergy,transportation,andfoodmanufacturing
Explanatory notes 17
costs, which account for a large share of the
Markets at a glance
retail price, remain high due to core inflation-
Easing FROM FROM
Neutral PREVIOUS PREVIOUS
ary pressures. The poor suffer the most from
Tightening FORECASTS SEASON
WHEAT N/A high food prices as they spend high shares
MAIZE N/A
of their incomes on food and have weak ca-
RICE N/A
pacity to cope with price shocks.
SOYBEANS N/A
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy a

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*