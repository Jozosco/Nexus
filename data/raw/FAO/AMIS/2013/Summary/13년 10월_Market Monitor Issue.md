# 비정형 요약 — 13년 10월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `13년 10월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2013` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 11 |
| 추출 문자 수 | 23,315 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 생산변동, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 22 · 하방어 17) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, EU, Ukraine, Biodiesel Mandate, WASDE Surprise, ENSO Phase

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 생산변동, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market Monitor
No.12 – October 2013 www.amis-outlook.org
The Market Monitor is a product of the Contents
Agricultural Market Information System (AMIS), a
World Supply-Demand Outlook .......................... 1
G20 initiative to provide information, analysis and
short-term supply and demand forecasts. It covers Crop Monitor ..................................................... 2
the international markets for wheat, maize, rice
International Prices .............................................. 4
and soybeans, giving a synopsis of major market
Futures Markets ................................................... 6
developments and the policy and other market
Policy Developments ........................................... 7
drivers behind them. The analysis is a collective
assessment of the market situation and outlook Market Indicators ................................................ 8
by the ten international organizations that form
Explanatory Notes ............................................. 10
the AMIS Secretariat. Ultimately, the report aims
at improving market transparency and detecting
emerging problems that might warrant the
attention of policy makers.
AMIS No. 12 –October 2013 1
World Supply-Demand Outlook
In spite of downward revisions to the September production
forecasts for all AMIS crops except for maize, the overall
From previous From previous
prospects still point to a more balanced supply and demand month f’cast season
situation in 2013/14. Climate conditions 

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*