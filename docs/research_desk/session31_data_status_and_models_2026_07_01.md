# Session 31 — 데이터 수집 현황·모델 배정·추가 데이터 종합 (C-01~C-03)

**작성일**: 2026-07-01 · **조정자 공유용**  
**참여**: C-01(PM) · C-02(시장조사) · C-03(데이터) · P1-01~05

---

## 1. 데이터 수집 현황 요약 (요청 6 — 중단/미수집/추가필요)

### 1.1 ⏸️ 중단(의도적)
| 항목 | 상태 | 사유 |
|---|---|---|
| External Data Pipeline (일별) | **중단**(main 병합 발효) | 9개년 히스토리 기반 G1 분석 일관성 확보 위해 조정자 요청 |

### 1.2 ✅ 이번 세션 해결(수집·정형화 완료)
| 데이터 | 소스 | 결과 |
|---|---|---|
| 대체재 유지류(Canola·Palm·Rapeseed·Sunflower)+대두 | TE 9개년 xlsx | `te_commodities_historical.parquet` 34,118행 |
| 에너지(Brent·WTI·Coal·NatGas·Gasoline) | TE 9개년 | 상동(7종) |
| 해운(BDI·CFI) | TE 9개년 | BDI 2,392행 → **z-score 산출 가능** |
| GPR_NORMALIZED | 원시 GPR 정규화 파생 | P90 분포 임계로 산출 |
| ICE 거래량(US/EU 선물·옵션) | ICE xlsx | `ice_monthly_volumes.parquet` 5,332행 |
| 무역(GATS)·수급전망(WASDE/PSD) | 기수집 xlsx | FILE_PATTERNS 등록 완료(백필 재실행 시 인식) |

### 1.3 ❌ 미수집(빌드 필요) — 승인 후 커넥터 구축
| 항목 | 원인 | 해결안(무료) | 상태 |
|---|---|---|---|
| 작황(crop) 9개년 | production 커넥터 실시간 전용·백필 공백 | **NASA POWER** agromet 백필 커넥터 신규 + WASDE 생산 파생 | 미빌드 |
| 수입통계(customs) 9개년 | 관세청 실시간·키 의존 | **UN Comtrade** 월별 백필 커넥터 신규 | 미빌드 |
| 실시간 감성 히스토리(P1-05) | Perplexity 실시간 전용 | 과거 재현 불가 → GDELT 이벤트 DB 역사 쿼리로 대체 | 설계 |

### 1.4 ➕ 추가 필요(파생·확보)
- **CBOT BO=F(대두"유" 선물)**: TE엔 Soybeans(대두)만 있음. `commodity_connector.py` BO=F 확인 필요.
- **CPO_SBO_SPREAD**: BO=F(SBO) + TE Palm Oil로 파생 산출(D-015 핵심 변수, 현재 미충족).
- **SBO_CRUSH_SPREAD / OIL_SHARE**: TE Soybeans + (BO=F, 대두박 ZM=F)로 파생.

> **C-01 방침**: 방법론은 데이터 양·유형에 따라 유연 적용(조정자 지시). 관측 부족 변수는 임계 알림
> 대신 월별 신호로 다운그레이드하는 등 적응적 처리. 공통 분석창 2017-01~2025-12로 정렬·클리핑.

---

## 2. 추가 Trading Economics 데이터 권고 (요청 4.3/4.4 — C-01 정리)

TE 제공 목록 중 **대두유 수급·가격 연관성이 높은 것**만 선별(과수집 방지). TE API 불안정으로
**조정자 수동 업로드**(기존 14종과 동일 방식) 권장.

