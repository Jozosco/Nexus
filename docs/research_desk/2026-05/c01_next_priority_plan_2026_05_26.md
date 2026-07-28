# C-01 PM 다음 우선순위 계획

**작성일**: 2026-05-26  
**패널**: C-01(PM) · C-05(QA/QC) · C-08(DQOps)  
**분류**: 내부 프로젝트 관리 문서  
**참조**: `reports/wbs/wbs_full_project.md` v1.6 · `MEMORY.md` PM-020

---

> **HITL 게이트**: 이 계획은 데이터 파이프라인 운영 목적입니다. 조달 실행 결정은 CLAUDE.md §6 HITL 프로세스를 반드시 거쳐야 합니다.

---

## 1. C-01 현황 평가

### 1.1 완료된 핵심 작업 (Session 19~21)

| WBS | 작업 | 상태 | 품질 영향 |
|---|---|---|---|
| 1.1.22 | GPR openpyxl 버그 수정 | ✅ | GPR 역사 데이터 수집 복구 |
| 1.1.23 | 백필 워크플로우 C-08→C-06→G1 파이프라인 추가 | ✅ | 데이터 품질 게이트 확립 |
| 1.1.24 | AIS 해협 탱커 모니터 커넥터 | ✅ (Phase A) | 신규 지정학 변수 |
| 1.1.25 | Parquet→Excel 내보내기 | ✅ | 다운로드 가용성 |
| 1.1.26 | G1 PDF+Markdown 다중 형식 출력 | ✅ | 보고서 접근성 |
| 1.1.27 | Hormuz Monitor 기술 분석 | ✅ | 아키텍처 결정 확정 |
| 1.1.28 | BDI TE SDK → REST API 교체 | ✅ | Shipping 백필 오류 해소 |
| 1.1.29 | WASDE HISTORICAL_START_YEAR 수정 | ✅ | 작황 데이터 백필 활성화 |
| 1.1.30 | PDF 한국어·영어 분리 출력 | ✅ | 보고서 국제화 |
| 1.1.31 | C-05 QA/QC 에이전트 신설 | ✅ | 코드 품질 게이트 확립 |
| 1.1.32 | 역사 위기 분석 수정 (C-02×P-02) | ✅ | 분석 정확도 향상 |

### 1.2 잔여 블로커 현황

| ID | 블로커 | 해결 주체 | 긴급도 |
|---|---|---|---|
| **B-01** | `DATA_GO_KR_SERVICE_KEY` 만료 → 관세청 401 | 사용자 (data.go.kr 수동 갱신) | 🔴 HIGH |
| **B-02** | `AISSTREAM_API_KEY` 미등록 → AIS Phase A 미작동 | 사용자 (aisstream.io 무료 가입) | 🟡 MEDIUM |
| **B-03** | PR #17 미병합 → main 브랜치 Actions 미작동 | 사용자 (GitHub PR 병합 승인) | 🔴 HIGH |
| **B-04** | `USDA_FAS_API_KEY` 미등록 → WASDE 인증 제한 | 사용자 (FAS OpenData 포털 발급) | 🟡 MEDIUM |

---

## 2. C-05 × C-08 협업 — 다음 코드 작업 사전 검토

> **운영 규칙**: 이하 모든 코드 관련 작업은 구현 전 C-05 리뷰 → C-08 데이터 품질 검증 순서를 따릅니다.

### C-05가 다음 PR에서 검토할 핵심 항목

| 파일 예정 변경 | C-05 핵심 검토 포인트 |
|---|---|
| `wasde_connector.py` | USDA FAS 인증 헤더 처리, 연도 루프 내 pd.concat O(n²) 방지 |
| `customs_connector.py` | UN Comtrade comtradeapicall 레이트리밋 1초 sleep, 빈 응답 처리 |
| `shipping_connector.py` | TE REST API 401/403 처리 분기, stooq 심볼 실패 시 명확한 경고 |
| `c08_dq_validator.py` | 함수 30줄 이내 유지, 한국어 오류 메시지 `[오류]` 접두사 |

### C-08이 다음 백필 실행에서 검증할 항목

