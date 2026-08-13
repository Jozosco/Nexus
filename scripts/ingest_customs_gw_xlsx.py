#!/usr/bin/env python3
"""
관세청 품목별 국가별 수출입실적(GW) — 대체·보완재 확장 수집 (WBS 1.1.48 · A-069/A-073)

목적(조정자 Req): 대두유 외 **대체재·보완재**와 **추가 원산지**의 한국 수출입 실적을 관세청 API로
수집해, 기존 업로드본과 **완전히 동일한 형식**(연도별 시트 × 월별 행 × 5개 지표 열)으로 저장.

저장 규칙(조정자 지정):
  data/raw/관세청/Import Export Performance by Commodity and Country(GW)/
      {품목명 (HS코드)}/{국가}.xlsx
  예) 'Palm Oil (1511)/China.xlsx' · 'Soybean (1201.90)/Brazil.xlsx'
  시트: '{YYYY}년' · 행: '{M}월' · 열: 무역수지(달러)·수출액(달러)·수출량(kg)·수입액(달러)·수입량(kg)

엔드포인트: http://apis.data.go.kr/1220000/nitemtrade/getNitemtradeList  (REST, XML)
인증: 환경변수 DATA_GO_KR_SERVICE_KEY  (⚠️ 하드코딩 금지 — CLAUDE.md §2)

⚠️ 실행 환경: apis.data.go.kr 은 개발 샌드박스 프록시에서 차단(A-069) → **GitHub Actions 전용**.

의존성: httpx · pandas · openpyxl
"""
from __future__ import annotations

import os
import time
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import NamedTuple
from xml.etree import ElementTree as ET

import httpx
import pandas as pd

# as-of 헬퍼 로드 — 스크립트 직접 실행 시 저장소 루트를 경로에 추가
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from src.pipeline.asof import attach_asof  # noqa: E402

# A-085: 한국 공공기관 호스트에서 러너 IPv6 경로 블랙홀 → IPv4 강제 트랜스포트
_KR_TRANSPORT = httpx.HTTPTransport(local_address="0.0.0.0", retries=2)

# A-094: 호출마다 Client를 새로 만들면 TCP·TLS 핸드셰이크가 매번 반복되고 소켓이 닫히지
# 않아 고갈된다. 커넥션 풀을 재사용하는 단일 클라이언트로 교체.
# 타임아웃 분리: connect 10s(연결 안 되는 호스트를 60초 기다려도 결과 동일) / read 30s.
_TIMEOUT = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)
_CLIENT = httpx.Client(transport=_KR_TRANSPORT, timeout=_TIMEOUT,
                       limits=httpx.Limits(max_connections=12, max_keepalive_connections=8))

MAX_RETRIES   = int(os.environ.get("CUSTOMS_MAX_RETRIES", "3"))
CALL_INTERVAL = float(os.environ.get("CUSTOMS_CALL_INTERVAL", "0.5"))   # (HS·국가) 쌍 간 페이싱
# A-101: 다년 범위 불가 확정 → 연 단위 1,530회를 **동시 실행**으로 흡수한다.
#        레이트리밋 유발을 피하려고 과도하게 올리지 않는다(기본 5).
MAX_WORKERS   = int(os.environ.get("CUSTOMS_MAX_WORKERS", "5"))
# 잡 전체 예산(초) — 초과 시 수집분을 저장하고 정상 종료(6시간 강제 취소 방지)
TIME_BUDGET_S = float(os.environ.get("CUSTOMS_TIME_BUDGET_S", "10800"))  # 기본 3시간

# 실패 집계(A-109 F1) — 하나라도 있으면 종료코드 1로 파이프라인을 차단한다
_FAILURES: list[str] = []
# 프로브로 확정되는 조회 폭(개월). 리스트로 둬 스레드에서 읽기만 한다.
_WINDOW_MONTHS: list[int] = [12]

BASE_URL = "http://apis.data.go.kr/1220000/nitemtrade/getNitemtradeList"
GW_ROOT  = Path("data/raw/관세청/Import Export Performance by Commodity and Country(GW)")
PARQUET  = Path("data/raw/customs_gw_historical.parquet")

START_YEAR = int(os.environ.get("HISTORICAL_START_YEAR", "2010"))
END_YEAR   = int(os.environ.get("HISTORICAL_END_YEAR", "2026"))

