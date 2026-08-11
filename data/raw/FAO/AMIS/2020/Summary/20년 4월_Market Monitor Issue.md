# 비정형 요약 — 20년 4월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `20년 4월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2020` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 18 |
| 추출 문자 수 | 40,966 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 생산변동, 수입관세, 수출규제, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 45 · 하방어 43) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, Ukraine, Export Tax, Import Duty, ENSO Phase

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 생산변동, 수입관세, 수출규제, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

AMIS Market Monitor No. 77 – April 2020 1
Feature article
COVID-19 may spare global food markets, but not vulnerable countries
While the impact of the COVID-19 crisis on global Concurrently, the slowdown in the global economy
food markets has so far been limited, the pandemic and disruptions to global agricultural supply chains
poses a serious threat to food security at local level. have cutback demand for cash and high-valued crops,
According to official statistics, the virus has not yet such as fruits, coffee and tea, which are key export-
spread widely in countries where food insecurity is earners in many less-developed countries. These
pervasive, most notably in Sub-Saharan Africa. If it reductions will translate into income losses for
did, the outbreak could be expected to have similar farming households, while national foreign currency
effects to previous epidemic-induced shocks, such as reserves could shrink, with implications for funding
the Ebola Virus Disease, which caused steep harvest of social-safety net programmes and the ability to pay
reductions, food price spikes and aggravated food for food imports. Particularly in urban areas of less-
insecurity. Additionally, and perhaps more imminent, developed countries, the slowdown in economic
is the risk posed by the global economic downturn activities and movement restrictions are likely to cut
caused by the COVID-19 crisis, which may households’ incomes and purchasing power, factors
compromise import-dependent count

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*