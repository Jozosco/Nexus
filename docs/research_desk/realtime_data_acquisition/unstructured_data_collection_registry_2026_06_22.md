# 비정형 데이터 수집 레지스트리 — 소스·수집 범위·실시간 메커니즘

**작성일**: 2026-06-22  
**의제**: 현재 수집 중인 **비정형 데이터의 소스 · 수집 범위(발행일 포함) · 실시간(일별) 기사·리포트
수집 방식**을 정리.  
**참여**: C-02(시장조사) · C-03(데이터 파이프라인) · P1-01 · P1-02 · P1-03 · P1-04  
**참조**: `unstructured_data_geopolitical_panel_2026_06_18.md`,
`keywords_geopolitical_biodiesel_sources.md`, `.github/workflows/external_data_refresh.yml`

---

## 0. 핵심 요약

| 구분 | 소스 | 수집 방식 | 발행/수집 범위 | 적시성 |
|---|---|---|---|---|
| 실시간 뉴스 | Perplexity `sonar` | LLM 웹검색 + 인용 | 최근 30~60일 롤링 | 일별(평일 05:30 KST) |
| 지정학 지수 | Caldara & Iacoviello GPR | 공개 xlsx 다운로드 | 1985~현재(월별) | 월별 |
| 해상 위험 | AISstream.io | WebSocket AIS | 실시간 선박 위치 | 일별 스냅샷 |
| 지질·기상·화재 | USGS·NOAA·GDELT·FIRMS | 공개 REST API | 실시간~일별 | 일별 |
| 정책 보고서(PDF) | USDA FAS GAIN | 수동 업로드 후 판독 | 2017.01~2026.06 | 수시(수동) |
| 식용유 시장(PDF) | FAO AMIS | 수동 업로드 후 판독 | 분기 | 분기 |

---

## 1. 실시간(일별) 기사·리포트 수집 메커니즘 (요청 2번 핵심)

### 1.1 스케줄 — `external_data_refresh.yml`
```
on:
  schedule:
    - cron: "30 20 * * 0-4"   # 20:30 UTC, 일~목 → 05:30 KST 월~금 (한국 장 시작 전)
```
- **자동 실행**: 매주 **월~금 오전 05:30 KST**, 전체 커넥터 일괄 수집(`github.event_name == 'schedule'`).
- **수동 실행**: `workflow_dispatch` 로 특정 커넥터만 재실행 가능(기본값 `all`).
- 주말(금·토 발) 미수집 — CBOT·거시 지표가 주말 휴장이라 의도적 제외(C-03).

### 1.2 실시간 뉴스 수집 엔진 — Perplexity `sonar`
- **위치**: `src/pipeline/connectors/gpr_connector.py` (`_fetch_policy_news_proxy`, Hormuz, GPR 실시간)
- **방식**: Perplexity API(OpenAI 호환 엔드포인트 `https://api.perplexity.ai`)에 **구조화 프롬프트**를
  보내 LLM이 **실시간 웹을 검색 → 출처 인용과 함께 요약**. 모델명은 `PERPLEXITY_MODEL` 상수로 관리
  (하드코딩 금지 — MEMORY L-006/L-007).
- **출력 강제 포맷**: 각 쿼리가 `RATE/CHANGE/DATE/SOURCE` 등 **고정 필드**를 요구해 파싱 가능한
  반정형 레코드로 변환 → `indicator_code` + `value` + `price_date(today)` + `ingested_at`.

### 1.3 수집 중인 실시간 뉴스 지표 5종
| indicator_code | 검색 대상 | 롤링 윈도우 | P1 |
|---|---|---|---|
| `GPR_REALTIME` | 글로벌 지정학 위험(오늘) | 당일 | P1-02 |
| `HORMUZ_THREAT_LEVEL` | 호르무즈 해협 위협 수위 | 당일 | P1-02 |
| `ARG_EXPORT_TAX_NEWS` | 아르헨티나 대두유 수출세 동향 | 최근 30일 | P1-01 |
| `INDIA_DUTY_NEWS` | 인도 정제대두유(HS 1507.90) 수입관세 | 최근 60일 | P1-01 |
| `BIODIESEL_MANDATE_NEWS` | 인니·말레이 바이오디젤 의무혼합 | 최근 60일 | P1-04 |
| `WASDE_CONSENSUS_SCORE` | WASDE 발표 컨센서스 vs 실제 서프라이즈 | 발표 주기 | P1-01 |

> **발행일(publication date) 처리**: 각 쿼리가 `DATE: [latest change date]` 필드를 강제하므로
> 뉴스의 **사건 발생일**을 응답에서 추출. `price_date` 는 수집 당일, `DATE` 필드는 별도 사건일로
> 저장해 **선행성 분석(이벤트→가격 시차)** 에 활용. (P1-02 요청 반영)

### 1.4 한계 (C-03)
- Perplexity 실시간 쿼리는 **BACKFILL_MODE=true 시 자동 건너뜀** — 과거 특정일 재현 불가(오늘만).
- 따라서 역사적 비정형 신호는 **GPR xlsx(월별, 1985~)** + **GAIN PDF(2017~)** 로 보완.

