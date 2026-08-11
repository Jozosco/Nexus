# 비정형 요약 — 19년 5월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `19년 5월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2019` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 18 |
| 추출 문자 수 | 44,103 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 수출규제, 압착, 재고 |
| 방향성(SBO 가격 기준) | 중립/혼재 (상방어 45 · 하방어 48) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, Ukraine, Korea, Export Tax, Import Duty, WASDE Surprise

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 수출규제, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

1 No.68 – May 2019 AMIS Market Monitor
Feature article
ASF: global challenges call for global collaboration
The rapid spread of African Swine Fever tandem, imports of cassava feed ingredients
(ASF) throughout East Asia has started to have fallen precipitously, while purchases
affect AMIS commodity markets. ASF is of barley and sorghum have almost come to
now endemic in China; it has recently a complete halt. Secondly, many of the ASF
spread to Viet Nam, Mongolia and affected countries are underequipped to
Cambodia and is likely to make inroads into contain the spread of the disease: their
other Asian countries. biosecurity situation needs to be improved,
their feeding and husbandry practices need
The FAO Emergency Prevention System
to change and their infrastructure
(EMPRES) monitors the ASF outbreak and
(slaughterhouses, transportation) needs to
provides regular updates on the speed and
be upgraded. This could take years to
extent of the spread. In doing so, EMPRES
materialize. Finally, the effects of ASF are
perfectly supplements AMIS, providing
compounded by other market distortions.
early warnings and issuing crisis prevention
Trade disputes, especially those between
measures. Together, the two systems offer a
the biggest trading partners, have spread
powerful and yet underutilised tool to
almost at the same pace as the disease.
capture - early on - the likely impacts of
They have added to and further exacerbated
animal diseases on commodity markets.
the effects of ASF; t

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*