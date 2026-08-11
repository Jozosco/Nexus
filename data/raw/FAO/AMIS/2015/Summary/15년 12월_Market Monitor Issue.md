# 비정형 요약 — 15년 12월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `15년 12월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2015` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 17 |
| 추출 문자 수 | 54,777 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 수출규제, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 44 · 하방어 40) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Flood, Production Volume, Soybean, Neutral Regime, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 수출규제, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Feb
Market Monitor
No.34 – December 2015
ROUNDUP
Contents
The overall market outlook for AMIS crops has changed little in recent
World Supply-Demand Outlook ..................... 1
months with generally favourable production prospects and high
Crop Monitor ..................................................... 3
inventory levels leading to a relatively calm situation across the board.
Policy Developments ........................................ 6
While international prices have weakened considerably and remain
well below the corresponding period last year, markets appear International Prices .......................................... 7
particularly exposed to weather anomalies, fluctuations in the US Futures Markets ................................................ 8
dollar, slowing income growth and geopolitical conflicts.
Monthly US Ethanol Update ........................... 9
Fertilizer Outlook NEW!.................................10
MARKETS AT A GLANCE
Supplementary tables and charts ................13
From previous From previous
f’cast season
Wheat
Maize
Rice
Soybeans
www.amis-outlook.org
While international prices of all
four AMIS commodities rose
slightly in October, they remained
below the corresponding period
last year. Weaker prices reflect
large export availabilities in
2015/16 in the face of generally
frail import demand, especially
with regard to wheat and maize.
AMIS No. 34 – December 2015 1
World Supply-Demand Outlook
in million tonnes  Wheat production forecast

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*