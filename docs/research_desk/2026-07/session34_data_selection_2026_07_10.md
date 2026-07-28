# Session 34 — 데이터 선별·HS코드·해상도 종합 (C-02·C-03·P1-01~04)

**작성일**: 2026-07-10 · **스코프**: 2010~2026 15개년 확장 반영  
**대상 요청**: Dataset2(Daily 여부) · Req2(PSD/WASDE 선별) · Req3(HS코드) · Req2-1(NASA 2026) · Req4(결측·중복)

---

## 1. USDA PSD — 필요 원료·속성 선별 (Req 2.1)

### 1.1 원료(Raw Material) 선별
| 그룹 | ✅ 선택 | 근거 | 제외 |
|---|---|---|---|
| **Oil** | Soybean · Palm · Palm Kernel · Rapeseed · Sunflowerseed · Cottonseed | SBO(타깃) + 대체 식용유 5종(스프레드·수요전환) | Coconut·Olive·Peanut(SBO 연관 미미) |
| **Meal** | Soybean · Rapeseed · Sunflowerseed | 크러시 연산물(대두박=압착 경제성) | Palm Kernel·Peanut |
| **Oilseed** | Soybean · Rapeseed · Sunflowerseed · Palm Kernel | 업스트림 원료·압착 | Copra·Cottonseed |

### 1.2 속성(Attribute) 선별
| ✅ 선택 | 의미 | SBO 신호 |
|---|---|---|
| Production · Crush | 생산·압착량 | 공급 직접 |
| Beginning/Ending Stocks | 재고 | **STU(재고사용비율) 산출** — D-015 핵심 |
| Exports · Imports | 무역 | 글로벌 흐름·한국 조달 |
| Domestic Consumption · Food Use Dom. Cons. | 내수·식용 | 수요 축 |
| **Industrial Dom. Cons. · SME** | 산업용·대두메틸에스터 | **바이오디젤 수요**(핵심 채널) |
| Total Supply · Total Distribution | 수급 총량 | 밸런스 |
- **제외**: Extr. Rate(추출률·부차), Feed Waste(비관련).

---

## 2. USDA WASDE — 필요 품목·속성 선별 (Req 2.2)

### 2.1 품목(Commodity)
| ✅ 선택 | 근거 |
|---|---|
| Oil, Soybean · Soybean Oil | 타깃 |
| Oilseed, Soybean · Soybean | 업스트림 |
| Meal, Soybean · Soybean Meal | 크러시 연산물 |
| Vegetable Oils · Oilseeds · Oilmeals | 식용유 복합체 총량 |
| Corn | 에탄올·사료 경쟁(간접) |
- **제외**: 축산(Beef·Pork·Broiler·Eggs·Milk·Cheese 등), Rice·Sugar·Cotton(SBO 직접성 낮음), Wheat(보조만).

### 2.2 속성(Attribute)
| ✅ 선택 | SBO 신호 |
|---|---|
| Production · Yield · Area Harvested/Planted | 공급·작황 |
| Beginning/Ending Stocks · Ending Stocks Total | **STU** |
| Crushings · Domestic Crush | 압착 → SBO 공급 |
| Exports · Imports · Trade | 무역 |
| Domestic Use · Total Use · Total Supply | 수급 밸런스 |
| Avg. Farm Price (+High/Low) | 가격 앵커 |
| **For Methyl Ester · Ethanol for Fuel · Food Seed & Industrial** | **바이오연료 수요** |
- **제외**: CCC Inventory·Outstanding Loans·Free Stocks(정책재고 부차), Rough/Milled(쌀 전용).

---

## 3. HS코드 — 대체재·보완재 추가 필요 (Req 3)

**확보(대두유)**: 1507.10(.1000 조유/.2000 바이오디젤용), 1507.90(.1010 정제식품/.1020 바이오디젤용).

### 3.1 추가 필요 — 대체재(타 식용유)
| 품목 | HS코드 | 근거 |
|---|---|---|
| 팜유 | **1511**(.10 조유·.90 정제) | CPO-SBO 스프레드 1순위 |
| 해바라기유 | **1512.11/.19** | 흑해 지정학 대체 수요 |
| 유채/카놀라유 | **1514.11/.19** | EU 바이오디젤·식용 대체 |
| 팜핵유 | **1513.21/.29** | 라우릭유 대체 |
| 코코넛유 | **1513.11/.19** | 라우릭유(부차) |
| 면실유 | **1512.21/.29** | 부차 대체 |

