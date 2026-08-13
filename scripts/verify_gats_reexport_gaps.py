#!/usr/bin/env python3
"""
GATS 재수출 결측 연도 검증 (A-086) — "무역 부재" vs "미보고" 판별

배경(조정자 Req): 일부 HTS·연도에 재수출량 데이터가 없음. 실제 거래가 없었던 것인지
(=정상 0), 보고 누락인지 판별해야 분석에서 0/NaN 처리를 올바르게 할 수 있다(D4 원칙).

판별 기준(C-02 협의):
  ① 파일 자체 부재  → '미수집'(수집 범위 문제 — 재다운로드 대상)
  ② 파일 존재·전 국가 0 → '무역 부재'(정상 0 — 대체 금지, 0으로 보존)
  ③ 파일 존재·행 없음/헤더만 → '미보고'(USDA 미공표 — NaN 유지)
사용: python scripts/verify_gats_reexport_gaps.py
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

BASE = Path("data/raw/USDA/FAS/GATS/Oilseeds/Soybean Oil/Exports & Re-Exports")
TARGETS = {
    "1507.10.0000": [2010, 2016, 2018],
    "1507.90/.4020": [2012, 2013, 2014, 2020, 2021],
    "1517.90.4035": [2010, 2020, 2026],
}


def run() -> None:
    print("[C-02] GATS 재수출 결측 연도 검증 — 무역부재 vs 미보고\n")
    rows = []
    for hts, years in TARGETS.items():
        d = BASE / hts
        files = sorted(d.rglob("*")) if d.exists() else []
        data_files = [f for f in files if f.suffix.lower() in (".csv", ".xlsx")]
        for yr in years:
            hit = [f for f in data_files if str(yr) in f.name]
            if not hit:
                verdict, note = "미수집", "해당 연도 파일 없음 — 재다운로드 대상"
            else:
                f = hit[0]
                try:
                    # GATS csv는 상단 메타 행 존재 → 헤더 자동 탐지(최대 10행 스킵)
                    if f.suffix.lower() == ".csv":
                        df = None
                        for skip in range(0, 10):
                            try:
                                cand = pd.read_csv(f, encoding="utf-8-sig", skiprows=skip)
                                if cand.shape[1] >= 2:
                                    df = cand; break
                            except Exception:
                                continue
                        if df is None:
                            raise ValueError("헤더 탐지 실패")
                    else:
                        df = pd.read_excel(f)
                    num = df.select_dtypes("number")
                    if df.empty or num.empty:
                        verdict, note = "미보고", "행 없음/수치열 없음 — NaN 유지"
                    elif float(num.fillna(0).to_numpy().sum()) == 0.0:
                        verdict, note = "무역 부재", "전 국가 0 — 정상 0으로 보존(대체 금지)"
                    else:
                        verdict, note = "데이터 존재", f"합계 {num.fillna(0).to_numpy().sum():,.0f}"
                except Exception as e:
                    verdict, note = "판독 실패", str(e)[:60]
            rows.append({"HTS": hts, "연도": yr, "판정": verdict, "비고": note})
            print(f"  {hts:16s} {yr}  {verdict:8s}  {note}")
    out = Path("reports/market/gats_reexport_gap_verification.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("# GATS 재수출 결측 연도 검증 (A-086)\n\n"
                   "> 판정 기준: 미수집(파일 부재) · 무역 부재(전 국가 0 — 정상) · 미보고(행 없음)\n\n"
                   + "| HTS | 연도 | 판정 | 비고 |\n|---|---|---|---|\n"
                   + "\n".join(f"| {r['HTS']} | {r['연도']} | {r['판정']} | {r['비고']} |"
                                for r in rows) + "\n", encoding="utf-8")
    print(f"\n[완료] → {out}")


if __name__ == "__main__":
    run()
