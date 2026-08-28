#!/usr/bin/env python3
"""관세청 무역 부재 쌍 교차검증 프로빙 (조정자 요청 2026-08-26 · A-215).

조정자 수작업에서 '조회 데이터 없음'으로 파일이 생성되지 않은 (10단위 세번 × 국가)
13쌍을 관세청 API로 전 기간(2010~2026) 실측해 무역 부재를 확정하거나, 데이터가
있으면 연·월·값을 정리한다. XML 응답 대응(A-152)·10단위 hsSgn(A-196).

산출: reports/market/customs_absent_pairs_verification_{날짜}.md
      + 데이터 발견 시 reports/market/customs_absent_pairs_found_{날짜}.csv
"""
from __future__ import annotations

import os
import sys
import time
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

import httpx

BASE = "http://apis.data.go.kr/1220000/nitemtrade/getNitemtradeList"
YEARS = range(2010, 2027)
# 조정자 부재 목록 (2026-08-26) — 세번 10자리 × ISO 국가코드
# 1차(1201.90 13쌍)는 2026-08-26 검증 완결(전건 부재 확인) — 2차: 팜·유채·바이오디젤
ABSENT_PAIRS: dict[str, list[str]] = {
    "1511901000": ["AR", "NL", "PY", "ES"],      # 팜 올레인
    "1511902000": ["US", "AR", "BR", "PY"],      # 팜 스테아린
    "1511909000": ["PY"],                        # 팜 기타(RBD 포함)
    "1514111000": ["BR", "PY"],                  # 유채 조유(저에루크산)
    "3826000000": ["AR", "PY"],                  # 바이오디젤
}
CODE_LABEL = {"1511901000": "팜 올레인(.1000)", "1511902000": "팜 스테아린(.2000)",
              "1511909000": "팜 기타(.9000)", "1514111000": "유채 조유(1514.11)",
              "3826000000": "바이오디젤(3826.00)"}


def _fetch_year(client: httpx.Client, key: str, hs: str, cc: str, year: int) -> list[dict]:
    params = {"serviceKey": key, "strtYymm": f"{year}01", "endYymm": f"{year}12",
              "hsSgn": hs, "cntyCd": cc}
    for attempt in range(3):
        try:
            r = client.get(BASE, params=params, timeout=httpx.Timeout(30, connect=10))
            r.raise_for_status()
            break
        except Exception as e:
            if attempt == 2:
                print(f"[경고] {hs}×{cc} {year}: 호출 실패 — {type(e).__name__}")
                return [{"_error": str(e)}]
            time.sleep(3 * (attempt + 1))
    try:
        root = ET.fromstring(r.content)
    except ET.ParseError:
        print(f"[경고] {hs}×{cc} {year}: XML 파싱 실패")
        return [{"_error": "xml_parse"}]
    rc = root.findtext(".//resultCode")
    if rc not in (None, "00"):
        msg = root.findtext(".//resultMsg") or ""
        print(f"[경고] {hs}×{cc} {year}: resultCode={rc} {msg[:60]}")
        return [{"_error": f"rc={rc}"}]
    rows = []
    for item in root.iter("item"):
        d = {ch.tag: (ch.text or "").strip() for ch in item}
        # 합계(국가명 '총계' 류)·헤더성 행 제외 — 실 데이터 행만
        if d.get("year") and any(d.get(k) for k in ("impWgt", "impDlr", "expWgt", "expDlr")):
            rows.append(d)
    return rows