### 3.2 추가 필요 — 보완재·업스트림·연관
| 품목 | HS코드 | 근거 |
|---|---|---|
| 대두(원두) | **1201**(.10 종자·.90 기타) | 압착 업스트림 |
| 대두박/유박 | **2304** | 크러시 연산물(마진) |
| 바이오디젤 | **3826** | SBO 산업수요 직접 |
| 글리세롤 | **1520** | 바이오디젤 부산물 |

> **권고(C-02·C-03·P1-01~04)**: 3.1의 **팜·해바라기·유채(1511·1512.1·1514)** + 3.2의 **대두·대두박
> (1201·2304)** 을 1순위 추가. 관세청 GW로 한국 수입 물량·CIF 확보 시 대체탄력성 정량화.

---

## 4. Daily vs Monthly 해상도 — G1 관점 재평가 (Dataset 2, C-02·P1-03)

**결론: G1(변수 중요도)에는 Monthly로 충분. Daily는 G2(변동성) 전용.**

| 관점 | 판단 |
|---|---|
| G1 목적 | 대두유 수급·가격 **핵심 변수 식별**(상관·Granger·중요도) — 구조적 관계 |
| 대다수 드라이버 주기 | WASDE·PSD·ENSO·정책·수입통계 = **월별** → Daily로 내려도 상위 지표가 월별이라 정보 증가 미미 |
| 기상(NASA) | 열스트레스일수 등 Daily 파생은 유용하나 **월별로 집계**되어 G1 투입 → Monthly 대표값으로 충분 |
| Daily 실익 | GARCH·VMD·가격밴드(G2), 단기 충격 탐지 → **G2에서 도입** |
| 비용 | Daily는 행수 20~30배 → 저장·연산 부담, G1 해석력 향상 근거 약함 |

→ **G1은 Monthly 확정**. Daily 데이터셋은 **G2 착수 시** 선별 도입(우선순위: CBOT SBO·CPO·BDI 일별).

---

## 5. NASA POWER 2026 — 수집 방법 무료/유료 (Req 2-1, C-02·P1-03)

| 방법 | 비용 | 커버리지 | 권장 |
|---|---|---|---|
| **NASA POWER API**(community=AG, monthly) | **무료·키 불필요** | 1981~현재(1~3개월 잠정 지연) | ★★★ **채택** |
| `production_connector.py::fetch_nasa_power_agromet`(A-065) | 무료 | 동일 좌표·9파라미터 | 자동 보충 |
| 상용 기상(DTN·Meteoblue) | 유료 | 실시간·고해상 | 불필요 |

- **결론**: 2026은 **무료 API로 자동 보충** — 수동 업로드 불필요. 최근월 `provisional=true` 플래그,
  최종 확정 시 교체. 매월 초 갱신(파이프라인 재개 후).

---

## 6. 결측·중복 교차검증 (Req 4)

### 6.1 중복 점검 — 이상 없음
| 데이터 | 기존 | 신규 | 중복 |
|---|---|---|---|
| NASA POWER | 2017~2025(삭제됨) | 2010~2025 | ❌ 없음(교체) |
| TE | 2017~2026(삭제됨) | 2010~2026 | ❌ 없음(교체) |
| WASDE | 2017~2025(17~25년) | 2010~2016 + 2026 | ❌ 연속(10~26 무겹침) |
| ICE | 2017~2026 | 2010~2016 | ❌ 연속 |
| FAO AMIS | 2017~(94) | 2012~2016(43) | ⚠️ **2017 경계 확인 필요** |

### 6.2 결측·미확보
| 항목 | 상태 | 조치 |
|---|---|---|
| 관세청 GW(2010~2026) | 업로드 예정 | 폴더 생성 완료, 파서 대기 |
| CPO_SBO_SPREAD | 미산출 | BO=F(commodity_connector) + TE Palm 파생 |
| 2026 NASA/일부 실시간 | 잠정 | API 자동 보충 |
| WASDE 신규(Korean 취합본) | 파서 검증 필요 | 리포트별 시트 포맷 → ingest_wasde_xlsx 재검증 |

---

## 7. 확정 요청
1. PSD/WASDE 선별(§1·§2) 승인 → 파서가 해당 원료·속성만 추출.
2. HS코드 1순위(팜·해바라기·유채·대두·대두박) 추가 승인.
3. G1=Monthly / Daily는 G2 유예 — 확정.
4. NASA 2026 무료 API 자동보충 확정.
5. WASDE 신규 취합본(Korean·리포트별 시트) 파서 재검증 착수 승인.
