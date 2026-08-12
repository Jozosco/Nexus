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
from pathlib import Path
from xml.etree import ElementTree as ET

import httpx
import pandas as pd

# A-085: 한국 공공기관 호스트에서 러너 IPv6 경로 블랙홀 → IPv4 강제 트랜스포트
_KR_TRANSPORT = httpx.HTTPTransport(local_address="0.0.0.0", retries=2)

# A-094: 호출마다 Client를 새로 만들면 TCP·TLS 핸드셰이크가 매번 반복되고 소켓이 닫히지
# 않아 고갈된다. 커넥션 풀을 재사용하는 단일 클라이언트로 교체.
# 타임아웃 분리: connect 10s(연결 안 되는 호스트를 60초 기다려도 결과 동일) / read 30s.
_TIMEOUT = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)
_CLIENT = httpx.Client(transport=_KR_TRANSPORT, timeout=_TIMEOUT,
                       limits=httpx.Limits(max_connections=8, max_keepalive_connections=4))

MAX_RETRIES   = int(os.environ.get("CUSTOMS_MAX_RETRIES", "3"))
CALL_INTERVAL = float(os.environ.get("CUSTOMS_CALL_INTERVAL", "1.0"))   # 레이트리밋 회피 페이싱
# 잡 전체 예산(초) — 초과 시 수집분을 저장하고 정상 종료(6시간 강제 취소 방지)
TIME_BUDGET_S = float(os.environ.get("CUSTOMS_TIME_BUDGET_S", "10800"))  # 기본 3시간

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


def _request(params: dict, label: str, max_retries: int = MAX_RETRIES) -> list[dict] | None:
    """단일 HTTP 조회 — 공유 클라이언트·짧은 connect 타임아웃·지수 백오프.

    A-094: 실패 1건당 최악 254초(4×60s + 백오프)였던 구조가 6시간 초과의 직접 원인.
    connect 10s / read 30s로 분리해 지연 손실을 1/6로 줄인다(연결 안 되는 호스트를
    60초 기다려도 결과는 같음). 반환 None = 재시도 소진(호출부에서 실패 집계).
    """
    delay = 2
    for attempt in range(max_retries):
        try:
            r = _CLIENT.get(BASE_URL, params=params)
            r.raise_for_status()
            root = ET.fromstring(r.text)
            code = root.findtext(".//resultCode")
            if code not in ("00", None):
                print(f"    [경고] {label}: resultCode={code} {root.findtext('.//resultMsg')}")
                return []
            return _parse_items(root, params.get("hsSgn", ""), params.get("cntyCd", ""))
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(delay); delay *= 2; continue
            print(f"    [경고] {label} 수집 실패: {type(e).__name__}: {str(e)[:80]}")
            return None


def fetch_range(hs: str, cnty: str, start_year: int, end_year: int) -> list[dict]:
    """(HS·국가)의 전 기간을 **단일 호출**로 조회 — 실패 시에만 연도별 분할 폴백.

    A-094 근본 개선: API가 strtYymm~endYymm 다월 범위를 지원하므로 연도 루프가 불필요했다.
    1,530회 → 90회(17배 감소)로 호출량을 줄여 레이트리밋·타임아웃 노출을 함께 낮춘다.
    """
    key = os.environ.get("DATA_GO_KR_SERVICE_KEY", "").strip()
    if not key:
        raise RuntimeError("[오류] DATA_GO_KR_SERVICE_KEY 미등록 — GitHub Secrets 등록 필요")
    base = {"serviceKey": key, "hsSgn": hs, "cntyCd": cnty}
    rows = _request({**base, "strtYymm": f"{start_year}01", "endYymm": f"{end_year}12"},
                    f"{hs}/{cnty}/{start_year}~{end_year}")
    if rows:
        return rows
    if rows is None:   # 범위 조회 자체가 실패 → 연도 분할 폴백(응답 크기 제한 대비)
        print(f"    [정보] {hs}/{cnty}: 범위 조회 실패 — 연도별 분할 재시도")
        out: list[dict] = []
        for year in range(start_year, end_year + 1):
            r = _request({**base, "strtYymm": f"{year}01", "endYymm": f"{year}12"},
                         f"{hs}/{cnty}/{year}")
            if r:
                out.extend(r)
            time.sleep(CALL_INTERVAL)
        return out
    return []


def _write_gw_xlsx(rows: list[dict], out_path: Path) -> None:
    """업로드본과 동일 포맷으로 저장: 연도별 시트 × 월행 × 5지표열."""
    if not rows:
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for year, g in df.groupby("year"):
            # A-085: 동일 (연,월)이 복수 HS·응답행으로 중복 → set_index 후 reindex가
            #        "duplicate labels" ValueError. 월 단위로 먼저 합산해 유일화한다.
            g = g.groupby("month", as_index=True)[_COL_ORDER].sum(min_count=1)
            sheet = g.reindex(range(1, 13))[_COL_ORDER]
            sheet.index = [f"{m}월" for m in sheet.index]
            sheet.index.name = None
            sheet.to_excel(writer, sheet_name=f"{int(year)}년")


def run() -> None:
    """전 품목·국가 수집. 시간 예산 초과 시 수집분을 저장하고 정상 종료."""
    started = time.monotonic()
    all_records: list[dict] = []
    done = skipped = 0
    total_pairs = len(COMMODITIES) * len(COUNTRIES)

    for folder, hs in COMMODITIES:
        print(f"[C-03] {folder} (HS {hs}) 수집...")
        for cnty_code, cnty_name in COUNTRIES.items():
            elapsed = time.monotonic() - started
            if elapsed > TIME_BUDGET_S:
                skipped += 1
                continue
            rows = fetch_range(hs, cnty_code, START_YEAR, END_YEAR)
            done += 1
            time.sleep(CALL_INTERVAL)
            if not rows:
                print(f"  [정보] {folder}/{cnty_name}: 데이터 없음")
                continue
            out = GW_ROOT / folder / f"{cnty_name}.xlsx"
            _write_gw_xlsx(rows, out)
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
        print(f"\n[경고] 시간 예산({TIME_BUDGET_S/3600:.1f}h) 초과 — {skipped}/{total_pairs}쌍 미수집. "
              f"다음 실행에서 이어서 수집됨(수집분은 저장 완료)")
    if all_records:
        pd.DataFrame(all_records).to_parquet(PARQUET, index=False)
        print(f"\n[완료] → {PARQUET} ({len(all_records):,}행 · {done}/{total_pairs}쌍 · {mins:.1f}분)")
    else:
        print(f"\n[경고] 수집 데이터 없음 ({mins:.1f}분) — 키·네트워크 확인(Actions에서 실행 필요)")


if __name__ == "__main__":
    run()
