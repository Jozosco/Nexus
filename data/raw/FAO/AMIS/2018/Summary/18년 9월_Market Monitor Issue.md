# 비정형 요약 — 18년 9월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `18년 9월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2018` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 19 |
| 추출 문자 수 | 54,479 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 수출규제, 압착, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 59 · 하방어 44) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, EU, Ukraine, Korea, Export Tax, Import Duty, ENSO Phase, Palm Oil

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 수출규제, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

1 No.61 – September 2018 AMIS Market Monitor
Feature article
Currency depreciations pose further challenge to food market stability
As the 2017/18 season gradually unfolds, it is becoming increasingly clear that agricultural markets are in rougher
shape than in previous years. Several factors are at play. While policy developments such as the US-China trade
dispute (the focus of July’s featured article) have loomed over markets for the past couple of months, more recently
heat waves and prolonged dry conditions in several parts of the world have introduced new risks by sharply reducing
the expected production of wheat and other crops. A less apparent but potentially very destabilizing factor is the
drastic depreciation of several emerging market currencies against the US dollar, the most widely traded currency.
In 2018, most currencies have weakened against the dollar, but emerging economies have been particularly hard hit.
The Argentinean peso is almost 60 percent lower since the beginning of the year while the Brazilian real and the
Russian ruble have lost more than one fifth and one sixth of their values, respectively. Considering that all of these
countries are major exporters of agricultural commodities, the importance of these currency depreciations for global
food markets cannot be overstated.
A case in point is Brazil. In normal times, the sharp drop in international soybean prices – denominated in US dollars –
would be a signal for a large exporter to produce and sel

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*