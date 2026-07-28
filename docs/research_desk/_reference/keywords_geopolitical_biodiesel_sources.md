# 비정형 데이터 수집 키워드 및 소스 — 지정학·바이오디젤 정책

**작성일**: 2026-06-22  
**분류**: C-02(시장조사) · P1-02(지정학) · P1-04(공급망)  
**목적**: 대두유 공급·수요·가격에 영향을 미치는 지정학 이벤트 및 바이오연료 정책 뉴스 수집 시
사용하는 표준 키워드와 1차 소스 목록. Perplexity API·GDELT·GeoIntel 쿼리 기반 구성.

---

## §1 지정학 이벤트 키워드

### 1.1 해운·항로 리스크

| 키워드(영문) | 키워드(한국어) | 대두유 영향 경로 | 근거 이벤트 |
|---|---|---|---|
| `Red Sea attack`, `Houthi shipping`, `Bab-el-Mandeb closure` | 홍해 공격, 후티, 밥엘만데브 봉쇄 | 아시아↔유럽 탱커 운임 급등 → 한국 CIF +3~8% | 2023.11~2024 후티 드론·미사일 공격 |
| `Suez Canal disruption`, `Cape of Good Hope reroute` | 수에즈 운하 차단, 희망봉 우회 | 10~14일 항로 연장 → BDI 급등 | 2024.01 탱커 운항 중단 |
| `Strait of Hormuz`, `Iran tanker seizure` | 호르무즈 해협, 이란 유조선 나포 | 벙커유 가격 → 운임 전이 | 2019 이란 제재, 2023 이란 원유 제재 복원 |
| `Black Sea grain corridor`, `Ukraine export ban`, `Odesa port` | 흑해 곡물 협정, 우크라이나 수출 금지, 오데사 항 | 해바라기유 수출 중단 → SBO 대체 수요 급등 | 2022.07 협정, 2023.07 러시아 탈퇴 |
| `Panama Canal drought`, `vessel backlog` | 파나마 운하 가뭄, 선박 적체 | 브라질산 대두 미주→아시아 운송 지연 → FOB/CIF 스프레드 확대 | 2023.09~2024.01 역대급 가뭄 |

### 1.2 무역 정책·관세

| 키워드(영문) | 키워드(한국어) | 대두유 영향 경로 | 근거 이벤트 |
|---|---|---|---|
| `US-China trade war`, `China soybean tariff`, `retaliatory tariff` | 미중 무역전쟁, 중국 대두 관세, 보복 관세 | 중국 미국산 대두 수입 급감 → 브라질·아르헨티나 공급 과점화 | 2018.07 25% 추가 관세; 2025~재개 |
| `Argentina soybean export tax`, `soja retenciones` | 아르헨티나 대두유 수출세, 레텐시오네스 | 수출세 인상 → 수출 감소 → 글로벌 공급 타이트 | 2022.08 수출세 임시 인하(30%→33.5%) |
| `India import duty soybean oil`, `India edible oil tariff` | 인도 대두유 수입 관세 | 관세 인하 → 수입 수요 급증 → 글로벌 SBO 공급 타이트 | 2021.10 관세 인하(→5.5%) |
| `Indonesia CPO export levy`, `Indonesia palm oil ban` | 인도네시아 CPO 수출 레비, 팜유 수출금지 | CPO 공급 감소 → SBO 대체 수요 증가 | 2022.04~05 인도네시아 팜유 수출금지 |
| `EU anti-dumping biodiesel Argentina`, `CVD biodiesel US` | EU 아르헨티나 바이오디젤 반덤핑, 미국산 CVD | 아르헨티나·미국산 SBO 수출 경로 변화 | 2013(EU AD), 2018(재확인), 2021 연장 |
| `US soybean oil tariff`, `Section 301`, `Section 232` | 미국 관세 조치 | 글로벌 무역 흐름 재편 | 2025 트럼프 2기 관세 부과 |

### 1.3 분쟁·지역 불안

| 키워드(영문) | 키워드(한국어) | 대두유 영향 경로 | 근거 이벤트 |
|---|---|---|---|
| `Russia Ukraine war`, `Kyiv offensive`, `Black Sea naval` | 러시아-우크라이나 전쟁 | 해바라기유 공급 충격 → SBO 급등; 에너지 가격 → 비료·운임 상승 | 2022.02.24 개전 |
| `Middle East escalation`, `Israel Iran conflict` | 중동 긴장, 이스라엘-이란 분쟁 | 유가 → 벙커유 → 운임; 호르무즈 위협 | 2024.04 이란 이스라엘 직접 공격 |
| `Brazil political risk`, `Argentina peso crisis` | 브라질 정치 리스크, 아르헨티나 페소 위기 | 수출 정책 불확실성 → 공급 변동성 | 2022 브라질 대선; 2023 아르헨 페소 급락 |