# 품목 → (폴더명, HS코드) — session37 §4 확정(대체재·보완재)
COMMODITIES: list[tuple[str, str]] = [
    ("Palm Oil (1511)",            "1511"),
    ("Sunflower Oil (1512.11)",    "151211"),
    ("Sunflower Oil (1512.19)",    "151219"),
    ("Rapeseed Oil (1514.11)",     "151411"),
    ("Rapeseed Oil (1514.19)",     "151419"),
    ("Palm Kernel Oil (1513.21)",  "151321"),
    ("Soybean (1201.90)",          "120190"),
    ("Soybean Meal (2304)",        "2304"),
    ("Biodiesel (3826)",           "3826"),
]

# 국가코드 → 파일명(기존 업로드본 표기 준수: U.S.A / Argentina …)
COUNTRIES: dict[str, str] = {
    "US": "U.S.A", "BR": "Brazil", "AR": "Argentina", "CN": "China",
    # session37 §4.1 확대 원산지
    "MY": "Malaysia", "ID": "Indonesia", "PY": "Paraguay",
    "VN": "Vietnam", "NL": "Netherlands", "ES": "Spain",
}

_COL_ORDER = ["무역수지(달러)", "수출액(달러)", "수출량(kg)", "수입액(달러)", "수입량(kg)"]


def _parse_items(root: ET.Element, hs: str, cnty: str) -> list[dict]:
    """응답 XML → 월별 레코드. 연 총계 행(`year`에 '총계' 또는 월 구분 없음)은 제외."""
    rows: list[dict] = []
    for it in root.findall(".//item"):
        yr = (it.findtext("year") or "").strip()
        if "총계" in yr or "." not in yr:
            continue
        try:
            y_str, m_str = yr.split(".")[:2]
            year, month = int(y_str), int(m_str)
        except ValueError:
            continue
        if not (1 <= month <= 12):
            continue
        rows.append({
            "year": year, "month": month,
            "무역수지(달러)": pd.to_numeric(it.findtext("balPayments"), errors="coerce"),
            "수출액(달러)":  pd.to_numeric(it.findtext("expDlr"), errors="coerce"),
            "수출량(kg)":    pd.to_numeric(it.findtext("expWgt"), errors="coerce"),
            "수입액(달러)":  pd.to_numeric(it.findtext("impDlr"), errors="coerce"),
            "수입량(kg)":    pd.to_numeric(it.findtext("impWgt"), errors="coerce"),
        })
    return rows


class Outcome(NamedTuple):
    """조회 결과 3상태 — A-109.

    이전 구조는 `[]`가 "데이터 없음"과 "요청 거부"를 동시에 뜻해, 서비스키 만료 같은
    전면 실패가 `[정보] 데이터 없음` 로그와 exit 0으로 위장됐다(세션 45·46 반복 증상).
    성공/무데이터/실패를 **타입 수준에서 분리**한다.
    """
    rows: list[dict]
    status: str          # "ok" | "empty" | "rejected" | "error"
    detail: str = ""

    @property
    def failed(self) -> bool:
        return self.status in ("rejected", "error")


def _request(params: dict, label: str, max_retries: int = MAX_RETRIES) -> Outcome:
    """단일 HTTP 조회 — 공유 클라이언트·짧은 connect 타임아웃·지수 백오프."""
    delay = 2
    for attempt in range(max_retries):
        try:
            r = _CLIENT.get(BASE_URL, params=params)
            r.raise_for_status()
            root = ET.fromstring(r.text)
            code = root.findtext(".//resultCode")
            msg = root.findtext(".//resultMsg") or ""
            if code not in ("00", None):
                # 업무 오류는 재시도해도 동일 — 즉시 rejected로 확정해 상위가 구분하게 한다
                print(f"    [경고] {label}: resultCode={code} {msg}")
                return Outcome([], "rejected", f"{code}: {msg}")
            rows = _parse_items(root, params.get("hsSgn", ""), params.get("cntyCd", ""))
            return Outcome(rows, "ok" if rows else "empty")
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(delay); delay *= 2; continue
            print(f"    [경고] {label} 수집 실패: {type(e).__name__}: {str(e)[:80]}")
            return Outcome([], "error", f"{type(e).__name__}: {e}")
    return Outcome([], "error", "재시도 소진")


def _period_windows(year: int, months: int) -> list[tuple[str, str]]:
    """연도를 `months` 폭으로 분할한 (strtYymm, endYymm) 목록."""
    out = []
    for m0 in range(1, 13, months):
        m1 = min(m0 + months - 1, 12)
        out.append((f"{year}{m0:02d}", f"{year}{m1:02d}"))
    return out


