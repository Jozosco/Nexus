# 승인자 업로드 2종 편입 — BRL/USD 환율 15개년 · ENSO ONI 1950~ (2026-09-14 · A-266)

**판독 규율**: CONFIRMED(실측) / INFERENCE / DATA GAP. **원본 xlsx는 읽기 전용**(A-184) — 파서가 롱포맷 parquet를 만들고 준비도 잡이 매 실행 재구성한다.

## 1. 파일 실측 (CONFIRMED)

| 파일 | 구조 | 범위 | 특이사항 |
|---|---|---|---|
| `data/raw/15yrs Dataset_BRL_USD Exchange Rate.xlsx` | 연도 시트 17(2010년~2026년) · Month/Day/Price/Open/High/Low(+2019~2023 `Vol.`) | 2010-01-01~2026-09-14, 4,358행 | **값은 USD per BRL**(0.19~0.57) — 정본 FRED DEXBZUS(BRL per USD)의 역수 · 투자 포털(Investing.com) 원본 · Vol.은 2019(251)·2020(250)·2021(250)·2022(251)·**2023(18행, 1/25까지)** |
| `data/raw/1950~2026.xlsx` | 10년 시트 8(1950s~2020s) · Year/Month/Index | 1950-01~2026-07, 919개월 | NOAA PSL ONI(Niño3.4 5°N–5°S·170°W–120°W) · 2020s 시트는 2029-12까지 빈 행 · 파이프라인 API 계열(CPC oni.ascii.txt)과 값이 ~0.05~0.1 다를 수 있는 별도 vintage |

## 2. 편입 규약

| 항목 | BRL/USD | ENSO ONI |
|---|---|---|
| 파서 | `scripts/ingest_fx_brl_usd_xlsx.py` | `scripts/ingest_enso_oni_xlsx.py` |
| 지표 코드 | **`FX_BRL_USD`**(BRL per USD로 역수 통일, 원본 방향은 `fx_usd_per_brl` 보존) | **`ENSO_ONI`**(API `ONI`와 분리 — 같은 코드면 마트 값충돌 하드 실패, D-033) |
| 전처리 | 휴일 이월 행 제거(주말·OHLC 동일 94건) · 고/저가 역수 시 자리 교환 · Vol. `44.05K`→44,050 | 빈 Index 행 제거 · ±5 물리 가드 · 위상(El Niño/La Niña/Neutral) 파생 |
| as-of | `FX_BRL_` immediate·lag 1일·**revises=False** | `ENSO_ONI` monthly_on_day(10)·**revises=False**(업로드본 재산출 시 전량 재적재) |
| 산출 | `data/raw/fx_brl_usd_historical.parquet` 4,264행(2010-01-04~2026-09-11) | `data/raw/enso_oni_historical.parquet` 919개월 |
| 등록 | FILE_PATTERNS·C-08 매니페스트(선택)·readiness 파서/업로드·G1 복원·스키마 yaml | 동일 · G1 ONI 경보 블록은 ENSO_ONI 우선 → API ONI 폴백 · 브리프 스냅샷 `["ENSO_ONI","ONI"]` |

**준비도 판정(로컬 재실행, 2026-09-14)**: ⑤ FX BRL/USD ✅ 192/192개월 100% · ⑥ ENSO ONI ✅ 192/192개월 100% — 두 차단 항목 해소(잔여 1건 = 목표변수, CI 전용 산출).
**FRED DEXBZUS와의 값 대조**: 로컬은 FRED 파케이가 없어 미실시 — 다음 정기 실행의 마트 자체검증(동일 날짜 두 코드는 서로 다른 지표라 충돌 아님)과 스냅샷 표에서 병행 표기로 확인(DATA GAP → CI 판정).

## 3. 거래량 결측 — 무엇을 채울 수 있고 무엇을 못 채우는가 (정직 판정)

- 현물 환율은 집중 거래소가 없어 **'거래량'이 정의상 존재하지 않는다**. 투자 포털의 `Vol.`은 자사 피드의 틱 집계라 2010~2018·2023-02 이후·2024~2026을 **같은 정의로 복원할 수 있는 무료 소스는 없다(DATA GAP)**.
- 정직한 대안: **CME BRL/USD 선물(6L, 62,500 BRL) 일별 거래량을 별도 열 `volume_proxy_cme_6l`에 대리 지표로 채움**. 원본 `Vol.` 열은 그대로 두고, 동반 파일 `..._volume_filled.xlsx`(연도 시트 복제 + 대리 열·출처 열)로 제공. 정의가 다르므로 원본 구간과 수준 비교는 금지(NOT COMPARABLE) — 상대 변화·이벤트 반응 참고 전용.
- 실행: `scripts/fill_fx_volume_proxy.py` — yfinance `6L=F`는 샌드박스 프록시가 차단하므로 `fx_volume_proxy.yml`(원샷)이 Actions에서 실행·커밋한다. 6L 이력 깊이(2010년까지 닿는지)는 실행 로그로 판정하며, 부족 구간은 빈칸 유지 + 커버리지 보고서(`reports/market/fx_volume_proxy_{date}.md`). 야후 약관상 자동 수집은 회색 영역(무료 대안 인벤토리 A1 참조) — 대안은 Databento GLBX 6L ohlcv-1d(종량·승인 필요).

## 4. 소비자 반영

- 준비도·G1 경보·브리프 스냅샷·유사 시기 별칭(`ENSO_ONI__z252/z90`)·신뢰도 규칙(`col("ENSO_ONI","ONI")`)은 코드 변경 없이 새 코드를 본다.
- 유사 시기 참조는 개정 미보존 필터를 우회하는 비필터 레벨 경로(A-270)가 추가돼, 업로드 ONI가 없어도 원시 계열로 산출된다.
- 마트: `FX_BRL_USD`·`ENSO_ONI`가 피처로 편입(revises=False → 오염 표기 아님) — 다음 정기 실행에서 피처 수 증가 확인.
