# 비정형 요약 — 12년 12월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `12년 12월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2012` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 8 |
| 추출 문자 수 | 15,386 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 16 · 하방어 14) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, EU, Ukraine, Biodiesel Mandate, WASDE Surprise, ENSO Phase

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market Monitor
Number 4 – December 2012
AMIS Crops: World Supply-Demand Balances in 2012/13
Markets stabilized in recent weeks as forecasts for
From previous From previous
2012/13 balances of AMIS crops became more definite. month f’cast season (2011/12)
Given the overall tightness for wheat, maize and soybeans, Wheat
the focus is shifting to the influence of weather on crop Maize
prospects for 2013. Drought affecting winter wheat in the Rice
US and unfavourable weather in parts of Europe and South Soybeans
America, have raised concerns, although it is not possible
Easing Neutral Tightening
to draw any firm conclusions at this early stage.
million tonnes  Wheat production in 2012 falling below the record in 2011. The
USDA IGC FAO-AMIS forecast lowered further since November on reduced prospects in
WHEAT 2011/12 2012/13 2011/12 2012/13 2011/12 2012/13
Australia and Brazil.
est. f'cast est. f'cast est. f'cast
09-Nov 29-Nov 08-Nov 06-Dec  Utilization in 2012/13 down from 2011/12 with lower feed use in
Production 696 651 695 654 699 661 659 China and the EU more than offsetting higher feed use in the US.
Supply 894 849 889 851 883 850 843  Trade contracting sharply on reduced import demand from North
Utilization 696 675 693 678 694 687 686 Africa and Asia. The forecast increased from November on higher
Trade 156 133 146 134 146 135 136 imports by CIS countries.
Ending Stocks 198 174 196 173 184 167 163  Stocks (ending 2013) declining significantly, with a further cut in the
f

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*