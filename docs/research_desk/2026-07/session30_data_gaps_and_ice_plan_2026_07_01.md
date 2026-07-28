# Session 30 — 데이터 공백 해결·소스 확장·ICE 활용 계획 (요청 1~5 대응)

**작성일**: 2026-07-01 · **조정자 요청 기반**  
**참여**: C-03(데이터) · C-06(EDA/통계) · C-08(DQSOps) · P1-01(대두유) · P1-02(지정학) · P1-03(기후) · P1-04(공급망) · P1-05(에너지·바이오연료)  
**성격**: 요청 1·2·3·5는 방법 확정 후 **구현 승인 요청**. 요청 4는 결정 반영(소스 확장).

> ✅ 참고: 요청과 별개로 **Topic 3(리포트 문구 19종 + 제외 6종)** 는 `variable_importance_g1.py`에
> 이미 반영·검증 완료(구문·스모크 테스트 통과).

---

## 요청 1 — BDI z-score 산출 (C-03 · C-06 · C-08 협의)

### 현행 진단
`variable_importance_g1.py::_check_structural_breaks`에 **90일 롤링 z-score 계산 로직이 이미 존재**함
(원시 `BDI` → `z = (xₜ − rolling_mean) / rolling_std`, 임계 z>2σ). 문제는 **산출 안정성**:

| 이슈 | 현행 | C-06/C-08 판단 |
|---|---|---|
| 창(window) | `min(90, n)` — n<90이면 전체표본 평균/표준편차 | "90일" 의미 왜곡. 실제 trailing window 필요 |
| 최소 관측 | 5건 | z 안정성 부족(표준편차 과소·과대) |
| 이상치 | 미처리 | 단일 스파이크가 z 왜곡(MEMORY M-003 IQR 캡 미적용) |
| 신뢰도 | 표기 없음 | n에 따른 신뢰도 라벨 필요 |

### 제안 방법 (승인 시 적용)
```
1) IQR 캡(MEMORY M-003)으로 BDI 이상치 완화 후
2) rolling(window=90, min_periods=30) — 진짜 trailing 90거래일, 최소 30건
3) 표본 표준편차(ddof=1) 유지
4) 신뢰도 라벨: n≥60 '정상' · 30≤n<60 '주의(관측 부족)' · n<30 '저신뢰(계산 보류)'
5) 리포트에 z·n·신뢰도 동시 표기
```
- **C-03**: 임계 2σ는 유지. **C-06**: min_periods=30이 계절성 제거·표준편차 안정의 균형점.
  **C-08**: 신뢰도 라벨을 DQSOps 신선도와 별도 축으로 병기.
- **선결 조건**: BDI 원시 히스토리가 백필로 ≥90거래일 확보돼야 함(무료 stooq/TE 커버리지 점검 필요).

---

## 요청 2 — `GPR_NORMALIZED` 해결안 탐색

### 원인(확정)
G1은 `indicator_code == "GPR_NORMALIZED"`(임계 0.022)를 조회하나, `gpr_connector`는
`GPR`·`GPR_QUALITATIVE`·`GPR_REALTIME`만 출력 → **정규화 산출 단계 부재(네이밍 불일치)** →
상시 "데이터 미수집".

### 해결안 비교
| 옵션 | 방법 | 장점 | 단점 | 권장 |
|---|---|---|---|---|
| A | **파이프라인에 정규화 산출 추가**: 원시 GPR → 표준화 → `GPR_NORMALIZED` 저장 | 임계 0.022 스케일과 정합, 커넥터 계약 유지 | 정규화 방식 확정 필요 | ✅ **권장** |
| B | G1 임계 로직을 실제 출력명(`GPR`/`GPR_QUALITATIVE`)으로 매핑 + 인라인 정규화 | 파이프라인 무변경 | 임계 0.022 재보정 필요, G1에 로직 혼입 | 대안 |

### 정규화 방식(옵션 A 세부, C-03·P1-02)
- Caldara & Iacoviello GPR 원지수는 벤치마크 100 스케일. **0.022** 는 "정규화(비율)" 기준이므로
  → `GPR_NORMALIZED = (GPRₜ − min) / (max − min)` 또는 `GPRₜ / 100`의 스케일 확인 필요.
- **선결**: 현 `GPR` 값의 실제 스케일(0~100 지수 vs 이미 비율)을 확인해 정규화식·임계 정합화. → **승인 요청**.

---

## 요청 3 — 작황·수입·무역·수급전망: 두 접근 비교 (C-03 · P1-01~04)

**두 후보**  
(A) *realtime-skip + 패턴 매칭 수정* — 기존 커넥터/파일 패턴을 고쳐 이미 수집된 것을 인식  
(B) *NASA POWER + UN Comtrade 백필 + WASDE/PSD* — 신규 무료 소스로 히스토리 백필

| 항목 | (A) 패턴 수정 | (B) 신규 백필 | 분석목적 적합 |
|---|---|---|---|
| 작황(crop) | production 커넥터 실시간 전용 → 백필 공백 잔존 | **NASA POWER**(무료·1981~ 백필) agromet + WASDE 생산·수율 파생 | **(B)** — 9개년 연속성 필수 |
| 수입통계 | 관세청 실시간·키 의존 → 과거 공백 | **UN Comtrade**(등록 키) 월별 백필 | **(B)** — 과거 수입 단가 필요 |
| 무역통계 | GATS xlsx 이미 수집 → **패턴 매핑만 하면 인식** | 중복 | **(A)** — 이미 확보 |
| 수급전망 | WASDE/PSD xlsx 이미 수집 → **패턴 매핑만** | 중복 | **(A)** — 이미 확보 |

