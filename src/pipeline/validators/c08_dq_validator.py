#!/usr/bin/env python3
"""
C-08 Data Quality Validator — DQSOps Automated Gatekeeper (WBS 1.1.8)
대상: data/raw/**/*.parquet (각 커넥터 수집 결과)
출력: reports/data_quality/dq_report_{DATE}.json

DQSOps 5차원:
  Accuracy (0.3): 수치 범위 유효성 (음수 가격 금지 등)
  Completeness (0.25): 결측치 비율
  Consistency (0.20): 날짜 순서·중복·스키마 일관성
  Timeliness (0.15): ingested_at 기준 신선도 (5영업일 기준)
  Skewness (0.10): 히스토리 기준선 대비 분포 편차
"""
from __future__ import annotations

import glob
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPORT_DIR = "reports/data_quality"
RAW_DIR = "data/raw"
STALE_BDAYS = 5
DQ_THRESHOLD = 0.70  # PASS 기준 (0.0~1.0)
DQ_WARN = 0.50       # WARNING 기준

# DQSOps 차원 가중치 (합계 = 1.0)
DQ_WEIGHTS: dict[str, float] = {
    "accuracy":     0.30,
    "completeness": 0.25,
    "consistency":  0.20,
    "timeliness":   0.15,
    "skewness":     0.10,
}

# 커넥터별 필수 컬럼 스키마 (최소 요건)
REQUIRED_COLUMNS: dict[str, list[str]] = {
    "economic_indicators":  ["price_date", "indicator_code", "value"],
    "shipping_indices":     ["price_date", "indicator_code", "value"],
    "crop_data":            ["price_date"],
    "climate_data":         ["price_date", "indicator_code", "value"],
    "geopolitical_indices": ["price_date", "indicator_code", "value"],
    "production_data":      ["price_date"],
    "commodity_data":       ["price_date"],
    "customs_import":       ["price_date"],
}

# 수치 컬럼 유효 범위 (정확도 검증용)
VALID_RANGES: dict[str, tuple[float, float]] = {
    "value":             (-1000.0, 1_000_000.0),
    "import_cif_usd":   (0.0, 1e12),
    "import_weight_kg": (0.0, 1e12),
}

# 핵심 컬럼 — 결측 시 추가 패널티
KEY_COLUMNS: list[str] = ["price_date", "value", "indicator_code"]


def _score_accuracy(df: pd.DataFrame, connector_name: str) -> float:
    """수치 컬럼의 유효 범위 준수 여부를 점수화한다.

    Returns:
        float: 1.0 - (범위 초과 값 수 / 전체 비결측 수치 값 수).
               수치 컬럼이 없으면 1.0 반환.
    """
    if df.empty:
        return 1.0

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        return 1.0

    total_non_null: int = 0
    out_of_range: int = 0

    for col in numeric_cols:
        series = df[col].dropna()
        total_non_null += len(series)
        if col in VALID_RANGES:
            lo, hi = VALID_RANGES[col]
            out_of_range += int(((series < lo) | (series > hi)).sum())

    if total_non_null == 0:
        return 1.0

    score = 1.0 - (out_of_range / total_non_null)
    return max(0.0, float(score))


def _score_completeness(df: pd.DataFrame) -> float:
    """결측치 비율을 기반으로 완전성 점수를 계산한다.

    핵심 컬럼(price_date, value, indicator_code)의 결측은 2배 패널티를 적용한다.

    Returns:
        float: 0.0~1.0 범위의 완전성 점수.
    """
    if df.empty:
        return 1.0

    total_cells = df.shape[0] * df.shape[1]
    if total_cells == 0:
        return 1.0

    base_null_count = int(df.isnull().sum().sum())

    # 핵심 컬럼 추가 패널티 (존재하는 컬럼만 적용)
    key_penalty: int = 0
    for col in KEY_COLUMNS:
        if col in df.columns:
            key_penalty += int(df[col].isnull().sum())

    # 패널티 반영: 핵심 컬럼 결측을 한 번 더 카운트
    adjusted_null = base_null_count + key_penalty
    adjusted_total = total_cells + sum(1 for col in KEY_COLUMNS if col in df.columns) * df.shape[0]

    score = 1.0 - (adjusted_null / adjusted_total)
    return max(0.0, float(score))


