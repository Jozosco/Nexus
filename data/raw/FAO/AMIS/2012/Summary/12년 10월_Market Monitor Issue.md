# 비정형 요약 — 12년 10월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `12년 10월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2012` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 6 |
| 추출 문자 수 | 11,957 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 압착, 재고 |
| 방향성(SBO 가격 기준) | 하방 우세 (상방어 3 · 하방어 12) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, India, China, Ukraine, Biodiesel Mandate, WASDE Surprise, ENSO Phase

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

4 October 2012
http://www.amis-outlook.org/ N. 2
AMIS Market Monitor
The IGC joins the AMIS Secretariat
AMIS is pleased to announce that with effect from October 2012 the International Grains Council (IGC) joined the AMIS Secretariat.
This follows close collaboration with the IGC since the launch of AMIS in September 2011. The IGC becomes the tenth member of
the AMIS Secretariat which already includes the following international organizations and entities: FAO, IFPRI, IFAD, OECD, UNCTAD,
the UN High Level Task Force (UN-HLTF), the World Bank, WFP, and WTO.
Supply-Demand Balances at a Glance
Wheat million tonnes
 World wheat production in 2012 to fall below
World USDA IGC FAO-AMIS the 2011 record as drought cut production in the
2011/12 2012/13 2011/12 2012/13 2011/12 2012/13 Black Sea.
 Per caput consumption in 2012/13 to stay stable
Estimate Forecast Estimate Forecast Estimate Forecast
12-Sep 28-Sep 06-Sep 04-Oct but feed use to decline from the above-average
Production 695 659 696 657 699 663 663 2011/12 level.
Supply 893 857 888 854 892 856 856  Trade in 2012/13 to contract sharply on lower
Utilization 694 681 691 679 692 687 687 feed use and high international prices.
Trade 155 135 145 132 145 135 135  World stocks to stay at a relatively comfortable
level, although falling below their opening levels
Ending Stocks 199 177 197 175 193 174 172
to make up for the decrease in production.
Maize
 World maize production to decline significantly
World USDA IGC FAO-AMIS in 20

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*