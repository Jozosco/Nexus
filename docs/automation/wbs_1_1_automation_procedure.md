# WBS 1.1.2~1.1.6 자동화 절차서
> 최종 수정: 2026-04-17 | 작성: C-04 (Azure Infrastructure Engineer)
> 관련 워크플로우: `.github/workflows/external_data_refresh.yml`

---

## 1. 자동화 가능성 요약

| WBS | 작업 | 자동화 수준 | 비고 |
|-----|------|------------|------|
| 1.1.2 | 경제 지표 (FRED · EIA · BOK ECOS) | ✅ 완전 자동 | API 키 3종 등록 완료 |
| 1.1.3 | 해운 지수 (BDI · SCFI) | ✅ 자동 (프록시) | Baltic Exchange 직접 API 유료 (B-003); Perplexity sonar-pro 대체 |
| 1.1.4 | WASDE 작황 데이터 | ✅ 완전 자동 | USDA PSD API 키 불필요 |
| 1.1.5 | ENSO · 기상이상 | 🔶 부분 자동 | NOAA ✅; OpenWeatherMap 키 미등록 |
| 1.1.6 | 지정학 리스크 (GPR) | ✅ 자동 (복합) | Caldara & Iacoviello 공개 + Perplexity |

---

## 2. 사전 준비 — GitHub Secrets 등록 상태

GitHub Repository → Settings → Secrets and variables → Actions → **Repository secrets**

| Secret 이름 | 용도 | 상태 |
|---|---|---|
| `FRED_API_KEY` | FRED 경제 지표 | ✅ 등록 완료 |
| `EIA_API_KEY` | EIA Brent 유가 | ✅ 등록 완료 |
| `BOK_ECOS_API_KEY` | BOK ECOS KRW/USD | ✅ 등록 완료 |
| `PERPLEXITY_API_KEY` | BDI/SCFI · GPR 실시간 | ✅ 등록 완료 |
| `OPENWEATHERMAP_API_KEY` | 원산지 기상이상 | ⚠️ 미등록 (openweathermap.org 무료 키 필요) |

### OpenWeatherMap 키 등록 방법 (필요 시)
1. https://openweathermap.org → 무료 계정 생성
2. API Keys 메뉴 → 기본 키 복사
3. GitHub → Settings → Secrets → `OPENWEATHERMAP_API_KEY` 추가
4. `.github/workflows/external_data_refresh.yml` → `climate-enso` job 수정:
   ```yaml
   # 변경 전
   OPENWEATHERMAP_API_KEY: ""
   # 변경 후
   OPENWEATHERMAP_API_KEY: ${{ secrets.OPENWEATHERMAP_API_KEY }}
   ```

---

## 3. Phase A — 즉시 실행 (GitHub Actions → Artifact)

현재 구성: GitHub Actions runner에서 Python 직접 실행 → `data/raw/*.parquet` → GitHub Artifact 저장 (7일)

### 3.1 자동 스케줄 실행
- **주기**: 평일(월~금) 오전 1시 UTC (KST 오전 10시)
- **cron**: `"0 1 * * 1-5"`
- 별도 조작 불필요 — 등록된 Secrets로 자동 실행

### 3.2 수동 단일 커넥터 실행
1. GitHub Repository → **Actions** 탭
2. 왼쪽 목록에서 **"External Data Pipeline — Daily Refresh"** 클릭
3. 오른쪽 상단 **"Run workflow"** 버튼 클릭
4. `connector` 드롭다운 선택:
   - `all` — 5개 커넥터 전체 병렬 실행
   - `economic` — WBS 1.1.2 단독
   - `shipping` — WBS 1.1.3 단독
   - `wasde` — WBS 1.1.4 단독
   - `climate` — WBS 1.1.5 단독
   - `gpr` — WBS 1.1.6 단독
5. **"Run workflow"** 클릭 → 실행 시작

### 3.3 결과 확인 (Artifact)
1. 실행된 워크플로우 클릭
2. 하단 **Artifacts** 섹션에서 파일 다운로드:
   - `economic-indicators-{run_id}` → `economic_indicators_YYYYMMDD.parquet`
   - `shipping-indices-{run_id}` → `shipping_indices_YYYYMMDD.parquet`
   - `wasde-crop-{run_id}` → `crop_data_YYYYMMDD.parquet`
   - `climate-enso-{run_id}` → `climate_data_YYYYMMDD.parquet`
   - `geopolitical-risk-{run_id}` → `geopolitical_indices_YYYYMMDD.parquet`