def _probe_window_months(base: dict, year: int) -> int:
    """A-109(F2): '1년 이내'의 경계 해석이 불확실하다(12개월 inclusive가 거부될 수 있음).

    첫 조합 1건으로 12 → 6 → 3개월 폭을 시험해 **통과하는 최대 폭**을 확정하고
    전체에 적용한다. 경계가 어긋나 1,530회를 통째로 낭비하는 사태를 막는다.
    """
    for months in (12, 6, 3):
        s, e = _period_windows(year, months)[0]
        res = _request({**base, "strtYymm": s, "endYymm": e}, f"프로브 {s}~{e}")
        if not res.failed:
            print(f"[프로브] 조회 폭 {months}개월 확정 (요청당 {12 // months}회/연)")
            return months
        if "1년" not in res.detail and res.status == "error":
            break      # 네트워크 오류면 폭 문제 아님 — 기본값으로 진행
    print("[경고] 프로브 실패 — 기본 12개월 폭으로 진행(실패 시 로그 확인)")
    return 12


def fetch_range(hs: str, cnty: str, start_year: int, end_year: int) -> list[dict]:
    """(HS·국가)의 전 기간을 **연 단위로 병렬 조회**.

    A-101: 다년 범위 호출은 API가 거부한다 —
      `resultCode=99 시작과 종료의 조회기간은 1년이내 기간만 가능합니다`.
    A-094의 "1,530→90회" 최적화는 **불가능**했음이 실측으로 확정됐다. 연 단위로 되돌리되,
    6시간 초과를 막기 위해 **동시성**으로 벽시계 시간을 줄인다(순차 1,530회 → 동시 N).
    조회 기간을 1년 이내로 유지하기 위해 각 요청은 `{YYYY}01~{YYYY}12`(=12개월)로 고정한다.
    """
    key = os.environ.get("DATA_GO_KR_SERVICE_KEY", "").strip()
    if not key:
        raise RuntimeError("[오류] DATA_GO_KR_SERVICE_KEY 미등록 — GitHub Secrets 등록 필요")
    base = {"serviceKey": key, "hsSgn": hs, "cntyCd": cnty}
    years = list(range(start_year, end_year + 1))
    months = _WINDOW_MONTHS[0]

    def _one(year: int) -> tuple[list[dict], list[str]]:
        rows: list[dict] = []
        fails: list[str] = []
        for s, e in _period_windows(year, months):
            res = _request({**base, "strtYymm": s, "endYymm": e}, f"{hs}/{cnty}/{s}~{e}")
            if res.failed:
                fails.append(f"{s}~{e}({res.detail[:40]})")
            rows.extend(res.rows)
        return rows, fails

    out: list[dict] = []
    failed: list[str] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for rows, fails in pool.map(_one, years):
            out.extend(rows)
            failed.extend(fails)
    if failed:
        # A-109(F1): 실패를 삼키지 않고 상위로 올린다
        _FAILURES.append(f"{hs}/{cnty}: {len(failed)}구간 실패 — {failed[0]}")
    return out


def _write_gw_xlsx(rows: list[dict], out_path: Path,
                   expected_years: int | None = None) -> None:
    """업로드본과 동일 포맷으로 저장: 연도별 시트 × 월행 × 5지표열.

    A-109(F10): 전량 덮어쓰기이므로 **부분 수집이 직전의 완전한 산출물을 파괴**할 수 있다
    (17시트 파일이 3시트로 축소되어도 경고가 없었다). 기대 연도 수에 못 미치면
    기존 파일을 `.partial.xlsx`로 분리 저장해 원본을 보존한다.
    """
    if not rows:
        return
    df = pd.DataFrame(rows)
    got_years = df["year"].nunique()
    if expected_years and got_years < expected_years and out_path.exists():
        out_path = out_path.with_suffix(".partial.xlsx")
        print(f"    [보호] 연도 {got_years}/{expected_years}만 수집 — 기존 파일 보존, "
              f"{out_path.name}에 저장")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for year, g in df.groupby("year"):
            # A-085: 동일 (연,월)이 복수 HS·응답행으로 중복 → set_index 후 reindex가
            #        "duplicate labels" ValueError. 월 단위로 먼저 합산해 유일화한다.
            g = g.groupby("month", as_index=True)[_COL_ORDER].sum(min_count=1)
            sheet = g.reindex(range(1, 13))[_COL_ORDER]
            sheet.index = [f"{m}월" for m in sheet.index]
            sheet.index.name = None
            sheet.to_excel(writer, sheet_name=f"{int(year)}년")


