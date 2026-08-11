# 비정형 요약 — 18년 10월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `18년 10월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2018` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 18 |
| 추출 문자 수 | 48,131 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 46 · 하방어 37) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, EU, Ukraine, Korea, Import Duty, ENSO Phase

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

1 No.62 – October 2018 AMIS Market Monitor
The Upside Down World of Soybeans: A Trader’s Perspective
For fifteen years, US farmers have responded to China’s inexorable demand for soybeans by nearly doubling their
output of the oilseed, even as other countries eagerly joined the soybean production race. While the flow of US
soybean sales to China reached about 36 million tonnes in 2016/17, today it has nearly halted.
In a retaliatory measure to US tariffs on a host of Chinese products, China imposed an additional 25 percent tariff on
soybeans coming from the US in July 2018. Previously unthinkable distortions to trade flows and prices have emerged
as a result. Compounded by a bumper soybean crop in the US, owing to favourable weather and near record soybean
acreage, US producers now face a triple price disadvantage: the soybean futures price plummeted to a ten-year low;
the cash basis quotes in multiple growing areas dropped to historically low levels; and the carrying charge from this
November to next has reached a record wide number. In other words, US producers selling soybeans during this fall
period are certain to make distressed sales.
China’s hog and chicken producers (China today is the largest hog producer and pork consumer in the world) have
also sustained economic burdens. Tariffs on US soybeans have caused soybean cargo prices originating from South
American countries such as Brazil to rise to historic premiums over US cargo prices of around USD 90 per tonne. This


## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*