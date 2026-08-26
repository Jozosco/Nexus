# 1201.90-1000 — Crushing & Meal

- **판정**: ★필수 — 채유·탈지대두박용(⚠️콩나물용 아님). 국내 압착 원료 직결
- **권장 국가**: US·BR·AR (+CN·CA 보조)
- **상태**: 실측 검증 대기(API 프로빙 예정 — hs_code_classification_2026_08_25.md §6)
- 파일 규칙(A-184): 조정자 업로드 = `{국가}.xlsx` · API 수집 = `{국가}_API.xlsx`
- 형식: 연도 시트(2010~) × 월 행 × 5지표 열(무역수지·수출액·수출량·수입액·수입량)


## 수작업 수집 현황 (2026-08-26 — 조정자)

국가별 파일 7개(AR·BR·CN·MY·PY·US·VN, 각 2010~2026년 17시트) — 루트에서 본 폴더로
이동(2026-08-26). **무역 부재로 파일 미생성 3개국: Indonesia·Netherlands·Spain** —
API 전 기간 프로빙으로 교차검증(probe_customs_absent_pairs · 결과는
reports/market/customs_absent_pairs_verification_*.md).
