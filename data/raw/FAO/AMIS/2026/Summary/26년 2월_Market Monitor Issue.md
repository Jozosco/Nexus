# 비정형 요약 — 26년 2월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `26년 2월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2026` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 20 |
| 추출 문자 수 | 66,714 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 바이오연료수요, 수입관세, 수출규제, 압착, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 59 · 하방어 44) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Import Volume, Export Volume, Heatwave, Soil Moisture Percentile, Planted Area, Marketing Year, Soybean, Crude Palm Oil, Canola Oil, Bear Regime, Neutral Regime, Freight Rate

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 바이오연료수요, 수입관세, 수출규제, 압착, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 135 February 2026
Contents
Grains and oilseeds export prices edged
Feature article:
Stability in an unstable world 2 slightlylowerinJanuary,withtheIGC’sGrains
World supply-demand outlook 3 and Oilseeds Index reflecting ample global
Crop monitor 5 supplies and year‑on‑year declines across
Policy developments 8 most commodities except soybeans. Fertil-
izerpricescontinuedtoeaseovermajornutri-
International prices 11
ents, although urea prices remained elevated
Futures markets 13
due to rising natural gas costs. As Febru-
Market indicators 14
ary 2026 begins, market fundamentals and
Fertilizer outlook 16
prevailing uncertainties point to a cautiously
Vegetable oils 18
stable outlook. Robust supplies, diversified
Ocean freight markets 19
trade flows and adequate inventories suggest
Explanatory notes 20
that the agrifood system can absorb mod-
erate shocks. However, this stability should
Markets at a glance
not be taken for granted. Unexpected dis-
Easing FROM FROM
Neutral PREVIOUS PREVIOUS
ruptions could quickly increase volatility, un-
Tightening FORECASTS SEASON
WHEAT derscoring the importance of open trade and
MAIZE
greater transparency. Ongoing vigilance and
RICE
sound policy choices will be essential for sus-
SOYBEANS
taining market stability.
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*