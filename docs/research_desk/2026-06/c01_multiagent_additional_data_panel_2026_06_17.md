# 다중 에이전트 패널 — 추가 데이터 필요성 및 범위 확대 검토

**작성일**: 2026-06-17  
**패널**: C-01(PM) · C-02(시장조사) · C-04(데이터인프라) · P1-01(상품애널리스트) · P1-02(지정학) · P1-03(기후) · P1-04(공급망)  
**의제**: ① 현재 수집 중인 데이터에서 누락된 변수가 있는가? ② 대두유 가격 예측에 타 유지류 데이터를 포함해야 하는가? ③ 수집 기간 2017 확장 후 추가로 필요한 조치는?  
**결정 원칙**: 범위 확대는 CLAUDE.md §1 Scope Lock(대두유 고정) 위반 없이, G1/G2/G3 신호 품질 향상에 한정.

---

## 1. C-01 PM — 의제 설정 및 결론 선요약

### 결론 (선결론)

> **대두유(SBO) 범위는 유지한다.** 타 유지류는 **외생 변수(exogenous covariate)**로만 포함 — 즉, 모델의 설명/예측 변수로만 사용하며, 분석 대상(target) 확장이 아니다.

| 구분 | 결정 | 이유 |
|---|---|---|
| 범위 | SBO 고정 | CLAUDE.md §1 Scope Lock |
| 팜유(CPO) | 외생 변수로 포함 ✅ | CPO-SBO 스프레드가 가장 강력한 대체재 시그널 |
| 유채유(Rapeseed/Canola) | 조건부 포함 ⚠️ | EU 바이오디젤 연계 시 포함; 평시 관련성 낮음 |
| 해바라기유(Sunflower) | Phase B 검토 ⏳ | 우크라이나 전쟁 리스크 모니터 목적에 한정 |
| 코코넛유(Coconut) | 제외 ❌ | SBO와 대체 관계 없음, 틈새 시장 |
| 옥수수유(Corn Oil) | 제외 ❌ | SBO와 공급 연동 없음, 미국 내 부산물 |
| 라드/수지(Animal Fats) | 제외 ❌ | 식품용 대체재이나 무역 구조 상이 |

---

## 2. C-02 시장조사 — 주요 미수집 시장 인텔리전스

### 2.1 즉시 추가 권고 변수 (Phase A)

| 변수 | 소스 | 수집 방법 | 중요도 | 근거 |
|---|---|---|---|---|
| `CPO_SBO_SPREAD` | FRED CPO 프록시 - CBOT BO=F | 기존 커넥터 파생 | ★★★ | 식용유 대체재 스위칭 임계값 |
| `INDIA_PALM_IMPORT_QUOTA` | USDA FAS GAIN India | C-04 PDF 추출 | ★★★ | 인도가 글로벌 팜유 최대 수입국 → SBO 대체 결정 |
| `INDONESIA_B35_COMPLIANCE_RATE` | Perplexity 프록시 | gpr_connector.py 확장 | ★★★ | 인도네시아 바이오디젤 혼합 실행률 → CPO/SBO 수요 균형 |
| `EU_RED3_BIOFUEL_MANDATE` | EUR-Lex 공시 | C-04 PDF 추출 또는 Perplexity | ★★ | EU RE 지침 III → 유채유·SBO 혼합 연료 의무 |
| `ARGENTINA_SOY_CRUSH_VOLUME` | USDA FAS GAIN Argentina | C-04 PDF 추출 | ★★★ | SBO 공급의 35~40%가 아르헨티나 발 |
| `BRAZIL_SOY_EXPORT_PACE` | USDA FAS Weekly Export Sales | wasde_connector.py 확장 | ★★★ | 수확기 브라질 수출 속도 → 단기 가격 방향 |
| `CHINA_SOY_CRUSH_MARGIN` | USDA FAS GAIN China | C-04 PDF 추출 | ★★ | 중국 내 압착 마진 → 중국 SBO 생산·수입 스위치 |
| `ROTTERDAM_SBO_PREMIUM` | Perplexity sonar-pro | gpr_connector.py 확장 | ★★ | 유럽 현물가 프리미엄 → 한국 CFR 기준가 |

