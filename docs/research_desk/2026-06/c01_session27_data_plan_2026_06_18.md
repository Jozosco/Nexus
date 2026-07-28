# C-01 PM × 멀티에이전트 패널 — Session 27 데이터 구성 및 보고서 개편 계획

**작성일**: 2026-06-18  
**패널**: C-01(PM) · C-02(시장분석) · C-03(데이터) · C-06(EDA) · C-08(DQSOps) · P1-01(상품) · P1-02(거시) · P1-03(지정학) · P1-04(공급망)  
**참조 요청**: Session 27 사용자 지시사항

---

## §1. GAIN PDF 데이터 활용 계획 (요청 1.1.1)

### 1.1 현황

- main 브랜치 root에 ~519개 USDA FAS GAIN Oilseeds PDF 파일 존재 (형식: `YY.MM_Country_Title.pdf`)
- 대상 이동 경로: `data/raw/USDA/FAS/GAIN/Oilseeds/`
- 기간: 2017년 10월 ~ 2021년 12월 (일부 누락 월 있음)
- 국가: 아르헨티나, 브라질, 중국, EU, 인도, 인도네시아, 일본, 말레이시아, 파키스탄, 러시아, 한국, 태국, 터키, 우크라이나, 베트남 등 50+ 국가

### 1.2 C-02 × P1-01~04 활용 전략

**활용 가능 정보 (패널 합의):**

| 추출 항목 | 해당 에이전트 | 대두유 관련성 | 추출 방법 |
|---|---|---|---|
| 작황 전망 (Production Outlook) | C-03 / P1-01 | WASDE 서프라이즈 선행지표 | pdfplumber 표 추출 |
| 정부 정책 변경 (수입관세, 수출세) | P1-03 / P1-04 | 공급망 비용 직접 영향 | FinBERT 키워드 + regex |
| 재고/소비 전망 (S&U 관련) | C-03 / P1-01 | WASDE_SBO_STU 검증 보조 | 숫자 패턴 추출 |
| 무역 흐름 변화 (수출입 방향성) | P1-04 | GATS_US_SBO_EXPORT_KOREA 검증 | 국가별 무역 표 |
| 지정학 리스크 서술 | P1-03 | GPR 보조 신호 | 텍스트 감성 분석 |

**C-01 결정(초안):**
- Phase A: `ingest_fao_amis_pdf.py` 패턴 기반, 핵심 수치(생산/소비/재고/가격) 위주 추출
- Phase B: FinBERT 정책 감성 스코어링
- 우선 국가: 브라질, 아르헨티나, 인도, 인도네시아, 중국 (대두유 공급망 핵심 5개국)

### 1.3 파일 이동 계획

**구현 방법**: GitHub Actions 워크플로우 (`reorganize_fas_files.yml`)

- 트리거: `workflow_dispatch` (수동 실행)
- 작업: root PDFs → `data/raw/USDA/FAS/GAIN/Oilseeds/` git mv
- 예상 소요: ~5분 (git mv 519건)
- 주의: root에 있는 PDF 파일은 현재 `.gitignore`에 해당 없음 → 이동 후 root 정리 필요

**→ 사용자 확인 필요**: 워크플로우 실행 전 승인

---

## §2. GATS Excel 파일 활용 계획 (요청 1.2)

### 2.1 파일 현황

**기존 GATS 폴더 파일 (HS 1507.10 추정):**

| 파일명 | 경로 | 내용 |
|---|---|---|
| 2017~2026년 미국 對국가별 수출량.xlsx | `data/raw/USDA/FAS/GATS/` | HS 1507.10 수출 물량 |
| 2017~2026년 미국 對국가별 재수출량.xlsx | `data/raw/USDA/FAS/GATS/` | HS 1507.10 재수출 물량 |

**신규 업로드 파일 (HS 1507.90, FAS 루트):**

