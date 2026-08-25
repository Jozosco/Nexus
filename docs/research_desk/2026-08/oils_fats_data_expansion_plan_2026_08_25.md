기존 자산 파악을 마쳤습니다. 세 관점의 의견과 C-01 종합 계획서를 반환합니다.

---

# 유지류(Oils & Fats) 시장 구조 데이터 확충 계획 — 에이전트 합동 검토 (2026-08-25)

**작성**: C-01 종합 (P1-01·P1-04·C-03 순차 의견 청취) · **조정자 지시**: 유지류 전반 시장 구조 추가 데이터 수집 계획 수립

## 0. 기존 자산 실측 (중복 수집 방지 기준선)

| 축 | 이미 보유 | 출처 확인 |
|---|---|---|
| 가격(대체유) | **팜유(Bursa FCPO MYR)·해바라기유(인도 INR)·유채(Euronext EUR)·카놀라(ICE CAD) 15개년 일별** + TE CPO 실시간 + FRED PPOILUSDM 월별 | `data/raw/Trading Economics/Markets/Commodities/` 28파일 · `te_connector.py` |
| 무역(한국) | 관세청 16 HS(대체 11·보완 3) 6단위 + **10단위 확장 계획 확정**(대두유 6코드·품목별 권장국) + Comtrade 폴백 | `customs_substitute_scope_2026_08_13.md` · `hs_code_classification_2026_08_25.md` |
| 수급(세계) | PSD **대두유 단일**(2222000) — 단, 벌크 CSV 폴백(psd_oilseeds_csv.zip)은 전 유지류 포함·필터로 대두만 남김 · FAO AMIS **식물성유지 합산** 지수·수급 · FAS WMT 최신호 1건(수동) | `wasde_connector.py:34,272` |
| 기업 구조 | 시장구조 브리프 + 7사 폴더(ADM·Bunge·Cargill·LDC·COFCO·Wilmar·한국) + Cargill 연차 9건 | `Market Structure (…)/README.md` |
| 비정형 | farmdoc·OFI·World Grain 등 RSS 9종 일별 + GAIN/FAO 코퍼스 2,226건 | egress v2.3 (47호스트) |
| 유료 대기 | DQ-1(Platts/Fastmarkets basis) · DQ-2(Baltic BCAA) | `decision_queue.md` |

---

## 1. P1-01 (시장 분석) 관점

**① 실질 갭**: 가격 축은 사실상 충족(위 표) — 진짜 갭은 **대체유별 수급(생산·압착·재고) 분해**다. FAO AMIS는 유지류 *합산*이라 "팜 재고 급감 + 유채 풍작"이 상쇄돼 보이지 않는다. farmdoc이 실증한 **2020년 이후 SBO–팜유 공행성 붕괴**(A-201, CE-015 해석 규칙) 이후로는 유종별 수급 없이 스프레드 레짐을 판별할 수 없다. 특히 ⓐ **팜유 재고(말레이시아 MPOB 월간)** — 세계 유지 가격의 단기 앵커인데 전무, ⓑ **해바라기유는 인도 내수 INR 시계열뿐**(흑해 FOB 아님 — TERM-057 흑해 경로 판별에 부적합), ⓒ 인도(세계 최대 수입국) 수입 수요 신호 부재.

**② 무료 소스**:
- **USDA FAS PSD 타 유종 확장** — 이미 쓰는 벌크 CSV(키 불요)에서 필터만 완화(팜·해바라기·유채·팜핵·코코넛 + 각 유지작물/박). 신규 호스트 0, 생산·압착·수출입·기말재고 전 속성, 월별 갱신. **최소 비용 최대 효과**.
- **USDA FAS WMT(Oilseeds: World Markets and Trade) 월간 정기화** — B-1에서 1회 수동 회수한 것을 `fetch_reference_docs` 패턴으로 월간 자동화(WASDE 발표일 연동). 유종별 가격표·수급 코멘터리 — 호스트 기존(apps.fas.usda.gov).
- **MPOB 월간 통계**(bepi.mpob.gov.my) — 팜 생산·재고·수출, 매월 10일경 공표. 신규 호스트·신규 커넥터.
- **FRED IMF 벤치마크 시리즈 추가**(PSUNOUSDM 해바라기유·PROILUSDM 유채유 등) — 기존 economic_connector에 시리즈 ID 추가만. ⚠️ 시리즈 실존은 첫 호출로 확정(추측 금지 원칙).

**③ 유료 갭**: 흑해 해바라기유 FOB 실측 호가는 Platts/Fastmarkets 계열 — **DQ-1에 통합**(별도 신규 구독 만들지 않음). **④ 우선순위**: PSD 필터 확장·FRED 시리즈는 이번 주(G1 무간섭 — 원자료만 추가), MPOB는 9월.

