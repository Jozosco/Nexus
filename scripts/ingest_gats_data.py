#!/usr/bin/env python3
"""
USDA FAS GATS 수출/재수출 통계 수집 스크립트 (WBS 1.1.42)

입력 폴더 (reorganize_fas_files.yml 실행 후):
  data/raw/USDA/FAS/GATS/
    1507.10/   YYYY년 미국 對국가별 수출량.xlsx / 재수출량.xlsx (조대두유)
    1507.90/   YYYY년 미국 對국가별 수출량.xlsx (정제 대두유)
    export_value_top10/  9개년 미국 XX 수출액_상위 10개국.xlsx (USD)

출력:
  data/raw/gats_quantity_historical.parquet  — 월별 수출/재수출 물량 (MT)
  data/raw/gats_value_historical.parquet     — 연간 수출액 (USD)

실제 수출량 파일 구조 (A-052):
  row0 = 월 밴드(January..December, Total) — 각 밴드 3컬럼
  row1 = 하위 헤더 [Value, Qty, Unit Value] (밴드별 반복)
  col0 = Country, col1 = Unit of Measure (1507.90은 col1=Product, col2=Unit)
  → Qty 컬럼이 수출 물량(MT). 'World Total' 행 = 전체.

HS 접두사: 1507.10 → GATS_US_SBO_ , 1507.90 → GATS_US_RSBO_
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pandas as pd

# as-of 헬퍼 로드 — 스크립트 직접 실행 시 저장소 루트를 경로에 추가
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from src.pipeline.asof import attach_asof  # noqa: E402

GATS_DIR   = Path("data/raw/USDA/FAS/GATS")
OUTPUT_DIR = Path("data/raw")

_YEAR_RE = re.compile(r"^(\d{4})")

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}

# 행 라벨(국가) → 지표 국가 태그
TARGET_COUNTRIES = {
    "world total": "TOTAL", "world": "TOTAL",
    "korea, south": "KOREA", "south korea": "KOREA", "korea": "KOREA",
    "china": "CHINA", "india": "INDIA", "mexico": "MEXICO",
    "japan": "JAPAN", "colombia": "COLOMBIA", "canada": "CANADA",
}

_VALUE_COMMODITY = {"대두유": "SBO", "대두박": "SBM", "대두": "SOY"}


def _year_from_filename(name: str) -> int | None:
    m = _YEAR_RE.match(name.strip())
    return int(m.group(1)) if m else None



def _read_gats_table(path: Path) -> pd.DataFrame:
    """A-118: GATS 원본은 **xlsx와 csv가 섞여 있다**(1507.10.0000은 csv 24건).
    구 파서는 `read_excel`만 써서 csv 계열을 통째로 놓쳤다. 확장자로 분기한다.
    csv에는 헤더 위에 메타 행이 있을 수 있어 header=None으로 원시 판독한다(A-086 전례).
    """
    if path.suffix.lower() == ".csv":
        # 첫 행이 `"Data generated on ..."` 한 필드뿐이라 pandas가 **1열로 추론**하고
        # 이후 행을 전부 버린다(on_bad_lines=skip). 최대 열 수를 먼저 세어 강제 지정한다.
        import csv as _csv
        for enc in ("utf-8-sig", "cp949", "utf-8", "latin-1"):
            try:
                with open(path, newline="", encoding=enc) as fh:
                    rows = list(_csv.reader(fh))
                break
            except UnicodeDecodeError:
                continue
        else:
            return pd.DataFrame()
        if not rows:
            return pd.DataFrame()
        width = max(len(r) for r in rows)
        padded = [r + [""] * (width - len(r)) for r in rows]
        return pd.DataFrame(padded, dtype=str)
    return pd.read_excel(path, header=None, engine="openpyxl")

def parse_quantity_file(xlsx_path: Path, hs_prefix: str) -> pd.DataFrame:
    """수출량/재수출량 파일 → 월별 물량(Qty, MT) 정규화."""
    year = _year_from_filename(xlsx_path.name)
    if year is None:
        raise ValueError(f"[오류] 연도 추출 실패: {xlsx_path.name}")
    flow = "REEXPORT" if "재수출" in xlsx_path.name else "EXPORT"

    raw = _read_gats_table(xlsx_path)
    if raw.shape[0] < 3:
        return pd.DataFrame()

    # A-118: 헤더 위치를 0·1·2행으로 **하드코딩**하고 있었다. xlsx는 맞았지만 csv는
    #   상단에 생성일시·제목 3행이 더 있어 전량 0건이 됐다. 'Qty' 라벨이 있는 행을 찾아
    #   기준을 잡으면 두 포맷을 모두 처리한다(A-086 skiprows 자동탐지와 같은 접근).
    sub_row = next((r for r in range(min(12, raw.shape[0]))
                    if raw.iloc[r].astype(str).str.strip().str.lower().eq("qty").any()), None)
    if sub_row is None:
        return pd.DataFrame()
    band_row  = max(sub_row - 1, 0)
    first_data = sub_row + 1

    band = raw.iloc[band_row].astype(str).where(lambda s: s != "nan").ffill()
    sub  = raw.iloc[sub_row].astype(str)

    # 국가명 열 위치도 포맷마다 다르다(csv는 선행 인덱스 열이 있어 col1) — 라벨로 특정
    country_col = next((i for i in range(raw.shape[1])
                        if sub.iat[i].strip().lower() in ("partner", "country")), 0)

    # Qty 컬럼만 추출: (밴드 라벨, 컬럼 인덱스)
    qty_cols: list[tuple[str, int]] = []
    for i in range(raw.shape[1]):
        if sub.iat[i].strip().lower() == "qty":
            qty_cols.append((str(band.iat[i]).strip().lower(), i))

    base = {
        "source_name": "USDA_GATS_XLSX",
        "unit":        "MT",
        "ingested_at": pd.Timestamp.utcnow(),
        "note":        xlsx_path.name,
    }
    records: list[dict] = []

    for r in range(first_data, raw.shape[0]):
        country_raw = str(raw.iat[r, country_col]).strip().lower()
        tag = TARGET_COUNTRIES.get(country_raw)
        if tag is None:
            continue
        for band_label, ci in qty_cols:
            month = _MONTHS.get(band_label)
            if month is None:        # 'total' 밴드는 월별 합산이라 생략(중복 방지)
                continue
            qty = pd.to_numeric(str(raw.iat[r, ci]).replace(",", ""), errors="coerce")
            # A-121(D4): 구 코드는 `qty != 0`으로 **0을 버렸다**. 월간 무역 시계열에서
            #   0은 "그 달 선적 없음"이라는 **정보**이지 결측이 아니다. 버리면 as-of join이
            #   직전 비영(非零) 값을 끌어와 물량을 과대계상한다.
            #   A-086에서 이미 "전 국가 0 = 실제 무역 부재 → 0으로 보존(대체 금지)"로 확정.
            if pd.notna(qty):
                records.append({**base, "price_date": date(year, month, 1),
                                "indicator_code": f"{hs_prefix}{flow}_{tag}",
                                "value": float(qty)})

    # A-121(D4): GATS는 **교역이 없는 국가 행을 파일에 싣지 않는다**. 그대로 두면
    #   "그 달 선적 0"이 결측으로 남고, as-of join이 직전 비영 값을 끌어와 물량을
    #   과대계상한다(2017년 한국 조유가 통째로 사라진 사례).
    #   World Total이 존재하면 그 파일은 정상 파싱된 것이므로, 파일에 등장한 월에 한해
    #   **대상국 중 누락된 국가를 0으로 채운다**(파싱 실패와 무역 부재를 구분).
    #   ⚠️ 채울 월의 판정 기준(A-122): 컬럼 헤더에 12개월이 다 있다고 해서 12개월이
    #   보고된 것은 아니다. **당해 연도 파일은 미래 월 컬럼을 빈칸으로 미리 갖고 있다.**
    #   헤더 기준으로 채우면 아직 오지 않은 달에 0이 들어가 "선적 없음"으로 위조된다
    #   (2026-09~12에 192행 발생). 실제 보고 여부는 **World Total 행의 값 유무**가
    #   유일한 근거이므로 그 행이 숫자를 가진 월만 채운다.
    total_row = next((r for r in range(first_data, raw.shape[0])
                      if TARGET_COUNTRIES.get(str(raw.iat[r, country_col]).strip().lower()) == "TOTAL"),
                     None)
    months_seen = sorted({
        _MONTHS[b] for b, ci in qty_cols
        if b in _MONTHS and total_row is not None
        and pd.notna(pd.to_numeric(str(raw.iat[total_row, ci]).replace(",", ""), errors="coerce"))
    })
    if total_row is not None and months_seen:
        present = {(rec["price_date"], rec["indicator_code"]) for rec in records}
        for tag in sorted(set(TARGET_COUNTRIES.values())):
            code = f"{hs_prefix}{flow}_{tag}"
            for mo in months_seen:
                key = (date(year, mo, 1), code)
                if key not in present:
                    records.append({**base, "price_date": key[0],
                                    "indicator_code": code, "value": 0.0})

    # A-122: 당해 연도 파일은 **미래 월의 Total 칸에 0을 채워 배포**한다. 그래서 위의
    #   'Total 값 유무' 판정만으로는 걸러지지 않는다(2026-09~12에 160행 잔존).
    #   물리적 제약을 최종 방어선으로 둔다 — **끝나지 않은 달의 월간 무역통계는
    #   존재할 수 없다**. 그 달의 0은 "선적 없음"이 아니라 "아직 데이터 없음"이며,
    #   as-of join에서 걸러지더라도 커버리지·품질 지표를 오염시킨다.
    out = pd.DataFrame(records)
    if not out.empty:
        month_end = pd.to_datetime(out["price_date"]) + pd.offsets.MonthEnd(0)
        elapsed = month_end < pd.Timestamp.today().normalize()
        if (~elapsed).any():
            dropped = sorted(pd.to_datetime(out.loc[~elapsed, "price_date"])
                             .dt.strftime("%Y-%m").unique())
            print(f"    [제외] 미완결 월 {int((~elapsed).sum())}건 — {', '.join(dropped)}")
            out = out[elapsed].reset_index(drop=True)
    return out


def parse_value_file(xlsx_path: Path) -> pd.DataFrame:
    """9개년 수출액 파일 → 연간 총수출액(USD). 행=국가, row1=연도."""
    tag = next((t for kw, t in _VALUE_COMMODITY.items()
                if kw in xlsx_path.name.lower()), None)
    if tag is None:
        print(f"  [건너뜀] 품목 식별 불가: {xlsx_path.name}")
        return pd.DataFrame()

    raw = _read_gats_table(xlsx_path)
    # 연도 행 탐색 (값이 2000~2040 정수인 행)
    year_row_idx, year_cols = None, {}
    for r in range(min(5, raw.shape[0])):
        cols = {}
        for c in range(raw.shape[1]):
            v = pd.to_numeric(raw.iat[r, c], errors="coerce")
            if pd.notna(v) and 2000 <= v <= 2040:
                cols[c] = int(v)
        if len(cols) >= 3:
            year_row_idx, year_cols = r, cols
            break
    if not year_cols:
        print(f"  [경고] {xlsx_path.name}: 연도 행 없음")
        return pd.DataFrame()

    base = {
        "source_name":    "USDA_GATS_VALUE_XLSX",
        "unit":           "USD",
        "ingested_at":    pd.Timestamp.utcnow(),
        "note":           xlsx_path.name,
        "indicator_code": f"GATS_US_{tag}_EXPORT_VALUE",
    }
    records: list[dict] = []
    for c, yr in year_cols.items():
        col_vals = pd.to_numeric(raw.iloc[year_row_idx + 1:, c], errors="coerce").dropna()
        total = float(col_vals.sum())   # 상위 10개국 합산
        if total > 0:
            records.append({**base, "price_date": date(yr, 10, 1), "value": total})
    return pd.DataFrame(records)


def run(gats_dir: Path = GATS_DIR, output_dir: Path = OUTPUT_DIR) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── 수출량 (1507.10 + 1507.90) ──────────────────────────────────────────
    # A-118: D-019 재정리로 GATS 파일이
    #   `Oilseeds/Soybean Oil/Exports & Re-Exports/{1507.10.0000, 1507.90/.4020, ...}`로
    #   이동했는데 파서는 구 경로(`GATS/1507.10`)를 그대로 봤다 → **수출량 전량 미수집**.
    #   ICE(A-114)·GAIN(A-083)과 같은 '경로 이동 후 하드코딩 조회' 유형.
    #   HS 코드를 **경로 문자열이 아니라 하위 트리 전체에서 매칭**해 재정리에 견디게 한다.
    quantity_frames: list[pd.DataFrame] = []
    # A-121: `1507.90` 아래 **.4020(1회 정제)·.4050(완전 정제)** 두 하위 코드가 같은
    #   `GATS_US_RSBO_` 접두사로 합쳐져 동일 (price_date, indicator_code)에 2행이 생겼다
    #   (연도별 관측이 24개월로 나온 원인) → as-of join이 임의 행을 선택.
    #   KOSIS 키 붕괴(A-116)와 같은 유형. 하위 코드를 접두사에 반영해 유일화한다.
    HS_PREFIX_MAP = [("1507.10", "GATS_US_SBO_"),    # 조대두유
                     ("1507.90", "GATS_US_RSBO_"),   # 정제 대두유(하위코드로 세분)
                     ("1517.90", "GATS_US_HSBO_")]   # 완전 경화 대두유

    def _sub_suffix(path) -> str:
        """경로의 하위 HTS 코드(.4020/.4050 등)를 지표코드 접미사로."""
        for part in path.parts:
            if part.startswith(".") and part[1:].isdigit():
                return part[1:] + "_"
        return ""
    for hs_sub, prefix in HS_PREFIX_MAP:
        files = sorted(f for f in gats_dir.rglob("*")
                       if f.suffix.lower() in (".xlsx", ".csv")
                       and hs_sub in str(f) and not f.name.startswith("~$"))
        if not files:
            print(f"[경고] GATS {hs_sub} — xlsx 없음(하위 트리 전체 탐색).")
            continue
        print(f"[C-04] GATS {hs_sub}: {len(files)}개 파일 파싱...")
        for f in files:
            print(f"  처리 중: {f.name}")
            try:
                df = parse_quantity_file(f, prefix + _sub_suffix(f))
                if not df.empty:
                    quantity_frames.append(df)
                print(f"    → {len(df)}건")
            except Exception as e:
                print(f"    [오류] {f.name}: {e}")

    if quantity_frames:
        qty = pd.concat(quantity_frames, ignore_index=True)
        qty = qty.sort_values(["price_date", "indicator_code"]).reset_index(drop=True)
        qpath = output_dir / "gats_quantity_historical.parquet"
        # D-023: 저장 직전 as-of 5필드 부여 — 규칙은 src/pipeline/asof.py 단일 관리
        qty = attach_asof(qty, source="GATS_")
        qty.to_parquet(qpath, index=False)
        print(f"\n[완료] 수출량 {len(qty)}건 → {qpath}")
        print(f"  기간: {qty['price_date'].min()} ~ {qty['price_date'].max()}")
        print(f"  지표: {sorted(qty['indicator_code'].unique())}")
    else:
        print("[경고] 수출량 데이터 없음.")

    # ── 수출액 (export_value_top10) ─────────────────────────────────────────
    vdir = gats_dir / "export_value_top10"
    vfiles = sorted(vdir.glob("*.xlsx")) if vdir.exists() else []
    if not vfiles:
        print(f"[경고] {vdir} — xlsx 없음.")
        return
    print(f"\n[C-04] export_value_top10: {len(vfiles)}개 파일 파싱...")
    value_frames: list[pd.DataFrame] = []
    for f in vfiles:
        print(f"  처리 중: {f.name}")
        try:
            df = parse_value_file(f)
            if not df.empty:
                value_frames.append(df)
            print(f"    → {len(df)}건")
        except Exception as e:
            print(f"    [오류] {f.name}: {e}")

    if value_frames:
        val = pd.concat(value_frames, ignore_index=True)
        val = val.sort_values(["price_date", "indicator_code"]).reset_index(drop=True)
        vpath = output_dir / "gats_value_historical.parquet"
        # D-023: 저장 직전 as-of 5필드 부여 — 규칙은 src/pipeline/asof.py 단일 관리
        val = attach_asof(val, source="GATS_")
        val.to_parquet(vpath, index=False)
        print(f"\n[완료] 수출액 {len(val)}건 → {vpath}")
        print(f"  지표: {sorted(val['indicator_code'].unique())}")


if __name__ == "__main__":
    run()
