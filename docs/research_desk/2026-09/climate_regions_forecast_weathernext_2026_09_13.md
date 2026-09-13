# 산지 기후 확장(23지역)·산지 예보 층·WeatherNext 3 판정 — 2026-09-13

> 대상: 기후 커넥터(`src/pipeline/connectors/climate_connector.py`) · 산지 설정(`config/production_regions.yaml`) ·
> as-of 규칙(`src/pipeline/asof.py`) · 스키마(`data/schemas/climate_data.yaml`) · 검증(`tests/test_climate_regions.py`)
> 라벨 규약: CONFIRMED(실측·정본 일치) / INFERENCE(근사·추정) / DATA GAP(미확보)
> 관련 원장 코드는 괄호 병기(A-261 · DQ-25)

---

## §1 요청과 결론 요약

승인자 지시 3건 — ① 산지 기후 수집 범위를 정본 12지역에서 확장, ② 기상 **예보** 층 도입 여부,
③ Google DeepMind **WeatherNext 3** 도입 가능성 판정.

| 항목 | 결론 | 라벨 |
|---|---|---|
| 산지 확장 | 12 → **23지역**. 단일 진실 원천 `config/production_regions.yaml` 신설. tier1 12 = 정본 좌표 표 §3.2와 일치, tier2 11 = 주 중심 근사(승인자 좌표 확인 대기) | tier1 CONFIRMED · tier2 INFERENCE |
| 예보 층 | Open-Meteo 예보 API(무료·키 불필요·15일·`best_match`=ECMWF IFS/AIFS) 로 `FCST_{var}_{region}` 층 **구현 완료**. 참고 전용 — 관측 대체 아님, skill 검증 전 모델 투입 금지 | CONFIRMED(구현) |
| WeatherNext 3 | 모델 **비공개**. 데이터는 Google Cloud 계정 + 데이터 요청 양식(검토 5~7영업일) + 요청자 과금 경로만 존재 → **승인자 결정 사항(DQ-25)**. 코드 변경 없이 대기 | CONFIRMED(접근 조건) |
| 부하 | 런당 호출 약 24 → 약 58. 429 발생 시 `CLIMATE_FORECAST=0` → `CLIMATE_TIER=1` 2단 축소 절차 | INFERENCE(실측은 다음 런) |

부수 정정: 생산 커넥터 `ORIGIN_COORDS` 4지점(일리노이·마투그로수·파라나·산타페)이 기후 커넥터 좌표와
어긋나 있던 것을 정본 좌표 표와 정합. 레거시 OWM 마투그로수 좌표도 동일 정정.

---

## §2 산지 표 (23행)

tier1 근거: 승인자 공유 정본 좌표 표 `docs/research_desk/_reference/soybean_oil_production_climate.md` §3.2
(NASA POWER 업로드본 좌표와 일치). tier2 근거: 주(州) 중심 근사 — 대두 생산 순위·가뭄 손실 지역(Embrapa 50년 정량)·
팜유 집중 산지(MY·ID 합산 세계 80%+, Zhang 2025)를 기준으로 선정.

