#!/usr/bin/env python3
"""
파이프라인 요약 PDF 보고서 생성기 — WBS 1.1.8
실행: python src/pipeline/report_generator.py
출력: reports/pipeline_report_{YYYYMMDD_HHMM}.html  +  .pdf (weasyprint 가용 시)
"""
from __future__ import annotations

import glob
import os
from datetime import datetime
from pathlib import Path

import pandas as pd

OUTPUT_DIR = "data/raw"
REPORT_DIR = "reports"


def _collect_stats() -> list[dict]:
    files = sorted(
        glob.glob(f"{OUTPUT_DIR}/**/*.parquet", recursive=True)
        + glob.glob(f"{OUTPUT_DIR}/*.parquet")
    )
    results = []
    for f in files:
        try:
            df = pd.read_parquet(f)
            size_kb = os.path.getsize(f) / 1024
            ingested = df["ingested_at"].max() if "ingested_at" in df.columns else "N/A"
            null_pct = df.isnull().mean().mean() * 100
            results.append({
                "file":        Path(f).name,
                "rows":        len(df),
                "cols":        len(df.columns),
                "size_kb":     round(size_kb, 1),
                "ingested_at": str(ingested)[:19],
                "null_pct":    round(null_pct, 1),
                "status":      "OK",
            })
        except Exception as e:
            results.append({
                "file": Path(f).name, "rows": "–", "cols": "–",
                "size_kb": "–", "ingested_at": "–", "null_pct": "–",
                "status": f"ERROR: {e}",
            })
    return results


def _render_html(stats: list[dict], run_id: str, run_ts: str) -> str:
    rows_html = ""
    for s in stats:
        bg = "#d4edda" if s["status"] == "OK" else "#f8d7da"
        null_val = s["null_pct"]
        null_warn = (
            " ⚠️" if isinstance(null_val, float) and null_val > 5 else
            " 🚨" if isinstance(null_val, float) and null_val > 15 else ""
        )
        rows_html += (
            f"<tr style='background:{bg}'>"
            f"<td>{s['file']}</td>"
            f"<td style='text-align:right'>{s['rows']}</td>"
            f"<td style='text-align:right'>{s['size_kb']} KB</td>"
            f"<td style='text-align:right'>{null_val}%{null_warn}</td>"
            f"<td>{s['ingested_at']}</td>"
            f"<td><b>{s['status']}</b></td>"
            f"</tr>\n"
        )

    total_rows = sum(s["rows"] for s in stats if isinstance(s["rows"], int))
    ok_count   = sum(1 for s in stats if s["status"] == "OK")
    err_count  = len(stats) - ok_count
    warn_files = [s["file"] for s in stats
                  if isinstance(s.get("null_pct"), float) and s["null_pct"] > 5]

    warn_section = ""
    if warn_files:
        warn_items = "".join(f"<li>{f}</li>" for f in warn_files)
        warn_section = (
            "<h2>⚠️ 데이터 품질 주의 파일</h2>"
            f"<ul style='color:#856404'>{warn_items}</ul>"
            "<p>결측치 5% 초과 — API 키·소스 연결 상태 확인 필요.</p>"
        )

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nexus Pipeline Report {run_ts[:10]}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
  body  {{ font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
           margin: 40px 60px; color: #333; font-size: 13px; line-height: 1.6; }}
  h1   {{ color: #1a237e; border-bottom: 3px solid #1a237e; padding-bottom: 10px; font-size: 20px; }}
  h2   {{ color: #283593; margin-top: 28px; font-size: 15px; }}
  .meta {{ background: #e8eaf6; padding: 14px 18px; border-radius: 8px; margin: 18px 0; }}
  .badge {{ display: inline-block; padding: 4px 12px; border-radius: 14px; font-size: 11px; font-weight: bold; margin: 2px; }}
  .ok   {{ background: #c8e6c9; color: #1b5e20; }}
  .err  {{ background: #ffcdd2; color: #b71c1c; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 14px; font-size: 12px; }}
  th    {{ background: #1a237e; color: #fff; padding: 9px 14px; text-align: left; }}
  td    {{ padding: 7px 14px; border-bottom: 1px solid #e0e0e0; }}
  tr:hover {{ opacity: 0.9; }}
  .quality-box {{ background: #fff8e1; border-left: 4px solid #ffc107; padding: 12px 16px;
                  border-radius: 4px; margin-top: 20px; font-size: 12px; }}
  .footer {{ margin-top: 48px; font-size: 11px; color: #9e9e9e;
             border-top: 1px solid #e0e0e0; padding-top: 14px; }}
</style>
</head>
<body>

<h1>Nexus External Data Pipeline<br>Summary &amp; Data Quality Report</h1>

<div class="meta">
  <strong>Run ID:</strong> {run_id}　│
  <strong>생성 시각 (UTC):</strong> {run_ts}　│
  <strong>총 파일:</strong> {len(stats)}개　│
  <strong>총 행 수:</strong> {total_rows:,}건　│
  <span class="badge ok">성공 {ok_count}</span>
  <span class="badge err">오류 {err_count}</span>
</div>

<h2>커넥터별 수집 결과</h2>
<table>
  <tr>
    <th>파일명</th>
    <th style="text-align:right">행 수</th>
    <th style="text-align:right">크기</th>
    <th style="text-align:right">결측치</th>
    <th>수집 시각 (UTC)</th>
    <th>상태</th>
  </tr>
  {rows_html}
</table>

{warn_section}

<div class="quality-box">
  <strong>데이터 품질 기준 (WBS 1.1.8)</strong><br>
  결측치 &lt;5%: 정상 &nbsp;|&nbsp;
  결측치 5–15%: 주의 ⚠️ &nbsp;|&nbsp;
  결측치 &gt;15%: 경보 🚨 &nbsp;|&nbsp;
  미갱신 &gt;5영업일: STALE 판정
</div>

<div class="footer">
  Project Nexus · WBS 1.1.8 Data Quality Report ·
  Branch: claude/setup-nexus-llm-tools-RX4aS ·
  Generated: {run_ts} UTC
</div>

</body>
</html>"""


def run() -> None:
    os.makedirs(REPORT_DIR, exist_ok=True)
    now    = datetime.utcnow()
    tag    = now.strftime("%Y%m%d_%H%M")
    run_ts = now.strftime("%Y-%m-%d %H:%M:%S")
    run_id = os.environ.get("GITHUB_RUN_ID", "local")

    stats = _collect_stats()
    if not stats:
        print(f"[경고] {OUTPUT_DIR} 에서 parquet 파일을 찾을 수 없음 — 보고서 건너뜀.")
        return

    html_path = f"{REPORT_DIR}/pipeline_report_{tag}.html"
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(_render_html(stats, run_id, run_ts))
    print(f"[완료] HTML 보고서 → {html_path}")

    try:
        from weasyprint import HTML as WeasyprintHTML  # type: ignore
        pdf_path = f"{REPORT_DIR}/pipeline_report_{tag}.pdf"
        WeasyprintHTML(filename=html_path).write_pdf(pdf_path)
        print(f"[완료] PDF 보고서  → {pdf_path}")
    except ImportError:
        print("[경고] weasyprint 미설치 — HTML만 저장됨. pip install weasyprint 로 PDF 활성화.")
    except Exception as e:
        print(f"[경고] PDF 변환 실패: {e} — HTML 보고서를 사용하세요.")


if __name__ == "__main__":
    run()
