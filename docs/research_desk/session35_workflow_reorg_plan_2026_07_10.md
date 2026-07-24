# Session 35 — 워크플로우 재정비 + API 오류 근본원인 계획 (승인 대기)

**작성일**: 2026-07-10 · **참여**: C-03 · C-05 · C-06 · P1-01~04  
**성격**: ⏸️ **구현 전 담당 승인 필요** (Req 1.2). 아래 계획 확정 후 착수.

---

## 0. 워크플로우 정리 결과 (Req 1.1 — 완료)
**삭제(7종, 일회성 완료)**: reorganize_{data,fas,ice,nasa_power,te}_files · auto_move_gats_files · move_gats_2026.
**유지(5종)**: external_data_refresh(일별·중단) · historical_backfill(주력) · llm_health_check ·
llm_model_monitor · reorganize_all_data_files(범용 재정리, 재사용).

---

## 1. API 오류 근본원인 분석 (Req 1.2.2 — 지속 오류 규명)

MEMORY + 코드 + 실측(A-069) 종합. 오류는 **5개 범주**로, 코드 수정만으론 해소 불가한 것이 다수.

| # | 범주 | 사례 | 근본원인 | 코드로 해결? |
|---|---|---|---|---|
| 1 | **인증 만료·미승인** | data.go.kr 401(A-025/A-036) | 포털 서비스키 만료·활용신청 미승인 | ❌ 포털 수동 갱신 |
| 2 | **네트워크 정책 차단** | apis.data.go.kr 403(A-069 실측) | 실행환경 프록시가 특정 호스트 CONNECT 거부 | ❌ 환경(Actions)에서 실행 |
| 3 | **엔드포인트·파라미터 변경** | FAS PSD/ESR URL 재변경, 관세청 파라미터명 | 제공기관의 잦은 스펙 변경 | ✅ 코드 갱신(이미 다수 반영) |
| 4 | **레이트리밋·쿼터** | Perplexity 429, Comtrade 500건/일 | 무료 티어 한도 | ⚠️ 백오프·배치(A-067 반영) |
| 5 | **패키지·IP 차단** | yfinance IP 차단, pandas-datareader 비호환 | 비공식 소스 불안정 | ⚠️ 대체 소스·직접 HTTP |

### 핵심 통찰
- **1·2번은 코드로 해결 불가** — "API 업데이트에도 오류 지속"의 진짜 원인. 포털 키 갱신 + 올바른
  실행환경(Actions, 사내 네트워크)에서만 해소.
- 개발 샌드박스는 다수 외부 호스트(data.go.kr·arxiv·medium 등) **프록시 차단** → API 테스트가
  샌드박스에서 실패해도 **Actions에선 성공**할 수 있음(환경 차이 구분 필수).

---

## 2. 계획 A — 기존 data/raw 최대 활용 (Req 1.2.1, 자동화 전까지)

> **원칙(C-03)**: 완전 자동수집 안정화 전까지 **수동 업로드 히스토리(data/raw)가 1차 소스**.
> 실시간 API는 보조·최신월 보충 역할로 강등.

| 데이터 | 1차(수동 xlsx/pdf) | 보조(API) |
|---|---|---|
| 상품가격(대체·에너지·해운) | **TE 15개년** ✅ | commodity_connector(BO=F 최신) |
| 작황기상 | **NASA POWER 15개년** ✅ | production_connector(2026 보충) |
| 수급전망 | **WASDE 취합본 15개년** ✅ | FAS API(보조) |
| 공급수요 | **PSD xlsx** ✅ | FAS PSD API(보조) |
| 무역·수입 | **관세청 GW**(수집예정) · GATS ✅ | Comtrade(교차검증) |
| 정책신호 | **GAIN/FAO PDF 15개년** ✅ | Perplexity(실시간) |

- **G1 분석 파이프라인**: 수동 xlsx 인제스터(ingest_*_xlsx.py) → parquet → G1. **API 미의존**으로
  재현성·적시성 확보(조정자 요구).

---

## 3. 계획 B — 분석 워크플로우 2종 재정비 (승인 후 구현)

### 3.1 Historical Backfill (주력)
- **현행 문제**: API 커넥터 잡과 수동 xlsx 잡이 혼재, 실패 시 전체 영향.
- **재정비안**: ①**수동 xlsx/pdf 인제스터 잡을 최상위·독립화**(API 실패와 격리) → TE·NASA·WASDE·
  PSD·GATS·GAIN·customs-GW 정형화가 API 없이 완결 ②API 커넥터 잡은 `continue-on-error`로 강등
  ③C-08 DQ → C-06 EDA → G1 게이트는 수동데이터만으로도 통과 가능하게.

### 3.2 External Data Pipeline (일별, 현재 중단)
- **재정비안**: 자동화 안정화 전까지 **중단 유지**. 재개 시 ①실패 커넥터가 파이프라인 전체를
  막지 않도록 잡 독립화 ②최신월 보충 전용(히스토리는 수동)으로 범위 축소.

### 3.3 협의 포인트 (C-05/C-06)
- C-05(코드리뷰): 인제스터 예외·백오프 표준 준수 점검.
- C-06(EDA): 수동데이터만으로 DQ 게이트 통과 기준 재정의(결측·신선도 완화).

---

## 4. 확정 요청 (구현 전)
1. **계획 A**(수동 data/raw 1차 소스) 승인 — G1을 API 비의존으로 구성.
2. **계획 B**(Backfill 잡 독립화 + External 중단 유지) 승인.
3. API 오류 1·2번(키 갱신·네트워크)은 **조정자 수동 조치** 필요 — data.go.kr 신규키 GitHub Secrets
   `DATA_GO_KR_SERVICE_KEY` 갱신 확인 요청(A-069 신규키).
4. 승인 시 historical_backfill.yml 재구성 + customs-GW 잡 추가 착수.