| 파일명 | 경로 | 내용 |
|---|---|---|
| 2017~2026년 미국 對국가별 수출량.xlsx | `data/raw/USDA/FAS/` | HS 1507.90 수출 물량 |

**9개년 요약 파일 (FAS 루트):**

| 파일명 | 내용 | 단위 |
|---|---|---|
| 9개년 미국 대두 수출액_상위 10개국.xlsx | 미국 대두 수출액, 상위 10개국, 2017~2025 | USD |
| 9개년 미국 대두박 수출액_상위 10개국.xlsx | 미국 대두박 수출액, 상위 10개국, 2017~2025 | USD |
| 9개년 미국 대두유 수출액_상위 10개국.xlsx | 미국 대두유 수출액, 상위 10개국, 2017~2025 | USD |

### 2.2 폴더 재구성 계획

**제안 구조:**

```
data/raw/USDA/FAS/GATS/
├── 1507.10/              ← 기존 파일 이동 (수출량 + 재수출량)
│   ├── 2017년 미국 對국가별 수출량.xlsx
│   ├── 2017년 미국 對국가별 재수출량.xlsx
│   └── ... (2018~2026)
├── 1507.90/              ← 신규 파일 이동
│   ├── 2017년 미국 對국가별 수출량.xlsx
│   └── ... (2018~2026)
├── summary/              ← 9개년 요약 파일
│   ├── 9개년 미국 대두 수출액_상위 10개국.xlsx
│   ├── 9개년 미국 대두박 수출액_상위 10개국.xlsx
│   └── 9개년 미국 대두유 수출액_상위 10개국.xlsx
└── README.md
```

### 2.3 C-03 × P1-01~04 데이터 활용 전략

**HS 코드별 역할 분담:**

| 파일 종류 | 지표 코드 | G1/G2/G3 역할 |
|---|---|---|
| 1507.10 수출량 (조유) | `GATS_US_SBO_1507_10_EXPORT` | G1 피처 후보: 미국 조대두유 수출 흐름 |
| 1507.90 수출량 (정제유) | `GATS_US_SBO_1507_90_EXPORT` | G1 핵심: GATS_US_SBO_EXPORT_KOREA (D-015) |
| 재수출량 | `GATS_US_SBO_REEXPORT` | G1 보조: 미국 중개 무역 패턴 |
| 9개년 대두유 수출액 | `GATS_US_SBO_EXPORT_VALUE` | G2 보조: 달러 기준 무역 가치 |
| 9개년 대두 수출액 | `GATS_US_SOY_EXPORT_VALUE` | G1 보조: 대두 vs 대두유 수출 상관 |
| 9개년 대두박 수출액 | `GATS_US_SBM_EXPORT_VALUE` | G1 보조: 압착 마진 계산 보조 |

**C-01 결정(초안):**
- 1507.90(정제유)이 한국 수입 핵심 HS 코드 → D-015 `GATS_US_SBO_EXPORT_KOREA` 지표 구현 우선
- 1507.10(조유)은 보조 지표로 G1 변수 풀에 포함
- 9개년 요약은 연간 무역 패턴 분석용 (월별 세분화 없음, G1 Granger 검정 보조)
- `ingest_gats_data.py` (Sprint 4-A) 파서: 1507.10/1507.90 각각 파싱 → 별도 parquet

### 2.4 파일 이동 계획

**구현 방법**: 동일 GitHub Actions 워크플로우 (`reorganize_fas_files.yml`)에 포함

- GATS 기존 파일 → `GATS/1507.10/`
- FAS 루트 수출량.xlsx → `GATS/1507.90/`
- FAS 루트 9개년 파일 → `GATS/summary/`

---

## §3. 보고서 구조 개편 계획 (요청 1.1.3)

### 3.1 현재 보고서 구조 vs 제안 구조

