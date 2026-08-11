# 비정형 요약 — 19년 11월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `19년 11월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2019` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 17 |
| 추출 문자 수 | 40,350 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 수출규제, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 47 · 하방어 39) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Soil Moisture Percentile, Planted Area, Soybean, Neutral Regime, Baltic Dry Index, Freight Rate, Import Tariff, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 수출규제, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

AMIS Market Monitor No.73 – November 2019 1
Feature article
Improving the multilateral foundation for agricultural trade
Amid decelerating global trade and economic Since the 2015 landmark agreement to eliminate
growth as well as geopolitical tensions and export subsidies, all WTO Members with
uncertainties, the multilateral trading system is scheduled reduction commitments, with the
engaged towards a momentous reform objective as exception of three developing countries, have
it heads to the Twelfth Session of the WTO taken the required implementation steps. Many
Ministerial Conference, scheduled to take place in participants are now keen to refine specific export
Nur-Sultan, Kazakhstan, on 8-11 June 2020, i.e. competition elements, ensuring that past
"to establish a fair and market-oriented achievements are not circumvented through the
agricultural trading system". A range of policy operations of exporting state trading enterprises,
domains of relevance to AMIS commodities is international food aid, or subsidized export credits.
being examined, including a fundamental cross-
cutting theme, i.e. transparency. While the right to temporarily institute export
restrictions and prohibitions to relieve critical
As a priority, alternative approaches to reduce domestic food shortages has long been recognized,
trade-distorting support are being studied, possibly the debate focuses primarily on transparency
through the revamping of the current conceptual requirements and the need to mi

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*