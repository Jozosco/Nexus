# 비정형 요약 — 19년 12월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `19년 12월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2019` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 17 |
| 추출 문자 수 | 42,222 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 44 · 하방어 36) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, Ukraine, Korea, WASDE Surprise, ENSO Phase

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

AMIS Market Monitor No.74 – December 2019 1
Feature article
The global maritime transport landscape is changing
Maritime transport handles over four-fifths of the norm. Other forces at play include (1) supply
world merchandise trade by volume. It is now chain restructuring in favour of more regionalized
lying at a crossroad of intertwined forces trade flows; (2) greater use of technology and
spanning economics, politics, environment, and services in value chains and logistics;
technology. Wide-ranging trends are redefining (3)intensified natural disasters and climate-
the sector with softer global economic growth related disruptions; (4) changes in demand
being at the forefront. Trade tensions and patterns; and (5) accelerated environmental
geopolitical risks also constitute major risk sustainability and energy transition agendas.
factors.
Looking forward, maritime trade is projected to
Against this background, world maritime trade grow at an average annual rate of 3.4 percent
lost momentum in 2018, expanding at a rate over the 2019-2024 period. Nevertheless, several
below the historical average. Nearly 2 percent of risks continue to cloud the horizon. Aside from a
maritime trade was affected by tariffs escalations weakening in global demand, growth prospects of
(September 2018 to May 2019), especially grain, dry bulks – particularly relevant for AMIS – are
containerized trade and steel products. Winners also shaped by economic and regulatory
and losers are emerging from prod

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*