def run() -> int:
    """전 품목·국가 수집. 반환값 = 프로세스 종료코드(0 정상 / 1 실패 존재)."""
    started = time.monotonic()
    all_records: list[dict] = []
    done = skipped = empty = 0
    total_pairs = len(COMMODITIES) * len(COUNTRIES)
    expected_years = END_YEAR - START_YEAR + 1

    # A-109(F2): 조회 폭을 선행 프로브로 확정 — 경계 오판으로 1,530회를 낭비하지 않는다
    key = os.environ.get("DATA_GO_KR_SERVICE_KEY", "").strip()
    if not key:
        print("[오류] DATA_GO_KR_SERVICE_KEY 미등록 — GitHub Secrets 등록 필요")
        return 1
    probe_base = {"serviceKey": key, "hsSgn": COMMODITIES[0][1],
                  "cntyCd": next(iter(COUNTRIES))}
    _WINDOW_MONTHS[0] = _probe_window_months(probe_base, START_YEAR)

    for folder, hs in COMMODITIES:
        print(f"[C-03] {folder} (HS {hs}) 수집...")
        for cnty_code, cnty_name in COUNTRIES.items():
            if time.monotonic() - started > TIME_BUDGET_S:
                skipped += 1
                continue
            rows = fetch_range(hs, cnty_code, START_YEAR, END_YEAR)
            done += 1
            time.sleep(CALL_INTERVAL)
            if not rows:
                # A-109(F1): '무데이터'와 '실패'는 _FAILURES로 구분된다 — 여기서는 사실만 기록
                empty += 1
                print(f"  [정보] {folder}/{cnty_name}: 반환 행 없음")
                continue
            out = GW_ROOT / folder / f"{cnty_name}.xlsx"
            _write_gw_xlsx(rows, out, expected_years=expected_years)
            print(f"  [xlsx] {folder}/{cnty_name}.xlsx ({len(rows)}개월)")
            for r in rows:
                all_records.append({**r, "commodity": folder, "hs_code": hs,
                                    "country": cnty_name,
                                    "price_date": pd.Timestamp(year=r["year"],
                                                               month=r["month"], day=1),
                                    "source_name": "KoreaCustoms_GW",
                                    "ingested_at": pd.Timestamp.now("UTC")})

    mins = (time.monotonic() - started) / 60
    if skipped:
        # A-109(F10): 재개 상태를 저장하지 않으므로 "이어서 수집"은 사실이 아니다.
        # 매 실행이 같은 순서로 돌아 같은 지점에서 소진된다 — 정확히 알린다.
        print(f"\n[경고] 시간 예산({TIME_BUDGET_S/3600:.1f}h) 초과 — {skipped}/{total_pairs}쌍 미수집. "
              f"⚠️ 재개 기능 없음: 다음 실행도 동일 순서로 시작하므로 뒤쪽 품목은 계속 누락된다. "
              f"CUSTOMS_TIME_BUDGET_S 상향 또는 COMMODITIES 분할 실행 필요")

    if all_records:
        # D-023: 저장 직전 as-of 5필드 부여 — 규칙은 src/pipeline/asof.py 단일 관리
        # 관세청은 확정치 개정이 있으므로 vintage(수집일)를 명시 부여한다
        _df = attach_asof(pd.DataFrame(all_records), source="CUSTOMS_")
        _df.to_parquet(PARQUET, index=False)
        print(f"\n[완료] → {PARQUET} ({len(all_records):,}행 · 수집 {done}/{total_pairs}쌍 · "
              f"무데이터 {empty} · {mins:.1f}분)")
    else:
        print(f"\n[경고] 수집 데이터 없음 ({mins:.1f}분)")

    # ── A-109(F1) 실패 집계 → 종료코드로 파이프라인 차단 ──────────────────────
    if _FAILURES:
        print(f"\n[오류] 요청 실패 {len(_FAILURES)}건 — 아래는 최대 10건:")
        for f in _FAILURES[:10]:
            print(f"    · {f}")
        print("  ⚠️ 실패가 '데이터 없음'으로 위장되지 않도록 종료코드 1로 차단합니다.")
        return 1
    if not all_records:
        print("  ⚠️ 성공 요청이 하나도 없음 — 키·네트워크 확인 필요(종료코드 1)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run())