| 커넥터 | DQSOps 우선 검증 차원 | 예상 이슈 |
|---|---|---|
| shipping_indices | Completeness (BDI 히스토리 기간 확인) | TE REST 성공 여부 |
| crop_data | Timeliness (WASDE 연도별 수집 완료 확인) | HISTORICAL_START_YEAR 적용 확인 |
| customs_import | Accuracy (HS코드 10단위 값 범위 검증) | 401 → Comtrade 폴백 성공 여부 |
| ais_strait_risk | Completeness (AISSTREAM_API_KEY 없으면 0행) | Perplexity 폴백 작동 확인 |

---

## 3. WSJF 우선순위 (다음 3가지 스프린트)

> **WSJF** = (사업가치 + 시간긴박도 + 리스크 감소) ÷ 업무크기

### Sprint 1 — 즉시 실행 (이번 주, ~8시간)

| 우선순위 | 작업 | WSJF 점수 | 담당 | 소요 |
|---|---|---|---|---|
| **P0** | **PR #17 병합** → main 브랜치 Actions 활성화 | 9.0 | 사용자 | 10분 |
| **P0** | **DATA_GO_KR_SERVICE_KEY 갱신** → 관세청 수집 복구 | 8.5 | 사용자 | 30분 |
| **P0** | **daily 워크플로우 스케줄 재활성화** (CLAUDE.md `cron` 주석 해제) | 8.0 | Claude | 2h |
| **P1** | **AISSTREAM_API_KEY 등록** → AIS Phase A 정상화 | 6.5 | 사용자 | 15분 |
| **P1** | **USDA_FAS_API_KEY 등록** → WASDE 인증 강화 | 6.0 | 사용자 | 15분 |

### Sprint 2 — 단기 (다음 주, ~24시간)

| 우선순위 | 작업 | WSJF | 담당 | 소요 |
|---|---|---|---|---|
| **P1** | **Historical Backfill 재실행** (BDI+WASDE 수정 후) | 8.0 | Claude | 30분 트리거 |
| **P1** | **WBS 1.1.8 — GE 데이터 품질 테스트** (`tests/test_pipeline_quality.py`) | 7.5 | C-08 | 16h |
| **P1** | **G1 분석 안정화** — 30일+ 데이터 누적 후 재실행, LASSO 수렴 확인 | 7.0 | C-03 | 8h |
| **P2** | **UN Comtrade WITS 대안 구현** → customs_connector 폴백 강화 | 6.0 | C-04 | 8h |

### Sprint 3 — 중기 (2~4주, ~80시간)

| 우선순위 | 작업 | WSJF | 담당 | 소요 |
|---|---|---|---|---|
| **P1** | **G2 가격 밴드 모델 착수** (G1 안정화 후) — GARCH + LSTM 설계 | 8.5 | C-03 | 40h |
| **P1** | **news_sentiment_connector.py** — Phase B FinBERT 감성 분석 | 7.0 | C-04 | 24h |
| **P2** | **G3 레짐 감지 설계** — Markov Regime Switching 모델 설계 | 6.5 | C-03 | 32h |
| **P2** | **WBS 1.3 EDA 실행** — C-06 외부 데이터 EDA 보고서 | 6.0 | C-06 | 24h |
| **P3** | **MarineTraffic API 평가** (Phase B — AIS 정확도 향상) | 4.0 | C-01 | 8h |

---

## 4. 단계별 실행 절차 (Step-by-Step)

### Step 1: PR #17 병합 (즉시)
```
1. GitHub → Pull Requests → PR #17 (claude/setup-nexus-llm-tools-RX4aS → main)
2. "Squash and merge" 또는 "Merge" 클릭
3. Actions 탭 → external_data_refresh.yml 스케줄 트리거 확인
4. pipeline-summary job 완료 후 C-08 DQ 리포트 확인
```

### Step 2: 수동 조치 항목 (사용자 직접 실행)
```
관세청 키 갱신:
  1. data.go.kr 로그인 → 마이페이지 → 활용현황
  2. '관세청_품목별국가별수출입실적(GW)' → 재신청/갱신
  3. 신규 serviceKey → GitHub Secrets → DATA_GO_KR_SERVICE_KEY 업데이트

AIS 키 등록:
  1. aisstream.io → 무료 가입 → API Key 발급
  2. GitHub Secrets → AISSTREAM_API_KEY 등록

USDA FAS 키 등록:
  1. apps.fas.usda.gov/opendatawebV2 → 계정 생성/로그인 → API Key 발급
  2. GitHub Secrets → USDA_FAS_API_KEY 등록
```

