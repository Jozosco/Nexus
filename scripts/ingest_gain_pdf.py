#!/usr/bin/env python3
"""
USDA FAS GAIN 보고서 PDF 수집·판독·요약 스크립트 (WBS 1.1.43)

입력 폴더:
  data/raw/USDA/FAS/GAIN/Oilseeds/*.pdf   — Oilseeds and Products 보고서
  data/raw/USDA/FAS/GAIN/Biofuels/*.pdf   — Biofuels/Biodiesel/Ethanol 보고서

출력:
  1) data/raw/gain_historical.parquet
       PDF별 메타 + 판독 결과 + 대두유 신호 태그 (기계 판독용 / G1 보조 신호)
  ※ 열람용 요약 md는 본 스크립트가 아니라 summarize_pdfs.py(요약 스킴 v2 —
    PDF 옆 Summary/ 폴더)가 전담. 구 gain_summaries/ 이중 생성 제거(Session 44).

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

# as-of 헬퍼 로드 — 스크립트 직접 실행 시 저장소 루트를 경로에 추가
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from src.pipeline.asof import attach_asof  # noqa: E402

GAIN_DIR     = Path("data/raw/USDA/FAS/GAIN")
OUTPUT_DIR   = Path("data/raw")

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
        # A-092: 원본 파일명이 US 형식(MM.DD)으로 붙은 사례 — 월 자리에 일(日)이 들어와
        # 규칙 위반. 추정 변환하지 않고 건너뜀 → 재정리 시 YY.MM 규칙으로 개명 필요.
        print(f"  [경고] 월 범위 초과({month}) — 파일명이 MM.DD 형식일 가능성: {stem}")
        return None
    parts = stem.split("_", 2)
    country = parts[1].strip() if len(parts) > 1 else "Unknown"
    title   = parts[2].strip() if len(parts) > 2 else stem
    return (year, month, country, title)


def _is_real_pdf(path: Path) -> tuple[bool, str]:
    """매직바이트 판정 (A-085). GAIN 코퍼스 72건이 '<DOCUMENT SAFER...>' 사내 문서보안(DRM)
    래퍼로 저장돼 있어 어떤 파서도 해독 불가 — WASDE 17~23년(A-051)과 동일 사례.
    pypdf의 'No /Root object!'는 이 DRM 래퍼의 증상이며 파서 결함이 아니다."""
    try:
        head = open(path, "rb").read(16)
    except OSError as e:
        return False, f"읽기 실패({e})"
    if head[:4] == b"%PDF":
        return True, ""
    if b"DOCUMENT" in head or b"SAFER" in head:
        return False, "문서보안(DRM) 래퍼 — 평문 재저장 필요"
    return False, f"미상 매직({head[:4]!r})"


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


def parse_gain_pdf(pdf_path: Path, category: str) -> Optional[dict]:
    """단일 GAIN PDF → 메타·판독·신호 레코드. 파일명 파싱 실패 시 None."""
    parsed = _parse_filename(pdf_path.stem)
    if parsed is None:
        print(f"  [건너뜀] 파일명 규칙 불일치: {pdf_path.name}")
        return None
    year, month, country, title = parsed

    real, why = _is_real_pdf(pdf_path)
    if not real:
        print(f"  [건너뜀-DRM] {pdf_path.name}: {why}")
        return {"price_date": date(year, month, 1), "country": country,
                "category": category, "title": title, "n_pages": 0, "n_chars": 0,
                "readable": False, "signal_tags": "", "source_name": "USDA_FAS_GAIN_PDF",
                "note": f"{pdf_path.name} [DRM 차단]",
                "ingested_at": pd.Timestamp.now("UTC")}

    try:
        text = _extract_text(pdf_path)
    except Exception as e:
        print(f"    [오류] 텍스트 추출 실패: {pdf_path.name}: {e}")
        text = ""
    n_pages  = _page_count(pdf_path)
    n_chars  = len(text.strip())
    readable = n_chars > 50
    signals  = _detect_signals(text) if readable else []

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
        # A-083: 연/월 재정리 후 PDF가 {YYYY}/{MM}/ 하위로 이동 → 재귀 탐색 필수
        #        (구 glob("*.pdf")=최상위만 → "PDF 없음" 오탐의 근본 원인)
        pdfs = sorted(pp for pp in sub.rglob("*.pdf")
                      if "summary" not in (q.lower() for q in pp.parts)) if sub.exists() else []
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
    # D-023: GAIN 보고서는 발행일에 즉시 공개 — price_date가 곧 이용 가능 시점
    df = attach_asof(df, source="USDA_FAS_GAIN_PDF")
    df.to_parquet(out_path, index=False)

    print(f"\n[완료] GAIN 판독 집계 → {out_path}")
    print(f"  총 {total}건 | 판독 정상 {ok} · 판독 실패 {failed} · 건너뜀 {skipped}")
    print(f"  기간: {df['price_date'].min()} ~ {df['price_date'].max()}")
    print(f"  국가 수: {df['country'].nunique()} · 카테고리: {sorted(df['category'].unique())}")
    print("  열람용 요약 md: summarize_pdfs.py gain (PDF 옆 Summary/ 폴더 — 요약 스킴 v2)")
    if failed:
        bad = df[~df["readable"]]["note"].tolist()
        print(f"  [주의] 판독 실패 {failed}건 (스캔본/이미지 PDF 가능성): {bad[:5]}"
              + (" ..." if failed > 5 else ""))


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else GAIN_DIR
    run(gain_dir=target)
