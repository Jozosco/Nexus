# Feature Mart 생성 결과 — 2026-08-13

- 분석창: 2010-01-01 ~ 2025-12-31 · 거래일 **4,174일**
- 목표변수: **🚨 미보유 — 타깃 컬럼 전량 결측**
- 원천 지표 432종 → 파생 포함 피처 **1,655열**
- 산출: `data/gold/feature_mart.parquet` (4,174행 × 1,661열)

## 커버리지 분포

| 구간 | 지표 수 |
|---|---|
| 90% 이상 | 308 |
| 70~90% | 47 |
| 40~70% | 52 |
| 40% 미만 | 25 |

## 개정 오염 피처 (revision-contaminated)

> 해당 소스는 값을 개정하는데 **우리는 개정 전 값을 갖고 있지 않다**.
> 즉 백테스트가 '당시 알 수 없었던 확정치'를 쓰고 있다. 제거가 아니라
> **표기 + 민감도 검증**(해당 피처 제외 성능 비교)이 필요하다.

대상 **94종**: `GATS_US_HSBO_EXPORT_CANADA`, `GATS_US_HSBO_EXPORT_CHINA`, `GATS_US_HSBO_EXPORT_COLOMBIA`, `GATS_US_HSBO_EXPORT_INDIA`, `GATS_US_HSBO_EXPORT_JAPAN`, `GATS_US_HSBO_EXPORT_KOREA`, `GATS_US_HSBO_EXPORT_MEXICO`, `GATS_US_HSBO_EXPORT_TOTAL`, `GATS_US_HSBO_REEXPORT_CANADA`, `GATS_US_HSBO_REEXPORT_CHINA`, `GATS_US_HSBO_REEXPORT_COLOMBIA`, `GATS_US_HSBO_REEXPORT_INDIA`, `GATS_US_HSBO_REEXPORT_JAPAN`, `GATS_US_HSBO_REEXPORT_KOREA`, `GATS_US_HSBO_REEXPORT_MEXICO`, `GATS_US_HSBO_REEXPORT_TOTAL`, `GATS_US_RSBO_4020_EXPORT_CANADA`, `GATS_US_RSBO_4020_EXPORT_CHINA`, `GATS_US_RSBO_4020_EXPORT_COLOMBIA`, `GATS_US_RSBO_4020_EXPORT_INDIA`, `GATS_US_RSBO_4020_EXPORT_JAPAN`, `GATS_US_RSBO_4020_EXPORT_KOREA`, `GATS_US_RSBO_4020_EXPORT_MEXICO`, `GATS_US_RSBO_4020_EXPORT_TOTAL`, `GATS_US_RSBO_4020_REEXPORT_CANADA` …

## 발표 이벤트가 적은 지표 (이월값 주의)

> 결측률 기준 커버리지는 높아도 **실제 갱신 횟수**가 적으면 대부분이 이월값이다.
> 커버리지 게이트를 이월값으로 통과시키지 않기 위한 대조 지표.

| 지표 | 발표 횟수 | 결측률 기준 커버리지 |
|---|---|---|
| `PSD_SBM_BEGINNING_STOCKS` | 9 | 51.4% |
| `PSD_SBM_DOMESTIC_USE` | 9 | 51.4% |
| `PSD_SBM_ENDING_STOCKS` | 9 | 51.4% |
| `PSD_SBM_EXPORTS` | 9 | 51.4% |
| `PSD_SBM_IMPORTS` | 9 | 51.4% |
| `PSD_SBM_PRODUCTION` | 9 | 51.4% |
| `PSD_SBM_STU` | 9 | 51.4% |
| `PSD_SBM_TOTAL_DISTRIBUTION` | 9 | 51.4% |
| `PSD_SBM_TOTAL_SUPPLY` | 9 | 51.4% |
| `PSD_SBO_BEGINNING_STOCKS` | 9 | 51.4% |
| `PSD_SBO_DOMESTIC_USE` | 9 | 51.4% |
| `PSD_SBO_ENDING_STOCKS` | 9 | 51.4% |
| `PSD_SBO_EXPORTS` | 9 | 51.4% |
| `PSD_SBO_IMPORTS` | 9 | 51.4% |
| `PSD_SBO_PRODUCTION` | 9 | 51.4% |
| `PSD_SBO_STU` | 9 | 51.4% |
| `PSD_SBO_TOTAL_DISTRIBUTION` | 9 | 51.4% |
| `PSD_SBO_TOTAL_SUPPLY` | 9 | 51.4% |
| `PSD_SOY_BEGINNING_STOCKS` | 9 | 51.4% |
| `PSD_SOY_CRUSH` | 9 | 51.4% |

