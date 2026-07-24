#!/usr/bin/env python3
"""
USDA FAS WASDE Excel 수동 업로드 데이터 수집 스크립트 (WBS 1.1.41)

입력: data/raw/USDA/WASDE/*.xlsx  (17년~26년 취합본, 월별 시트)
출력: data/raw/wasde_historical.parquet

파일 형식 주의 (A-050):
  - 24년~26년: 정상 OOXML(.xlsx, zip) — tidy long 포맷
  - 17년~23년: 사내 문서보안(DRM) "SAFER" 래퍼로 암호화됨 → 어떤 파서도 해독 불가.
    매직바이트가 'PK'(zip)가 아니면 DRM/비정상으로 판단하고 건너뜀.
    해결: DRM 클라이언트에서 평문 .xlsx로 재저장 후 재업로드 필요 (사용자 수동 작업).

tidy long 포맷 (24년~):
  컬럼 = [Report Title, Attribute, Reliability Projection, Commodity, Region,
          Market Year, Proj Est Flag, Annual/Quarter Flag, Value, Unit]
  시트명 = 보고서 발행월 (예: 'Jan 12' = 1월 12일 발행)

수집 지표 (World / United States):
  WASDE_SBO_PRODUCTION      : 대두유 생산량 (Million MT)
  WASDE_SBO_EXPORTS         : 대두유 수출량
  WASDE_SBO_IMPORTS         : 대두유 수입량
  WASDE_SBO_ENDING_STOCKS   : 대두유 기말재고
  WASDE_SBO_DOMESTIC_USE    : 대두유 국내소비(Domestic Total)
  WASDE_SBO_STU             : 재고사용비율 = Ending Stocks / Domestic Total × 100 (%)
  WASDE_US_SBO_*            : 미국 한정 동일 지표
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd

WASDE_DIR  = Path("data/raw/USDA/WASDE")
OUTPUT_DIR = Path("data/raw")

# 파일명 → 연도: "17년_..." / "26년 1~5월_..." → 2017 / 2026
_YEAR_RE = re.compile(r"^(\d{2})년")

# 시트명 → 월: 'Jan 12' / '1월' / 'Jan' → 1
_MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

# WASDE Attribute → 지표 접미사 (session34 §2.2 선별)
_ATTR_MAP = {
    "Production":        "PRODUCTION",
    "Exports":           "EXPORTS",
    "Exports, Total":    "EXPORTS",
    "Imports":           "IMPORTS",
    "Ending Stocks":     "ENDING_STOCKS",
    "Ending Stocks, Total": "ENDING_STOCKS",
    "Beginning Stocks":  "BEGINNING_STOCKS",
    "Domestic Total":    "DOMESTIC_USE",
    "Domestic, Total":   "DOMESTIC_USE",
    "Domestic Use":      "DOMESTIC_USE",
    "Total Use":         "TOTAL_USE",
    "Use, Total":        "TOTAL_USE",
    "Total Supply":      "TOTAL_SUPPLY",
    "Supply, Total":     "TOTAL_SUPPLY",
    "Crushings":         "CRUSH",
    "Domestic Crush":    "CRUSH",
    "Crush":             "CRUSH",
    "Yield":             "YIELD",
    "Area Harvested":    "AREA_HARVESTED",
    "Area Planted":      "AREA_PLANTED",
    "Avg. Farm Price":   "FARM_PRICE",
    "For Methyl Ester":  "BIODIESEL_USE",
    "Ethanol for Fuel":  "ETHANOL_USE",
    "Food Seed & Industrial":  "FSI",
    "Food, Seed & Industrial": "FSI",
}

# Commodity(tidy 명칭) → 지표 인픽스 (session34 §2.1 선별)
_COMMODITY_MAP = {
    "Soybean Oil":      "SBO",
    "Oil, Soybean":     "SBO",
    "Soybean Meal":     "MEAL",
    "Meal, Soybean":    "MEAL",
    "Oilseed, Soybean": "SOY",
    "Soybean":          "SOY",
    "Soybeans":         "SOY",
    "Vegetable Oils":   "VEGOIL",
    "Oilseeds":         "OILSEEDS",
    "Oilmeals":         "OILMEALS",
    "Corn":             "CORN",
}

# Region → 지표 접두사
_REGION_PREFIX = {
    "World":         "WASDE_",
    "United States": "WASDE_US_",
}


def _year_from_filename(filename: str) -> Optional[int]:
    m = _YEAR_RE.match(filename)
    return 2000 + int(m.group(1)) if m else None


def _month_from_sheet(sheet_name: str) -> Optional[int]:
    sn = sheet_name.strip().lower()
    if sn[:3] in _MONTH_MAP:
        return _MONTH_MAP[sn[:3]]
    m = re.match(r"^(\d{1,2})\s*월?", sn)
    if m:
        v = int(m.group(1))
        return v if 1 <= v <= 12 else None
    return None


def _is_ooxml(path: Path) -> bool:
    """매직바이트로 정상 OOXML(zip) 여부 판정. DRM/HTML 래퍼 차단."""
    try:
        with open(path, "rb") as fh:
            return fh.read(4) == b"PK\x03\x04"
    except OSError:
        return False


def _detect_wrapper(path: Path) -> str:
    """비정상 파일의 래퍼 종류 식별 (로그 메시지용)."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(64)
    except OSError:
        return "읽기 실패"
    if b"SAFER" in head or b"DOCUMENT" in head:
        return "문서보안(DRM) 래퍼 — 평문 재저장 필요"
    if head[:1] == b"<":
        return "HTML/XML 래퍼"
    if head[:4] == b"\xd0\xcf\x11\xe0":
        return "구형 .xls(OLE2) — xlrd 필요"
    return f"미상(매직 {head[:4].hex()})"


