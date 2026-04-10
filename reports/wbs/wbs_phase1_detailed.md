# Phase 1 — Foundation: Detailed WBS
> **Version**: 1.0 · **Date**: 2026-04-10 · **Owner**: C-01 Senior PM
> **Phase Goal**: 모든 분석의 토대가 되는 데이터 파이프라인 구축 및 G1 변수 풀 확정
> **Total Estimated Effort**: ~520h
> **Dependencies**: 1.1 and 1.2 must be ≥ 80% complete before 1.3 can begin. 1.3 must be complete before 1.4. 1.4 must be complete before Phase 2 kickoff.

---

## Dependency Map

```
1.1 External Pipeline ──┐
                        ├──► 1.3 EDA ──► 1.4 Variable Pool ──► Phase 2
1.2 Internal Pipeline ──┘
                                          ↓
                                     1.5 Baselines (parallel with 1.4)
```

---

## 1.1 External Data Pipeline (~152h)
*담당 주요 에이전트: C-04 (인프라), P1-05 (API 설계)*
*선행조건: .env.template에 API 키 환경 변수 설정 완료*

### Deliverable: Snowflake Raw Schema
| WBS ID | 작업명 | 담당 | 공수 | 선행 | 상태 |
|---|---|---|---|---|---|
| 1.1.1 | Design Snowflake Raw Schema for External Indicators | C-04 + P1-05 | 16h | — | ⬜ |

**1.1.1 상세 산출물**:
- Snowflake DDL 스크립트: `soybean_oil.raw.economic_indicators`, `soybean_oil.raw.shipping_indices`, `soybean_oil.raw.crop_data`, `soybean_oil.raw.climate_data`, `soybean_oil.raw.geopolitical_indices`
- 각 테이블: `price_date DATE`, `source_name VARCHAR`, `indicator_code VARCHAR`, `value FLOAT`, `unit VARCHAR`, `ingested_at TIMESTAMP` 컬럼 포함
- YAML 스키마 파일: `data/schemas/external_*.yaml`

### Deliverable: Economic & Trade Connectors
| WBS ID | 작업명 | 담당 | 공수 | 선행 | 상태 |
|---|---|---|---|---|---|
| 1.1.2 | Implement Economic Indicators Connector (Fed, CPI, KRW/USD, WTI) | C-04 | 24h | 1.1.1 | ⬜ |
| 1.1.3 | Implement Shipping Index Connector (BDI, SCFI) | C-04 | 16h | 1.1.1 | ⬜ |

**1.1.2 데이터 소스 매핑**:
| 지표 | 소스 API | 업데이트 주기 | 비고 |
|---|---|---|---|
| Fed 기준금리 | FRED API (fred.stlouisfed.org) | 회의 시 | 무료 API키 필요 |
| 글로벌 CPI | FRED / World Bank API | 월간 | |
| KRW/USD 환율 | 한국은행 ECOS API | 일간 | T+2 결제일 오프셋 적용 필수 (MEMORY M-002) |
| WTI/Brent 유가 | EIA API (eia.gov) | 일간 | 무료 API키 필요 |

**1.1.3 데이터 소스 매핑**:
| 지표 | 소스 | 업데이트 주기 | 비고 |
|---|---|---|---|
| BDI | Baltic Exchange (유료 또는 Perplexity 대체) | 일간 | 유료 직접 API — Perplexity로 대체 가능 (HITL 확인 필요) |
| SCFI | Shanghai Shipping Exchange | 주간 | |

### Deliverable: Agricultural & Climate Connectors
| WBS ID | 작업명 | 담당 | 공수 | 선행 | 상태 |
|---|---|---|---|---|---|
| 1.1.4 | Implement WASDE/USDA Crop Data Connector | P1-05 | 24h | 1.1.1 | ⬜ |
| 1.1.5 | Implement ENSO/Weather Anomaly API Connector | P1-05 | 16h | 1.1.1 | ⬜ |

**1.1.4 데이터 소스 매핑**:
| 지표 | 소스 API | 업데이트 주기 |
|---|---|---|
| WASDE 대두 수급 | USDA PSD API (apps.fas.usda.gov) | 월간 (매월 둘째 주) |
| 원산지별 작황 | USDA NASS API | 분기 |

**1.1.5 데이터 소스 매핑**:
| 지표 | 소스 | 업데이트 주기 |
|---|---|---|
| ENSO 페이즈 | NOAA CPC API (cpc.ncep.noaa.gov) | 격주 |
| 원산지 날씨 이상 | OpenWeatherMap API (아르헨티나, 브라질, 미국 콩 재배 주요 지역) | 일간 |

### Deliverable: Geopolitical Connector
| WBS ID | 작업명 | 담당 | 공수 | 선행 | 상태 |
|---|---|---|---|---|---|
| 1.1.6 | Implement Geopolitical Risk Index Connector | P1-05 | 24h | 1.1.1 | ⬜ |

