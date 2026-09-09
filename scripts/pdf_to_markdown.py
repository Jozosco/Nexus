"""PDF → Markdown 변환 + 요약 골격 생성 (A-251 — 승인자 지시: 향후 공유 PDF는 md 요약으로 처리).

용도: docs/research_desk/references/ 에 반입된 논문·보고서 PDF를 텍스트 마크다운으로 변환해 세션이
      PDF 대신 md를 읽게 함(토큰 절감·판독 재현성). 요약 본문(핵심 주장·Nexus 관련성·정직 분류)은
      세션이 md를 읽고 채움 — 자동 생성분은 서지·판독 메타·목차·키워드 적중·수치 후보까지.
사용: python scripts/pdf_to_markdown.py [PDF 또는 폴더 ...] [--force]
출력: references/markdown/{stem}.md · references/summaries/{stem}.md(골격, 기존 파일은 보존)
판독: PyMuPDF(fitz) 텍스트 블록 → 헤딩 복원(폰트 크기 상위), pdfplumber 표 → 마크다운 표. 스캔본은 '텍스트 없음' 판정.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

REF_DIR = Path("docs/research_desk/references")
MD_DIR = REF_DIR / "markdown"
SUM_DIR = REF_DIR / "summaries"
SBO_KEYWORDS = ["soybean oil", "soyoil", "palm oil", "sunflower", "rapeseed", "canola", "crush", "biodiesel",
                "renewable diesel", "RIN", "RVO", "basis", "freight", "CIF", "FOB", "Hormuz", "Suez", "Red Sea",
                "Black Sea", "tariff", "export tax", "WASDE", "stocks-to-use", "quantile", "GARCH", "regime",
                "forecast", "supply chain", "concentration", "HHI", "CR4", "대두유", "팜유", "해바라기", "압착"]
MIN_TEXT_CHARS = 200          # 페이지당 평균 이하이면 스캔본 의심


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _tables_md(pdf: Path, max_pages: int = 60) -> list[tuple[int, str]]:
    """pdfplumber 표 추출 → (페이지, 마크다운 표). 실패는 비치명."""
    out: list[tuple[int, str]] = []
    try:
        import pdfplumber
    except ImportError:
        return out
    try:
        with pdfplumber.open(str(pdf)) as doc:
            for i, page in enumerate(doc.pages[:max_pages], start=1):
                for tb in page.extract_tables() or []:
                    rows = [[(c or "").replace("\n", " ").strip() for c in r] for r in tb if r]
                    rows = [r for r in rows if any(r)]
                    if len(rows) < 2 or max(len(r) for r in rows) < 2:
                        continue
                    w = max(len(r) for r in rows)
                    rows = [r + [""] * (w - len(r)) for r in rows]
                    md = "| " + " | ".join(rows[0]) + " |\n|" + "---|" * w + "\n"
                    md += "\n".join("| " + " | ".join(r) + " |" for r in rows[1:])
                    out.append((i, md))
                page.flush_cache()
    except Exception as e:                                          # noqa: BLE001
        print(f"  [경고] 표 추출 실패(비치명): {e}")
    return out


def convert(pdf: Path) -> dict:
    import fitz  # PyMuPDF
    doc = fitz.open(str(pdf))
    sizes: Counter = Counter()
    pages_blocks: list[list[tuple[float, str]]] = []
    for page in doc:
        blocks = []
        for b in page.get_text("dict")["blocks"]:
            if b.get("type") != 0:
                continue
            for line in b["lines"]:
                txt = "".join(sp["text"] for sp in line["spans"]).strip()
                if not txt:
                    continue
                sz = round(max(sp["size"] for sp in line["spans"]), 1)
                sizes[sz] += len(txt)
                blocks.append((sz, txt))
        pages_blocks.append(blocks)
    n_pages = len(doc)
    total_chars = sum(len(t) for pb in pages_blocks for _, t in pb)
    body_size = sizes.most_common(1)[0][0] if sizes else 0
    big = sorted({s for s in sizes if s > body_size * 1.15}, reverse=True)
    h_level = {s: min(i + 1, 3) for i, s in enumerate(big[:3])}

    lines: list[str] = []
    headings: list[str] = []
    for pi, pb in enumerate(pages_blocks, start=1):
        lines.append(f"\n<!-- page {pi} -->\n")
        buf: list[str] = []
        for sz, txt in pb:
            lvl = h_level.get(sz)
            if lvl and len(txt) < 120 and not re.match(r"^\d+(\.\d+)*$", txt):
                if buf:
                    lines.append(" ".join(buf)); buf = []
                lines.append(f"\n{'#' * (lvl + 1)} {txt}\n")
                headings.append(f"{'  ' * (lvl - 1)}- {txt} (p.{pi})")
            else:
                buf.append(txt)
                if txt.endswith((".", "。", ":", "?", "!")):
                    lines.append(" ".join(buf)); buf = []
        if buf:
            lines.append(" ".join(buf))
    text = "\n".join(lines)
    tables = _tables_md(pdf)
    kw_hits = {k: len(re.findall(re.escape(k), text, re.IGNORECASE)) for k in SBO_KEYWORDS}
    kw_hits = {k: v for k, v in kw_hits.items() if v}
    nums = re.findall(r"[^\n]{0,60}\b\d{1,3}(?:[,.]\d{3})*(?:\.\d+)?\s?(?:%|\$|USD|MT|t\b|bp|million|billion|천|만|톤)[^\n]{0,60}", text)
    scanned = n_pages > 0 and total_chars / max(n_pages, 1) < MIN_TEXT_CHARS
    return {"pages": n_pages, "chars": total_chars, "scanned": scanned, "text": text, "headings": headings,
            "tables": tables, "keywords": kw_hits, "numbers": nums[:40], "sha256": _sha256(pdf)}


def write_outputs(pdf: Path, r: dict, force: bool) -> tuple[Path, Path]:
    MD_DIR.mkdir(parents=True, exist_ok=True)
    SUM_DIR.mkdir(parents=True, exist_ok=True)
    md = MD_DIR / f"{pdf.stem}.md"
    head = (f"# {pdf.stem}\n\n> 원본: `{pdf.as_posix()}` · SHA256 `{r['sha256'][:16]}…` · {r['pages']}쪽 · "
            f"{r['chars']:,}자 · 변환 {date.today()} (pdf_to_markdown.py)\n"
            + ("> ⚠️ 텍스트 층 부족 — 스캔본 추정(이미지 판독 필요)\n" if r["scanned"] else "") + "\n")
    toc = "## 목차(자동 복원)\n" + ("\n".join(r["headings"]) if r["headings"] else "- (헤딩 미검출)") + "\n\n"
    tbl = ""
    if r["tables"]:
        tbl = "## 표(자동 추출)\n" + "\n\n".join(f"**표 p.{p}**\n\n{t}" for p, t in r["tables"]) + "\n\n"
    md.write_text(head + toc + tbl + "## 본문\n" + r["text"] + "\n", encoding="utf-8")
    summ = SUM_DIR / f"{pdf.stem}.md"
    if summ.exists() and not force:
        return md, summ
    kw = ", ".join(f"{k}({v})" for k, v in sorted(r["keywords"].items(), key=lambda kv: -kv[1])[:15]) or "—"
    numbers = "\n".join(f"- {n.strip()}" for n in r["numbers"][:20]) or "- (후보 없음)"
    summ.write_text(f"""# 요약 — {pdf.stem}

