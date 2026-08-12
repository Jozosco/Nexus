# 목표 아키텍처 대응 — Nexus 데이터 아키텍처 분류·이관 판단서

**작성일**: 2026-08-12 · **주도**: C-04(Document Intelligence & MLOps 인프라)
**협의**: C-01(PM·거버넌스) · C-03(Lead Data Scientist) · P1-06(시맨틱)
**입력**: 조정자 공유 — 현행 Azure Hub-and-Spoke 구성 + 11월 목표(AWS CT 통합 · Apache Hop ·
Snowflake EDP 단일화)

---

## 0. 핵심 판단 3가지

| # | 판단 | 근거 |
|---|---|---|
| 1 | **Nexus는 외부 트랙이나, 저장 계층은 공통 EDP(Snowflake)로 간다** | 조정자 분류 기준은 *데이터 출처* 축과 *저장·서빙 플랫폼* 축이 한 축에 섞여 있음. 문자 그대로 적용하면 ADLS Gen2 폐지 후 **Nexus 데이터의 착지점이 사라짐** |
| 2 | **Supabase·Neo4j 도입을 철회한다** | 회사가 걷어내는 PostgreSQL을, 사외 3rd-party에, 이관 3개월 전에 신설하는 **3중 역행**. 직전 세션(R-012)의 제 권고를 뒤집음 |
| 3 | **9/10 G2 Preview까지는 플랫폼을 이관하지 않는다** | 플랫폼과 모델을 동시에 바꾸면 성능 변화의 원인을 분리할 수 없음(교란). 지금 할 일은 인프라 구축이 아니라 **이식성 확보** |

---

## 1. 데이터 아키텍처 분류표 (조정자 요청 형식)

### 1.1 내부 데이터 운영 — PostgreSQL · AWS · Snowflake

| 구성요소 | 현행 | 목표(11월) | Nexus 해당 여부 | 이관 시 조치 |
|---|---|---|---|---|
| Oracle Server | 사내 · VPN/VNet GW로 Azure 연결 | AWS CT 내 유지 | ❌ **미해당** | 없음 — D-021로 접근 금지 |
| FTP Server | 사내 · VPN 경유 | AWS CT 내 유지 | ❌ **미해당** | 없음 |
| **PostgreSQL** (CDI-Data-RG) | Azure Spoke 내 운영 | 🔴 **폐지 → Snowflake 흡수** | ❌ **미해당** | 없음. **신규 PostgreSQL 계열 도입 금지**(§3) |
| ADF Integration Runtime | Hub Vnet, 내부 소스 연결 | Apache Hop ETL #1로 대체 | ❌ **미해당** | 없음 — Nexus는 내부 VPN 불필요 |
| **AWS Control Tower** | 전사 표준(데이터는 이원화) | 🟢 **CT 통합 완료** | 🟡 **간접** | 계정·네트워크 거버넌스 하위로 편입. **방화벽 아웃바운드 allowlist 신청 필요**(§4) |
| **Snowflake** | 내부 데이터 웨어하우스 | 🟢 **전사 EDP 단일화(ODS→Mart)** | 🟢 **해당 — 저장·서빙 정착지** | `NEXUS_EXT` **전용 DB**로 진입. 내부 스키마 GRANT 미부여(§2.2) |

### 1.2 외부 데이터 운영 — MS Foundry · Azure ML Computing

| 구성요소 | 현행 | 목표(11월) | Nexus 해당 여부 | 이관 시 조치 |
|---|---|---|---|---|
| 외부 수집 경로 | 방화벽 경유 직접 수집 | Apache Hop ETL #1(내부·외부 데이터 lane) | 🟢 **해당 — 커넥터 30종** | Python 모듈은 **그대로** 이관. 오케스트레이션만 재구축(§2.1) |
| **ADLS Gen2** (CDI-Data-RG) | 외부 데이터 레이크 | 🔴 **폐지 → Snowflake 흡수** | 🟡 **잠재적 해당** | 현재 미사용(parquet은 Git). **비정형 바이트는 오브젝트 스토리지 유지**(§2.3) |
| **Azure ML Computing** | 외부 데이터 AI 컴퓨트 | 🟢 유지 | 🟢 **해당 — G1/G2/G3 학습** | **Challenger 딥러닝(GPU) 단계에서 도입**. 9/10 이전 이관 금지 |
| **MS Foundry** (Azure AI Foundry) | 외부 데이터 LLM 계층 | 🟢 유지 | 🟢 **해당 — P1-05/P1-06** | 현행 OpenAI 직접 호출 유지 → `llm_router.py`에 **백엔드 축 추가**로 설정 전환화 |
| Apache Hop ETL #2 (AI용 정형·비정형) | — | 🟢 신설 | 🟢 **해당 — 비정형 파이프라인** | GAIN/FAO PDF 판독·요약·시계열화가 이 lane |
| Azure Purview | 데이터 카탈로그 | 유지(또는 AWS Glue Catalog) | 🟡 **연계** | `src/semantic/*.yaml`이 **원천**, 카탈로그는 하류 — **단방향 투영**(중복 아님) |
| Event Hubs · Monitor · Log Analytics | 운영 관측 | AWS CloudWatch 계열로 수렴 예상 | 🟡 **연계** | 파이프라인 로그·실패 알림 연동 대상 |

