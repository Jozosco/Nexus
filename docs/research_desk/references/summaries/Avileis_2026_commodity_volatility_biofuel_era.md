# 요약 — Avileis, *Commodity Price Volatility in the Biofuel Era* (UC Davis ARE 세미나 워킹페이퍼, 2026-01)

> ⚠️ **원문 미회수**: PDF(arefiles.ucdavis.edu, 2026-01-09)와 세미나 페이지(2026-01-16)는 실행 환경의 네트워크에서 열람이 차단됐다. 본 요약은 **검색 발췌문(초록 문장)** 과 적대 검증(2026-09-25)에 근거한 골격이며, 원문 회수 후 `scripts/pdf_to_markdown.py` 변환 → 정식 요약으로 교체한다(references 규칙).
> 정직 분류: **배경** — 비심사 워킹페이퍼. 수치는 '저자 추정'으로만 병기하고 모델 파라미터로 사용하지 않는다.

## 서지·메타
- 저자: Felipe G. Avileis (소속 University of Nebraska–Lincoln 교원, UC Davis 박사 2025 — 검증 ③-1). 선행판: Avileis & Swanson, *Drivers of Commodity Volatility in the Biofuel Era*, NCCC-134 2025.
- 형태: 워킹페이퍼(비심사) · 표본: 내재변동성 1996~2024.
- 공유 경로: 시장구조 조사(A-281) — `docs/research_desk/2026-09/market_structure_update_2026_09_25.md` §4 A1.

## 핵심 주장(발췌 기준)
- 바이오연료 의무가 에너지 수요충격의 비중을 키우고, **의무수요가 수요곡선을 가파르게 만들어** 대두유 가격 변동성을 구조적으로 높였다.
- 대두유 변동성은 2021년 재생디젤 붐 이후 **수출 대체(export displacement) 국면**에서 상승했고, 에너지→농산물 변동성 전이가 강화됐다.
- 수치(저자 추정, 판본 의존): 대두유 내재변동성 **+19%**(2026-01판) · 2025 NCCC-134판은 옥수수 +19%/대두유 +18%.

## Nexus 관련성
- G2 변동성 층(EGARCH-X, AM-09): 정책 국면 더미·에너지 전이 항의 설계 근거(정성). CE-020·CE-022 evidence.
- 식별 전략(DID형·내재변동성)은 조달 도메인 변수와 다르므로 이식 대상이 아니다.

## 온톨로지 반영
- `src/semantic/methods.yaml` MP-18(배경) · `ontology.yaml` CE-020 evidence(A-281).

## 미확인(DATA GAP)
- 원문 표·식별식·표본 구성 · 심사 저널 투고 여부.
