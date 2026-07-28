# 비정형 데이터(지정학 이벤트) 수집 전략 — 다중 에이전트 패널
**작성일**: 2026-06-18  
**패널**: C-01(PM) · C-02(시장조사) · C-03(데이터) · P1-01(상품) · P1-02(지정학) · P1-03(기후) · P1-04(공급망)  
**의제**:  
① 대두유 공급·수요에 영향을 주는 지정학 이벤트(호르무즈·수에즈·러-우 전쟁·흑해·미중 무역전쟁 등)의 현재 수집 현황  
② 수집 공백 분석 및 권고 키워드·미디어 채널  
③ 데이터 수집 현황(해운·작황·GPR·관세청·지정학인텔) 미수집 원인 및 해결 방안

---

## 1. 현재 비정형 데이터 수집 현황 (C-03)

### 1.1 현재 수집 중인 비정형·반정형 소스

| 소스 | 수집 변수 | 방식 | BACKFILL 지원 |
|---|---|---|---|
| Caldara & Iacoviello GPR xlsx | `GPR_NORMALIZED`, `GPR_HISTORICAL` | API (공개 xlsx 다운로드) | ✅ (2017~) |
| Perplexity sonar-pro (GPR 실시간) | `GPR_REALTIME` | Perplexity API | ❌ (오늘 날짜만) |
| Perplexity sonar-pro (호르무즈) | `HORMUZ_THREAT_LEVEL` | Perplexity API | ❌ |
| Perplexity sonar-pro (정책 뉴스) | `ARG_EXPORT_TAX_NEWS`, `INDIA_DUTY_NEWS`, `BIODIESEL_MANDATE_NEWS`, `WASDE_CONSENSUS_SCORE` | Perplexity API | ❌ |
| GeoIntel (USGS/NOAA/GDELT/FIRMS) | `GEOINTEL_RISK_COMPOSITE`, `SEISMIC_*` | 공개 REST API | ❌ (실시간 전용) |

### 1.2 현재 미수집 이벤트 유형

| 이벤트 | SBO 영향 경로 | 현재 수집 여부 |
|---|---|---|
| 호르무즈 해협 위기 (이란·후티) | 유가 → 벙커유 → CFR +3~8% | 🟡 Perplexity 실시간만 |
| 수에즈 운하 봉쇄 (후티 2023~24) | 아시아↔유럽 탱커 우회 → 운임 급등 | ❌ 미수집 |
| 러-우크라이나 전쟁 (2022~) | 해바라기유 공급 차질 → SBO 대체 수요 | ❌ 미수집 |
| 흑해 곡물 협정 (2022~23) | 우크라이나 대두·해바라기유 수출 중단·재개 | ❌ 미수집 |
| 미·중 무역전쟁 관세 (2018, 2025~) | 중국 미국산 SBO 수입 급감 → 글로벌 재편 | 🟡 WASDE_CONSENSUS_SCORE로 간접 |
| 인도네시아 수출금지 (2022 팜유) | CPO 공급 충격 → SBO 대체 수요 | ❌ 미수집 |
| 아르헨티나 수출세 변경 | 대두유 수출 채산성 → 글로벌 공급 | 🟡 ARG_EXPORT_TAX_NEWS로 간접 |
| 브라질 작황 뉴스 (파종기·수확기) | 대두 생산량 선행 → SBO 공급 | ❌ 체계적 미수집 |

---

## 2. C-02 시장조사 — 비정형 데이터 수집 필요성 분석

### 2.1 수집 근거 (SBO 가격 영향 실증)

**러시아-우크라이나 전쟁 (2022)**  
- 우크라이나는 세계 1위 해바라기유 수출국 (전 세계 공급의 46%). 전쟁 직후 해바라기유 수출 중단.  
- SBO 대체 수요 급증 → CBOT BO=F 2022년 3월 USc 77/lb (역대 최고).  
- 선행 신호: "Ukraine sunflower oil export ban", "Black Sea grain corridor" 키워드 → 가격 급등 3~6주 선행.

**수에즈 운하 후티 공격 (2023년 말~2024)**  
- 희망봉 우회로 → 아시아↔유럽 항로 10~14일 연장 → 탱커 운임 +35~80%.  
- 한국 대두유 수입 CFR에 직접 영향.  
- BDI 및 BCAA가 해당 기간 급등했으나 당시 미수집 상태.

