# Trading Economics — Markets / Commodities (2017~2026 히스토리)

Trading Economics 제공 9개년(2017.01.01~2026.07.01) 상품 시세 히스토리 xlsx.
TE API 실시간 수집 불안정(요청 근거)으로 수동 업로드 히스토리를 1차 소스로 사용.

## 폴더 구조

| 폴더 | 품목 | 대두유 분석 역할 |
|---|---|---|
| `Agricultural/` | Canola·Palm Oil·Rapeseed·Soybeans·Sunflower Oil | 대체재(유지류) 스프레드·보완재(대두) 크러시 |
| `Energy/` | Brent·WTI·Coal·(EU/UK/US) Natural Gas·Gasoline | 바이오디젤 채널·운임 원가(벙커유) |
| `Shipping Indices/` | BDI·Containerized Freight Index | 해상 운임 충격 → CIF 원가 |

- 파일명: `YYYY~YYYY_{Commodity}_{Exchange}_{Units}.xlsx`
- 시트명: `YYYY년` (연도별 시트)
- 파서: scripts/ingest_te_xlsx.py (연도 시트 → 롱포맷 parquet)
