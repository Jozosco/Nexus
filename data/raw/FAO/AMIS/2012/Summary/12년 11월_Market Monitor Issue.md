# 비정형 요약 — 12년 11월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `12년 11월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2012` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 7 |
| 추출 문자 수 | 12,973 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 생산변동, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 12 · 하방어 13) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Export Volume, Production Volume, Stock-to-Use Ratio, Soybean, Baltic Dry Index, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 생산변동, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market Monitor
Number 3 – November 2012
AMIS Crops: World Supply-Demand Balances in 2012/13
W
orld supply and demand situation continues to
From previous From previous
tighten for wheat and maize but rice and soybeans have month f’cast season (2011/12)
eased. In recent weeks, unfavourable weather Wheat
conditions affecting some winter wheat growing areas Maize
in the northern hemisphere and maize and soybeans in Rice
the southern hemisphere have become a concern. In Soybeans
addition, contradictory reports about possible export
Easing Neutral Tightening
restrictions by Ukraine also influenced the market.
million tonnes
USDA IGC FAO-AMIS  Wheat production down sharply from 2011 record, mainly because
WHEAT 2011/12 2012/13 2011/12 2012/13 2011/12 2012/13
of severe drought in eastern Europe and central Asia.
est. f'cast est. f'cast est. f'cast
11-Oct 25-Oct 04-Oct 08-Nov  Utilization above production for the second consecutive season but
Production 696 653 694 655 699 663 661 feed use falling from the peak in 2011/12.
Supply 894 851 889 851 892 856 850  Trade in 2012/13 falls, mostly on improved production in several
Utilization 695 678 692 679 698 687 687 importing countries and reduced feed demand as well as tighter
Trade 157 131 145 132 147 135 135 exportable supplies.
Ending Stocks 198 173 196 172 189 172 167  Stocks (ending 2013) to fall below their opening levels (by even more
than was anticipated in October) reflecting larger draw down in
China.
USDA IGC FAO-AMIS  Ma

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*