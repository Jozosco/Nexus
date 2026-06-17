# USDA FAS GATS

Global Agricultural Trade System — 미국 대국가별 대두유 수출/재수출 통계

## HS 코드
1507 (대두유, crude + refined)

## 파일 명명 규칙
- 수출: `YYYY년 미국 對국가별 수출량.xlsx`
- 재수출: `YYYY년 미국 對국가별 재수출량.xlsx`

## 수집 범위
2017년 ~ 2026년 (2026년은 4월까지)

## 결측
2018년 재수출량 파일 없음 → 해당 연도 재수출 = 0 처리

## 처리 스크립트
`scripts/ingest_gats_data.py`