**미·중 무역전쟁 2차 (2025)**  
- D-009 역사 분석(현재 유사도 9/10). 중국이 미국산 SBO 수입을 브라질/아르헨티나로 전환.  
- 한국 조달자: 미국 물량이 중국으로 전환되지 않으면서 단기 가격 하락 → 구매 기회.

### 2.2 P1-02 지정학 — 권고 수집 키워드 목록

#### 최우선 키워드 (Phase A 즉시 적용)

| 주제 | 한국어 키워드 | 영문 키워드 | 가격 방향 |
|---|---|---|---|
| 호르무즈·이란 | 호르무즈 봉쇄, 이란 미사일, 후티 공격 | Hormuz closure, Iran sanctions, Houthi attack tanker | ▲ |
| 수에즈·홍해 | 수에즈 봉쇄, 홍해 위기, 후티 선박 공격 | Suez blocked, Red Sea shipping, Houthi vessel attack | ▲ |
| 러-우크라이나 | 우크라이나 전쟁, 흑해 수출, 해바라기유 | Ukraine war grain, Black Sea corridor, sunflower oil | ▲ |
| 미·중 관세 | 미중 관세 전쟁, 대두 추가관세, 중국 보복 | US China tariff, soybean tariff, China retaliatory | ▼단기/혼조 |
| 아르헨티나 | 아르헨 수출세 인상, 아르헨 대두유 수출 | Argentina soybean oil export tax, Argentina devaluation | ▲/▼ |
| 인도 정책 | 인도 식용유 관세, 인도 CPO 수입 | India edible oil duty, India palm oil import | ▲ |
| 인도네시아 | 인도네시아 수출금지, CPO 수출 제한 | Indonesia palm oil export ban, CPO export restriction | ▲(SBO) |
| 브라질 작황 | 브라질 대두 작황, 마토그로소 수확 | Brazil soybean harvest, Mato Grosso crop, Brazil drought | ▲/▼ |

#### 2차 키워드 (Phase B)

| 주제 | 키워드 | 소스 |
|---|---|---|
| 바이오디젤 정책 | B35/B40 의무 혼합, SAF 항공유 원료 | OECD/IEA 보고서 |
| WASDE 컨센서스 | WASDE 서프라이즈, USDA 예상 대비 실제 | Bloomberg/Reuters |
| 중국 SPR 비축 | 중국 식용유 비축, 국가비축물자 | 중국 국가발전개혁위 |

### 2.3 P1-04 공급망 — 권고 미디어 채널

| 채널 | 유형 | 무료 여부 | 수집 방법 |
|---|---|---|---|
| Reuters Commodities | 뉴스 | 일부 무료 | Perplexity sonar-pro 쿼리 |
| Bloomberg Markets | 뉴스 | 유료 | Perplexity 프록시 (제목 요약) |
| Oil World (Hamburg) | 전문 보고서 | 유료 | Phase B — API 없음, 수동 |
| USDA FAS GAIN Reports | 국가별 농산물 정보 | 무료 | C-04 PDF 파서 (이미 구현) |
| FAO AMIS Market Monitor | 월간 공급·수요 | 무료 | ingest_fao_amis_pdf.py (구현) |
| GDELT (지정학 이벤트) | 뉴스 DB | 무료 | geointel_connector.py (기존) |
| MarineTraffic / VesselsValue | AIS 선박 | 유료 | Phase B (비용 이슈) |

---

## 3. C-01 PM — 비정형 데이터 수집 실행 계획

### 3.1 Phase A 즉시 조치 (gpr_connector.py 확장)

현재 `_fetch_policy_news_proxy()`가 4가지 정책 뉴스를 수집 중. 아래 3개 이벤트 카테고리를 추가:

```python
# gpr_connector.py에 추가할 Perplexity 프록시 함수

EVENT_QUERIES: dict[str, str] = {
    "SUEZ_RED_SEA_RISK": (
        "Current shipping disruption status in Suez Canal and Red Sea in past 7 days. "
        "Any Houthi attacks, vessel damage, or rerouting? "
        "Format: RISK_LEVEL: [HIGH/MEDIUM/LOW] | DISRUPTION: [yes/no + brief]"
    ),
    "UKRAINE_GRAIN_CORRIDOR": (
        "Current status of Ukraine grain and sunflower oil exports via Black Sea corridor or alternative routes. "
        "Any export bans, military threats, or disruptions in past 7 days? "
        "Format: EXPORT_STATUS: [NORMAL/DISRUPTED/BLOCKED] | RISK: [HIGH/MEDIUM/LOW]"
    ),
    "US_CHINA_TARIFF_STATUS": (
        "Current US-China trade tariff status for soybeans and soybean oil. "
        "Any new tariff announcements, exemptions, or negotiations in past 7 days? "
        "Format: TARIFF_CHANGE: [INCREASED/DECREASED/UNCHANGED] | IMPACT: [positive/negative/neutral for US exporters]"
    ),
    "BRAZIL_HARVEST_PROGRESS": (
        "Current Brazil soybean harvest progress and export pace in Mato Grosso region. "
        "Any weather disruptions, port delays, or logistic issues? "
        "Format: HARVEST_PCT: [%] | DELAY: [yes/no] | EXPORT_PACE: [above/on/below average]"
    ),
}
```

### 3.2 Phase B 고도화 계획

- `news_sentiment_connector.py` 신규: FinBERT 감성 분석 (-1~+1) + 키워드 매칭
- GDELT 역사 이벤트 DB 수집 (2017~현재): geointel_connector.py BACKFILL 모드 추가
- MarineTraffic Phase B: AIS WebSocket → 수에즈·호르무즈 실시간 탱커 추적

---

## 4. 데이터 수집 미수집 원인 분석 및 해결 방안 (C-08)

### 4.1 미수집 원인 요약

| 데이터셋 | 현재 상태 | 미수집 근본 원인 | 해결 방안 |
|---|---|---|---|
| **해운지수(BCAA/BDI)** | ❌ parquet 없음 | Historical Backfill 워크플로우 미실행. TE REST API 수정 완료(A-034)이나 배포 안됨. BCAA는 BACKFILL_MODE에서 Perplexity 건너뜀(정상). | ① dev→main 브랜치 병합 ② GitHub Actions → Historical Backfill 수동 트리거 (connector=shipping) |
| **작황(WASDE/PSD)** | ❌ parquet 없음 | USDA FAS API 엔드포인트 수정 완료(A-007/A-019)이나 Backfill 미실행. | Backfill 트리거 (connector=wasde) |
| **지정학(GPR/호르무즈)** | ❌ parquet 없음 | GPR xlsx openpyxl 버그 수정 완료(A-030)이나 Backfill 미실행. 호르무즈는 BACKFILL_MODE 건너뜀(정상). | Backfill 트리거 (connector=gpr) |
| **수입통계(관세청 HS1507)** | ❌ parquet 없음 | **HS 코드 오류**: 10단위(1507101000 등) → API는 6단위(150710, 150790) 수용. → 2026-06-18 수정 완료. 서비스키는 유효함. | customs_connector.py 수정 배포 후 Backfill 트리거 (connector=customs) |
| **지정학 인텔리전스(USGS/NOAA/GDELT/FIRMS)** | ❌ (설계적 제외) | BACKFILL_MODE=true 시 geointel_connector.py 전체 건너뜀(실시간 전용). GDELT 역사 API는 별도 구현 필요. | Phase B: GDELT 역사 수집 추가. 현재 Phase A에서는 USGS/NOAA/FIRMS 일별 실시간 수집만 가능. GPR 역사가 지정학 대리 지표로 활용 가능. |

### 4.2 즉시 실행 절차 (사용자 조치 필요)

```
1. GitHub → Nexus 저장소 → Actions 탭
2. "Historical Data Backfill" 워크플로우 선택
3. "Run workflow" 클릭
4. 입력값:
   - start_year: 2017
   - end_year:   2025
   - connector:  all          (전체 재수집)
   - skip_analysis: false     (C-08→C-06→G1 분석 포함)
5. "Run workflow" 확인

예상 소요 시간: ~25분
```

> **사전 조건**: dev 브랜치(`claude/setup-nexus-llm-tools-RX4aS`) → main 병합 완료 후 실행할 것.  
> 병합 전 실행 시 customs_connector.py HS 코드 수정이 반영되지 않아 관세청 수집 실패 지속.

