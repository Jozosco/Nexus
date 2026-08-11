# 비정형 요약 — 23년 10월_Market Monitor Issue.pdf

## 1. 문서 기본정보 (템플릿 §1.1/§1.2 — C-04)
| 항목 | 내용 |
|---|---|
| 파일명 | `23년 10월_Market Monitor Issue.pdf` |
| 문서 경로 | `data/raw/FAO/AMIS/2023` |
| 판독 상태 | ✅ 정상 |
| PDF 전체 페이지 | 17 |
| 추출 문자 수 | 90,838 |
| 발행일·기준 시점 | 미확인(파일명 연·월 참조) |

## 2. 핵심 판단 요약표 (템플릿 §2.2 — P1-05)
| 항목 | 값 |
|---|---|
| aspect 신호 태그 | 기상이변, 물류충격, 생산변동, 수입관세, 수출규제, 재고 |
| 방향성(SBO 가격 기준) | 상방 우세 (상방어 50 · 하방어 32) |
| 신뢰도 | 자동(키워드 기반) — LLM 정밀 스코어는 Phase B |

## 3. 관련 국가·엔티티 (템플릿 §3.1 — P1-06)
- 정규 엔티티 후보: Inflation, Import Volume, Export Volume, Flood, Stock-to-Use Ratio, Soybean, Bear Regime, Neutral Regime, Freight Rate, Import Tariff, Export Tax, Policy Pivot

## 5. 인과 신호 (템플릿 §5.1 — 원인→메커니즘→가격 매핑은 P1-06 온톨로지 참조)
- 감지 신호: 기상이변, 물류충격, 생산변동, 수입관세, 수출규제, 재고 → src/semantic/causal_chains.md 의 해당 체인 참조

## 근거 발췌 (템플릿 원칙 2 — verbatim provenance)

Market
Monitor
No. 112 October 2023
Rice continues to be in the news. Since In-
Contents
dia banned non-Basmati rice exports in July,
Feature article:
Impact of rising interest rates on grain rice prices have risen markedly, raising con-
markets 2
cerns that other countries might follow suit
World supply-demand outlook 3
and also restrict trade. As a case in point,
Crop monitor 5
Myanmar, the world's sixth largest rice ex-
Policy developments 8
porter, announced new export licensing re-
International prices 10
quirements while the Philippines has put in
Futures markets 12 placepriceceilingstocapretailriceprices.All
Market indicators 13 oftheseactionshaveoccurredasastrength-
Fertilizer outlook 15 ening El Niño threatens to cut rice produc-
tion of key Asian suppliers and push prices
Ocean freight markets 16
higher. ASEAN leaders have recognized the
Explanatory notes 17
threattofoodsecurityandrecentlyconfirmed
Markets at a glance
theircommitmenttokeeptheflowofagricul-
FROM FROM
Easing
Neutral PREVIOUS PREVIOUS
Tightening FORECASTS SEASON tural products unimpeded and refrain from
WHEAT using "unjustified" trade barriers. AMIS will
MAIZE
continue working with its participating coun-
RICE
tries to promote the open flow of food com-
SOYBEANS
modities.
The Market Monitor is a product of the Agricultural Market Information System (AMIS). It covers international markets for wheat, maize, rice
and soybeans, giving a synopsis of major market developments and the policy and other market 

## 미작성 섹션 (템플릿 원칙 4)
- 경영진 요약(§2.1)·수급/가격 전망(§6)·한국 관점 해석(§7): **미확인 — 자동 단계에서는 미작성**
  (LLM 정밀 요약 Phase B에서 작성 예정. 원문에 없는 값 추정 금지)

---
*자동 생성: scripts/summarize_pdfs.py v2 · 템플릿: .claude/agents/비정형데이터 요약본 Template.md*