| 우선 | 카테고리 | 품목 | 대두유 연관 경로 |
|---|---|---|---|
| 🔴 | Agricultural | **Corn, Wheat, Sugar** | 곡물 복합체 대체·에탄올 원료(옥수수·사탕수수)→식용유↔연료 |
| 🔴 | Energy | **Heating Oil, Ethanol, Naphtha** | 바이오디젤·에탄올 채널, 정제 마진 |
| 🔴 | Index | **World Container Index, EU Carbon Permits** | 컨테이너 운임(CIF), 탄소가격→바이오연료 경제성 |
| 🟠 | Industrial | **Urea, Di-ammonium(DAP)** | 비료가→대두 재배 비용→공급 |
| 🟠 | Index | **CRB Index, GSCI** | 원자재 광역 심리(거시 동행) |
| 🟢 | Metals/Livestock | (대부분 제외) | SBO 직접 연관 낮음 |

> **비권장**: Gold/Silver/Copper/Steel/Lithium 등 금속, Live Cattle/Salmon 등 축산은 SBO 직접
> 연관이 낮아 제외(필요 시 거시 헤지 지표로 소수만). → **확정 요청**: 🔴 9종 우선 업로드 여부.

---

## 3. 에이전트 역할별 모델 배정 (요청 detail 2 — 구현 완료)

최신 라인업(Opus 4.8 / Sonnet 5 / Haiku 4.5) 기준 역할 적합도로 배정:

| 계층 | 에이전트 | 이전 | 현재 | 근거 |
|---|---|---|---|---|
| 중추 추론 | C-01·C-02·C-03·P1-01·P1-02 | Opus 4.8 | **Opus 4.8**(유지) | 종합·인과·전략 최상위 추론 |
| 분석 실행 | C-04·C-06·P1-03·P1-04·P1-05 | Sonnet 4.6 | **Sonnet 5**(승급) | 추출·EDA·도메인 분석 균형 |
| 고속 검증 | C-05·C-08 | Haiku 4.5 | **Haiku 4.5**(유지) | 리뷰·품질검증 저지연 |

- 외부 LLM(Perplexity sonar / Gemini)은 데이터 수집용으로 역할 모델과 분리 — `llm_router.py`
  라우팅 유지. Gemini는 `gemini-2.5-pro` 최신 확인(별도 검토).

---

## 4. .md 관리·컨텍스트 최적화 방침 (요청 detail 7)

참조 URL 2건은 **본 환경에서 접근 불가(프록시 403)** — 확보 시 반영. 현재는 프로젝트에 이미
적용 중인 원칙 + 일반 베스트프랙티스로 운용:

| 원칙 | 현재 적용 | 강화 |
|---|---|---|
| CLAUDE.md ≤120줄 하드리밋 | ✅ 준수 | 유지 |
| 경로 스코프 규칙(§4) — 필요한 rule만 로드 | ✅ | 신규 rule도 동일 패턴 |
| 결정 압축(D-/A-/R- ID) | ✅ MEMORY 테이블 | 세션별 PM- 요약 |
| 스킬 모듈화(progressive disclosure) | ✅ `.claude/skills/` | 시맨틱 레이어도 모듈화 |
| 문서 위치 규약 | research_desk 하위 폴더 | realtime_data_acquisition/ 등 주제 분리 |

> 참조(미조회): `tech.hancom.com/claude-md-context-optimization`,
> `github.com/multica-ai/andrej-karpathy-skills`. 원문 공유 시 규칙 파일로 반영하겠습니다.

---

## 5. 확정 요청 종합
1. 작황·수입 커넥터(NASA POWER·UN Comtrade) 신규 빌드 승인.
2. CPO_SBO_SPREAD·크러시 파생 산출 승인(BO=F+TE Palm/대두박).
3. 추가 TE 🔴 9종(Corn·Wheat·Sugar·Heating Oil·Ethanol·Naphtha·WCI·EU Carbon·CRB) 업로드 여부.
4. 시맨틱 레이어 `src/semantic/` 신설 착수(별도 문서 §5).
5. 에너지 TE 파일 라우팅(요청서 "→Agricultural" 오기 → Energy로 처리) 확인.
6. Historical Backfill `connector=all` 재실행 시점(코드 반영 완료, main 병합 후).

*본 세션 코드/데이터 반영분은 전부 dev 브랜치 push 완료. 백필 재실행으로 신규 parquet·리포트 생성.*
