"""BRL/USD 거래량 결측 — CME BRL/USD 선물(6L) 거래량 **대리 열** 채우기 (2026-09-14 · A-266).

승인자 요청: 업로드 xlsx의 'Vol.'이 2019~2023(2023-01-25까지)만 있으니 2010~2018·2024~2026·중간 공백을 채울 것.
정직한 한계: 현물 환율에는 집중 거래소 거래량이 없다. 원본 Vol.은 투자 포털 자사 피드 틱 집계라 다른 기간을
같은 정의로 복원할 수 있는 무료 소스는 없다(DATA GAP). 따라서 **원본 열은 건드리지 않고** 별도 열
`volume_proxy_cme_6l`에 CME 6L 선물(계약 62,500 BRL) 일별 거래량을 대리 지표로 채우고 `volume_note`에 정의 차이를
명시한다(NOT COMPARABLE — 수준 비교 금지, 방향·상대 변화 참고만).
실행 표면: yfinance `6L=F`는 샌드박스 프록시가 차단하므로 Actions(`fx_volume_proxy.yml`)에서 실행.
산출: data/raw/15yrs Dataset_BRL_USD Exchange Rate_volume_filled.xlsx(원본 시트 + 대리 열, 원본 불가침 A-184)
      + data/raw/fx_brl_usd_historical.parquet의 volume_proxy_cme_6l 열 갱신 + reports/market/fx_volume_proxy_{date}.md
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd

_root = Path(__file__).resolve().parents[1]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

SRC_XLSX = Path("data/raw/15yrs Dataset_BRL_USD Exchange Rate.xlsx")
OUT_XLSX = Path("data/raw/15yrs Dataset_BRL_USD Exchange Rate_volume_filled.xlsx")
PARQUET = Path("data/raw/fx_brl_usd_historical.parquet")
REPORT = Path("reports/market") / f"fx_volume_proxy_{date.today().isoformat()}.md"
SYMBOLS = ("6L=F", "BRL=F")          # CME BRL/USD 선물 연속물 — 야후 심볼 후보
VOLUME_NOTE = "원본 Vol.=투자 포털 틱 집계(2019~2023-01) · 대리=CME 6L 선물 일별 거래량(계약 수) — 정의 상이, NOT COMPARABLE"


def fetch_cme_6l_volume() -> tuple[pd.Series, str]:
    """yfinance로 6L 연속물 일별 거래량. (series, symbol) — 실패 시 (빈, '')."""
    try:
        import yfinance as yf
    except ImportError:
        print("[경고] yfinance 미설치 — Actions 의존성 확인")
        return pd.Series(dtype=float), ""
    for sym in SYMBOLS:
        for period in ("max", "10y", "5y"):
            try:
                hist = yf.Ticker(sym).history(period=period, auto_adjust=False)
            except Exception as e:                                # noqa: BLE001
                print(f"[정보] {sym} {period}: {type(e).__name__}: {str(e)[:80]}")
                continue
            if hist is None or hist.empty or "Volume" not in hist.columns:
                continue
            idx = pd.to_datetime(hist.index)
            if getattr(idx, "tz", None) is not None:
                idx = idx.tz_localize(None)
            s = pd.Series(hist["Volume"].values, index=idx.normalize()).astype(float)
            s = s[s > 0]
            if len(s) >= 200:
                print(f"[정보] 대리 거래량: {sym} period={period} → {len(s):,}일 "
                      f"{s.index.min().date()}~{s.index.max().date()}")
                return s.sort_index(), sym
    return pd.Series(dtype=float), ""


def apply_proxy(vol: pd.Series, symbol: str) -> pd.DataFrame:
    if not PARQUET.is_file():
        raise SystemExit("[오류] fx_brl_usd_historical.parquet 없음 — 파서를 먼저 실행")
    df = pd.read_parquet(PARQUET)
    df["price_date"] = pd.to_datetime(df["price_date"])
    df["volume_proxy_cme_6l"] = df["price_date"].map(vol) if len(vol) else pd.NA
    df["volume_proxy_source"] = f"yfinance {symbol}" if symbol else None
    df["volume_note"] = VOLUME_NOTE
    df.to_parquet(PARQUET, index=False)
    return df


def write_filled_xlsx(df: pd.DataFrame) -> None:
    """원본 시트 구조(연도 시트·Month/Day/…)를 복제하고 대리 열 2개를 덧붙인다 — 원본 파일은 불변."""
    import openpyxl
    from openpyxl import load_workbook
    wb = load_workbook(SRC_XLSX)
    lookup = df.set_index("price_date")
    for ws in wb.worksheets:
        if not str(ws.title).endswith("년"):
            continue
        year = int(str(ws.title)[:4])
        header = [c.value for c in ws[1]]
        try:
            m_col, d_col = header.index("Month") + 1, header.index("Day") + 1
        except ValueError:
            continue
        col_p = len([h for h in header if h is not None]) + 1
        ws.cell(1, col_p, "Vol.(대리: CME 6L 선물 거래량)")
        ws.cell(1, col_p + 1, "Vol. 출처")
        for r in range(2, ws.max_row + 1):
            m, dd = ws.cell(r, m_col).value, ws.cell(r, d_col).value
            if m is None or dd is None:
                continue
            try:
                ts = pd.Timestamp(year=year, month=int(m), day=int(dd))
            except ValueError:
                continue
            if ts in lookup.index:
                row = lookup.loc[ts]
                v = row["volume_proxy_cme_6l"] if "volume_proxy_cme_6l" in lookup.columns else None
                orig = row["volume"]
                if pd.notna(orig):
                    ws.cell(r, col_p + 1, "원본(투자 포털 틱 집계)")
                elif pd.notna(v):
                    ws.cell(r, col_p, float(v)); ws.cell(r, col_p + 1, "대리(CME 6L 선물)")
    wb.save(OUT_XLSX)


def run() -> int:
    vol, sym = fetch_cme_6l_volume()
    df = apply_proxy(vol, sym)
    write_filled_xlsx(df)
    orig = df["volume"].notna(); proxy = df["volume_proxy_cme_6l"].notna()
    by_year = df.assign(y=df["price_date"].dt.year).groupby("y").agg(
        rows=("value", "size"), orig=("volume", lambda s: int(s.notna().sum())),
        proxy=("volume_proxy_cme_6l", lambda s: int(s.notna().sum())))
    lines = [f"# BRL/USD 거래량 대리 채움 — {date.today().isoformat()}", "",
             f"> {VOLUME_NOTE}", f"> 대리 원천: {sym or '미수신'} · 대리 커버리지 {int(proxy.sum()):,}/{len(df):,}행 · 원본 {int(orig.sum()):,}행", "",
             "| 연도 | 거래일 | 원본 Vol. | 대리(6L) |", "|---|---|---|---|"]
    lines += [f"| {y} | {r.rows} | {r.orig} | {r.proxy} |" for y, r in by_year.iterrows()]
    lines += ["", "- 원본 xlsx는 불변 · 동반 파일 `..._volume_filled.xlsx`에 대리 열 2개 추가.",
              "- 대리는 정의가 다르므로 원본 구간(2019~2023-01)과 수준 비교 금지 — 상대 변화·이벤트 반응 참고 전용."]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[완료] 대리 거래량 {int(proxy.sum()):,}행 → {PARQUET} · {OUT_XLSX} · {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
