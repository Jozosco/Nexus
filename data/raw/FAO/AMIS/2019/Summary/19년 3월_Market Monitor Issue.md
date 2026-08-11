# 비정형 요약 — 19년 3월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `19년 3월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2019` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 18 |
| 추출 문자 수 | 43,612 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 35 · 하방어 39) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Planted Area, Production Volume, Soybean, Neutral Regime, Trade War, Baltic Dry Index, Freight Rate, Import Tariff, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

1 No.66 – March 2019 AMIS Market Monitor
Early forecasts point to a strong recovery in global wheat
production in 2019
FAO is publishing its first production forecasts for 2019 wheat crops in the March issue of Crop Prospects and Food
Situation1. With AMIS hosted at FAO and sharing a common platform, these forecasts are a joint effort and their
source is referred to as ‘FAO-AMIS’. While providing a detailed analysis of regional outlooks for cereals, the March
report also foresees global wheat production to strongly recover from last year, rising by 4.0 percent, to 757.4 million
tonnes in 2019. This would be close to the record crop of 2017, with the bulk of the recovery stemming from Europe.
In the EU, a larger planted area combined with generally good weather (so far) is seen to drive up wheat production
by at least 8 percent from last year’s six-year low. Similarly, in the Russian Federation, an expectation of increased
overall plantings in combination with beneficial weather could push up production by almost 10 percent. Favourable
crop conditions also currently prevail in Ukraine, where this year’s wheat output is forecast to rise by nearly 8 percent.
In North America, this year’s production in the United States is likely to remain close to last year’s level, whereas in
Canada it could increase by around 4 percent. In Australia, a strong rebound from last year’s drought afflicted level is
foreseen, though wheat planting will only begin in May. Elsewhere, the 2019 output i

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*