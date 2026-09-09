# 온톨로지 v3.2 개정 — 시장구조 층 + 일별 데이터 바인딩

**작성일**: 2026-09-09 · **대상 파일**: `src/semantic/entities.yaml` · `src/semantic/ontology.yaml`
**검증 게이트**: `scripts/validate_semantic_layer.py --strict`

---

## 1. 한 줄 요약

공유된 시장구조 자료(ABCD 계열 트레이딩하우스·곡물/유지 집중도 논문)와 일별 수집 지표를
시맨틱 레이어에 정식 등재했다. 기업·항만·해상 병목이 이름표만 있던 상태에서 **용어 사전에
등재된 실체**로 바뀌었고, 태그가 붙지 않은 채 매일 쌓이던 일별 지표 13종이 온톨로지 태그에
전량 연결됐다.

---

## 2. 추가된 것 — 용어 사전 (`entities.yaml`)

새 분류 `market_structure_and_trade` 23종 (TERM-153 ~ TERM-175). 기존 레코드 스키마를 그대로
따르며, `status`는 저장소 문서가 사실을 명시하면 `confirmed`, 문서 서술로부터의 해석이면
`inference`로 부여했다.

| 구분 | 개수 | 용어 | 클래스 |
|---|---|---|---|
| 트레이딩하우스 | 8 | ADM · Bunge · Cargill · LDC · COFCO International · Wilmar · CHS · VAL 베트남 합작 | `TradingHouse` |
| 국내 압착·정제 | 4 | 씨제이제일제당 · 사조대림 · 롯데푸드 · 오뚜기 | `Processor` (신설) |
| 수입 양하 항만 | 2 | 평택항 · 인천항 | `Port` |
| 해상 병목 | 4 | 말라카 해협 · 수에즈 운하 · 홍해·바브엘만데브 해협 · 흑해 곡물회랑(터키 해협) | `Chokepoint` |
| 거래 개념 | 5 | CR4 · HHI · 포스파 표준계약 · 선물+베이시스/고정 · 업리버 FOB | `ConcentrationMetric` ×2, `ContractStandard`, `PricingConvention`, `PriceBenchmark` (모두 신설) |

기업 레코드에는 상류·중류·하류 역할(`role_upstream` / `role_midstream` / `role_downstream`),
본사(`hq`), 한국 관련성(`korea_relevance`), 채널 주석(`korea_channel_note`)을 부가 필드로 넣었다.
국내 4개사의 점유율은 **값 단독으로 두지 않고** `market_share_as_of: '2024-03'`와
`market_share_source`(USDA FAS GAIN KS2024-0010)를 반드시 동반한다.

**클래스 5종 신설**: 온톨로지의 `entity_types`에 `market_structure` 계보를 만들고
`Processor` · `ConcentrationMetric` · `ContractStandard` · `PricingConvention` · `PriceBenchmark`를
한 줄 설명과 함께 등록했다. 트레이딩하우스와 가공 사업자를 같은 클래스로 묶지 않은 이유는
전자가 국제 조달·수출 주체이고 후자는 국내 수요 측 주체여서 가격 해석 방향이 반대이기 때문이다.

### 흑해를 두 개로 나눈 이유

흑해는 이미 해역(`TERM-082`, `TradeRegion`)으로 등재돼 있었다. 여기에 통항 병목인
**흑해 곡물회랑(터키 해협)**을 `TERM-170`으로 따로 등재하고 `region_ref: TERM-082`로 이었다.
해역 전체의 위험지수와 통항 차단 사건은 성격이 다르므로 하나로 합치면 신호가 섞인다.

---

## 3. 추가된 것 — 공급망 층 (`ontology.yaml` `supply_chain`)

- **등재 대기 해소**: 기업 6곳·항만 2곳·해협 2곳의 `pending_entity_registration`을 전부
  `entity_term`으로 확정했다. 신규 기업 2곳(CHS · VAL 베트남 합작)도 추가했다.
- **경유지 신설**: `WP-BAB_EL_MANDEB` · `WP-BLACKSEA`.
  **설계 판단** — 바브엘만데브를 수에즈에 접지 않고 지점으로 분리하되, 두 지점에
  `corridor: red_sea`를 붙여 하나의 회랑으로 묶었다. 사건 원천(공격 지점 vs 통항 제한)은
  구분해 기록해야 하지만, 위험 신호를 집계할 때는 회랑 단위로 **1회만 계상**한다.
  이 규칙은 `corridor_note`에 명문화했다.
- **항로 보강**(공급망 관점 판정 반영):
  - 남미 2개 항로 — `alternatives: [순다 해협, 롬복 해협]`(해석 · 추가 1~3일 추정, 미검증) 및
    "말라카 혼잡·봉쇄는 차단이 아닌 지연·비용 사건"이라는 `disruption_semantics` 추가.
  - 미국 걸프 항로 — 파나마 제약 시 대안으로 `[WP-SUEZ, 희망봉 우회]` 추가(해석).
  - **`RT-CN-KR` 신설** — 중국발 정제 대두유 채널. 해협 무경유 연안 항로(해석),
    리드타임은 데이터 공백, 적출 항만은 특정 불가(`PORT-CN`은 의도적으로 등재 대기 상태로 두고
    `data_gap` 사유를 명시).
  - 운임 주석에 "중동만 청정제품선 적출 증가 → 선복 재배치 → 아시아 운임 전이"(해석) 1문장과,
    흑해 회랑은 해바라기유 경로 관측 표시까지만 허용한다는 제약을 추가했다.