---

## §2 바이오연료 정책 키워드

### 2.1 바이오디젤 혼합 의무 (국가별)

| 국가 | 키워드(영문) | 키워드(한국어) | 현재 정책 수준 | SBO 수요 영향 |
|---|---|---|---|---|
| 인도네시아 | `Indonesia B35`, `B40 mandate`, `biodiesel blend`, `Pertamina` | 인도네시아 B35, B40 혼합의무 | B35(2023.02~), B40 로드맵 | CPO 수요 증가 → SBO 상대가격 하락 방어 |
| 브라질 | `Brazil RenovaBio`, `B15 mandate`, `BNDES biodiesel`, `CNPEM` | 브라질 RenovaBio, B15 | B15(2024~), 증가 예정 | 대두유 바이오디젤 원료 → 국내 소비 증가 |
| EU | `EU RED III`, `REDIII`, `renewable energy directive`, `biofuel mandate` | EU RED III, 재생에너지 지침 | 14% 재생(2030년 목표) | SBO 바이오연료 단계적 축소(2026부터) |
| 미국 | `RVO`, `renewable volume obligation`, `EPA biofuel`, `RFS2` | RVO, 재생연료기준 | 연간 갱신 | SBO→HVO 수요 이동 |
| 인도 | `India ethanol blending`, `EBP`, `E20 target` | 인도 에탄올 혼합, E20 | E10→E20 추진 중 | 사탕수수 에탄올 중심 — SBO 직접 영향 적음 |
| 말레이시아 | `Malaysia B20`, `Malaysia palm biodiesel`, `B30` | 말레이시아 B20, 팜 바이오디젤 | B20(2024), B30 검토 | CPO 소비 증가 → SBO 경쟁 심화 |
| 콜롬비아 | `Colombia E4`, `Colombia biodiesel`, `ethanol blend Colombia` | 콜롬비아 E4, 바이오디젤 | E4~E10 변동 | 지역 영향 한정 |

### 2.2 SAF (지속가능 항공연료)

| 키워드(영문) | 키워드(한국어) | 관련 소스 | SBO 영향 |
|---|---|---|---|
| `SAF mandate`, `sustainable aviation fuel`, `EU SAF blending` | SAF 혼합 의무, 지속가능 항공연료 | ICAO CORSIA, EU ReFuelEU Aviation | SBO→HVO→SAF 경로로 수요 증가(2025~) |
| `HVO`, `hydrotreated vegetable oil`, `renewable diesel` | HVO, 수첨 식물유, 재생디젤 | IEA, IRENA, 각국 에너지부 | SBO 직접 원료 → 운송 부문 수요 증가 |
| `Japan SAF target`, `METI SAF` | 일본 SAF 목표, METI | USDA GAIN Japan 2022~2024 | SBO 원료 비중 증가 검토 중 |
| `Korea K-SAF`, `Korea biofuel` | 한국 K-SAF | 국토부, 산업부 | 2030년 K-SAF 5% 목표 — 원료 대두유 일부 포함 |

### 2.3 기후·기상 정책 (연료 전환 촉진)

| 키워드(영문) | 키워드(한국어) | 관련 소스 | SBO 영향 |
|---|---|---|---|
| `carbon intensity`, `CI score`, `LCFS California` | 탄소집약도, LCFS 캘리포니아 | CARB(캘리포니아 대기자원위원회) | SBO→HVO 경제성 결정 |
| `deforestation-free supply chain`, `EUDR` | 산림 파괴 없는 공급망, EUDR | EU 삼림벌채방지법 | 브라질·아르헨티나산 대두 수출 제약 가능 |
| `land use change`, `ILUC factor` | 간접 토지 이용 변화, ILUC | EU RED III 부속서 | 대두 바이오연료 ILUC 계수 높음 → EU 시장 배제 위험 |

---

## §3 1차 소스 목록

### 3.1 정형 데이터 소스 (API/다운로드)

