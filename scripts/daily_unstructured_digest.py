#!/usr/bin/env python3
"""
일별 비정형 신호 다이제스트 — Perplexity 수집분 요약 (A-163 · 조정자 지시 8/14)

지시: "Perplexity로 수집하는 비정형 데이터는 일 단위 갱신이 가능하므로
      매일 확인·수집·요약할 것."

동작: 당일 수집된 실시간 프록시 지표(지정학·해협·정책뉴스·운임·기상특보)를
      data/raw parquet에서 모아 하나의 한국어 다이제스트로 렌더링한다.
      수치와 함께 note(Perplexity 근거 발췌)를 보존해 '요약'이 되게 한다.

출력: reports/market/daily_unstructured_digest_{YYYY-MM-DD}.md
      (+ stdout — 워크플로우가 GITHUB_STEP_SUMMARY로 노출)
"""
from __future__ import annotations

import glob
import os
from datetime import date
from pathlib import Path

import pandas as pd

RAW = os.environ.get("NEXUS_DATA_ROOT", "data/raw")
OUT = Path("reports/market")
# A-181: 일별 신호의 변수별 영구 아카이브 (조정자 지시 8/16 — 아티팩트 7~30일 한계 해소).
#   커밋 저장은 unstructured_analysis.yml 인덱스 CSV 선례(A-090)를 따른다.
ARCHIVE = Path("data/processed/unstructured_daily_signals.csv")

# 일 단위 갱신되는 비정형·프록시 지표 (커넥터별)
DAILY_UNSTRUCTURED = {
    "지정학 위험":   ["GPR_REALTIME", "GPR", "HORMUZ_THREAT_LEVEL", "HORMUZ_AWRP_MULTIPLIER"],
    "정책 뉴스":     ["ARG_EXPORT_TAX_NEWS", "INDIA_DUTY_NEWS", "BIODIESEL_MANDATE_NEWS",
                     "WASDE_CONSENSUS_SCORE"],
    "지정학 이벤트": ["SUEZ_RED_SEA_RISK", "UKRAINE_GRAIN_CORRIDOR", "US_CHINA_TARIFF_STATUS",
                     "BRAZIL_HARVEST_PROGRESS"],
    "해협 탱커":     ["AIS_HORMUZ_TANKERS", "AIS_MALACCA_TANKERS", "AIS_PANAMA_TANKERS",
                     "SBO_STRAIT_RISK_COMPOSITE"],
    "GeoIntel 복합": ["GEOINTEL_RISK_COMPOSITE", "SEISMIC_RISK", "GDELT_EVENT_SCORE"],
    "운임(실시간)":  ["BCAA", "BCTI_PROXY"],
    "기상 특보":     ["WEATHER_ALERT_COUNT", "WEATHER_ANOMALY_SCORE"],
    "전문 매체":     ["RSS_FARMDOC_DAILY", "RSS_WORLD_GRAIN"],
}

