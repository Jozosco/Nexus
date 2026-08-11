# 비정형 요약 — 19년 9월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `19년 9월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2019` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 19 |
| 추출 문자 수 | 50,265 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 59 · 하방어 44) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Planted Area, Production Volume, Soybean, Bear Regime, Neutral Regime, Trade War, Baltic Dry Index, Freight Rate, Import Tariff, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

1 No.71 – September 2019 AMIS Market Monitor
Feature article
The market signal is weaker than the noise
The latest OECD-FAO Agricultural Outlook supply can be increased sustainably. So open
projects that food supply growth over the next ten markets and trade will be important both for food
years will modestly outpace demand growth. security and sustainable resource use.
Continued productivity gains are expected to
expand cereal supplies by about 15 percent over Yet with lower food prices, according to the latest
the decade, while demand growth will be driven OECD Monitoring and Evaluation of agricultural
primarily by population growth of just over policies, a significant number of countries are
1 percent per year. Only a minor share of the increasingly applying protectionist policies to
increase in cereal demand will come from higher safeguard farm incomes. Overall, support could be
per capita consumption, which has already reached provided via targeted measures that do not require
saturation levels in most countries. For most crop border protection and address the long-term needs
and livestock commodities, gradual real price of producers, consumers and the natural
declines are projected, of the order of 1 percent per environment.
year.
The broad conclusion is that markets are
As noted regularly in the AMIS Market Monitor,
responding well to the challenge of feeding the
monthly and annual price variations (due to a wide
world. Policies are doing less well in terms of
range of

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*