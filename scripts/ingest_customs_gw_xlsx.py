#!/usr/bin/env python3
"""
관세청 품목별 국가별 수출입실적(GW) — 대체·보완재 확장 수집 (WBS 1.1.48 · A-069/A-073)

목적(조정자 Req): 대두유 외 **대체재·보완재**와 **추가 원산지**의 한국 수출입 실적을 관세청 API로
수집해, 기존 업로드본과 **완전히 동일한 형식**(연도별 시트 × 월별 행 × 5개 지표 열)으로 저장.

저장 규칙(조정자 지정):
  data/raw/관세청/Import Export Performance by Commodity and Country(GW)/
      {품목명 (HS코드)}/{국가}.xlsx
  예) 'Palm Oil (1511)/China.xlsx' · 'Soybean (1201.90)/Brazil.xlsx'
  시트: '{YYYY}년' · 행: '{M}월' · 열: 무역수지(달러)·수출액(달러)·수출량(kg)·수입액(달러)·수입량(kg)

엔드포인트: http://apis.data.go.kr/1220000/nitemtrade/getNitemtradeList  (REST, XML)
인증: 환경변수 DATA_GO_KR_SERVICE_KEY  (⚠️ 하드코딩 금지 — CLAUDE.md §2)

⚠️ 실행 환경: apis.data.go.kr 은 개발 샌드박스 프록시에서 차단(A-069) → **GitHub Actions 전용**.

의존성: httpx · pandas · openpyxl
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from xml.etree import ElementTree as ET

import httpx
import pandas as pd

BASE_URL = "http://apis.data.go.kr/1220000/nitemtrade/getNitemtradeList"
GW_ROOT  = Path("data/raw/관세청/Import Export Performance by Commodity and Country(GW)")
PARQUET  = Path("data/raw/customs_gw_historical.parquet")

START_YEAR = int(os.environ.get("HISTORICAL_START_YEAR", "2010"))
END_YEAR   = int(os.environ.get("HISTORICAL_END_YEAR", "2026"))

# 품목 → (폴더명, HS코드) — session37 §4 확정(대체재·보완재)
COMMODITIES: list[tuple[str, str]] = [
    ("Palm Oil (1511)",            "1511"),
    ("Sunflower Oil (1512.11)",    "151211"),
    ("Sunflower Oil (1512.19)",    "151219"),
    ("Rapeseed Oil (1514.11)",     "151411"),
    ("Rapeseed Oil (1514.19)",     "151419"),
    ("Palm Kernel Oil (1513.21)",  "151321"),
    ("Soybean (1201.90)",          "120190"),
    ("Soybean Meal (2304)",        "2304"),
    ("Biodiesel (3826)",           "3826"),
]

# 국가코드 → 파일명(기존 업로드본 표기 준수: U.S.A / Argentina …)
COUNTRIES: dict[str, str] = {
    "US": "U.S.A", "BR": "Brazil", "AR": "Argentina", "CN": "China",
    # session37 §4.1 확대 원산지
    "MY": "Malaysia", "ID": "Indonesia", "PY": "Paraguay",
    "VN": "Vietnam", "NL": "Netherlands", "ES": "Spain",
}

_COL_ORDER = ["무역수지(달러)", "수출액(달러)", "수출량(kg)", "수입액(달러)", "수입량(kg)"]


def _fetch_year(hs: str, cnty: str, year: int, max_retries: int = 4) -> list[dict]:
    """단일 (HS·국가·연도) 월별 실적 조회 — 지수 백오프 재시도."""
    key = os.environ.get("DATA_GO_KR_SERVICE_KEY", "").strip()
    if not key:
        raise RuntimeError("[오류] DATA_GO_KR_SERVICE_KEY 미등록 — GitHub Secrets 등록 필요")
    params = {"serviceKey": key, "strtYymm": f"{year}01",
              "endYymm": f"{year}12", "hsSgn": hs, "cntyCd": cnty}
    delay = 2
    for attempt in range(max_retries):
        try:
            r = httpx.get(BASE_URL, params=params, timeout=40)
            r.raise_for_status()
            root = ET.fromstring(r.text)
            code = root.findtext(".//resultCode")
            if code not in ("00", None):
                print(f"    [경고] {hs}/{cnty}/{year}: resultCode={code} "
                      f"{root.findtext('.//resultMsg')}")
                return []
            rows = []
            for it in root.findall(".//item"):
                yr = (it.findtext("year") or "").strip()
                if "총계" in yr or "." not in yr:
                    continue                      # 연 총계 행 제외 — 월별만
                month = int(yr.split(".")[1])
                rows.append({
                    "year": year, "month": month,
                    "무역수지(달러)": pd.to_numeric(it.findtext("balPayments"), errors="coerce"),
                    "수출액(달러)":  pd.to_numeric(it.findtext("expDlr"), errors="coerce"),
                    "수출량(kg)":    pd.to_numeric(it.findtext("expWgt"), errors="coerce"),
                    "수입액(달러)":  pd.to_numeric(it.findtext("impDlr"), errors="coerce"),
                    "수입량(kg)":    pd.to_numeric(it.findtext("impWgt"), errors="coerce"),
                })
            return rows
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(delay); delay *= 2; continue
            print(f"    [경고] {hs}/{cnty}/{year} 수집 실패: {e}")
            return []


def _write_gw_xlsx(rows: list[dict], out_path: Path) -> None:
    """업로드본과 동일 포맷으로 저장: 연도별 시트 × 월행 × 5지표열."""
    if not rows:
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for year, g in df.groupby("year"):
            sheet = g.set_index("month").reindex(range(1, 13))[_COL_ORDER]
            sheet.index = [f"{m}월" for m in sheet.index]
            sheet.index.name = None
            sheet.to_excel(writer, sheet_name=f"{int(year)}년")


def run() -> None:
    all_records: list[dict] = []
    for folder, hs in COMMODITIES:
        print(f"[C-03] {folder} (HS {hs}) 수집...")
        for cnty_code, cnty_name in COUNTRIES.items():
            rows: list[dict] = []
            for year in range(START_YEAR, END_YEAR + 1):
                rows.extend(_fetch_year(hs, cnty_code, year))
                time.sleep(0.3)
            if not rows:
                print(f"  [정보] {folder}/{cnty_name}: 데이터 없음")
                continue
            out = GW_ROOT / folder / f"{cnty_name}.xlsx"
            _write_gw_xlsx(rows, out)
            print(f"  [xlsx] {folder}/{cnty_name}.xlsx ({len(rows)}개월)")
            for r in rows:
                all_records.append({**r, "commodity": folder, "hs_code": hs,
                                    "country": cnty_name,
                                    "price_date": pd.Timestamp(year=r["year"],
                                                               month=r["month"], day=1),
                                    "source_name": "KoreaCustoms_GW",
                                    "ingested_at": pd.Timestamp.now("UTC")})
    if all_records:
        pd.DataFrame(all_records).to_parquet(PARQUET, index=False)
        print(f"\n[완료] → {PARQUET} ({len(all_records):,}행)")
    else:
        print("\n[경고] 수집 데이터 없음 — 키·네트워크 확인(Actions에서 실행 필요)")


if __name__ == "__main__":
    run()