## 2. P1-04 (공급망·물류) 관점

**① 실질 갭**: 시장 "구조"의 공급망 축 — ⓐ **압착·정제 처리량 실측**: 브리프의 capacity ≠ throughput 규율(D-047)대로, 설비 목록은 있으나 가동 실측이 없다. 미국은 **NASS Fats & Oils 월간 압착·유지 재고**(NOPA 대체 공적 통계)가 QuickStats API로 열람 가능 — **기존 호스트**(quickstats.nass.usda.gov)에서 쿼리 확장만 하면 된다(대두 외 카놀라·해바라기 압착 포함). ⓑ **EU 유채 축**: Eurostat(생산·압착·교역)와 JRC MARS 작황 회보 — 신규 호스트 2종. ⓒ **인니 바이오디젤 의무혼합(B40/B50) 이행 실적**: GAPKI/Kemendag는 API 부재 — Perplexity 프록시 + policy_calendar(C4 차별화 과제)로 흡수, 신규 수집 불요. ⓓ 운임: BCAA 실측은 **DQ-2 유지**(신규 없음).

**② 소스**: NASS(기존 호스트·주기 월별) · Eurostat API(ec.europa.eu — JSON, 무료·키 불요) · JRC MARS 회보(PDF 월간 — FAO AMIS와 동일한 비정형 요약 파이프라인 재사용). **③ 유료**: 신규 없음(DQ-2로 충분). **④ 우선순위 + 경고 1건**: **egress 제출이 8/29 하드**(DQ-7) — 9월에 쓸 신규 호스트(MPOB·Eurostat·JRC)를 지금 v2.4에 선등재하지 않으면 11월 통합 후 차단된다(A-069 실증 패턴). **수집 코드보다 allowlist 등재가 선행**되어야 한다.

## 3. C-03 (정량 데이터 과학) 관점

**① 실질 갭 판정 — 모델 관점의 엄격한 기준**: 현재 mart 1,463지표·표본 4,023행에서 병목은 변수 수가 아니라 **유효 신호 밀도**다. 따라서 ⓐ 유종별 *재고/STU*(MPOB 재고·PSD 유종별 STU)는 레짐 판별력이 있어 **찬성**, ⓑ 가격 시계열 추가는 이미 보유분과 공선성만 키우므로 **FRED 월별 2종 외 반대**, ⓒ **CFTC COT 포지셔닝**(D-002 이래 미구현 갭)은 시장 구조의 "포지션" 축으로 G3 레짐에 유용 — cftc.gov 공개 CSV 주간, 무료. **② 피처화 규율(M-014 재확인)**: 원자료는 전량 수집하되 G1 투입은 **스프레드·상대가격·STU 파생 선별**(SBO−CPO 기존 + SBO−SUN·SBO−RSO 월별, 팜 재고 z-score) — D-014 5단계 게이트 통과분만. **③ as-of**: MPOB(매월 10일 공표)·NASS Fats & Oils(익월 1일)·PSD 타 유종은 `asof.py` RELEASE_RULES에 규칙 추가 필수(D-023) — 커넥터 작성과 동일 PR에서. **④ 우선순위**: G1 8/31 전 신규 변수 투입 금지(산출 수치 변경 동결 원칙 D-026 J-4와 정합) — 이번 주는 *수집만*, 피처 승격은 9월 G2 체계에서.

---

## 4. C-01 종합 — 수집 계획 확정안

### 1순위 — 이번 주(~8/29) · 무료 · 기존 파이프라인 확장

| 데이터 | 소스 | 방법 | 공수 | egress 추가 |
|---|---|---|---|---|
| 유종별 세계 수급(팜·해바라기·유채·팜핵·코코넛 + 유지작물·박 — 생산·압착·수출입·기말재고) | USDA PSD 벌크 CSV(키 불요) | **기존 확장** — `wasde_connector.py:267` 필터 완화 + 유종별 지표코드·STU 파생 | 0.5일 | 없음 |
| 해바라기유·유채유 국제 벤치마크(월별) | FRED IMF 시리즈(PSUNO·PROIL 계열 — 첫 호출로 실존 확정) | **기존 확장** — economic_connector 시리즈 추가 | 0.5일 | 없음 |
| 미국 월간 압착·유지 재고 실측(대두+카놀라·해바라기) | USDA NASS Fats & Oils (QuickStats API) | **기존 확장** — production_connector 쿼리 추가 | 1일 | 없음 |
| CFTC COT 포지셔닝(ZL 등 주간) | cftc.gov 공개 CSV | 신규 소형(D-002 갭 해소) | 1일 | **cftc.gov — 8/29 v2.4에 포함** |
| **egress v2.4 선등재** | MPOB·Eurostat·JRC·CFTC 4~5호스트 | allowlist 갱신 → **8/29 제출분에 포함**(DQ-7) | 0.5일 | 본 항목 자체 |
| 전 신규 소스 as-of 규칙 | — | `asof.py` RELEASE_RULES 추가(수집 PR 동봉) | 포함 | — |

