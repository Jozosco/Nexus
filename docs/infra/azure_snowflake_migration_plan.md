# Azure Storage 우선 데이터 이관 계획 (이관 대상·경로 확정)

**작성일**: 2026-08-12 · **개정**: 2026-08-12(팀장 지시 반영) · **주도**: C-04 · **협의**: C-01 · C-03
**전제(조정자 확인)**: Azure ML Studio **Compute 인스턴스 보유** · Snowflake **계정 보유**.
따라서 **프로비저닝 리드타임이 없다** — 남은 문제는 오직 **경로(path)**다.

> ## 📌 2026-08-12 개정 — **Azure Storage 우선**, Snowflake 후순위
> 팀장 지시: *"데이터 마이그레이션은 Azure Storage로 먼저 진행"*.
> 이에 따라 **경로 우선순위를 B안(Azure Blob 직행) → 1순위**로 교체하고,
> Snowflake 적재(구 A안)는 **11월 EDP 통합 시점으로 이연**한다.
> 아래 §2의 A/B 판정은 이 지시에 맞춰 갱신했다(원 판단 근거는 이력으로 보존).
>
> **판단이 바뀌어도 유효한 것**: 이관 대상 3계층(§1)·as-of 필드 선행(§3 M1)·
> 수집 계층을 GitHub Actions에 남기는 구조(§5)는 목적지와 무관하게 그대로다.

---

## 0. 핵심 판단 — 방화벽은 이관 경로를 막지 않는다

제약을 정확히 규정하면 해법이 나온다.

| 방향 | 가능 여부 | 근거 |
|---|---|---|
| 사내(Azure ML) → **외부 API**(USDA·FRED·관세청…) | 🔴 **차단** | 조정자 확인 사항. 이것이 "API 연동이 어렵다"의 실체 |
| GitHub Actions → **외부 API** | 🟢 가능 | 현행 파이프라인이 이미 이렇게 동작 중 |
| GitHub Actions → **Azure Blob** | 🟡 **확인 필요** | Storage 계정의 public network access 설정에 달림(§4-①) — **B안의 유일한 관문** |
| Azure ML Compute → **Azure Blob** | 🟢 가능 | 동일 구독·VNet 내부 경로 |
| GitHub Actions → **Snowflake** | 🟢 가능(예상) | SaaS 공개 엔드포인트 — 대안 경로로 보존 |

> **결론**: 외부 API를 사내에서 직접 부를 필요가 **없다**. 수집은 지금처럼 Actions가 하고,
> **Actions가 Azure Storage로 밀어 넣으면(push)** 사내는 받기만 하면 된다.
> 막힌 방향(사내→외부 API)을 쓰지 않는 설계이므로 방화벽과 충돌하지 않는다.

```text
[외부 API 30여종]
      │  (Actions만 egress 보유 — 사내에서는 호출 불가)
      ▼
[GitHub Actions]  ── 수집·파싱·품질검증·as-of 부여 ──▶ parquet
      │  push (azure-storage-blob, SAS/AAD)
      ▼
[Azure Blob  nexus-ext/{tier}/{dataset}/{snapshot_date}/]
      │  Data Asset 마운트
      ▼
[Azure ML Compute]  ── 학습·평가·모델 등록 (외부 API 불요)

      ※ Snowflake 적재는 11월 EDP 통합 시 동일 parquet에서 분기(경로 A)
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
| **B. Azure Blob 직행** | Actions → Blob(SAS/AAD) → Azure ML Data Asset | **Azure ML 네이티브 데이터 평면** · 학습 잡이 마운트로 직접 읽음 · 중간 계층 없음 | Storage 계정이 private endpoint면 Actions 인바운드 차단(§4-①) | 🟢 **채택(팀장 지시)** |
| A. Snowflake 경유 | Actions → Snowflake stage(PUT) → COPY INTO → Azure ML이 connector로 읽기 | 양쪽 접근 가능 · 기존 승인 인프라 · loader 코드 존재 | 학습 데이터 평면으로는 Blob보다 한 단계 우회 | 🟡 **11월 EDP 통합 시 재개** |
| C. 수동 전송 | 로컬 다운로드 → 업로드 | 방화벽 무관 | 재현 불가 · 자동화 불가 · 인계 시 단절 | 🔴 최후 수단 |

**B안이 학습 관점에서 더 자연스러운 이유**: Azure ML의 Data Asset은 Blob을 **네이티브 데이터
평면**으로 삼는다. `command()` 잡이 데이터셋을 마운트/다운로드로 직접 받으므로 커넥터 인증·
드라이버가 불필요하고, 스냅샷 버저닝(Data Asset version)이 재현성 요건과 1:1로 맞는다.
Snowflake 경유는 학습 때마다 쿼리→pandas 변환이 끼어들어 대용량에서 병목이 된다.

**단, B안의 유일한 관문은 §4-①**이다. Storage 계정이 `public network access: Disabled`
(private endpoint 전용)이면 GitHub Actions에서 직접 쓸 수 없다. 이 경우의 대안은 §4에 정리했다.

### 2.1 B안 구현 — Azure Blob 적재

```python
# scripts/upload_to_azure_blob.py (신설 예정)
# 인증: AZURE_STORAGE_CONNECTION_STRING 또는 SAS 토큰 (GitHub Secrets)
from azure.storage.blob import BlobServiceClient
import os, pathlib