### 1.3 분류 기준 자체에 대한 C-04 의견 (중요)

조정자 기준은 **Snowflake를 내부 트랙에만** 배치했으나, 목표 아키텍처는
**PostgreSQL + ADLS Gen2 → Snowflake EDP 단일화**를 지시합니다. 이 둘을 문자 그대로 적용하면
둘 중 하나가 깨집니다.

| 시나리오 | 결과 |
|---|---|
| Nexus = 순수 외부 트랙 → Snowflake 진입 금지 | ADLS Gen2 폐지 후 **Nexus 데이터의 착지점 소멸**. EDP 단일화 목표와 모순 |
| Nexus = 내부 트랙 편입 | D-021 경계가 조직·플랫폼 레벨에서 흐려짐. 동일 스키마 배치 시 **조인 사고 위험** |

**권고 — 2축 분류로 교정**

| 축 | Nexus 귀속 | 근거 |
|---|---|---|
| 원천·수집·전처리 | **외부 트랙** (Hop ETL, 외부 방화벽 경유) | 출처 100% 외부, 내부 VPN/IR 불필요 |
| AI 컴퓨트·모델 | **외부 트랙** (Azure ML / MS Foundry) | 조정자 기준 ② + modeling.md. **CT의 AWS 통합 ≠ 컴퓨트 통합** |
| 저장·서빙(ODS→Mart) | **공통 EDP (Snowflake)** — 별도 DB·역할 분리 | 단일화 목표 충족 + D-021은 기술 가드레일로 보장 |

---

## 2. Nexus 이관 로드맵

### 2.1 Apache Hop 이관 — 그대로 가는 것 / 다시 만드는 것

| 자산 | 판정 | 비고 |
|---|---|---|
| 커넥터 Python 30종 (`src/pipeline/connectors/`, `scripts/ingest_*`) | 🟢 **그대로** | 순수 httpx+pandas. Hop **Execute Process**로 호출 |
| parquet 산출 계약 (`data/schemas/*.yaml`) | 🟢 **그대로** | 롱포맷 유지 + as-of 컬럼 보강(§5) |
| 시맨틱 레이어 (`src/semantic/*.yaml`) | 🟢 **그대로** | 파일 기반이라 플랫폼 무관 |
| `os.environ['KEY']` 규약 | 🟢 **그대로** | 시크릿 백엔드만 AWS Secrets Manager로 교체 — **규약 준수의 배당금** |
| Snowflake DDL·loader (작성 완료·휴면) | 🟢 **재활성** | 이관 자산 중 준비도 최상 |
| 재시도·폴백 체인 | 🟢 **그대로** | Hop 네이티브 재구현 시 A-015~A-107 계열 장애 **전부 재발 위험** |
| 오케스트레이션 DAG (워크플로우 6종·41잡) | 🔴 **재구축** | Hop Workflow(제어) + Pipeline(데이터) |
| 시크릿 28종 | 🔴 **재구축** | GitHub Secrets → AWS Secrets Manager |
| 품질 게이트 전달 (`GITHUB_OUTPUT`) | 🔴 **재구축** | 종료코드 + `NEXUS_EXT.OPS.DQ_RUN_RESULT` 테이블 |
| 아티팩트·`git push` 저장 | 🔴 **재구축** | 오브젝트 스토리지로 전환 |