def main() -> int:
    key = os.environ.get("DATA_GO_KR_SERVICE_KEY", "").strip()
    if not key:
        print("[오류] DATA_GO_KR_SERVICE_KEY 미설정 — 프로빙 불가")
        return 1
    from urllib.parse import unquote
    if "%" in key:
        key = unquote(key)

    # A-222: 2차 프로빙이 잡 timeout-minutes 30에 30분 정각 취소(런 33169143433 —
    # KST 20:57 저녁 발화 = data.go.kr 저녁 장애 시간대, A-161 패턴). 실패 시 재시도
    # 대기가 누적돼 잡 강제 종료 → 커밋 스텝 skip으로 수집분 전량 유실.
    # 스크립트 자체 시간 예산으로 잡 종료 전에 부분 결과를 저장한다.
    budget_s = int(os.environ.get("PROBE_TIME_BUDGET_S", "1500"))
    t0 = time.monotonic()
    results: list[dict] = []
    found_rows: list[dict] = []
    untried: list[tuple[str, str]] = []
    errors = 0
    with httpx.Client() as client:
        for hs, ccs in ABSENT_PAIRS.items():
            for cc in ccs:
                if time.monotonic() - t0 > budget_s:
                    untried.append((hs, cc))
                    continue
                recs_all: list[dict] = []
                pair_err = 0
                for yr in YEARS:
                    recs = _fetch_year(client, key, hs, cc, yr)
                    if recs and "_error" in recs[0]:
                        pair_err += 1
                    else:
                        recs_all += recs
                    time.sleep(0.4)
                imp_wgt = sum(float(r.get("impWgt", 0) or 0) for r in recs_all)
                imp_dlr = sum(float(r.get("impDlr", 0) or 0) for r in recs_all)
                exp_wgt = sum(float(r.get("expWgt", 0) or 0) for r in recs_all)
                verdict = ("⚠️ 호출 실패 다수 — 재실행 필요" if pair_err >= 9 else
                           "✅ 무역 부재 확인" if imp_wgt == 0 and imp_dlr == 0 and exp_wgt == 0 else
                           "🚨 데이터 존재 — 보완 필요")
                results.append({"hs": hs, "cc": cc, "records": len(recs_all),
                                "imp_wgt": imp_wgt, "imp_dlr": imp_dlr,
                                "exp_wgt": exp_wgt, "errors": pair_err, "verdict": verdict})
                if imp_wgt or imp_dlr or exp_wgt:
                    for r in recs_all:
                        if any(float(r.get(k, 0) or 0) for k in ("impWgt", "impDlr", "expWgt", "expDlr")):
                            found_rows.append({"hs": hs, "cc": cc, **r})
                errors += pair_err
                print(f"[완료] {hs}×{cc}: 레코드 {len(recs_all)} · 수입 {imp_wgt:,.0f}kg/${imp_dlr:,.0f} · {verdict}")

    today = date.today()
    suffix = os.environ.get("PROBE_SUFFIX", "")
    out = Path(f"reports/market/customs_absent_pairs_verification_{today}{suffix}.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# 관세청 무역 부재 쌍 교차검증 — {today} (A-215)", "",
             "조정자 수작업에서 파일이 생성되지 않은 13쌍의 API 전 기간(2010~2026) 실측.", "",
             "| 세번 | 품명 | 국가 | 레코드 | 수입중량(kg) | 수입금액($) | 수출중량(kg) | 판정 |",
             "|---|---|---|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['hs']} | {CODE_LABEL[r['hs']]} | {r['cc']} | {r['records']} | "
                     f"{r['imp_wgt']:,.0f} | {r['imp_dlr']:,.0f} | {r['exp_wgt']:,.0f} | {r['verdict']} |")
    n_absent = sum(1 for r in results if "무역 부재" in r["verdict"])
    n_found = sum(1 for r in results if "데이터 존재" in r["verdict"])
    n_fail = sum(1 for r in results if "호출 실패" in r["verdict"])
    lines += ["", f"**요약**: 무역 부재 확인 {n_absent} · 데이터 존재(보완 필요) {n_found} · "
              f"호출 실패 {n_fail} / 총 {len(results)}쌍 (호출 오류 연도 {errors}건)",
              "", "무역 부재 = 전 기간 수입·수출 실적 0 (A-086 원칙: 부재는 정보 — 파일 미생성이 정확)."]
    if untried:
        pairs_txt = " · ".join(f"{h}×{c}" for h, c in untried)
        lines += ["", f"⏳ **시간 예산({budget_s}s) 소진으로 미시도 {len(untried)}쌍**: {pairs_txt}",
                  "재실행(workflow_dispatch — KST 주간 권장: data.go.kr 저녁 장애 시간대 회피, A-161)으로 잔여 확정 필요."]
        print(f"[경고] 시간 예산 소진 — 미시도 {len(untried)}쌍(부분 결과는 저장됨)")
    if found_rows:
        import csv
        fp = Path(f"reports/market/customs_absent_pairs_found_{today}{suffix}.csv")
        with open(fp, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=sorted({k for r in found_rows for k in r}))
            w.writeheader()
            w.writerows(found_rows)
        lines.append(f"\n발견 데이터 상세: `{fp.name}` ({len(found_rows)}행) — 조정자 템플릿 형식 삽입 대상.")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[완료] → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
