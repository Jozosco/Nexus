# 비정형 요약 — 20년 2월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `20년 2월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2020` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 18 |
| 추출 문자 수 | 42,831 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 수출규제, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 45 · 하방어 37) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Soil Moisture Percentile, Planted Area, Production Volume, Soybean, Soybean Oil, Crude Palm Oil, Neutral Regime, Biodiesel Feedstock, Baltic Dry Index, Freight Rate

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 수출규제, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

AMIS Market Monitor No.75 – February 2020 1
Feature article
Forward curves and why they are important for supply and demand analysis
Certain portions of the forward curves are
Forward curves represent a term structure of
commonly referred to as “spreads” and are quoted
prices. They are constructed by connecting a line
as the arithmetic difference between nearest and
along the sequence of futures contract price
the furthest contract month. For example, the
quotations at a given reference point in time, which
difference between the July and November
are plotted along the horizontal axis. These price
soybean contracts of any one year is keenly
quotations typically proceed from the spot or
watched as one of commodity markets’ most
nearby futures month and extend forward about 18
dynamic spreads. To illustrate, in 2013, the
to 24 months at fixed monthly intervals. For
July/November spread displayed steep
example, the contract months listed for the maize
backwardation reaching a level of USD 132 per
trading are March, May, July, September and
tonne as global demand exceeded supplies.
December, repeating forward as market
Conversely, in 2018, the July/November spread
transactions occur in deferred months. The slope of
declined from a small inverse to a USD 9 contango
the futures curve conveys information about the
as the demand rate slowed amid abundant supplies.
supply and demand of its underlying commodity
and also transmits important indicators to
In 2019, the maize market exhibi

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*