# 비정형 요약 — 14년 3월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `14년 3월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2014` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 11 |
| 추출 문자 수 | 27,492 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 물류충격, 생산변동, 압착, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 33 · 하방어 21) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, EU, Ukraine, Korea, Biodiesel Mandate, WASDE Surprise

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 물류충격, 생산변동, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market Monitor
No.16 – March 2014 www.amis-outlook.org
Contents
The Market Monitor is a product of the
Agricultural Market Information System (AMIS). It World Supply-Demand Outlook .......................... 1
covers the international markets for wheat,
Crop Monitor ....................................................... 2
maize, rice and soybeans, giving a synopsis of
International Prices .............................................. 4
major market developments and the policy and
other market drivers behind them. The analysis is Policy Developments ........................................... 6
a collective assessment of the market situation
Futures Markets ................................................... 7
and outlook by the ten international
Market Indicators ................................................ 8
organizations that form the AMIS Secretariat.
Ultimately, the report aims at improving market Explanatory Notes and Calendar ....................... 10
transparency and detecting emerging problems
that might warrant the attention of policy
makers.
AMIS No. 16 –March 2014 1
World Supply-Demand Outlook
While possible slowing down of grain exports from Ukraine
because of escalated geopolitical tensions is a concern in the
From previous From previous
short term, bumper crops in several major producing
month f’cast season
countries are likely to boost supplies and to result in much
Wheat
higher world stocks in 2014 for maize, wheat, rice and Maize
soybean. The early out

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*