> 원칙: 이번 주 작업은 **원자료 수집·등재까지만** — G1 8/31 산출에는 미투입(변경 동결 D-026 J-4).

### 2순위 — 9월(G2 Preview 9/10 이후 편입) · 신규 커넥터

| 데이터 | 소스 | 방법 | 공수 | egress |
|---|---|---|---|---|
| 팜유 생산·**재고**·수출 월간(세계 단기 앵커) | MPOB(bepi.mpob.gov.my, 매월 ~10일) | 신규 `mpob_connector.py` | 2일 | 1순위에서 선등재 |
| EU 유채 생산·압착·교역 | Eurostat API(무료·키 불요) | 신규 커넥터 | 2일 | 동상 |
| EU 작황 회보(유채·해바라기) | JRC MARS 월간 PDF | **기존 재사용** — FAO AMIS 비정형 요약 파이프라인(summarize_pdfs v2) | 1일 | 동상 |
| FAS WMT Oilseeds 월간 정기화(유종별 가격·수급 표) | fas.usda.gov(기존 호스트) | **기존 재사용** — fetch_reference_docs 월간화(WASDE 발표 연동) | 1일 | 없음 |
| 관세청 10단위 확장·누락국(VN 등 6국) 수집 | 기확정 계획 실행 | hs_code_classification §4 그대로(신규 계획 아님 — 중복 배제) | 기계획 | 없음 |
| 인니 B40/인도 수입 수요 | Perplexity 프록시 + policy_calendar(C4) | **기존 재사용** — 신규 커넥터 불요 판정 | 0 | 없음 |
| 피처 승격(선별) | — | M-014: SBO−SUN·SBO−RSO 스프레드, 팜 재고 z-score, 유종별 STU만 D-014 게이트 통과 시 투입 | C-03 소관 | — |

### 3순위 — 유료 결정 대기 (신규 구독 없음 — 기존 DQ에 통합)

| 갭 | 통합처 | 비고 |
|---|---|---|
| 흑해 해바라기유 FOB·CFR 아시아 실측 호가 | **DQ-1**(Platts/Fastmarkets) | 견적 요청 시 "대두유 basis + 해바라기·팜 CFR" 묶음 견적으로 확장 명기 |
| 식물성유지 탱커 실측 운임 | **DQ-2**(Baltic BCAA) | 변동 없음 |
| 화물 추적(Kpler/Vortexa) | D-046 기등재 | 신규 등재 없음 |

### 낭비 방지·리스크 (조정자 보고 요점)

1. **수집 ≠ 피처화**: 원자료 전량 수집·피처는 스프레드/STU 파생 선별(M-014) — 유지류 가격 동행성으로 개별 투입 시 공선성만 증가.
2. **최대 지렛대는 PSD 벌크 필터 1줄**: 신규 호스트·키·커넥터 없이 유종별 세계 수급 전 축이 열림.
3. **시급한 단일 행동은 egress v2.4(8/29)**: 신규 호스트 4~5종 미등재 시 9월 커넥터가 11월 통합에서 전면 차단(A-069 전례). 코드보다 등재가 먼저.
4. **G1/G2 무간섭 순서**: 이번 주 수집만 → 9/10 G2 Preview 후 피처 승격 — 마일스톤 지연 요인 없음.
5. 승인 필요 사항(R-021 ③): egress v2.4 제출 승인 · DQ-1 견적 범위 확장(해바라기·팜 CFR 포함) 여부.

---

**참조 파일**: `/home/user/Nexus/docs/research_desk/2026-08/hs_code_classification_2026_08_25.md` · `/home/user/Nexus/docs/research_desk/2026-08/customs_substitute_scope_2026_08_13.md` · `/home/user/Nexus/docs/infra/egress_allowlist.yaml`(v2.3, 47호스트) · `/home/user/Nexus/docs/research_desk/decision_queue.md`(DQ-1·2·7) · `/home/user/Nexus/src/pipeline/connectors/wasde_connector.py`(PSD 필터 지점 L267) · `/home/user/Nexus/data/raw/Trading Economics/Markets/Commodities/`(대체유 가격 15개년 기보유 실측).