> **핵심 권고**: Hop은 **오케스트레이션·적재·표준 변환**에 쓰고, **수집·파싱은 Python 모듈 호출로
> 유지**한다. 커넥터를 Hop 네이티브 변환으로 재작성하는 것은 비권고 — 2년치 실패 디버깅이
> 축적된 자산이다.

### 2.2 Snowflake EDP 계층 매핑

```text
Stage(S3/오브젝트)  →  NEXUS_EXT.ODS      vintage append-only (개정치 덮어쓰기 금지)
                    →  NEXUS_EXT.SILVER   단위·엔티티 정규화 (QUDT·entities.yaml)
                    →  NEXUS_EXT.MART     ASOF 피처마트 (available_at ≤ t)
                    →  NEXUS_EXT.LOCKBOX  실험 스냅샷 (재현성 동결)
```

**D-021 기술 가드레일 3종** — 정책이 아니라 권한으로 강제한다.

| # | 가드레일 | 구현 |
|---|---|---|
| G-1 | 물리 분리 | `NEXUS_EXT` 전용 DB. 내부 EDP DB와 별도 |
| G-2 | 권한 차단 | Nexus 서비스 롤에 내부 스키마 `SELECT` **미부여** → 크로스 DB 조인이 권한 오류로 실패 |
| G-3 | 감사 | 쿼리 이력에서 내부 스키마 참조 0건을 정기 확인 |

> ⚠️ **기존 `MERGE INTO ... UPDATE SET` 업서트 로직은 as-of 규칙 위반**이다(개정치를 덮어씀).
> D-023에 따라 vintage별 append로 PK를 재설계해야 한다.

### 2.3 비정형 데이터(PDF 2,231건 + 요약 2,240건, 약 1.65GB)

| 대상 | 위치 |
|---|---|
| PDF 원본 바이트 | **오브젝트 스토리지(S3)** — Snowflake에 적재하지 않음 |
| 메타·추출 텍스트·근거(EvidenceSpan) | **Snowflake** (External Stage + Directory Table로 카탈로그화) |

> **선결 과제**: 현재 1.65GB 문서가 **Git에 커밋**돼 있다. 이관 전 반드시 오브젝트 스토리지로
> 분리해야 한다 — 저장소 비대는 이관 원가에 직접 반영된다.

### 2.4 단계·시점

| 단계 | 시점 | 내용 | 선행조건 |
|---|---|---|---|
| 0 | **지금~9/10** | **이관하지 않음.** 이식성만 확보(§3) | — |
| 1 | 9월 하순 | as-of 컬럼 보강 + DuckDB feature mart 확정 | data/schemas 개정 |
| 2 | 10월 | Snowflake `NEXUS_EXT` 스키마 생성·DDL 재활성·시범 적재 | 계정·롤 발급 |
| 3 | 10~11월 | Hop 파이프라인 정의(오케스트레이션만), 시크릿 이관 | ETL 서버 프로비저닝 |
| 4 | 11월 CT 통합 후 | 아웃바운드 allowlist 반영, 스케줄 전환, Actions 폐기 | 방화벽 승인 |

---

## 3. 도구 도입 재판단 — **직전 권고를 철회합니다**

| 도구 | 8/12 오전 권고 | **확정 판단** | 근거 |
|---|---|---|---|
| **Supabase** | [B] 도입(무료 티어) | 🔴 **철회 — 도입하지 않음** | 회사가 **폐지 중인 PostgreSQL**을, **사외 3rd-party**에, **이관 3개월 전**에 신설. 목표 아키텍처 어디에도 없음 |
| **Neo4j AuraDB** | [B] 조건부 도입 | 🔴 **무기한 보류** | 선행조건(validated 엣지 100건) **현재 0건** + 현행·목표 아키텍처에 **그래프 DB 카테고리 자체가 부재** |
| **DuckDB** | 1순위 | 🟢 **유지** | 파일 임베디드 — 서버·계정 없음, 이식성 100%. as-of join에 **어차피 필요** |
| **Snowflake** | 보류 | 🟢 **보류 해제** | 구 근거("내부 웨어하우스 목적 소멸")가 무효화 — 이제 **전사 단일 저장 계층** |
| **Azure ML** | G2 학습 시 | 🟡 **Challenger 단계로 연기** | 9/10 이전 도입 시 플랫폼·모델 동시 변경으로 성능 교란 |

**이관 원가 비교** — 왜 Supabase가 손해인가

