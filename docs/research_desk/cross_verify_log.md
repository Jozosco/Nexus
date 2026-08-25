# GPT-5.6-Sol 교차검증 누적 원장

**갱신**: 2026-08-25 · **자동 생성**: `scripts/build_cross_verify_log.py`

> 조정자 상시 지시(2026-08-13): 인프라·분석·코드 작업은 GPT-5.6-Sol로 교차검증한다.
> 이 파일은 그 **실행 이력과 판정을 한곳에 모은 원장**이다. 개별 판정 전문은
> `reports/cross_verify/` 의 해당 파일에 있다(저장소에 커밋 — 아티팩트 만료 무관).

## 요약

- 총 검증 기록 **56건** — 판정 산출 52 · 실패(미판정) 4
- 누적 지적: **[치명] 33건 · [높음] 458건**
- ⚠️ 실패 기록은 **그 대상이 검증되지 않았다**는 뜻 — 재검증 대상이다.

## 실행 이력

| 일자 | 대상 | 상태 | 치명 | 높음 | 판정 요지 | 런 | 전문 |
|---|---|---|---|---|---|---|---|
| 2026-08-25 | `reports/market/procurement_alternatives_2026-08-14.m` | ✅ 무지적 | 0 | 0 | (요지 추출 불가) | 32841524051 | [xverify_2026-08-25_328415240…](../../reports/cross_verify/xverify_2026-08-25_32841524051_reports_market_procurement_alternatives_2026-08-14.md_report_1.md) |
| 2026-08-25 | `reports/market/landed_cost_band_2026-08-14.md, repor` | ✅ 무지적 | 0 | 0 | (요지 추출 불가) | 32841524051 | [xverify_2026-08-25_328415240…](../../reports/cross_verify/xverify_2026-08-25_32841524051_reports_market_landed_cost_band_2026-08-14.md_reports_market_1.md) |
| 2026-08-25 | `git diff HEAD~1` | ⚠️ 지적 | 1 | 0 | [치명][재현 불가능] 검증 대상 코드가 제공되지 않음**: 현재 대화에는 `git diff HEAD~1`의 출력, 커밋 해시, 저장소 접근 정보가 없어 변경 내용을 재현·검증할  | 32841524051 | [xverify_2026-08-25_328415240…](../../reports/cross_verify/xverify_2026-08-25_32841524051_git_diff_HEAD_1_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/knowledge_repository_opti` | ⚠️ 지적 | 1 | 13 | [높음] EvidenceSpan 준수 주장과 저장 스키마가 모순된다. | 32841524051 | [xverify_2026-08-25_328415240…](../../reports/cross_verify/xverify_2026-08-25_32841524051_docs_research_desk_2026-08_knowledge_repository_options_2026_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/hs_code_classification_20` | ✅ 무지적 | 0 | 0 | (요지 추출 불가) | 32841524051 | [xverify_2026-08-25_328415240…](../../reports/cross_verify/xverify_2026-08-25_32841524051_docs_research_desk_2026-08_hs_code_classification_2026_08_25_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/glossary_mart_asof_duckdb` | ✅ 무지적 | 0 | 0 | 지적 사항 없음 | 32841524051 | [xverify_2026-08-25_328415240…](../../reports/cross_verify/xverify_2026-08-25_32841524051_docs_research_desk_2026-08_glossary_mart_asof_duckdb_2026_08_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/g1_publication_schedule_p` | ⚠️ 지적 | 2 | 23 | [높음] 분석창 연수가 잘못 표기됨.** `2010-01~2025-12`를 양끝 포함하면 192개월, 즉 **16개년**이다. “15개년 추정창”과 실제 시작·종료월 중 어느 쪽이 | 32841524051 | [xverify_2026-08-25_328415240…](../../reports/cross_verify/xverify_2026-08-25_32841524051_docs_research_desk_2026-08_g1_publication_schedule_panel_202_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/differentiation_brainstor` | ⚠️ 지적 | 1 | 26 | [높음] 아이디어 개수가 맞지 않음 | 32841524051 | [xverify_2026-08-25_328415240…](../../reports/cross_verify/xverify_2026-08-25_32841524051_docs_research_desk_2026-08_differentiation_brainstorm_2026_0_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/abcd_trading_structure_20` | ⚠️ 지적 | 1 | 18 | [높음] 조유 추정량의 범위 판정이 산술적으로 틀림 | 32841524051 | [xverify_2026-08-25_328415240…](../../reports/cross_verify/xverify_2026-08-25_32841524051_docs_research_desk_2026-08_abcd_trading_structure_2026_08_15_1.md) |
| 2026-08-25 | `reports/market/procurement_alternatives_2026-08-14.m` | ✅ 무지적 | 0 | 0 | (요지 추출 불가) | 32814173562 | [xverify_2026-08-25_328141735…](../../reports/cross_verify/xverify_2026-08-25_32814173562_reports_market_procurement_alternatives_2026-08-14.md_report_1.md) |
| 2026-08-25 | `reports/market/landed_cost_band_2026-08-14.md, repor` | ✅ 무지적 | 0 | 0 | (요지 추출 불가) | 32814173562 | [xverify_2026-08-25_328141735…](../../reports/cross_verify/xverify_2026-08-25_32814173562_reports_market_landed_cost_band_2026-08-14.md_reports_market_1.md) |
| 2026-08-25 | `git diff HEAD~1` | ✅ 무지적 | 0 | 0 | (요지 추출 불가) | 32814173562 | [xverify_2026-08-25_328141735…](../../reports/cross_verify/xverify_2026-08-25_32814173562_git_diff_HEAD_1_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/knowledge_repository_opti` | ✅ 무지적 | 0 | 0 | (요지 추출 불가) | 32814173562 | [xverify_2026-08-25_328141735…](../../reports/cross_verify/xverify_2026-08-25_32814173562_docs_research_desk_2026-08_knowledge_repository_options_2026_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/hs_code_classification_20` | ⚠️ 지적 | 1 | 15 | [치명] 대두유 HSK 코드가 6개가 아니라 7개다. | 32814173562 | [xverify_2026-08-25_328141735…](../../reports/cross_verify/xverify_2026-08-25_32814173562_docs_research_desk_2026-08_hs_code_classification_2026_08_25_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/glossary_mart_asof_duckdb` | ✅ 무지적 | 0 | 0 | 지적 사항 없음 | 32814173562 | [xverify_2026-08-25_328141735…](../../reports/cross_verify/xverify_2026-08-25_32814173562_docs_research_desk_2026-08_glossary_mart_asof_duckdb_2026_08_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/g1_publication_schedule_p` | ⚠️ 지적 | 1 | 24 | [높음] 분석 기간 연수 계산 오류 및 표본비율 근거 불일치** — §1·§2.2의 `2010-01~2025-12`는 192개월, 즉 **16개년**이지 15개년이 아니다. `하루 | 32814173562 | [xverify_2026-08-25_328141735…](../../reports/cross_verify/xverify_2026-08-25_32814173562_docs_research_desk_2026-08_g1_publication_schedule_panel_202_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/differentiation_brainstor` | ✅ 무지적 | 0 | 0 | (요지 추출 불가) | 32814173562 | [xverify_2026-08-25_328141735…](../../reports/cross_verify/xverify_2026-08-25_32814173562_docs_research_desk_2026-08_differentiation_brainstorm_2026_0_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/abcd_trading_structure_20` | ❌ 실패 | 0 | 0 | 검증 실패 — 미판정 | 32814173562 | [xverify_2026-08-25_328141735…](../../reports/cross_verify/xverify_2026-08-25_32814173562_docs_research_desk_2026-08_abcd_trading_structure_2026_08_15_1.md) |
| 2026-08-25 | `reports/market/procurement_alternatives_2026-08-14.m` | ✅ 무지적 | 0 | 0 | (요지 추출 불가) | 32809857474 | [xverify_2026-08-25_328098574…](../../reports/cross_verify/xverify_2026-08-25_32809857474_reports_market_procurement_alternatives_2026-08-14.md_report_1.md) |
| 2026-08-25 | `reports/market/landed_cost_band_2026-08-14.md, repor` | ✅ 무지적 | 0 | 0 | (요지 추출 불가) | 32809857474 | [xverify_2026-08-25_328098574…](../../reports/cross_verify/xverify_2026-08-25_32809857474_reports_market_landed_cost_band_2026-08-14.md_reports_market_1.md) |
| 2026-08-25 | `git diff HEAD~1` | ✅ 무지적 | 0 | 0 | (요지 추출 불가) | 32809857474 | [xverify_2026-08-25_328098574…](../../reports/cross_verify/xverify_2026-08-25_32809857474_git_diff_HEAD_1_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/knowledge_repository_opti` | ⚠️ 지적 | 2 | 14 | [높음] “문서 ~5천”은 중복 계상이다.** 권장안의 실제 정규화 대상은 `2,175 + 300+ + 66 + 152 = 약 2,693건`이다. 약 5천은 인덱스 CSV 2,22 | 32809857474 | [xverify_2026-08-25_328098574…](../../reports/cross_verify/xverify_2026-08-25_32809857474_docs_research_desk_2026-08_knowledge_repository_options_2026_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/hs_code_classification_20` | ⚠️ 지적 | 0 | 12 | [높음] HSK 연도 버전과 누적기간이 불일치한다. | 32809857474 | [xverify_2026-08-25_328098574…](../../reports/cross_verify/xverify_2026-08-25_32809857474_docs_research_desk_2026-08_hs_code_classification_2026_08_25_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/glossary_mart_asof_duckdb` | ✅ 무지적 | 0 | 0 | 지적 사항 없음 | 32809857474 | [xverify_2026-08-25_328098574…](../../reports/cross_verify/xverify_2026-08-25_32809857474_docs_research_desk_2026-08_glossary_mart_asof_duckdb_2026_08_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/g1_publication_schedule_p` | ⚠️ 지적 | 1 | 20 | [높음] 분석 기간이 “15개년”이라는 표기와 실제 기간이 불일치 | 32809857474 | [xverify_2026-08-25_328098574…](../../reports/cross_verify/xverify_2026-08-25_32809857474_docs_research_desk_2026-08_g1_publication_schedule_panel_202_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/differentiation_brainstor` | ⚠️ 지적 | 3 | 17 | [높음] B1·B2의 원화/kg 변환에 필요한 단위 변환이 누락됨 | 32809857474 | [xverify_2026-08-25_328098574…](../../reports/cross_verify/xverify_2026-08-25_32809857474_docs_research_desk_2026-08_differentiation_brainstorm_2026_0_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/abcd_trading_structure_20` | ⚠️ 지적 | 0 | 18 | [높음] 잔차 부호 서술이 수치와 모순됨. | 32809857474 | [xverify_2026-08-25_328098574…](../../reports/cross_verify/xverify_2026-08-25_32809857474_docs_research_desk_2026-08_abcd_trading_structure_2026_08_15_1.md) |
| 2026-08-25 | `reports/market/procurement_alternatives_2026-08-14.m` | ✅ 무지적 | 0 | 0 | (요지 추출 불가) | 32804710386 | [xverify_2026-08-25_328047103…](../../reports/cross_verify/xverify_2026-08-25_32804710386_reports_market_procurement_alternatives_2026-08-14.md_report_1.md) |
| 2026-08-25 | `reports/market/landed_cost_band_2026-08-14.md, repor` | ✅ 무지적 | 0 | 0 | (요지 추출 불가) | 32804710386 | [xverify_2026-08-25_328047103…](../../reports/cross_verify/xverify_2026-08-25_32804710386_reports_market_landed_cost_band_2026-08-14.md_reports_market_1.md) |
| 2026-08-25 | `git diff HEAD~1` | ✅ 무지적 | 0 | 0 | 지적 사항 없음 | 32804710386 | [xverify_2026-08-25_328047103…](../../reports/cross_verify/xverify_2026-08-25_32804710386_git_diff_HEAD_1_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/knowledge_repository_opti` | ⚠️ 지적 | 1 | 17 | [높음] 요약과 인덱스의 건수가 불일치하며 조인 완전성이 입증되지 않았다. | 32804710386 | [xverify_2026-08-25_328047103…](../../reports/cross_verify/xverify_2026-08-25_32804710386_docs_research_desk_2026-08_knowledge_repository_options_2026_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/glossary_mart_asof_duckdb` | ✅ 무지적 | 0 | 0 | 지적 사항 없음 | 32804710386 | [xverify_2026-08-25_328047103…](../../reports/cross_verify/xverify_2026-08-25_32804710386_docs_research_desk_2026-08_glossary_mart_asof_duckdb_2026_08_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/g1_publication_schedule_p` | ⚠️ 지적 | 0 | 22 | [높음] 분석 기간의 연수 표기가 틀림 | 32804710386 | [xverify_2026-08-25_328047103…](../../reports/cross_verify/xverify_2026-08-25_32804710386_docs_research_desk_2026-08_g1_publication_schedule_panel_202_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/differentiation_brainstor` | ⚠️ 지적 | 1 | 25 | [높음] 아이디어 건수가 일치하지 않는다. | 32804710386 | [xverify_2026-08-25_328047103…](../../reports/cross_verify/xverify_2026-08-25_32804710386_docs_research_desk_2026-08_differentiation_brainstorm_2026_0_1.md) |
| 2026-08-25 | `docs/research_desk/2026-08/abcd_trading_structure_20` | ⚠️ 지적 | 1 | 20 | [높음] 조유 추정량의 범위 판정 오류 (§4b) | 32804710386 | [xverify_2026-08-25_328047103…](../../reports/cross_verify/xverify_2026-08-25_32804710386_docs_research_desk_2026-08_abcd_trading_structure_2026_08_15_1.md) |
| 2026-08-19 | `reports/market/procurement_alternatives_2026-08-14.m` | ✅ 무지적 | 0 | 0 | (요지 추출 불가) | 32251935391 | [xverify_2026-08-19_322519353…](../../reports/cross_verify/xverify_2026-08-19_32251935391_reports_market_procurement_alternatives_2026-08-14.md_report_1.md) |
| 2026-08-19 | `reports/market/landed_cost_band_2026-08-14.md, repor` | ⚠️ 지적 | 3 | 10 | [치명] 예측 분위로 해석할 수 없는 값을 P10/P50/P90 도착가 밴드로 제시 — 양 문서 | 32251935391 | [xverify_2026-08-19_322519353…](../../reports/cross_verify/xverify_2026-08-19_32251935391_reports_market_landed_cost_band_2026-08-14.md_reports_market_1.md) |
| 2026-08-19 | `git diff HEAD~1` | ⚠️ 지적 | 1 | 9 | [치명] 알려진 오규격 밴드를 제거하지 않고 핵심 수치로 계속 노출·재사용한다. | 32251935391 | [xverify_2026-08-19_322519353…](../../reports/cross_verify/xverify_2026-08-19_32251935391_git_diff_HEAD_1_1.md) |
| 2026-08-19 | `docs/research_desk/2026-08/glossary_mart_asof_duckdb` | ✅ 무지적 | 0 | 0 | 지적 사항 없음 | 32251935391 | [xverify_2026-08-19_322519353…](../../reports/cross_verify/xverify_2026-08-19_32251935391_docs_research_desk_2026-08_glossary_mart_asof_duckdb_2026_08_1.md) |
| 2026-08-19 | `docs/research_desk/2026-08/g1_publication_schedule_p` | ❌ 실패 | 0 | 0 | 검증 실패 — 미판정 | 32251935391 | [xverify_2026-08-19_322519353…](../../reports/cross_verify/xverify_2026-08-19_32251935391_docs_research_desk_2026-08_g1_publication_schedule_panel_202_1.md) |
| 2026-08-19 | `docs/research_desk/2026-08/differentiation_brainstor` | ⚠️ 지적 | 1 | 24 | [높음] 대표 아이디어 수가 24건이 아니라 28건이다. | 32251935391 | [xverify_2026-08-19_322519353…](../../reports/cross_verify/xverify_2026-08-19_32251935391_docs_research_desk_2026-08_differentiation_brainstorm_2026_0_1.md) |
| 2026-08-19 | `docs/research_desk/2026-08/abcd_trading_structure_20` | ❌ 실패 | 0 | 0 | 검증 실패 — 미판정 | 32251935391 | [xverify_2026-08-19_322519353…](../../reports/cross_verify/xverify_2026-08-19_32251935391_docs_research_desk_2026-08_abcd_trading_structure_2026_08_15_1.md) |
| 2026-08-19 | `reports/market/procurement_alternatives_2026-08-14.m` | ⚠️ 지적 | 1 | 16 | [치명] 2·4주 대기 손익을 단일 시점 가격 밴드로 판단했다. | 32242841236 | [xverify_2026-08-19_322428412…](../../reports/cross_verify/xverify_2026-08-19_32242841236_reports_market_procurement_alternatives_2026-08-14.md_1.md) |
| 2026-08-19 | `reports/market/landed_cost_band_2026-08-14.md` | ✅ 무지적 | 0 | 0 | (요지 추출 불가) | 32242841236 | [xverify_2026-08-19_322428412…](../../reports/cross_verify/xverify_2026-08-19_32242841236_reports_market_landed_cost_band_2026-08-14.md_1.md) |
| 2026-08-19 | `git diff HEAD~1` | ✅ 무지적 | 0 | 0 | (요지 추출 불가) | 32242841236 | [xverify_2026-08-19_322428412…](../../reports/cross_verify/xverify_2026-08-19_32242841236_git_diff_HEAD_1_1.md) |
| 2026-08-19 | `docs/research_desk/2026-08/glossary_mart_asof_duckdb` | ✅ 무지적 | 0 | 0 | 지적 사항 없음 | 32242841236 | [xverify_2026-08-19_322428412…](../../reports/cross_verify/xverify_2026-08-19_32242841236_docs_research_desk_2026-08_glossary_mart_asof_duckdb_2026_08_1.md) |
| 2026-08-19 | `docs/research_desk/2026-08/g1_publication_schedule_p` | ⚠️ 지적 | 1 | 22 | [높음] 분석기간 연수 계산 오류 | 32242841236 | [xverify_2026-08-19_322428412…](../../reports/cross_verify/xverify_2026-08-19_32242841236_docs_research_desk_2026-08_g1_publication_schedule_panel_202_1.md) |
| 2026-08-19 | `docs/research_desk/2026-08/differentiation_brainstor` | ⚠️ 지적 | 1 | 24 | [높음] 아이디어 수 집계 오류 — 문서 전반 | 32242841236 | [xverify_2026-08-19_322428412…](../../reports/cross_verify/xverify_2026-08-19_32242841236_docs_research_desk_2026-08_differentiation_brainstorm_2026_0_1.md) |
| 2026-08-19 | `docs/research_desk/2026-08/abcd_trading_structure_20` | ❌ 실패 | 0 | 0 | 검증 실패 — 미판정 | 32242841236 | [xverify_2026-08-19_322428412…](../../reports/cross_verify/xverify_2026-08-19_32242841236_docs_research_desk_2026-08_abcd_trading_structure_2026_08_15_1.md) |
| 2026-08-19 | `reports/market/procurement_alternatives_2026-08-14.m` | ⚠️ 지적 | 3 | 21 | [치명] 현재 도착가 밴드로 2·4주 대기 손익을 판단했다.** 동일 일자의 `[1,290, 1,770]` 밴드는 2주·4주 후 조건부 가격분포가 아니다. 또한 무추세 가정은 `E | 32207719881 | [xverify_2026-08-19_322077198…](../../reports/cross_verify/xverify_2026-08-19_32207719881_reports_market_procurement_alternatives_2026-08-14.md_1.md) |
| 2026-08-19 | `reports/market/landed_cost_band_2026-08-14.md` | ⚠️ 지적 | 1 | 14 | [치명] ‘내재 basis+운임’ 층이 정의상 해당 성분을 식별하지 못해 주 밴드의 해석이 성립하지 않음. | 32207719881 | [xverify_2026-08-19_322077198…](../../reports/cross_verify/xverify_2026-08-19_32207719881_reports_market_landed_cost_band_2026-08-14.md_1.md) |
| 2026-08-19 | `git diff HEAD~1` | ⚠️ 지적 | 1 | 0 | [치명] 재현 불가능**: 저장소와 `git diff HEAD~1` 출력이 제공되지 않아 변경 내용을 검증할 수 없습니다. 또한 `HEAD~1`은 저장소 상태에 따라 달라져 대상  | 32207719881 | [xverify_2026-08-19_322077198…](../../reports/cross_verify/xverify_2026-08-19_32207719881_git_diff_HEAD_1_1.md) |
| 2026-08-19 | `docs/research_desk/2026-08/glossary_mart_asof_duckdb` | ✅ 무지적 | 0 | 0 | 지적 사항 없음 | 32207719881 | [xverify_2026-08-19_322077198…](../../reports/cross_verify/xverify_2026-08-19_32207719881_docs_research_desk_2026-08_glossary_mart_asof_duckdb_2026_08_1.md) |
| 2026-08-19 | `docs/research_desk/2026-08/g1_publication_schedule_p` | ⚠️ 지적 | 2 | 16 | [높음] 분석창 연수와 표본 비율이 불일치함. | 32207719881 | [xverify_2026-08-19_322077198…](../../reports/cross_verify/xverify_2026-08-19_32207719881_docs_research_desk_2026-08_g1_publication_schedule_panel_202_1.md) |
| 2026-08-19 | `docs/research_desk/2026-08/differentiation_brainstor` | ✅ 무지적 | 0 | 0 | (요지 추출 불가) | 32207719881 | [xverify_2026-08-19_322077198…](../../reports/cross_verify/xverify_2026-08-19_32207719881_docs_research_desk_2026-08_differentiation_brainstorm_2026_0_1.md) |
| 2026-08-19 | `docs/research_desk/2026-08/abcd_trading_structure_20` | ⚠️ 지적 | 1 | 18 | [치명] 월별 수입 합계를 개별 화물(parcel) 크기로 오인 | 32207719881 | [xverify_2026-08-19_322077198…](../../reports/cross_verify/xverify_2026-08-19_32207719881_docs_research_desk_2026-08_abcd_trading_structure_2026_08_15_1.md) |

## 해소 이력

지적된 [치명] 항목의 수정 경위는 MEMORY 원장에 ID로 남는다:

- A-167 — 도착가 밴드 분위 단순합 → MC 독립 컨볼루션 · 대체유 임계 부호 정정
- A-169 — 게이트 `always()` 무차별 우회 → `!cancelled()` + PASS/WARNING 명시
- A-179 — vintage 주석(개정 이력 미보존 지표 수) 보고서 삽입

*미해소 [치명]: G2 대체유 z격차 방향 해석(작업 대기열 등재) · 개정 확정치 94종 분리(M-009 단계)*