| 소스 | URL/방법 | 데이터 유형 | 업데이트 주기 | C-03 변수 |
|---|---|---|---|---|
| USDA FAS GAIN | fas.usda.gov/data (검색) | 국가별 농업 정책 보고서 PDF | 수시 | `GAIN_*_SIGNAL` |
| USDA WASDE | usda.gov/oce/commodity (PDF/xlsx) | 월간 수급 전망 | 월 1회 | `WASDE_SBO_*` |
| USDA FAS PSD | apps.fas.usda.gov/psdonline | 공급·수요·무역 연간 전망 | 월 1회 | `PSD_SOY_*` |
| FAO AMIS | amis-outlook.org | 분기 식용유 시장 보고 | 분기 | `FAO_AMIS_SBO_*` |
| Caldara & Iacoviello GPR | matteoiacoviello.com/gpr.htm | 지정학적 위험 지수 (1985~) | 월 1회 | `GPR_NORMALIZED` |
| CBOT BO=F | yfinance (`BO=F`) | 대두유 선물 일별 가격 | 일별 | `CBOT_SBO_FUTURES` |
| FRED DEXBZUS / DEXCHUS | fred.stlouisfed.org | BRL/USD, CNY/USD 환율 | 일별 | `FX_BRL_USD`, `FX_CNY_USD` |
| NOAA CPC ONI | psl.noaa.gov/enso/mei | ENSO Oceanic Niño Index | 주 1회 | `ENSO_ONI` |
| Baltic Exchange BDI | balticexchange.com | 벌크선 운임 지수 | 일별 | `BDI` |
| GDELT Project | gdeltproject.org | 뉴스 이벤트 지정학 데이터베이스 | 15분 | `GEOINTEL_RISK_COMPOSITE` 보조 |
| AISstream.io | aisstream.io | 실시간 선박 AIS | 실시간 | `SBO_STRAIT_RISK_COMPOSITE` |

### 3.2 비정형 모니터링 소스 (Perplexity API 쿼리용)

| 소스 유형 | 예시 미디어 | 권장 쿼리 예시 | P1 역할 |
|---|---|---|---|
| 아르헨티나 농업부 | minagri.gob.ar, InformeAgro | `"Argentina soybean oil export tax 2025"` | P1-01, P1-02 |
| 인도네시아 에너지부 | esdm.go.id, Reuters | `"Indonesia biodiesel B35 palm oil mandate 2024"` | P1-04 |
| EU 집행위원회 | ec.europa.eu, Platts | `"EU RED III soybean biofuel phase-out"` | P1-02 |
| 브라질 농업부 | mapa.gov.br, Bloomberg | `"Brazil soybean crop forecast 2025 USDA"` | P1-03 |
| 중국 농업부 | moa.gov.cn, CNGOIC | `"China soybean import volume 2024 USDA"` | P1-02 |
| 인도 상무부 | commerce.gov.in, Reuters | `"India edible oil import duty 2025"` | P1-01 |
| 해운 뉴스 | Splash247, TradeWinds, Lloyd's List | `"Red Sea Houthi tanker freight rate 2024"` | P1-04 |
| 에너지 뉴스 | ICIS, Argus Media, Platts | `"soybean oil HVO demand Europe 2025"` | P1-01, P1-04 |

---

## §4 수집 우선순위 매트릭스

| 이벤트 유형 | 가격 선행성 | 수집 난이도 | 우선 순위 | 현재 상태 |
|---|---|---|---|---|
| 아르헨티나 수출세 변경 | 1~3주 선행 | 낮음(보도 즉시) | ★★★ | 🟡 Perplexity 간접 |
| 인도네시아 바이오디젤 혼합 의무 상향 | 1~4주 선행 | 낮음 | ★★★ | ✅ GAIN PDF |
| 흑해·수에즈 항로 차단 | 즉시~2주 | 중간(AIS 필요) | ★★★ | ❌ 미수집 |
| 중국 대두 수입 관세 변동 | 2~6주 선행 | 낮음 | ★★★ | 🟡 WASDE 간접 |
| EU RED III 정책 변경 | 3~12개월 선행 | 낮음(공식 문서) | ★★☆ | ✅ GAIN PDF |
| 브라질 작황 뉴스(파종/수확) | 4~8주 선행 | 중간 | ★★★ | 🟡 WASDE 간접 |
| 인도 수입 관세 변동 | 2~4주 선행 | 낮음 | ★★★ | 🟡 GAIN 간접 |
| 호르무즈 해협 긴장 | 즉시~1주 | 높음(AIS 필요) | ★★☆ | 🟡 GPR 간접 |
| 미중 추가 관세 | 즉시~2주 | 낮음(보도 즉시) | ★★★ | 🟡 GPR 간접 |

