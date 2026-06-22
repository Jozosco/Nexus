# 대두유 대체재·보완재(타 유지류) 추가 수집 우선순위 — 다중 에이전트 패널

**작성일**: 2026-06-22  
**의제**: 대두유(SBO)의 **대체재(substitutes)·보완재(complements)** 데이터 미확보 구간을
긴급도 순으로 정리하고, ① 현재 등록 API로 수집 가능 여부 ② 불가 시 무료/유료 수집 방법과
권위·적시성 있는 소스를 명시.  
**참여**: C-01 · C-02 · P1-01 · P1-02 · P1-03 · P1-04  
**참조**: README §QR(D-015 8대 핵심 변수), `feature_engineering_selection_framework_2026_06_17.md`

---

## 0. 핵심 요약 (TL;DR)

| 순위 | 데이터 | 분류 | 현재 상태 | 등록 API 수집 | 권장 수집(무료/유료) |
|---|---|---|---|---|---|
| 🔴 1 | CBOT 대두박 `ZM=F` + 대두 `ZS=F` 선물 | 보완재(연산물) | ❌ 가격 미수집 | ✅ **가능(무료)** | yfinance (BO=F와 동일 채널) |
| 🔴 2 | 팜유(CPO) **일별** 벤치마크 (Bursa FCPO) | 대체재 #1 | 🟡 월별 프록시·TE 스팟만 | ⚠️ 부분 | 유료(Bursa/Refinitiv) 또는 FRED 월별 무료 |
| 🟠 3 | 유채유(Rapeseed/Canola) 가격 | 대체재(EU·북미) | ❌ 미수집 | ✅ **월별 무료(FRED)** | FRED `PROILUSDM` 무료 / MATIF 유료(일별) |
| 🟠 4 | 해바라기유(Sunflower) FOB | 대체재(흑해) | ❌ 미수집 | ✅ **월별 무료(FRED)** | FRED `PSUNOUSDM` 무료 / APK-Inform·Platts 유료(주별) |
| 🟡 5 | ICE 캐놀라(Winnipeg) 선물 | 대체재(북미) | ❌ 미수집 | ⚠️ 제한적 | yfinance 제한 / Nasdaq Data Link |
| 🟢 6 | 라우릭유(팜핵유 PKO·코코넛유) | 대체재(틈새) | ❌ 미수집 | ❌ | FRED 코코넛유 월별 무료 |

> **즉시 실행 권고(C-01)**: 순위 1·3·4는 **이미 등록된 무료 API(yfinance·FRED)** 만으로 오늘
> 바로 수집 가능. 순위 2(CPO 일별)만 유료 도입 검토 대상. → **무료 3종 우선 착수**.

---

## 1. 배경 — 왜 대체재·보완재인가 (C-02 시장조사)

대두유 가격은 단독으로 움직이지 않고 **글로벌 식물성 유지류 복합체(vegetable oil complex)**
안에서 상대가격으로 결정됨. 8대 식용유(팜·대두·유채·해바라기) 중 대두유는 생산량 2위이며,
**팜유와의 스프레드(CPO-SBO spread)** 가 식품·바이오디젤 수요의 대체 방향을 결정함.

- **대체재 채널**: 팜유·유채유·해바라기유 가격이 SBO 대비 싸지면 → 식품·바이오디젤 수요가
  대체재로 이탈 → SBO 가격 하방. (D-015의 `CPO_SBO_SPREAD` 가 이 채널을 직접 포착)
- **보완재(연산물) 채널**: 대두 압착 시 **대두유(약 19%) + 대두박(약 79%)** 이 동시 생산됨.
  대두박 수요(사료)가 강하면 압착량 증가 → **대두유 공급 증가(부산물)** → 가격 하방.
  이 관계를 포착하려면 **크러시 스프레드(crush spread)** 와 **oil share** 가 필요함.

**C-02 결론**: 현재 SBO·BDI·WASDE는 갖췄으나 **상대가격 축(대체재)** 과 **공급 부산물 축
(보완재)** 이 비어 있어 G1 변수 중요도·G2 가격 밴드의 설명력이 구조적으로 부족함.

