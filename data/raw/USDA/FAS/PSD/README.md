# USDA FAS PS&D

USDA FAS Production, Supply & Distribution 데이터

## 파일 목록
- `Oil, Soybean.xlsx` — 대두유 공급/수요 밸런스 (국제 무역 포함) ✅ 사용
- `Oilseed, Soybean.xlsx` — 대두(원료) 공급/수요 밸런스 ✅ 사용
- `Meal, Soybean.xlsx` — 대두박 밸런스 (압착 마진 계산용) ✅ 사용
- `Oil, Soybean (Local).xlsx` — 수공업 생산분, 무역 비포함 ❌ 모델 제외

## 주의
`Oil, Soybean (Local)`은 국제 무역에 진입하지 않는 소규모 생산분으로 G1/G2/G3 모델에서 제외됩니다.
상세: `docs/research_desk/c01_p101_psd_local_vs_standard_2026_06_17.md`

## 처리 스크립트
`scripts/ingest_psd_data.py`