### 2.2 팜유(CPO) 외생 변수 포함 근거

팜유는 대두유의 가장 직접적인 대체재이며, 글로벌 식물성 유지류 무역의 약 35%를 차지한다. C-02 분석에 따르면:

- **계절성 패턴**: CBOT SBO 계절 고점(3~5월)과 CPO 계절 저점(4~6월)이 교차하는 시점에 구매 스위칭 발생
- **가격 관계**: CPO-SBO 스프레드 > $175/MT → 식품업체 SBO에서 CPO로 전환. 스프레드 < $50/MT → 역전환
- **데이터 가용성**: FRED CPO 프록시(PPOILUSDM) 및 Malaysia Bursa CPO 선물(FCPOc1) 모두 무료·API 접근 가능

### 2.3 유채유(Rapeseed/Canola) 조건부 포함 기준

유채유 포함은 아래 조건 중 **2개 이상** 충족 시 활성화:
1. EU FAME(바이오디젤) 혼합 의무 변경으로 SBO × 유채유 경쟁 심화
2. 우크라이나 수출 회랑 협약(Black Sea Grain Initiative) 관련 위기 발생
3. G1 Granger 인과검정에서 유채유 가격 p < 0.05 확인

### 2.4 해바라기유(Sunflower) Phase B 포함 기준

- 우크라이나가 글로벌 해바라기유 수출의 약 45%를 담당 (전쟁 이전 기준)
- 2022년 우크라이나 침공 이후 SBO와 일시 가격 연동성 상승
- Phase B 조건: G2 모델 안정화 + 우크라이나 분쟁 장기화 시나리오 시 지정학 더미로 포함

---

## 3. C-04 문서 인프라 — 데이터 수집 기술 검토

### 3.1 신규 파일 구조 (data/raw/ 재편)

```
data/raw/
├── USDA/
│   ├── WASDE/          # 월별 WASDE 취합본 Excel (17년~26년)
│   ├── FAS/
│   │   ├── PSD/        # PS&D Excel (Oil/Oilseed/Meal Soybean)
│   │   └── GATS/       # 미국 대국가별 수출입 통계 Excel
└── FAO/
    └── AMIS/           # FAO AMIS Market Monitor PDF (~99개)
```

### 3.2 추가 데이터 수집 경로

| 데이터 | 현황 | 추가 방법 | 우선순위 |
|---|---|---|---|
| Malaysia CPO 선물 (Bursa) | FRED PPOILUSDM (월별만) | commodity_connector.py yfinance FCPOc1 추가 | 즉시 |
| EU 유채유 가격 | 미수집 | Perplexity 프록시 (월별 EUR/MT) | Sprint 2 |
| Argentina INDEC 수출 월별 | 연별만 수집 | production_connector.py 월별 엔드포인트 추가 | Sprint 2 |
| Brazil ABIOVE 압착량 | 미수집 | Perplexity 프록시 (월별) | Sprint 2 |
| USDA Weekly Export Sales (SBO) | 미수집 | api.fas.usda.gov/api/esr/exports/weekly | Sprint 2 |
| Rotterdam FOB 가격 (SBO) | 미수집 | Perplexity 프록시 | Sprint 3 |
| MPOB Malaysia CPO 재고/생산 | 미수집 | mpob.gov.my PDF 추출 (C-04) | Sprint 3 |

### 3.3 FAO AMIS PDF 처리 방법론

99개 PDF에서 구조화 데이터 추출 우선순위:
1. **즉시 추출 목표**: 공급/수요 밸런스 테이블 (SBO 생산·소비·재고·무역량)
2. **모델**: Claude claude-sonnet-4-6 (128K context) → 표 인식 + 정규화
3. **마케팅연도 처리**: "2023/24" → price_date = 2023-10-01 (10월 기준)
4. **결측 이슈**: 2017년 1월·3월·8월, 2018년~현재 1월·8월 공백 → ffill(limit=1) 허용

