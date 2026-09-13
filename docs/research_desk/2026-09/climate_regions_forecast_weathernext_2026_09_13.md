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

## §2 산지 표 (23행) — 2026-09-13 tier2 좌표·생산 근거 검증 반영

tier1 근거: 승인자 공유 정본 좌표 표 `docs/research_desk/_reference/soybean_oil_production_climate.md` §3.2
(NASA POWER 업로드본 좌표와 일치). tier2 근거: 승인자 요청에 따라 주(州) 중심 근사 좌표를 **주산 벨트 중심**으로
교정하고, 생산 비중·순위를 공식 통계로 확인했다(§2.1). 좌표 라벨 CONFIRMED = 공식·통계 출처의 생산 근거 **와**
gazetteer 기준점 좌표가 모두 확보된 항목. 단일 원천은 `config/production_regions.yaml`(anchor · share_note ·
source_url · verified_on 필드 추가).

| 코드 | 한글명 | 국가 | 작물 | 위도 | 경도 | 기준점(주산 벨트) | 생산 비중·순위(연도·출처) | 좌표 라벨 | 비고 |
|---|---|---|---|---|---|---|---|---|---|
| CN_Heilongjiang | 헤이룽장 | 중국 | 대두 | 48.0 | 128.0 | 정본 §3.2 | 중국 최대 국내 대두 재배 지역(정본) | CONFIRMED | tier1 · grow |
| CN_Shandong | 산둥 | 중국 | 대두 | 36.5 | 118.0 | 정본 §3.2 | 연안 최대 압착 클러스터(정본) | CONFIRMED | tier1 · crush |
| CN_Jiangsu | 장쑤 | 중국 | 대두 | 32.5 | 120.0 | 정본 §3.2 | 양쯔강 압착 허브(정본) | CONFIRMED | tier1 · crush |
| US_Illinois | 일리노이 | 미국 | 대두 | 40.0 | -89.0 | 정본 §3.2 | 미국 생산 1위 주(정본) | CONFIRMED | tier1 · grow_crush |
| US_Iowa | 아이오와 | 미국 | 대두 | 42.0 | -93.5 | 정본 §3.2 | 미국 압착 설비 1위 주(정본) | CONFIRMED | tier1 · grow_crush |
| US_Indiana | 인디애나 | 미국 | 대두 | 40.2 | -86.1 | 정본 §3.2 | 미국 생산 3위 주(정본) | CONFIRMED | tier1 · grow |
| BR_MatoGrosso | 마투그로수 | 브라질 | 대두 | -13.0 | -56.0 | 정본 §3.2 | 브라질 생산 1위 주(정본) | CONFIRMED | tier1 · grow_crush |
| BR_Parana | 파라나 | 브라질 | 대두 | -24.5 | -51.5 | 정본 §3.2 | 브라질 주요 유지 가공 주(정본) | CONFIRMED | tier1 · grow_crush |
| BR_MatoGrossodoSul | 마투그로수두술 | 브라질 | 대두 | -20.0 | -54.5 | 정본 §3.2 | 생산 비중 확대 중(정본) | CONFIRMED | tier1 · grow |
| AR_Cordoba | 코르도바 | 아르헨티나 | 대두 | -31.4 | -64.2 | 정본 §3.2 | 아르헨티나 재배 1위 주(정본) | CONFIRMED | tier1 · grow |
| AR_SantaFe | 산타페 | 아르헨티나 | 대두 | -33.0 | -60.6 | 정본 §3.2 | 로사리오 압착 허브(전국 설비 약 80%, 정본) | CONFIRMED | tier1 · crush |
| AR_BuenosAires | 부에노스아이레스 | 아르헨티나 | 대두 | -36.0 | -60.0 | 정본 §3.2 | 팜파스 핵심 재배 지역(정본) | CONFIRMED | tier1 · grow |
| BR_RioGrandedoSul | 히우그란지두술 | 브라질 | 대두 | -28.7 | -53.3 | Cruz Alta(-28.64/-53.61)·Tupanciretã(-29.08/-53.84)·Passo Fundo(-28.25/-52.40) 북서 고원 벨트 | 생산 4위 주 · 약 18.6백만 t(전국 171.5백만 t의 약 11%) — CONAB 2024/25 12차 조사(단수 2,342 kg/ha 전국 최저 — 가뭄) | CONFIRMED | 구 -30.0/-53.0 → 북으로 1.3°(NASA 격자 2칸 이동) · Embrapa 50년 가뭄 손실 최대 지역 |
| BR_Goias | 고이아스 | 브라질 | 대두 | -17.8 | -51.0 | Rio Verde(-17.75/-50.92)·Jataí 남서 세하두 벨트 | 생산 3위 주 · 약 20.4백만 t(전국의 약 12%) — CONAB 2024/25(단수 4,183 kg/ha 전국 최고) · 생산액 상위 Rio Verde·Jataí·Cristalina(IBGE PAM) | CONFIRMED | 구 -16.5/-49.5 → 남서로 1.3°/1.5°(NASA 격자 이동) |
| US_Minnesota | 미네소타 | 미국 | 대두 | 44.1 | -94.6 | Mankato(44.16/-94.01) 남중부 — 상위 카운티 Redwood·Renville·Blue Earth·Jackson | 생산 3위 주 · 349.4백만 bu(전국 4,366백만 bu의 8.0%) — USDA NASS 2024 Crop Production Summary | CONFIRMED | 구 44.5/-94.5 → 남으로 0.4°(NASA 격자 경계 근접 — 이동 유효) |
| US_Nebraska | 네브래스카 | 미국 | 대두 | 41.1 | -97.3 | York(40.87/-97.59) 동부·남동부 — Saunders·York·Fillmore·Platte | 생산 5위 주 · 301.0백만 bu(전국의 6.9%, 단수 57.5 bu/ac 기록) — USDA NASS 네브래스카 2024 연간 요약 | CONFIRMED | 구 41.0/-98.0 → 동으로 0.7° · 관개 비중 높음 |
| US_Ohio | 오하이오 | 미국 | 대두 | 40.8 | -84.0 | Celina(Mercer, 40.56/-84.56) — Wood·Darke·Seneca 서부·북서부 벨트 | 생산 6위 주 · 274.3백만 bu(전국의 6.3%) — USDA NASS 2024 · 상위 카운티 Wood 9.67·Darke 8.75·Seneca 7.81백만 bu | CONFIRMED | 구 40.3/-83.0 → 북서로 0.5°/1.0°(NASA 격자 이동) |
| PY_AltoParana | 알토파라나(파라과이) | 파라과이 | 대두 | -25.9 | -55.0 | Santa Rita(-25.98/-54.95)·Naranjal — 시우다드델에스테 서쪽 벨트 | 생산 1위 도 · 3.06백만 t(전국 9.34백만 t의 32.7%) — MAG·INBIO 2024/25 · 파종 면적 896천 ha(26.3%) — CAPECO 2025/26 | CONFIRMED | 구 -25.5/-55.0 → 남으로 0.4° |
| IN_MadhyaPradesh | 마디아프라데시(인도) | 인도 | 대두 | 23.0 | 75.8 | Ujjain(23.18/75.78)·Indore(22.72/75.86) 말와 고원 벨트 | 생산 1위 주 · 55.4 lakh t(전국 125.8 lakh t의 약 44%) — SOPA kharif 2024 | CONFIRMED | 구 23.0/77.0 → 서로 1.2°(NASA 격자 2칸 이동) · 수입 관세 정책 연계 |
| MY_Sabah | 사바(말레이시아) | 말레이시아 | 팜 | 5.0 | 118.0 | Lahad Datu(5.03/118.34)·Tawau(4.26/117.89) 동해안 벨트 | CPO 생산 1위 주 · 4.27백만 t(전국 19.34백만 t의 22.1%) — MPIC 국회 서면답변·MPOB 2024 · 식재 약 1.48백만 ha(26.4%) — MPOB Planted Area 2024 | CONFIRMED | 구 5.5/117.5 → 남동으로 0.5°/0.5° · 동해안 6개 지구가 주 생산의 약 75% |
| MY_Johor | 조호르 | 말레이시아 | 팜 | 1.9 | 103.6 | Kluang(2.03/103.32)·Kota Tinggi(1.73/103.90) 중부·남동부 벨트 | 반도 식재 면적 1위 주 · 659,820 ha(전국의 11.8%) — MPOB Oil Palm Planted Area 2024 | CONFIRMED | 구 2.0/103.5와 0.1° 차 — NASA POWER 0.5° 격자에서 동일(사실상 유지) |
| ID_Riau | 리아우(인도네시아) | 인도네시아 | 팜 | 0.5 | 101.5 | Pekanbaru 권역 — Pangkalan Kerinci(0.40/101.86) 동측·Kampar·Rokan Hulu 서측의 중간 | 팜유 생산 1위 주 · 8.79백만 t(전국 46.99백만 t의 18.7%) — BPS 2023 · 군별 상위 Rokan Hulu·Pelalawan·Kampar·Rokan Hilir | CONFIRMED | **기존 좌표 유지** — 주산 군이 Pekanbaru 동서 양측에 분포해 주 중심이 벨트 중심과 일치 |
| ID_CentralKalimantan | 중부칼리만탄 | 인도네시아 | 팜 | -2.5 | 112.8 | Sampit(Kotawaringin Timur, -2.53/112.95)·Seruyan 남부 벨트 | 팜유 생산 2위 주 · 8.55백만 t(전국의 18.2%) — BPS 2023 · Kotawaringin Timur가 주 생산의 26.7%(1위)·Seruyan 2위 | CONFIRMED | 구 -2.0/113.5 → 남서로 0.5°/0.7°(NASA 격자 이동) · MY·ID 합산 세계 팜유 80%+(Zhang 2025) |