---

## 2. 비정형 소스별 상세 레지스트리

### 2.1 Caldara & Iacoviello GPR 지수 (반정형, 역사)
| 항목 | 내용 |
|---|---|
| 소스 | matteoiacoviello.com/gpr.htm (공개 xlsx) |
| 변수 | `GPR_NORMALIZED`, `GPR_HISTORICAL`, `GPR_QUALITATIVE` |
| 수집 범위 | **1985년~현재, 월별** (백필 지원) |
| 권위·적시성 | ★★★ 학술 표준 지정학 위험 지수 / 월 1회 갱신 |
| 비용 | 무료 |

### 2.2 AIS 해협 탱커 모니터 (실시간)
| 항목 | 내용 |
|---|---|
| 소스 | AISstream.io (`AISSTREAM_API_KEY` 등록) |
| 변수 | `SBO_STRAIT_RISK_COMPOSITE`, `HORMUZ_AWRP_MULTIPLIER` |
| 대상 해협 | 호르무즈·말라카·파나마 |
| 수집 범위 | 실시간 선박 위치 → 일별 위험 스냅샷 |
| 적시성 | 일별(실시간 WebSocket) / 백필 불가(실시간 전용) |
| 비용 | 무료 티어 |

### 2.3 GeoIntel 복합 (실시간)
| 항목 | 내용 |
|---|---|
| 소스 | USGS(지진)·NOAA(기상)·GDELT(뉴스 이벤트 DB)·NASA FIRMS(화재) |
| 등록 키 | `NASA_FIRMS_MAP_KEY`, `OPENWEATHERMAP_API_KEY`, `ECMWF_API_KEY` |
| 변수 | `GEOINTEL_RISK_COMPOSITE`, `SEISMIC_*` |
| 수집 범위 | 실시간~일별 |
| 비용 | 무료(공개 REST) |

### 2.4 USDA FAS GAIN 정책 보고서 (PDF, 수동)
| 항목 | 내용 |
|---|---|
| 소스 | fas.usda.gov GAIN (수동 다운로드·업로드) |
| 판독 도구 | `scripts/ingest_gain_pdf.py` (pdfplumber→pypdf) |
| 분류 | `Biofuels/`(280+), `Oilseeds/`(950+) |
| 수집 범위 | **2017.01~2026.06**, 국가·월별 (`YY.MM_Country_Title.pdf`) |
| 신호 태그 | 수출규제·수입관세·바이오연료수요·기상이변·압착·재고·생산변동 |
| 적시성 | 수시(수동 업로드) |
| 비용 | 무료 |

### 2.5 FAO AMIS 식용유 시장 (PDF, 수동)
| 항목 | 내용 |
|---|---|
| 소스 | amis-outlook.org |
| 판독 도구 | `scripts/ingest_fao_amis_pdf.py` |
| 수집 범위 | 분기 식용유 4종(대두·팜·유채·해바라기) 수급 |
| 비용 | 무료 |

---

## 3. 수집 공백 및 보강 권고 (C-02·P1 종합)

| 공백 | 현황 | 권고 |
|---|---|---|
| 흑해/수에즈 항로 차단 역사 | 실시간만, 역사 부재 | GDELT 이벤트 DB 역사 쿼리로 백필 |
| 브라질 작황 뉴스(파종·수확) | 체계적 미수집 | Perplexity 신규 쿼리 `BRAZIL_CROP_NEWS` 추가 |
| 해바라기·유채유 **일별 가격** | 미수집 | FRED 월별(무료) + Perplexity 가격 동향 뉴스 보강 (§ `substitute_complement_oils_acquisition_2026_06_22.md`) |
| 뉴스 **사건일 vs 수집일** 분리 저장 | 부분 | `DATE` 필드 표준화 → 이벤트-가격 시차 분석 정식화 |

---

## 4. 운영 원칙 (going forward)

1. **신규 실시간 쿼리 추가 시** — 이 레지스트리에 indicator_code·검색대상·롤링윈도우·P1 매핑 추가.
2. **모든 비정형 레코드** — `price_date`(수집일)와 사건 `DATE`(발행/발생일)를 분리 저장.
3. **출처 인용 보존** — Perplexity 응답의 `SOURCE` 필드는 폐기하지 말고 레코드에 동반 저장
   (해석가능성 요구 — CLAUDE.md modeling.md).
4. **백필 한계 명시** — 실시간 전용 소스(Perplexity·AIS·GeoIntel)는 과거 재현 불가임을 항상 표기.

---

## 참고

- `external_data_refresh.yml` — 일별 수집 스케줄(평일 05:30 KST)
- `src/pipeline/connectors/gpr_connector.py` — Perplexity 실시간 뉴스 엔진
- `keywords_geopolitical_biodiesel_sources.md` — 검색 키워드·소스 표준 목록
- [Caldara & Iacoviello GPR Index](https://www.matteoiacoviello.com/gpr.htm)

*최종 업데이트: 2026-06-22 · Session 29*
