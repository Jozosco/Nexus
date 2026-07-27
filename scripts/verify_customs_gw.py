#!/usr/bin/env python3
"""
관세청 GW 대두유 데이터 교차검증 (WBS 1.1.49 · A-072)

배경(조정자 Req): 업로드 GW 시트에 빈 행/0값이 많아 분석 전 교차검증 필요.
교차검증 기준(C-02·C-03·P1-01~04 협의):
  ① 0 vs 결측 구분: 수출액/수출량=0 은 **정상**(한국은 대두유 수입국 — 對상대국 수출 거의 없음).
     NaN = 진짜 결측(미래월·미신고).
  ② 무역수지 항등식: 무역수지(달러) ≈ 수출액 − 수입액 (허용오차 1달러).
  ③ 합계 정합: 통합본(16years) 수입량 ≥ 4개국(US·BR·AR·CN) 합 (통합은 전세계).
  ④ 커버리지: 연·월별 수입량 유효(>0) 비율 → 분석 가용 구간 판정.

입력: data/raw/관세청/Import Export Performance by Commodity and Country(GW)/**/*.xlsx
출력: 콘솔 리포트 + data/raw/customs_gw_verification.parquet (셀 단위 진단)

의존성: pandas · openpyxl
"""
from __future__ import annotations

import glob
import re
from pathlib import Path

import pandas as pd

GW_ROOT = Path("data/raw/관세청/Import Export Performance by Commodity and Country(GW)")
_MONTH_RE = re.compile(r"(\d{1,2})\s*월")
_COLS = ["무역수지", "수출액", "수출량", "수입액", "수입량"]


def _parse_file(path: Path) -> pd.DataFrame:
    recs = []
    try:
        xl = pd.ExcelFile(path)
    except Exception as e:
        print(f"  [오류] {path.name}: {e}")
        return pd.DataFrame()
    for sheet in xl.sheet_names:
        ym = re.search(r"(\d{4})", str(sheet))
        if not ym:
            continue
        year = int(ym.group(1))
        raw = xl.parse(sheet, header=None)
        # 헤더행 탐지(무역수지 포함 행), 그 아래 월 데이터
        hdr = next((i for i in range(min(5, len(raw)))
                    if raw.iloc[i].astype(str).str.contains("무역수지").any()), None)
        if hdr is None:
            continue
        for r in range(hdr + 1, len(raw)):
            mm = _MONTH_RE.search(str(raw.iloc[r, 0]))
            if not mm:
                continue
            month = int(mm.group(1))
            vals = [pd.to_numeric(raw.iloc[r, c], errors="coerce") for c in range(1, 6)]
            recs.append({"file": path.stem, "hs_folder": path.parent.parent.name,
                         "use": path.parent.name, "year": year, "month": month,
                         **{col: v for col, v in zip(_COLS, vals)}})
    return pd.DataFrame(recs)


def run() -> None:
    files = [Path(f) for f in sorted(glob.glob(str(GW_ROOT / "**" / "*.xlsx"), recursive=True))]
    if not files:
        print("[경고] GW 파일 없음."); return
    frames = [_parse_file(f) for f in files]
    df = pd.concat([x for x in frames if not x.empty], ignore_index=True)

    print(f"[C-03] 관세청 GW 교차검증 — {len(files)}개 파일 · {len(df):,}행(월)\n")

    # ① 0 vs 결측
    imp = df["수입량"]
    print("① 수입량 셀 진단:")
    print(f"   유효(>0): {(imp > 0).sum():,} · 0값: {(imp == 0).sum():,} · 결측(NaN): {imp.isna().sum():,}")
    print(f"   수출량 0값(정상=수입국): {(df['수출량'] == 0).sum():,} / 유효 {(df['수출량'] > 0).sum():,}\n")

    # ② 무역수지 항등식
    bal = df.dropna(subset=["무역수지", "수출액", "수입액"]).copy()
    bal["resid"] = (bal["무역수지"] - (bal["수출액"] - bal["수입액"])).abs()
    ok = (bal["resid"] <= 1).sum()
    print(f"② 무역수지 = 수출액−수입액 정합: {ok:,}/{len(bal):,} "
          f"({ok/max(len(bal),1)*100:.1f}%) · 불일치 {len(bal)-ok:,}\n")

    # ③ 통합본 vs 4개국 합 (수입량, HS·용도별)
    print("③ 통합본 vs 4개국 합 (연 수입량 합, 용도별):")
    for (hs, use), g in df.groupby(["hs_folder", "use"]):
        comb = g[g["file"].str.contains("16years")]["수입량"].sum()
        ctry = g[~g["file"].str.contains("16years")]["수입량"].sum()
        flag = "✅ 통합≥합" if comb >= ctry * 0.99 else "⚠️ 통합<합(확인)"
        print(f"   {hs}/{use[:18]:18s} 통합 {comb/1e6:8.1f}M · 4개국 {ctry/1e6:8.1f}M kg  {flag}")

    # ④ 커버리지(연도별 유효 수입량 비율) — 국가 파일만
    print("\n④ 연도별 수입량 커버리지(국가 파일):")
    cf = df[~df["file"].str.contains("16years")]
    cov = cf.groupby("year")["수입량"].apply(lambda s: (s > 0).mean() * 100)
    print("   " + " · ".join(f"{int(y)}:{v:.0f}%" for y, v in cov.items()))

    out = Path("data/raw/customs_gw_verification.parquet")
    df.to_parquet(out, index=False)
    print(f"\n[완료] 셀 단위 진단 → {out}")


if __name__ == "__main__":
    run()
