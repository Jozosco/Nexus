#!/usr/bin/env python3
"""
as-of 시점 정합성 검증 — 모델 진입 게이트 (D-023 · A-114)

검사 항목:
  ① 필수 필드 존재      — event_time · available_at
  ② 결측 없음           — 위 두 필드
  ③ 시간 역전 없음      — available_at >= event_time (미래 정보가 과거에 보이면 안 됨)
  ④ 미래 available_at   — 오늘보다 미래면 그 행은 **현재 모델이 쓸 수 없음**(경고)
  ⑤ 개정 소스 vintage   — revises=True 소스에 source_vintage가 있는가
  ⑥ 스키마 정합         — data/schemas/*.yaml에 5필드가 선언돼 있는가

위반 시 종료코드 1 — 파이프라인이 모델 학습으로 진행하지 못하게 차단한다.
"검증할 게 없어서 통과"를 막기 위해, 대상 parquet이 0건이면 그것도 실패로 본다(A-108 교훈).

사용:
    python scripts/validate_asof.py            # data/raw 전수
    python scripts/validate_asof.py --warn     # 경고만(종료코드 0) — 이행기 전용
의존성: pandas · pyarrow · pyyaml
"""
from __future__ import annotations

import glob
import os
import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.pipeline.asof import ASOF_FIELDS, ASOF_REQUIRED, rule_for  # noqa: E402

RAW_DIR = os.environ.get("NEXUS_DATA_ROOT", "data/raw")
SCHEMA_DIR = Path("data/schemas")

# 이행기 면제 — as-of 부여 전에 수집된 산출물. 적용 완료 시 목록에서 제거한다.
EXEMPT_PREFIXES: set[str] = set(
    filter(None, os.environ.get("ASOF_EXEMPT", "").split(","))
)


def _check_frame(path: str, df: pd.DataFrame) -> list[str]:
    """단일 parquet 검증 → 위반 메시지 목록."""
    name = os.path.basename(path)
    issues: list[str] = []

    missing = [f for f in ASOF_REQUIRED if f not in df.columns]
    if missing:
        return [f"{name}: 필수 as-of 필드 없음 — {', '.join(missing)}"]

    for f in ASOF_REQUIRED:
        n = int(df[f].isna().sum())
        if n:
            issues.append(f"{name}: {f} 결측 {n:,}/{len(df):,}행")

    ev = pd.to_datetime(df["event_time"], errors="coerce")
    av = pd.to_datetime(df["available_at"], errors="coerce")
    inverted = int((av < ev).sum())
    if inverted:
        worst = (ev - av).max()
        issues.append(f"{name}: available_at < event_time 역전 {inverted:,}행 (최대 {worst})")

    future = int((av > pd.Timestamp(date.today())).sum())
    if future:
        issues.append(f"{name}: available_at이 미래인 행 {future:,}건 — 현시점 모델 사용 불가(정상일 수 있음)")

    # 개정 소스인데 vintage가 없으면 백테스트에서 최신값을 쓰게 된다
    if "indicator_code" in df.columns and "source_vintage" in df.columns:
        codes = df["indicator_code"].astype(str)
        rev = codes.map(lambda c: rule_for(c).revises)
        no_vint = int((rev & df["source_vintage"].isna()).sum())
        if no_vint:
            issues.append(f"{name}: 개정 소스인데 source_vintage 결측 {no_vint:,}행 "
                          f"— vintage 없이 백테스트하면 개정 후 값을 과거에 쓰게 됨")
    return issues


def _check_schemas() -> list[str]:
    """스키마 YAML에 5필드가 선언돼 있는지."""
    try:
        import yaml
    except ImportError:
        return ["[정보] pyyaml 미설치 — 스키마 검증 건너뜀"]
    out: list[str] = []
    for p in sorted(SCHEMA_DIR.glob("*.yaml")):
        try:
            d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            names = {c.get("name") for c in (d.get("columns") or [])}
        except Exception as e:
            out.append(f"{p.name}: 파싱 실패 {e}"); continue
        lack = [f for f in ASOF_FIELDS if f not in names]
        if lack:
            out.append(f"{p.name}: 스키마에 as-of 필드 누락 — {', '.join(lack)}")
    return out


def main() -> int:
    warn_only = "--warn" in sys.argv
    files = sorted(glob.glob(os.path.join(RAW_DIR, "**", "*.parquet"), recursive=True))
    files = [f for f in files
             if not any(os.path.basename(f).startswith(p) for p in EXEMPT_PREFIXES)]

    print(f"[as-of 검증] 대상 {len(files)}개 parquet · 기준일 {date.today()}")
    if EXEMPT_PREFIXES:
        print(f"  면제(이행기): {', '.join(sorted(EXEMPT_PREFIXES))}")

    schema_issues = _check_schemas()
    for s in schema_issues:
        print(f"  [스키마] {s}")

    if not files:
        print("[오류] 검증 대상 parquet 0건 — 수집 실패가 '통과'로 위장되지 않도록 차단")
        return 0 if warn_only else 1

    issues: list[str] = []
    passed = 0
    for f in files:
        try:
            df = pd.read_parquet(f)
        except Exception as e:
            issues.append(f"{os.path.basename(f)}: 읽기 실패 {type(e).__name__}: {e}")
            continue
        found = _check_frame(f, df)
        if found:
            issues.extend(found)
        else:
            passed += 1
            print(f"  ✅ {os.path.basename(f)} ({len(df):,}행)")

    hard = [i for i in issues if "미래" not in i]     # 미래 available_at은 경고
    for i in issues:
        print(f"  {'⚠️' if '미래' in i else '🚨'} {i}")

    print(f"\n[결과] 통과 {passed}/{len(files)} · 위반 {len(hard)}건 · 경고 {len(issues)-len(hard)}건")
    if hard or schema_issues:
        print("[차단] as-of 규칙 위반 — CLAUDE.md §1에 따라 모델 투입 불가")
        return 0 if warn_only else 1
    print("[통과] 모든 산출물이 as-of 계약을 충족합니다")
    return 0


if __name__ == "__main__":
    sys.exit(main())
