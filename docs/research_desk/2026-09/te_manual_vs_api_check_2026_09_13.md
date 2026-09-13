# Trading Economics 수동 갱신본 ↔ API 부착분 대조 검증 (2026-09-13)

> 승인자 요청: "TE 파일을 최신 일자까지 수동 갱신했으니 API 부착분과 대조 검증하고, 일치하면 API 최신
> 수집 체계를 확정할 것." 본 문서는 그 대조 결과와 확정 결정을 기록함.
> 라벨 어휘: **CONFIRMED**(실측 확인) / **INFERENCE**(추정) / **DATA GAP**(자료 부재).

---

## 1. 목적·범위

- **목적**: 승인자 수동 갱신본과 일별 스냅샷 봇(`te_xlsx_update.yml`)이 덧붙인 행이 같은 일자에서
  같은 종가를 갖는지 확인하고, 일치하면 9/11 이후 일별 갱신 경로를 API 단일 경로로 확정함.
- **범위**: `data/raw/Trading Economics/Markets/Commodities/{Agricultural,Energy,Industrial,Shipping Indices}/`
  아래 xlsx **26개 전부**. 검증 기준은 origin/main 최신 blob(9/13 시점).
- **갱신 주체 구분**(CONFIRMED):
  - 9/13 승인자 업로드 커밋은 **7개 파일만** 변경함 — `6eb4650`(DAP·Urea), `6b040fc`(BDI·CRB·EU Carbon·GSCI·CFI).
  - 나머지 **19개 파일의 최신 행은 봇 스냅샷 런**에서 옴 — `1b15205`(9/11 12:49 UTC)·`ce2599d`(9/11 23:24 UTC).

## 2. 대조 방법

1. **구조 검사**: 파일별 연도 시트를 열어 (Month, Day) 중복, Close 비수치, 정렬 방향, 9월 공백(영업일 3일 초과)을 점검함.
2. **동일 일자 종가 대조**: 수동 갱신본과 봇 append 행이 **같은 일자**를 가진 경우 Close 값을 소수점 그대로 비교함
   (허용 오차 0 — 일치율 %로 표기).
3. **커밋 계보 대조**: 파일별로 9/10 이후 커밋을 `git log`로 추적해 최신 행의 출처(봇/수동)를 확정하고, 수동 업로드가
   봇 행을 되돌린 경우를 blob 간 diff로 식별함.
4. **게이트 로그 대조**: 봇 런 2회(`1b15205`, `ce2599d`)의 보고서·로그에서 점프 게이트·심볼 미발견·무응답 항목을 추출함.
5. **하위 파서 영향 확인**: `scripts/ingest_te_xlsx.py`를 grep해 봇 행의 Open/High/Low 공란이 분석 투입값에 영향을
   주는지 확인함.

## 3. 결과 요약

| 항목 | 결과 | 라벨 |
|---|---|---|
| 구조 무결성(26파일) | (Month, Day) 중복 **0** · Close 비수치 **0** · 전 시트 오름차순 · 9월 영업일 3일 초과 공백 **없음**(미국 거래소 파일의 9/7 결측 = Labor Day 휴장) | CONFIRMED |
| 동일 일자 종가 일치 | 대조 가능 5건 전부 **정확히 일치(0.000%)** — Sunflower Oil 9/10 1643.8 · Coal 9/10 148 · Ethanol 9/10 2.065 · Naphtha 9/10 871.169 · Urea 9/10 450.25 | CONFIRMED |
| 봇 append 행의 O/H/L | 공란. `ingest_te_xlsx.py`는 `value`를 **Close 컬럼에서만** 산출(L224·L233)하고 Open/High/Low는 결측 허용 부가 컬럼(L234~235)이라 분석 투입값에 영향 없음 | CONFIRMED |
| 수동 업로드가 봇 행을 되돌린 파일 | 5건(Urea·CRB·EU Carbon·GSCI·CFI) — 다음 런이 재-append하므로 데이터 손실 없음 | CONFIRMED |
| BDI 계열 재척도 | **2023-01-03 이후(정오표 실측)** 860행 변경(배율 중앙값 2.7배 · 2022-12-23 이전 동일), 봇의 점프 게이트가 차단했던 API 값과 정합 — 승인자 확인(9/13): 구 계열 오류·정정본 정본 | CONFIRMED(§5 ②) |
| API 미확정 심볼 | EU Natural Gas(TTF)·Drewry WCI 무응답, DAP 심볼 미해결 | DATA GAP |

