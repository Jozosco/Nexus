#!/usr/bin/env python3
"""Trading Economics API → 기존 수동 xlsx(연도 시트 × Month/Day/Open/High/Low/Close) 증분 갱신 (A-248).

배경: 수동 업로드본 26파일은 2026-07-01까지이고(≈46거래일 공백), 승인자가 API 구독을 연장했다.
기존 파일 형식·경로를 그대로 유지하며 **마지막 일자 이후 행만 append**한다(원본 시트 불변).

규약:
  - 심볼은 자기발견(A-150 — /markets/search → :COM/:IND 우선 A-159) + REGISTRY의 고정 심볼 우선.
  - historical 엔드포인트 409/403은 '플랜 미포함'으로 판정해 파일을 건드리지 않고 보고만 한다(A-140).
  - 새 연도 시트는 원본 헤더(Month|Day|Open|High|Low|Close)를 복제해 생성. 내림차순 시트는 상단 삽입.
  - 갱신 전 원본을 `.bak` 없이 임시 사본에 쓰고, ingest_te_xlsx 파서로 재판독 검증(행 수 증가·날짜 단조)
    을 통과할 때만 교체한다(A-109 .partial 가드와 동일 원리).
  - 샌드박스는 api.tradingeconomics.com 차단 — GitHub Actions(te_xlsx_update.yml)에서 실행한다.

사용: python scripts/update_te_xlsx_from_api.py [--dry-run] [--only "Soybeans,BDI"]
출력: xlsx 갱신 + reports/market/te_api_update_{date}.md
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

import httpx
import pandas as pd
from openpyxl import load_workbook

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

TE_ROOT = Path("data/raw/Trading Economics/Markets/Commodities")
REPORT_DIR = Path("reports/market")
_YEAR_SHEET_RE = re.compile(r"(\d{4})\s*년")
HEADER = ["Month", "Day", "Open", "High", "Low", "Close"]
THROTTLE = ("slow down", "throttle", "too many")

# 파일명 품목 → (검색어, 이름 키워드, 고정 심볼 후보). 고정 심볼은 자기발견 실패 시 폴백.
REGISTRY: dict[str, tuple[str, tuple[str, ...], tuple[str, ...]]] = {
    "Soybeans":      ("soybeans", ("soybean",), ("S 1:COM",)),
    "Corn":          ("corn", ("corn",), ("C 1:COM",)),
    "Wheat":         ("wheat", ("wheat",), ("W 1:COM",)),
    "Palm Oil":      ("palm oil", ("palm",), ("PLO:COM",)),
    "Canola":        ("canola", ("canola",), ("RS1:COM",)),
    "Rapeseed":      ("rapeseed", ("rapeseed",), ("RSD:COM",)),
    "Sunflower Oil": ("sunflower oil", ("sunflower",), ()),
    "Sugar":         ("sugar", ("sugar",), ("SB1:COM",)),
    "Brent Crude Oil": ("brent", ("brent",), ("CO1:COM",)),
    "WTI Crude Oil": ("crude oil", ("crude", "wti"), ("CL1:COM",)),
    "Coal":          ("coal", ("coal",), ("XAL1:COM",)),
    "Natural Gas":   ("natural gas", ("natural", "gas"), ("NG1:COM",)),
    "EU Natural Gas": ("ttf", ("ttf",), ("TTF:COM",)),
    "UK Natural Gas": ("uk gas", ("uk", "gas"), ("NBP:COM",)),
    "Gasoline":      ("gasoline", ("gasoline",), ("XB1:COM",)),
    "Heating Oil":   ("heating oil", ("heating",), ("HO1:COM",)),
    "Naphtha":       ("naphtha", ("naphtha",), ("NAPHTHA:COM",)),
    "Ethanol":       ("ethanol", ("ethanol",), ("ETHANOL:COM",)),
    "Urea":          ("urea", ("urea",), ("UREA:COM",)),
    "Di-ammonium":   ("dap", ("dap",), ("DAP:COM",)),
    "BDI":           ("baltic dry", ("baltic", "dry"), ("BDIY:IND",)),
    "CRB Index":     ("crb", ("crb",), ("CRY:IND",)),
    "GSCI":          ("gsci", ("gsci",), ("SPGSCI:IND",)),
    "EU Carbon Permits": ("carbon", ("carbon",), ("EECXM:IND",)),
    "Containerized Freight Index": ("containerized freight", ("container",), ("CFI:IND",)),
    "Drewry World Container Index": ("drewry", ("drewry",), ("WCI:IND",)),
}


def _commodity_of(path: Path) -> str:
    parts = path.stem.split("_")
    return parts[1].strip() if len(parts) >= 3 else path.stem


def _read_last_date(path: Path) -> tuple[date | None, bool]:
    """마지막 관측일과 시트 정렬 방향(내림차순 여부)."""
    wb = load_workbook(path, read_only=True, data_only=True)
    years = sorted((int(m.group(1)), n) for n in wb.sheetnames if (m := _YEAR_SHEET_RE.search(n)))
    if not years:
        return None, False
    ws = wb[years[-1][1]]
    rows = [r for r in ws.iter_rows(min_row=2, values_only=True) if r and r[0] is not None and r[1] is not None]
    if not rows:
        return date(years[-1][0], 1, 1) - timedelta(days=1), False
    first, last = rows[0], rows[-1]
    desc = (int(first[0]), int(first[1])) > (int(last[0]), int(last[1]))
    m, d = (first if desc else last)[:2]
    return date(years[-1][0], int(m), int(d)), desc


def _te_get(url: str, params: dict, timeout: int = 30) -> httpx.Response:
    return httpx.get(url, params=params, timeout=timeout)


def discover_symbols(te_key: str, commodity: str) -> list[str]:
    term, kws, fixed = REGISTRY.get(commodity, (commodity.lower(), (commodity.lower(),), ()))
    found: list[str] = []
    for url in (f"https://api.tradingeconomics.com/markets/search/{quote(term)}",
                "https://api.tradingeconomics.com/markets/commodities"):
        try:
            r = _te_get(url, {"c": te_key})
            if r.status_code != 200:
                continue
            data = r.json()
            for item in data if isinstance(data, list) else []:
                name = str(item.get("Name") or item.get("name") or "")
                if all(k.lower() in name.lower() for k in kws):
                    sym = item.get("Symbol") or item.get("symbol")
                    if sym and str(sym) not in found:
                        found.append(str(sym))
            if found:
                break
        except Exception as e:  # noqa: BLE001
            print(f"[정보] TE 심볼 검색 실패({commodity}): {e}")
    found.sort(key=lambda x: (0 if x.endswith(":COM") else 1 if x.endswith(":IND") else 2))   # A-159
    return list(dict.fromkeys((*fixed, *found)))


def fetch_history(te_key: str, symbols: list[str], d1: date, d2: date) -> tuple[pd.DataFrame, str]:
    """→ (DataFrame[date,open,high,low,close], 상태) 상태 ∈ ok | plan | empty | error."""
    last_status = "empty"
    for sym in symbols:
        r = _te_get(f"https://api.tradingeconomics.com/markets/historical/{quote(sym, safe=':')}",
                    {"c": te_key, "d1": d1.isoformat(), "d2": d2.isoformat(), "f": "json"})
        if r.status_code in (403, 409) or any(t in r.text.lower() for t in THROTTLE):
            print(f"[정보] TE historical {r.status_code} ({sym}) — 플랜 미포함/스로틀 추정")
            return pd.DataFrame(), "plan"
        if r.status_code != 200:
            print(f"[정보] TE historical HTTP {r.status_code} ({sym}) — 다음 심볼")
            last_status = "error"
            continue
        data = r.json()
        if not isinstance(data, list) or not data:
            continue
        raw = pd.DataFrame(data)
        dcol = next((c for c in ("Date", "DateTime", "date") if c in raw.columns), None)
        ccol = next((c for c in ("Close", "Last", "close") if c in raw.columns), None)
        if not dcol or not ccol:
            continue
        out = pd.DataFrame({
            "date": pd.to_datetime(raw[dcol], errors="coerce").dt.normalize(),
            "open": pd.to_numeric(raw.get("Open"), errors="coerce"),
            "high": pd.to_numeric(raw.get("High"), errors="coerce"),
            "low": pd.to_numeric(raw.get("Low"), errors="coerce"),
            "close": pd.to_numeric(raw[ccol], errors="coerce"),
        }).dropna(subset=["date", "close"])
        out = out[(out["date"].dt.date > d1) & (out["date"].dt.date <= d2)]   # 요청 창 밖·미래 행 차단(A-246)
        if not out.empty:
            print(f"[완료] TE historical {len(out)}행 ({sym}, {d1}~{d2})")
            return out.sort_values("date").drop_duplicates("date"), "ok"
    return pd.DataFrame(), last_status


def append_rows(path: Path, rows: pd.DataFrame, desc: bool) -> int:
    """rows(date/open/high/low/close)를 연도 시트에 append. 반환: 추가 행 수."""
    wb = load_workbook(path)
    added = 0
    for year, grp in rows.groupby(rows["date"].dt.year):
        name = f"{year}년"
        if name not in wb.sheetnames:
            ws = wb.create_sheet(name)
            ws.append(HEADER)
        ws = wb[name]
        recs = [[int(d.month), int(d.day), o, h, l, c] for d, o, h, l, c in
                grp[["date", "open", "high", "low", "close"]].itertuples(index=False)]
        recs = [[m, dd] + [None if pd.isna(v) else float(v) for v in vals] for m, dd, *vals in recs]
        if desc:   # 내림차순 시트: 오름차순으로 순회하며 매번 2행에 삽입 → 최신이 최상단
            for rec in recs:
                ws.insert_rows(2)
                for j, v in enumerate(rec, start=1):
                    ws.cell(2, j, v)
        else:
            for rec in recs:
                ws.append(rec)
        added += len(recs)
    wb.save(path)
    return added


def _validate(orig: Path, cand: Path) -> tuple[bool, str]:
    """재판독 검증 — 행 수 증가·마지막 일자 진전·시트 수 유지 이상."""
    a, _ = _read_last_date(orig); b, _ = _read_last_date(cand)
    wa, wb_ = load_workbook(orig, read_only=True), load_workbook(cand, read_only=True)
    if len(wb_.sheetnames) < len(wa.sheetnames):
        return False, "시트 수 감소"
    if a and b and b < a:
        return False, f"마지막 일자 역행 {a}→{b}"
    return True, f"{a}→{b}"


def run(dry_run: bool = False, only: set[str] | None = None) -> list[dict]:
    te_key = os.environ.get("TRADING_ECONOMICS_API_KEY", "").strip()
    if not te_key and not dry_run:
        raise SystemExit("[오류] TRADING_ECONOMICS_API_KEY 미설정 — GitHub Secrets 확인")
    today = date.today()
    results: list[dict] = []
    for path in sorted(TE_ROOT.rglob("*.xlsx")):
        commodity = _commodity_of(path)
        if only and commodity not in only:
            continue
        last, desc = _read_last_date(path)
        rec = {"file": path.name, "commodity": commodity, "last_before": last, "status": "", "added": 0, "symbol": ""}
        if last is None:
            rec["status"] = "시트 없음"; results.append(rec); continue
        if last >= today - timedelta(days=1):
            rec["status"] = "최신"; results.append(rec); continue
        if dry_run:
            rec["status"] = f"dry-run(갱신 필요 {last}~{today})"; results.append(rec); continue
        symbols = discover_symbols(te_key, commodity)
        rec["symbol"] = ",".join(symbols[:3])
        hist, status = fetch_history(te_key, symbols, last, today)
        if status != "ok":
            rec["status"] = {"plan": "플랜 미포함(409/403)", "empty": "응답 0행", "error": "HTTP 오류"}[status]
            results.append(rec); continue
        with tempfile.TemporaryDirectory() as td:
            cand = Path(td) / path.name
            shutil.copy(path, cand)
            n = append_rows(cand, hist, desc)
            ok, msg = _validate(path, cand)
            if not ok:
                rec["status"] = f"검증 실패({msg}) — 원본 유지"; results.append(rec); continue
            shutil.copy(cand, path)
        rec["status"] = f"갱신({msg})"; rec["added"] = n
        results.append(rec)
        print(f"[완료] {path.name}: +{n}행 ({msg})")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    rp = REPORT_DIR / f"te_api_update_{today.isoformat()}.md"
    lines = [f"# Trading Economics API 갱신 결과 — {today}", "",
             "| 파일 | 품목 | 갱신 전 마지막 일자 | 심볼 | 상태 | 추가 행 |", "|---|---|---|---|---|---|"]
    lines += [f"| {r['file']} | {r['commodity']} | {r['last_before']} | {r['symbol']} | {r['status']} | {r['added']} |" for r in results]
    plan = [r for r in results if r["status"].startswith("플랜")]
    if plan:
        lines += ["", f"> ⚠️ {len(plan)}건이 '플랜 미포함(409/403)' — 연장 플랜에 Markets Historical이 포함되지 않았다면 "
                      "①플랜 상향 또는 ②일별 스냅샷 append(te_connector)로 대체해야 함(결정 요청)."]
    rp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[완료] 보고서 → {rp}")
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    run(dry_run=a.dry_run, only=set(x.strip() for x in a.only.split(",") if x.strip()) or None)
