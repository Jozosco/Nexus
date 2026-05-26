"""
리서치 문서 PDF/HTML 변환 스크립트
입력: docs/research_desk/*.md (또는 인수로 지정한 경로)
출력:
  - {name}_ko.pdf + {name}_ko.html  (한국어 원본)
  - {name}_en.pdf + {name}_en.html  (영어 번역 — PERPLEXITY_API_KEY 등록 시 자동 생성)

실행: python scripts/generate_research_pdf.py [입력_마크다운_경로] [--lang ko|en|both]
예시: python scripts/generate_research_pdf.py docs/research_desk/soybean_oil_historical_crisis_analysis.md --lang both

의존성: GitHub Actions — weasyprint + fonts-noto-cjk + markdown2
번역 의존성: PERPLEXITY_API_KEY 또는 OPENAI_API_KEY 환경변수
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date
from pathlib import Path


CSS_STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');

* { box-sizing: border-box; }
body {
    font-family: 'Noto Sans KR', 'Noto Sans', 'Malgun Gothic', sans-serif;
    font-size: 10pt;
    line-height: 1.6;
    color: #1a1a2e;
    margin: 0;
    padding: 0;
}
@page {
    size: A4;
    margin: 20mm 18mm 20mm 18mm;
    @top-right { content: "Nexus | Project Confidential"; font-size: 8pt; color: #888; }
    @bottom-center { content: counter(page) " / " counter(pages); font-size: 8pt; color: #888; }
}
h1 { font-size: 18pt; color: #0a3d62; border-bottom: 2px solid #0a3d62; padding-bottom: 4px; margin-top: 20px; }
h2 { font-size: 14pt; color: #1e3799; border-bottom: 1px solid #ddd; padding-bottom: 3px; margin-top: 16px; }
h3 { font-size: 12pt; color: #2c3e50; margin-top: 12px; }
h4 { font-size: 10pt; color: #34495e; font-style: italic; }
table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
    font-size: 9pt;
}
th {
    background-color: #0a3d62;
    color: white;
    padding: 6px 8px;
    text-align: left;
}
td { padding: 5px 8px; border: 1px solid #ddd; }
tr:nth-child(even) { background-color: #f7f9fc; }
code {
    font-family: 'Courier New', monospace;
    background: #f0f0f0;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 8.5pt;
}
pre {
    background: #f8f8f8;
    border: 1px solid #ddd;
    border-left: 4px solid #0a3d62;
    padding: 10px;
    font-size: 8.5pt;
    overflow-x: auto;
    page-break-inside: avoid;
}
blockquote {
    border-left: 4px solid #e74c3c;
    background: #fff5f5;
    margin: 10px 0;
    padding: 8px 12px;
    color: #c0392b;
}
.warning { color: #e74c3c; font-weight: bold; }
.hitl-gate {
    background: #fff3cd;
    border: 1px solid #ffc107;
    padding: 8px 12px;
    border-radius: 4px;
    margin: 8px 0;
    font-size: 9pt;
}
hr { border: none; border-top: 1px solid #ddd; margin: 16px 0; }
"""


def _md_to_html(md_text: str, title: str) -> str:
    """마크다운 → HTML 변환 (markdown2 패키지 사용)."""
    try:
        import markdown2  # type: ignore
        body = markdown2.markdown(
            md_text,
            extras=["tables", "fenced-code-blocks", "header-ids", "strike", "task_list"],
        )
    except ImportError:
        # markdown2 미설치 시 기본 처리 (테이블 없음)
        try:
            import markdown  # type: ignore
            body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
        except ImportError:
            print("[경고] markdown2 또는 markdown 패키지 미설치. pip install markdown2")
            # 최소 HTML 래핑만 적용
            body = f"<pre>{md_text}</pre>"

    generated = date.today().isoformat()
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>{CSS_STYLE}</style>
</head>
<body>
  <div style="text-align:right; font-size:8pt; color:#888; margin-bottom:16px;">
    생성일: {generated} | Nexus Project — 내부 기밀 문서
  </div>
  {body}