**판정**: 수동 갱신본과 API 부착분은 대조 가능한 모든 지점에서 일치함. 구조 결함 없음. 따라서 **9/11 이후 일별 갱신은
API 스냅샷 단일 경로로 확정**하고, 수동 업로드는 공백 복구·교정 용도로 한정함(§6).

## 4. 파일별 대조표 (26행)

열 설명 — *9/10 이후 커밋*: bot=봇 스냅샷 런, manual=승인자 업로드 · *2026 행*: 2026년 시트 행 수 · *마지막 일자/Close* ·
*API↔수동*: 동일 일자 종가 대조 결과(n/a=대조 일자 없음) · *특이사항*.

| # | 폴더 | 파일(품목) | 9/10 이후 커밋 | 2026 행 | 마지막 일자 | Close | API↔수동 | 특이사항 |
|---|---|---|---|---|---|---|---|---|
| 1 | Agricultural | Canola | bot | 181 | 9/11 | 828.9705 | n/a | 9/11 행 O/H/L 공란 |
| 2 | Agricultural | Corn | bot | 177 | 9/11 | 509.8686 | n/a | — |
| 3 | Agricultural | Palm Oil | bot | 166 | 9/11 | 4814 | n/a | — |
| 4 | Agricultural | Rapeseed | bot | 182 | 9/11 | 552.9848 | n/a | — |
| 5 | Agricultural | Soybeans | bot | 177 | 9/11 | 1302.336 | n/a | — |
| 6 | Agricultural | Sugar | bot | 179 | 9/11 | 18.1495 | n/a | — |
| 7 | Agricultural | Wheat | bot | 177 | 9/11 | 718.4229 | n/a | — |
| 8 | Agricultural | Sunflower Oil | bot×2 | 172 | 9/11 | 1636.5 | **9/10 일치**(1643.8) | — |
| 9 | Energy | Brent Crude Oil | bot | 178 | 9/11 | 104.8725 | n/a | — |
| 10 | Energy | Coal | bot×2 | 180 | 9/11 | 146.75 | **9/10 일치**(148) | — |
| 11 | Energy | EU Natural Gas | 없음 | 181 | 9/10 | 80.0738 | n/a | TTF 스냅샷 2런 모두 빈 응답 |
| 12 | Energy | Ethanol | bot×2 | 173 | 9/11 | 2.055 | **9/10 일치**(2.065) | — |
| 13 | Energy | Gasoline | bot | 178 | 9/11 | 3.3381 | n/a | — |
| 14 | Energy | Heating Oil | bot | 176 | 9/11 | 5.0592 | n/a | — |
| 15 | Energy | Naphtha | bot×2 | 174 | 9/11 | 855.28 | **9/10 일치**(871.169) | — |
| 16 | Energy | Natural Gas | bot | 177 | 9/11 | 2.7925 | n/a | — |
| 17 | Energy | UK Natural Gas | bot | 179 | 9/11 | 203.1014 | n/a | — |
| 18 | Energy | WTI Crude Oil | bot | 176 | 9/11 | 99.8158 | n/a | — |
| 19 | Industrial | Di-ammonium(DAP) | manual | 174 | 9/11 | 800 | n/a | API 기록 0건(게이트·심볼 미해결) · 수동 +50행으로 7/1→9/11 공백 복구(O/H/L 전부 채움) |
| 20 | Industrial | Urea | manual + bot×2 | 173 | 9/10 | 450.25 | **9/10 일치**(450.25) | 수동 업로드가 봇 9/11 행(450.75) 되돌림 |
| 21 | Shipping Indices | BDI | manual | 177 | 9/9 | 3620 | n/a(게이트 차단) | 2023-01-03 이후 계열 정정(860행 변경, 예 7/1 733.42→2562 — 정오표 실측) · 3행(4/3·4/6·5/4)은 영국 공휴일 무발표(정상) |
| 22 | Shipping Indices | CRB Index | manual + bot | 172 | 9/9 | 544.12421 | n/a | 수동 업로드가 봇 9/10 행(551.94611) 되돌림 |
| 23 | Shipping Indices | EU Carbon Permits | manual + bot | 178 | 9/10 | 85.9 | n/a | 수동 업로드가 봇 9/11 행(85.12) 되돌림 |
| 24 | Shipping Indices | GSCI | manual + bot | 178 | 9/10 | 746.57 | n/a | 수동 업로드가 봇 9/11 행(750.491) 되돌림 |
| 25 | Shipping Indices | Containerized Freight Index(CFI) | manual + bot | 181 | 9/10 | 3590.0479 | n/a | 수동 업로드가 봇 9/11 행 되돌림 — 그 행은 9/10과 동일값의 정체 이월(stale carry-forward) |
| 26 | Shipping Indices | Drewry WCI | 없음 | 25 | 6/25 | 4166 | n/a | 11주 정체(주간 지수) — 승인자가 검증 범위에서 제외 |

