# NASA POWER Agromet — 파라미터 선별 (C-03 · P1-01 · P1-03)

**작성일**: 2026-07-10 · **대상**: 작황(Crop/Agroclimatology) 9개년 백필  
**결정 ID**: A-065 · **구현**: `production_connector.py::fetch_nasa_power_agromet`

---

## 1. Single Point 설정 선택 (근거 포함)

| 설정 | 옵션 | **선택** | 근거 |
|---|---|---|---|
| 1. Resolution | Standard / High | **Standard** | High는 **2024년만** 제공 → 9개년(2017~) 히스토리 불가. Standard는 오늘(2026-07-10)까지 |
| 2. Community | Renewable / Buildings / **Agroclimatology** | **Agroclimatology(AG)** | 대두 작황 도메인. 농업 표준 파생변수 정합 |
| 3. Temporal | Hourly/Daily/Monthly/Climatology | **Monthly**(우선) + Daily(권장 확장) | 월별=타 지표(WASDE/PSD/FX 월별) 정합. Daily는 열스트레스일수·연속무강수 등 파생에 추후 확장 |
| 4. Location | Lat/Lon | **6개 원산지 좌표** | 미국 중서부·아르헨티나 팜파스·브라질 마투그로수·(베트남) 등 대두 벨트 |
| 5. Time Extent | ~today (Std) | **2017-01 ~ 현재** | 공통 분석창 |
| 6. Parameters | 다중 | **9종 선별(아래)** | 대두 수율 4대 구동축만 |

> **High Resolution 배제 확정**: 2024년 단일연도만 → 시계열 분석·Granger 인과에 부적합.
> 단, 특정 사건연도(예: 2024 남미 가뭄) 정밀 검증이 필요하면 보조로만 활용.

---

## 2. 파라미터 선별 — 대두 수율 4대 구동축 (P1-01 · P1-03)

대두 수율은 **① 열 · ② 수분 · ③ 일사 · ④ 토양수분**이 결정. 각 축에서 핵심만 선별(과수집 방지):

| 축 | POWER 코드 | 지표 | 대두 영향 |
|---|---|---|---|
| ① 열 | `T2M` · `T2M_MAX` · `T2M_MIN` | 평균·최고·최저기온 | 개화기 >35℃ 열스트레스 → 결협 감소. 최저=냉해 |
| ② 수분 | `PRECTOTCORR` · `RH2M` | 강수·상대습도 | 착협·종실비대기 수분 부족 → 감수. 습도=병해(녹병) |
| ③ 일사 | `ALLSKY_SFC_SW_DWN` · `ALLSKY_SFC_PAR_TOT` | 전천일사·PAR | 광합성 에너지 직접 입력. 흐린 해 감수 |
| ④ 토양수분 | `GWETROOT` · `GWETTOP` | 근권·표층 토양수분 | 가뭄 조기경보(라니냐 남미). ENSO_ONI 보완 |

**제외 파라미터 근거**:
- 풍속/풍향(WS/WD 계열): 대두 수율 직접성 낮음 → 제외(도복·건조 특수사례만).
- UV(UVA/UVB/UV Index): 인체·재생에너지용 → 농업 무관.
- Wet Bulb·Earth Skin·Dew Point: T2M·RH로 대체 가능 → 중복 제외.
- TOA·Clear Sky 일사: All-Sky가 실제 지표면 값 → Clear Sky 제외.

---

## 3. 파생 피처 (C-03 — 백필 후 산출 권장)

| 파생 | 정의 | 신호 |
|---|---|---|
| `GDD_soy_{region}` | Growing Degree Days = Σ max(0, (Tmax+Tmin)/2 − 10℃) | 생육 적산온도 |
| `HEAT_STRESS_DAYS` | T2M_MAX > 35℃ 일수(Daily 확장 시) | 개화기 열해 |
| `DRY_SPELL` | GWETROOT < 0.3 지속 개월 | 가뭄 강도 |
| `RADIATION_ANOM` | 일사 전년동월 대비 편차 | 광부족 감수 |

> 파생은 **Daily 확장 시** 정밀도↑. 현재 Monthly로 GDD·토양수분 이상은 산출 가능.

---

## 4. 구현 반영 (A-065)
- `NASA_POWER_PARAMS` 상수(9종) 신설, `fetch_nasa_power_agromet` 제네릭 루프로 재작성.
- 결측 센티넬(−999) 필터. `indicator_code = {param}_{region}` (예: `T2M_MAX_US_Midwest`).
- community=AG · Standard Monthly · 2017~현재 · 키 불필요(무료).

## 5. 확정 요청
1. Monthly 확정 vs **Daily 확장**(열스트레스일수·연속무강수 파생) 착수 여부.
2. 6개 원산지 좌표 적정성(미국 중서부·아르헨 팜파스·브라질 MT·베트남) 확인.
3. 파생 피처 4종 산출 승인.
