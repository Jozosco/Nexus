# Session 43 — 워크플로우 오류 근본원인·해결 종합 보고

**작성일**: 2026-08-11 · **참여**: C-01(종합) · C-03·C-04 · P1-05·P1-06

---

## 1. Databento exit 128 — 원인·해결 (수정 완료, 재실행 필요)
- **핵심**: **데이터 수집 자체는 성공**(ZL 15개년 csv+xlsx 생성, 4,062행 커밋 생성됨). 실패 지점은
  마지막 `git push` — `github-actions[bot] denied (403)`.
- **근본 원인**: `historical_backfill.yml`에 **`permissions:` 블록이 없어** GITHUB_TOKEN이
  **읽기 전용**으로 발급됨(리포지토리 기본값). 재정리 워크플로우들은 `contents: write`가 있어
  main push가 됐지만 이 워크플로우만 누락 — 런너 종료와 함께 수집분 유실.
- **해결(API 우선)**: 워크플로우에 `permissions: contents: write` 추가. **수동 작업 불필요** —
  `connector=databento` 재실행만 하면 됨(소액 종량제 재과금 ~$1 미만 수준).

## 2. gain-pdf "PDF 없음" — 원인·해결 (수정 완료)
- **근본 원인**: 연·월 재정리로 PDF가 `{sub}/{YYYY}/{MM}/`로 이동했는데, `ingest_gain_pdf.py`가
  **최상위 폴더만 검색**(`glob`, 비재귀) → 0건 오탐. 파일은 전부 정상 존재.
- **해결**: 재귀 탐색(`rglob`)으로 교체 + Summary 폴더 제외. C-04·P1-05/06 협의 결론: 판독 로직
  자체는 정상(2020년 178건 실검증 완료) — 경로 탐색만의 문제였음.

## 3. 헬스체크 오류 4종 — 원인·해결 (수정 완료)

| API | 원인 | 해결(API 우선) |
|---|---|---|
| **BOK·KOSIS·관세청 ConnectTimeout** | 세 곳 모두 **한국 호스팅** — 미국 Actions 러너에서 대륙간 지연·간헐 혼잡. 헬스체크가 **단발 호출(재시도 없음)+15~20s 타임아웃**이라 일시 지연에도 즉시 실패. (직전 실행에선 셋 다 성공했음 = 간헐성 입증) | 타임아웃 60s + **3회 지수 재시도 헬퍼** 전 스텝 적용 |
| **USDA PSD 500** | `apps.fas.usda.gov` 구 호스트 서버 오류(ESR 전례와 동일한 이관 정황). 헬스체크가 구 호스트만 직접 호출 | 헬스체크에도 **api.fas.usda.gov 우선 폴백 체인** 적용. "2024" 표기는 스모크 1개 연도일 뿐 — **실수집은 `fetch_wasde_multi_year(2010)`이 2010~현재 전체 담당**(기본값 2010으로 수정 완료) |
| **USDA ARMS 404** | `data.ers.usda.gov` 구 호스트 폐기 정황 → `api.ers.usda.gov` 신규 후보 추가. 404는 "리포트 조합 미제공"일 수도 있어 **비치명 처리**(보조 지표) | 후보 체인 + 404 시 경고 후 통과 |
| **ECMWF CDS 308/404 "연결 성공인데 데이터 없음"** | **CDS v2 API는 2024년 CDS-Beta 이관으로 폐기** — 그리고 핵심: **기후 데이터는 CDS로 수집한 적이 없음**. 실제 수집원은 **Open-Meteo ERA5-Land**(climate_connector, 무료·키 불요, 동일 ERA5 원천). CDS 체크는 유물이었음 | 헬스체크를 **실수집원(Open-Meteo)** 점검으로 교체. 데이터 부재가 아니라 "안 쓰는 문 두드림"이 원인 |

## 4. 관세청 GW 대체·보완재 xlsx 공백 — 원인·계획
- **원인**: 그 파일들은 **8/3 착수 대비 사전 생성한 빈 템플릿**(Session 39) — 실수집이 아직 실행되지
  않았음(포털 점검→키 로테이션→이번 permissions 이슈 순으로 지연).
- **해결**: permissions 수정 완료 + customs-gw 잡에 main 커밋 단계 존재 → **`connector=customs-gw`
  실행 시 90개 템플릿이 실데이터로 채워짐**. 수동 작업 불필요.

## 5. 요청 이행 현황
| 항목 | 상태 |
|---|---|
| GATS `Oilseeds/Soybean Oil/Exports & Re-Exports/{1507.10.0000, 1517.90.4035, 1507.90/.4050, .4020}` | ✅ 생성 |
| 루트 `YY.MM_*.pdf` 138건 → `GAIN/Oilseeds/{Y}/{M}` | ✅ 재정리 워크플로우 단계 추가(푸시 시 main 실행) |
| GATS `수출량·재수출량.csv` → `…/1507.10.0000/` | ✅ 동일 |
| 구 요약 삭제(`summary_index.csv`·`summary/2020` 2곳·FAO 구 md) | ✅ 316파일 삭제 |
| **요약 스킴 v2**: FAO `{Y}/Summary/` · GAIN `{Y}/{M}/Summary/` | ✅ 적용 — FAO 137건 재생성 중 |
| **템플릿 정합**: '비정형데이터 요약본 Template.md' 기반 | ✅ 자동화 서브셋(§1 메타·§2.2 판단표·§3.1 국가·§5.1 신호·근거발췌) + 서술 섹션은 원칙 4에 따라 `미확인` 표기(추정 금지) — LLM 정밀 요약은 Phase B. 인덱스는 `data/processed/unstructured_index_*.csv`로 이동 |
| 기술문서 업로드(관세청 docx·KOSIS 가이드·ICE 3종) | ⏳ 조정자 업로드 대기 — 업로드 시 파라미터 검증에 활용 |
| **LLM 교체(Req 4)** | ✅ Gemini 전면 배제. P1-05/P1-06 secondary=`gpt-5.6-sol`. `config/llm_cross_validation.json` 신설: 전 분석 교차검증 = OpenAI gpt-5.6-sol/luna · Reasoning **Pro** · effort **high/xhigh** 상시 |

## 6. 다음 실행 (조정자 — dev→main 병합 후)
1. `connector=databento` 재실행 → BO=F 15개년 (이번엔 push 성공)
2. `connector=gain-pdf` 재실행 → 1,371건 요약(신규 Summary 스킴)
3. `connector=customs-gw` → 대체·보완재 90파일 실데이터 채움
4. Health Check 재실행 → 재시도·폴백 체인 검증