- **관세청 커버리지 캐비엇 신설**(`customs_coverage_note`, 2025-08~2026-07 실측, CONFIRMED):
  조유 1507.10.1000은 세계 233,046 t 중 수집국 합 58,749 t(25.2%), 정제 1507.90.1010은
  115,095 t 중 86,757 t(75.4%). **원산지 비중을 가중치로 쓰는 합성 지수는 커버리지 비율을
  함께 표기하지 않으면 발행할 수 없다** — 특히 조유는 4분의 1만 관측된다.

### 집중도 블록 (`concentration`) 신설

| 항목 | 값 | 라벨 |
|---|---|---|
| 선적 실거래 기준 세계 CR4 | 곡물 32% · 유지 27% | CONFIRMED |
| 대두 CR4 | 45% | CONFIRMED |
| 선적 물량 1위(CNF) | COFCO International | CONFIRMED |
| 상위 7개사 핵심군 | 45% (ABCD + Viterra + COFCO + CHS) | CONFIRMED |
| HHI 판정 관례 | 5000 이상 극도 · 2500 이상 높음 · 1500 이상 보통 | CONFIRMED(관례) |
| 'ABCD 70~90%' 통설 | 매출 합산 계열 — 분모·단위 상이 | **NOT COMPARABLE** |
| 브라질 트레이딩 점유(2020) | Cargill 11.4 · Bunge 9.4 · ADM 7.8 · LDC 7.5 · COFCO 3.8% | CONFIRMED |
| 브라질 외국 다국적 통제 | 65.4% (제2 출처 교차검증 일치) | CONFIRMED |
| 팜유 말레이시아+인도네시아 수출 점유 | 21년간 80% 이상 불변 | CONFIRMED |
| 해바라기유 수출(MY2026/27) | 러시아 5,000 · 우크라이나 4,950 천 t | CONFIRMED |
| 한국 조유 수입 채널 | 아르헨 45개월·중앙 10,981 MT·CIF 1,183 / 미국 12개월·15,115 MT·1,383 / 브라질 14개월·1,326 MT·1,267 / 중국 8개월·156 MT·1,654 | CONFIRMED(물량) + INFERENCE(성격) |
| 채널별 수출 기업·계약형 | 월별 통계로 식별 불가 | **DATA GAP** |

블록에는 판독 규율 5칙(용량≠처리량 · 관세청 CIF≠CFR 호가 · 판매등록≠선적 · 부분연도≠연간 ·
월별 합계≠개별 화물)과 집중도 해석 2칙을 `interpretation_rules`로 붙였다. 핵심 해석은 다음과 같다.

> 집중도가 통설보다 낮다는 실측(CR4 27~45%)은 기업 마진층이 작다는 뜻이다. 따라서
> 도착가에서 선물가를 뺀 잔차층은 기업 마진이 아니라 **운임·보험·정책(수출세·관세)·품질·시차**로
> 귀속해 해석한다.

---

## 4. 추가된 것 — 일별 데이터 바인딩

**신규 태그 2종**

| 태그 | 감성 지표 | 연결 엔티티 | 일별 코드 |
|---|---|---|---|
| `지정학위험` | 없음(전용 aspect 미정의 — 후속 과제) | GPR지수 · 호르무즈 · 흑해 회랑 | GPR · GPR_REALTIME · GDELT_EVENT_SCORE · SEISMIC_RISK |
| `전문매체` | SBO_NEWS_SENTIMENT | 대두유 · 감성점수 | RSS 10종 |

**일별 코드 배정**: 태그가 없던 13종을 전량 배정했다 — 해협 탱커·해협 위험·운임 6종은
`물류충격`, 지정학 3종은 `지정학위험`, 기상 2종은 `기상이변`, RSS 10종은 `전문매체`.
`GPR_REALTIME`은 이전에 `물류충격`에 있었으나 GPR과 같은 지수 계열이므로 `지정학위험`으로
옮겼다(일별 코드는 한 태그에만 배정 — 브리지 중복 금지). 배정 결과는 **33종 전량 배정 ·
중복 0 · 미확인 코드 0**이다.

**정형 바인딩 확장** — 커넥터 실산출 코드 5종(ARS_USD_OFICIAL · BCTI · CPO_USD_MT ·
GPR_QUALITATIVE · ONI)을 등재했다. `ONI`에는 `alias_of: ENSO_ONI`를 명시해 같은 계열을 두 지표로
세지 않게 했다. 해상 병목 위협도 6종(호르무즈·수에즈·말라카·파나마·흑해 + 종합)은 병목 용어와
CE-013에 연결하되, 전 항목에 **"규칙 기반 파생 — 확률 아님"** 주석을 달아 사건 발생 확률로
읽히는 오용을 차단했다.

