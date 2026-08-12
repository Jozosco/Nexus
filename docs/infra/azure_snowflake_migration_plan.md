# Azure ML · Snowflake 데이터 이관 계획 (이관 대상·경로 확정)

**작성일**: 2026-08-12 · **주도**: C-04 · **협의**: C-01 · C-03
**전제(조정자 확인)**: Azure ML Studio **Compute 인스턴스 보유** · Snowflake **계정 보유**.
따라서 **프로비저닝 리드타임이 없다** — 남은 문제는 오직 **경로(path)**다.

---

## 0. 핵심 판단 — 방화벽은 이관 경로를 막지 않는다

제약을 정확히 규정하면 해법이 나온다.

| 방향 | 가능 여부 | 근거 |
|---|---|---|
| 사내(Azure ML) → **외부 API**(USDA·FRED·관세청…) | 🔴 **차단** | 조정자 확인 사항. 이것이 "API 연동이 어렵다"의 실체 |
| GitHub Actions → **외부 API** | 🟢 가능 | 현행 파이프라인이 이미 이렇게 동작 중 |
| GitHub Actions → **Snowflake** | 🟢 가능(예상) | Snowflake는 SaaS 공개 엔드포인트 |
| Azure ML Compute → **Snowflake** | 🟢 가능(예상) | 사내에서 이미 내부 데이터가 Snowflake로 유입 중 = 방화벽 허용 기존재 |

> **결론**: 외부 API를 사내에서 직접 부를 필요가 **없다**. 수집은 지금처럼 Actions가 하고,
> **Snowflake를 중립 접점(neutral meeting point)** 으로 삼으면 양쪽이 만난다.
> Snowflake는 이미 승인된 사내 인프라이므로 신규 방화벽 심의가 최소화된다.

```text
[외부 API 30여종]
      │  (Actions만 egress 보유)
      ▼
[GitHub Actions]  ── 수집·파싱·품질검증 ──▶ parquet
      │  PUT + COPY INTO
      ▼
[Snowflake NEXUS_EXT]  ◀── 중립 접점: 양쪽이 접근 가능
      │  snowflake-connector / Snowpark
      ▼
[Azure ML Compute]  ── 학습·평가·모델 등록 (외부 API 불요)
```

---

## 1. 이관 대상 데이터 — 3계층

데이터 **용량은 문제가 아니다**(전체 정형 데이터 약 70만 행 ≈ 30MB 미만). 우선순위는
용량이 아니라 **G2 학습에 필요한가**로 정한다.

### Tier 1 — G2 학습 필수 (즉시 이관) · 약 5MB

| 데이터 | 지표 | 행 수(추정) | 용도 |
|---|---|---|---|
| `databento_bo_historical` | `CBOT_BO_OPEN/HIGH/LOW/CLOSE/VOLUME` | 약 20,000 | **목표변수** — 없으면 G2 불가 |
| 핵심 8변수 피처 | CBOT · CPO–SBO spread · WASDE STU · BDI · FX_BRL · ENSO ONI · crush · GATS | 약 50,000 | Champion 입력 |
| `feature_mart`(gold) | as-of 정렬 완료 피처 뷰 | 약 4,000행 × N열 | 학습 직접 입력 |

### Tier 2 — 분석 전체 (G1 완료 후) · 약 25MB

| 데이터 | 비고 |
|---|---|
| 정형 parquet 18종 전체(silver) | economic · shipping · climate · customs_gw · te_commodities · ice · wasde · psd · gats … |
| `unstructured_signals_historical` | UNSTR_* 월별 태그·톤 (2,156행) |
| 최대 테이블 = `climate_data` | 12지역 × 8변수 × 약 6,000일 ≈ 57만 행 — 그래도 20MB 미만 |

### Tier 3 — 비정형 원문 (이관 보류) · 약 1.65GB

| 데이터 | 판단 |
|---|---|
| GAIN·FAO PDF 2,231건 + 요약 md 2,240건 | **Snowflake에 바이트를 넣지 않는다.** 메타·요약·근거 스팬만 테이블화하고 원문은 오브젝트 스토리지 유지 |
| 이관 시점 | G2 Preview 이후. **학습에 필요한 것은 이미 시계열화된 UNSTR_* 지표**이지 PDF 원문이 아니다 |

---

## 2. 이관 경로 — 3안 비교

| 안 | 경로 | 장점 | 단점 | 판정 |
|---|---|---|---|---|
| **A. Snowflake 경유** | Actions → Snowflake stage(PUT) → COPY INTO → Azure ML이 connector로 읽기 | 양쪽 모두 접근 가능 · **기존 승인 인프라** · loader 코드 이미 존재 | Snowflake 컴퓨트 비용(소액) | 🟢 **채택** |
| B. Azure Blob 직행 | Actions → Blob(SAS) → Azure ML Data Asset | Azure ML 네이티브 데이터 평면 | **Storage 계정이 private endpoint면 Actions 인바운드 차단**(§4 확인 필요) | 🟡 조건부 |
| C. 수동 전송 | 로컬 다운로드 → 업로드 | 방화벽 무관 | 재현 불가 · 자동화 불가 · 인계 시 단절 | 🔴 최후 수단 |