| # | 현재 섹션 | 변경 제안 | 영향도 |
|---|---|---|---|
| 1 | 경영진 요약 (KPI 카드 + 신호 배너) | 유지 | 없음 |
| 2 | 데이터 수집 현황 → 활용 데이터 | 명칭 변경 (완료) | 낮음 |
| 3 | 변수 중요도 (LASSO 기반) | **신규**: 상위 5개 핵심 변수 섹션 추가 (기존 표 위) | 중간 |
| 4 | 피처 엔지니어링/선택 방법론 | 현행 유지 + 실제 선택 결과 추가 | 중간 |
| 5 | LASSO 계수 0.0 진단 | 유지 | 없음 |
| 6 | 구조적 단절 임계값 현황 | 유지 | 없음 |
| 7 | 변수 카탈로그 | 유지 | 없음 |
| 8 | Granger 인과검정 | 유지 | 없음 |
| 9 | 핵심 인과관계 체인 | **강화**: 상위 5개 변수와 연결된 단계별 설명 추가 | 높음 |

### 3.2 상위 5개 핵심 변수 섹션 설계 (C-03 × P1-01 합의)

**표시 내용:**
- 선택 기준: D-014 5단계 게이트 적용 결과 (|피어슨 r| 상위, LASSO 비제로, Granger 인과 유의)
- 데이터 부족 시: D-015 Phase A 확정 8개 피처 중 현재 수집된 상위 5개 표시
- 각 변수별 표시 항목: 변수명 | 카테고리 | 현재값/최신값 | 피어슨 r | LASSO 계수 | 대두유 가격 영향 방향

**C-01 판단:**
- 데이터 충분 시: 실제 분석 결과 상위 5개 (동적)
- 데이터 부족 시: D-015 Phase A 핵심 8개 피처 중 수집 완료된 것 우선 표시 (정적 fallback)
- 구현 방법: `_render_top5_variables(importance_df, lang)` 신규 함수

### 3.3 Feature Engineering/Selection 실제 결과 표시 (C-03 × C-06 × C-08)

**현재**: `_render_feature_selection_methodology()` = 방법론 설명만 (D-014/D-015 기반)  
**추가**: 현재 분석 실행에서 실제 적용된 결과

```
5단계 게이트 실제 적용 결과 (현재 분석 기준):
1단계 DQSOps:    N개 커넥터 중 M개 PASS (기준 ≥ 0.70)
2단계 단변량:    전체 K개 변수 → |r| ≥ 0.25 충족 J개
3단계 공선성:    VIF 제거 후 I개 잔류
4단계 ML 순위:   LASSO+SHAP+Granger 합산 상위 H개
5단계 도메인:    P1-01~04 검토 → 최종 G개 확정
```

- 구현: `run()` 함수에서 각 단계 실행 후 결과 dict 생성 → `_render_html()`에 전달

### 3.4 단계별 인과관계 체인 (상위 5개 변수 연결)

**설계:**
- 상위 5개 핵심 변수 각각에 대해 이미 `_CAUSAL_CHAINS` 정의된 체인 자동 연결
- 체인이 없는 변수: 자동 생성 (변수 카테고리 + 방향성 기반)
- "과거 유사 사례" 참조: `soybean_oil_historical_crisis_corrections_2020_2025.md`에서 관련 케이스 자동 매핑

**구현**: `_render_top5_causal_chains(importance_df, lang)` 신규 함수

---

## §4. 비정형 데이터 수집 현황 (요청 1.3 / Session 26 D-018 연속)

### 4.1 현재 수집 상태

