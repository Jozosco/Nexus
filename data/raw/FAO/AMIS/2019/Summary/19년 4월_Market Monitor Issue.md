# 비정형 요약 — 19년 4월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `19년 4월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2019` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 18 |
| 추출 문자 수 | 44,885 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 36 · 하방어 42) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Gross Domestic Product, Import Volume, Export Volume, Planted Area, Soybean, Neutral Regime, Baltic Dry Index, Freight Rate, Import Tariff, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

1 No.67 – April 2019 AMIS Market Monitor
Grains/oilseeds freight markets: Mixed prospects following a
slump
Freight markets slumped in January as disappointing spot demand and concerns about weakening global economic growth
dashed expectations for a strong start to the season. With early pressure compounded by seasonal holidays in Asia, coupled
with a fallout from a mining dam collapse in Brazil, the Baltic Dry Index (BDI) – a benchmark for costs across dry bulk segments
–slid to its lowest in around two and a half years in late-February. Despite a slight recovery since then, the Index was still
38 percent lower y/y as at late-March, reflecting a market which continues to grapple with overcapacity. In a longer-term
perspective, the Index remains well below historic peaks of a decade ago.
Although prices for ocean transportation of grains and oilseeds displayed a steadier tone over the past year they, too, fell
sharply in 2019. This can be illustrated by the International Grains Council (IGC) Grains and Oilseeds Freight Index (GOFI), which
provides a measure of freight rates across selected heavy grains and oilseeds routes. The Index touched a 17-month low in
mid-February and was down by 14 percent y/y as at 27 March. Although all GOFI sub-Indices stabilised or advanced recently,
led by Brazil, which saw particularly strong soybean shipments, prospects for grains/oilseeds freight markets across key
exporting origins remain mixed, in part because of variable trade forecasts.
IG

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*