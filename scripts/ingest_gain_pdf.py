#!/usr/bin/env python3
"""
USDA FAS GAIN 보고서 PDF 수집·판독·요약 스크립트 (WBS 1.1.43)

입력 폴더:
  data/raw/USDA/FAS/GAIN/Oilseeds/*.pdf   — Oilseeds and Products 보고서
  data/raw/USDA/FAS/GAIN/Biofuels/*.pdf   — Biofuels/Biodiesel/Ethanol 보고서

출력:
  1) data/raw/gain_historical.parquet
       PDF별 메타 + 판독 결과 + 대두유 신호 태그 (기계 판독용 / G1 보조 신호)
  2) data/processed/gain_summaries/{YYYY}/{MM}/{Country}/{stem}.md
       연·월·국가별로 정리된 요약 문서 (사용자 열람용)

파일명 규칙 (A-046/A-057):
  {YY}.{MM}_{Country}_{Title}.pdf
  예) "22.04_Vietnam_Oilseeds and Products Annual.pdf" → 2022-04 · Vietnam
      "20.09_Czech Republic_Sees Solid Harvest...pdf" → 2020-09 · Czech Republic
  (Country 는 공백 포함 가능, Title 은 두 번째 '_' 이후 전체)

의존성: pdfplumber >= 0.9 (fallback: pypdf >= 3.0) · pandas >= 2.0
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd

GAIN_DIR     = Path("data/raw/USDA/FAS/GAIN")
OUTPUT_DIR   = Path("data/raw")
SUMMARY_ROOT = Path("data/processed/gain_summaries")

_FNAME_RE = re.compile(r"^(\d{2})\.(\d{2})_")

# 대두유 조달 관점 핵심 신호 키워드 → 태그 (정성 신호; G1 보조)
_SIGNAL_KEYWORDS: dict[str, str] = {
    r"export\s+tax|export\s+duty|export\s+ban|export\s+restrict": "수출규제",
    r"import\s+tariff|import\s+duty|tariff\s+hike":               "수입관세",
    r"biodiesel|renewable\s+diesel|\bSAF\b|blending\s+mandate":   "바이오연료수요",
    r"drought|dry\s+weather|la\s*ni|el\s*ni":                     "기상이변",
    r"crush|crushing":                                            "압착",
    r"ending\s+stock|carryover|stocks?-to-use":                   "재고",
    r"production\s+(?:up|down|increase|decrease|revised)":        "생산변동",
}


def _parse_filename(stem: str) -> Optional[tuple[int, int, str, str]]:
    """파일명 stem → (year, month, country, title). 실패 시 None."""
    m = _FNAME_RE.match(stem)
    if not m:
        return None
    year, month = 2000 + int(m.group(1)), int(m.group(2))
    if not (1 <= month <= 12):
        return None
    parts = stem.split("_", 2)
    country = parts[1].strip() if len(parts) > 1 else "Unknown"
    title   = parts[2].strip() if len(parts) > 2 else stem
    return (year, month, country, title)


def _extract_text(pdf_path: Path) -> str:
    """PDF 텍스트 추출 — pdfplumber 우선, fallback pypdf."""
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            return "\n".join(p.extract_text() or "" for p in pdf.pages)
    except ImportError:
        pass
    from pypdf import PdfReader  # pdfplumber 부재 시
    reader = PdfReader(str(pdf_path))
    return "\n".join(p.extract_text() or "" for p in reader.pages)


def _page_count(pdf_path: Path) -> int:
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            return len(pdf.pages)
    except ImportError:
        from pypdf import PdfReader
        return len(PdfReader(str(pdf_path)).pages)
    except Exception:
        return 0


def _detect_signals(text: str) -> list[str]:
    """본문에서 대두유 관련 정성 신호 태그 추출."""
    low = text.lower()
    tags = [tag for pat, tag in _SIGNAL_KEYWORDS.items()
            if re.search(pat, low, re.IGNORECASE)]
    return sorted(set(tags))


def _clean_excerpt(text: str, limit: int = 1200) -> str:
    """요약 발췌용 텍스트 정리 (과도한 공백 제거, 길이 제한)."""
    collapsed = re.sub(r"[ \t]+", " ", text)
    collapsed = re.sub(r"\n{3,}", "\n\n", collapsed).strip()
    return collapsed[:limit]


def _write_summary(
    year: int, month: int, country: str, title: str, category: str,
    n_pages: int, n_chars: int, readable: bool, signals: list[str],
    excerpt: str, stem: str,
) -> Path:
    """연/월/국가 폴더에 요약 마크다운 저장."""
    safe_country = re.sub(r"[^\w\s-]", "", country).strip() or "Unknown"
    out_dir = SUMMARY_ROOT / f"{year:04d}" / f"{month:02d}" / safe_country
    out_dir.mkdir(parents=True, exist_ok=True)
    status = "✅ 판독 정상" if readable else "🚨 판독 실패(빈 텍스트)"
    sig = ", ".join(signals) if signals else "—"
    lines = [
        f"# {title}",
        "",
        f"- 카테고리: {category}",
        f"- 국가: {country}",
        f"- 발행: {year}년 {month:02d}월",
        f"- 페이지: {n_pages} · 추출 문자수: {n_chars:,} · {status}",
        f"- 대두유 관련 신호: {sig}",
        "",
        "## 요약 발췌",
        "",
        excerpt if excerpt else "_(텍스트 추출 실패 — 스캔본/이미지 PDF 가능성)_",
    ]
    out_path = out_dir / f"{stem}.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def parse_gain_pdf(pdf_path: Path, category: str) -> Optional[dict]:
    """단일 GAIN PDF → 메타·판독·신호 레코드. 파일명 파싱 실패 시 None."""
    parsed = _parse_filename(pdf_path.stem)
    if parsed is None:
        print(f"  [건너뜀] 파일명 규칙 불일치: {pdf_path.name}")
        return None
    year, month, country, title = parsed

    try:
        text = _extract_text(pdf_path)
    except Exception as e:
        print(f"    [오류] 텍스트 추출 실패: {pdf_path.name}: {e}")
        text = ""
    n_pages  = _page_count(pdf_path)
    n_chars  = len(text.strip())
    readable = n_chars > 50
    signals  = _detect_signals(text) if readable else []
    excerpt  = _clean_excerpt(text) if readable else ""

    _write_summary(year, month, country, title, category,
                   n_pages, n_chars, readable, signals, excerpt, pdf_path.stem)

    return {
        "price_date":     date(year, month, 1),
        "country":        country,
        "category":       category,
        "title":          title,
        "n_pages":        n_pages,
        "n_chars":        n_chars,
        "readable":       readable,
        "signal_tags":    ",".join(signals),
        "source_name":    "USDA_FAS_GAIN_PDF",
        "note":           pdf_path.name,
        "ingested_at":    pd.Timestamp.now("UTC"),
    }


def run(gain_dir: Path = GAIN_DIR, output_dir: Path = OUTPUT_DIR) -> None:
    """GAIN PDF 전체 판독·요약·집계."""
    categories = {"Oilseeds": gain_dir / "Oilseeds",
                  "Biofuels": gain_dir / "Biofuels"}
    records: list[dict] = []
    total = ok = failed = skipped = 0

    for category, sub in categories.items():
        pdfs = sorted(sub.glob("*.pdf")) if sub.exists() else []
        if not pdfs:
            print(f"[정보] {sub} — PDF 없음.")
            continue
        print(f"[C-04] GAIN {category}: {len(pdfs)}개 PDF 판독 중...")
        for f in pdfs:
            total += 1
            rec = parse_gain_pdf(f, category)
            if rec is None:
                skipped += 1
                continue
            records.append(rec)
            if rec["readable"]:
                ok += 1
            else:
                failed += 1

    if not records:
        print("[경고] 처리된 GAIN PDF 없음. (폴더 비었거나 파일명 규칙 불일치)")
        return

    df = pd.DataFrame(records).sort_values(
        ["category", "price_date", "country"]).reset_index(drop=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "gain_historical.parquet"
    df.to_parquet(out_path, index=False)

    print(f"\n[완료] GAIN 판독 집계 → {out_path}")
    print(f"  총 {total}건 | 판독 정상 {ok} · 판독 실패 {failed} · 건너뜀 {skipped}")
    print(f"  기간: {df['price_date'].min()} ~ {df['price_date'].max()}")
    print(f"  국가 수: {df['country'].nunique()} · 카테고리: {sorted(df['category'].unique())}")
    print(f"  요약 문서: {SUMMARY_ROOT}/{{YYYY}}/{{MM}}/{{Country}}/*.md")
    if failed:
        bad = df[~df["readable"]]["note"].tolist()
        print(f"  [주의] 판독 실패 {failed}건 (스캔본/이미지 PDF 가능성): {bad[:5]}"
              + (" ..." if failed > 5 else ""))


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else GAIN_DIR
    run(gain_dir=target)
