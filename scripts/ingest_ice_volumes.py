#!/usr/bin/env python3
"""
ICE 월별 거래량(Monthly Volumes) 수집·정형화 (WBS 1.1.45 · A-063)

입력: data/raw/ICE/Reports/Monthly Volumes/{U.S.,E.U.}/*.xlsx
      - U.S. : ICE Futures U.S.  (Financial·Agricultural·Energy) — Futures / Options
      - E.U. : ICE F&O Europe    (Oil·Energy)                   — Futures&Options
      파일명: 'YYYY_Monthly Volume(s) {Futures|Options|Futures&Options}.xlsx'  (단·복수 허용)
      시트명: 'YYYY년' · 다단 헤더(0행=상품군, 1행=세부상품), 2행~=월별 값

출력: data/raw/ice_monthly_volumes.parquet (롱포맷)
      price_date(월초), year, market(US/EU), contract_type, product_group, product,
      value(거래량), indicator_code, source_name, ingested_at

성격: 가격이 아닌 '거래량(유동성·참여도)' — G1 보조 / G2 변동성 레이어 입력 (핵심 인과 변수 아님).

의존성: pandas >= 2.0 · openpyxl
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

# as-of 헬퍼 로드 — 스크립트 직접 실행 시 저장소 루트를 경로에 추가
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from src.pipeline.asof import attach_asof  # noqa: E402

ICE_ROOT = Path("data/raw/ICE/Reports/Monthly Volumes")
OUT_PATH = Path("data/raw/ice_monthly_volumes.parquet")

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}
_YEAR_RE = re.compile(r"(\d{4})")

# 열 수 없는 원본 목록 — 실행 끝에 재업로드 요청으로 모아 보고한다(A-124)
_CORRUPT: list[tuple[Path, str]] = []


def _contract_type(name: str) -> str:
    low = name.lower()
    if "futures&options" in low or "futures & options" in low:
        return "Futures&Options"
    if "option" in low:
        return "Options"
    if "future" in low:
        return "Futures"
    return "Unknown"


def _slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", str(text)).strip("_").upper()


def _instrument(group: str, contract: str) -> str:
    """지표코드의 상품군 구분자 — A-123.

    구 코드는 `contract_type`만 붙였다. 그런데 EU 파일은 하나의 리포트 안에
    **Futures 섹션과 Options 섹션이 나란히** 들어 있어(contract_type이 둘 다
    'Futures&Options') 같은 상품의 선물·옵션이 **같은 지표코드로 뭉개졌다**
    (전체 행의 15.8%). as-of 정렬에서 둘 중 하나만 임의로 남아 거래량이 뒤바뀐다.
    섹션 헤더(product_group)가 실제 상품군이므로 그것을 우선 사용한다.
    """
    g = (group or "").lower()
    if "future" in g:
        return "FUTURES"
    if "option" in g:
        return "OPTIONS"
    return _slug(contract)


def parse_ice_file(path: Path, market: str) -> pd.DataFrame:
    """단일 ICE xlsx → 롱포맷(월×상품×거래량)."""
    contract = _contract_type(path.stem)
    try:
        xl = pd.ExcelFile(path)
    except Exception as e:
        # A-124: 구 코드는 여기서 조용히 빈 프레임을 반환했다. 2015·2016 미국 선물 파일이
        #   **정확히 16,384바이트로 잘려**(EOCD가 가리키는 중앙 디렉터리 끝이 파일 끝을 넘김)
        #   BadZipFile을 던졌는데, 로그 한 줄로 흘러가 2개년 결측이 발견되지 않았다.
        #   재업로드가 필요한 사안이므로 목록으로 모아 상단에 보고한다.
        _CORRUPT.append((path, f"{type(e).__name__} · {path.stat().st_size:,}B"))
        return pd.DataFrame()

    # A-124: 연도의 출처는 **파일명**이다. 시트명을 신뢰하던 구 코드는
    #   `2010_Monthly Volumes Futures.xlsx`의 시트가 '2017년'으로 남아 있어(2017 워크북을
    #   복사해 2010 수치를 붙여넣고 시트명을 안 고친 흔적) **2010년 데이터를 2017년으로 적재**했다.
    #   그 결과 2010년 미국 선물 거래량이 통째로 사라지고 2017년은 값이 둘로 충돌했다(132건).
    fm = _YEAR_RE.search(path.stem)
    file_year = int(fm.group(1)) if fm else None

    records: list[dict] = []
    for sheet in xl.sheet_names:
        ym = _YEAR_RE.search(str(sheet))
        sheet_year = int(ym.group(1)) if ym else None
        year = file_year or sheet_year
        if file_year and sheet_year and file_year != sheet_year:
            print(f"  [경고] {path.name}: 시트명 연도({sheet_year})가 파일명({file_year})과 "
                  f"불일치 — 파일명 기준으로 적재")
        raw = xl.parse(sheet, header=None)
        if raw.empty:
            continue
        # 헤더 행 탐지: 0열이 'Month'인 행
        hdr_idx = None
        for i in range(min(6, len(raw))):
            if str(raw.iloc[i, 0]).strip().lower() == "month":
                hdr_idx = i
                break
        if hdr_idx is None:
            continue
        group_row = raw.iloc[hdr_idx - 1].ffill() if hdr_idx >= 1 else raw.iloc[hdr_idx]
        prod_row = raw.iloc[hdr_idx]
        data = raw.iloc[hdr_idx + 1:]

        for _, row in data.iterrows():
            month_name = str(row.iloc[0]).strip().lower()
            month = _MONTHS.get(month_name)
            if month is None or year is None:
                continue
            price_date = pd.Timestamp(year=year, month=month, day=1)
            for col in range(1, raw.shape[1]):
                product = str(prod_row.iloc[col]).strip()
                if not product or product.lower() in ("nan", "month"):
                    continue
                val = pd.to_numeric(row.iloc[col], errors="coerce")
                if pd.isna(val):
                    continue
                group = str(group_row.iloc[col]).strip()
                group = "" if group.lower() == "nan" else group
                # A-123: 'Monthly Totals' 섹션은 거래소 전체 합계(Futures/Options/Overall)로,
                #   상품이 아니라 집계다. 상품명 칸에 'Futures'가 들어와 `ICE_US_FUTURES_FUTURES`
                #   같은 무의미한 코드가 생기고, 두 리포트에서 같은 코드가 중복 생성된다.
                #   대두유 유동성과 무관한 거래소 총량이므로 적재하지 않는다.
                if not group or "monthly total" in group.lower():
                    continue
                records.append({
                    "price_date":    price_date,
                    "year":          year,
                    "market":        market,
                    "contract_type": contract,
                    "product_group": group,
                    "product":       product.replace("*", "").strip(),
                    # A-125: 컬럼명 계약은 프로젝트 전역에서 `value`다. `volume`으로
                    #   내보내던 탓에 G1 로더(값 컬럼=value)가 ICE를 조용히 건너뛰었다.
                    "value":         float(val),
                    "indicator_code": f"ICE_{market}_{_slug(product)}_{_instrument(group, contract)}",
                    "source_name":   "ICE_MonthlyVolumes_xlsx",
                    "ingested_at":   pd.Timestamp.now("UTC"),
                })

    return pd.DataFrame(records)


def run() -> None:
    if not ICE_ROOT.exists():
        print(f"[경고] {ICE_ROOT} 없음.")
        return
    markets = {"U.S.": "US", "E.U.": "EU"}
    frames = []
    for folder, market in markets.items():
        # D-027(파생 발견): 비재귀 `glob`이라 **U.S./Futures/·U.S./Options/ 34개 파일이
        # 전량 누락**돼 있었다(EU만 수집 → 3,459행·24지표. A-063 기록 5,332행·41지표와 불일치).
        # GAIN의 A-083과 동일한 버그 유형 — 하위 폴더가 생기면 조용히 사라진다.
        files = sorted(p for p in (ICE_ROOT / folder).rglob("*.xlsx")
                       if not p.name.startswith("~$"))     # 엑셀 임시파일 제외
        if not files:
            print(f"[정보] {folder} — 파일 없음.")
            continue
        print(f"[C-03] ICE {market}: {len(files)}개 파일 파싱...")
        for f in files:
            df = parse_ice_file(f, market)
            if not df.empty:
                frames.append(df)
                print(f"  [OK] {f.name}: {len(df):,}행")

    if _CORRUPT:
        print(f"\n[오류] 열 수 없는 원본 {len(_CORRUPT)}건 — **재업로드 필요**")
        for pth, why in _CORRUPT:
            print(f"  · {pth.relative_to(ICE_ROOT)} ({why})")
        print("  → 해당 연도 거래량은 결측으로 남습니다.")

    if not frames:
        print("[경고] 정형화된 ICE 데이터 없음.")
        return

    combined = pd.concat(frames, ignore_index=True).sort_values(
        ["market", "contract_type", "price_date", "product"]).reset_index(drop=True)

    # D-027(파생 발견): 원본 xlsx는 연도 전체 월 컬럼을 미리 두고 있어, **아직 오지 않은 달**이
    # volume=0으로 들어온다. 0(거래 없음)과 미도래(데이터 없음)를 혼동시키는 D4 위반이므로
    # 당월 이후 행은 제거한다. as-of 게이트가 걸러주긴 하지만 EDA·리포트까지 오염된다.
    cur_month = pd.Timestamp.today().normalize().replace(day=1)
    future = pd.to_datetime(combined["price_date"]) > cur_month
    if future.any():
        zeros = int((combined.loc[future, "value"].fillna(0) == 0).sum())
        print(f"[정리] 미도래 월 {int(future.sum())}행 제거 (그중 0값 {zeros}행) — "
              f"'거래량 0'과 '아직 없음'의 혼동 방지")
        combined = combined[~future].reset_index(drop=True)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    # D-023: 저장 직전 as-of 5필드 부여 — 규칙은 src/pipeline/asof.py 단일 관리
    combined = attach_asof(combined, source="ICE_")
    combined.to_parquet(OUT_PATH, index=False)

    print(f"\n[완료] → {OUT_PATH}")
    print(f"  총 {len(combined):,}행 · 지표 {combined['indicator_code'].nunique()}종 "
          f"· 기간 {combined['price_date'].min().date()}~{combined['price_date'].max().date()}")
    for (mkt, ct), g in combined.groupby(["market", "contract_type"]):
        print(f"  - {mkt}/{ct}: {g['product'].nunique()}개 상품, {len(g):,}행")


if __name__ == "__main__":
    run()