# ── 전문 매체 RSS (조정자 지시 8/25 · 확장 8/25 2차 — 일별·거시 시황 소스) ──────
# egress_allowlist 등재 호스트만. RSS 실패는 다이제스트를 죽이지 않는다(비치명).
# URL 후보는 폴백 순서 — 실제 피드 경로는 Actions 런 로그로 판정(샌드박스 열람 차단).
# ⚠️ IGC(igc.int)는 RSS 부재 추정 — 월별 Grain Market Report는 수동/추후 경로(미편입).
RSS_SOURCES = {
    # farmdoc daily(일리노이대) — 작황·바이오연료·무역 실증 분석 (A-201 farmdoc 논문 계열)
    "RSS_FARMDOC_DAILY": ["https://farmdocdaily.illinois.edu/feed"],
    # World Grain — 곡물·유지 산업 전문지 (한국 압착·생산 기사 다수 — 부록 3차)
    "RSS_WORLD_GRAIN": ["https://www.world-grain.com/rss/articles",
                        "https://www.world-grain.com/rss"],
    # OFI(Oils & Fats International) — 유지 산업 전문지 (한국 압착·중국 순수출 기사)
    "RSS_OFI_MAGAZINE": ["https://www.ofimagazine.com/news/rss",
                         "https://www.ofimagazine.com/rss"],
    # GRAIN — 농업·식량 체계 NGO (토지·정책 신호)
    "RSS_GRAIN_ORG": ["https://grain.org/en/rss",
                      "https://grain.org/system/articles.rss"],
    # ASA(미 대두협회) — 미 대두 정책·업계 신호 (부록 2차 #6 Iowa Soy 계열)
    "RSS_SOYGROWERS": ["https://soygrowers.com/feed/",
                       "https://soygrowers.com/category/news-releases/feed/"],
    # 크라이미트폴 — 한국 기후·에너지 매체 (SAF·바이오연료 국문 — 부록 8차 원문 소스)
    "RSS_CLIMATEPOL": ["https://www.climatepol.com/rss/allArticle.xml",
                       "https://www.climatepol.com/rss/S1N2.xml"],
    # ── 2026-08-28 조정자 추가 지시 4계열 (egress v2.5) — WordPress /feed 관행,
    #    실피드 URL은 샌드박스 차단으로 미검증: 첫 Actions 런 로그로 확정(비치명 설계) ──
    # AgMarket.Net — 조간·마감 시장 분석
    "RSS_AGMARKET": ["https://www.agmarket.net/feed/",
                     "https://www.agmarket.net/category/daily/pm-report/feed/"],
    # Grain Central(호주) — 무역·작황·기상
    "RSS_GRAINCENTRAL": ["https://www.graincentral.com/feed/",
                         "https://www.graincentral.com/trade/feed/"],
    # Total Farm Marketing — TFM 360° 곡물 리포트 (시세 페이지는 yfinance·TE로 기수집)
    "RSS_TFM": ["https://www.totalfarmmarketing.com/feed/",
                "https://www.totalfarmmarketing.com/tfm-reports/tfm-360-grain/feed/"],
    # UkrAgroConsult — 흑해 유지작물·곡물·물류 (해바라기유 축 — D-049 정합)
    "RSS_UKRAGRO": ["https://ukragroconsult.com/en/feed/",
                    "https://ukragroconsult.com/feed/"],
    # S&P Global Commodity Insights: 공개 RSS 부재 추정 — 자동 수집 미등재(실패 소음 방지).
    # 부록 인사이트는 Perplexity 프록시 경유 요약으로 커버 (egress에는 열람용 등재)
}
# SBO·유지 관련 기사만 통과 (제목+요약 매칭 — 영문 소문자·국문 원형)
_RSS_KEYWORDS = (
    "soybean", "soy oil", "soyoil", "soybean oil", "vegetable oil", "oilseed",
    "palm oil", "canola", "rapeseed", "sunflower", "crush", "biodiesel",
    "renewable diesel", "wasde", "export tax", "tariff", "south korea",
    # 국문 (climatepol 등 한국 매체용)
    "대두", "대두유", "팜유", "식용유", "유지", "바이오디젤", "바이오연료",
    "항공유", "saf", "곡물", "수출세", "관세",
)


def _fetch_specialist_media() -> list[dict]:
    """전문 매체 RSS → 일자·소스별 1행(값=관련 기사 수, note=제목+링크 — S-5 출처 보존).

    파싱은 stdlib XML만 사용(신규 의존성 없음 — httpx는 커넥터 공통 의존).
    항목이 임계 대상이 아니므로 온톨로지 후보 큐에는 넣지 않는다 — 태그 매칭·시계열화는
    build_unstructured_timeseries 편입 시(30일+ 축적 후) 판단.
    """
    try:
        import httpx
    except ImportError:
        print("[경고] httpx 미설치 — 전문 매체 RSS 수집 건너뜀")
        return []
    import xml.etree.ElementTree as ET
    from email.utils import parsedate_to_datetime

    cutoff = pd.Timestamp(date.today()) - pd.Timedelta(days=2)
    rows: list[dict] = []
    for indicator, urls in RSS_SOURCES.items():
        items: list = []
        for url in urls:
            try:
                r = httpx.get(url, timeout=30, follow_redirects=True,
                              headers={"User-Agent": "Mozilla/5.0 (Nexus data pipeline)"})
                r.raise_for_status()
                items = ET.fromstring(r.content).findall(".//item")
                if items:
                    break
            except Exception as e:   # 네트워크·파싱 어느 쪽이든 비치명
                print(f"[경고] RSS 수집 실패({url}): {type(e).__name__} — 다음 후보로")
        by_date: dict[str, list[str]] = {}
        for it in items:
            title = (it.findtext("title") or "").strip()
            desc = it.findtext("description") or ""
            link = (it.findtext("link") or "").strip()
            pub = it.findtext("pubDate")
            try:
                pub_d = pd.Timestamp(parsedate_to_datetime(pub).date()) if pub \
                    else pd.Timestamp(date.today())
            except Exception:
                pub_d = pd.Timestamp(date.today())
            if pub_d < cutoff:
                continue
            if not any(k in f"{title} {desc}".lower() for k in _RSS_KEYWORDS):
                continue
            by_date.setdefault(str(pub_d.date()), []).append(f"{title} ({link})")
        for d, notes in sorted(by_date.items()):
            rows.append({"indicator": indicator, "date": d, "value": len(notes),
                         "note": " ⋅ ".join(notes)[:500],
                         "source": indicator.lower()})
    if rows:
        print(f"[전문 매체] RSS 신호 {len(rows)}행 수집 "
              f"({', '.join(sorted({r['indicator'] for r in rows}))})")
    return rows


