"""대두유 시장·유통 구조 지표 (A-291 · 승인자 상시 원칙 2026-09-27 — 놓치기 쉬운 구조 요인의 정량화).

원시 parquet(data/raw)에서 8개 구조 지표를 계산해 data/raw/structural_indicators.parquet로 쓴다.
feature mart가 재귀 글로브로 읽으므로 변인 순위(G1)·브리프에 자동 편입된다.

| 코드 | 정의 | 경로(왜 보나) |
|---|---|---|
| STR_SBO_PALM_SPREAD | 대두유 $/t − 팜유 $/t (MYR/t ÷ 당시 환율) | 경쟁 식물성유 대체 — 2020년 이후 공행성 붕괴(farmdoc 2025-12) |
| STR_BOHO_SPREAD | 대두유 $/lb × 7.5 − 난방유 $/gal | 바이오디젤 원료 경제성 — D4 RIN의 약 80% 설명(Irwin 외 AJAE 2020) |
| STR_OIL_VALUE_SHARE | 대두유 11lb 가치 ÷ 대두 1부셸 가격 | 기름 비중과 압착 마진이 섞인 대리(대두박 가격 미보유) — farmdoc 25~35%→35~50% 구간 기준은 적용 불가 |
| STR_US_SBO_BIOFUEL_SHARE | 미국 대두유 바이오연료 사용 ÷ 총사용(WASDE) | 수요 구조 전환 15%→54% |
| STR_KR_CRUDE_SBO_ORIGIN_HHI | 한국 조대두유 수입 원산지 집중도(0~1) | 공급선 편중 — 2026 베트남 집중 |
| STR_KR_CRUDE_SBO_VN_SHARE | 조대두유 수입 중 베트남 비중 | 제3국 가공 허브 부상(D-045) |
| STR_KR_IMPORT_CRUSH_MARGIN | 0.19×조대두유 + 0.79×대두박 − 채유용 대두 도착 단가($/t) | 한국 압착 채산성(CE-024) — 국내 압착 축소 → 조유 수입 수요 |
| STR_KR_CRUDE_SBO_CIF_PREMIUM | 한국 조대두유 도착 단가 − 전월 시카고 선물 평균($/t) | 운임·원산지 프리미엄 층(참고 범위의 실측 차이층) |

한국(STR_KR_) 지표는 시카고 가격 동인이 아니라 한국 조달 노출도 지표 — G1 순위(시카고 20일 수익률) 대상에서 제외.
as-of: 값의 available_at = 쓰인 입력들의 available_at 최댓값. 환율은 그 날짜에 이미 공표된 값만 쓴다.
"""
from __future__ import annotations

import glob
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAW_DIR = Path("data/raw")
OUT_PATH = RAW_DIR / "structural_indicators.parquet"
LB_PER_MT = 2204.62
OIL_LB_PER_BU = 11.0            # CME 보드 크러시 관례(대두 1부셸 → 대두유 11lb)
BIODIESEL_LB_PER_GAL = 7.5      # farmdoc·Irwin BOHO 관례
KR_CRUDE = "KCS_1507101000"     # 관세청 식용 조대두유(10단위)
KR_MEAL, KR_BEAN = "KCS_230400", "KCS_1201901000"   # 대두박 · 채유용 대두
KR_YIELD_OIL, KR_YIELD_MEAL = 0.19, 0.79              # 한국 압착 수율 관례(대두 1톤 → 기름·박)
CODES = {"CBOT_BO_CLOSE", "TE_PALM_OIL", "DEXMAUS", "TE_HEATING_OIL", "TE_SOYBEANS",
         "WASDE_USDOM_SBO_BIODIESEL_USE", "WASDE_USDOM_SBO_TOTAL_USE"}


def _dates(s: pd.Series) -> pd.Series:
    s = pd.to_datetime(s, errors="coerce", utc=True)
    return s.dt.tz_convert(None).dt.normalize()


