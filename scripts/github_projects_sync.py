#!/usr/bin/env python3
"""GitHub Projects v2 GraphQL 동기화 (조정자 승인 2026-08-25 · A-211).

Projects v2 API는 GraphQL 전용(REST 없음 — R-023 실측)이며 통합 토큰으로는 접근이
안 될 가능성이 높아(A-146 전례) **classic PAT(project scope)** 를 사용한다.

동작: `decision-request`·`pipeline-failure` 라벨의 열린 이슈를 지정 프로젝트 보드에
추가한다(이미 있으면 GitHub이 멱등 처리). Projects의 auto-add 내장 워크플로가 있으면
이 스크립트 없이도 편입되지만, auto-add는 필터당 1개 제한·지연이 있어 GraphQL 경로를
보완으로 둔다(UI/UX 커스텀 필드 확장 시 이 스크립트가 유일한 자동화 경로).

필요 환경변수:
  PROJECTS_PAT     — classic PAT, scopes: project, repo(read) — GitHub Secrets 등재
  PROJECT_NUMBER   — 조정자가 웹 UI에서 만든 프로젝트 번호(URL의 /projects/{N})
미설정 시 안내만 출력하고 정상 종료(비치명 — 파이프라인을 막지 않는다).
"""
from __future__ import annotations

import json
import os
import sys

import httpx

OWNER = "Jozosco"
REPO = "Nexus"
LABELS = ["decision-request", "pipeline-failure"]
API = "https://api.github.com/graphql"


def _gql(token: str, query: str, variables: dict) -> dict:
    r = httpx.post(API, timeout=30,
                   headers={"Authorization": f"Bearer {token}"},
                   json={"query": query, "variables": variables})
    r.raise_for_status()
    out = r.json()
    if out.get("errors"):
        raise RuntimeError(f"[오류] GraphQL: {json.dumps(out['errors'], ensure_ascii=False)[:400]}")
    return out["data"]


def main() -> int:
    token = os.environ.get("PROJECTS_PAT", "").strip()
    number = os.environ.get("PROJECT_NUMBER", "").strip()
    if not token or not number:
        print("[정보] PROJECTS_PAT / PROJECT_NUMBER 미설정 — Projects 동기화 건너뜀.")
        print("       조정자 액션: ①웹 UI에서 프로젝트 생성(권장 구성: github_features_adoption §①)")
        print("       ②classic PAT(project scope) 발급 → Secrets PROJECTS_PAT ③번호 → PROJECT_NUMBER")
        return 0

    # 사용자 소유 프로젝트 조회 (owner가 org면 organization으로 교체)
    data = _gql(token, """
      query($login:String!, $number:Int!) {
        user(login:$login) { projectV2(number:$number) { id title } }
      }""", {"login": OWNER, "number": int(number)})
    proj = (data.get("user") or {}).get("projectV2")
    if not proj:
        print(f"[경고] 프로젝트 #{number} 미발견(user 스코프) — 번호·PAT 권한 확인 필요")
        return 0
    print(f"[정보] 프로젝트: {proj['title']} ({proj['id']})")

    added = 0
    for label in LABELS:
        data = _gql(token, """
          query($owner:String!, $repo:String!, $label:String!) {
            repository(owner:$owner, name:$repo) {
              issues(first: 50, states: OPEN, labels: [$label]) {
                nodes { id number title }
              }
            }
          }""", {"owner": OWNER, "repo": REPO, "label": label})
        for issue in data["repository"]["issues"]["nodes"]:
            _gql(token, """
              mutation($project:ID!, $content:ID!) {
                addProjectV2ItemById(input:{projectId:$project, contentId:$content}) {
                  item { id }
                }
              }""", {"project": proj["id"], "content": issue["id"]})
            print(f"[완료] #{issue['number']} {issue['title'][:50]} → 보드 추가(멱등)")
            added += 1
    print(f"[완료] Projects 동기화 — 이슈 {added}건 처리")
    return 0


if __name__ == "__main__":
    sys.exit(main())
