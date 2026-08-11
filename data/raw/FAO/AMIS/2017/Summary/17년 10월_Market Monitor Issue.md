# 비정형 요약 — 17년 10월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `17년 10월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2017` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 15 |
| 추출 문자 수 | 39,605 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 51 · 하방어 34) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Soil Moisture Percentile, Soybean, Neutral Regime, Source Document

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
No. 52 – October 2017
Roundup Markets at a glance
This month’s revisions largely concern production and stocks
forecasts although the overall supply and demand prospects From previous From previous
for the four AMIS crops in 2017/18 remain broadly in line forecast season
with earlier projections, with supplies at the global level still
Wheat
more than adequate to meet the anticipated world demand.
While recent movements in international prices of the four Maize
crops portray a mixed picture, they reflect normal seasonal
patterns expected for this time of the year. Looking forward, Rice
the final size of the forthcoming maize crop in the US will
factor heavily on international maize prices. As the season
Soybeans
progresses, the eventual size of plantings (winter wheat and
Easing Neutral Tightening
secondary rice in the northern hemisphere along with maize
and soybeans in South America) will also influence price
developments.
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice and
soybeans, giving a synopsis of major market developments and the policy and other market drivers behind them. The analysis is a collective assessment
of the market situation and o

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*