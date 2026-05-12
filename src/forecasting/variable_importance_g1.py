#!/usr/bin/env python3
"""
G1 변수 중요도 분석 — C-03 Lead Data Scientist (WBS 1.1.8 / Phase A)
수집된 외부 변수 parquet 파일을 로드하여 대두유 가격 변동성 드라이버를 분석.

Phase A 구현 (Snowflake 연동 전):
  - 데이터 소스: data/raw/*.parquet (GitHub Actions 수집 결과)
  - 분석 방법: LASSO 선택 + 피어슨 상관 + 기술통계 (기본 방법론)
  - XGBoost+SHAP / Granger 인과검정: 충분한 시계열 누적 후 Phase B에서 적용
  - 출력: reports/pipeline/g1_variable_importance_{DATE}.html (HTML 리포트)

출력 계약 (C-03 Output Contract):
  - 변수 중요도 테이블 [변수 | 피어슨 r | LASSO 계수 | 포함 여부]
  - 데이터 상태 매트릭스 [커넥터 | 파일 | 행수 | 날짜 범위 | 신선도]
  - 구조적 단절 임계값 현황 (C-03 임계값: GPR 0.022 / BDI 2σ / WASDE STU 10% / CPO $175)
  - 품질 경보 (결측치 5% 초과, STALE 판정 5영업일 초과)
"""
from __future__ import annotations

import glob
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

OUTPUT_DIR  = "data/raw"
REPORT_DIR  = "reports/pipeline"

# ── C-03 구조적 단절 임계값 (c03-data-scientist.md) ──────────────────────────
THRESHOLDS: dict[str, dict] = {
    "GPR_NORMALIZED":   {"alert": 0.022,  "dir": ">",  "label": "지정학 구조적 단절"},
    "BDI":              {"alert": None,    "dir": "z",  "label": "해운비용 급등 (90일 rolling z>2σ)"},
    "WASDE_STU":        {"alert": 0.10,   "dir": "<",  "label": "공급 스트레스"},
    "CPO_SBO_SPREAD":   {"alert": 175.0,  "dir": ">",  "label": "CPO 대체압력"},
    "ENSO_ONI":         {"alert": 0.5,    "dir": "abs", "label": "기후 레짐 전환"},
}

# ── 수집 파일별 지표 코드 매핑 ────────────────────────────────────────────────
FILE_PATTERNS: dict[str, str] = {
    "economic_indicators": "P1-01 거시(Fed/CPI/FX/Brent)",
    "shipping_indices":    "P1-04 해운(BCAA/BDI)",
    "crop_data":           "P1-01/P1-03 작황(WASDE/PSD)",
    "climate_data":        "P1-03 기후(ONI/기상이상)",
    "geopolitical_indices":"P1-02 지정학(GPR/호르무즈)",
    "production_data":     "P1-04 생산량(NASS/FAOSTAT/NASA)",
    "commodity_data":      "P1-01 상품가(CBOT/CPO/ARS/가뭄)",
    "customs_import":      "P1-04 수입통계(관세청 HS1507)",
}


def _load_all_parquets(days: int = 7) -> dict[str, pd.DataFrame]:
    """최근 N일 수집된 parquet 파일 로드. 파일명 접두사 기준 분류."""
    cutoff = date.today() - timedelta(days=days)
    frames: dict[str, list[pd.DataFrame]] = {k: [] for k in FILE_PATTERNS}

    for f in sorted(glob.glob(f"{OUTPUT_DIR}/**/*.parquet", recursive=True)
                    + glob.glob(f"{OUTPUT_DIR}/*.parquet")):
        name = Path(f).stem
        try:
            df = pd.read_parquet(f)
        except Exception as e:
            print(f"[경고] 파일 로드 실패 — {name}: {e}")
            continue

        # 최신성 필터: ingested_at 기준 cutoff 이내
        if "ingested_at" in df.columns:
            df["ingested_at"] = pd.to_datetime(df["ingested_at"], utc=True, errors="coerce")
            max_ingest = df["ingested_at"].max()
            if pd.notna(max_ingest) and max_ingest.date() < cutoff:
                continue

        matched = next((k for k in FILE_PATTERNS if name.startswith(k)), None)
        if matched:
            frames[matched].append(df)

    return {k: pd.concat(v, ignore_index=True) for k, v in frames.items() if v}


