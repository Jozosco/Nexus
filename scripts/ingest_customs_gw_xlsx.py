#!/usr/bin/env python3
"""
관세청 품목별 국가별 수출입실적(GW) — 대체재·보완재 HS코드 수집 (WBS 1.1.48 · A-069)

목적(조정자 Req 2.1): 대두유 대체재(타 식용유)·보완재(대두·대두박·바이오디젤) HS코드의
한국 수출입 실적을 관세청 API로 수집해 **품목별 .xlsx** 생성. HS 선정 근거:
docs/research_desk/session34_data_selection_2026_07_10.md §3.

엔드포인트: http://apis.data.go.kr/1220000/nitemtrade/getNitemtradeList  (XML)
인증: 환경변수 DATA_GO_KR_SERVICE_KEY  (⚠️ 코드/저장소에 키 하드코딩 금지 — CLAUDE.md §2)
파라미터: strtYymm·endYymm(YYYYMM) · hsSgn(HS 2/4/6/10자리) · cntyCd(국가, 선택)

응답 필드: impDlr(수입 USD·CIF) · impWgt(수입 kg) · expDlr(수출 USD·FOB) · expWgt ·
           hsCd · statCd(국가) · statKor(품목명) · year(YYYY.MM)

출력: data/raw/관세청/Import Export Performance by Commodity and Country(GW)/{Commodity}.xlsx
      + 통합 data/raw/customs_gw_historical.parquet

⚠️ 실행 환경: 이 스크립트는 data.go.kr 접근이 가능한 GitHub Actions에서 실행.
   (개발 샌드박스 프록시는 apis.data.go.kr 차단 — A-069)

의존성: httpx · pandas · openpyxl
"""
from __future__ import annotations

import os
import time
import re
from pathlib import Path
from xml.etree import ElementTree as ET

import httpx
import pandas as pd

BASE_URL = "http://apis.data.go.kr/1220000/nitemtrade/getNitemtradeList"
OUT_DIR  = Path("data/raw/관세청/Import Export Performance by Commodity and Country(GW)")
PARQUET  = Path("data/raw/customs_gw_historical.parquet")

START_YEAR = int(os.environ.get("HISTORICAL_START_YEAR", "2010"))
END_YEAR   = int(os.environ.get("HISTORICAL_END_YEAR", "2026"))

# 품목 → HS코드 (session34 §3 대체재·보완재)
HS_COMMODITIES: dict[str, list[str]] = {
    # 대체재 (타 식용유)
    "Palm_Oil":        ["1511"],
    "Sunflower_Oil":   ["151211", "151219"],
    "Rapeseed_Oil":    ["151411", "151419"],
    "PalmKernel_Oil":  ["151321", "151329"],
    "Coconut_Oil":     ["151311", "151319"],
    "Cottonseed_Oil":  ["151221", "151229"],
    # 보완재·업스트림·연관
    "Soybean":         ["120110", "120190"],
    "Soybean_Meal":    ["2304"],
    "Biodiesel":       ["3826"],
    "Glycerol":        ["1520"],
    # 확보 대두유(참조 재수집)
    "Soybean_Oil":     ["1507101000", "1507102000", "1507901010", "1507901020"],
}
# 주요 원산지 (빈 리스트면 전체 국가 집계)
COUNTRIES = ["US", "CN", "BR", "AR", "MY", "ID", "UA"]


def _fetch(hs: str, yymm_start: str, yymm_end: str, cnty: str | None,
           max_retries: int = 4) -> list[dict]:
    key = os.environ.get("DATA_GO_KR_SERVICE_KEY", "").strip()
    if not key:
        raise RuntimeError("[오류] DATA_GO_KR_SERVICE_KEY 미등록 — GitHub Secrets 등록 필요")
    params = {"serviceKey": key, "strtYymm": yymm_start,
              "endYymm": yymm_end, "hsSgn": hs}
    if cnty:
        params["cntyCd"] = cnty
    delay = 2
    for attempt in range(max_retries):
        try:
            r = httpx.get(BASE_URL, params=params, timeout=40)
            r.raise_for_status()
            root = ET.fromstring(r.text)
            code = root.findtext(".//resultCode")
            if code not in ("00", None):
                msg = root.findtext(".//resultMsg")
                print(f"    [경고] {hs}/{cnty}: resultCode={code} {msg}")
                return []
            rows = []
            for it in root.findall(".//item"):
                yr = it.findtext("year", "")
                if "총계" in yr or it.findtext("hsCd") in ("-", None):
                    continue
                rows.append({
                    "year_month": yr, "hs_code": it.findtext("hsCd"),
                    "country": it.findtext("statCd"),
                    "country_kr": it.findtext("statCdCntnKor1"),
                    "item_kr": it.findtext("statKor"),
                    "imp_usd": pd.to_numeric(it.findtext("impDlr"), errors="coerce"),
                    "imp_wgt_kg": pd.to_numeric(it.findtext("impWgt"), errors="coerce"),
                    "exp_usd": pd.to_numeric(it.findtext("expDlr"), errors="coerce"),
                    "exp_wgt_kg": pd.to_numeric(it.findtext("expWgt"), errors="coerce"),
                })
            return rows
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(delay); delay *= 2; continue
            print(f"    [경고] {hs}/{cnty} 수집 실패: {e}")
            return []


def fetch_commodity(commodity: str, hs_list: list[str]) -> pd.DataFrame:
    print(f"[C-03] {commodity}: HS {hs_list} 수집...")
    records: list[dict] = []
    targets = COUNTRIES or [None]
    for hs in hs_list:
        for cnty in targets:
            for yr in range(START_YEAR, END_YEAR + 1):
                rows = _fetch(hs, f"{yr}01", f"{yr}12", cnty)
                for row in rows:
                    row["commodity"] = commodity
                    records.append(row)
                time.sleep(0.3)
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    # year_month 'YYYY.MM' → price_date
    df["price_date"] = pd.to_datetime(df["year_month"].str.replace(".", "-", regex=False),
                                      format="%Y-%m", errors="coerce")
    df["source_name"] = "KoreaCustoms_GW"
    df["ingested_at"] = pd.Timestamp.now("UTC")
    return df.dropna(subset=["price_date"]).reset_index(drop=True)


def run() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_frames = []
    for commodity, hs_list in HS_COMMODITIES.items():
        df = fetch_commodity(commodity, hs_list)
        if df.empty:
            print(f"  [정보] {commodity}: 데이터 없음")
            continue
        # tz 제거 후 품목별 xlsx
        xl = df.copy()
        xl["ingested_at"] = xl["ingested_at"].dt.tz_localize(None)
        out = OUT_DIR / f"{commodity}.xlsx"
        xl.to_excel(out, index=False)
        all_frames.append(df)
        print(f"  [xlsx] {out.name}: {len(df):,}행 "
              f"({df['price_date'].min().date()}~{df['price_date'].max().date()})")
    if all_frames:
        combined = pd.concat(all_frames, ignore_index=True)
        combined.to_parquet(PARQUET, index=False)
        print(f"\n[완료] → {PARQUET} ({len(combined):,}행, {combined['commodity'].nunique()}품목)")


if __name__ == "__main__":
    run()
