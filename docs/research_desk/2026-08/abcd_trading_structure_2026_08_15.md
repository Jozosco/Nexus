# 유지류 생산·유통 기업 거래구조 조사 — ABCD·COFCO·Wilmar와 한국 수입 채널

**작성일**: 2026-08-15 · **주관**: C-01 (P1-01 거시정책 · P1-04 공급망 협업) · **요청**: 조정자 (2026-08-15)
**교차검증**: GPT-5.6-Sol xhigh — push 시 자동 (§8)

> **데이터 경계 (D-021·§3c)**: 조달 부서 담당자가 특정 ABCD 계열사와 실제 거래 중인 조건
> (계약 물량·가격·주기)은 **내부 정보이므로 본 저장소 어디에도 기록하지 않는다**.
> 본 문서는 공개 정보 + 외부 파이프라인 실측만 사용하며, 실거래 조건은
> `procurement_alternatives.py` §3c 방식(런타임 입력 전용·저장 금지)으로만 결합한다.

---

## 1. 조사 배경

수입사(한국 F&B)마다 물량·가격·구매 주기 선호가 다르므로, G2 운영 계층이 "현실적 대안"을
제시하려면 공급 측(ABCD 등 트레이딩 하우스)의 상류→가공→유통 구조와 표준 거래 조건을
알아야 한다. 본 문서는 ①글로벌 공급 기업 구조 ②국제 거래 관행(계약·가격·물량 단위)
③한국 수입·정제 구조 ④실측 기반 수입 채널 프로파일 ⑤4축 엔진 연계 스키마를 정리한다.

## 2. 글로벌 유지류 기업 — 상류→가공→유통 구조

| 기업 | 상류(원료 확보) | 가공(압착·정제) | 유통·수출 | 한국 관련성 |
|---|---|---|---|---|
| **ADM** (A) | 미국 중서부 원곡 집하망·엘리베이터 | 미국 압착 4개 공장 증설 중(연 2,500만 부셸 추가 — IN·MO·NE·ND), EU 압착 상위 | 미국 걸프·PNW 수출 터미널, 글로벌 트레이딩 데스크 | 미국산 조유·정제유 수출 채널 |
| **Bunge** (B) | 브라질·아르헨·미국 원곡 (농가 직구매·저장·운송 통합 모델) | 남미 압착 최대급, EU 압착 상위(스페인 3공장), Viterra 합병으로 집하망 확대 | 산투스·파라나과·Up River 수출 | 남미산 조유 주력 채널 |
| **Cargill** (C) | 미주·남미·유럽 집하망 | 미국·남미·EU 압착(스페인 1공장 포함) | 자가 물류(Cargill Ocean Transportation) | 미국·남미 양쪽 채널 |
| **LDC** (D) | 남미(아르헨 Up River 크러셔 보유)·미국 | 미국 오하이오 신설 압착: 연 150만 MT 압착·**대두유 32만 MT** 생산 능력 | 로사리오·미국 걸프 | 아르헨 조유 전통 강자 |
| **COFCO Intl** | 남미 원곡(중국 국유 수요 기반 물량) | 아르헨·브라질 압착 자산 | 중국향 최우선 + 제3국 판매 | 아르헨·중국발 조유 |
| **Wilmar** | 팜(자체 농园)+대두(중국 압착 1위권) | **아시아 최대 통합 정제망** — 압착→정제→소비자 브랜드까지 수직 통합 | 아시아 역내 유통망(중국 JV는 ADM·COFCO와 합작 연혁) | 아시아 정제유·팜 채널, 중국발 재수출 |

구조 요지: ABCD는 **원곡 집하→압착(조유+대두박)→(일부)정제→수출 터미널→트레이딩**을
수직 통합하고, 이익은 flat 가격이 아니라 **압착 마진과 basis(현물−선물)**에서 발생한다.
EU 압착 능력의 약 80%를 A·B·C 3사가 점유(2021)할 만큼 집중도가 높다. 미국 압착은
2025/26 사상 최대(26.5억 부셸 전망) — 재생디젤 수요가 증설 동인이다.

## 3. 국제 거래 관행 — 계약·가격·물량 단위

