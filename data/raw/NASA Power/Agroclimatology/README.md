# NASA POWER — Agroclimatology (주요 생산국 3대 산지, 2017~2025)

NASA POWER Single Point · Standard Resolution · Monthly · community=AG.
대두 주요 생산국별 3대 산지(재배 grow / 압착 crush)의 농업기상 히스토리.

| 국가 | 산지 (역할) |
|---|---|
| United States | Illinois(grow_crush)·Iowa(grow_crush)·Indiana(grow) |
| Brazil | MatoGrosso(grow_crush)·Parana(grow_crush)·MatoGrossodoSul(grow) |
| Argentina | Cordoba(grow)·SantaFe(crush)·Buenos Aires(grow) |
| China | Heilongjiang(grow)·Shandong(crush)·Jiangsu(crush) |

- 파일명: `YYYY~YYYY_{Region}_Agroclimatology Dataset(s).xlsx` · 시트: `YYYY년`
- 파라미터 10종: T2M·T2M_MAX·T2M_MIN·PRECTOTCORR·RH2M·ALLSKY_SFC_SW_DWN·
  ALLSKY_SFC_PAR_TOT·GWETROOT·GWETTOP 등 (열·수분·일사·토양수분)
- 파서: scripts/ingest_nasa_power_xlsx.py → nasa_power_agroclimatology_historical.parquet