**A안 채택 근거**: 내부 데이터가 이미 Snowflake로 흐르고 있다는 것은 **사내→Snowflake 경로가
이미 방화벽 승인돼 있다**는 뜻이다. 신규 심의 대상은 Actions→Snowflake 한 방향뿐이며,
이는 Snowflake 측 네트워크 정책(IP allowlist) 설정으로 해결된다.

### 2.1 A안 구현 (기존 자산 재활용)

이미 있는 것: `src/pipeline/snowflake_loader.py` · `src/pipeline/sql/create_raw_tables.sql`
(작성 완료·휴면 상태 — **이관 자산 중 준비도 최상**)

수정 필요 2가지:

1. **`MERGE INTO ... UPDATE SET` → INSERT 전용으로 교체**
   현행 업서트는 개정치를 덮어써 **as-of 규칙(D-023)을 위반**한다. PK에 `SOURCE_VINTAGE`를
   추가하고 append-only로 바꿔야 한다. 최신값은 뷰로 제공:
   ```sql
   SELECT * FROM NEXUS_EXT.ODS.T QUALIFY
     ROW_NUMBER() OVER (PARTITION BY price_date, indicator_code
                        ORDER BY source_vintage DESC) = 1;
   ```
2. **`available_at` 등 as-of 5필드를 DDL에 반영** (수집 측 보강과 동시 진행)

### 2.2 Azure ML 측

```python
# Azure ML Compute에서 실행 — 외부 API 호출 없음
import snowflake.connector, os
conn = snowflake.connector.connect(
    account=os.environ["SNOWFLAKE_ACCOUNT"], user=os.environ["SNOWFLAKE_USER"],
    password=os.environ["SNOWFLAKE_PASSWORD"], warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
    database="NEXUS_EXT", schema="MART")
df = conn.cursor().execute("SELECT * FROM FEATURE_MART").fetch_pandas_all()
```
학습 산출은 `mlflow.log_model()`로 Azure ML Model Registry에 등록(pickle 금지).

---

## 3. 단계별 실행

| 단계 | 내용 | 선행조건 | 산출 |
|---|---|---|---|
| M0 | **연결성 검증**(§4 3건) — 실제 데이터 이관 전 | 없음 | 가부 확정 |
| M1 | as-of 5필드 보강(수집 측) + DDL 반영 | — | 스키마 8종 개정 |
| M2 | `NEXUS_EXT` DB·스키마 생성(ODS/SILVER/MART) | Snowflake 롤 | DDL 적용 |
| M3 | **Tier 1 적재** — Actions에 `snowflake-load` 잡 추가 | M1·M2 | 목표변수·핵심피처 |
| M4 | Azure ML에서 Tier 1 읽기 검증 | M3 | 학습 가능 확인 |
| M5 | **Tier 2 적재** | M3 | 전체 정형 |
| M6 | G2 학습을 Azure ML `command()` 잡으로 실행 | M4 | 모델 등록 |
| M7 | Tier 3(비정형) — 오브젝트 스토리지 + 카탈로그 | 후순위 | 보류 |

---

## 4. 착수 전 확인 필요 3건 (M0)

이 3건이 확정돼야 경로가 확정된다. **각각 10분이면 검증 가능**하다.

| # | 확인 사항 | 방법 | 실패 시 대안 |
|---|---|---|---|
| 1 | **Snowflake가 GitHub Actions IP를 허용하는가** | Actions에서 `snowflake.connector.connect()` 스모크 잡 1회 실행 | Snowflake 네트워크 정책에 Actions IP 레인지 추가(GitHub meta API 제공) |
| 2 | **Azure ML Compute가 Snowflake에 접근 가능한가** | Compute 노트북에서 동일 connect 시도 | 사내 방화벽에 Snowflake 엔드포인트 허용 신청 |
| 3 | **Azure Storage 계정이 public network access를 허용하는가** | Portal → Storage account → Networking 확인 | B안 폐기하고 A안(Snowflake 경유) 단독 진행 |

> 3번이 `Disabled`(private endpoint 전용)면 **B안은 불가**이고 A안만 남는다.
> A안을 1순위로 둔 이유가 이것이다 — 3번 결과와 무관하게 성립한다.

---

## 5. 이관 후에도 GitHub Actions가 남는 이유

전면 이관이 아니다. **수집 계층은 Actions에 남는다.**

| 계층 | 이관 후 위치 | 이유 |
|---|---|---|
| 외부 API 수집 | **GitHub Actions 유지** | 사내에서 외부 API 호출이 방화벽으로 막혀 있음 — 대체 불가 |
| 저장·서빙 | Snowflake `NEXUS_EXT` | 전사 EDP 단일화 목표 |
| 학습·평가 | Azure ML Compute | 외부 데이터 AI 컴퓨트 지정 |

11월 Control Tower 통합 시 수집 계층이 Apache Hop ETL로 옮겨가려면 **그 ETL 서버가
외부 egress를 확보**해야 한다(`docs/infra/egress_allowlist.yaml` 34종). 그때까지는
Actions가 유일한 수집 경로다.
