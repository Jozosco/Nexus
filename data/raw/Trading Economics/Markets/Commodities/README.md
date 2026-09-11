# Trading Economics — Markets / Commodities (2010~ 히스토리 · API 증분 갱신)

Trading Economics 상품 시세 히스토리. **수동 업로드본(2010-01-01~2026-09-10)** 을 기준선으로 두고,
그 이후 일자는 **API 스냅샷으로 매일 1행씩 같은 형식에 append** 한다(A-248·A-250).

## 수집 범위 (26 파일)

| 폴더 | 품목 | 대두유 분석 역할 |
|---|---|---|
| `Agricultural/` (8) | Soybeans·Corn·Wheat(CBOT) · Palm Oil(MYR/MT) · Canola(ICE) · Rapeseed(Euronext) · Sunflower Oil(INR/10kg) · Sugar(ICE) | 대체재 유지류 스프레드 · 보완재(대두) 압착 마진 · 곡물 동조화 |
| `Energy/` (10) | Brent·WTI · Coal · Natural Gas(US/EU TTF/UK NBP) · Gasoline · Heating Oil · Naphtha · Ethanol | 바이오디젤 채널 · 운임 원가(벙커유) · 에탄올→옥수수유 부산물 |
| `Industrial/` (2) | Urea · Di-ammonium(DAP) | 비료 원가 → 작황 비용(보조) |
| `Shipping Indices/` (6) | BDI · Containerized Freight Index · Drewry WCI · CRB Index · GSCI · EU Carbon Permits | 해상 운임 충격 → CIF 원가 · 상품 지수·탄소 비용 |

## 파일 형식 (수동본·API 갱신분 동일)

- 파일명: `YYYY~YYYY_{Commodity}_{Exchange}_{Units}.xlsx` — 파일명의 시작 연도는 원본 그대로 두고 갱신하지 않음
- 시트명: `YYYY년` (연도별) · 컬럼: `Month | Day | Open | High | Low | Close` (헤더 1행)
- 정렬: 대부분 오름차순, Urea 등 일부 내림차순 — 파서(`scripts/ingest_te_xlsx.py`)와 갱신기 모두 방향 자동 판별
- 단위: 거래소 원단위 유지 — USD/MT 환산은 `scripts/normalize_te_units.py`(D8, 직전 월 FRED 환율)

## 일별 API 갱신(스냅샷)

- **언제**: 평일 21:30 UTC(= KST 06:30) 자동 실행 — 미국 장 마감 이후, 일별 파이프라인(22:52 UTC) 이전.
  워크플로우 `.github/workflows/te_xlsx_update.yml`, 모드 기본값 `snapshot`.
- **무엇을 쓰는가**: 파일별로 심볼을 찾아 `/markets/symbol/{심볼}` 스냅샷 1건을 받고, 그 중 **첫 레코드**만
  사용해 해당 연도 시트에 1행을 덧붙인다.
  - `Close` ← 응답 `Last`(응답의 `Close`는 전일 종가일 수 있어 후순위 폴백)
  - `Open`/`High`/`Low` ← `Open`/`DayHigh`/`DayLow`(없으면 `High`/`Low`, 그래도 없으면 공란)
  - 하위 파서(`scripts/ingest_te_xlsx.py`)는 `Close`만 값으로 쓰므로 O/H/L 공란은 무해하다.
- **게이트**(하나라도 걸리면 파일을 건드리지 않고 보고서에만 기록)
  1. 일자가 파일의 마지막 일자보다 **커야** 함(같으면 `최신`) · **오늘 이하** · **평일(월~금)**
  2. 기존 마지막 종가 대비 변동률 **±30% 이하**(`MAX_JUMP` — 계약·집계 혼입 차단, A-249)
  3. 임시 사본에 append → 재판독 검증(시트 수 유지·마지막 일자 진전) 통과 시에만 원본 교체
  4. 409/429·"slow down" 응답이면 **남은 파일 호출을 즉시 중단**(상태 `스로틀 — 중단`, 비치명).
     다음 회차에서 이어서 갱신된다.
- **보고서**: `reports/market/te_api_update_{날짜}.md` — 파일·품목·`모드`·갱신 전 마지막 일자·심볼·상태·추가 행.
  상태는 `갱신(+1행)` / `최신` / `스냅샷 응답 없음` / `필드 없음(컬럼 …)` / `점프 …% — 미갱신` /
  `스로틀 — 중단` 등. `필드 없음`이면 실제 응답 컬럼 목록이 로그·보고서에 남으므로 필드 매핑을 교정한다.
- **공백 복구**: 며칠이 빠졌다면 Actions → Run workflow → `mode = historical`(필요 시 `only`로 품목 한정).
  창 조회 경로이며 밀도(영업일 대비 ≥60%)·점프 게이트가 함께 걸린다. 응답이 월별 표본이면 `밀도 부족`으로
  거부된다(A-249 실측).
- **원칙**: 수동 업로드본이 여전히 기준선이다. API는 **파일 안에 행을 덧붙일 뿐**이며, 파서·분석의 단일
  출처는 어디까지나 이 xlsx 파일들이다(별도 API 계열을 만들지 않는다).

## 갱신 절차 (공통)

1. 스크립트 `scripts/update_te_xlsx_from_api.py`가 파일별 마지막 일자를 읽어 그 이후만 요청
2. 심볼은 자기발견(`/markets/search` → `:COM`/`:IND` 우선) + 레지스트리 고정 심볼 폴백, 호출 간 0.5초 간격
3. 임시 사본에 append → 재판독 검증 통과 시에만 원본 교체 → parquet 재생성(`ingest_te_xlsx.py`)
4. 결과를 보고서에 기록하고 `nexus-daily-bot`이 xlsx·보고서를 커밋
5. **409/403 = 구독 플랜에 Markets Historical 미포함** — 파일은 손대지 않고 보고서에 표시(플랜 상향 여부는
   최종 결정자 판단). 일별 경로는 이 제약과 무관한 스냅샷을 쓴다.

## 이력

- 2026-07-01: 수동 업로드본(연도 시트) 26파일 — 기준선(A-061)
- 2026-09-10: 승인자 수동 갱신 26파일(2026-09-10까지) — 새 기준선
- 2026-09-07: API 증분 갱신 체계 도입(A-248). **첫 실행 실측**: historical 응답이 2개월 창에 4~5행(월별 표본·당일 일자 스탬프 의심)+비현실적 점프 → 갱신분 전량 되돌림, 밀도(≥60% 영업일)·점프(≤30%) 게이트 추가(A-249). 일별 관측 확보 여부는 TE 지원 문의·엔드포인트 파라미터 확인 후 재실행(DQ-21) · Industrial·CRB·GSCI·탄소·Drewry·Corn·Sugar·Wheat·Ethanol·Naphtha·Heating Oil 범위 명시
- 2026-09-11: 일별 스냅샷 갱신 체계 도입(A-250). `/markets/symbol` 스냅샷 1행 append를 기본 모드로 두고
  historical은 공백 복구 전용으로 강등. 평일 21:30 UTC 스케줄 신설. 첫 실전 실행에서 응답 필드
  (`DateTime`·`Last`·`Open`/`DayHigh`/`DayLow`) 실재 여부를 보고서로 확인해야 함