| 코드 | 한글명 | 국가 | 작물 | 역할 | 위도 | 경도 | tier | 좌표 라벨 | 근거 |
|---|---|---|---|---|---|---|---|---|---|
| CN_Heilongjiang | 헤이룽장 | 중국 | 대두 | grow | 48.0 | 128.0 | 1 | CONFIRMED | 정본 §3.2 — 중국 최대 국내 재배 |
| CN_Shandong | 산둥 | 중국 | 대두 | crush | 36.5 | 118.0 | 1 | CONFIRMED | 정본 §3.2 — 연안 최대 압착 |
| CN_Jiangsu | 장쑤 | 중국 | 대두 | crush | 32.5 | 120.0 | 1 | CONFIRMED | 정본 §3.2 — 양쯔강 압착 허브 |
| US_Illinois | 일리노이 | 미국 | 대두 | grow_crush | 40.0 | -89.0 | 1 | CONFIRMED | 정본 §3.2 — 생산 1위 |
| US_Iowa | 아이오와 | 미국 | 대두 | grow_crush | 42.0 | -93.5 | 1 | CONFIRMED | 정본 §3.2 — 압착 설비 1위 |
| US_Indiana | 인디애나 | 미국 | 대두 | grow | 40.2 | -86.1 | 1 | CONFIRMED | 정본 §3.2 — 생산 3위 |
| BR_MatoGrosso | 마투그로수 | 브라질 | 대두 | grow_crush | -13.0 | -56.0 | 1 | CONFIRMED | 정본 §3.2 — 생산 1위 주 |
| BR_Parana | 파라나 | 브라질 | 대두 | grow_crush | -24.5 | -51.5 | 1 | CONFIRMED | 정본 §3.2 — 주요 유지 가공 |
| BR_MatoGrossodoSul | 마투그로수두술 | 브라질 | 대두 | grow | -20.0 | -54.5 | 1 | CONFIRMED | 정본 §3.2 — 확대 중 |
| AR_Cordoba | 코르도바 | 아르헨티나 | 대두 | grow | -31.4 | -64.2 | 1 | CONFIRMED | 정본 §3.2 — 재배 1위 |
| AR_SantaFe | 산타페 | 아르헨티나 | 대두 | crush | -33.0 | -60.6 | 1 | CONFIRMED | 정본 §3.2 — 로사리오 압착 80% |
| AR_BuenosAires | 부에노스아이레스 | 아르헨티나 | 대두 | grow | -36.0 | -60.0 | 1 | CONFIRMED | 정본 §3.2 — 팜파스 핵심 |
| BR_RioGrandedoSul | 히우그란지두술 | 브라질 | 대두 | grow | -30.0 | -53.0 | 2 | INFERENCE | 브라질 남부 최대 가뭄 손실 지역(Embrapa) — CE-006 지역 분리 해석 |
| BR_Goias | 고이아스 | 브라질 | 대두 | grow | -16.5 | -49.5 | 2 | INFERENCE | 세하두 주요 생산 주 |
| US_Minnesota | 미네소타 | 미국 | 대두 | grow | 44.5 | -94.5 | 2 | INFERENCE | 북부 주요 생산 주 |
| US_Nebraska | 네브래스카 | 미국 | 대두 | grow | 41.0 | -98.0 | 2 | INFERENCE | 관개 비중 높은 서부 코른벨트 |
| US_Ohio | 오하이오 | 미국 | 대두 | grow | 40.3 | -83.0 | 2 | INFERENCE | 동부 코른벨트 |
| PY_AltoParana | 알토파라나(파라과이) | 파라과이 | 대두 | grow | -25.5 | -55.0 | 2 | INFERENCE | 파라과이 최대 생산 지역 |
| IN_MadhyaPradesh | 마디아프라데시(인도) | 인도 | 대두 | grow | 23.0 | 77.0 | 2 | INFERENCE | 인도 대두 1위 주 — 수입 관세 정책 연계 |
| MY_Sabah | 사바(말레이시아) | 말레이시아 | 팜 | grow | 5.5 | 117.5 | 2 | INFERENCE | 말레이시아 팜유 1위 주 |
| MY_Johor | 조호르 | 말레이시아 | 팜 | grow | 2.0 | 103.5 | 2 | INFERENCE | 반도 주요 팜 재배 주 |
| ID_Riau | 리아우(인도네시아) | 인도네시아 | 팜 | grow | 0.5 | 101.5 | 2 | INFERENCE | 인도네시아 팜유 1위 주 |
| ID_CentralKalimantan | 중부칼리만탄 | 인도네시아 | 팜 | grow | -2.0 | 113.5 | 2 | INFERENCE | 칼리만탄 팜 확장 지역 |

팜 산지 편입 근거: 대두유−팜유 가격 전이(CE-015 — 2020 이후 공행성 붕괴, 레짐 인지 하에서만 해석)의
배경으로 팜 산지 기후는 팜유 수급 경로의 선행 신호다. 다만 팜 기후 변수는 대두유 가격의 직접 동인이 아니라
스프레드 레짐 판별의 보조 입력으로만 두며, 피처화는 5단계 게이트(D-014)를 거친다.

**좌표 확인 요청(최종 결정자)**: tier2 11지점의 위·경도는 주 중심 근사이므로 정본 좌표 표 §3.2를 같은 형식으로
증보하는 확인이 필요하다. 확인 전까지 tier2는 수집·적재는 하되 **모델 투입 후보에서 제외**하며, 확인 후
`coord_status`를 CONFIRMED로 바꾸고 토양 hourly 수집을 tier1과 동일하게 승격할지 함께 결정한다.

---

## §3 부하 산정

| 구분 | 현행(12지역) | 신규(23지역) | 산식 |
|---|---|---|---|
| 아카이브 daily | 12 | 23 | 지역당 1회 |
| 아카이브 토양 hourly | 12 | 12 | **tier1만**(tier2 생략 — 값 규모의 약 89%가 토양 hourly라 여기서 부하를 묶음) |
| 변수 프로브 | 1 | 1 | 첫 지역 1회 |
| 예보 | 0 | 23 | 지역당 1회(5변수 일괄) |
| **합계(런당)** | **약 25** | **약 59** | 로그 `[정보] 기후 지역 23개(tier1 12·tier2 11) · 호출 예상 36` + 예보 23 |