---

## §5 역사적 이벤트별 키워드 검증 사례

### Case 1. 2022년 러시아-우크라이나 전쟁 (SBO 역대 최고가 배경)

- **선행 신호 키워드**: `"Ukraine sunflower oil export ban"`, `"sunflower oil supply shortage"`, `"Kyiv invasion"`, `"Black Sea port closure"`
- **선행성**: 2022-01~02월 국경 긴장 보도 시작 → 가격 상승 선행 3~6주
- **가격 결과**: CBOT BO=F 2022-03-08 USc 77.26/lb (역대 최고)
- **SBO 영향 경로**: 우크라이나 해바라기유(세계 공급 46%) 수출 중단 → SBO 대체 수요 급증

### Case 2. 2023~24년 수에즈 운하 후티 공격 (운임 급등)

- **선행 신호 키워드**: `"Houthi Red Sea attack"`, `"MSC Maersk Red Sea reroute"`, `"Cape of Good Hope oil tanker"`
- **선행성**: 2023-11월 첫 공격 후 운임 2주 내 급등
- **가격 결과**: BCAA(발틱탱커지수) +35~80%; 한국 대두유 CIF +$15~30/MT 추정
- **SBO 영향 경로**: 유럽행 탱커 희망봉 우회 → 운임 급등 → 한국·일본 수입 CIF 상승

### Case 3. 2018년 미중 무역전쟁 1라운드

- **선행 신호 키워드**: `"Trump soybean tariff China"`, `"China retaliatory tariff soybean"`, `"Section 301 agriculture"`
- **선행성**: 2018-06-15 부과 전 2~4주 보도 기간 내 선물 하락 선행
- **가격 결과**: CBOT BO=F 2018년 6~8월 약세; 브라질·아르헨티나산으로 수요 이동
- **SBO 영향 경로**: 중국 미국산 대두 관세 → 브라질 공급 집중 → 아르헨티나 압착 여력 감소 → SBO 공급 타이트

### Case 4. 2022년 인도네시아 팜유 수출금지 (CPO→SBO 대체)

- **선행 신호 키워드**: `"Indonesia palm oil export ban 2022"`, `"Jokowi CPO ban"`, `"Indonesia cooking oil"`, `"Indonesia edible oil shortage"`
- **선행성**: 2022-04-22 금지령 → 즉시 CPO 공급 충격
- **가격 결과**: CBOT BO=F 2022-04~05월 추가 상승; CPO/SBO 스프레드 역전
- **SBO 영향 경로**: CPO 대체 수요(인도·EU·중국) → SBO 수요 급증

### Case 5. 2023년 인도네시아 B35 시행 (바이오디젤 수요)

- **선행 신호 키워드**: `"Indonesia B35 February 2023"`, `"Indonesia biodiesel CPO demand 2023"`, `"Pertamina B35"`
- **선행성**: 2023-01월 공식 발표 → 2월 시행; 시행 전 CPO 수요 선반영
- **가격 결과**: CPO 강보합; SBO 상대적 약세(CPO 수요 증가로 경쟁 완화)
- **SBO 영향 경로**: 인도네시아 CPO 바이오디젤 의무 증가 → 수출 감소 → CPO 공급 타이트 → SBO 경쟁 해소

---

## §6 기존 관련 파일 참조

| 파일 | 내용 |
|---|---|
| `docs/research_desk/unstructured_data_geopolitical_panel_2026_06_18.md` | 지정학 이벤트 수집 전략 패널 (C-01~C-03, P1-01~P1-04) |
| `docs/research_desk/hormuz_monitor_tech_analysis.md` | 호르무즈 해협 모니터링 기술 분석 |
| `docs/research_desk/soybean_oil_historical_crisis_analysis.md` | SBO 역사적 위기 분석 |
| `docs/research_desk/soybean_oil_historical_crisis_corrections_2020_2025.md` | 2020~2025 위기 보정 데이터 |
| `docs/research_desk/feature_engineering_selection_framework_2026_06_17.md` | D-014 피처 엔지니어링 5단계 프레임워크 |

---

*최종 업데이트: 2026-06-22 · Session 29 | 지정학(P1-02) + 바이오연료(P1-04) 키워드 통합본*