def _latest_market_year(my_series: pd.Series) -> Optional[str]:
    """'2021/22','2023/24' 중 가장 최신 마케팅연도 문자열 반환."""
    best, best_key = None, -1
    for v in my_series.dropna().astype(str).unique():
        m = re.match(r"(\d{4})", v.strip())
        if m and int(m.group(1)) > best_key:
            best_key, best = int(m.group(1)), v
    return best


def parse_wasde_tidy(xlsx_path: Path, year: int) -> pd.DataFrame:
    """정상 OOXML(tidy long) WASDE 파일 파싱."""
    xl = pd.ExcelFile(xlsx_path, engine="openpyxl")
    records: list[dict] = []

    for sheet_name in xl.sheet_names:
        month = _month_from_sheet(sheet_name)
        if month is None:
            continue
        price_date = date(year, month, 1)

        df = xl.parse(sheet_name, header=0)
        # 컬럼명 정규화: 'Market Year'/'MarketYear' 양쪽 포맷 대응
        norm = {re.sub(r"\s+", "", str(c)).lower(): c for c in df.columns}
        col = {
            "attribute":   norm.get("attribute"),
            "commodity":   norm.get("commodity"),
            "region":      norm.get("region"),
            "market_year": norm.get("marketyear"),
            "value":       norm.get("value"),
        }
        if any(v is None for v in col.values()):
            continue

        comm_series = df[col["commodity"]].astype(str).str.strip()
        base = {
            "price_date":  price_date,
            "source_name": "USDA_WASDE_XLSX",
            "unit":        "1000000MT",
            "ingested_at": pd.Timestamp.now("UTC"),
            "note":        f"{xlsx_path.name} / {sheet_name}",
        }

        for comm_name, infix in _COMMODITY_MAP.items():
            comm_df = df[comm_series == comm_name]
            if comm_df.empty:
                continue
            for region, prefix in _REGION_PREFIX.items():
                reg = comm_df[comm_df[col["region"]].astype(str).str.strip() == region]
                if reg.empty:
                    continue
                my = _latest_market_year(reg[col["market_year"]])
                if my is None:
                    continue
                cur = reg[reg[col["market_year"]].astype(str).str.strip() == my]

                vals: dict[str, float] = {}
                for _, r in cur.iterrows():
                    attr = str(r[col["attribute"]]).strip()
                    code = _ATTR_MAP.get(attr)
                    v = pd.to_numeric(r[col["value"]], errors="coerce")
                    if code and pd.notna(v) and code not in vals:
                        vals[code] = float(v)
                        records.append({**base, "market_year": my,
                                        "indicator_code": f"{prefix}{infix}_{code}",
                                        "value": float(v)})

                # STU = Ending Stocks / (Total Use|Domestic) × 100 — SBO 핵심
                es = vals.get("ENDING_STOCKS")
                du = vals.get("TOTAL_USE") or vals.get("DOMESTIC_USE")
                if es is not None and du and du > 0:
                    records.append({**base, "market_year": my, "unit": "percent",
                                    "indicator_code": f"{prefix}{infix}_STU",
                                    "value": round(es / du * 100, 2)})

    return pd.DataFrame(records)


def run(wasde_dir: Path = WASDE_DIR, output_dir: Path = OUTPUT_DIR) -> None:
    # 하위 폴더('곡물 및 유지류 취합본/') 포함 재귀 탐색
    xlsx_files = sorted(wasde_dir.rglob("*.xlsx"))
    if not xlsx_files:
        print(f"[오류] {wasde_dir}에 xlsx 파일 없음. 파일 업로드 후 재실행하세요.")
        return

    print(f"[C-04] WASDE Excel {len(xlsx_files)}개 파일 파싱 시작...")
    all_frames: list[pd.DataFrame] = []
    skipped_drm: list[str] = []

    for f in xlsx_files:
        if not _is_ooxml(f):
            reason = _detect_wrapper(f)
            print(f"  [건너뜀] {f.name}: {reason}")
            skipped_drm.append(f.name)
            continue
        print(f"  처리 중: {f.name}")
        year = _year_from_filename(f.name)
        if year is None:
            print(f"    [경고] 연도 추출 실패 — 건너뜀")
            continue
        try:
            df = parse_wasde_tidy(f, year)
            if not df.empty:
                all_frames.append(df)
            print(f"    → {len(df)}건 추출")
        except Exception as e:
            print(f"    [오류] {f.name}: {e}")

    if skipped_drm:
        print(f"\n[경고] DRM/비정상 형식으로 건너뛴 파일 {len(skipped_drm)}개: {skipped_drm}")
        print("       → 문서보안 해제 후 평문 .xlsx로 재업로드 필요 (수동 작업).")

    if not all_frames:
        print("[경고] 추출된 WASDE 레코드 없음 — parquet 미생성.")
        return

    combined = pd.concat(all_frames, ignore_index=True)
    combined = combined.sort_values(["price_date", "indicator_code"]).reset_index(drop=True)

    out_path = output_dir / "wasde_historical.parquet"
    output_dir.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(out_path, index=False)

    print(f"\n[완료] {len(combined)}건 → {out_path}")
    print(f"  기간: {combined['price_date'].min()} ~ {combined['price_date'].max()}")
    print(f"  지표: {sorted(combined['indicator_code'].unique())}")


if __name__ == "__main__":
    run()