### 4.3 날짜 범위 기본값 표준화 (현재 상태 및 변경 내역)

- `historical_backfill.yml`: `start_year` 기본값 = **2017**, `end_year` 기본값 = **2025** (이미 설정됨)
- 커넥터별 `HISTORICAL_START_YEAR` / `HISTORICAL_END_YEAR` 환경변수 주입: 전체 커넥터에 이미 적용됨
- `customs_connector.py`: `HISTORICAL_END_YEAR` 읽기 기능 → 2026-06-18 수정 완료

> 워크플로우 실행 전 입력값 UI에서 start_year/end_year를 자유롭게 변경 가능.  
> 예) 2022~2024년 재수집: start_year=2022, end_year=2024

---

## 5. 대두유 가격 영향 인과관계 체인 — 추가 분석 (3-1)

C-02, C-03, P1-01~04 공동 검토. 현재 보고서에 12개 체인이 등록됨. 아래 4개를 추가 권고.

### 5.1 신규 추가 권고 인과관계 (미등록)

| 번호 | 동인 | 인과관계 경로 | 가격 방향 | SBO 특정성 |
|---|---|---|---|---|
| A | **수에즈·홍해 운항 중단** | 후티 공격 → 탱커 희망봉 우회 → 운항 거리 +10~14일 → CFR 운임 +35~80% → 한국 CIF 상승 | ▲ | 높음 |
| B | **우크라이나 해바라기유 공급 차질** | 전쟁 격화 → 흑해 수출항 봉쇄 → 해바라기유 대체 수요 → SBO 가격 급등 | ▲ | 높음 (대체재 경쟁) |
| C | **브라질 대두 파종기(9~11월) 날씨 이상** | 파종기 가뭄 → 재배 면적 축소 우려 → 6~9개월 선행 선물 가격 상승 | ▲ | 높음 (원료 공급) |
| D | **중국 전략비축물자(SPR) 방출** | SPR 방출 발표 → 시장 과잉 공급 신호 → 단기 가격 하락 | ▼ | 중간 |

### 5.2 인과관계 체인 완전성 평가 (P1-01)

현재 보고서의 12개 체인을 카테고리별로 평가:

| 카테고리 | 등록 체인 수 | 완전성 평가 | 미등록 주요 체인 |
|---|---|---|---|
| 정책·규제 | 5개 | ✅ 충분 | EUDR 발효 (이미 포함) |
| 기후·작황 | 3개 | ⚠️ 파종기 날씨 미포함 | 브라질 파종기 이상기후 추가 필요 |
| 지정학·무역 | 3개 | ⚠️ 수에즈·우크라이나 미포함 | A, B 추가 필요 |
| 시장 구조 | 4개 | ✅ 충분 | — |

**C-03 결론**: 신규 4개 체인을 `_CAUSAL_CHAINS` 리스트에 추가 권고. 다음 세션에서 구현.

---

## 6. AISstream.io API 상태 확인 결과

**확인 방법**: GitHub 참조 코드 분석 (Hue-Jhan/OSINT-War-Room, JJ/AISstreamer)

| 항목 | 확인 결과 |
|---|---|
| 프로토콜 | **WebSocket 전용** (`wss://stream.aisstream.io/v0/stream`). REST API 없음. |
| 인증 방식 | 연결 직후 JSON payload에 `APIkey` 필드 전송 (HTTP 헤더 아님) |
| 무료 tier | **현재 제공 중** (experimental 서비스, 무료). IP 블록 주의. |
| 키 만료 | 공식 만료 정책 없음. 과도한 연결 시 IP 차단 → 24시간 대기 또는 키 재발급 |
| 코드 수정 | `ais_connector.py` → WebSocket 방식으로 수정 완료 (2026-06-18) |

**재발급 방법**: 필요 시 [aisstream.io](https://aisstream.io) 에서 무료 재등록 → 새 API Key 발급 → GitHub Secrets `AISSTREAM_API_KEY` 업데이트.

---

*→ 다음 조치: dev→main 브랜치 병합 → Historical Backfill 수동 트리거 → gpr_connector.py에 신규 이벤트 4개 추가*