---

## 2. 긴급도 1순위 🔴 — 대두박·대두 선물 (보완재/연산물)

### 근거 (P1-01 대두유 시장)
> 커머디티 데스크에서 SBO 공급을 읽는 핵심은 **크러시 마진(board crush)** 입니다.
> `Board Crush = (대두박 가격 × 0.022 + 대두유 가격 × 0.11) − 대두 가격`.
> 크러시 마진이 높으면 압착업체가 가동률을 올리고, 대두유는 그 **부산물로 공급이 늘어** 가격이
> 눌립니다. 반대로 대두박 수요가 약하면 압착이 줄어 SBO 공급도 타이트해집니다.
> **oil share = 대두유 가치 / (대두유+대두박 가치)** 는 SBO 단독 수요 강도를 보여주는 1급 지표입니다.

### 영향 경로
```
대두박(사료) 수요 강세 → 압착 가동률 ↑ → 대두유 부산물 공급 ↑ → SBO 가격 하방 압력
대두박 수요 약세      → 압착 감소      → 대두유 공급 타이트       → SBO 가격 상방 압력
```

### 데이터·수집 방법
| 지표 | 티커 | 소스 | 비용 | 갱신 |
|---|---|---|---|---|
| CBOT 대두박 선물 | `ZM=F` | yfinance (Yahoo Finance) | **무료** | 일별 |
| CBOT 대두 선물 | `ZS=F` | yfinance | **무료** | 일별 |
| (보유) CBOT 대두유 | `BO=F`/`ZL=F` | yfinance | 무료 | 일별 |

- **등록 API로 수집 가능**: ✅ — `commodity_connector.py` 의 BO=F 수집 로직(yfinance)을 그대로
  확장. 신규 키·비용 불필요. (`ZM=F`, `ZS=F` Yahoo Finance 확인 완료)
- **폴백**: yfinance IP 차단 시 Nasdaq Data Link(`NASDAQ_DATALINK_API_KEY` 등록됨)의
  CME 연속 선물(CHRIS) — 단, 무료 티어 제약 있어 적시성 낮음.
- **신규 파생 지표**: `SBO_CRUSH_SPREAD`, `SBO_OIL_SHARE` 를 파이프라인에서 계산해 G1 피처로 추가.

---

## 3. 긴급도 2순위 🔴 — 팜유(CPO) 일별 벤치마크 (대체재 #1)

### 근거 (P1-01)
> `CPO_SBO_SPREAD` 는 D-015 8대 핵심 변수입니다. 그런데 현재 CPO는 **FRED 월별 프록시
> (`PPOILUSDM`)** 와 **Trading Economics 스팟** 에만 의존해 **일별 해상도가 없습니다**. 일별 SBO와
> 월별 CPO를 빼면 스프레드가 왜곡됩니다. 진짜 벤치마크는 **Bursa Malaysia 원유팜유 선물(FCPO,
> MYR/톤)** 과 **Rotterdam CIF CPO** 입니다.

### 현재 상태
- `commodity_connector.py`: Trading Economics `CPO_USD_MT`(스팟) 우선 → 실패 시 FRED
  `PPOILUSDM`(월별 프록시) 폴백. → **일별 연속 시계열 부재**.

### 수집 방법·소스
| 옵션 | 소스 | 권위 | 적시성 | 비용 |
|---|---|---|---|---|
| A (권장 일별) | **Bursa Malaysia FCPO** (Refinitiv/Bursa Station) | ★★★ (글로벌 팜유 기준가) | 일별(실시간) | **유료** (Bursa 시세 ~USD 25~/월, Refinitiv 별도) |
| B (대안 일별) | **Trading Economics** 유료 티어 commodities | ★★☆ | 일별 | **유료** (TE는 무료 티어 샘플만) |
| C (무료 월별) | **FRED `PPOILUSDM`** (IMF Palm Oil, Malaysia/Indonesia) | ★★★ (IMF) | 월별 | **무료** (등록 키) |
| D (무료 일별 근사) | MPOB·GAPKI 고시가 스크래핑 | ★★☆ | 일별~주별 | 무료(비공식) |

