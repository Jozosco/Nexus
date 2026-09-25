# 유지류 시장구조 최신 자료 수집·핵심 추출 — 온톨로지 반영 (2026-09-25)

> 승인자 지시(9/25): 유지류 전체 시장(대두유 포함)과 대두유 유통·가공 기업 구조에 관한 **최신 보도자료·학술·연구자료**를 수집해 핵심만 추출하고 온톨로지에 반영한다.
> 방법: 조사 에이전트 3기(공식 통계·기업 공시·학술/전문매체) 병렬 웹 조사 → 적대 검증 에이전트 3기가 핵심 주장을 독립 재검색으로 반박 시도 → 통과분만 반영.
> **접근 제약(전 항목 공통)**: 원문 페이지 열람이 네트워크에서 차단돼 모든 수치는 **검색 엔진 발췌문**에서 확보했다. 라벨 CONFIRMED는 "서로 다른 출처 2곳 이상의 발췌문이 같은 수치를 인용"을 뜻하며, 쪽·표 위치(locator)는 대부분 미확인이다. 원문 대조는 후속 과제다.
> 판독 규율: 용량≠처리량 · 발표≠완공 · 매출 비중≠선적 비중 · 부분연도≠연간 · 회계연도≠역년 · 보고서 회차(vintage) 혼용 금지 · 확정 고시≠행정예고. 4-라벨: CONFIRMED / INFERENCE / DATA GAP / NOT COMPARABLE.
> 원자료: 조사 원문 3건·검증 원문 3건은 세션 작업 폴더에 보관(저장소 미반입 — 발췌문 기반 초안이므로).

## 0. 한눈 요약

| 축 | 핵심 변화(2026-06~09) | 온톨로지 반영 |
|---|---|---|
| 압착·정제 자산 | 미국(ADM 4곳 +70만 t/yr·CHS 8,000만 bu·Incobrasa 준공)·브라질(COFCO 4,500→10,000 t/day)·아르헨티나(LDC Bahía Blanca 4,000 t/day)·베트남(VAL 7,800 t/day)·캐나다(Cargill Regina 1 Mt/yr)에서 **동시 증설** — 전부 설계 능력 | `ontology.yaml` concentration.midstream_capacity_moves_2026 · 기업 엔티티 `disclosures_2026_09` |
| 기업 실적 귀속 | ADM·Bunge 2분기 압착 마진 급등의 귀속이 **RVO·45Z·에너지 가격**으로 공시됨 | CE-022 evidence · CE-020(검증 ③ 후) |
| 아르헨티나 수출세 | Decreto 423/2026(관보 2026-06-03): 대두 24→15%(2028-12), 대두유·박 22.5→14%(2028-12) | CE-003 evidence 정정(구 '비례 인하'→종착 수치) |
| 한국 | GMO 완전표시제 식용유지류는 **확정 2027-12-31**, 2026-12-31 조기안은 행정예고 단계 · CJ제일제당 1H26 대두 매입 4,354억원(단일 매체) | TERM-161 · 정책 캘린더 발표일/시행일 분리 |
| 공식 통계·학술 | 검증 ①·③ 진행 중 — 통과분은 §3·§4에 추기 | (대기) |

## 1. 검증 결과 요약 — 기업 공시(검증 ②, 12개 주장)

| 판정 | 건수 | 내용 |
|---|---|---|
| 확인 | 7 | ADM 2Q26·ADM 증설·Bunge 2Q26·Bunge→COFCO 제당소·LDC 1H26/Bahía Blanca/Ponta Grossa·Wilmar 1H26/VAL·CHS Evansville |
| 정정 | 3 | Cargill Regina 투자액 **C$350M**(US$ 아님) · 아르헨티나 유·박 **22.5%→14%(2028-12)** 종착 수치 · 한국 GMO 완전표시제 **식용유지류 확정 2027-12-31**(2026-12-31은 행정예고) |
| 부분 확인 | 2 | COFCO Rondonópolis(출처가 시청 발표·회사 공시 미확인) · Incobrasa 능력(신공장 단독인지 부지 합계인지 출처 충돌 → INFERENCE) |

규율 위반 의심으로 걸러진 항목(반영 시 정정 적용): 보도된 '연 135만 t 가공'을 능력으로 재해석(COFCO) · 기사일과 사건일 혼동(LDC Ponta Grossa 8/17→인수 8/1·생산 8/3) · 2차 헤드라인 수치(CHS +60% → 회사 표현 '3분의 2 이상') · 콜 발언을 보도자료 본문으로 표기(ADM 45Z) · 단일 매체 2차 인용(CJ제일제당 → '확인 대기').

## 2. 기업 공시·보도 — 반영 사실(검증 통과분)