def main() -> int:
    today = pd.Timestamp(date.today())
    rows: list[dict] = []
    for f in sorted(glob.glob(os.path.join(RAW, "**", "*.parquet"), recursive=True)):
        try:
            df = pd.read_parquet(f)
        except Exception:
            continue
        if "indicator_code" not in df.columns or "price_date" not in df.columns:
            continue
        d = pd.to_datetime(df["price_date"], errors="coerce")
        recent = df[(d >= today - pd.Timedelta(days=2))]      # 주말·시차 여유 2일
        if recent.empty:
            continue
        for _, r in recent.iterrows():
            rows.append({
                "indicator": str(r["indicator_code"]),
                "date": str(pd.Timestamp(r["price_date"]).date()),
                "value": r.get("value"),
                "note": str(r.get("note", "") or "")[:400],
                "source": str(r.get("source_name", "") or ""),
            })

    # 전문 매체 RSS (조정자 지시 8/25) — 실패해도 다이제스트는 계속
    try:
        rows += _fetch_specialist_media()
    except Exception as e:
        print(f"[경고] 전문 매체 RSS 단계 실패(비치명): {e}")

    got = {r["indicator"] for r in rows}
    lines = [f"# 일별 비정형 신호 다이제스트 — {date.today()}", "",
             "> Perplexity·실시간 프록시 수집분의 당일 요약 (조정자 지시 8/14 · A-163).",
             "> 수치와 함께 근거 발췌(note)를 보존한다 — S-5 출처보존.", ""]
    missing_all: list[str] = []
    for cat, inds in DAILY_UNSTRUCTURED.items():
        hit = [r for r in rows if r["indicator"] in inds]
        lines.append(f"## {cat}")
        lines.append("")
        if not hit:
            missing = [i for i in inds if i not in got]
            lines.append(f"_당일 수집 없음_ (대상: {', '.join(inds[:4])}"
                         f"{' …' if len(inds) > 4 else ''})")
            missing_all += missing
            lines.append("")
            continue
        lines.append("| 지표 | 일자 | 값 | 근거 발췌 |")
        lines.append("|---|---|---|---|")
        seen = set()
        for r in sorted(hit, key=lambda x: (x["indicator"], x["date"]), reverse=True):
            key = (r["indicator"], r["date"])
            if key in seen:
                continue
            seen.add(key)
            note = r["note"].replace("|", "／").replace("\n", " ")[:220]
            lines.append(f"| `{r['indicator']}` | {r['date']} | {r['value']} | {note} |")
        lines.append("")

    lines += ["## 수집 상태 요약", "",
              f"- 당일(±2일) 비정형 지표 확보: **{len(got & set(sum(DAILY_UNSTRUCTURED.values(), [])))}종** / "
              f"대상 {len(set(sum(DAILY_UNSTRUCTURED.values(), [])))}종",
              f"- 미확보: {', '.join(sorted(set(missing_all))[:12]) or '없음'}", ""]

    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f"daily_unstructured_digest_{date.today()}.md"
    text = "\n".join(lines) + "\n"
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"[완료] → {out}")

    _append_archive(rows)
    _emit_ontology_candidates(rows)
    return 0