**`structured_patterns` 신설** — 지역·품목·속성 축이 접미로 붙어 개별 열거가 불가능한 계열
7종(AIS 해협 척수/위험 · 가뭄 단계×주 · 지역 작황 · 기후 변수×생산지역 · PS&D 속성 ·
대두유 속성×국가)을 `{pattern, regex, entities, note}` 형태로 계약했다. 각 항목의 주석에는
접미가 빠지면 값 충돌이 발생한다는 사실을 적어 두었다.

**인과엣지 집계 정정** — 21건/검증 10/후보 11로 적혀 있던 집계를 실측대로
**24건 / 검증 10 / 후보 14**로 고쳤다.

---

## 5. 출처와 라벨

| 출처 | 사용 내용 | 라벨 |
|---|---|---|
| `abcd_trading_structure_2026_08_15.md` §2·§3·§4b·§5 | 기업 역할, 계약·가격 관행, 국내 압착·정제 점유, 수입 채널 프로파일 | CONFIRMED(수치) · INFERENCE(채널 성격) |
| `market_structure_errata_2026_08_19.md` | Bunge–Viterra 합병 2025-07-02, Cargill 시설 수 상충 | CONFIRMED / 출처 상충 표기 |
| `Dynamics_2025_AEPP_grain_oilseed_trading_concentration.pdf` | 선적 실거래 CR4·HHI, 7개사 핵심군, 통설 해체 | CONFIRMED + NOT COMPARABLE 주석 |
| `Transparency_2021_Brazil_soy_supply_chain_accountability.pdf` | 브라질 트레이딩 점유 2020, 외국 통제 65.4% | CONFIRMED |
| `Brazil_policy_Missing_Target_foreign_investment_smallholders.pdf` | 점유율 제2 출처 교차검증 | CONFIRMED |
| `Competitiveness_drivers_soybean_exportation_supply_chain.pdf` | 브라질 물류 마이너스 동인 | CONFIRMED(대두 기준) · 대두유 전이는 INFERENCE |
| `PalmOil_2025_global_trade_complex_network.pdf` | 팜유 2개국 80% 이상 집중 | CONFIRMED |
| `Ukraine_grain_seed_trade_global_position.pdf` | 해바라기 취약점(압착·물류) | CONFIRMED |
| `China_2023_financialized_soybeans_food_regime.pdf` | 비중국행 41%, 채널 분리 해석 규율 | CONFIRMED + 해석 규율 |
| `farmdoc_2024_US_Brazil_China_soybean_triangle_20yr.pdf` | 중국 축 구조 배경 | CONFIRMED(배경) |
| 관세청 실측 2025-08~2026-07 | 커버리지 비율, 정제유 중국 99.9% | CONFIRMED |
| MEMORY 원장 A-211 | 베트남 합작 일 7,800톤·조유 연 50만 MT 겨냥 | CONFIRMED |

---

## 6. 남은 갭

| 갭 | 내용 | 성격 |
|---|---|---|
| 기업별 한국향 물량 | 관세청은 국가별까지만 분해 — 수출 기업·계약형 확정 불가 | DATA GAP(구조적) |
| Cargill 남미 시설 수 | 외부 집계 14·13 대 자사 공시 12·20 | 출처 상충(미해소) |
| 포스파 85% 분모 | 유지종자 포함 여부 원문 확인 필요 | 확인 대기 |
| 원산지별 CIF 차이 요인 | 동월 비교 부재로 정책·운임·품질 귀속 불가 | 후속 분석 |
| 중국발 정제유 리드타임 | 연안 단거리라 월별 통계로 역산 불가 | DATA GAP |
| 조유 커버리지 25.2% | 수집국 밖 물량이 4분의 3 — 원산지 가중 지수 신뢰도 제약 | 수집 확대 과제 |
| `지정학위험` 전용 감성 aspect | 정의된 지표가 없어 현재는 비워 둠 | 후속(Phase B) |
| RSS 8종 | 다이제스트 레지스트리 편입과 함께 유효 — 배정은 선행 완료 | 동시 진행 |
| 해협 대체 항로 소요일 | 순다·롬복 +1~3일은 추정치 | 미검증 |

---

## 7. 검증 결과

**개정 전** (`--strict`): 위반 0건 · 경고 6건 — 경고 중 1건은 온톨로지 태그가 붙지 않은
일별 지표 13종.

**개정 후** (`--strict`): **위반 0건 · 경고 5건.**
잔여 경고 5건은 이번 개정 범위 밖의 기존 갭이다(감성 지표의 용어 사전 연결 1건,
쿼리 템플릿과 지표 정의의 상호 커버리지 4건).
일별 신호 브리지 경고는 **해소**됐다 — 다이제스트 등록 지표 33종이 전량 태그에 배정되고,
중복 배정 0건·실존하지 않는 코드 0건이다.

```
- 모드: strict · 위반 0건 · 경고 5건
- ✅ 위반 없음
- ℹ️ 용어 175건 · 관계 60종 · 인과엣지 24건 로드
```
