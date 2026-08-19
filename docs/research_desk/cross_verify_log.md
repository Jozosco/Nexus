# GPT-5.6-Sol 교차검증 누적 원장

**갱신**: 2026-08-19 · **자동 생성**: `scripts/build_cross_verify_log.py`

> 조정자 상시 지시(2026-08-13): 인프라·분석·코드 작업은 GPT-5.6-Sol로 교차검증한다.
> 이 파일은 그 **실행 이력과 판정을 한곳에 모은 원장**이다. 개별 판정 전문은
> `reports/cross_verify/` 의 해당 파일에 있다(저장소에 커밋 — 아티팩트 만료 무관).

## 요약

- 총 검증 기록 **21건** — 판정 산출 18 · 실패(미판정) 3
- 누적 지적: **[치명] 16건 · [높음] 174건**
- ⚠️ 실패 기록은 **그 대상이 검증되지 않았다**는 뜻 — 재검증 대상이다.

## 실행 이력

| 일자 | 대상 | 상태 | 치명 | 높음 | 판정 요지 | 런 | 전문 |
|---|---|---|---|---|---|---|---|
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