### §2.1 검증 방법·조회일

- **조회일**: 2026-09-13. 샌드박스가 원문 도메인 대부분(CONAB·NASS·MPOB·BPS·Wikipedia 등)의 직접 열람을 차단하므로
  검색 색인 요약 경유로 수치를 확보했다(A-200·A-209 동일 경로). 원문 URL은 설정 파일 `source_url`에 보존 — 승인자
  사내망 열람으로 재대조 가능.
- **생산 근거(공식·통계 출처)**: 브라질 CONAB 2024/25 12차 조사(e-book) + CONAB 인용 보도(InfoMoney·Agência Cora
  GO) · IBGE PAM(시군 생산액) / 미국 USDA NASS 2024 Crop Production Summary(2025-01-10) + 네브래스카 연간 요약
  (2025-01-23) + 오하이오 Ag Across Ohio 카운티 추정 / 파라과이 MAG·INBIO 2024/25 수확 보고 + CAPECO 2025/26
  파종 면적 / 인도 SOPA kharif 2024 주별 통계 / 말레이시아 MPOB Oil Palm Planted Area 2024 + MPIC 국회 서면답변
  (Sabah CPO 4.27백만 t) / 인도네시아 BPS 2023 주별 생산(Produksi Tanaman Perkebunan) + Kalteng BPS 2024 군별.
