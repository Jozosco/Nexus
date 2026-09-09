# .claude/rules/references.md
> `docs/research_desk/references/`(승인자 공유 PDF·논문)를 다룰 때 로드. 승인자 지시(2026-09-09): **향후 PDF는 전부
> Markdown으로 변환한 뒤 .md 요약을 생성해 처리**한다(토큰 절감·판독 재현성). 세션은 PDF를 직접 판독하지 않는다.

## 반입 절차 (순서 고정)
1. **해시 중복 검사** — `sha256sum`으로 기보관본과 대조(D-038: 중복은 재보관 금지, README에 '중복 차단'만 기록).
2. **변환** — `python scripts/pdf_to_markdown.py <pdf>` → `references/markdown/{stem}.md`(본문·목차·표) +
   `references/summaries/{stem}.md`(요약 골격: 서지·메타·키워드·수치 후보 자동).
   승인자가 웹으로 PDF를 올리면 `reference_pdf_to_md.yml`이 push 시 자동 변환·커밋한다.
3. **요약 작성** — 세션은 `markdown/*.md`만 읽고 골격의 '핵심 주장·방법·Nexus 관련성·정직 분류·인용 문장·온톨로지 후보'를 채운다.
   분류 어휘: 채용 / Challenger 검토 대기 / 배경 / 인용 주의 / 반면교사. 수치는 locator(쪽·표) 없이는 인용하지 않는다.
4. **색인** — `references/README.md` 표에 1행 추가(파일 | 출처 | 공유일 | 연결 문서). 4-라벨(CONFIRMED/INFERENCE/DATA GAP/NOT COMPARABLE) 준수.
5. **온톨로지 반영** — 인과 근거는 `src/semantic/ontology.yaml` evidence, 방법론 선례는 `src/semantic/methods.yaml`(MP-xx),
   엔티티는 `entities.yaml` → `python scripts/validate_semantic_layer.py --strict` 통과 후 커밋.
6. **MEMORY** — 당월 아카이브에 통합 결과(반영 위치·정직 분류) 기록.

## 규율
- 스캔본(텍스트 층 부족)은 변환기가 표시 — 이때만 이미지 판독을 예외 허용하고 요약에 '스캔본 판독' 명시.
- 원문 PDF는 보관·출처 추적용이며 요약·markdown이 작업 입력이다. markdown은 재생성 가능 산출물이므로 원문 변경 시 `--force`로 재생성.
- 기밀·거취·인프라 상세는 요약에 기록하지 않는다.