---

## 4. P1-01 상품 애널리스트 — 대두유 가격 드라이버 심화 분석

### 4.1 현재 G1 변수 풀 평가

수집 중이나 아직 G1에 포함 안 된 핵심 변수:

| 변수 코드 | 설명 | 공급처 | G1 중요도 추정 |
|---|---|---|---|
| `SBO_CRUSH_MARGIN` | SBO가 + SBM가 - 대두가 (압착 마진) | CBOT 파생 | ★★★ |
| `CBOT_SBO_COT_NET_LONG` | CFTC COT 순매수 포지션 (투기세력) | CFTC.gov CSV | ★★★ |
| `WASDE_SBO_STU_REVISION` | 월별 WASDE 재고사용비율 개정폭 | wasde_connector.py 파생 | ★★★ |
| `BRAZIL_SOY_EXPORT_PACE` | 주간 대두 선적 진도율 (대비 목표) | FAS Weekly Export Sales | ★★ |
| `PALM_BIODIESEL_MANDATE_DELTA` | 인도네시아 B35→B40 의무 확대분 | Perplexity 프록시 | ★★ |
| `US_BIOFUEL_BLEND_RATE_ACTUAL` | EPA RFS 실제 혼합 실행률 | EPA 공개 데이터 | ★★ |

### 4.2 타 유지류의 대두유 가격 영향 메커니즘

```
팜유(CPO)    → SBO와 직접 대체 (식용유지 + 바이오디젤)
유채유       → SBO와 부분 대체 (EU 바이오디젤 FAME)
해바라기유   → SBO와 간접 대체 (유럽·중동 식용 시장)
코코넛유     → SBO와 대체 관계 없음 (세정제·특수식품용)
```

**G1 변수로 추가할 대체재 지표**:
- `CPO_SPOT_ROTTERDAM` (달러/MT) — 즉시 추가 권고
- `RAPESEED_EU_SPOT` (유로/MT) — 조건부 추가
- `SUNFLOWER_BLACK_SEA_FOB` (달러/MT) — Phase B

### 4.3 USDA FAS GATS 데이터 활용 방안

GATS(Global Agricultural Trade System) HS 1507 수출 데이터는 아래 변수를 생성한다:

| 변수 코드 | 설명 | G-목표 |
|---|---|---|
| `US_SBO_EXPORT_KOREA` | 미국→한국 SBO 수출량 (MT) | G1: 한국 수입 다변화 |
| `US_SBO_EXPORT_CHINA` | 미국→중국 SBO 수출량 | G1: 미중 무역 긴장 프록시 |
| `US_SBO_EXPORT_TOTAL` | 미국 SBO 전체 수출량 | G1/G2: 미국 공급 측 압력 |
| `US_SBO_EXPORT_YOY_GROWTH` | 전년비 미국 수출 성장률 | G1: 추세 가속·감속 |

---

## 5. P1-02 지정학 — 지정학 변수 확장 검토

### 5.1 현재 누락된 지정학 변수

| 변수 | 관련 지역 | SBO 영향 경로 | 수집 방법 |
|---|---|---|---|
| `BLACK_SEA_CONFLICT_INDEX` | 우크라이나·러시아 | 해바라기유·유채유 공급 위기 → SBO 대체 수요 | GDELT + geointel_connector |
| `SOUTH_CHINA_SEA_RISK` | 남중국해 | 말라카 해협 탱커 위협 → SBO CIF 상승 | AIS + GDELT |
| `ARGENTINA_POLITICAL_RISK` | 아르헨티나 | 밀레이 정부 농업 정책 → 수출세 변동 | GPR 국가별 + Perplexity |
| `BRAZIL_ELECTION_DUMMY` | 브라질 | 선거 연도 농업 정책 불확실성 | 연도 더미 변수 |
| `US_FARM_BILL_STATUS` | 미국 | 농업 보조금·RFS 정책 지속성 | Perplexity 프록시 |

### 5.2 지정학 인과관계 확장 체인

현재 `_render_causal_chains()`에 아래 체인 추가 권고:

| 동인 | 경로 | 방향 |
|---|---|---|
| 중국 정부 SBO 비축 발표 | 중국 수입 급증 발표 → 글로벌 재고 감소 우려 → 선물 가격 급등 | ▲ |
| 인도 팜유 수입관세 인하 | CPO 수입 증가 → CPO-SBO 스프레드 축소 → SBO 대체 수요 감소 | ▼ |
| EU 탈삼림 규정(EUDR) 강화 | 팜유 EU 시장 접근 차단 → SBO 대체 수요 증가 → 가격 상승 | ▲ |
| 미국-아르헨티나 무역 긴장 | 아르헨 수출세 협상 리스크 → 공급 불확실성 프리미엄 | ▲ |

---

## 6. P1-03 기후 — 기후 변수 심화 검토

### 6.1 현재 누락된 기후 변수

| 변수 | 관련 지역 | SBO 영향 | 수집 방법 |
|---|---|---|---|
| `BRAZIL_SOIL_MOISTURE_ANOMALY` | 마토그로소/파라나 | 파종기(9~11월) 토양 수분 이상 → 작황 선행 지표 | NASA POWER soil_moisture_0_to_10cm |
| `ARGENTINA_PRECIPITATION_ANOMALY` | 팜파스 | 개화기(1~2월) 강수 편차 → 수율 영향 | Open-Meteo ERA5 |
| `US_MIDWEST_GDD_ACCUMULATION` | 아이오와·일리노이 | 생육도일수(GDD) 누적량 → 수확량 예측 | NOAA NASS 파생 또는 NASA POWER |
| `LA_NINA_PROBABILITY` | ENSO | 다음 시즌 라니냐 확률 → 남미 가뭄 선행 | NOAA CPC ENSO Outlook PDF |
| `INDIAN_OCEAN_DIPOLE_INDEX` | 인도양 | IOD 양위상 → 인도·인도네시아 건조 → CPO·SBO 공급 감소 | NOAA 또는 BOM Australia |

### 6.2 기후 이벤트 → SBO 가격 반응 시차

```
ENSO 신호(6개월 전) → 남미 강수 이상(3개월 전) → 작황 조정(수확 직전) → 가격 반응(2주 내)
```

G1 Granger 검정에서 ENSO_ONI의 최적 시차(best_lag)가 2~6개월 범위에 집중될 것으로 예상.  
현재 수집 중이나 `G1 LASSO`에서 아직 통계적 유의성 미확인 → 30일+ 누적 후 재검증.

---

## 7. P1-04 공급망 — 물류·가격 연동 변수 추가 검토

### 7.1 현재 누락된 공급망 변수

| 변수 | 설명 | 수집 방법 | 우선순위 |
|---|---|---|---|
| `BCAA_TANKER_SBO_SPECIFIC` | BCAA 중 SBO 특정 항로 운임 | Baltic Exchange 직접 API (Phase B) 또는 Perplexity | Sprint 2 |
| `PARANAGUA_WAITTIME` | 파라나구아항(BR) 대기 시간 | AIS 데이터 파생 또는 Perplexity 프록시 | Sprint 2 |
| `KOREA_SBO_STOCK_DAYS` | 한국 내 SBO 재고 일수 | KHOA(한국유지가공협회) 보고서 → C-04 PDF | Sprint 3 |
| `INCOTERM_CFR_BUSAN_SBO` | 부산항 도착 CFR 대두유 현물가 | Argus Media (유료) 또는 IHS Markit | Phase B |
| `US_GULF_TO_BUSAN_FREIGHT` | 미국 걸프 → 부산 탱커 운임 | BCAA 항로 데이터 또는 Perplexity | Sprint 2 |

### 7.2 GATS 재수출 데이터 활용

**재수출(Re-export)** 데이터의 의미: 미국이 수입한 SBO를 제3국으로 재수출하는 물량.  
2018년 재수출 데이터 없음 → 해당 연도 이 변수는 0 또는 결측으로 처리.