- **등록 API로 수집 가능**: ⚠️ **부분** — 무료로는 FRED 월별(C)이 한계. 일별은 유료(A/B) 필요.
- **C-01 권고**: 우선 **FRED 월별 + yfinance BO=F 일별** 로 스프레드의 월별 기준선을 확보하고,
  유료 일별(Bursa)은 G2 학습 정밀도 요구가 확인된 뒤 도입. (예산 게이트 통과 후)

---

## 4. 긴급도 3순위 🟠 — 유채유 (Rapeseed/Canola, 대체재)

### 근거 (P1-04 물류·공급망 / P1-02 거시)
> 유채유는 **EU 바이오디젤의 주원료**이자 식용 대체재입니다. EU RED III 및 2026년 **EU 대두기반
> 바이오연료 단계적 폐지** 발표로 유채유↔대두유 수요 전환이 가속됩니다. 캐나다 캐놀라는 북미
> 대체 공급원으로 미국 SBO와 직접 경쟁합니다.

### 데이터·수집 방법
| 지표 | 소스 | 권위 | 적시성 | 비용 |
|---|---|---|---|---|
| 글로벌 유채유 가격(월) | **FRED `PROILUSDM`** (IMF Rapeseed Oil) | ★★★ (IMF) | 월별 | **무료(등록 키)** |
| MATIF 유채씨 선물(일) | Euronext (Rapeseed, EUR/톤) | ★★★ | 일별 | 유료 (Euronext/Refinitiv) |
| ICE 캐놀라 선물(일) | ICE Futures (Winnipeg, CAD/톤) | ★★★ | 일별 | 유료 / yfinance 제한적 |

- **등록 API로 수집 가능**: ✅ **월별 무료** (FRED `PROILUSDM`) — 오늘 즉시 가능.
  일별 선물(MATIF/ICE)은 유료. → **무료 월별 우선 착수**.

---

## 5. 긴급도 4순위 🟠 — 해바라기유 (Sunflower, 대체재·지정학 핵심)

### 근거 (P1-02 지정학)
> 해바라기유는 **흑해(우크라이나·러시아)가 세계 수출의 약 60%** 를 차지하는 **지정학 최민감
> 유지류** 입니다. 2022년 러-우 전쟁 시 해바라기유 수출 중단 → SBO 대체 수요 급증 → CBOT BO=F
> 역대 최고가(2022-03, 77¢/lb)의 직접 원인이었습니다. 흑해 리스크의 **가격 전이 경로를 정량화**
> 하려면 해바라기유 가격이 필수입니다.

### 데이터·수집 방법
| 지표 | 소스 | 권위 | 적시성 | 비용 |
|---|---|---|---|---|
| 글로벌 해바라기유 가격(월) | **FRED `PSUNOUSDM`** (IMF Sunflower Oil) | ★★★ (IMF) | 월별 | **무료(등록 키)** |
| 흑해 FOB 해바라기유(주) | **APK-Inform** (우크라이나) | ★★★ (지역 권위) | 주별 | 유료(구독) |
| FOB/CIF 평가가(일) | S&P Global Platts / Fastmarkets | ★★★ | 일별 | 유료(고가) |

- **등록 API로 수집 가능**: ✅ **월별 무료** (FRED `PSUNOUSDM`) — 오늘 즉시 가능.
  일·주별 FOB는 유료. → **무료 월별 + 비정형(Perplexity 뉴스) 보강** 권장.

---

## 6. 긴급도 5·6순위 🟡🟢 — 캐놀라 선물 / 라우릭유

- **ICE 캐놀라(5순위)**: 북미 한정 영향. yfinance 커버리지 불안정 → Nasdaq Data Link 또는
  월별 FRED 유채유로 대체 가능. **별도 유료 도입 우선순위 낮음**.
- **라우릭유 — 팜핵유(PKO)·코코넛유(6순위)**: 식품·화장품 틈새 대체재. SBO 가격 영향 미미.
  필요 시 FRED 코코넛유 월별(`PCOCOUSDM` 계열) 무료 수집으로 충분.

