# Session 36 — API 갱신 판별·수동수집 데이터·비정형 해석 계획 (C-02·C-03·C-04·P1-01~05)

**작성일**: 2026-07-27

---

## 1. 필수 갱신 API 판별 방법 (Req 1.2.2)

**목표**: "어떤 API가 반드시 갱신(코드/키/엔드포인트 수정)돼야 하는가"를 체계적으로 탐지.

### 1.1 자동 판별 — LLM & Data API Health Check 확장 (2일 주기)
| 신호 | 판정 | 조치 등급 |
|---|---|---|
| HTTP 401/403 | 키 만료·미승인·정책 차단 | 🔴 필수(수동 키갱신/포털) |
| HTTP 404 / 스키마 불일치 | 엔드포인트·파라미터 변경 | 🔴 필수(코드 갱신) |
| HTTP 429 지속 | 쿼터 초과 | 🟠 백오프·배치·유료 검토 |
| 응답 빈 배열/0행 | 데이터 미제공·범위 밖 | 🟠 소스 재확인 |
| 타임아웃·연결거부 | 네트워크/호스트 차단 | 🟠 환경(Actions) 확인 |
| 200 + 정상 스키마 | 정상 | ✅ |

### 1.2 판별 절차 (체크리스트)
1. health check가 커넥터별 **최소 1콜 스모크**(키 유효·스키마·최근월 행수) 수행 → 상태 코드 기록.
2. `config/api_status.json`에 소스별 `{status, http, last_ok, msg}` 누적 → 대시보드화.
3. 🔴 등급은 **자동 GitHub Issue 생성**(Ralph Loop 패턴, CI-007) → 담당 조치.
4. 월 1회 **엔드포인트 스펙 회귀 테스트**(응답 컬럼셋 해시 비교) → 무성(silent) 스키마 변경 탐지.

### 1.3 현재 🔴 필수 갱신 목록 (기지)
| API | 문제 | 조치 |
|---|---|---|
| data.go.kr(관세청) | 신규 키 발급됨(노출→**로테이션 필수**) | Secrets `DATA_GO_KR_SERVICE_KEY` 갱신 |
| USDA FAS PSD/ESR | 엔드포인트 잦은 변경 | 수동 xlsx로 대체(우선) |
| yfinance(BO=F) | IP 차단 위험 | Databento 등 유료 검토 |

---

## 2. API 수집 불가 → 수동 수집 필수 데이터 (WASDE 확정 관련)

C-02·C-03·C-04·P1 검토: **API로 안정 수집 불가 → 수동 업로드가 정답**인 데이터.

| 데이터 | API 불가 사유 | 수동 소스 | 현황 |
|---|---|---|---|
| WASDE 취합본(과거·정제) | FAS API 스키마 불안정·품목 제약 | USDA 다운로드 xlsx | ✅ 15개년 |
| PSD(품목·속성 전체) | PSD API 부분·형식 상이 | PSD online xlsx | ✅ xlsx |
| GATS 미국 수출량/액 | API 세분·인증 제약 | GATS xlsx | ✅ |
| 관세청 GW(한국 수입) | 키 401·네트워크 차단(A-069) | data.go.kr CSV/xlsx | 🔄 업로드 |
| Trading Economics 상품 | TE API 히스토리 불안정 | TE xlsx | ✅ 15개년 |
| NASA POWER 과거 | (API 가능하나) 대량·잠정 | POWER xlsx | ✅ 15개년 |
| GAIN/FAO 정성 보고서 | API 없음(PDF only) | 수동 PDF | ✅ |

> **원칙(C-03)**: 위 데이터는 **수동 업로드가 1차**, API는 최신월 보충. Historical Analysis
> 파이프라인은 이들 수동 데이터 전용(include_api=false).

---

## 3. 비정형 데이터 해석·핵심정보 추출 계획 (Req 2 + WASDE)

**전제(조정자)**: 관계 분석은 **비정형(FAO-AMIS·GAIN PDF)까지 완전히 해석·통합**해야 의미. 정형
상관만으론 불충분.

### 3.1 요약·추출 가능성 평가 (C-04·P1-05)
| 코퍼스 | 규모 | 추출 가능성 | 도구 |
|---|---|---|---|
| GAIN (Biofuels/Oilseeds) | 1,234 PDF | ✅ 높음(텍스트 PDF) | pdfplumber → 신호 7종 태그(구현됨) |
| FAO AMIS Market Monitor | 137 PDF | ✅ 높음(표·서술) | pdfplumber + 표추출(camelot/pdfplumber tables) |

### 3.2 처리 파이프라인 (제안)
```
PDF → 텍스트/표 추출 → ① 핵심 지표(수급 전망치·정책 변경) 파싱
                      → ② 신호 태그(수출규제·관세·바이오연료·기상·압착·재고·생산변동)
                      → ③ 감성/방향성(강화·완화) 스코어 (P1-05)
                      → ④ 엔티티·인과 그래프 매핑 (P1-06 시맨틱)
→ 월별 시계열 parquet (정형 지표와 결합 → 상관·리드랙 재분석)
```

### 3.3 추가 에이전트/도구 필요성 (협의 결과)
| 필요 | 담당 | 도구/라이브러리 |
|---|---|---|
| PDF 표 추출 강화 | C-04 | `pdfplumber.extract_tables` · `camelot` |
| 감성 스코어 | P1-05 | `transformers`(FinBERT) — 승인 시 |
| 엔티티·온톨로지 | P1-06 | `src/semantic/*.yaml` + 지식그래프(arXiv 2503.07584) |
| 대량 PDF 병렬 | C-04 | 배치 스크립트(ingest_gain_pdf 확장) |

- **결론**: 신규 에이전트는 **P1-05(감성)·P1-06(시맨틱)** 로 충분(이미 골격 생성). 추가 에이전트
  불필요. 도구는 pdfplumber(표)+FinBERT(감성)+시맨틱 YAML로 커버.
- **선행 작업**: `ingest_gain_pdf.py`·FAO AMIS 파서를 15개년 전체 실행 → **신호/지표 시계열 parquet**
  확보 → §session35 정형 상관분석에 **비정형 축 결합** 후 재실행 → 완전한 관계 분석.

### 3.4 즉시 실행 권고
1. FAO AMIS PDF 파서 신규(`ingest_fao_amis_pdf.py` 확장) — 월별 수급 표 추출.
2. GAIN 신호 태그 15개년 시계열화(백필 gain-pdf 잡).
3. 정형(TE/WASDE/NASA) + 비정형(GAIN/FAO 신호) 결합 상관·Granger 재실행 → 통합 리포트.

---

## 4. 확정 요청
1. API 상태 `config/api_status.json` + 2일주기 헬스체크 확장 + 🔴 자동 Issue 승인.
2. 관세청 신규키 **로테이션 후 Secrets 갱신** 확인.
3. 비정형 처리 파이프라인(§3.2) 착수 승인 — FAO/GAIN 시계열화 후 통합 관계분석.
4. FinBERT 감성(P1-05) 도입 시점(Phase 2 내 vs 후).
