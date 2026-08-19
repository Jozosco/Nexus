#!/usr/bin/env python3
"""시장구조 브리프 Perplexity Deep Research 교차검증 (A-189 · 조정자 지시 2026-08-19).

대상: data/raw/Market Structure (Production & Distribution)/
      Global Oilseeds & Fats Market Structure_26.08.19.docx

조정자 지시: "Perplexity Deep Research로 파일 내용을 철저히 교차검증하고,
프로젝트 전 단계에서 이 정보를 염두에 둘 것."

동작: docx 본문을 추출해 5개 주제(수급·한국수입·기업자산·아르헨수출·바이오연료정책)로
      나눠 sonar-deep-research에 검증 질의 → 주제별 판정을 하나의 보고서로 저장.
      쿼리별 실패는 비치명(부분 보고 저장) — 전 쿼리 실패 시에만 종료코드 1.

⚠️ 비용: sonar-deep-research는 고비용 모델 — 이 스크립트는 수동/1회성 실행 전용
   (스케줄 편입 금지 — CI-004 크레딧 관리 원칙).

출력: docs/research_desk/2026-08/market_structure_deep_verify_{날짜}.md
"""
from __future__ import annotations

import os
import re
import sys
import zipfile
from datetime import date
from pathlib import Path

import httpx

DOCX = Path("data/raw/Market Structure (Production & Distribution)/"
            "Global Oilseeds & Fats Market Structure_26.08.19.docx")
OUT_DIR = Path("docs/research_desk/2026-08")
MODEL = "sonar-deep-research"          # L-007: 구 huge — 심층 조사 전용
API_URL = "https://api.perplexity.ai/chat/completions"
PER_QUERY_TIMEOUT_S = 1800             # deep research는 질의당 수 분~수십 분

# 주제별 검증 질의 — 문서의 핵심 수치·사실 주장을 명시적으로 나열해 반증을 요구
THEMES: list[tuple[str, str]] = [
    ("글로벌 수급·수출 집중도", """다음 주장들을 최신 공식 출처(USDA FAS Oilseeds WMT 2026-08 등)로 검증하라:
① 2026/27 전망 생산량: 팜유 81.44Mt · 대두유 75.03Mt · 유채유 37.60Mt · 해바라기유 23.57Mt (주요 식물성유지 244.95Mt의 88.9%)
② 수출 집중도(2026/27): 팜유 인도네시아 23.70Mt+말레이시아 15.90Mt=세계 수출 45.31Mt의 87.4% · 대두유 아르헨티나 6.65Mt=세계 14.64Mt의 45.4% · 카놀라유 캐나다 4.00Mt=8.71Mt의 45.9% · 해바라기유 러시아 5.00Mt+우크라이나 4.95Mt=15.67Mt의 63.5%
③ FAO 식물성유지 가격지수 2026-07 = 195.7 (전월비 +2.0%, 2022-06 이후 최고)"""),
    ("한국 수입 구조", """다음 한국 수입 통계 주장을 검증하라(USDA FAS Seoul Oilseeds Annual 2026-03, UN Comtrade, 관세청):
① 한국 MY2024/25 완결연도 수입: 팜유 586kt(CIF 1,087$/t) · 대두유 482kt(1,120$/t) · 유채유 152kt(1,103$/t) · 해바라기유 37kt(1,718$/t)
② 대두유 원산지(MY24/25): 미국 84,686t(17.6%) · 아르헨티나 153,122t(31.7%) · 베트남 132,764t(27.5%); MY25/26 10~1월 부분기간은 베트남 45.9%
③ UN Comtrade 2024 CY: 조대두유(HS150710) 277,913t — 아르헨 195,655t·베트남 62,397t·미국 12,003t; 정제팜유(HS151190) 625,192t — 말레이 395,608t·인니 229,203t"""),
    ("ABCD·COFCO 기업 자산", """다음 기업 자산·공시 주장을 각사 최신 공시(10-K·연차보고서 등)로 검증하라:
① ADM 2025: AS&O 가공능력 169kt/day · 2025년 유지종자 36.324Mt 가공 · 저장 16.590Mt
② Bunge(Viterra 포함, 2025-12-31): 대두 가공 35개소·정제 22개소·193,165 t/day · 대두 항만터미널 17 · Viterra 합병 2025-07-02 종결 · 캐나다 시정조치(엘리베이터 6개 매각 등)
③ Cargill: 남미 대두 네트워크 가공공장 14 · 남미 항만 13 · Regina 카놀라 1.0Mt/yr (2026-04 개소)
④ LDC: General Lagos 대두 2.5Mt/yr·바이오디젤 0.6Mt/yr · Timbues 복수유지 라인(2026-01) · Bahia Blanca 신공장 발표(2026-06)
⑤ COFCO Intl 2025: 가공 35.6Mt · 항만 28.7Mt · 3자 판매 100.4Mt · Santos STS11 목표 14.5Mt/yr"""),
    ("아르헨티나 수출·가격", """다음 아르헨티나 공식 통계 주장을 검증하라(농업사무국 Law 21.453 수출자 순위·FOB 공시·DJVE):
① 2025년 법인별 대두유 수출: Viterra Argentina 1,496,325t · Cargill 1,171,480t · LDC 716,462t · COFCO 689,036t · Bunge Argentina 200,047t
② 아르헨티나 조대두유 공식 FOB 2026-08-04 = USD 1,187/t
③ 2026-07 DJVE 대두유 판매등록 사례: COFCO 15,000t · Bunge 6,300/6,800/3,800t · Cargill 4,000t · LDC 5,000t"""),
    ("바이오연료 정책·수요", """다음 바이오연료 정책·수요 주장을 검증하라(EPA·EIA·인니 에너지광물자원부):
① EPA RFS 최종 BBD 의무량: 2026년 9.07bn RINs · 2027년 9.20bn RINs
② EIA 2026-05 미국 바이오연료 원료 투입: 대두유 1,434백만lb(바이오디젤 747/재생디젤 687) · 우지 796 · UCO 605 · 옥수수유 457 · 카놀라유 293
③ 인도네시아 B50(2026-07 발표): 바이오디젤 16.7~18.0백만kL · CPO 소요 15.2~16.3Mt 전망"""),
]

