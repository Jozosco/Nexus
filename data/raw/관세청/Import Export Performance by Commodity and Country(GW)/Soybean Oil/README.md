# 관세청 GW — 대두유(Soybean Oil) HS코드별 업로드 폴더

파일명이 동일해 혼동 방지를 위해 HS 10단위·용도별 하위폴더로 분리 (조정자 지정).

| HS | 용도 | 폴더 |
|---|---|---|
| 1507.10 | 바이오디젤 제조용 (.2000) | `1507.10/Biodiesel production (.2000)/` |
| 1507.10 | 식품용 조유 (.1000) | `1507.10/Food use (.1000)/` |
| 1507.90 | 바이오디젤 제조용 정제 (.1020) | `1507.90/Biodiesel production (.1020)/` |
| 1507.90 | 식품용 정제 (.1010) | `1507.90/Food use (.1010)/` |
| 1507.90 | 정제유 (.10) | `1507.90/(Whole) Refined Soybean Oil (.1090)/` |

- 집계: 수입=CIF USD, 수출=FOB USD · 중량=순중량(kg) · 월별
- 파서: scripts/ingest_customs_gw_xlsx.py (env DATA_GO_KR_SERVICE_KEY)
| `1507.90/Soya-bean Oil Fractions (.9000)/` | 1507909000 | 대두유 분획물 (실데이터 보유 — A-196 정정) |