- **좌표 검증**: 행정 중심(주 중심)이 아닌 **주산 벨트 중심**을 채택. 벨트 기준 도시의 위·경도를 gazetteer(Wikipedia
  좌표 — 검색 색인 경유)로 확인한 뒤 기준점 2~3개의 산술 중심을 0.1° 단위로 반올림. 기준점이 하나뿐인 지역(Rio Verde·
  Mankato·York·Celina·Santa Rita)은 카운티·군 분포 방향으로 0.1~0.3° 보정.
- **격자 감도**: Open-Meteo ERA5-Land 0.1° · NASA POWER 0.5°. 0.25° 미만 이동은 NASA POWER 격자에서 무의미
  (조호르 0.1° 차 · 리아우 유지). 0.5° 이상 이동 8건(RS·GO·MN·NE·OH·MP·Sabah·Kalteng)은 NASA POWER 격자 자체가 바뀌므로
  **다음 아카이브 백필부터 신좌표 적용 — 구좌표 수집분과 시계열을 잇지 않는다**(코드 동일·좌표 상이 = vintage 분리,
  `source_vintage`에 좌표 버전 2026-09-13 기록 권장).
- **라벨 규칙**: CONFIRMED = (a) 공식·통계 출처 생산 근거 + (b) gazetteer 기준점 좌표 양쪽 확보. 한쪽이라도 없으면
  INFERENCE(사유 명기). DATA GAP = 근거 미확보. 11건 전부 (a)(b) 충족 → CONFIRMED.

### §2.2 승인자 확인 요청 잔여(INFERENCE 항목)

INFERENCE 라벨 잔여 **0건**. 다만 다음 3건은 CONFIRMED 안에서 승인자 재대조를 권장한다.

| 항목 | 내용 | 요청 |
|---|---|---|
| 브라질 주별 톤수 | RS 18.6·GO 20.4백만 t는 CONAB 조사 회차별 보도 인용(12차 최종 e-book 원표 미열람). 순위(GO 3위·RS 4위)는 3개 출처 일치 | e-book 12차 주별 표 사내망 열람 후 톤수 확정 |
| 미국 NE·OH 순위 | 일부 재보도가 NE 266.8백만 bu(구 추정치)로 OH를 5위로 표기 — NASS 최종(NE 301.0)으로 NE 5위·OH 6위 채택 | NASS Crop Production 2024 Summary 원표 대조 |
| 정본 좌표 표 §3.2 증보 | tier2 11행을 정본 표에 같은 형식으로 추가해야 tier1과 동일한 승인 지위 | 승인자 승인 시 tier2 → 정본 편입 · 토양 hourly 승격 여부 결정 |

팜 산지 편입 근거: 대두유−팜유 가격 전이(CE-015 — 2020 이후 공행성 붕괴, 레짐 인지 하에서만 해석)의
배경으로 팜 산지 기후는 팜유 수급 경로의 선행 신호다. 다만 팜 기후 변수는 대두유 가격의 직접 동인이 아니라
스프레드 레짐 판별의 보조 입력으로만 두며, 피처화는 5단계 게이트(D-014)를 거친다.

**최종 결정자 확인 요청**: tier2 11지점은 본 검증으로 CONFIRMED 라벨을 얻었으나 정본 좌표 표 §3.2 편입은 승인
사항이다. 편입 전까지 tier2는 수집·적재는 하되 **모델 투입 후보에서 제외**하며, 편입 후 토양 hourly 수집을 tier1과
동일하게 승격할지 함께 결정한다.

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
