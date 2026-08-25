# GitHub Projects · Wiki · Agents 활용 방안 — 조사·권고 (조정자 요청 2026-08-25)

**작성**: C-01 (전문 에이전트 조사 기반 · WebSearch 출처 확인) · **전제 제약**: 사용자는
GitHub 웹 UI, 세션 자동화는 통합 토큰 MCP(이슈·PR·파일·Actions 계열만 — **Projects·Wiki
도구 없음** 실측, A-146 `actions:write` 부재 전례와 정합).

## 요약 권고

| 기능 | 권고 | 이유 한 줄 |
|---|---|---|
| **Projects v2** | ✅ **도입 권장** — 이슈 자동화와 결합한 "파이프라인 장애 칸반 + 결정 대기 뷰" | 세션이 이슈 생성·라벨링까지 자동화하고, Projects의 **auto-add 내장 워크플로**가 무토큰으로 보드 편입을 대신함 |
| **Wiki** | ⚠️ **소극 권장** — 도입 시 열람용 미러로 한정 | 콘텐츠 API 자체가 없어 자동화는 Actions sync뿐인데, 이는 D-026(Actions 종속 신규 금지)·R-014와 충돌. Knowledge Mart(R-020)가 검색 갭을 이미 커버 |
| **Agents(Copilot coding agent)** | ⚠️ **보조·한시 실험만** | 유료 Copilot 필수 + 실행 기반이 GitHub Actions → 11월 CT 통합(Actions 정지)과 충돌. `.claude/agents/`와는 계층이 다른 별개물 |

## ① GitHub Projects (신형 v2)

- 이슈·PR·드래프트를 테이블/보드/로드맵 뷰로 관리. 커스텀 필드·뷰별 필터·**내장
  자동화**(필터 일치 이슈 auto-add, close→Done 등). 구형(classic)은 2024 폐기.
- API는 **GraphQL 전용**(REST 없음) — 통합 토큰의 project scope 보유 여부 미확인 ❓라
  세션 직접 조작은 기대하지 않음. **우회 확정 경로**: 세션이 MCP로 이슈 생성+라벨
  (`pipeline-failure`, `decision-request` 등) → Projects **auto-add 필터**가 보드에 자동 편입.
- 무료 플랜 포함(아이템 한도 충분). Insights 과거 추이 차트는 Team 이상 전용.

**권장 구성(조정자 웹 UI 설정 — 약 15분)**
1. 저장소 → Projects → New project(Board) — 이름 예: `Nexus Ops`
2. 필드: Status(기본) + `유형`(장애/결정대기/자료회수/마일스톤) 단일선택
3. Workflows(프로젝트 내 자동화): **Auto-add** 필터 `is:issue label:pipeline-failure`,
   `is:issue label:decision-request` 두 건 · Item closed → Status=Done
4. 이후 운영: Ralph Loop(CI-007)가 만드는 파이프라인 실패 이슈가 자동 편입되고,
   세션이 decision_queue(D-042) 항목을 이슈로 발행하면 "결정 대기" 열에 모임 —
   **조정자는 보드 한 화면으로 장애·결정 현황 열람**
5. (선택) GraphQL 자동화까지 원하면 classic PAT(`project` scope) 발급 → GitHub
   Secrets 등재 — 필요성 확인 후 결정 권장(현 구성만으로 목적 달성)

## ② GitHub Wiki

- 실체는 별도 git 저장소(`{repo}.wiki.git`). **콘텐츠 API 없음**(커뮤니티 공식 확인) —
  프로그램 접근은 git 경유뿐. 빈 위키는 첫 페이지를 웹 UI에서 만들어야 `.wiki.git`이
  생성됨. private 저장소 위키는 유료 플랜 필요(저장소 공개 여부 확인 ❓).
- 자동 동기화는 Actions 잡(GITHUB_TOKEN wiki push 패턴)이 유일 — **D-026 "Actions 종속
  신규 생성 금지" + R-014 ②(git push 저장소 패턴 제거)와 정면 충돌**. 11월 Actions 정지
  시 그대로 부채가 됨.
- **판정**: 현 단계 미도입 권고. "사람 열람 UI" 갭은 ①README/docs 링크 정리
  ②Knowledge Mart Phase 1(승인 대기)로 충족 가능. 도입하려면 조정자가 D-026 예외를
  승인하고 열람용 미러(단일 진실 원천은 repo `docs/`)로 한정.

## ③ 상단 바 'Agents' — Copilot coding agent (Agent HQ)

- GitHub의 **호스팅 자율 코딩 서비스**: 이슈를 Copilot에 할당하거나 Agents 패널에서
  태스크 발주 → GitHub 관리 Actions 샌드박스에서 자율 실행 → **draft PR** 생성 → 사람
  리뷰. 2025-05 출시, Agent HQ(2025-10)로 확장 — 서드파티 에이전트(Claude·Codex)도
  2026-02부터 preview(모델 선택 2026-04, 보안 검증 2026-06).
- **요건·비용**: 유료 Copilot 구독 필수(Free 플랜 불가 — Pro $10/월부터), 세션당 premium
  request + **Actions 분 소모**(2026-06 사용량 기반 과금 전환 발표 — 세부 크레딧 ❓).
- **`.claude/agents/`와의 차이(핵심)**:

| 구분 | Copilot coding agent | `.claude/agents/` (현행) |
|---|---|---|
| 본질 | GitHub **플랫폼 제품**(호스팅 실행 서비스) | 저장소 내 **역할 정의 파일**(md 스펙) |
| 실행 위치 | GitHub 관리 Actions 러너 | Claude Code 세션 내부 |
| 트리거 | 이슈 할당·Agents 패널 → 비동기 | C-01 오케스트레이션이 위임 |
| 산출물 | draft PR(코드 변경) | 분석·검증 결과 → 세션 규율 내 반영 |
| 거버넌스 | GitHub 브랜치 보호·PR 리뷰 | CLAUDE.md §6 HITL·C-05·C-08 게이트 |
| 과금 | Copilot 구독+요청+Actions 분 | Claude 세션에 포함 |

  → 상호 대체재가 아님: `.claude/agents/`는 "누가 어떤 규율로 생각하는가"의 정의,
  Copilot agent는 "GitHub가 대신 코드를 고쳐 PR을 내는" 외부 실행자.
- **판정**: 핵심 체인(모델링·조달 판단 — HITL §6)에는 편입 금지. 도입한다면 잡무성
  수정(lint·경로 버그)을 이슈 할당으로 위임하고 draft PR을 C-05 리뷰에 태우는 실험
  수준 — 단 ①유료 구독 필요 ②Actions 분이 데이터 파이프라인과 예산 공유
  ③11월 Actions 정지와 충돌이라 **현 시점 비권장, 이관 후 재평가**.

## 실행 현황 (이번 회차)

- 세션에서 실행 가능한 것: **없음**(Projects·Wiki 모두 웹 UI 수동 설정 필요 —
  위 ① 권장 구성 절차 참조). 이슈 발행 자동화는 기존 MCP로 이미 가능(Ralph Loop 가동 중).
- 조정자 액션 필요: ①Projects 보드 생성+auto-add 2건(15분, 위 절차) ②Wiki는 결정
  보류 권고 ③Copilot 구독은 현 시점 비권장.

**출처**: GitHub 공식 문서·changelog·커뮤니티 공식 답변 (조사 에이전트 보고 원문에 URL
전체 수록 — 세션 기록 wf_f8fc3682-a12).
