# 비정형 요약 — 20년 3월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `20년 3월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2020` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 17 |
| 추출 문자 수 | 39,015 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 생산변동, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 47 · 하방어 45) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Gross Domestic Product, Import Volume, Export Volume, Planted Area, Soybean, Bear Regime, Neutral Regime, Baltic Dry Index, Freight Rate, Source Document

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 생산변동, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

AMIS Market Monitor No. 76 – March 2020 1
Feature article
Food markets are not immune to the impacts of the coronavirus outbreak,
but effects will mostly be local
After only two months since the first reported which would be the lowest level since the financial
outbreak of a novel coronavirus in Wuhan, a city of crisis a decade ago, warning that a prolonged and
11 million in China’s central province of Hubei, it more intensive coronavirus epidemic could even
has already spread to almost 80 countries worldwide halve this figure to a mere 1.5 percent.
(according to the World Health Organization as of
Global food markets – and the markets for the four
5 March 2020). With more than 90 000 confirmed
AMIS commodities – are of course not immune to
cases and over 3 000 deaths, COVID-19 has become
these developments. However, they are likely to be
the most important global health scare since SARS in
less affected than other sectors that are more exposed
2003. China still accounts for the majority of cases,
to logistical disruptions and weakened demand, such
but latest figures suggest that the number of new
as travel, manufacturing and energy markets. While
infections outside of China largely outpaces those
basic food commodities may face some constraints
inside the country. In comparison, SARS, which also
stemming from transport interruptions and quarantine
originated in China, spread to 26 countries, infected
measures, impacts are expected to be less severe and
about 8 000 people and

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*