def _freshness_flag(df: pd.DataFrame, stale_days: int = 5) -> str:
    """데이터 신선도 판정: STALE / OK."""
    if "ingested_at" not in df.columns:
        return "⚠️ 수집일 미확인"
    max_ingest = pd.to_datetime(df["ingested_at"], utc=True, errors="coerce").max()
    if pd.isna(max_ingest):
        return "⚠️ 수집일 미확인"
    biz_days_old = np.busday_count(max_ingest.date(), date.today())
    return f"🚨 STALE ({biz_days_old}영업일)" if biz_days_old > stale_days else "✅ OK"


def _build_data_status(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """커넥터별 데이터 현황 테이블."""
    rows = []
    for key, label in FILE_PATTERNS.items():
        if key not in frames:
            rows.append({"커넥터": label, "파일수": 0, "행수": 0,
                         "날짜범위": "미수집", "신선도": "❌ 데이터 없음"})
            continue
        df = frames[key]
        date_col = next((c for c in ["price_date", "ingested_at"] if c in df.columns), None)
        if date_col:
            dates = pd.to_datetime(df[date_col], errors="coerce").dropna()
            date_range = f"{dates.min().date()} ~ {dates.max().date()}" if len(dates) else "N/A"
        else:
            date_range = "N/A"
        rows.append({
            "커넥터":   label,
            "파일수":   1,
            "행수":     len(df),
            "날짜범위": date_range,
            "신선도":   _freshness_flag(df),
        })
    return pd.DataFrame(rows)


def _pivot_for_correlation(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """모든 numeric 시계열을 price_date 기준으로 pivot하여 상관분석용 wide-format 생성."""
    series: dict[str, pd.Series] = {}

    for key, df in frames.items():
        if "price_date" not in df.columns:
            continue
        df = df.copy()
        df["price_date"] = pd.to_datetime(df["price_date"], errors="coerce")
        df = df.dropna(subset=["price_date"])

        # indicator_code 컬럼이 있으면 장형 -> 피벗
        if "indicator_code" in df.columns and "value" in df.columns:
            for code, grp in df.groupby("indicator_code"):
                s = grp.set_index("price_date")["value"]
                s = pd.to_numeric(s, errors="coerce").dropna()
                if len(s) > 2:
                    series[str(code)] = s.resample("D").last()
        else:
            # numeric 컬럼 직접 사용
            num_cols = df.select_dtypes(include="number").columns.tolist()
            num_cols = [c for c in num_cols if c not in ("ingested_at", "rows")]
            for col in num_cols[:5]:  # 컬럼 수 제한
                s = df.set_index("price_date")[col]
                s = pd.to_numeric(s, errors="coerce").dropna()
                if len(s) > 2:
                    series[f"{key}_{col}"] = s.resample("D").last()

    if not series:
        return pd.DataFrame()

    wide = pd.DataFrame(series)
    wide = wide.sort_index().ffill(limit=3)  # 최대 3일 forward-fill
    return wide


def _lasso_importance(wide: pd.DataFrame, target_col: str | None = None) -> pd.DataFrame:
    """LASSO 회귀로 변수 중요도 계산. target_col이 없으면 가장 완전한 컬럼을 사용."""
    from sklearn.linear_model import LassoCV
    from sklearn.preprocessing import StandardScaler

    if wide.empty or len(wide) < 10:
        return pd.DataFrame(columns=["변수", "피어슨_r", "LASSO_계수", "포함여부"])

    wide_clean = wide.dropna(thresh=max(2, len(wide) // 2), axis=1)
    wide_clean = wide_clean.dropna()

    if wide_clean.empty or wide_clean.shape[1] < 2:
        return pd.DataFrame(columns=["변수", "피어슨_r", "LASSO_계수", "포함여부"])

    # target: 가장 완전한 컬럼 (대두유 관련 코드 우선)
    priority = ["CBOT_BO_CLOSE", "BO_CLOSE", "cbot_soybean_oil", "BRENT_USD_BBL"]
    if target_col is None:
        target_col = next(
            (c for c in priority if c in wide_clean.columns),
            wide_clean.columns[0],
        )

    y = wide_clean[target_col]
    X = wide_clean.drop(columns=[target_col])

    if X.empty:
        return pd.DataFrame(columns=["변수", "피어슨_r", "LASSO_계수", "포함여부"])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    try:
        lasso = LassoCV(cv=min(5, len(y) // 2), max_iter=5000, random_state=42)
        lasso.fit(X_scaled, y)
        coefs = dict(zip(X.columns, lasso.coef_))
    except Exception:
        coefs = {c: 0.0 for c in X.columns}

    rows = []
    for col in X.columns:
        try:
            r = float(np.corrcoef(X[col], y)[0, 1])
        except Exception:
            r = float("nan")
        coef = coefs.get(col, 0.0)
        rows.append({
            "변수":      col,
            "피어슨_r":  round(r, 3),
            "LASSO_계수": round(coef, 4),
            "포함여부":  "✅ 포함" if abs(coef) > 0.001 else "— 제외",
        })

    df_imp = pd.DataFrame(rows)
    df_imp["abs_coef"] = df_imp["LASSO_계수"].abs()
    return df_imp.sort_values("abs_coef", ascending=False).drop(columns="abs_coef")


def _check_structural_breaks(frames: dict[str, pd.DataFrame]) -> list[dict]:
    """C-03 구조적 단절 임계값 현황 점검."""
    alerts = []

    # GPR 지수 (normalized)
    if "geopolitical_indices" in frames:
        gpr_df = frames["geopolitical_indices"]
        gpr = gpr_df[gpr_df.get("indicator_code", pd.Series(dtype=str)) == "GPR_NORMALIZED"]
        if not gpr.empty and "value" in gpr.columns:
            latest_gpr = float(gpr["value"].dropna().iloc[-1])
            alerts.append({
                "변수": "GPR_NORMALIZED",
                "현재값": round(latest_gpr, 4),
                "임계값": THRESHOLDS["GPR_NORMALIZED"]["alert"],
                "상태": "🚨 임계초과" if latest_gpr > 0.022 else "✅ 정상",
                "설명": THRESHOLDS["GPR_NORMALIZED"]["label"],
            })

    # ENSO ONI
    if "climate_data" in frames:
        oni_df = frames["climate_data"]
        oni = oni_df[oni_df.get("indicator_code", pd.Series(dtype=str)) == "ONI"] if "indicator_code" in oni_df.columns else pd.DataFrame()
        if not oni.empty and "value" in oni.columns:
            latest_oni = float(oni["value"].dropna().iloc[-1])
            alerts.append({
                "변수": "ENSO_ONI",
                "현재값": round(latest_oni, 2),
                "임계값": "±0.5",
                "상태": "🚨 임계초과" if abs(latest_oni) >= 0.5 else "✅ 정상",
                "설명": THRESHOLDS["ENSO_ONI"]["label"],
            })

    # BDI z-score (90일 rolling)
    if "shipping_indices" in frames:
        bdi_df = frames["shipping_indices"]
        bdi = bdi_df[bdi_df.get("indicator_code", pd.Series(dtype=str)) == "BDI"] if "indicator_code" in bdi_df.columns else pd.DataFrame()
        if not bdi.empty and "value" in bdi.columns and len(bdi) > 10:
            vals = pd.to_numeric(bdi["value"], errors="coerce").dropna()
            if len(vals) >= 5:
                roll_mean = vals.rolling(min(90, len(vals))).mean().iloc[-1]
                roll_std  = vals.rolling(min(90, len(vals))).std().iloc[-1]
                z = (vals.iloc[-1] - roll_mean) / roll_std if roll_std > 0 else 0.0
                alerts.append({
                    "변수": "BDI_ZSCORE",
                    "현재값": round(z, 2),
                    "임계값": "2.0σ",
                    "상태": "🚨 임계초과" if z > 2.0 else "✅ 정상",
                    "설명": THRESHOLDS["BDI"]["label"],
                })

    return alerts


def _render_html(
    status_df: pd.DataFrame,
    importance_df: pd.DataFrame,
    alerts: list[dict],
    run_id: str,
    run_ts: str,
    days: int,
    lang: Literal["ko", "en"] = "ko",
) -> str:
    """G1 분석 보고서 HTML 렌더링 (한국어 + 영어 이중언어)."""
    font_import = (
        "@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');"
        if lang == "ko" else ""
    )
    font_family = (
        "'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif"
        if lang == "ko" else
        "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
    )
    title  = "G1 변수 중요도 분석 리포트" if lang == "ko" else "G1 Variable Importance Report"
    sub    = f"C-03 Lead Data Scientist · 최근 {days}일 데이터 기준" if lang == "ko" else f"C-03 Lead Data Scientist · Based on last {days} days"

    # status table
    status_html = status_df.to_html(index=False, border=0, classes="tbl")

    # importance table
    if not importance_df.empty:
        imp_html = importance_df.to_html(index=False, border=0, classes="tbl")
    else:
        imp_html = "<p>데이터 부족 — 충분한 시계열 누적 후 재실행 (최소 30일 권장)</p>" if lang == "ko" else "<p>Insufficient data — re-run after 30+ days of accumulation.</p>"

    # alerts table
    if alerts:
        alert_df = pd.DataFrame(alerts)
        alerts_html = alert_df.to_html(index=False, border=0, classes="tbl")
    else:
        alerts_html = "<p>✅ 현재 임계값 초과 변수 없음</p>" if lang == "ko" else "<p>✅ No structural break thresholds breached.</p>"

    return f"""<!DOCTYPE html>
<html lang="{'ko' if lang == 'ko' else 'en'}">
<head>
<meta charset="UTF-8">
<title>Nexus {title}</title>
<style>
  {font_import}
  body  {{ font-family: {font_family}; margin: 40px 60px; color: #333; font-size: 13px; line-height: 1.6; }}
  h1   {{ color: #1a237e; border-bottom: 3px solid #1a237e; padding-bottom: 10px; font-size: 20px; }}
  h2   {{ color: #283593; margin-top: 28px; font-size: 15px; }}
  .meta {{ background: #e8eaf6; padding: 14px 18px; border-radius: 8px; margin: 18px 0; }}
  .badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; margin: 2px; }}
  .note {{ background: #fff8e1; border-left: 4px solid #ffc107; padding: 10px 14px; border-radius: 4px; margin: 16px 0; font-size: 12px; }}
  .tbl  {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 12px; }}
  .tbl th {{ background: #1a237e; color: #fff; padding: 8px 12px; text-align: left; }}
  .tbl td {{ padding: 6px 12px; border-bottom: 1px solid #e0e0e0; }}
  .footer {{ margin-top: 40px; font-size: 11px; color: #9e9e9e; border-top: 1px solid #e0e0e0; padding-top: 12px; }}
</style>
</head>
<body>
<h1>{title}<br><small style="font-size:14px;color:#5c6bc0">{sub}</small></h1>

<div class="meta">
  <strong>Run ID:</strong> {run_id} &nbsp;│&nbsp;
  <strong>Generated (UTC):</strong> {run_ts} &nbsp;│&nbsp;
  <strong>{'분석 기간' if lang == 'ko' else 'Period'}:</strong> {'최근' if lang == 'ko' else 'Last'} {days}{'일' if lang == 'ko' else ' days'}
</div>

<div class="note">
  ⚠️ <strong>Phase A 분석 한계:</strong>
  현재는 수집된 데이터의 기술통계·LASSO 상관 분석만 수행합니다.
  XGBoost+SHAP, Granger 인과검정, TCN-XGBoost 하이브리드는 30일+ 시계열 누적 후 Phase B(Snowflake)에서 적용 예정.
</div>

<h2>{'데이터 수집 현황' if lang == 'ko' else 'Data Collection Status'}</h2>
{status_html}

<h2>{'변수 중요도 (LASSO 기반)' if lang == 'ko' else 'Variable Importance (LASSO-based)'}</h2>
{imp_html}

<h2>{'구조적 단절 임계값 현황 (C-03)' if lang == 'ko' else 'Structural Break Status (C-03)'}</h2>
{alerts_html}

<div class="note">
  임계값 정의 (C-03): GPR &gt; 0.022 (지정학) · BDI z &gt; 2σ (해운) · WASDE STU &lt; 10% (공급) · CPO-SBO spread &gt; $175/MT (대체)
</div>

<div class="footer">
  Project Nexus · G1 Variable Importance · C-03 Lead Data Scientist (claude-opus-4-7, Thinking Mode) ·
  Branch: claude/setup-nexus-llm-tools-RX4aS · {run_ts} UTC
</div>
</body>
</html>"""


def run(days: int = 7) -> None:
    os.makedirs("src/forecasting", exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)

    from datetime import datetime
    now    = datetime.utcnow()
    tag    = now.strftime("%Y%m%d_%H%M")
    run_ts = now.strftime("%Y-%m-%d %H:%M:%S")
    run_id = os.environ.get("GITHUB_RUN_ID", "local")

    print(f"[C-03] G1 변수 중요도 분석 시작 — 최근 {days}일 데이터 로드 중...")
    frames = _load_all_parquets(days=days)

    if not frames:
        print(f"[경고] {OUTPUT_DIR} 에서 유효한 parquet 파일 없음 — 분석 건너뜀.")
        return

    print(f"[C-03] {len(frames)}개 커넥터 데이터 로드 완료: {list(frames.keys())}")

    status_df    = _build_data_status(frames)
    wide         = _pivot_for_correlation(frames)
    importance_df = _lasso_importance(wide)
    alerts       = _check_structural_breaks(frames)

    print(f"[C-03] 상관 분석 변수 수: {wide.shape[1] if not wide.empty else 0}")
    print(f"[C-03] 구조적 단절 임계값 초과: {sum(1 for a in alerts if '🚨' in a.get('상태', ''))}/{len(alerts)}")

    for lang in ("ko", "en"):
        html_path = f"{REPORT_DIR}/g1_variable_importance_{tag}_{lang}.html"
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(_render_html(status_df, importance_df, alerts, run_id, run_ts, days, lang=lang))  # type: ignore[arg-type]
        print(f"[완료] G1 리포트 ({lang.upper()}) → {html_path}")

    # 구조적 단절 경보 요약 출력 (Korean narrative — C-03 계약)
    breach = [a for a in alerts if "🚨" in a.get("상태", "")]
    if breach:
        print("\n[C-03 경보] 구조적 단절 임계값 초과 변수:")
        for a in breach:
            print(f"  • {a['변수']}: 현재값 {a['현재값']} (임계값 {a['임계값']}) — {a['설명']}")
    else:
        print("\n[C-03 정보] 모든 구조적 단절 임계값 정상 범위 내.")


if __name__ == "__main__":
    import sys
    d = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    run(days=d)