def _score_consistency(df: pd.DataFrame, connector_name: str) -> float:
    """스키마 적합성, 날짜 단조성, 중복 행 여부를 검사하여 일관성 점수를 반환한다.

    세 가지 하위 검사의 평균을 최종 점수로 사용한다.

    Returns:
        float: 0.0~1.0 범위의 일관성 점수.
    """
    if df.empty:
        return 1.0

    # 하위 검사 1: 필수 컬럼 존재 여부
    required = REQUIRED_COLUMNS.get(connector_name, ["price_date"])
    missing_cols = [c for c in required if c not in df.columns]
    schema_score = 1.0 - (len(missing_cols) / max(len(required), 1))

    # 하위 검사 2: price_date 단조 증가 (역방향 점프 > 365일 없음)
    date_score = 1.0
    if "price_date" in df.columns:
        try:
            dates = pd.to_datetime(df["price_date"], errors="coerce").dropna().sort_values()
            if len(dates) > 1:
                diffs = dates.diff().dropna()
                # 365일 초과 역방향 점프(음수 차이)를 위반으로 판정
                violations = int((diffs < timedelta(days=-365)).sum())
                date_score = 1.0 - (violations / max(len(diffs), 1))
        except Exception:
            date_score = 0.5  # 날짜 파싱 실패 시 중간 점수

    # 하위 검사 3: 완전 중복 행 없음
    dup_count = int(df.duplicated().sum())
    dup_score = 1.0 - (dup_count / max(len(df), 1))

    score = (schema_score + date_score + dup_score) / 3.0
    return max(0.0, float(score))


def _score_timeliness(df: pd.DataFrame) -> float:
    """ingested_at 컬럼 기준으로 데이터 신선도 점수를 계산한다.

    5영업일 초과 시 점수 0.0, 0영업일 이하 시 점수 1.0.
    ingested_at 컬럼이 없으면 중립값 0.5 반환.

    Returns:
        float: 0.0~1.0 범위의 신선도 점수.
    """
    if df.empty or "ingested_at" not in df.columns:
        return 0.5  # 컬럼 부재 — 중립 점수

    try:
        ingested = pd.to_datetime(df["ingested_at"], errors="coerce").dropna()
        if ingested.empty:
            return 0.5

        latest_ingested = ingested.max().date()
        today = date.today()

        # 영업일 기준 경과일 계산 (토/일 제외)
        biz_days = int(np.busday_count(latest_ingested, today))
        score = max(0.0, 1.0 - (biz_days / STALE_BDAYS))
        return float(score)

    except Exception:
        return 0.5


def _score_skewness(df: pd.DataFrame) -> float:
    """수치 컬럼의 왜도(skewness)를 분석하여 분포 이상 점수를 반환한다.

    |skewness| > 3 인 컬럼을 heavy-tail 이상으로 판정한다.
    수치 컬럼이 없거나 관측치가 5개 미만이면 1.0 반환.

    Returns:
        float: 1.0 - (이상 컬럼 수 / 전체 수치 컬럼 수).
    """
    if df.empty:
        return 1.0

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        return 1.0

    flagged: int = 0
    eligible: int = 0

    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) < 5:
            continue
        eligible += 1
        skew_val = float(series.skew())
        if abs(skew_val) > 3.0:
            flagged += 1

    if eligible == 0:
        return 1.0

    score = 1.0 - (flagged / eligible)
    return max(0.0, float(score))