SYSTEM = """당신은 원자재 시장 사실검증 전문가다. 제시된 주장 각각에 대해:
- 판정: ✅확인 / ⚠️부분확인(차이 명시) / ❌불일치(올바른 값 제시) / ❓검증불가
- 근거 출처(기관·문서·날짜)를 판정마다 명시
- 수치가 다르면 정확한 값과 출처를 제시
한국어로 답하되 기관·문서명은 원어 유지. 추측 금지 — 확인 불가면 ❓로 표기."""


def _extract_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    paras = re.findall(r"<w:p[ >].*?</w:p>", xml, re.S)
    lines = []
    for para in paras:
        t = "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", para, re.S))
        t = (t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
              .replace("&quot;", '"').replace("&apos;", "'"))
        lines.append(t)
    return "\n".join(lines)


def _deep_research(client: httpx.Client, key: str, theme: str, claims: str) -> str:
    resp = client.post(
        API_URL,
        headers={"Authorization": f"Bearer {key}"},
        json={"model": MODEL,
              "messages": [{"role": "system", "content": SYSTEM},
                           {"role": "user", "content": f"[검증 주제] {theme}\n\n{claims}"}]},
        timeout=PER_QUERY_TIMEOUT_S)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def main() -> int:
    key = os.environ.get("PERPLEXITY_API_KEY", "").strip()
    if not key:
        print("[오류] PERPLEXITY_API_KEY 미설정 — Deep Research 검증 불가")
        return 1
    if not DOCX.exists():
        print(f"[오류] 대상 문서 없음: {DOCX}")
        return 1

    doc_chars = len(_extract_docx_text(DOCX))
    print(f"[정보] 대상 문서 {doc_chars:,}자 · 주제 {len(THEMES)}개 · 모델 {MODEL}")

    sections, ok, fail = [], 0, 0
    with httpx.Client() as client:
        for theme, claims in THEMES:
            print(f"[진행] Deep Research: {theme} …")
            try:
                verdict = _deep_research(client, key, theme, claims)
                sections.append(f"## {theme}\n\n{verdict}\n")
                ok += 1
                print(f"  ✅ 판정 수신 ({len(verdict):,}자)")
            except Exception as e:                       # 쿼리별 비치명 — 부분 보고 보존
                sections.append(f"## {theme}\n\n⚠️ **검증 실패** — `{type(e).__name__}`: {e}\n"
                                f"이 주제는 검증되지 않았습니다. 재실행 필요.\n")
                fail += 1
                print(f"  ❌ 실패({type(e).__name__}): {e}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"market_structure_deep_verify_{date.today()}.md"
    out.write_text(
        f"# 시장구조 브리프 Deep Research 교차검증 — {date.today()}\n\n"
        f"- **대상**: `{DOCX.name}` (조정자 업로드 · 컷오프 2026-08-19 17:41 KST)\n"
        f"- **모델**: Perplexity `{MODEL}` · 주제 {len(THEMES)}개 중 판정 {ok} · 실패 {fail}\n"
        f"- **지시**: 조정자 2026-08-19 — 브리프 내용의 철저한 교차검증\n\n---\n\n"
        + "\n---\n\n".join(sections), encoding="utf-8")
    print(f"[완료] 보고서 → {out} (판정 {ok}/{len(THEMES)})")
    return 0 if ok > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