svc = BlobServiceClient.from_connection_string(os.environ["AZURE_STORAGE_CONNECTION_STRING"])
container = svc.get_container_client("nexus-ext")
# 경로 규약: {tier}/{dataset}/{snapshot_date}/{file}.parquet — Data Asset 버저닝과 정합
for p in pathlib.Path("data/raw").glob("*.parquet"):
    blob = f"tier1/{p.stem}/{SNAPSHOT_DATE}/{p.name}"
    container.upload_blob(name=blob, data=p.read_bytes(), overwrite=False)  # 스냅샷 불변
```

**핵심 규약 2가지**
1. **`overwrite=False`** — 스냅샷은 불변(immutable). 재현성의 전제이며 개정치 덮어쓰기를
   물리적으로 차단한다(as-of 규칙 D-023과 동일 사상).
2. **경로에 `snapshot_date` 포함** — Azure ML Data Asset의 version과 1:1 대응시킨다.

### 2.2 A안 구현 (Snowflake — 11월 EDP 통합 시 재개, 기존 자산 재활용)

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

### 2.3 Azure ML 측

```python
# Azure ML Compute에서 실행 — 외부 API 호출 없음 (B안: Blob Data Asset)
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes
# 등록된 Data Asset을 학습 잡에 마운트 → 커넥터·드라이버 불요
# az ml data create --name nexus-feature-mart --version 2026-08-28 \
#     --path azureml://.../nexus-ext/tier1/feature_mart/2026-08-28/ --type uri_folder
import pandas as pd
df = pd.read_parquet("${{inputs.feature_mart}}/feature_mart.parquet")   # 잡 입력으로 주입
```
학습 산출은 `mlflow.log_model()`로 Azure ML Model Registry에 등록(pickle 금지).

---

## 3. 단계별 실행

| 단계 | 내용 | 선행조건 | 산출 |
|---|---|---|---|
| M0 | **연결성 검증**(§4) — 실제 이관 전 | Storage 인증정보 | 경로 가부 확정 |
| M1 | **as-of 5필드 보강**(수집 측) | — | 스키마 8종 개정 · `asof.py` |
| M2 | Blob 컨테이너 `nexus-ext` + 경로 규약 확정 | Storage 접근 | 경로 스킴 |
| M3 | **Tier 1 적재** — Actions에 `azure-blob-upload` 잡 추가 | M0·M1·M2 | 목표변수·핵심피처 |
| M4 | Azure ML **Data Asset 등록** + 읽기 검증 | M3 | 학습 가능 확인 |
| M5 | **Tier 2 적재** | M3 | 전체 정형 |
| M6 | G2 학습을 Azure ML `command()` 잡으로 실행 | M4 | 모델 등록 |
| M7 | Tier 3(비정형) 이관 | 후순위 | 보류 |
| M8 | Snowflake 적재(경로 A) — **11월 EDP 통합 시** | 별건 | 이연 |

---

## 4. 착수 전 확인 필요 3건 (M0)

이 3건이 확정돼야 경로가 확정된다. **각각 10분이면 검증 가능**하다.

| # | 확인 사항 | 방법 | 실패 시 대안 |
|---|---|---|---|
| **①** | **Storage 계정의 public network access** — 최우선 | Portal → Storage account → **Networking** → `Enabled from all networks` / `Enabled from selected networks` / `Disabled` 중 무엇인지 | ↓ 아래 분기표 |
| ② | 쓰기 인증 수단 | 계정 키 · **SAS 토큰**(권장, 컨테이너 한정·만료 지정) · AAD 서비스주체 중 발급 가능한 것 | SAS가 가장 간단 |
| ③ | Azure ML Compute → Blob 읽기 | Compute 노트북에서 컨테이너 list 시도 | 동일 구독이면 대개 문제없음 |

**①의 분기 — 여기서 경로가 갈립니다**

| Networking 설정 | Actions → Blob | 조치 |
|---|---|---|
| `Enabled from all networks` | 🟢 가능 | SAS 발급만으로 즉시 진행 |
| `Enabled from selected networks` | 🟡 조건부 | GitHub Actions IP 레인지를 방화벽 규칙에 추가(`https://api.github.com/meta`의 `actions` 배열 — 다만 목록이 크고 변동됨) |
| `Disabled`(private endpoint 전용) | 🔴 불가 | **경로 A(Snowflake 경유)로 전환** 또는 **self-hosted runner**(사내 네트워크 내부에 두되, 외부 API 수집은 계속 GitHub-hosted가 담당하는 2단 구성) |

> **조정자께 요청**: ①만 확인해 주시면 나머지는 제가 진행합니다.
> `Disabled`인 경우에도 막다른 길은 아닙니다 — 경로 A를 이미 설계해 뒀습니다(§2.2).

---

## 5. 이관 후에도 GitHub Actions가 남는 이유

전면 이관이 아니다. **수집 계층은 Actions에 남는다.**

| 계층 | 이관 후 위치 | 이유 |
|---|---|---|
| 외부 API 수집 | **GitHub Actions 유지** | 사내에서 외부 API 호출이 방화벽으로 막혀 있음 — 대체 불가 |
| 저장(학습 데이터) | **Azure Blob `nexus-ext`** | 팀장 지시 — Azure ML 네이티브 데이터 평면 |
| 저장·서빙(분석) | Snowflake `NEXUS_EXT` | 11월 전사 EDP 단일화 시점 |
| 학습·평가 | Azure ML Compute | 외부 데이터 AI 컴퓨트 지정 |

11월 Control Tower 통합 시 수집 계층이 Apache Hop ETL로 옮겨가려면 **그 ETL 서버가
외부 egress를 확보**해야 한다(`docs/infra/egress_allowlist.yaml` 34종). 그때까지는
Actions가 유일한 수집 경로다.