**봇 게이트 로그**(CONFIRMED):
- 런 1(`1b15205`): BDI `BDIY:IND` 점프 **+380%** 차단 · DAP는 오발견 심볼 `BIF:HB`로 **−64%** 차단.
- 런 2(`ce2599d`): BDI 점프 **+378%** 차단 · DAP는 접미 필터(`52cb4b3`, :COM/:IND 외 제외) 이후 심볼 목록이 비어
  스냅샷 없음 · EU Natural Gas·Drewry는 빈 응답.

## 5. 주의 항목 7건과 판정

| # | 항목 | 관찰 | 판정 | 라벨 |
|---|---|---|---|---|
| ① | 5파일 봇 행 되돌림(Urea·CRB·EU Carbon·GSCI·CFI) | 수동 업로드본이 봇이 덧붙인 최신 1행을 포함하지 않아 파일 마지막 일자가 하루 후퇴함 | **문제 없음** — 갱신기가 파일 마지막 일자 이후만 append하므로 다음 런이 해당 행을 재-append함. 시트는 오름차순 유지·중복 0 보장(`_validate` 역행 거부 + 일자 초과 조건). CFI의 되돌려진 9/11 행은 정체 이월값이라 오히려 제거가 타당함 | CONFIRMED |
| ② | BDI 계열 재척도 | 정오표 실측: **2023-01-03 이후 860행**이 바뀜(배율 중앙값 2.7배, 예 7/1 733.42→2562 · 2022-12-23 이전 동일). 봇 런 2회가 `BDIY:IND` 스냅샷을 +378~380% 점프로 차단했던 값과 새 수동본이 **정합**함 | **승인자 확인(9/13): 구 계열 오류 · 정정본 정본** — 정정본이 정본이므로 API 값은 게이트에 걸리지 않고 정상 append됨(9/9 3,620 vs API ≈3,521 → −2.7%). 정정본 기준 9/9 표준화 지수 +2.12(G1 방식)·+2.74(도착가 방식) → 2σ 경보·운임 레짐 급등. 실측·영향 산출물은 `bdi_series_correction_errata_2026_09_13.md` | CONFIRMED |
| ③ | TTF(EU Natural Gas)·Drewry WCI 무응답 | 고정 심볼 `TTF:COM`·`WCI:IND`가 2런 모두 빈 스냅샷. 단일 검색어(`ttf`·`drewry`)도 :COM/:IND 필터 뒤 0건 | 심볼 미확정 상태. 다중 검색어 폴백(§7)으로 다음 런 로그에서 유효 심볼을 확정함. Drewry는 주간 지수라 일별 스냅샷 대상 적합성 자체가 낮음 — 승인자가 검증 범위에서 제외했으므로 미확정 유지 | DATA GAP |
| ④ | DAP 심볼 미해결 | 런 1은 오발견 `BIF:HB`(다른 상품)로 −64% 차단, 런 2는 접미 필터 후 심볼 없음. 결과적으로 API가 DAP 파일에 기록한 행 **0건**이며 7/1→9/11 공백 50행은 수동 업로드로만 복구됨 | 접미 필터 자체는 옳음(오상품 차단). 다중 검색어(`dap`·`diammonium`·`di-ammonium phosphate`·`phosphate`)로 재탐색하고 시도 심볼·검색어를 보고서에 남겨 다음 런에서 확정함 | DATA GAP |
| ⑤ | BDI 3행 부재(4/3·4/6·5/4) | 정정본에서 3개 영업일 행이 없음 | **공휴일 정상(백필 불요)** — 성금요일·부활절 월요일·5월 초 은행휴일로 발틱거래소가 지수를 발표하지 않는 날임. 2023·2024년도 같은 패턴이며 구본은 해당일에 이월 행을 채운 계열이었음. 발표 없는 날에 값을 만들면 실측 원칙(D4)에 어긋나므로 메우지 않음(정오표 §3) | CONFIRMED |
| ⑥ | Drewry WCI 11주 정체 | 마지막 행 6/25(4166), 2026 행 25개 | 주간 지수라 정체가 곧 오류는 아니나 11주는 갱신 부재임. 승인자가 검증 범위에서 제외 — 현행 유지, 심볼 확정(③) 후 재검토 | DATA GAP |
| ⑦ | 봇 행 O/H/L 공란(Canola 9/11 포함) | 스냅샷 응답에 Open/DayHigh/DayLow가 없는 품목은 Close만 기록됨 | **무해** — 파서는 Close만 `value`로 씀(§3). 수동본과 형식 차이는 있으나 분석 투입값 동일 | CONFIRMED |

