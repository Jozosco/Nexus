# 비정형 요약 — 19년 7월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `19년 7월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2019` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 19 |
| 추출 문자 수 | 47,712 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 48 · 하방어 55) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Gross Domestic Product, Import Volume, Export Volume, Soil Moisture Percentile, Planted Area, Production Volume, Stock-to-Use Ratio, Soybean, Neutral Regime, Geopolitical Conflict, Trade War, Baltic Dry Index

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

1 No.70 – July 2019 AMIS Market Monitor
Feature article
What is the “new normal” for commodity prices?
Most commodity prices gained momentum in Overall, however, commodity markets appear to
the first half of 2019, following last year’s be stabilizing following the end of the boom
declines. Among the most salient trends that began in the early 2000s. The new average
affecting commodity prices now are the price level for most commodities is expected to
evolution of the US shale oil industry, China’s be slightly higher than the pre-boom stable level
role as a major consumer of industrial but much lower than the 2008 and 2011 peaks.
commodities, and international trade tensions.
This “new normal” is shaped by several factors.
The emergence of the US as a dominant player The post-2000 price boom attracted investment
in the global oil market—its output is now on across the entire commodity spectrum, spurring
par with production in the Russian Federation innovation and technological improvements that
and Saudi Arabia—is shaping the energy price lowered production costs. On the consumption
outlook. US shale oil production has (and is side, demand has remained relatively weak,
likely to) offset most of the price effect of any especially in emerging markets and developing
production cuts by the Organization of the economies that were key drivers of the boom, as
Petroleum Exporting Countries (OPEC). Still, economic growth in many of these countries has
oil markets have been notoriously 

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*