# Trading Economics — Markets / Commodities (2010~ 히스토리 · API 증분 갱신)

Trading Economics 상품 시세 히스토리. **수동 업로드본(2010-01-01~2026-07-01)** 을 기준선으로 두고,
2026-09 구독 연장 이후에는 **API로 마지막 일자 이후 행만 같은 형식에 append** 한다(A-248).

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

## 갱신 절차 (API)

1. `.github/workflows/te_xlsx_update.yml` 수동 실행(Actions → Run workflow, `only` 비우면 전체)
   — 스크립트 `scripts/update_te_xlsx_from_api.py`가 파일별 마지막 일자를 읽어 그 이후만 요청
2. 심볼은 자기발견(`/markets/search` → `:COM`/`:IND` 우선) + 레지스트리 고정 심볼 폴백
3. 임시 사본에 append → 재판독 검증(시트 수·마지막 일자 진전) 통과 시에만 원본 교체
4. `reports/market/te_api_update_{날짜}.md`에 파일별 결과(추가 행·심볼·상태) 기록, parquet 재생성
5. **409/403 = 구독 플랜에 Markets Historical 미포함** — 파일은 손대지 않고 보고서에 표시(플랜 상향 또는
   일별 스냅샷 append로 대체 여부는 최종 결정자 판단)

## 이력

- 2026-07-01: 수동 업로드본(연도 시트) 26파일 — 기준선(A-061)
- 2026-09-07: API 증분 갱신 체계 도입(A-248). **첫 실행 실측**: historical 응답이 2개월 창에 4~5행(월별 표본·당일 일자 스탬프 의심)+비현실적 점프 → 갱신분 전량 되돌림, 밀도(≥60% 영업일)·점프(≤30%) 게이트 추가(A-249). 일별 관측 확보 여부는 TE 지원 문의·엔드포인트 파라미터 확인 후 재실행(DQ-21) · Industrial·CRB·GSCI·탄소·Drewry·Corn·Sugar·Wheat·Ethanol·Naphtha·Heating Oil 범위 명시
