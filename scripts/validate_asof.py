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
from src.pipeline.asof import (ASOF_FIELDS, ASOF_REQUIRED,  # noqa: E402
                               leak_inversions, revision_status)

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
    # A-195: 전망 라벨 행(event_time > ingested_at)의 역전은 정상 — 공용 판정 사용
    inv_mask = leak_inversions(df)
    inverted = int(inv_mask.sum())
    if inverted:
        worst = (ev - av)[inv_mask].max()
        issues.append(f"{name}: available_at < event_time 역전 {inverted:,}행 (최대 {worst})")

    future = int((av > pd.Timestamp(date.today())).sum())
    if future:
        issues.append(f"{name}: available_at이 미래인 행 {future:,}건 — 현시점 모델 사용 불가(정상일 수 있음)")

    # ── 개정 이력 (D-034) ────────────────────────────────────────────────────
    # 구 검사는 `source_vintage`의 non-null만 봤다. 그런데 그 값이 **수집일 한 개**로
    # 일괄 스탬프돼 있었기 때문에(파일당 고유값 1개) 검사는 100% 통과하면서
    # 실제로는 아무것도 막지 못했다 — 게이트가 있는데 비어 있던 상태.
    # 이제 "vintage가 있는가"가 아니라 "**개정 전 값을 복원할 수 있는가**"를 묻는다.
    if "indicator_code" in df.columns:
        codes = df["indicator_code"].astype(str)
        contaminated = sorted({c for c in codes.unique() if revision_status(c) == "none"})
        if contaminated:
            issues.append(
                f"{name}: [경고] 개정 이력 없는 지표 {len(contaminated)}종 — "
                f"백테스트가 '당시 알 수 없던 확정치'를 사용합니다"
                f"(예: {', '.join(contaminated[:3])}). 제거가 아니라 민감도 검증 대상.")
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
    # A-175: G1 잡이 전체 아티팩트를 data/raw/로 병합 다운로드하면서 gold 산출물
    # (feature_mart — 와이드 포맷, as-of는 조립 시 이미 강제됨)이 원천 검사에 오탐 유입.
    # 원천 롱포맷 계약(indicator_code+value) 파일만 검증 대상으로 한다.
    _NON_SOURCE_PREFIXES = {"feature_mart"}
    files = [f for f in files
             if not any(os.path.basename(f).startswith(p)
                        for p in EXEMPT_PREFIXES | _NON_SOURCE_PREFIXES)]

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

    # 차단(hard) vs 경고 구분: 규칙 위반은 차단, 상태 보고는 경고.
    #   · 미래 available_at — 아직 못 쓸 뿐 데이터는 정상
    #   · 개정 이력 없음    — 사실 보고이며 지금 고칠 수단이 없다. 여기서 차단하면
    #     해결 경로 없이 전 작업이 멈춘다. 대신 **반드시 눈에 띄게** 남긴다.
    hard = [i for i in issues if "미래" not in i and "[경고]" not in i]
    for i in issues:
        soft = ("미래" in i) or ("[경고]" in i)
        print(f"  {'⚠️' if soft else '🚨'} {i}")

    print(f"\n[결과] 통과 {passed}/{len(files)} · 위반 {len(hard)}건 · 경고 {len(issues)-len(hard)}건")
    if hard or schema_issues:
        print("[차단] as-of 규칙 위반 — CLAUDE.md §1에 따라 모델 투입 불가")
        return 0 if warn_only else 1
    print("[통과] 모든 산출물이 as-of 계약을 충족합니다")
    return 0


if __name__ == "__main__":
    sys.exit(main())