| 요소 | 표준 관행 | 근거 |
|---|---|---|
| **계약 표준** | FOSFA 표준계약 — 세계 유지·유지종자 거래의 **85%**가 FOSFA 계약 기반. CIF·C&F·FOB별, 원산지·운송수단별 계약서식 세분화 | FOSFA International |
| **가격 구조** | `가격 = CBOT ZL 선물 ± basis(포인트)`. 예: 브라질 FOB 파라나과 −1,850pt, 아르헨 FOB Up River −1,800pt (2023-07 실측 사례, 100pt=1¢/lb) | S&P Global |
| **고정(fixation)** | basis 계약 체결 후 매수자가 지정 창 안에서 CBOT 레그를 고정(buyer's call 관행). flat(일괄 확정) 계약과 병존 | 업계 관행 |
| **물량 단위** | 액체 벌크 탱커 파슬 — 한국향 실측 화물 10,000~40,000 MT급 (§5 실측) | 관세청 GW 실측 |
| **품질 사양** | 조대두유: NOPA 사양(FFA 0.75% 등 — competitive_differentiation §3b), FOSFA 품질 조항 | NOPA·FOSFA |
| **결제** | 신용장(LC) 중심, 선적서류 상환 | 업계 관행 |
| **분쟁** | FOSFA 중재 | FOSFA |

## 4. 한국 수입·정제 구조 (GAIN KS2024-0010 · 2024-03 + 관세청 실측)

- **수입 의존**: 한국 식물성유지 공급의 82%가 수입(MY22/23). 연 소비 1.5~1.6 백만 MT 중
  팜 41% · 대두유 36% · 유채유 순으로 3대 유종이 86% — **상호 대체재**로 가격 경쟁력에
  따라 점유율이 움직인다(D-031 대체재 수집·CE-015와 정합).
- **조유 수입**: 조대두유 **연 350,000~400,000 MT** 수입 — 국내 압착 능력(대두유 환산
  연 0.21 백만 MT)을 수요가 초과하며, 기존 정제 설비로 조유를 정제하는 구조.
- **압착(국내)**: CJ제일제당 2,100 MT/일 + 사조대림 1,100 MT/일 (모두 인천, 65:35).
  CJ 설비는 유채 겸용 700 MT 포함.
- **정제·유통 플레이어**(시장점유): CJ제일제당 25% · 롯데푸드(정제) 18% · 사조대림
  (압착+정제) 11% · 오뚜기(정제) 7.3% · 삼양(정제) 5%. 수입 정제유도 국내 재탈취·재포장
  후 국산 표기 유통이 일반적.
- **관세**: 일반 2~8%, 주요 FTA로 대부분 0%. 예외: 韓-ASEAN FTA는 조유 0% vs 정제유 5% —
  **국내 정제 보호 구조**(조유 수입 유인).
- **바이오디젤**: 식물성유지 시장의 약 20%, 혼합의무 확대 계획으로 점증(HS 1507.10.2000
  바이오디젤용 조유 트랙 별도 — 우리 수집 체계와 일치).

## 5. 실측 수입 채널 프로파일 — 관세청 GW (조유 식용 1507.10.1000, 2022~2026)

| 원산지 | 활동월 수 | 화물 중앙값 | 최대 화물 | CIF 중앙값 | 채널 성격 (실측 해석) |
|---|---|---|---|---|---|
| **아르헨티나** | 45개월 (준연속) | 10,981 MT | 88,088 MT | 1,183 $/MT | **주력·연속 채널** — Up River 크러셔(LDC·Bunge·Cargill·COFCO 소재)발, 수출세 할인으로 최저가. term/basis 성격의 정기 흐름 |
| **미국** | 12개월 (간헐) | 15,115 MT | 39,832 MT | 1,383 $/MT | **기회적 대형 화물** — 걸프발, 45Z 정책기 프리미엄으로 고가. 스팟 성격, 파슬이 큼 |
| **브라질** | 14개월 | 1,326 MT | 10,530 MT | 1,267 $/MT | 보조 채널(소형) |
| **중국** | 8개월 | 156 MT | 10,031 MT | 1,654 $/MT | 간헐·소형(가공무역 성격), 2026-03 10,031 MT@1,233 예외적 |

최근 실적 예: 아르헨 2025-06~12 매월/격월 1.7~38.7천 MT 연속 · 미국 2025-01/03/04
18~40천 MT 집중 후 공백 · 2026-01 미국 11.8천 MT@1,191.

**함의**: 한국 조유 수입은 "아르헨 연속 기반 물량 + 미국·기타 기회 물량"의 이중 구조다.
이는 §2의 공급 측 구조(아르헨=LDC·Bunge·COFCO 압착 허브, 미국=ADM·Cargill 걸프)와
맞물리며, 도착가 밴드의 내재 basis 층이 음수(−210/−32/+123 $/MT)인 실측 원인
(아르헨 수출세 할인 흡수)과 일관된다.

## 6. 수입사 선호 축과 4축 엔진 연계 (§3c 확장 스키마)

수입사별 선호(물량·가격·주기)를 G2 4축 대안 엔진이 반영하도록 **거래상대 프로파일**
파라미터를 §3c 방식으로 정의한다 — 값은 런타임 입력 전용(저장 금지):

```yaml
counterparty_profile:            # 실값은 실행 시에만 주입 — repo 저장 금지 (D-021)
  supplier_type: "ABCD | regional | broker"
  origin_mix: {AR: 0.6, US: 0.3, other: 0.1}   # 예시 자리 — 실측 §5로 초기화 가능
  contract_type: "term_basis | spot_flat | mixed"
  parcel_mt: 15000               # 표준 화물 단위
  fixation_window_days: 30       # basis 계약 시 고정 창
  cycle_months: 1.5              # 구매 주기
  quality_spec: "NOPA_crude"
```

- 기본값은 §5 실측 분포(원산지·파슬·주기)로 채울 수 있어 **내부 정보 없이도** 현실적인
  시뮬레이션이 가능하다. 담당자 실거래 조건은 회의 시 런타임으로만 대입.
- Incoterms 축(§3d)·대체유지 축(SBO−CPO>175, A-167 정정)과 결합해 "동일 물량을
  ①원산지 전환 ②계약형 전환(term↔spot) ③고정 시점 이연 ④유종 전환"으로 비교한다.

## 7. 갭과 지원 필요 (유·무료)

| 갭 | 무료 경로 | 유료 경로 | 비고 |
|---|---|---|---|
| CFR/CIF 아시아 실측 basis 호가 | 관세청 CIF 역산(월별·후행 — 확보) | **Platts / Fastmarkets** (DQ-1) | CME 남아시아 식용유 선물 기초지수가 Fastmarkets CFR India |
| 탱커 화물 추적(선적 시점 파악) | AISstream 해협 통과(확보) | **Kpler / Vortexa** (화물 단위) | 선적→도착 리드타임 실측화 |
| FOSFA 계약서 원문·중재 판례 | 계약 목록·개요(공개) | FOSFA 회원 가입 | 조항 세부는 회원 전용 |
| 기업별 압착·정제 능력 정밀치 | 연차보고서·GAIN(확보) | S&P Commodity Insights | 공개치로 1차 충분 |
| 국내 정제사별 수입 실적 분해 | 관세청은 국가별만(기업별 불가) | KITA K-stat 기업 통계도 제한 | **구조적 한계** — 기업별은 내부·비공개 |

## 8. GPT-5.6-Sol 교차검증

- 본 문서 push 시 cross_verify.yml이 검증(diff + 문서 글로브). 결과는 본 절에 추기.
- 검증 결과: (추기 예정)

## 출처

- USDA FAS GAIN **KS2024-0010** "Vegetable Oil Market Overview" (Seoul, 2024-03-12) — 저장소 코퍼스 판독
- 관세청 GW 실측: `data/raw/관세청/.../Soybean Oil/1507.10/Food use (.1000)/` 국가별 월별 (2010~2026)
- [FOSFA International — Contracts](https://www.fosfa.org/contracts/) (세계 유지 거래 85%)
- [S&P Global — South American soybean oil FOB basis](https://www.spglobal.com/commodity-insights/en/news-research/latest-news/agriculture/070323-south-american-soybean-oil-fob-basis-drops-to-record-low)
- [DTN — ADM to Expand Soybean Crush Capacity at 4 US Plants](https://www.dtnpf.com/agriculture/web/ag/news/business-inputs/article/2026/07/30/adm-expand-soybean-crush-capacity-4)
- [AgNavigator — LDC to build new soy plant in Ohio](https://www.agnavigator.com/Article/2023/10/23/louis-dreyfus-company-to-build-new-soy-plant-in-ohio/)
- [European Parliament — The role of commodity traders in shaping agricultural markets (2024)](https://www.europarl.europa.eu/RegData/etudes/STUD/2024/747276/IPOL_STU(2024)747276_EN.pdf)
- [Wilmar International — History & Milestones](https://www.wilmar-international.com/about-us/history-milestones)
- [CME Group — Soybean Oil Futures Contract Specs](https://www.cmegroup.com/markets/agriculture/oilseeds/soybean-oil.contractSpecs.html)