**1.1.6 접근 방법**: 공개 GPR 지수 (Caldara & Iacoviello) 다운로드 + Perplexity C-02 실시간 뉴스 스코어링으로 보완

### Deliverable: Pipeline Operations
| WBS ID | 작업명 | 담당 | 공수 | 선행 | 상태 |
|---|---|---|---|---|---|
| 1.1.7 | Configure API Retry Logic and GitHub Actions Daily Schedule | C-04 | 16h | 1.1.2~1.1.6 | ⬜ |
| 1.1.8 | Validate External Pipeline Data Quality (great_expectations suite) | C-08 | 8h | 1.1.7 | ⬜ |
| 1.1.9 | Document External Data Schemas in data/schemas/ | C-07 | 8h | 1.1.8 | ⬜ |

**1.1.7 GitHub Actions 스케줄**:
```yaml
# .github/workflows/external_data_refresh.yml
schedule:
  - cron: "0 1 * * 1-5"   # 평일 오전 1시 UTC (한국 오전 10시)
```

---

## 1.2 Internal Data Pipeline (~104h)
*담당 주요 에이전트: C-04 (인프라 설계)*
*⚠️ 주요 블로커: 사내 ERP → Snowflake 연동에 IT 부서 승인 및 DB 계정 발급 필요*

### Deliverable: Internal Snowflake Schemas
| WBS ID | 작업명 | 담당 | 공수 | 선행 | 상태 |
|---|---|---|---|---|---|
| 1.2.1 | Design Snowflake Schema for S&OP Data | C-04 | 16h | — | ⬜ |
| 1.2.2 | Design Snowflake Schema for Procurement History | C-04 | 16h | — | ⬜ |
| 1.2.3 | Design Snowflake Schema for Inventory and Logistics | C-04 | 16h | — | ⬜ |

**1.2.1 S&OP 스키마 포함 필드**:
`product_code`, `soybean_oil_input_kg_per_unit`, `production_plan_month`, `mps_qty`, `actual_qty`, `mape_pct`, `seasonality_coefficient`

**1.2.2 Procurement 스키마 포함 필드**:
`order_id`, `order_date`, `eta_date`, `actual_arrival_date`, `qty_mt`, `contract_price_usd_mt`, `supplier_id`, `origin_country`, `contract_type`, `hedging_pnl_krw`, `lead_time_days_variance`

**1.2.3 Inventory/Logistics 스키마 포함 필드**:
`snapshot_date`, `crude_oil_stock_mt`, `refined_oil_stock_mt`, `monthly_consumption_mt`, `turnover_rate`, `inbound_stage` (`order|shipment|customs|arrival`), `stage_date`

### Deliverable: ERP Sync Pipeline
| WBS ID | 작업명 | 담당 | 공수 | 선행 | 상태 |
|---|---|---|---|---|---|
| 1.2.4 | Implement Snowflake ERP Sync Pipeline | C-04 | 40h | 1.2.1~1.2.3 + IT 승인 | 🚫 |
| 1.2.5 | Validate Internal Pipeline Data Quality | C-08 | 8h | 1.2.4 | ⬜ |
| 1.2.6 | Document Internal Data Schemas | C-07 | 8h | 1.2.5 | ⬜ |

> 🚫 **1.2.4 블로커 상세**: 사내 ERP(MES 포함) 직접 접속 불가 — IT 보안 정책상 외부 클라우드 직접 연결 제한. 해결 옵션: (A) 사내 IT 부서가 Snowflake 전용 계정 생성 및 정기 데이터 덤프 → Azure Blob 경유 수동 업로드, (B) 주간 Excel 추출 → Snowpark로 처리 (단, `openpyxl` 금지 — CSV로 중간 변환 필요). **HITL 승인 필요**: IT 부서 협의 경로 확정.

---

## 1.3 EDA & Data Quality Reports (~72h)
*담당 주요 에이전트: C-06 (EDA), C-08 (검증)*
*선행조건: 1.1.8 + 1.2.5 완료 후 시작*

| WBS ID | 작업명 | 담당 | 공수 | 선행 | 상태 |
|---|---|---|---|---|---|
| 1.3.1 | Execute EDA on External Price Indicators (경제/무역 지표) | C-06 | 16h | 1.1.8 | ⬜ |
| 1.3.2 | Execute EDA on Climate and Crop Yield Data | C-06 | 16h | 1.1.8 | ⬜ |
| 1.3.3 | Execute EDA on Internal S&OP and Production Data | C-06 | 16h | 1.2.5 | ⬜ |
| 1.3.4 | Execute EDA on Procurement and Logistics History | C-06 | 16h | 1.2.5 | ⬜ |
| 1.3.5 | Compile Integrated EDA Summary Report | C-07 | 8h | 1.3.1~1.3.4 | ⬜ |

