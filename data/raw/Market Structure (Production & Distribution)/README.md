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


## 브리프 보강 — 미·브·중 대두 삼각무역 20년 정량 (2026-08-29 통합, A-239)

원천: `docs/research_desk/references/farmdoc_2024_US_Brazil_China_soybean_triangle_20yr.pdf`
((14):35, 2024-02-20, Colussi·Schnitkey·Janzen·Paulson — 원문 판독 완료). D-047 브리프의
중국 축을 20년 실측으로 보강:

- **구조**: 미국+브라질 = 세계 대두 수출 80%+ · 중국 = 세계 수입 ~60%. 브라질 수출
  20년 4배(705→3,744백만 bu, 2023 기록) — 미국(1,789백만 bu)의 2배.
- **2018 무역전쟁 실측**(Case D 구조 근거 — CE-011 evidence 등재): 중국 25% 보복관세로
  미국 대두 수출의 對중 비중 60%→**18%** 급락 · 브라질 對중 비중 **82%** 피크. 이후
  미국 ~50% 회복(완전 회복 못함) — 관세 충격의 무역 재편은 **지속적**.
- **의존 비대칭**: 2019~23 브라질 수출의 73%가 對중 vs 미국 51% — 미국은 다변화·압착
  내수화(RD 붐), 브라질은 對중 집중. 중국 수입 정점론·5개년 자급 계획 병존.
- 판독 규율: 연도별 점유율은 달력연도(Secex·USDA) 기준 — 마케팅연도 수치와 혼용 금지.
