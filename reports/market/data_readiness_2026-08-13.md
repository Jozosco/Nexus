# 데이터 준비도 감사 — 2026-08-13

**분석창**: 2010-01-01 ~ 2025-12-31 (192개월, M-008)
**보유 지표 수**: 432종

> 이 문서는 추정이 아니라 **실제 parquet을 열어 확인한 사실**이다.

## 1. 모델 착수 요건 — 핵심 8변수 + 목표변수

| 요건 | 상태 | 지표코드 | 관측 개월 | 커버리지 | as-of | 조달 경로 |
|---|---|---|---|---|---|---|
| 목표변수 — CBOT 대두유 선물 종가 | 🚨 **미보유** | — | — | — | — | Historical Analysis Pipeline · connector=databento |
| ① CBOT 대두유 선물 | 🚨 **미보유** | — | — | — | — | Historical · connector=databento |
| ② CPO(팜유) — CPO–SBO 스프레드 재료 | ✅ | `TE_PALM_OIL` | 192/192 | 100% | ✅ | te_commodities_historical.parquet |
| ③ WASDE 대두유 재고사용비율 | ✅ | `WASDE_SBO_STU` | 186/192 | 97% | ✅ | wasde_historical.parquet |
| ④ BDI 해운지수 | ✅ | `TE_BDI` | 192/192 | 100% | ✅ | te_commodities_historical.parquet |
| ⑤ FX BRL/USD | 🚨 **미보유** | — | — | — | — | Data Integration · connector=economic |
| ⑥ ENSO ONI | 🚨 **미보유** | — | — | — | — | Data Integration · connector=climate |
| ⑦ 대두 압착량 | ✅ | `WASDE_SOY_CRUSH` | 186/192 | 97% | ✅ | wasde_historical.parquet |
| ⑧ GATS 미국→한국 대두유 수출 | ✅ | `GATS_US_SBO_EXPORT_KOREA` | 192/192 | 100% | ✅ | gats_quantity_historical.parquet |

## 2. 판정

🚨 **모델 착수 불가 — 미충족 4건**

c03 스펙 §6 모델 진입 게이트는 목표가격 ≥98%·핵심 피처 커버리지 ≥85%를 요구한다.
아래가 해소되기 전 G1 동인분석·G2 가격밴드는 **의미 있는 결과를 낼 수 없다**.

- 목표변수 — CBOT 대두유 선물 종가 → Historical Analysis Pipeline · connector=databento
- ① CBOT 대두유 선물 → Historical · connector=databento
- ⑤ FX BRL/USD → Data Integration · connector=economic
- ⑥ ENSO ONI → Data Integration · connector=climate

## 3. 보유 지표 요약 (관측 상위 25)

| 지표코드 | 행 수 | 기간 | 분석창 개월 | as-of |
|---|---|---|---|---|
| `TE_BRENT_CRUDE_OIL` | 4,415 | 2010-01-01~2026-07-01 | 192 | ✅ |
| `TE_ETHANOL` | 4,373 | 2010-01-01~2026-07-01 | 192 | ✅ |
| `TE_WTI_CRUDE_OIL` | 4,369 | 2010-01-04~2026-07-01 | 192 | ✅ |
| `TE_GSCI` | 4,317 | 2010-01-01~2026-07-01 | 192 | ✅ |
| `TE_CRB_INDEX` | 4,293 | 2010-01-01~2026-07-01 | 192 | ✅ |
| `TE_NATURAL_GAS` | 4,280 | 2010-01-01~2026-07-01 | 192 | ✅ |
| `TE_CORN` | 4,254 | 2010-01-01~2026-07-01 | 192 | ✅ |
| `TE_HEATING_OIL` | 4,251 | 2010-01-04~2026-07-01 | 192 | ✅ |
| `TE_EU_CARBON_PERMITS` | 4,244 | 2010-01-04~2026-07-01 | 192 | ✅ |
| `TE_WHEAT` | 4,240 | 2010-01-01~2026-07-01 | 192 | ✅ |
| `TE_GASOLINE` | 4,238 | 2010-01-04~2026-07-01 | 192 | ✅ |
| `TE_UK_NATURAL_GAS` | 4,227 | 2010-01-04~2026-07-01 | 192 | ✅ |
| `TE_SUGAR` | 4,201 | 2010-01-04~2026-07-01 | 192 | ✅ |
| `TE_SOYBEANS` | 4,192 | 2010-01-04~2026-07-01 | 192 | ✅ |
| `TE_RAPESEED` | 4,182 | 2010-01-04~2026-07-01 | 192 | ✅ |
| `TE_BDI` | 4,148 | 2010-01-04~2026-07-01 | 192 | ✅ |
| `TE_NAPHTHA` | 4,146 | 2010-01-04~2026-07-01 | 192 | ✅ |
| `TE_COAL` | 4,099 | 2010-01-01~2026-07-01 | 192 | ✅ |
| `TE_CANOLA` | 4,085 | 2010-01-04~2026-07-01 | 192 | ✅ |
| `TE_PALM_OIL` | 4,062 | 2010-01-04~2026-07-01 | 192 | ✅ |
| `TE_EU_NATURAL_GAS` | 3,868 | 2010-03-12~2026-07-01 | 190 | ✅ |
| `TE_SUNFLOWER_OIL` | 3,641 | 2012-05-25~2026-07-01 | 164 | ✅ |
| `TE_CONTAINERIZED_FREIGHT_INDEX` | 3,338 | 2013-09-06~2026-07-01 | 148 | ✅ |
| `TE_DI_AMMONIUM` | 1,745 | 2019-06-07~2026-07-01 | 79 | ✅ |
| `TE_UREA` | 1,675 | 2019-06-07~2026-07-01 | 78 | ✅ |

## 4. as-of 미충족 지표

**0종** — `available_at` 없는 피처는 모델 투입 금지(CLAUDE.md §1)