3. Artifact 보존 기간: **7일**

---

## 4. Phase B — 목표 상태 (GitHub Actions → Azure ML → Snowflake)

> **활성화 조건**: Snowflake 관련 GitHub Secrets 6종 등록 완료 시

### 4.1 추가 등록 필요 Secrets

| Secret 이름 | 내용 |
|---|---|
| `SNOWFLAKE_ACCOUNT` | Snowflake 계정 식별자 (예: `xy12345.ap-northeast-1.aws`) |
| `SNOWFLAKE_USER` | 서비스 계정 사용자명 |
| `SNOWFLAKE_PASSWORD` | 서비스 계정 비밀번호 |
| `SNOWFLAKE_WAREHOUSE` | 컴퓨팅 웨어하우스 이름 |
| `SNOWFLAKE_DATABASE` | 대상 데이터베이스 (예: `SOYBEAN_OIL`) |
| `SNOWFLAKE_SCHEMA` | 대상 스키마 (예: `RAW`) |

### 4.2 활성화 절차
1. Snowflake Secrets 6종 GitHub Repository Secrets에 등록
2. `.github/workflows/external_data_refresh.yml` 하단 주석 해제:
   ```yaml
   # snowflake-upload:   ← 이 블록 전체 주석 해제
   ```
3. `src/pipeline/snowflake_loader.py` 작성 (C-04 담당 — WBS 1.2.x)
4. 스키마: `soybean_oil.raw.economic_indicators`, `soybean_oil.raw.shipping_indices` 등

---

## 5. 모니터링 및 장애 대응

### 5.1 실행 실패 알림
- GitHub Actions 기본 이메일 알림 (Repository Watch → Actions notifications 설정)
- 실패 시: Actions → 해당 실행 → 실패한 step의 로그 확인

### 5.2 커넥터별 주요 오류 패턴

| 커넥터 | 예상 오류 | 대응 |
|---|---|---|
| economic | `[오류] FRED_API_KEY 환경변수...` | GitHub Secret 확인 |
| shipping | BDI/SCFI 파싱 실패 경고 | Perplexity 응답 형식 변경 → regex 수정 |
| wasde | `[경고] USDA PSD: {year}년 데이터 없음` | 마케팅 연도 파라미터 조정 |
| climate | `[경고] OPENWEATHERMAP_API_KEY 미등록` | 키 등록 또는 무시 가능 |
| gpr | GPR 엑셀 컬럼 구조 변경 감지 | gpr_connector.py 컬럼 탐지 로직 업데이트 |

### 5.3 재시도 정책
모든 커넥터는 지수 백오프(2s → 4s → 8s → 16s, 최대 4회) 내장 (MEMORY A-003).
GitHub Actions job 레벨 재시도는 별도 설정 가능 (`retry-action` 참조).

---

## 6. VS Code Web (Azure ML) 로컬 테스트 절차

GitHub Actions 트리거 전 VS Code Web에서 개별 커넥터 테스트:

```bash
# VS Code Web Terminal (Azure ML Studio)
cd /home/azureuser/Nexus   # 또는 클론 경로

# 환경 변수 설정 (터미널 세션 내 임시)
export FRED_API_KEY="your_key_here"
export EIA_API_KEY="your_key_here"
export BOK_ECOS_API_KEY="your_key_here"
export PERPLEXITY_API_KEY="your_key_here"

# 개별 커넥터 테스트
python src/pipeline/connectors/economic_connector.py
python src/pipeline/connectors/shipping_connector.py
python src/pipeline/connectors/wasde_connector.py
python src/pipeline/connectors/climate_connector.py
python src/pipeline/connectors/gpr_connector.py

# 출력 확인
ls -lh data/raw/
```

> ⚠️ 보안: 터미널에 직접 키를 입력하지 말고 `.env` 파일 사용 후 `source .env` 실행.
> `.env` 파일은 절대 git commit 하지 않음 (`.gitignore` 확인).