| 기업 | 사실(기간·단위) | 라벨 | 반영 위치 |
|---|---|---|---|
| ADM | 2Q26(2026-08-04): AS&O 영업이익 US$867M(+129%) · 압착 US$363M(전년 33M) · 조정 EPS 가이던스 5.15~5.60 · 45Z 기대 약 US$250M(콜) · 2026-07-30 압착 증설 4곳 +700,000 t/yr(완공 2028~29, 능력) | CONFIRMED | TERM-153 · CE-022 · capacity_moves |
| Bunge | 2Q26(2026-07-29): Softseed P&R 조정 EBIT US$255M(전년 14M) · Viterra 시너지 목표 350M · 가이던스 9.25~9.75 · 부문 4개 재편 · 2026-09-01 브라질 제당소 2곳 COFCO 매각 합의(pending) · Vicentin US$50M 신용 법원 승인(2026-09-16) | CONFIRMED | TERM-154 · capacity_moves |
| Cargill | FY2026(6~5월) 매출 US$164B · 조정 영업이익 ≈US$3.8B(+10%) · Regina 카놀라 1 Mt/yr 가동(2026-04-21, C$350M) · Nantong 약 US$500M 착공(2025-09-12) · 조직 5→3 | CONFIRMED(회계연도 — 분기와 NOT COMPARABLE) | TERM-155 · capacity_moves |
| LDC | 1H26 매출 US$26.8B · EBITDA US$1.036B · Bahía Blanca 4,000 t/day US$400M(2026-06-08 발표) · Ponta Grossa → 협동조합 7사 JV(2026-08-01 인수·08-03 생산) | CONFIRMED | TERM-156 · capacity_moves |
| COFCO International | Rondonópolis 4,500→10,000 t/day, R$20억, 완공 2028초 — **시청 발표(2026-04-14)** 기준 · DCF 조달 99%+ · Timbúes 2.3 Mt/yr(능력) | CONFIRMED-정부발표 | TERM-157 · capacity_moves |
| Wilmar | 1H26(2026-08-12): 핵심 순이익 US$641.5M(+9.9%) · 유지종자·곡물 판매량 14.9 Mt(+6.1%, 중국 사료 수요) · Feed&Industrial 세전 US$591M(+54.9%) · 인니 압수 팜 농장 2.37 Mha Agrinas 이관(2026-05-13) | CONFIRMED | TERM-158 |
| CHS | Evansville WI US$700M 압착소 발표(2026-09-14) — 80M bu/yr 설계, 완공 2028 가을 | CONFIRMED · announced | TERM-159 · capacity_moves |
| VAL(Bunge×Wilmar) | Phu My 제2라인 준공 2025-12-10 → 합계 7,800 t/day(능력) · 2026 가동률·對韓 수출 DATA GAP | CONFIRMED | TERM-160 · capacity_moves |
| Incobrasa · Bartlett×Shell Rock | US$250M 신공장 준공(2026-06-22, 부지 합계 약 100M bu — INFERENCE) · 압착 사업 결합(2026-06-18, 완료 2027-01) | CONFIRMED / INFERENCE | capacity_moves |
| 아르헨티나 정책 | Decreto 423/2026(관보 2026-06-03·발효 06-05): 대두 24→21%(2027-12)→15%(2028-12) · 대두유·박 22.5→14%(2028-12) · 대체유 바이오디젤 0% | CONFIRMED | CE-003 evidence · 정책 캘린더 2027-01-01 |
| 한국 | CJ제일제당 1H26 대두 매입 4,354억원(뉴스핌 단일 매체 — 확인 대기) · GMO 완전표시제 간장 2026-12-31 확정·당류·식용유지류 2027-12-31 확정(2026-12-31 조기안 행정예고) · 사조대림 B2C 유지류 3% 인하(2026-04) | 확인 대기 / CONFIRMED | TERM-161 · TERM-162 |

DATA GAP(기업 축): ADM Decatur East·2026-09 8-K, Bunge Destrehan JV 가동 여부·Tropical Oils EBIT, Cargill 순이익·Nantong 능력, LDC 순이익, COFCO 2025 물량, Wilmar 2Q 단독·VAL 2026 실적, 한국 4사 반기보고서 원문(DART), 2026 대두유 수입 원산지 보도, 국내 바이오디젤 혼합률 고시.

## 3. 공식 통계·전망 — 검증 ① 통과분

(검증 진행 중 — 통과 후 추기)

## 4. 학술·전문매체 — 검증 ③ 통과분

(검증 진행 중 — 통과 후 추기)

## 5. 온톨로지 반영 내역

| 파일 | 변경 | 검증 |
|---|---|---|
| `src/semantic/entities.yaml` | TERM-153~163(ADM·Bunge·Cargill·LDC·COFCO·Wilmar·CHS·VAL·CJ제일제당·사조대림)에 `disclosures_2026_09` 추가(라벨·출처 성격·규율 주석 병기) | `validate_semantic_layer.py --strict` 통과 |
| `src/semantic/ontology.yaml` | concentration.`midstream_capacity_moves_2026`(11건 · 능력·상태 분리 · 브라질/미국 능력 전망) · CE-022 evidence(기업 측 실증) · CE-003 evidence(Decreto 423/2026 종착 수치 정정) | 동일 |

## 6. 지원·승인 필요

- 원문 대조: 회사 IR·SEC·DART·USDA·FAO 원문 도메인이 실행 환경에서 차단됨 — 파이프라인 필요분은 아웃바운드 허용 목록 신청 대상(별도 판정).
- 관세청 HS 1507 2026-01~08 원산지별 월별 실측만이 한국 채널 정량의 유일 원천 — 파이프라인 실측으로 대체(외부 보도 보강 불가).