값 규모(증분 90일 기준·INFERENCE): 아카이브 tier1 12×(6 daily+2 토양)×90 ≈ 8,640 + tier2 11×6×90 ≈ 5,940 +
예보 23×5×15 = 1,725 → 런당 약 16,300행(현행 약 8,600행의 1.9배). 백필(2010~)은 tier2 daily가 11×6×약 6,100일
≈ 40만 행 추가되나 토양 hourly는 없으므로 요청 크기는 tier1 hourly 1회보다 작다.

429(무료 티어 시간당 한도 — A-110 실증) 발생 시 축소 절차:
1. `CLIMATE_FORECAST=0` — 예보 23호출 제거(참고 층이라 손실 없음)
2. `CLIMATE_TIER=1` — tier2 11호출 제거(정본 12지역만 · 구 부하로 복귀)
3. 그래도 반복되면 `CLIMATE_INCREMENTAL_DAYS` 축소(기본 90) — 값 규모 감소
실행 표면·시크릿 등 인프라 상세는 이 문서에 두지 않는다.

---

## §4 예보 층 설계

| 요소 | 설계 |
|---|---|
| 원천 | Open-Meteo forecast API · `models=best_match`(ECMWF IFS/AIFS 0.25°, AIFS AI 모델 포함) · `timezone=UTC` · `forecast_days=15` |
| 변수 | temperature_2m_max · temperature_2m_min · precipitation_sum · shortwave_radiation_sum · et0_fao_evapotranspiration (예보 daily는 토양·일조 미제공) |
| 코드 규약 | `FCST_{var}_{CC}_{Region}` — 아카이브 `{var}_{CC}_{Region}`과 접두사로 분리(mart 값충돌·D-033 게이트와 무관하게 공존) |
| 행 | price_date = 유효일(미래) · note = `issue_date=YYYY-MM-DD lead_days=n` · source_vintage = 발행일 |
| as-of | `RELEASE_RULES["FCST_"]` = immediate·lag 0·revises True. `attach_asof`의 전망 행 분기(event_time > ingested_at → available_at = ingested_at, A-195)로 **available_at = 수집 시각** — 합성 검증: 유효일 9/20 행이 available_at 9/13 13:07(수집 시각)·vintage_known True |
| vintage | `REVISION_HISTORY["FCST_"] = "full"` — 같은 유효일이 매일 재예보되므로 발행 회차별 행을 전부 보존(덮어쓰기 금지). 백테스트는 "available_at ≤ t 중 최신 vintage" 규칙이 그대로 적용 |
| 실행 | 일별 런에서만 수집(백필은 예보 개념이 없어 건너뜀) · `CLIMATE_FORECAST=0`으로 비활성 · 지역 단위 비치명 |

활용 원칙(전 에이전트 공통):
- 예보는 **관측 대체가 아니다** — 아카이브 계열의 최근 6일 결손(ERA5-Land 지연)을 예보로 메우지 않는다.
- **검증 전 모델 투입 금지** — 예보 이력을 30일 이상 축적한 뒤 유효일별 관측(아카이브)과 대조해 리드일수별
  skill(MAE·bias·강수 hit rate)을 산출하고, persistence 기준선을 이겨야 피처 후보가 된다(기준선 독트린 정합).
- 브리프에서는 "향후 15일 산지 기상 전망(ECMWF 기반·참고)" 블록으로만 노출하며 가격 전망 문장과 결합하지 않는다(A-191).

---

## §5 WeatherNext 3 판정표