파생 변수:
- `US_SBO_DOMESTIC_USE` = 미국 총수입 - 재수출 (진짜 미국 내수 수요)
- `US_SBO_REEXPORT_RATIO` = 재수출/수출 × 100 (전처리 무역 비중)

### 7.3 한국 SBO 조달 특이 구조

패널이 공유하는 한국 SBO 조달 구조:
1. **주 공급원**: 아르헨티나(~55%) → 브라질(~30%) → 미국(~10%) → 기타
2. **대체 구조**: 아르헨 수출세 충격 시 브라질·미국 물량으로 단기 전환
3. **계절성**: 10~12월 한국 수입 증가(연말 식품 수요), 아르헨 수확기(4~5월) 후 6월 한국 도착

---

## 8. C-01 PM — 우선순위 종합 및 Sprint 계획

### 8.1 즉시 추가 권고 (Sprint 2 — G1 안정화 병행)

| # | 작업 | 담당 | WBS | 예상 시간 |
|---|---|---|---|---|
| 1 | CPO 선물가(Bursa FCPOc1) → commodity_connector.py | C-04 | 1.1.25 확장 | 0.5h |
| 2 | SBO 압착 마진(Crush Margin) 파생 변수 계산 | C-03 | G1 전처리 | 0.5h |
| 3 | CFTC COT 순매수 포지션 수집 | C-04 → commodity_connector.py | 1.1.26 신규 | 1h |
| 4 | gpr_connector.py → 인도·EU 정책 뉴스 프록시 추가 | C-04 | 1.1.9 확장 | 0.5h |
| 5 | FAO AMIS PDF LLM 추출 스크립트 (ingest_fao_amis_pdf.py) | C-04 | 1.1.41 | 2h |
| 6 | GATS Excel 파서 (ingest_gats_data.py) | C-04 | 1.1.42 | 1h |

### 8.2 Phase B 데이터 확장 목록

| 데이터 | 이유 | 조건 |
|---|---|---|
| Rotterdam SBO FOB 현물가 | Argus Media 유료 | G2 모델 안정화 후 |
| MPOB Malaysia CPO 월별 재고·생산 | PDF 추출 노력 큼 | G2 안정화 후 |
| 한국 SBO 재고 일수 (KHOA) | 한국어 보고서 | Phase B |
| 해바라기유 Black Sea FOB | 우크라이나 위기 모니터 | 분쟁 지속 여부 조건 |
| Baltic Tanker SBO 항로 운임 | Baltic Exchange 유료 | Phase B |
| EU 유채유 선물 (Euronext) | API 접근 확인 필요 | Sprint 3 |

### 8.3 범위 확대 금지 항목 (CLAUDE.md §1 준수)

아래 항목은 요청이 있더라도 범위 외로 처리:
- 팜유 자체를 분석 **대상(target)**으로 확장
- 유채유·해바라기유를 Buy/Hold **신호 생성**에 직접 사용
- 비식품 유지류(윤활유, 공업용) 가격 수집
- 단백질 원료(대두박 SBM) 독립 분석 (대두유 가격 파생 계산용으로만 허용)

---

## 9. 최종 패널 합의

| 항목 | 합의 내용 |
|---|---|
| **범위** | SBO 대상 고정. 타 유지류 = 외생 변수만 |
| **팜유(CPO)** | 즉시 포함: FCPOc1 선물가 + CPO-SBO 스프레드 |
| **유채유** | EU 바이오디젤 연계 시 조건부 포함 |
| **해바라기유** | Phase B (우크라이나 지정학 더미로만) |
| **신규 우선 변수** | 압착 마진, CFTC COT, 브라질 수출 진도율, 인도·EU 정책 |
| **수집 기간** | 2017년 기준으로 확장 (D-014) |
| **causal chains** | 인도 관세·EU EUDR·중국 비축·미-아르헨 관계 추가 |

---

*Project Nexus · C-01×C-02×C-04×P1-01~04 패널 · 2026-06-17*  
*다음 조치: commodity_connector.py FCPOc1 추가 → Sprint 2 WBS 번호 부여*
