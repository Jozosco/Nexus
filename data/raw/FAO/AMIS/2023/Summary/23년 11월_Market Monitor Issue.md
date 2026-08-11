# 비정형 요약 — 23년 11월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `23년 11월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2023` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 17 |
| 추출 문자 수 | 54,160 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 39 · 하방어 43) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Gross Domestic Product, Export Volume, Precipitation Deficit, Soil Moisture Percentile, Soybean, Soybean Oil, Crude Palm Oil, Neutral Regime, Geopolitical Conflict, Freight Rate, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 113 November 2023
After nearing record levels following the out-
Contents
break of war in Ukraine, implied volatility of
Feature article:
Vegetable oils markets and trade - maize and soybean is now below the histor-
observations on recent trends 2
ical average. This reflects large global har-
World supply-demand outlook 3
vests and large estimated closing stocks. By
Crop monitor 5
contrast, wheat prices have remained highly
Policy developments 8
volatile, largely linked to uncertainty caused
International prices 10
by the conflict. Ukraine's wheat production
Futures markets 12 this year was 35 percent lower than pre-war
Market indicators 13 levels and prospects for a rebound in 2024
Fertilizer outlook 15 are unlikely. While shipping has resumed out
of the Black Sea ports through the so-called
Ocean freight markets 16
humanitarian corridor, persistent attacks on
Explanatory notes 17
exportinfrastructurecontinuetoroilmarkets.
Markets at a glance
Meanwhile rice prices have declined in the
Easing FROM FROM
Neutral PREVIOUS PREVIOUS
past few weeks, reflecting a smaller-than-
Tightening FORECASTS SEASON
WHEAT anticipated impact of El Niño on production,
MAIZE
and prompting some countries to reverse
RICE
market-distorting policies.
SOYBEANS
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy and other 

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*