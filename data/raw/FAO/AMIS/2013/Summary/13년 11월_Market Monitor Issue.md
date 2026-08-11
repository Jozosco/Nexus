# 비정형 요약 — 13년 11월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `13년 11월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2013` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 11 |
| 추출 문자 수 | 26,255 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 물류충격, 생산변동, 압착, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 28 · 하방어 21) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Soil Moisture Percentile, Production Volume, World Agricultural Supply and Demand Estimates, Soybean, Neutral Regime, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 물류충격, 생산변동, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market Monitor
No.13 – November 2013 www.amis-outlook.org
The Market Monitor is a product of the Contents
Agricultural Market Information System (AMIS), a World Supply-Demand Outlook .......................... 1
G20 initiative to provide information, analysis and
Crop Monitor ....................................................... 2
short-term supply and demand forecasts. It covers
International Prices .............................................. 4
the international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market Policy Developments ........................................... 6
developments and the policy and other market
Futures Markets ................................................... 7
drivers behind them. The analysis is a collective
Market Indicators ................................................ 8
assessment of the market situation and outlook
by the ten international organizations that form Explanatory Notes and Crop Calendar ................ 9
the AMIS Secretariat. Ultimately, the report aims
at improving market transparency and detecting
emerging problems that might warrant the
attention of policy makers.
AMIS No. 13 –November 2013 1
World Supply-Demand Outlook
Bumper crops in several major producing countries boost From previous From previous
global production to record levels and are expected to lead month f’cast season
the way to much higher world stocks by the end of seasons in Wheat
2014. International prices of all AMIS crop

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*