### 결론 (권장: 하이브리드)
- **무역·수급전망**: (A) — 이미 xlsx 수집됨. FILE_PATTERNS 매핑 확인 + `connector=all` 백필 재실행이면 충분.
- **작황·수입통계**: (B) — 9개년 히스토리 일관성이 분석 목적(G1 인과·선행성)에 직결되므로 무료 백필
  소스(NASA POWER·UN Comtrade)로 과거 구간을 메우는 것이 적합.
- **P1-01/03**: 작황은 NASA POWER 기상 + WASDE 생산 이중화가 단절 위험을 낮춤.
  **P1-04**: 수입통계는 Comtrade(글로벌) + 관세청(국내 실시간)의 역할 분리가 바람직.
- → **승인 요청**: 하이브리드(무역·수급=패턴수정 / 작황·수입=백필) 확정 여부.

---

## 요청 4 — 신뢰 소스: 기존 유지 + 권위 소스 추가 (반영)

방침대로 **기존 17개(CNN·BBC·NYT·Investopedia·Upstox 포함) 전부 유지**하고 농업·원자재
**권위 소스를 추가**함. 단, Perplexity `search_domain_filter`는 **쿼리당 도메인 상한**이 있어
17개+다수 추가는 한 번에 불가 → **카테고리별 도메인 서브셋** 방식으로 해결(각 쿼리 ≤20).

| 카테고리 | 기존 유지 | 추가(권위·적시성) | 담당 |
|---|---|---|---|
| 지정학·정책 | reuters, bloomberg, cnn, bbc, nytimes, usda.gov | ec.europa.eu, epa.gov, customs.gov.cn, theicct.org | P1-02·P1-05 |
| 기후·작황 | usda.gov, fao.org | cpc.ncep.noaa.gov, conab.gov.br, abiove.org.br, ipad.fas.usda.gov | P1-03 |
| 경제·무역 | reuters, bloomberg, spglobal, investopedia, upstox | igc.int, seaofindia.com, bcr.com.ar, comtrade.un.org | P1-01·P1-04 |
| 대체·보완재 | theice.com, euronext.com, mpob.gov.my, oilworld.de, fastmarkets, agricensus | gapki.id, mpoc.org.my, apk-inform.com, fediol.eu | P1-01 |

- **원칙**: "많이 모으고 나중에 큐레이션" — 일반지는 대량·속보 커버리지, 권위지는 정밀·1차 데이터.
  수집 후 신뢰도 스코어링으로 큐레이션(별도 단계).
- → **확정 요청**: 카테고리별 서브셋 방식 + 상기 추가 소스 승인.

---

## 요청 5 — ICE U.S./EU 선물·옵션 데이터 활용안 (C-03 · P1)

### 데이터 개요
| 폴더 | 시장 | 기초자산 | 파일 |
|---|---|---|---|
| `U.S./` | ICE Futures U.S. | Financial · Agricultural · Energy | Futures(10) + Options(10) |
| `E.U./` | ICE F&O Europe | Oil · Energy | Futures&Options(10) |

> ⚠️ **파일명 편차**: Options 파일은 `YYYY_Monthly Volume Options.xlsx`(단수 'Volume'),
> Futures는 `YYYY_Monthly Volumes Futures.xlsx`(복수). **파서는 'Volume(s)' 양쪽 허용** 필요.

### 성격 규정
ICE 데이터는 **가격이 아닌 거래량(volume)** — 즉 **유동성·시장 참여도·헤지 활동** 지표. 대두유
가격의 직접 동인이 아니라 **변동성·가격발견 활동의 선행/동행 신호**.

### 가공(C-03)
- 20+10개 xlsx → 연도·시장·기초자산(Financial/Agri/Energy·EU Oil/Energy)·상품(선물/옵션)별
  롱포맷 파싱 → `data/processed/ice_monthly_volumes.parquet` + 스키마 YAML 등록.
- **대두 복합(대두·대두유·대두박) 농산물 거래량**을 우선 선별.

### 피처 후보 (보조 변수)
| 피처 | 정의 | 가설 | 목표 |
|---|---|---|---|
| `ICE_AGRI_VOL_YOY` | 농산물 거래량 전년동월비 | 거래량 급증 → 헤지·투기 참여↑ → 변동성 선행 | G1 보조·G2 변동성 |
| `ICE_OPT_FUT_RATIO` | 옵션/선물 거래량 비율 | 옵션 비중↑ → 방향성 불확실·리스크 헤지 심리 | G2·G3 레짐 |
| `ICE_EU_OIL_ENERGY_VOL` | EU Oil/Energy 거래량 | 바이오디젤·에너지 채널 활동도 | P1-05 신호 |

### 활용 등급 (권장)
- **보조·해석 변수**로 자리매김(핵심 인과 변수 아님). G1 SHAP 상위 후보군엔 넣되, 인과 해석은
  "시장 미시구조 참여도" 프레임으로 한정. → **활용 등급(핵심 vs 보조) 확정 요청**.

---

## 확정 요청 요약

1. **요청 1**: BDI z-score 안정화 방법(IQR 캡·min_periods=30·신뢰도 라벨) 적용 승인.
2. **요청 2**: `GPR_NORMALIZED` 옵션 A(파이프라인 정규화 산출) + 정규화식 확정 승인.
3. **요청 3**: 하이브리드(무역·수급=패턴수정 / 작황·수입=NASA POWER·Comtrade 백필) 승인.
4. **요청 4**: 카테고리별 도메인 서브셋 + 권위 소스 추가 승인.
5. **요청 5**: ICE 파서(단·복수 파일명 허용) + 거래량 보조 변수 등급 확정.

*요청 1·2·3·5는 승인 후 구현. 요청 4는 스크립트 확정 시 반영. Topic 3(문구)만 선반영 완료.*