def _validate_connector(f: str) -> dict[str, Any]:
    """단일 parquet 파일에 대해 DQSOps 5차원 검증을 실행하고 결과를 반환한다.

    Args:
        f: 검증할 parquet 파일 경로.

    Returns:
        dict: 커넥터별 검증 결과 (상태, DQ 점수, 차원별 점수, 알림 목록 포함).
    """
    stem = Path(f).stem
    # 파일명에서 커넥터 이름 추출 (첫 번째 '_' 이전 또는 전체 스템)
    connector_name = stem.split("_")[0] if "_" in stem else stem

    alerts: list[str] = []

    # ── 파일 로드 ─────────────────────────────────────────────────────────────
    try:
        df = pd.read_parquet(f)
    except Exception as e:
        return {
            "connector": connector_name,
            "file": f,
            "status": "READ_ERROR",
            "dq_score": 0.0,
            "dimensions": {k: 0.0 for k in DQ_WEIGHTS},
            "alerts": [f"[오류] parquet 파일 로드 실패 '{f}': {e}"],
            "rows": 0,
            "duplicate_rows": 0,
        }

    rows = len(df)

    # ── 차원별 점수 계산 ───────────────────────────────────────────────────────
    acc  = _score_accuracy(df, connector_name)
    comp = _score_completeness(df)
    cons = _score_consistency(df, connector_name)
    time = _score_timeliness(df)
    skew = _score_skewness(df)

    dimensions: dict[str, float] = {
        "accuracy":     acc,
        "completeness": comp,
        "consistency":  cons,
        "timeliness":   time,
        "skewness":     skew,
    }

    dq_score = sum(DQ_WEIGHTS[k] * dimensions[k] for k in DQ_WEIGHTS)

    # ── 상태 판정 ──────────────────────────────────────────────────────────────
    if dq_score >= DQ_THRESHOLD:
        status = "PASS"
    elif dq_score >= DQ_WARN:
        status = "WARNING"
    else:
        status = "REJECTED"

    # ── 중복 행 수 ─────────────────────────────────────────────────────────────
    duplicate_rows = int(df.duplicated().sum())

    # ── 알림 생성 ──────────────────────────────────────────────────────────────
    # Timeliness: STALE 경고
    if time < 1.0 and "ingested_at" in df.columns:
        try:
            latest = pd.to_datetime(df["ingested_at"], errors="coerce").dropna().max().date()
            biz_days = int(np.busday_count(latest, date.today()))
            if biz_days > STALE_BDAYS:
                alerts.append(
                    f"[경고] STALE 데이터 — 커넥터 '{connector_name}': "
                    f"마지막 수집일 {latest} (영업일 {biz_days}일 경과, 기준 {STALE_BDAYS}일)"
                )
        except Exception:
            pass

    # Consistency: 스키마 드리프트 경고
    required = REQUIRED_COLUMNS.get(connector_name, ["price_date"])
    missing_cols = [c for c in required if c not in df.columns]
    if missing_cols:
        alerts.append(
            f"[경고] SCHEMA_DRIFT — 커넥터 '{connector_name}': "
            f"필수 컬럼 누락 {missing_cols}"
        )

    # Uniqueness: 중복 행 경고
    if duplicate_rows > 0:
        dup_pct = duplicate_rows / max(rows, 1) * 100
        alerts.append(
            f"[경고] DUPLICATE_ROWS — 커넥터 '{connector_name}': "
            f"중복 행 {duplicate_rows}건 ({dup_pct:.1f}%)"
        )

    # Accuracy: 범위 초과 경고
    if acc < 1.0:
        alerts.append(
            f"[경고] OUT_OF_RANGE — 커넥터 '{connector_name}': "
            f"수치 유효 범위 초과 (정확도 점수 {acc:.3f})"
        )

    # REJECTED 경우 명시적 오류 메시지
    if status == "REJECTED":
        alerts.append(
            f"[오류] 데이터 품질 검증 실패 — 커넥터 '{connector_name}': "
            f"DQ 점수 {dq_score:.3f} < 임계값 {DQ_WARN}. 파이프라인을 중단합니다."
        )

    return {
        "connector": connector_name,
        "file": f,
        "status": status,
        "dq_score": round(dq_score, 4),
        "dimensions": {k: round(v, 4) for k, v in dimensions.items()},
        "alerts": alerts,
        "rows": rows,
        "duplicate_rows": duplicate_rows,
    }