def _append_archive(rows: list[dict]) -> None:
    """당일 수집 행을 변수별 일별 아카이브 CSV에 append (중복 제거·S-5 발췌 보존)."""
    targets = set(sum(DAILY_UNSTRUCTURED.values(), []))
    cat_of = {ind: cat for cat, inds in DAILY_UNSTRUCTURED.items() for ind in inds}
    new = pd.DataFrame([{
        "date": r["date"],
        "indicator": r["indicator"],
        "category": cat_of.get(r["indicator"], ""),
        "value": r["value"],
        "note": r["note"][:500].replace("\n", " "),
        "source_name": r["source"],
        "appended_at": pd.Timestamp.now("UTC").isoformat(timespec="seconds"),
    } for r in rows if r["indicator"] in targets])
    if new.empty:
        print("[아카이브] 신규 비정형 신호 없음 — append 생략")
        return
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    if ARCHIVE.exists():
        old = pd.read_csv(ARCHIVE, dtype=str)
        merged = pd.concat([old, new.astype(str)], ignore_index=True)
    else:
        merged = new.astype(str)
    before = len(merged)
    merged = merged.drop_duplicates(subset=["date", "indicator"], keep="first")
    merged = merged.sort_values(["date", "indicator"]).reset_index(drop=True)
    n_new = len(merged) - (before - len(new))
    if ARCHIVE.exists() and n_new <= 0:
        print("[아카이브] 전량 기존재(중복) — 파일 무변경")
        return
    merged.to_csv(ARCHIVE, index=False, encoding="utf-8")
    print(f"[아카이브] 신규 {max(n_new, 0)}건 append → {ARCHIVE} (누적 {len(merged)}행)")


# ── 온톨로지 후보 큐 (A-198 · 조정자 재확인 후속) ────────────────────────────
# 일별 신호가 임계를 넘으면 event_schema.json의 MarketEvent 후보(review_status=
# extracted)로 대기열에 적재한다 — **자동화는 후보 발견·적재까지만**이며, causal_edges
# 승격은 P1-06 검증 계약(S-1: 도메인 검증 서명+evidence 필수)을 그대로 따른다.
# 기존 C10 게이트(validate_semantic_layer.py)가 이 파일을 무료로 검증한다.
CANDIDATE_DIR = Path("data/semantic/events")
# 임계: (지표, 판정 함수) — 값 파싱 실패는 후보 미적재(추측 금지)
_CANDIDATE_RULES = {
    "HORMUZ_THREAT_LEVEL":   lambda v: v >= 2,
    "SUEZ_RED_SEA_RISK":     lambda v: v >= 2,
    "US_CHINA_TARIFF_STATUS": lambda v: v >= 2,
    "GEOINTEL_RISK_COMPOSITE": lambda v: v >= 60,
    "GPR_REALTIME":          lambda v: v >= 200,   # 소통용 직관 기준(스킬 정합)
}


def _emit_ontology_candidates(rows: list[dict]) -> None:
    """임계 초과 일별 신호 → MarketEvent 후보 JSON (P1-06 검증 입구)."""
    import json
    cands = []
    for r in rows:
        rule = _CANDIDATE_RULES.get(r["indicator"])
        if rule is None:
            continue
        try:
            val = float(str(r["value"]).replace(",", ""))
        except (TypeError, ValueError):
            continue
        if not rule(val):
            continue
        cands.append({
            "event_id": f"EVT-{r['date']}-{r['indicator']}",
            "event_type": "MarketEvent",
            "event_date": r["date"],
            "region": "GLOBAL",
            "confidence": "LOW",                     # 프록시 단일 출처 — 검증 전
            "review_status": "extracted",            # S-1: 자동 승격 금지 — P1-06 검증 대기
            "indicator": r["indicator"],
            "value": val,
            "evidence": [{
                "document_id": f"daily_digest_{r['date']}",
                "page": 1,                            # 다이제스트 단일 페이지 산출물
                "exact_quote": (r.get("note") or "")[:300],
            }],
            "source_name": r.get("source", "perplexity_proxy"),
        })
    if not cands:
        print("[후보 큐] 임계 초과 신호 없음 — 온톨로지 후보 미생성")
        return
    CANDIDATE_DIR.mkdir(parents=True, exist_ok=True)
    out = CANDIDATE_DIR / f"candidates_{cands[0]['event_date']}.json"
    out.write_text(json.dumps(cands, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[후보 큐] MarketEvent 후보 {len(cands)}건 → {out} (P1-06 검증 대기 — 자동 승격 없음)")


if __name__ == "__main__":
    raise SystemExit(main())
