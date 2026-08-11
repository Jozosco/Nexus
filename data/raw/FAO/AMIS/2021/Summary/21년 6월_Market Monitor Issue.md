# 비정형 요약 — 21년 6월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `21년 6월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2021` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 16 |
| 추출 문자 수 | 39,193 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 생산변동, 압착, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 57 · 하방어 18) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, EU, Ukraine, Suez Disruption, ENSO Phase, Palm Oil, Rapeseed Oil

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 생산변동, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Contents
Feature article: Price formation ..................................... 1
World supply-demand outlook .................................... 2
Crop monitor ......................................................................... 3
Policy developments .......................................................... 6
International prices ............................................................. 8
Futures market (US) ......................................................... 10
Market indicators.............................................................. 11
Fertilizer outlook ............................................................... 13
Ocean freight markets.................................................... 14
Explanatory notes ............................................................. 15
M A R K E T
M O N I T O R
No. 89 – June 2021
Markets at a glance
Despite an overall favourable production outlook,
global supplies of AMIS crops could still prove
vulnerable in 2021/22, in particular because of
From previous From previous
uncertainties relating to demand from the feed and
forecast season
industrial sectors. The month of May registered yet
Wheat
another increase in international prices of most
food commodities, underpinned by brisk trade and Maize n/a
a weaker dollar. The coming months will be critical
Rice n/a
for how food markets evolve. Global grain and
soybean inventories could prove barely sufficient in
Soybeans n/a
case of a major production shortfall, whi

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*