---

## 7. 등록 API 가용성 종합 (요청 1번 답변)

### 7.1 현재 등록된 API로 **즉시 무료 수집 가능**
| 데이터 | 등록 API/키 | 비용 | 갱신 |
|---|---|---|---|
| 대두박 `ZM=F`·대두 `ZS=F` 일별 | yfinance (키 불요) | 무료 | 일별 |
| 팜유 월별 `PPOILUSDM` | `FRED_API_KEY` | 무료 | 월별 |
| 유채유 월별 `PROILUSDM` | `FRED_API_KEY` | 무료 | 월별 |
| 해바라기유 월별 `PSUNOUSDM` | `FRED_API_KEY` | 무료 | 월별 |
| 대두유 월별 `PSOILUSDM` | `FRED_API_KEY` | 무료 | 월별 |

> **즉시 실행 항목(C-03)**: `commodity_connector.py` 에 위 5종을 추가하면 신규 비용·키 없이
> 대체재(월별)·보완재(일별) 축을 모두 확보. **이번 백필 사이클에 포함 권장**.

### 7.2 등록되어 있으나 **유료 티어 필요**
| 데이터 | 등록 키 | 제약 |
|---|---|---|
| CPO/유채/해바라기 **일별 스팟** | `TRADING_ECONOMICS_API_KEY` | 무료 티어는 샘플 국가·지연 데이터만 → 실사용 유료 |
| CME 연속 선물(CHRIS) | `NASDAQ_DATALINK_API_KEY` | 다수 선물 데이터셋 유료 전환·일부 중단 |

### 7.3 등록 API 불가 → **신규 유료 소스 필요**
| 데이터 | 권장 소스 | 비용(개략) | 근거 |
|---|---|---|---|
| Bursa FCPO 일별 | Bursa Station / Refinitiv | 25 USD~/월+ | 팜유 글로벌 기준가, 일별 정밀 스프레드 |
| 흑해 해바라기유 FOB 주별 | APK-Inform | 구독(견적) | 흑해 수출가 지역 권위 |
| 유지류 FOB/CIF 일별 평가가 | S&P Global Platts·Fastmarkets | 고가(엔터프라이즈) | 무역 결제 기준가 |

---

## 8. 권고 실행 순서 (C-01 종합)

1. **즉시(이번 백필)**: FRED 4종(팜·유채·해바라기·대두유 월별) + yfinance `ZM=F`·`ZS=F` 일별 추가
   → 파생 지표 `SBO_CRUSH_SPREAD`·`SBO_OIL_SHARE`·월별 대체재 스프레드 생성. **무료**.
2. **단기(예산 게이트 후)**: CPO 일별(Bursa) 유료 도입 — G2 가격 밴드 정밀도 요구 확인 시.
3. **상시**: 해바라기유·유채유 **일별 부재 구간은 비정형(Perplexity 뉴스)** 으로 보강
   (§참조: `unstructured_data_collection_registry_2026_06_22.md`).

---

## 참고 소스 (권위·적시성)

- [Global price of Soybeans Oil (PSOILUSDM) — FRED/IMF](https://fred.stlouisfed.org/series/PSOILUSDM)
- [Global price of Sunflower Oil (PSUNOUSDM) — FRED/IMF](https://fred.stlouisfed.org/series/PSUNOUSDM)
- [Global price of Rapeseed Oil (PROILUSDM) — FRED/IMF](https://fred.stlouisfed.org/series/PROILUSDM)
- [Soybean Meal Futures (ZM=F) — Yahoo Finance](https://finance.yahoo.com/quote/ZM=F/)
- [Soybean Futures (ZS=F) — Yahoo Finance](https://finance.yahoo.com/quote/ZS=F/futures/)
- [IMF Primary Commodity Prices (monthly table)](https://www.imf.org/-/media/files/research/commodityprices/monthly/table3.pdf)

*최종 업데이트: 2026-06-22 · Session 29*