## 신선도 상한 초과 (수집 중단 의심)

> 상한을 넘긴 값은 결측 처리했다. 굳어버린 상수를 모델이 학습하는 것보다
> 결측이 안전하다.

| 지표 | 제외 일수 | 상한(일) | 최대 경과(일) |
|---|---|---|---|
| `ICE_EU_DUTCH_TTF_GAS_FUTURES` | 3,811 | 139 | 5474 |
| `ICE_EU_NAT_GAS_FUTURES` | 3,811 | 139 | 5474 |
| `WASDE_US_CORN_ETHANOL_USE` | 3,763 | 139 | 5408 |
| `WASDE_USDOM_SBO_BIODIESEL_USE` | 3,742 | 139 | 5377 |
| `ICE_US_CRB_CCI_INDEX_FUTURES` | 3,550 | 139 | 5109 |
| `ICE_EU_EMISSIONS_OPTIONS` | 3,550 | 139 | 5109 |
| `ICE_US_OTHER_FUTURES` | 3,550 | 139 | 5109 |
| `ICE_US_NYSE_INDEX_OPTIONS` | 3,550 | 139 | 5109 |
| `ICE_US_US_INDEX_OPTIONS` | 3,550 | 139 | 5109 |
| `ICE_US_OTHER_OPTIONS` | 3,550 | 139 | 5109 |
| `ICE_US_CRB_INDEX_OPTIONS` | 3,550 | 139 | 5109 |
| `ICE_EU_ELEC_FUTURES` | 3,550 | 139 | 5109 |
| `ICE_EU_COAL_FUTURES` | 3,550 | 139 | 5109 |
| `ICE_US_US_CRB_FUTURES` | 3,288 | 139 | 4743 |
| `ICE_US_US_CRB_OPTIONS` | 3,288 | 139 | 4743 |
| `ICE_EU_OTHER_OPTIONS` | 3,028 | 139 | 4378 |
| `ICE_EU_RBOB_GASOLINE_FUTURES` | 3,028 | 139 | 4378 |
| `ICE_US_RUSSELL_FUTURES` | 3,028 | 139 | 4378 |
| `ICE_US_GRAINS_OPTIONS` | 3,028 | 139 | 4378 |
| `ICE_US_GRAINS_FUTURES` | 3,028 | 139 | 4378 |
| `ICE_US_RUSSELL_OPTIONS` | 3,028 | 139 | 4378 |
| `ICE_EU_EMISSIONS_FUTURES` | 3,028 | 139 | 4378 |
| `ICE_EU_COAL_ELEC_FUTURES` | 3,028 | 139 | 4378 |
| `ICE_EU_HEATING_OIL_FUTURES` | 3,028 | 139 | 4378 |
| `PS_Buenos_Aires` | 2,265 | 139 | 3310 |
| `GATS_US_SBO_REEXPORT_TOTAL` | 2,243 | 139 | 3279 |
| `GATS_US_SBO_REEXPORT_CANADA` | 2,243 | 139 | 3279 |
| `GATS_US_SBO_REEXPORT_CHINA` | 2,243 | 139 | 3279 |
| `GATS_US_SBO_REEXPORT_COLOMBIA` | 2,243 | 139 | 3279 |
| `GATS_US_SBO_REEXPORT_INDIA` | 2,243 | 139 | 3279 |

## 제외된 파일

- gain_historical.parquet — 필수 컬럼 없음 ['indicator_code', 'value']
- te_commodities_historical.parquet — 중복 제외: te_commodities_usd_mt.parquet가 동일 지표에 단위정규화(value_usd_mt)를 더한 상위집합 (D8)

