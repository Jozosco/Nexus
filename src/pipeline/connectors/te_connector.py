"""
Trading Economics 커넥터 — WBS 1.1.3/1.1.2 보완
수집 대상: BDI (Baltic Dry Index) · CPO (Crude Palm Oil)

Trading Economics API 참고:
  - Python 패키지: tradingeconomics (pip install tradingeconomics)
  - 인증: te.login('key:secret') — GitHub Secret TRADING_ECONOMICS_API_KEY = 'key:secret' 형식
  - BDI: C-03 구조적 단절 모니터링 변수 (90일 z-score > 2σ 임계값)
  - CPO: CPO-SBO 스프레드 산출용 (G1 CONDITIONAL INCLUDE — MEMORY B-003)

커버리지 확인 (조사 결과):
  - BDI: ✅ 제공 (tradingeconomics.com/commodity/baltic)
  - CPO: ✅ 제공 (tradingeconomics.com/commodity/palm-oil)
  - BCAA (식물성유지탱커): ❌ 미제공 — Perplexity 프록시 사용 (shipping_connector.py)
  - CBOT ZL=F: ❌ 미제공 — yfinance 사용 (commodity_connector.py)

실행 환경: VS Code Web (Azure ML Studio) 또는 GitHub Actions
"""

from __future__ import annotations

import os
from datetime import date

import pandas as pd

OUTPUT_DIR = "data/raw"


def _login() -> bool:
    """Trading Economics 인증. 키 미등록 시 False 반환."""
    te_key = os.environ.get("TRADING_ECONOMICS_API_KEY", "").strip()
    if not te_key:
        print(
            "[경고] TRADING_ECONOMICS_API_KEY 미등록 — Trading Economics 수집 건너뜀.\n"
            "       등록 경로: tradingeconomics.com → GitHub Secrets (형식: key:secret)"
        )
        return False
    try:
        import tradingeconomics as te  # type: ignore
        te.login(te_key)
        return True
    except ImportError:
        print("[경고] tradingeconomics 패키지 미설치 — pip install tradingeconomics")
        return False
    except Exception as e:
        print(f"[경고] Trading Economics 인증 실패: {e}")
        return False


def _df_from_te_result(result: object, indicator_code: str, source: str, unit: str) -> pd.DataFrame:
    """TE 응답(DataFrame 또는 list)을 Nexus 표준 스키마로 변환."""
    import tradingeconomics as te  # type: ignore
    if result is None:
        return pd.DataFrame()
    try:
        if isinstance(result, pd.DataFrame):
            df = result.copy()
        else:
            df = pd.DataFrame(result)
    except Exception as e:
        print(f"[경고] TE 결과 DataFrame 변환 실패 ({indicator_code}): {e}")
        return pd.DataFrame()

    if df.empty:
        return pd.DataFrame()

    # TE 컬럼명은 버전·심볼에 따라 달라짐 — 유연하게 처리
    date_col  = next((c for c in ["DateTime", "Date", "date", "Datetime"] if c in df.columns), None)
    value_col = next((c for c in ["Last", "Close", "Value", "last", "close"] if c in df.columns), None)

    if not date_col or not value_col:
        print(f"[경고] TE {indicator_code}: 날짜/값 컬럼 없음. 실제 컬럼: {list(df.columns)}")
        return pd.DataFrame()

    out = pd.DataFrame({
        "price_date":     pd.to_datetime(df[date_col], errors="coerce"),
        "value":          pd.to_numeric(df[value_col], errors="coerce"),
        "source_name":    source,
        "indicator_code": indicator_code,
        "unit":           unit,
        "ingested_at":    pd.Timestamp.utcnow(),
    })
    return out.dropna(subset=["price_date", "value"])


def fetch_bdi() -> pd.DataFrame:
    """BDI (Baltic Dry Index) — C-03 구조적 단절 모니터링 변수.

    BDI z-score > 2σ (90일 rolling) → 해운비용 급등 경보.
    직접 Baltic Exchange API(유료) 대안으로 Trading Economics 사용.
    """
    if not _login():
        return pd.DataFrame()
    try:
        import tradingeconomics as te  # type: ignore
        # 심볼 우선 시도 — TE 심볼은 버전에 따라 달라질 수 있음
        for symbol in ("bdi", "baltic", "BADI:COM", ".BADI"):
            try:
                result = te.getMarketsBySymbol(symbols=symbol, output_type="df")
                if result is not None and len(result) > 0:
                    df = _df_from_te_result(result, "BDI", "TradingEconomics/BalticExchange", "points")
                    if not df.empty:
                        print(f"[정보] TE BDI 수집 완료 (심볼: {symbol}): {len(df)}건")
                        return df
            except Exception:
                continue
        # 전체 상품 목록 폴백
        all_comm = te.getMarketsData(marketsField="commodities", output_type="df")
        if all_comm is not None:
            bdi_row = all_comm[
                all_comm.get("Symbol", pd.Series(dtype=str))
                    .str.lower()
                    .str.contains("bdi|baltic", na=False)
            ]
            if len(bdi_row) > 0:
                df = _df_from_te_result(bdi_row, "BDI", "TradingEconomics/BalticExchange", "points")
                if not df.empty:
                    print(f"[정보] TE BDI 수집 완료 (상품목록 폴백): {len(df)}건")
                    return df
        print("[경고] Trading Economics BDI 심볼 확인 필요 — 수집 실패")
        return pd.DataFrame()
    except Exception as e:
        print(f"[경고] Trading Economics BDI 수집 실패: {e}")
        return pd.DataFrame()


def fetch_cpo() -> pd.DataFrame:
    """CPO (Crude Palm Oil) 현물 가격.

    CPO-SBO 스프레드 산출 시 사용 (G1 변수 CONDITIONAL INCLUDE).
    FRED PPOILUSDM 프록시 대비 더 자주 갱신됨.
    """
    if not _login():
        return pd.DataFrame()
    try:
        import tradingeconomics as te  # type: ignore
        for symbol in ("cpo", "palm-oil", "palm oil", "FCPO:COM"):
            try:
                result = te.getMarketsBySymbol(symbols=symbol, output_type="df")
                if result is not None and len(result) > 0:
                    df = _df_from_te_result(result, "CPO_USD_MT", "TradingEconomics/BursaMalaysia", "USD/MT")
                    if not df.empty:
                        print(f"[정보] TE CPO 수집 완료 (심볼: {symbol}): {len(df)}건")
                        return df
            except Exception:
                continue
        print("[경고] Trading Economics CPO 심볼 확인 필요 — FRED 프록시 사용 권장")
        return pd.DataFrame()
    except Exception as e:
        print(f"[경고] Trading Economics CPO 수집 실패: {e}")
        return pd.DataFrame()


def run() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y%m%d")
    frames = []

    bdi = fetch_bdi()
    if not bdi.empty:
        frames.append(bdi)

    cpo = fetch_cpo()
    if not cpo.empty:
        frames.append(cpo)

    if not frames:
        print("[경고] Trading Economics: 수집된 데이터 없음 — API 키 및 심볼 확인 필요.")
        return

    df = pd.concat(frames, ignore_index=True)
    out = f"{OUTPUT_DIR}/te_data_{today}.parquet"
    df.to_parquet(out, index=False)
    print(f"[완료] Trading Economics 데이터 {len(df)}건 저장 → {out}")


if __name__ == "__main__":
    run()
