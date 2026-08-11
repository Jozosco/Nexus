# 비정형 요약 — 18년 11월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `18년 11월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2018` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 18 |
| 추출 문자 수 | 48,946 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 50 · 하방어 35) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, EU, Ukraine, Korea, WASDE Surprise, ENSO Phase, Rapeseed Oil

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 수입관세, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

1 No.63 – November 2018 AMIS Market Monitor
Untapping the potential for wider use of Earth Observation
in mon it or in g a gr ic u lt u r e p r odu c t i on
There is international consensus that timely and transparent information on crop conditions and production
prospects is more critical than ever. Such information has a key role to play in ensuring market transparency and
stability, providing early warning of food shortages to guide humanitarian responses, and informing national agricultural
policies as well as field scale decisions, to name a few.
Where in the past remote-sensing (RS) based information provided crude crop condition and production indicators
at best, current satellite data and information technologies are increasingly offering cost-effective and timely
information on crop type and health, growth stage, and productivity from the field to global scales. Today, we are in a
new era of satellite data availability with major advances in capability with respect to just three years ago, and it’s
revolutionizing both the RS field and the ability of the agricultural monitoring community to provide accurate, timely
information across cropping systems at scale.
In this context, satellite technologies are playing an increasingly central role across the agricultural sector, from
informing government policies and humanitarian aid, to supporting precision agriculture and insurance decisions, and
to monitoring progress towards agricultural intensification for more sustaina

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*