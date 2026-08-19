# Market Structure (Production & Distribution)

**목적**: 대두유(및 관련 유지류 원료)의 **생산·유통을 담당하는 기업별 데이터 보관** 폴더.
조정자 지시(2026-08-19)로 신설.

## 기준 문서 (anchor)
- `Global Oilseeds & Fats Market Structure_26.08.19.docx` — 조정자 업로드 시장구조 브리프
  (컷오프 2026-08-19 17:41 KST · 출처 38종 · CONFIRMED/INFERENCE/DATA GAP 3등급 체계)
- Perplexity Deep Research 교차검증: `docs/research_desk/2026-08/market_structure_deep_verify_*.md`
- 관련 조사: `docs/research_desk/2026-08/abcd_trading_structure_2026_08_15.md` (D-044)

## 폴더 구조
회사별 하위 폴더에 해당 기업의 공시·자산 목록·수출 실적·터미널 tariff 등 원문 자료를 보관한다.

## 판독 규율 (기준 문서 §How to read — 전 단계 공통 적용)
| 라벨 | 의미 |
|---|---|
| CONFIRMED | 공식 통계·공시·1차 기업 출처 — 명시된 범위에서만 유효 |
| INFERENCE | 공시 자산·통상 항로로부터의 해석 — B/L·AIS 없이는 거래 사실 아님 |
| DATA GAP | 공개 검증 불가 — 물량·거래상대·조건을 추정하지 않음 (0 아님) |
| NOT COMPARABLE | 기간·등급·기준·단위 상이 — 방향성 참고만 |

**핵심 규칙**: capacity ≠ throughput(치환·합산 금지) · 관세청 CIF 단가 ≠ CFR 호가 ·
DJVE(판매등록) ≠ 선적 · 부분연도(4개월) ≠ 연간 구조 · 월별 수입 합계 ≠ 개별 화물 크기
