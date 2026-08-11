# 비정형 요약 — 23년 9월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `23년 9월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2023` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 17 |
| 추출 문자 수 | 91,500 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 53 · 하방어 33) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Argentina, Brazil, Indonesia, India, China, Ukraine, Black Sea Corridor, ENSO Phase

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 111 September 2023
Your feedback matters,
tell us how we can
better serve you. The war in Ukraine and India's export re-
Contents
Click here to take the survey!
strictions on rice have dominated commod-
Feature article:
Fuelling food prices: the role of ity news in recent weeks. In late July, India
fertilizer prices 2
announced a ban on non-Basmati rice ex-
World supply-demand outlook 3
ports and has since then imposed further
Crop monitor 5
restrictions on Basmati and parboiled rice
Policy developments 8
exports. Those restrictions, combined with
International prices 10
El Niño-related concerns over rice produc-
Futures markets 12 tion in the region, have roiled rice markets,
Market indicators 13 with Thai prices rising 20 percent since last
Fertilizer outlook 15 month. Wheat prices are still under pressure
from abundant Black Sea exports at com-
Ocean freight markets 16
petitiveprices,butmarketsremainvolatileas
Explanatory notes 17
the termination of the Black Sea Grain Initia-
Markets at a glance
tive and Russian attacks on Ukraine export
FROM FROM
Easing
Neutral PREVIOUS PREVIOUS
Tightening FORECASTS SEASON facilities have heightened uncertainty. Global
WHEAT soybean and maize production prospects
MAIZE
are improved this year with some stock re-
RICE
building anticipated despite dryness in North
SOYBEANS
America, Argentina and parts of Europe.
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international m

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*