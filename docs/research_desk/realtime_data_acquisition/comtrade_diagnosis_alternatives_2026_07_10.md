# UN Comtrade 미수집 원인 진단 + 무료/유료 대안 (C-02 · C-04 · P1-04)

**작성일**: 2026-07-10 · **대상**: 수입통계(Imports) 9개년 백필  
**참조 패키지**: [github.com/uncomtrade/comtradeapicall](https://github.com/uncomtrade/comtradeapicall)  
**구현 위치**: `customs_connector.py::fetch_comtrade_sbo_imports_fallback`

---

## 1. 원인 진단 (등록했는데도 미수집)

현행 코드는 `UN_COMTRADE_API_KEY` 유무로 분기:
- **키 없음** → `previewFinalData` (미리보기, **호출당 500건 상한**)
- **키 있음** → `getFinalData` (`subscription_key` 전달, 10,000건/일)

### 확인된 근본 원인 (사용자 지목 2건 모두 유효)
| # | 원인 | 상세 | 코드 근거 |
|---|---|---|---|
| 1 | **무료 일일 한도 초과** | 무료 등록키도 **하루 호출·레코드 한도**(free: 소량)가 있어 9년×12월 반복 시 429 → 루프 `break`로 조기 중단, 이후 연도 전부 누락 | `if "429" in str(e): break` (L346-348) |
| 2 | **데이터 미제공/부분** | HS `1507`(4단위)·월별·전체 파트너 조합은 preview 500건 상한에 쉽게 도달 → **연도별 truncation**. 일부 국가·월은 Comtrade에 미보고(0건) | `maxRecords=500` (L333) |
| 3 | 배치 과다 | 한 호출에 12개월 period를 한꺼번에 요청 → 응답 대형화 → 상한 조기 도달 | `period_str=",".join(12개월)` (L322) |
| 4 | 키 전달 방식 | `getFinalData`는 `subscription_key` kwarg 필요 — 등록만 하고 env 미주입 시 preview로 폴백(무료 경로) | L338-339 |

---

## 2. 해결안 (코드 수정 — 승인 후 적용)

1. **배치 축소**: 12개월 일괄 → **분기(3개월) 또는 월 단위** 호출로 상한 회피.
2. **429 처리**: `break` → **지수 백오프 재시도**(data_pipeline.md 규정) 후 다음 연도 진행(전체 중단 금지).
3. **파트너 집계**: `partnerCode=0`(World 합계) 우선 수집 → 레코드 급감. 국가별은 별도 저빈도 호출.
4. **키 검증 로그**: 시작 시 `getFinalData` 경로 여부·잔여 한도 명시 출력.
5. **HS 세분**: `1507`(4단위) + 필요 시 `150710/150790`(6단위)로 명확화.

---

## 3. 무료 / 유료 대안 정리 (C-02 · C-04 · P1-04)

### 3.1 무료
| 소스 | 접근 | 커버리지 | 한계 | 권장 |
|---|---|---|---|---|
| **UN Comtrade (free 등록키)** | comtradeapicall getFinalData | 전세계 월별 HS | 일일 한도·소량 | ★★☆ 배치축소+백오프 시 사용 가능 |
| **UN Comtrade preview** | previewFinalData | 동일 | **500건/호출** | ★☆☆ 탐색용만 |
| **World Bank WITS** | wits.worldbank.org API | 연간 중심 HS6 | 월별 약함·지연 | ★★☆ 연간 교차검증 |
| **한국 관세청 (data.go.kr)** | 등록 서비스키 | **한국 수입 월별 HS10** | 국내 전용(한국 관점엔 최적) | ★★★ **1차 소스** |
| **KOSIS / TRASS** | 공개 통계 | 한국 무역 | 갱신 지연 | ★★☆ 보완 |

### 3.2 유료
| 소스 | 비용 | 강점 | 권장 |
|---|---|---|---|
| **UN Comtrade Premium** | 구독 | 높은 일일 한도·벌크 다운로드 | ★★★ 9개년 벌크 필요 시 |
| **Trading Economics** | 구독 | 정제·API 안정 | ★★☆ (기수집 히스토리 활용) |
| **IHS/S&P Global GTA** | 고가 | 세계 무역 표준 | ★☆☆ 엔터프라이즈 |
| **CEIC / Panjiva** | 고가 | 선적 단위 | ☆ |

### 3.3 권고 (C-01 종합)
- **1차**: 한국 관세청(data.go.kr) — 한국 수입 관점에 가장 정확·무료·월별 HS10. `customs_connector`
  주 경로로 승격, Comtrade는 **글로벌 교차검증 보조**로 강등.
- **글로벌 백필**: UN Comtrade free 등록키 + 배치축소·백오프·World집계로 9개년 확보 시도 → 실패 시
  WITS 연간으로 폴백.
- **유료**는 관세청+Comtrade free로 커버 안 되는 구간이 확인될 때만 Premium 도입.

---

## 4. 확정 요청
1. Comtrade 코드 수정(배치축소·백오프·World집계) 적용 승인.
2. 관세청(data.go.kr)을 수입통계 **1차 소스로 승격** 승인(Comtrade는 보조).
3. free 경로로 9개년 미확보 시 **WITS 연간 폴백** vs **Comtrade Premium 유료** 중 방향.
