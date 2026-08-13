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
}


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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
