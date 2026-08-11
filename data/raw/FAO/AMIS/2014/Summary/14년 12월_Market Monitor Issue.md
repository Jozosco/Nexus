# 비정형 요약 — 14년 12월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `14년 12월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2014` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 13 |
| 추출 문자 수 | 35,778 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 37 · 하방어 32) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Soil Moisture Percentile, Production Volume, Harvest Delay, Soybean, Neutral Regime, Import Tariff, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Share your views on the AMIS Market
Monitor by participating in our survey
Market Monitor
No.24 – December 2014 www.amis-outlook.org
The Market Monitor is a product of the Contents
Agricultural Market Information System (AMIS). It World Supply-Demand Outlook .......................... 1
covers the international markets for wheat,
Crop Monitor ....................................................... 2
maize, rice and soybeans, giving a synopsis of
Policy Developments ........................................... 5
major market developments and the policy and
other market drivers behind them. The analysis is International Prices .............................................. 6
a collective assessment of the market situation
Futures Markets ................................................... 7
and outlook by the ten international
Monthly US Ethanol Update ................................ 8
organizations that form the AMIS Secretariat.
Ultimately, the report aims at improving market Supplementary tables and charts ............................... 9
transparency and detecting emerging problems Explanatory Notes and Crop Calendar ...................... 12
that might warrant the attention of policy
makers.
AMIS No. 24 – December 2014 1
World Supply-Demand Outlook
Large production and ample inventories continue to point to
a further easing of the global market situation in 2014/15 for From previous From previous
all AMIS crops. However, as some weather disruptions in a month f’cast seaso

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*