| 이벤트 유형 | 현재 수집 여부 | 커넥터 | 상태 |
|---|---|---|---|
| 호르무즈 해협 위험 | ✅ 수집 중 | `gpr_connector._fetch_hormuz_realtime()` | 실시간 전용 |
| 수에즈·홍해 후티 위험 | ✅ Session 26 추가 | `gpr_connector._fetch_geopolitical_event_proxy()` | 실시간 전용 |
| 우크라이나 흑해 회랑 | ✅ Session 26 추가 | `gpr_connector._fetch_geopolitical_event_proxy()` | 실시간 전용 |
| 미·중 관세 에스컬레이션 | ✅ Session 26 추가 | `gpr_connector._fetch_geopolitical_event_proxy()` | 실시간 전용 |
| 브라질 수확 진척률 | ✅ Session 26 추가 | `gpr_connector._fetch_geopolitical_event_proxy()` | 실시간 전용 |
| 러시아-우크라이나 전쟁 | ⚠️ 간접 수집 | GDELT (geointel) + Perplexity 프록시 | BACKFILL_MODE 건너뜀 |
| 아르헨티나 수출세 | ✅ 수집 중 | `gpr_connector._fetch_policy_news_proxy()` | 실시간 전용 |

### 4.2 GAIN PDF의 비정형 데이터 활용

GAIN PDF는 정형 수치 데이터 외에도 시장 서술적 정보를 포함:
- "분기 전망" 서술 → WASDE 서프라이즈 예측 보조 신호
- 정책 변경 서술 → 인도 관세·인도네시아 바이오디젤 선행 감지
- 교역 흐름 서술 → 한국 수입 경쟁 강도 신호

**Phase A 수집 방법**: Perplexity sonar-pro를 통해 GAIN 보고서 주요 내용 요약 요청  
**Phase B**: pdfplumber로 PDF 직접 파싱 + FinBERT 감성 스코어링

---

## §5. C-01 종합 판단 및 구현 우선순위

### 우선순위 결정

| 순위 | 작업 | WSJF | 차단 여부 |
|---|---|---|---|
| 1 | GATS 파일 폴더 재구성 (GitHub Actions) | 8.5 | G1 분석 정확도 영향 |
| 2 | GAIN PDF 폴더 이동 (GitHub Actions) | 7.8 | Sprint 4-A `ingest_gats_data.py` 전제 |
| 3 | 보고서 상위 5개 변수 섹션 추가 | 7.5 | 경영진 가독성 직결 |
| 4 | 보고서 Feature Selection 실제 결과 표시 | 7.0 | 피처 게이트 투명성 |
| 5 | `ingest_gats_data.py` 1507.10/1507.90 분리 파서 | 6.8 | Sprint 4-A 핵심 |
| 6 | 단계별 인과관계 체인 (상위 5개 연결) | 6.2 | 보고서 완성도 |

### 사용자 확인 요청 사항

아래 항목은 구현 전 사용자 승인이 필요합니다:

| 항목 | 제안 내용 | 승인 여부 |
|---|---|---|
| GATS 1507.10/1507.90 폴더 분리 | 기존 GATS 파일 → `GATS/1507.10/`, 신규 → `GATS/1507.90/`, 9개년 → `GATS/summary/` | 승인 필요 |
| GAIN PDF 이동 | root 전체 PDF → `data/raw/USDA/FAS/GAIN/Oilseeds/` | 승인 필요 |
| 보고서 섹션 신규 추가 | 상위 5개 변수 + Feature Selection 실제 결과 + 인과관계 체인 연결 | 승인 필요 |
| GAIN PDF 파싱 인제스트 | `ingest_gain_oilseeds_pdf.py` 신규 구현 (기존 FAO AMIS 패턴 유사) | 승인 필요 |

### 참조 URL 접근 불가 안내

`https://github.com/epoko77-ai/im-not-ai` — 이 저장소는 현재 세션의 GitHub MCP 접근 범위(`jozosco/nexus`만 허용) 밖에 있어 내용을 확인할 수 없습니다. 참조 내용을 직접 공유해 주시거나, 핵심 내용을 텍스트로 제공해 주시면 반영하겠습니다.

---

*→ 사용자 승인 후 구현 착수: `reorganize_fas_files.yml` GitHub Actions 워크플로우 → Sprint 4-A*  
*→ 다음 MEMORY.md 업데이트 예정: PM-026 (사용자 승인 후)*
