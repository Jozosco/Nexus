"""승인자 업로드 BRL/USD 환율 15개년(투자 포털 원본) → 롱포맷 parquet (2026-09-14 · A-266).

입력: data/raw/15yrs Dataset_BRL_USD Exchange Rate.xlsx — 연도 시트 '2010년'~'2026년',
      열 Month | Day | Price | Open | High | Low | (Vol. — 2019~2023만, '44.05K' 문자열)
단위 주의: 파일 값은 **USD per BRL**(0.19~0.57). 파이프라인 정본(FRED DEXBZUS)은 BRL per USD이므로
      역수를 취해 코드 FX_BRL_USD(단위 BRL/USD)로 발행한다. 원본 방향 값은 fx_usd_per_brl 열에 보존.
거래량: 현물 환율에는 집중 거래소 거래량이 없다. 원본 Vol.은 투자 포털 자사 피드 틱 집계라 다른 기간을
      같은 정의로 복원할 수 없다(DATA GAP). 원본 값만 volume(×1,000)에 두고 volume_source를 표기한다.
      대리 지표(CME 6L 선물 거래량)는 scripts/fill_fx_volume_proxy.py가 별도 열에 채운다.
휴일 이월 행(주말·OHLC 전부 동일한 1/1 등)은 관측이 아니므로 제거한다.
출력: data/raw/fx_brl_usd_historical.parquet · 원본 xlsx는 읽기 전용(A-184).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

_sys_root = Path(__file__).resolve().parents[1]
if str(_sys_root) not in sys.path:
    sys.path.insert(0, str(_sys_root))
from src.pipeline.asof import attach_asof  # noqa: E402

SRC_PATH = Path("data/raw/15yrs Dataset_BRL_USD Exchange Rate.xlsx")
OUT_PATH = Path("data/raw/fx_brl_usd_historical.parquet")
INDICATOR = "FX_BRL_USD"
SOURCE_NAME = "Investing.com_upload"
_YEAR_RE = re.compile(r"(\d{4})\s*년")


def _parse_volume(v: object) -> float | None:
    """'44.05K' → 44050 · '1.2M' → 1200000 · 빈값 → None."""
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    s = str(v).strip().replace(",", "")
    if not s or s in ("-", "—"):
        return None
    mult = 1.0
    if s[-1] in "Kk":
        mult, s = 1_000.0, s[:-1]
    elif s[-1] in "Mm":
        mult, s = 1_000_000.0, s[:-1]
    try:
        return float(s) * mult
    except ValueError:
        return None


def parse_workbook(path: Path = SRC_PATH) -> pd.DataFrame:
    xl = pd.ExcelFile(path)
    frames: list[pd.DataFrame] = []
    for sheet in xl.sheet_names:
        m = _YEAR_RE.search(str(sheet))
        if not m:
            continue
        year = int(m.group(1))
        df = xl.parse(sheet)
        if df.empty or not {"Month", "Day", "Price"}.issubset(df.columns):
            print(f"  [건너뜀] {sheet}: 필수 열 없음")
            continue
        sub = pd.DataFrame({
            "price_date": pd.to_datetime(
                dict(year=year, month=pd.to_numeric(df["Month"], errors="coerce"),
                     day=pd.to_numeric(df["Day"], errors="coerce")), errors="coerce"),
            "usd_per_brl": pd.to_numeric(df["Price"], errors="coerce"),
            "open_raw": pd.to_numeric(df.get("Open"), errors="coerce"),
            "high_raw": pd.to_numeric(df.get("High"), errors="coerce"),
            "low_raw": pd.to_numeric(df.get("Low"), errors="coerce"),
            "volume": [_parse_volume(v) for v in (df["Vol."] if "Vol." in df.columns else [None] * len(df))],
        })
        sub = sub.dropna(subset=["price_date", "usd_per_brl"])
        sub = sub[sub["usd_per_brl"] > 0]
        frames.append(sub)
    if not frames:
        raise SystemExit(f"[오류] {path}: 연도 시트에서 유효 행 없음")
    out = pd.concat(frames, ignore_index=True).sort_values("price_date")
    # 휴일 이월 행 제거: 주말 + OHLC 네 값이 전부 같은 행(거래 없는 날의 전일 값 복사)
    weekend = out["price_date"].dt.weekday >= 5
    flat = (out["usd_per_brl"] == out["open_raw"]) & (out["open_raw"] == out["high_raw"]) & (out["high_raw"] == out["low_raw"])
    carried = weekend | flat
    print(f"[정보] 휴일 이월 행 제거 {int(carried.sum()):,}건(주말 {int(weekend.sum()):,} · 무변동 {int((flat & ~weekend).sum()):,})")
    out = out[~carried].copy()
    out = out.drop_duplicates("price_date", keep="last")
    # 방향 통일: BRL per USD (FRED DEXBZUS와 동일 방향)
    out["value"] = 1.0 / out["usd_per_brl"]
    out["open"] = 1.0 / out["open_raw"]
    out["high"] = 1.0 / out["low_raw"]      # 역수를 취하면 고저가 뒤바뀐다
    out["low"] = 1.0 / out["high_raw"]
    out["fx_usd_per_brl"] = out["usd_per_brl"]
    out["indicator_code"] = INDICATOR
    out["unit"] = "BRL/USD"
    out["source_name"] = SOURCE_NAME
    out["volume_source"] = out["volume"].map(lambda v: "investing.com" if pd.notna(v) else None)
    out["note"] = "승인자 업로드 15개년 — 원본 USD/BRL 역수 · 거래량은 투자 포털 틱 집계(2019~2023-01)만"
    out["ingested_at"] = pd.Timestamp.now("UTC")
    cols = ["price_date", "indicator_code", "value", "open", "high", "low", "fx_usd_per_brl",
            "volume", "volume_source", "unit", "source_name", "note", "ingested_at"]
    return out[cols].reset_index(drop=True)


def run() -> None:
    if not SRC_PATH.is_file():
        print(f"[경고] {SRC_PATH} 없음 — 건너뜀")
        return
    df = parse_workbook(SRC_PATH)
    df = attach_asof(df, source="FX")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_PATH, index=False)
    vol = df["volume"].notna()
    print(f"[완료] {INDICATOR} {len(df):,}행 {df['price_date'].min().date()}~{df['price_date'].max().date()} "
          f"· 거래량 보유 {int(vol.sum()):,}행({df.loc[vol, 'price_date'].min().date() if vol.any() else '-'}~"
          f"{df.loc[vol, 'price_date'].max().date() if vol.any() else '-'}) → {OUT_PATH}")


if __name__ == "__main__":
    run()
