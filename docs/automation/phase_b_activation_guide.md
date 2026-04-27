# Phase B 활성화 가이드 — Snowflake 연동
> 작성: C-04 | 관련 WBS: 1.2.1~1.2.3 | 선행 조건: Phase A 안정 운영 확인 (최소 1주일)

---

## 현황 (Phase A) — 데이터 검증 및 저장 위치 확인 방법

**저장 위치**: GitHub Artifacts (7일 보존) — 영구 저장소 미연결

**현재 검증 방법**:
1. GitHub → Actions 탭 → "External Data Pipeline — Daily Refresh" 클릭
2. 가장 최근 실행(초록 체크 또는 빨간 X) 클릭
3. 우측 하단 **"Summary"** 탭 → `pipeline-summary` job의 **Step Summary** 확인
   - 각 parquet 파일명 · 행 수 · 수집 시각 자동 표시
4. 개별 데이터 확인이 필요한 경우: **"Artifacts"** 섹션에서 해당 파일 다운로드 → pandas로 로컬 검사

**Phase A 한계**:
- Artifacts는 7일 후 자동 삭제 → 이력 조회 불가
- 행 수 검증만 가능 (값 범위·스키마 유효성 미검증)
- Snowflake 쿼리 불가 → 다운스트림 분석 불가

---

## Phase B 활성화 — 단계별 절차

### Step 1: Snowflake 계정 및 서비스 계정 준비

Snowflake 관리자(또는 IT 부서)에 다음을 요청:

```sql
-- Snowflake Worksheet에서 실행
CREATE USER NEXUS_PIPELINE_USER
    PASSWORD = '<strong_password>'
    DEFAULT_WAREHOUSE = 'NEXUS_WH'
    DEFAULT_ROLE = 'NEXUS_PIPELINE_ROLE';

CREATE ROLE NEXUS_PIPELINE_ROLE;
CREATE WAREHOUSE NEXUS_WH WITH WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60;
GRANT ROLE NEXUS_PIPELINE_ROLE TO USER NEXUS_PIPELINE_USER;
```

### Step 2: GitHub Secrets 6종 등록

GitHub → Settings → Secrets and variables → Actions → **"New repository secret"**

| Secret 이름 | 내용 | 예시 |
|---|---|---|
| `SNOWFLAKE_ACCOUNT` | 계정 식별자 | `xy12345.ap-northeast-1.aws` |
| `SNOWFLAKE_USER` | 서비스 계정 사용자명 | `NEXUS_PIPELINE_USER` |
| `SNOWFLAKE_PASSWORD` | 서비스 계정 비밀번호 | `(강력한 비밀번호)` |
| `SNOWFLAKE_WAREHOUSE` | 컴퓨팅 웨어하우스 | `NEXUS_WH` |
| `SNOWFLAKE_DATABASE` | 데이터베이스명 | `SOYBEAN_OIL` |
| `SNOWFLAKE_SCHEMA` | 스키마명 | `RAW` |

### Step 3: Snowflake Raw 테이블 생성 (최초 1회)

Snowflake Worksheet에서 실행:
```sql
-- src/pipeline/sql/create_raw_tables.sql 전체 내용을 붙여넣기 후 실행
-- 5개 테이블 생성: ECONOMIC_INDICATORS, SHIPPING_INDICES, CROP_DATA, CLIMATE_DATA, GEOPOLITICAL_INDICES
```

### Step 4: GitHub Actions 워크플로우 활성화

`.github/workflows/external_data_refresh.yml` 편집:

```yaml
# 변경 전 (주석 처리 상태):
  # snowflake-upload:

# 변경 후 (주석 해제 — 'snowflake-upload:' 앞의 '# ' 제거):
  snowflake-upload:
```

전체 `snowflake-upload` 블록의 각 줄 앞 `# ` 제거 후 커밋.

### Step 5: 연결 테스트 (VS Code Web / Azure ML Terminal)

```bash
export SNOWFLAKE_ACCOUNT="xy12345.ap-northeast-1.aws"
export SNOWFLAKE_USER="NEXUS_PIPELINE_USER"
export SNOWFLAKE_PASSWORD="..."
export SNOWFLAKE_WAREHOUSE="NEXUS_WH"
export SNOWFLAKE_DATABASE="SOYBEAN_OIL"
export SNOWFLAKE_SCHEMA="RAW"

python src/pipeline/snowflake_loader.py
```

예상 출력:
```
[완료] economic_indicators_20260421.parquet → RAW.ECONOMIC_INDICATORS: 45행 업서트
[완료] shipping_indices_20260421.parquet → RAW.SHIPPING_INDICES: 2행 업서트
...
[완료] Snowflake 업로드 완료 — 총 NNN행
```

### Step 6: 데이터 검증 (Snowflake)

```sql
-- 수집 현황 확인
SELECT source_name, indicator_code, COUNT(*) AS rows, MAX(ingested_at) AS latest
FROM SOYBEAN_OIL.RAW.ECONOMIC_INDICATORS
GROUP BY 1, 2 ORDER BY 4 DESC LIMIT 20;

-- 전체 raw 테이블 행 수 요약
SELECT 'ECONOMIC_INDICATORS'  AS tbl, COUNT(*) AS n FROM SOYBEAN_OIL.RAW.ECONOMIC_INDICATORS UNION ALL
SELECT 'SHIPPING_INDICES',           COUNT(*) FROM SOYBEAN_OIL.RAW.SHIPPING_INDICES         UNION ALL
SELECT 'CROP_DATA',                  COUNT(*) FROM SOYBEAN_OIL.RAW.CROP_DATA                UNION ALL
SELECT 'CLIMATE_DATA',               COUNT(*) FROM SOYBEAN_OIL.RAW.CLIMATE_DATA             UNION ALL
SELECT 'GEOPOLITICAL_INDICES',       COUNT(*) FROM SOYBEAN_OIL.RAW.GEOPOLITICAL_INDICES;
```

### Step 7: (선택) AI 품질 검증 활성화

`ANTHROPIC_API_KEY` GitHub Secret 등록 후 워크플로우의 `ai-quality-check` 블록도 주석 해제.
Claude Haiku 4.5가 이상값·결측치 자동 탐지 → GitHub Step Summary로 리포트.

---

## 완료 기준 (Phase B Done)

- [ ] Snowflake 5개 Raw 테이블에 데이터 적재 확인
- [ ] 매일 자동 실행 후 Snowflake 행 수 증가 확인
- [ ] `pipeline-summary` Step Summary에 "Snowflake: N행 업서트" 표시
- [ ] WBS 1.2.1 실제 완료일 기입 (`reports/wbs/wbs_phase1_detailed.md`)