</body>
</html>"""


def _html_to_pdf(html_content: str, pdf_path: Path) -> bool:
    """HTML → PDF 변환 (weasyprint)."""
    try:
        from weasyprint import HTML  # type: ignore
        HTML(string=html_content).write_pdf(str(pdf_path))
        return True
    except ImportError:
        print("[경고] weasyprint 미설치. GitHub Actions: sudo apt-get install -y fonts-noto-cjk libpango-1.0-0 && pip install weasyprint")
        return False
    except Exception as e:
        print(f"[경고] PDF 변환 실패: {e}")
        return False


def _translate_to_english(md_text: str) -> str | None:
    """한국어 마크다운 → 영어 번역 (Perplexity sonar-pro 또는 OpenAI API).

    마크다운 포맷(헤더, 테이블, 코드블록, 목록) 완전 보존.
    API 키 미등록 시 None 반환 → 영어 PDF 생성 건너뜀.
    """
    api_key = os.environ.get("PERPLEXITY_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[정보] PERPLEXITY_API_KEY / OPENAI_API_KEY 미등록 — 영어 번역 건너뜀")
        return None

    use_perplexity = bool(os.environ.get("PERPLEXITY_API_KEY"))
    base_url = "https://api.perplexity.ai" if use_perplexity else "https://api.openai.com/v1"
    model = "sonar-pro" if use_perplexity else "gpt-4o-mini"

    system_prompt = (
        "You are a professional technical translator specializing in commodity trading and supply chain documents. "
        "Translate the Korean markdown document to English. "
        "Rules: (1) Preserve ALL markdown formatting exactly — headers (#), tables (|), code blocks (```), bullets. "
        "(2) Keep variable names, technical codes, and formula symbols unchanged. "
        "(3) Translate Korean text naturally with domain-appropriate English. "
        "(4) Output ONLY the translated markdown — no explanations or preamble."
    )

    try:
        from openai import OpenAI  # type: ignore
        client = OpenAI(api_key=api_key, base_url=base_url)
        # 8000자 초과 시 분할 처리 (토큰 안전 여유)
        chunks = [md_text[i:i+8000] for i in range(0, len(md_text), 8000)]
        translated_parts = []
        for i, chunk in enumerate(chunks):
            r = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": chunk},
                ],
                max_tokens=8192,
            )
            translated_parts.append(r.choices[0].message.content)
            if len(chunks) > 1:
                time.sleep(1)  # API 레이트 리밋 방지
        return "\n".join(translated_parts)
    except Exception as e:
        print(f"[경고] 영어 번역 실패: {e} — 영어 PDF 건너뜀")
        return None


def convert(
    md_path: str | Path,
    output_dir: str | Path | None = None,
    lang: str = "both",
) -> dict[str, tuple[Path, Path | None]]:
    """마크다운 파일을 HTML과 PDF로 변환. 한국어(ko)·영어(en)·양쪽(both) 지원.

    Args:
        md_path: 변환할 마크다운 파일 경로
        output_dir: 출력 디렉터리 (기본: 입력 파일과 동일 위치)
        lang: 출력 언어 — 'ko' | 'en' | 'both' (기본: 'both')

    Returns:
        {'ko': (html_path, pdf_path), 'en': (html_path, pdf_path)}
        — pdf_path는 weasyprint 없을 시 None; 'en'은 번역 실패 시 딕셔너리에서 제외
    """
    import time as _time  # noqa: F811

    src = Path(md_path)
    if not src.exists():
        raise FileNotFoundError(f"[오류] 파일 없음: {src}")

    out_dir = Path(output_dir) if output_dir else src.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    md_text = src.read_text(encoding="utf-8")
    stem = src.stem
    # 이미 _ko/_en 접미사가 있으면 그대로 사용, 없으면 추가
    base_stem = stem.removesuffix("_ko").removesuffix("_en")
    title_ko = base_stem.replace("_", " ").title()

    results: dict[str, tuple[Path, Path | None]] = {}

    # ─── 한국어 버전 ─────────────────────────────────────────────────────────
    if lang in ("ko", "both"):
        html_content_ko = _md_to_html(md_text, f"{title_ko} (한국어)")
        html_path_ko = out_dir / f"{base_stem}_ko.html"
        html_path_ko.write_text(html_content_ko, encoding="utf-8")
        print(f"[완료] HTML(KO) 저장 → {html_path_ko}")

        pdf_path_ko = out_dir / f"{base_stem}_ko.pdf"
        ok_ko = _html_to_pdf(html_content_ko, pdf_path_ko)
        if ok_ko:
            print(f"[완료] PDF(KO) 저장 → {pdf_path_ko}")
        results["ko"] = (html_path_ko, pdf_path_ko if ok_ko else None)

    # ─── 영어 버전 ─────────────────────────────────────────────────────────
    if lang in ("en", "both"):
        en_text = _translate_to_english(md_text)
        if en_text:
            html_content_en = _md_to_html(en_text, f"{title_ko} (English)")
            html_path_en = out_dir / f"{base_stem}_en.html"
            html_path_en.write_text(html_content_en, encoding="utf-8")
            print(f"[완료] HTML(EN) 저장 → {html_path_en}")

            pdf_path_en = out_dir / f"{base_stem}_en.pdf"
            ok_en = _html_to_pdf(html_content_en, pdf_path_en)
            if ok_en:
                print(f"[완료] PDF(EN) 저장 → {pdf_path_en}")
            results["en"] = (html_path_en, pdf_path_en if ok_en else None)
        else:
            print(f"[정보] {base_stem}: 영어 번역 불가 — 영어 PDF 건너뜀")

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Nexus 리서치 마크다운 → HTML/PDF 변환기 (한국어·영어 분리 출력)"
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="docs/research_desk",
        help="변환할 .md 파일 또는 디렉터리 (기본: docs/research_desk)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="출력 디렉터리 (기본: 입력 파일과 동일 위치)",
    )
    parser.add_argument(
        "--lang",
        choices=["ko", "en", "both"],
        default="both",
        help="출력 언어: ko(한국어만) | en(영어만) | both(양쪽, 기본)",
    )
    args = parser.parse_args()

    target = Path(args.input)

    if target.is_file() and target.suffix == ".md":
        md_files = [target]
    elif target.is_dir():
        md_files = sorted(target.glob("*.md"))
        if not md_files:
            print(f"[경고] {target}에 .md 파일 없음")
            sys.exit(0)
    else:
        print(f"[오류] 유효하지 않은 경로: {target}")
        sys.exit(1)

    lang_desc = {"ko": "한국어", "en": "영어", "both": "한국어+영어"}
    print(f"[정보] 변환 대상: {len(md_files)}개 파일 | 출력 언어: {lang_desc[args.lang]}")
    success_count = 0
    for md in md_files:
        try:
            results = convert(md, output_dir=args.output_dir, lang=args.lang)
            if results:
                success_count += 1
        except Exception as e:
            print(f"[오류] {md.name} 변환 실패: {e}")

    print(f"\n[완료] {success_count}/{len(md_files)}개 파일 변환 완료")


if __name__ == "__main__":
    main()