## 6. 확정 결정

> **9/11 이후 일별 갱신은 `te_xlsx_update.yml` 스냅샷 cron(평일 21:30 UTC, `update_te_xlsx_from_api.py --mode snapshot`)
> 단일 경로로 확정함. 수동 업로드는 공백 복구·교정 시에만 사용함.**

근거(CONFIRMED): ①대조 가능 5건 종가 0.000% 일치 ②26파일 구조 결함 0 ③되돌려진 봇 행은 다음 런이 자동 재-append하므로
수동·자동 경로가 충돌하지 않음 ④봇 행의 O/H/L 공란은 파서 투입값에 영향 없음.

운영 규약:
- 수동 재업로드는 봇이 덧붙인 최신 행을 되돌릴 수 있음(다음 런이 다시 붙이므로 무해). 따라서 **재업로드는 공백 복구·
  계열 교정 목적에만** 쓰고, 일상 갱신은 봇에 맡김.
- 수동 교정(BDI 재척도처럼 과거 계열을 바꾸는 경우)은 본 문서와 같은 대조 기록을 남김. BDI 정정의 실측·z 델타·영향 산출물·CI 수정은
  `docs/research_desk/2026-09/bdi_series_correction_errata_2026_09_13.md`(정오표)에 기록함.
- 미확정 심볼(TTF·WCI·DAP)은 다음 런의 보고서·로그(시도 심볼·검색어 열거)로 확정하며, 확정 전까지 해당 파일은
  수동 기준선 그대로 둠.

## 7. 후속 조치 (코드 변경 요약 — 이번 회차 반영)

| 대상 | 변경 | 목적 |
|---|---|---|
| `scripts/update_te_xlsx_from_api.py` REGISTRY | 검색어를 `str` 또는 `tuple[str, ...]`로 허용(하위 호환). EU Natural Gas=(`ttf`,`eu natural gas`,`dutch ttf`) · Drewry=(`drewry`,`world container index`,`container`) · DAP=(`dap`,`diammonium`,`di-ammonium phosphate`,`phosphate`) | 단일 검색어가 :COM/:IND 필터 뒤 0건이던 3품목의 심볼 재탐색. 고정 심볼을 새로 추측해 넣지 않음 |
| `discover_symbols` | 검색어를 순서대로 시도, 첫 매칭에서 중단. 이름 매칭은 키워드 전부 포함 **또는** 검색어 자체 포함. :COM/:IND 필터·정렬(:COM 우선)·고정 심볼 우선 순서는 유지. 매칭된 검색어를 `[정보]` 로그 | 어느 검색어가 유효했는지 로그로 확정 |
| `run` / 보고서 | 모든 심볼이 빈 스냅샷이면 `[정보]` 로그에 시도 심볼·검색어를 남기고, 보고서 행의 심볼 열에 **시도 심볼 전부**, 상태에 `스냅샷 응답 없음(시도 N심볼)`, 하단에 품목별 시도 심볼·검색어 목록을 추가 | 다음 Actions 런 로그·보고서로 유효 심볼 확정 |
| `tests/test_update_te_xlsx.py` | 다중 검색어 폴백 테스트 1건 추가(`_te_get` monkeypatch — 두 번째 검색어에서만 매칭, :NL 제외, 고정 심볼 우선, commodities 폴백 미도달 확인). `python -m pytest tests/test_update_te_xlsx.py -q` → **9 passed** | 회귀 방지 |
| `data/raw/Trading Economics/Markets/Commodities/README.md` | "일별 갱신 확정(2026-09-13)" 절 추가 | 운영 규약 고정 |

| 정오표 연계 | ②·⑤ 종결 후속 — `.github/workflows/external_data_refresh.yml` Readiness 아티팩트에 TE 수동본 parquet 추가 + G1 잡 복원 블록(A-258) | CI G1 경보가 API BDI(2017~) 폴백이 아닌 정정본 9개년 TE_BDI를 읽도록 함(정오표 §6) |

승인자 확인 결과(9/13): ②·⑤는 **종결** — 구 계열 오류·정정본 정본 확인, 3행(4/3·4/6·5/4)은 공휴일 정상으로 보완하지 않음
(정오표 `bdi_series_correction_errata_2026_09_13.md`). 남은 확인 요청 1건: 다음 런 보고서에서 TTF/WCI/DAP 확정 심볼 승인.