**각 EDA 작업 산출물 (C-06 output contract 기준)**:
- 결측값/이상값 리포트 (`reports/eda/[dataset]_quality.md`)
- 시계열 시각화: 분포, ACF/PACF, STL 분해 (`reports/eda/[dataset]_*.html`)
- ADF + KPSS 정상성 검정 결과
- 최소 데이터 길이 확인 (24개월 이상 — MEMORY M-004)
- 모델링 전 필수 처리 항목 목록

---

## 1.4 G1 Variable Pool Definition (~120h)
*담당 주요 에이전트: C-02, P1-01, P1-02, P1-03, P1-04, C-03*
*선행조건: 1.3.5 EDA 통합 보고서 완료*

| WBS ID | 작업명 | 담당 | 공수 | 선행 | 상태 |
|---|---|---|---|---|---|
| 1.4.1 | Collect Global Market Intelligence Brief (6년 이력 + 현재 동향) | C-02 | 24h | 1.3.5 | ⬜ |
| 1.4.2 | Analyze Geopolitical and Trade Risk Landscape | P1-02 | 24h | 1.4.1 | ⬜ |
| 1.4.3 | Analyze Climate and Crop Risk Landscape (ENSO 중심) | P1-03 | 16h | 1.4.1 | ⬜ |
| 1.4.4 | Analyze Supply Chain and Logistics Risk (BDI/SCFI/리드타임) | P1-04 | 16h | 1.4.1 | ⬜ |
| 1.4.5 | Identify and Rank Top 20 Candidate Price Variables | P1-01 | 24h | 1.4.2~1.4.4 | ⬜ |
| 1.4.6 | Score Variables by Data Availability and Predictive Value | C-03 | 8h | 1.4.5 | ⬜ |
| 1.4.7 | Document Final Variable Pool and Rationale | C-07 | 8h | 1.4.6 | ⬜ |

**1.4.5 변수 선정 기준**:
1. 데이터 가용성: 2020–2025 6년간 연속 수집 가능 여부
2. 업데이트 빈도: 일간 또는 주간 (월간은 G2/G3에서 사용)
3. 선행 지표성: 대두유 가격 변동 최소 4주 전 시그널 발생 여부
4. 수집 비용: 무료 API 우선; 유료는 HITL 승인 후 포함

**1.4.7 산출물**: `reports/variable_pool/g1_variable_pool_v1.md` — 변수명, 소스, 업데이트 주기, 예상 시차(lag), 포함 근거 포함

---

## 1.5 Baseline Model Benchmarks (~40h)
*담당 주요 에이전트: C-03 (모델), C-05 (리뷰)*
*선행조건: 1.3.1 (외부 가격 EDA) 완료 후 병행 가능*

| WBS ID | 작업명 | 담당 | 공수 | 선행 | 상태 |
|---|---|---|---|---|---|
| 1.5.1 | Implement Seasonal Naive Price Baseline (전년 동기 대비) | C-03 | 8h | 1.3.1 | ⬜ |
| 1.5.2 | Implement Last-Value Naive Baseline (전일 가격 = 예측) | C-03 | 8h | 1.3.1 | ⬜ |
| 1.5.3 | Compute Baseline Performance Metrics (MAPE, RMSE, 방향 정확도) | C-03 | 16h | 1.5.1~1.5.2 | ⬜ |
| 1.5.4 | Review Baseline Code Quality | C-05 | 8h | 1.5.3 | ⬜ |

**1.5.3 산출물 형식** (testing.md Model Baseline Requirement 기준):
```
| 지표 | 계절 나이브 | 전일 값 나이브 |
|---|---|---|
| MAPE | X% | Y% |
| RMSE | X | Y |
| 방향 정확도 | X% | Y% |
```

---

## Phase 1 리스크 레지스터

| # | 리스크 | 발생 가능성 | 영향도 | 완화 방안 |
|---|---|---|---|---|
| R-01 | 사내 ERP 연동 IT 승인 지연 | 높음 | 높음 | 1.2.4 우선 IT 협의 착수; 임시 수동 CSV 추출 방식 병행 |
| R-02 | BDI 직접 API 유료 — 비용 미승인 | 중간 | 중간 | Perplexity 기반 C-02 수집으로 대체 가능; HITL 확인 |
| R-03 | 외부 API 데이터 품질 불량 (결측 > 5%) | 중간 | 중간 | 1.1.8 great_expectations gate; 데이터 충분성 기준 미달 시 1.4.5에서 해당 변수 제외 |
| R-04 | 내부 S&OP 데이터 < 24개월 | 낮음 | 높음 | 1.3.3 EDA에서 조기 탐지; MEMORY M-004 fallback(ETS) 적용 |