### Step 3: 스케줄 재활성화 (PR 병합 후)
```
파일: .github/workflows/external_data_refresh.yml
변경: cron 스케줄 주석 해제
  on:
    schedule:
      - cron: "30 20 * * 0-4"  # KST 05:30, 월~금
```

### Step 4: Historical Backfill 재실행 (키 등록 완료 후)
```
Actions → Historical Data Backfill — 5-Year Seed → Run workflow
  start_year: 2020
  end_year: 2025
  connector: all
  skip_analysis: false
```

### Step 5: 결과 확인 (C-05 × C-08 협업)
```
C-08 DQSOps 리포트 확인:
  - reports/data_quality/dq_report_YYYYMMDD.json
  - overall_status: PASS (≥0.70) 확인
  - REJECTED 커넥터: 코드 수정 후 PR → C-05 리뷰

C-06 EDA 리포트 확인:
  - reports/pipeline/c06_eda_report_YYYYMMDD_backfill.json
  - price_date_range.min: 2020-01-01 부근 확인
  - stale_connectors: 없음 확인

G1 분석 결과:
  - reports/pipeline/g1_variable_importance_*_ko.pdf 다운로드
  - LASSO 계수 비(非)영 변수 ≥ 5개 확인 (MEMORY M-005)
```

---

## 5. G2/G3 착수 전 완료 기준 (C-01 게이트 체크리스트)

G2(가격밴드) 및 G3(레짐감지) 착수 전 다음 조건이 모두 충족되어야 합니다:

| 체크 항목 | 기준 | 현재 상태 |
|---|---|---|
| G1 LASSO 비영 계수 | ≥ 5개 (MEMORY M-005 — 30일 데이터 필요) | ❓ 데이터 축적 중 |
| BDI 히스토리 수집 | 2020~현재 ≥ 500 레코드 | ❓ BDI REST 수정 후 재확인 |
| WASDE PSD 수집 | 2020~2025 ≥ 5개 마케팅 연도 | ❓ HISTORICAL_START_YEAR 수정 후 재확인 |
| C-08 DQ 전체 PASS | overall_dq_score ≥ 0.70 | ❓ 백필 재실행 후 확인 |
| PR #17 병합 | main 브랜치 Actions 활성화 | ❌ 미병합 |
| Korea Customs 수집 | comtrade 폴백 또는 관세청 키 갱신 | ❌ 키 만료 |

---

## 6. 리스크 매트릭스

| 리스크 | 확률 | 영향도 | 완화 방안 |
|---|---|---|---|
| BDI TE REST API 401 (구독 플랜 문제) | MEDIUM | HIGH | stooq 폴백 + Perplexity 프록시 |
| WASDE FAS API 연간 데이터 누락 | LOW | MEDIUM | USDA_FAS_API_KEY 등록 시 해소 |
| G1 LASSO 계수 계속 0.0 (데이터 부족) | MEDIUM | HIGH | 30일 대기 후 재실행, Ridge/Elastic Net 대체 |
| Korea Customs 키 갱신 실패 | LOW | MEDIUM | UN Comtrade + WITS 폴백 강화 |
| PR #17 병합 지연 → Actions 미작동 | 사용자 결정 | CRITICAL | 즉시 병합 권고 |

---

## 7. C-05 운영 규칙 (신규 — 즉시 적용)

앞으로 모든 코드 관련 작업에 적용:

```
1. 신규 커넥터 또는 기존 코드 수정 → 개발 완료
2. PR 생성 → C-05 자동 리뷰 (claude-haiku-4-5)
3. C-05 → Executive Score 출력
   ├─ 🟢 APPROVED: C-01 PM 최종 승인 → merge
   ├─ 🟡 REQUEST CHANGES: 개발자 수정 → C-05 재검토
   └─ 🔴 REJECTED: C-01 에스컬레이션 → 설계 재검토
4. merge 후 → GitHub Actions 자동 실행
5. 실행 완료 → C-08 DQSOps 검증
6. PASS: C-06 EDA → G1 분석
   REJECTED: C-05 코드 리뷰 재요청 (루프)
```

---

*Project Nexus · C-01 PM 우선순위 계획 · 2026-05-26*  
*C-05 리뷰 대상: 이 문서의 코드 참조 섹션 (Step 3 cron 변경)*