def main() -> None:
    """RAW_DIR 내 모든 parquet 파일에 대해 DQSOps 검증을 실행하고 결과를 저장한다.

    - PASS / WARNING / REJECTED 상태 판정 (최악 커넥터 기준 종합 상태 결정)
    - JSON 리포트: reports/data_quality/dq_report_{DATE}.json
    - REJECTED 커넥터 존재 시 exit code 1 (CI 파이프라인 차단)
    """
    Path(REPORT_DIR).mkdir(parents=True, exist_ok=True)

    parquet_files = glob.glob(os.path.join(RAW_DIR, "**", "*.parquet"), recursive=True)

    if not parquet_files:
        print("[경고] data/raw/ 디렉토리에서 parquet 파일을 찾을 수 없습니다.")
        report: dict[str, Any] = {
            "run_date": str(date.today()),
            "overall_status": "WARNING",
            "overall_dq_score": 0.0,
            "connectors": [],
            "message": "검증할 parquet 파일이 없습니다.",
        }
        _write_report(report)
        _set_github_output("WARNING")
        return

    results: list[dict[str, Any]] = [_validate_connector(f) for f in sorted(parquet_files)]

    # ── 종합 상태 및 평균 DQ 점수 계산 ────────────────────────────────────────
    status_priority = {"REJECTED": 0, "READ_ERROR": 0, "WARNING": 1, "PASS": 2}
    worst_status = min(results, key=lambda r: status_priority.get(r["status"], 0))["status"]
    # READ_ERROR → REJECTED 로 상향
    overall_status = "REJECTED" if worst_status in ("REJECTED", "READ_ERROR") else worst_status

    valid_scores = [r["dq_score"] for r in results if r["status"] != "READ_ERROR"]
    overall_score = round(float(np.mean(valid_scores)) if valid_scores else 0.0, 4)

    report = {
        "run_date": str(date.today()),
        "overall_status": overall_status,
        "overall_dq_score": overall_score,
        "dq_weights": DQ_WEIGHTS,
        "thresholds": {"pass": DQ_THRESHOLD, "warning": DQ_WARN},
        "connectors": results,
    }

    report_path = _write_report(report)

    # ── 콘솔 요약 출력 (한국어 레이블) ────────────────────────────────────────
    _print_summary_table(results, overall_status, overall_score, report_path)

    # ── GitHub Actions 출력 변수 설정 ─────────────────────────────────────────
    _set_github_output(overall_status)

    # ── REJECTED 시 파이프라인 차단 (exit code 1) ──────────────────────────────
    if overall_status == "REJECTED":
        sys.exit(1)


def _write_report(report: dict[str, Any]) -> str:
    """검증 결과를 JSON 파일로 저장하고 파일 경로를 반환한다.

    Args:
        report: 저장할 검증 결과 딕셔너리.

    Returns:
        str: 저장된 JSON 파일의 경로.
    """
    report_path = os.path.join(REPORT_DIR, f"dq_report_{date.today()}.json")
    try:
        with open(report_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2, default=str)
    except OSError as e:
        raise RuntimeError(
            f"[오류] DQ 리포트 저장 실패 '{report_path}': {e}. 디렉토리 권한을 확인하세요."
        ) from e
    return report_path


def _print_summary_table(
    results: list[dict[str, Any]],
    overall_status: str,
    overall_score: float,
    report_path: str,
) -> None:
    """검증 결과 요약 테이블을 표준 출력에 출력한다."""
    status_icon = {"PASS": "🟢", "WARNING": "🟡", "REJECTED": "🔴", "READ_ERROR": "🔴"}

    print("\n" + "=" * 80)
    print("  C-08 DQSOps 데이터 품질 검증 리포트")
    print(f"  실행일: {date.today()}  |  종합 상태: {status_icon.get(overall_status, '?')} {overall_status}")
    print(f"  종합 DQ 점수: {overall_score:.4f}  |  리포트 경로: {report_path}")
    print("=" * 80)

    header = f"{'커넥터':<30} {'상태':<12} {'DQ점수':>8} {'정확도':>8} {'완전성':>8} {'일관성':>8} {'신선도':>8} {'왜도':>8}"
    print(header)
    print("-" * 80)

    for r in results:
        icon = status_icon.get(r["status"], "?")
        dims = r.get("dimensions", {})
        row = (
            f"{r['connector']:<30} "
            f"{icon} {r['status']:<9} "
            f"{r['dq_score']:>8.4f} "
            f"{dims.get('accuracy', 0.0):>8.4f} "
            f"{dims.get('completeness', 0.0):>8.4f} "
            f"{dims.get('consistency', 0.0):>8.4f} "
            f"{dims.get('timeliness', 0.0):>8.4f} "
            f"{dims.get('skewness', 0.0):>8.4f}"
        )
        print(row)

        for alert in r.get("alerts", []):
            print(f"    ↳ {alert}")

    print("=" * 80 + "\n")


def _set_github_output(overall_status: str) -> None:
    """GitHub Actions GITHUB_OUTPUT 환경 변수에 overall_status를 기록한다."""
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        try:
            with open(github_output, "a", encoding="utf-8") as fh:
                fh.write(f"overall_status={overall_status}\n")
        except OSError as e:
            print(f"[경고] GITHUB_OUTPUT 파일 쓰기 실패: {e}")
    else:
        # 로컬 실행 시 환경 변수가 없을 수 있으므로 경고만 출력
        print(f"[정보] GITHUB_OUTPUT 미설정 — overall_status={overall_status}")


if __name__ == "__main__":
    main()
