# 비정형 요약 — 21년 7월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `21년 7월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2021` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 17 |
| 추출 문자 수 | 42,800 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 생산변동, 수출규제, 압착, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 55 · 하방어 30) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, EU, Ukraine, Export Tax, ENSO Phase

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 생산변동, 수출규제, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Contents
Message from the Chair: Building a stronger AMIS.....1
World supply-demand outlook .......................................... 2
Crop monitor ............................................................................ 4
Policy developments .............................................................. 7
International prices ................................................................ 9
Futures market (US) ............................................................. 11
Market indicators .................................................................. 12
Fertilizer outlook ................................................................... 14
Ocean freight markets ......................................................... 15
Explanatorynotes.................................................................16
M A R K E T
M O N I T O R
No. 90 – July 2021
Markets at a glance
Production prospects for AMIS crops remain generally
favourable for 2021/22 and despite expectation of
stronger demand, the overall outlook points to a more
From previous From previous
comfortable supply situation in the new season as
forecast season
compared to 2020/21. In fact, prices in international
Wheat
markets have declined from their recent peaks due in part
to more reassuring fundamental factors. However, with
Maize
weather risks still posing threats to major producers,
Rice
inflation fears encouraging speculative purchases, energy
prices firming, and pandemic-induced uncertainties
Soybe

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*