| 시나리오 | 지금 투입 | 11월 추가 투입 | 총 공수 | 잔존 자산 |
|---|---|---|---|---|
| A. Supabase 도입 | 스키마·적재·RLS ≈ 3인일 | Snowflake 재적재·스크립트 재작성·계정 폐기 ≈ 5인일 | **≈8인일** | **0 (전량 폐기)** |
| B. DuckDB만 | feature mart ≈ 2인일 (**어차피 필요**) | parquet → Snowflake external stage ≈ 1인일 | **≈3인일** | **parquet 전량 승계** |

차액 **≈5인일 + 벤더 심의 리드타임**. 그 대가는 "관리형 PostgreSQL의 편의" 하나이며,
그 편의는 11월에 소멸합니다.

> **조정자께**: 직전 세션에서 Supabase 가입(약 15분)을 요청드렸는데, **철회합니다.
> 계정 생성 작업은 하지 않으셔도 됩니다.** 회사 아키텍처 정보를 먼저 주셨다면 나오지
> 않았을 권고였습니다.

---

## 4. 11월 CT 통합과 마일스톤 충돌

| 항목 | 판정 | 대응 |
|---|---|---|
| G1 8/31 · G2 Preview 9/10 | 🟢 **직접 충돌 없음** | 납기가 통합 창보다 앞섬 |
| 방화벽 아웃바운드 allowlist | 🟡 **간접 위험** | 외부 API 30여종의 도메인 목록을 **미리 제출**해야 함. CT 통합 후 차단되면 파이프라인 전면 정지 |
| 시크릿 28종 이관 | 🟡 간접 | 소유자·만료일 대장 작성 필요 |
| 변경 동결(freeze) 기간 | 🟡 간접 | 통합 전후 배포 제약 — 일정 확인 필요 |
| 저장소 1.65GB | 🟡 간접 | 이관 전 오브젝트 스토리지 분리(§2.3) |

**Purview ↔ `src/semantic/*.yaml`**: 중복이 아닙니다. 계층이 다릅니다 —
Purview는 **물리 자산 카탈로그**, 시맨틱 레이어는 **도메인 온톨로지**입니다.
Git YAML을 원천으로 두고 카탈로그로 **단방향 투영**하면 정합됩니다.

**Apache Hop ↔ 유료 API**: 무관계입니다. Hop은 *ETL 도구 라이선스*를 없앨 뿐이고,
Databento·TE·Perplexity·OpenAI는 *데이터 원재료비·컴퓨트비*입니다. 비용 계정을 분리해
별도 방어선(월 상한·사용량 알림)을 두는 것을 권고합니다.

---

## 5. 지금 해야 할 일 — 인프라가 아니라 **이식성**

| 우선 | 항목 | 이유 |
|---|---|---|
| 1 | **`data/schemas` as-of 컬럼 보강**(`available_at`·`release_time`·`source_vintage`) | D-023 게이트. Snowflake ODS 설계의 전제이자 모델 투입 조건 |
| 2 | **`git push`를 데이터 저장소로 쓰는 구조 제거** | Hop·Snowflake 어디에도 없는 패턴. 이관 시 전부 재작성 |
| 3 | **DQSOps 게이트 fail-open 수정** | `GITHUB_OUTPUT` 미설정 시 통과 — Actions 밖에서는 게이트가 무력화됨 |
| 4 | **아웃바운드 도메인 목록 문서화** | CT 통합 시 방화벽 신청에 필수 |
| 5 | 커넥터의 Actions 전용 API 의존 제거 | 이미 대부분 순수 Python — 잔여분만 정리 |

---

## 6. 조정자 확인 요청

| # | 확인 사항 | 이유 |
|---|---|---|
| 1 | Nexus 데이터의 **Snowflake EDP 진입 승인** 여부 (`NEXUS_EXT` 전용 DB) | 승인되면 ADLS 폐지 후 착지점이 확보됨. 불가 시 대안 저장소 지정 필요 |
| 2 | **MS Foundry** = Azure AI Foundry가 맞는지 | 명칭 확인 — P1-05/06 LLM 계층 배치에 영향 |
| 3 | 11월 **변경 동결 기간**과 방화벽 allowlist **신청 마감일** | 30여종 외부 도메인 사전 제출 필요 |
| 4 | Apache Hop ETL 서버 **사양·Python 사이드카 가능 여부** | Hop은 JVM 기반 — 커넥터 Python 실행 환경 필요 |