| 항목 | 사실 | 라벨 | 함의 |
|---|---|---|---|
| 모델 공개 여부 | WeatherNext 3(2026-09-03 발표) — 시간별 5 km · 15일 확률 예보 · 앙상블 64멤버. **모델 가중치·코드 비공개** | CONFIRMED | 자체 실행 불가 — 데이터 구독 경로만 검토 대상 |
| 데이터 접근 | BigQuery · Earth Engine · Cloud Storage 경유. **Google Cloud 계정 + WeatherNext Data Request 양식** 필요, 검토 5~7영업일(수시) | CONFIRMED | 계정·요청서 = 승인자 결정 사항. 자율 착수 불가 |
| 라이선스 | 이력 데이터(발행 1시간 경과분) CC BY 4.0 · 실시간 데이터는 실험 약관 | CONFIRMED | 실시간 운용은 약관 변경 리스크 — 이력 기반 skill 검증부터 |
| 비용 | **요청자 과금(Requester Pays)** · 전체 앙상블 글로벌 1회 수백 GB · 23지점 시계열 추출은 소규모(BigQuery 스캔 과금은 쿼리 설계에 좌우) | CONFIRMED(구조) · INFERENCE(금액) | 비용 상한을 요청서와 함께 승인자가 확정해야 함 — 금액 추정치는 실측 전 제시하지 않음 |
| egress 신규 필요 | bigquery.googleapis.com · storage.googleapis.com · earthengine.googleapis.com · oauth2.googleapis.com 등 — **등재는 결정 후**(현 v2.7은 Open-Meteo 예보 호스트만) | INFERENCE(호스트 목록) | 결정 없이 선등재하지 않음(A-069 전례는 결정 확정 소스에만 적용) |
| as-of / vintage | 발행 시각(init time)이 곧 available_at · 유효일=event_time · 앙상블 멤버/분위수 축 분리 필요(`FCST_WN3_{var}_{q}_{region}` 형태) | INFERENCE(설계) | 현 `FCST_` 규칙 재사용 가능 — 축 미분리 시 값충돌 게이트(D-033)에 걸림 |
| 정확도 주장 | 공개 벤치마크(ECMWF ENS 대비) 기준의 발표 수치 — **산지·리드일수·변수별 자체 검증 없이는 인용 불가** | INFERENCE | Open-Meteo 예보와 같은 skill 검증 절차를 통과해야 대체·병행 판단 가능 |
| 오픈 대안 | WeatherNext 2 · GraphCast · GenCast — GitHub 공개(코드 Apache 2.0 · 가중치 CC BY 4.0), ERA5 입력, GPU/TPU 필요 | CONFIRMED | Challenger 동결 대상(GPU 표면 배정 전 '미평가') |

출처:
- https://developers.google.com/weathernext/guides/models
- https://developers.google.com/weathernext/guides/osmodel
- https://developers.google.com/weathernext/guides/bigquery
- https://github.com/google-deepmind/weathernext
- https://open-meteo.com/en/docs/ecmwf-api

---

## §6 경로 3단

| 단계 | 내용 | 상태 | 필요 승인 |
|---|---|---|---|
| ① Open-Meteo 예보 | 무료·키 불필요·구현 완료. 다음 일별 런부터 `FCST_` 층 적재, 30일 후 skill 검증 | 즉시 | 없음(egress v2.7 등재 완료) |
| ② WeatherNext 3 데이터 요청 (**DQ-25**) | Google Cloud 계정 개설 · 데이터 요청서 제출 · 비용 상한 확정 → 승인 후 23지점 이력 추출로 skill 비교 | 승인자 결정 대기 | 계정 · 요청서 · 비용 상한 · egress 4~5종 |
| ③ WeatherNext 2 오픈 모델 | 자체 추론(ERA5 입력·GPU) — Challenger로 **동결** | GPU 표면 배정 후 | 컴퓨트 표면 결정(DQ-16 계열) |

①만으로 산지 예보 층의 운용 가치(브리프 전망 블록·경보 선행 신호)는 확보된다. ②는 ①의 skill 검증 결과가
"ECMWF 기반 예보의 리드 8~15일 skill이 부족"으로 나올 때 비로소 비용 대비 근거가 생기므로, 요청서 제출 여부는
30일 검증 후 재상정하는 것이 순서에 맞다(다만 검토 5~7영업일을 감안해 계정 개설만 선행하는 선택지는 열어 둔다).

---

## §7 후속

1. **브리프 예보 블록** — `src/reporting/daily_brief.py`에 "향후 15일 산지 기상 전망" 카드(tier1 12지역 우선 ·
   강수 누계·최고기온 이상·ET₀) 추가. 이번 변경 범위 밖 — 별도 작업으로 등재.
2. **G1 예보 피처 검증 절차** — 30일 축적 후 `scripts/`에 skill 검증기(유효일별 관측 대조·리드일수별 MAE·
   persistence 기준선) 신설 → 통과 변수만 `FCST_` 피처 후보로 5단계 게이트 진입. 검증 전에는 mart 빌드에서
   `FCST_` 접두를 타깃 전용 규칙과 같이 **명시 제외**할지 결정 필요(현재는 적재만 되고 소비 코드 없음).
3. **tier2 좌표 확정** — 승인자 확인 후 `coord_status` 갱신 · 토양 hourly 승격 여부 결정.
4. **워크플로우 의존성** — 기후 잡의 설치 목록에 `pyyaml`이 없어 커넥터는 최소 파서로 폴백한다(동일 결과를
   테스트로 보증). 설치 목록 갱신은 워크플로우 변경 권한이 있는 작업에서 처리.
5. **MEMORY** — 당월 아카이브에 A-261 등재 · decision_queue에 DQ-25 등재.