> 상태: **골격(자동)** — 서지·판독 메타·목차·키워드·수치 후보는 자동 생성. 아래 '핵심'부터는 세션이 `markdown/{pdf.stem}.md`를
> 읽고 채움. 원본 PDF는 직접 판독하지 않음(A-251). 정직 분류 어휘: 채용 / Challenger 검토 대기 / 배경 / 인용 주의 / 반면교사.

## 서지·판독 메타
- 원본: `{pdf.as_posix()}` · SHA256 `{r['sha256'][:16]}…`
- 분량: {r['pages']}쪽 · {r['chars']:,}자 · 표 {len(r['tables'])}개 · 스캔본 의심: {'예' if r['scanned'] else '아니오'}
- 변환일: {date.today()} · 변환기: scripts/pdf_to_markdown.py

## 목차(자동)
{chr(10).join(r['headings'][:30]) if r['headings'] else '- (헤딩 미검출)'}

## 대두유 관련 키워드 적중(자동)
{kw}

## 수치 후보(자동 — 검증 전)
{numbers}

## 핵심 주장 (세션 작성)
- (미작성)

## 방법·데이터 (세션 작성)
- (미작성)

## Nexus 관련성 — G1 / G2 / G3 / 시맨틱 (세션 작성)
- (미작성)

## 정직 분류·인용 가능 문장 (세션 작성)
- 분류: (미작성)
- 인용 가능 문장·locator: (미작성)

## 온톨로지 반영 후보 (세션 작성)
- CE evidence / MP 등재 / 엔티티: (미작성)
""", encoding="utf-8")
    return md, summ


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PDF → Markdown + 요약 골격")
    ap.add_argument("paths", nargs="*", default=[str(REF_DIR)])
    ap.add_argument("--force", action="store_true", help="기존 md·요약 덮어쓰기")
    ap.add_argument("--only-new", action="store_true", help="markdown/이 없는 PDF만 변환")
    a = ap.parse_args(argv)
    pdfs: list[Path] = []
    for p in a.paths:
        pp = Path(p)
        pdfs += sorted(pp.rglob("*.pdf")) if pp.is_dir() else [pp]
    pdfs = [p for p in pdfs if p.suffix.lower() == ".pdf" and MD_DIR not in p.parents]
    if a.only_new:
        pdfs = [p for p in pdfs if not (MD_DIR / f"{p.stem}.md").exists()]
    if not pdfs:
        print("[정보] 변환 대상 PDF 없음")
        return 0
    ok = fail = 0
    for pdf in pdfs:
        try:
            r = convert(pdf)
            md, summ = write_outputs(pdf, r, a.force)
            ok += 1
            print(f"[완료] {pdf.name}: {r['pages']}쪽·{r['chars']:,}자·표 {len(r['tables'])}"
                  f"{' ·⚠️스캔본' if r['scanned'] else ''} → {md.relative_to(REF_DIR)} / {summ.relative_to(REF_DIR)}")
        except Exception as e:                                      # noqa: BLE001
            fail += 1
            print(f"[오류] {pdf.name}: 변환 실패 — {e}")
    print(f"[집계] 성공 {ok} · 실패 {fail}")
    return 1 if fail and not ok else 0


if __name__ == "__main__":
    sys.exit(main())
