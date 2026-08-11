# 비정형 요약 — 19년 2월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `19년 2월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2019` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 19 |
| 추출 문자 수 | 46,064 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 41 · 하방어 33) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, Malaysia, India, China, EU, Ukraine, Korea, WASDE Surprise, ENSO Phase

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

1 No.65 – February 2019 AMIS Market Monitor
The China Conundrum
The editorial in the previous issue of this report described the challenge of accommodating recent large official
revisions to China’s annual cereal production data in the country’s cereal balance sheets following the outcome of
the country’s first agricultural census in 10 years. In particular, the editorial provided a cursory look into the
challenge of distributing the 10-year cumulative increase in cereal supplies of 312 million tonnes over the various
forms of utilization. In the absence of any official information on current and historic levels of the different types of
utilization, namely, food, feed, industrial, seed and losses, the challenge borders on the insurmountable.
Alternatively, the temptation to simply add the majority of the increase to stocks would lead to incredulity, since
this would bring a question mark over China’s physical capacity and economic incentive to hold on to such large
amounts of grain.
However, employing an accounting framework, which serves to guide the distribution of the additional supply to
utilization, is considered a way forward. The essence of the framework is to ‘triangulate’ elements of the cereal
balance with information from interconnected sectors. In the case of cereals, livestock constitutes the ‘standout’
sector. Indeed, in China’s cereal basket, maize production underwent the largest cumulative revision, an increase of
266 million tonnes in 10 years from 2008-201

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*