def load_inputs(raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    """필요 지표만 롱 포맷으로 읽는다 — 아티팩트 중첩 착지로 같은 파일이 두 번 있어도 (코드, 일자) 중복 제거."""
    parts = []
    for f in glob.glob(str(raw_dir / "**" / "*.parquet"), recursive=True):
        if Path(f).name == OUT_PATH.name or "te_commodities_usd_mt" in f:   # 자기 산출물·달러 환산본 제외
            continue
        try:
            df = pd.read_parquet(f, columns=None)
        except Exception:                                   # noqa: BLE001 — 손상 파일은 건너뜀
            continue
        if not {"indicator_code", "value", "price_date", "available_at"} <= set(df.columns):
            continue
        code = df["indicator_code"].astype(str)
        df = df[code.isin(CODES) | code.str.startswith((KR_CRUDE, KR_MEAL, KR_BEAN))]
        if not df.empty:
            parts.append(df[["indicator_code", "price_date", "value", "available_at"]])
    if not parts:
        return pd.DataFrame(columns=["indicator_code", "price_date", "value", "available_at"])
    out = pd.concat(parts, ignore_index=True)
    out["price_date"], out["available_at"] = _dates(out["price_date"]), _dates(out["available_at"])
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    out = out.dropna(subset=["price_date", "value", "available_at"])
    return (out.sort_values("available_at")
            .drop_duplicates(["indicator_code", "price_date"], keep="last").reset_index(drop=True))


def _s(long: pd.DataFrame, code: str) -> pd.DataFrame:
    return (long[long["indicator_code"] == code].set_index("price_date")[["value", "available_at"]]
            .sort_index())


def _asof_fx(dates: pd.Series, fx: pd.DataFrame) -> pd.DataFrame:
    """각 날짜에 **이미 공표된**(available_at ≤ 날짜) 최신 환율 — 사후 공표값 사용 금지."""
    left = pd.DataFrame({"d": pd.to_datetime(dates)}).sort_values("d")
    right = fx.reset_index()[["value", "available_at"]].sort_values("available_at")
    m = pd.merge_asof(left, right, left_on="d", right_on="available_at", direction="backward")
    return m.set_index("d")


def _rows(code: str, df: pd.DataFrame, unit: str, note: str, monthly: bool = False) -> pd.DataFrame:
    df = df.dropna(subset=["value", "available_at"])
    out = pd.DataFrame({"indicator_code": code, "price_date": df.index, "value": df["value"].values,
                        "available_at": df["available_at"].values, "unit": unit, "note": note})
    out["event_time"] = out["price_date"]
    out["period_end"] = out["price_date"] + (pd.offsets.MonthEnd(0) if monthly else pd.Timedelta(0))
    out["available_at"] = out[["available_at", "period_end"]].max(axis=1)   # 역전 방지(기간 종료 전 공표 불가)
    out["release_time"] = out["available_at"]
    return out


def _cif(long: pd.DataFrame, prefix: str) -> pd.DataFrame:
    """관세청 원산지 합계 도착 단가($/톤) — 수집된 원산지 물량 가중(WORLD 행 없는 품목용)."""
    x = long[long["indicator_code"].str.startswith(prefix + "_IMP_")]
    usd = x[x["indicator_code"].str.contains("_IMP_USD_")].groupby("price_date")["value"].sum()
    kg = x[x["indicator_code"].str.contains("_IMP_KG_")].groupby("price_date")["value"].sum()
    return pd.DataFrame({"value": (usd / kg * 1000).where(kg > 0),
                         "available_at": x.groupby("price_date")["available_at"].max()})


def _kr_crush_margin(long: pd.DataFrame, world_kg: pd.Series, kr: pd.DataFrame) -> pd.DataFrame:
    """CE-024(한국 압착 채산성) 정량화 — 세 품목 모두 수입이 있는 달만."""
    usd = kr[kr["indicator_code"] == f"{KR_CRUDE}_IMP_USD_WORLD"].set_index("price_date")["value"]
    oil = pd.DataFrame({"value": usd / world_kg * 1000,
                        "available_at": kr.groupby("price_date")["available_at"].max()})
    meal, bean = _cif(long, KR_MEAL), _cif(long, KR_BEAN)
    j = oil.join(meal, rsuffix="_m", how="inner").join(bean, rsuffix="_b", how="inner").dropna()
    return pd.DataFrame({"value": KR_YIELD_OIL * j["value"] + KR_YIELD_MEAL * j["value_m"] - j["value_b"],
                         "available_at": j[["available_at", "available_at_m", "available_at_b"]].max(axis=1)})


def build(long: pd.DataFrame) -> pd.DataFrame:
    frames = []
    sbo = _s(long, "CBOT_BO_CLOSE")                          # ¢/lb, 정산가
    if not sbo.empty:
        sbo_t = sbo.assign(value=sbo["value"] / 100 * LB_PER_MT)
        palm, fx = _s(long, "TE_PALM_OIL"), _s(long, "DEXMAUS")
        if not palm.empty and not fx.empty:
            j = sbo_t.join(palm, how="inner", rsuffix="_p")
            f = _asof_fx(j.index.to_series(), fx)
            j = j.assign(value=j["value"] - j["value_p"] / f["value"].values,
                         available_at=np.maximum(j["available_at"], j["available_at_p"]))
            frames.append(_rows("STR_SBO_PALM_SPREAD", j, "USD/MT",
                                "대두유 정산가 − 팜유 3월물 정산가(MYR/t ÷ 공표 환율 DEXMAUS)"))
        ho = _s(long, "TE_HEATING_OIL")
        if not ho.empty:
            j = sbo.join(ho, how="inner", rsuffix="_h")
            j = j.assign(value=j["value"] / 100 * BIODIESEL_LB_PER_GAL - j["value_h"],
                         available_at=np.maximum(j["available_at"], j["available_at_h"]))
            frames.append(_rows("STR_BOHO_SPREAD", j, "USD/gal", "대두유 $/lb × 7.5 − 난방유 $/gal"))
        soy = _s(long, "TE_SOYBEANS")
        if not soy.empty:
            j = sbo.join(soy, how="inner", rsuffix="_s")
            j = j.assign(value=(j["value"] / 100 * OIL_LB_PER_BU) / (j["value_s"] / 100),   # TE 대두는 ¢/bu(라벨은 USD)
                         available_at=np.maximum(j["available_at"], j["available_at_s"]))
            frames.append(_rows("STR_OIL_VALUE_SHARE", j, "ratio",
                                "대두유 11lb 가치 ÷ 대두 $/bu — 기름 비중×(1+압착 마진/대두가) 혼합 대리(대두박 미보유·farmdoc 구간 비교 불가)"))

    bio, tot = _s(long, "WASDE_USDOM_SBO_BIODIESEL_USE"), _s(long, "WASDE_USDOM_SBO_TOTAL_USE")
    if not bio.empty and not tot.empty:
        j = bio.join(tot, how="inner", rsuffix="_t")
        j = j.assign(value=j["value"] / j["value_t"],
                     available_at=np.maximum(j["available_at"], j["available_at_t"]))
        frames.append(_rows("STR_US_SBO_BIOFUEL_SHARE", j, "ratio",
                            "WASDE 미국 대두유 바이오연료 사용 ÷ 총사용(수출 포함) — 해당 회차 전망 · 5월 신곡 전환 계단 · 2021년 전후 정의 차이(재생디젤 포함)", monthly=True))

    kr = long[long["indicator_code"].str.startswith(f"{KR_CRUDE}_IMP_")]
    if not kr.empty:
        kg = kr[kr["indicator_code"].str.contains("_IMP_KG_")]
        vol = kg.pivot_table(index="price_date", columns="indicator_code", values="value")
        vol.columns = [c.rsplit("_", 1)[-1] for c in vol.columns]
        avail = kr.groupby("price_date")["available_at"].max()
        if "WORLD" in vol:
            world = vol.pop("WORLD")
            ok = world > 0
            idx = pd.date_range(vol.index.min(), vol.index.max(), freq="MS")
            # 한 달 한두 척 화물로 요동치지 않게 최근 12개월 물량 합으로 본다. 행 없는 원산지 = 그 달 수입 없음(A-086)
            w = world.reindex(idx)
            vol12 = vol.reindex(idx).fillna(0).where(w.notna(), axis=0).rolling(12, min_periods=9).sum()   # WORLD 미공표 달 제외
            world12 = w.rolling(12, min_periods=9).sum()
            share = vol12.div(world12, axis=0)[(world12 > 0) & w.notna()]   # 그 달 WORLD가 있어야 값 산출
            other = (1 - share.sum(axis=1)).clip(lower=0)
            hhi = (share ** 2).sum(axis=1) + other ** 2     # ponytail: 기타 원산지를 한 덩어리로 봄 — 상한 쪽 편향(조유는 차이 0.008 이하), 원산지 목록 확장 시 교체
            avail = avail.reindex(idx).ffill()
            frames.append(_rows("STR_KR_CRUDE_SBO_ORIGIN_HHI",
                                pd.DataFrame({"value": hhi, "available_at": avail}), "0-1",
                                "한국 조대두유 수입 원산지 집중도(최근 12개월 물량 기준 HHI)", monthly=True))
            if "VN" in share:
                frames.append(_rows("STR_KR_CRUDE_SBO_VN_SHARE",
                                    pd.DataFrame({"value": share["VN"], "available_at": avail}), "ratio",
                                    "한국 조대두유 수입 중 베트남 비중(최근 12개월 물량)", monthly=True))
            usd = kr[kr["indicator_code"] == f"{KR_CRUDE}_IMP_USD_WORLD"].set_index("price_date")["value"]
            if not sbo.empty and not usd.empty:
                cif = (usd / world * 1000).where(ok)                                  # $/t
                # 도착 40~50일 전에 가격이 정해지므로 전월 시카고 평균과 비교(같은 달 비교는 시차 혼입 — A-190)
                sbo_m = (sbo["value"] / 100 * LB_PER_MT).resample("MS").mean().shift(1)
                prem = (cif - sbo_m).dropna()
                frames.append(_rows("STR_KR_CRUDE_SBO_CIF_PREMIUM",
                                    pd.DataFrame({"value": prem, "available_at": avail}), "USD/MT",
                                    "한국 조대두유 도착 단가 − 전월 시카고 선물 평균(운임·원산지 프리미엄 혼재 — 호가 기준 베이시스 아님)",
                                    monthly=True))
        margin = _kr_crush_margin(long, world.where(ok), kr)
        if not margin.empty:
            frames.append(_rows("STR_KR_IMPORT_CRUSH_MARGIN", margin, "USD/MT",
                                "관세청 도착 단가 기준 압착 마진: 0.19×조대두유 + 0.79×대두박 − 채유용 대두($/톤 대두)",
                                monthly=True))
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out["source_name"] = "NEXUS_STRUCTURAL"
    out["source_vintage"] = None
    out["vintage_known"] = False
    out["ingested_at"] = pd.Timestamp.now("UTC")
    return out


def run(raw_dir: Path = RAW_DIR, out_path: Path = OUT_PATH) -> pd.DataFrame:
    out = build(load_inputs(raw_dir))
    if out.empty:
        print("[경고] 구조 지표 입력 부족 — 산출 없음(대두유 정산가·팜유·관세청 원시 계열 확인)")
        return out
    out.to_parquet(out_path, index=False)
    for code, g in out.groupby("indicator_code"):
        last = g.sort_values("price_date").iloc[-1]
        print(f"[완료] {code}: {len(g):,}건 {g['price_date'].min().date()}~{g['price_date'].max().date()}"
              f" · 최근 {last['value']:.3f} {last['unit']}")
    return out


def _self_test() -> None:
    d0, d1 = pd.Timestamp("2026-08-03"), pd.Timestamp("2026-08-04")
    rows = [("CBOT_BO_CLOSE", d0, 60.0, d0), ("CBOT_BO_CLOSE", d1, 60.0, d1),
            ("TE_PALM_OIL", d0, 4400.0, d0), ("TE_PALM_OIL", d1, 4400.0, d1),
            ("DEXMAUS", d0, 4.0, d1),                          # 8/3 환율은 8/4에 공표
            ("TE_HEATING_OIL", d0, 3.0, d1)]                   # 에너지 종가는 하루 뒤 반영(M-014)
    long = pd.DataFrame(rows, columns=["indicator_code", "price_date", "value", "available_at"])
    out = build(long).set_index(["indicator_code", "price_date"])
    spread = out.loc[("STR_SBO_PALM_SPREAD", d1), "value"]
    assert abs(spread - (60 / 100 * LB_PER_MT - 1100)) < 1e-6, spread
    assert ("STR_SBO_PALM_SPREAD", d0) not in out.index          # 8/3엔 환율 미공표 → 산출 없음(as-of)
    assert abs(out.loc[("STR_BOHO_SPREAD", d0), "value"] - (0.6 * 7.5 - 3.0)) < 1e-9
    assert (out["available_at"] >= out["event_time"]).all()
    print("[완료] 구조 지표 자체검증 통과")


if __name__ == "__main__":
    _self_test() if "--self-test" in sys.argv else run()
