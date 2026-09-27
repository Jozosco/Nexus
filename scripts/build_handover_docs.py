#!/usr/bin/env python3
"""인수인계 문서 4형식 재생성 빌더 — pptx 2종 · docx · xlsx (승인자 지시 2026-09-27 · A-284/R-041).

종전 pptx·docx·xlsx는 일회성 코드로 만들어져 재생성이 불가능했다(A-275 갭). 이 빌더는
`scripts/handover_content.py`(발표 자료 내용)와 `docs/handover/05_PoC_범위_정의서.md`(보고서·표 정본)를
읽어 4형식을 다시 만든다. 내용을 고칠 때는 md·content 모듈을 고치고 이 스크립트를 재실행한다.

디자인 원칙(승인자 제공 컨설팅사 보고서 실측 — 2026-09-27):
  · 16:9 · 백색 바탕 · 주황 강조(#FC5107)·진회색(#5D6168)·연회색(#E0E3E7)·연주황 패널(#FFEDE2)
  · 표지: 좌상 로고 텍스트, 영문 소제목(고딕 R) + 국문 대제목(명조 B 대형), 우측 주황 사선 띠, 좌하 발행월
  · 목차: 좌 1/3 색 블록, 우 "Agenda" 명조 제목 + 주황 번호 항목 · 섹션 구분: 상 2/3 색 블록 + 명조 대제목
  · 본문: 상단 회색 섹션 경로(고딕 R 10pt) · 명조 액션 타이틀(≈22pt) · 고딕 불릿(■/−) · 연주황 강조 패널 ·
    진회색 헤더 표 · 좌하 "자료:" 8pt · 푸터 "Nexus | 인수인계 보고 2026-09 | 쪽"
  · 사진 자산이 없으므로 사진 자리는 단색·연회색 블록으로 대체(외부 이미지 반입 없음)

폰트(승인자 지시): 제목 청정원고딕 B · 부제 청정원고딕 R · 본문 청정원명조 R (명조 대제목은 청정원명조 B).
  OTF는 사내 전용 라이선스라 저장소에 커밋하지 않는다 — 렌더 검증은 실행 환경 ~/.fonts 설치본으로만.
  python-pptx는 latin 폰트만 지정하므로 동아시아(`a:ea`)·복합(`a:cs`) 폰트를 XML로 함께 박는다.

사용:
    PYTHONPATH=. python scripts/build_handover_docs.py [--only pptx|docx|xlsx] [--out docs/handover]
의존: python-pptx ≥1.0 · python-docx ≥1.1 · openpyxl ≥3.1 (파이프라인 코드가 아니므로 openpyxl 사용 허용 — 문서 산출 전용)
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

# ── 스타일 상수 (교정 지점을 한곳에) ─────────────────────────────────────────
ORANGE = "FC5107"
ORANGE_SOFT = "FFEDE2"
GREY_DARK = "5D6168"
GREY_LIGHT = "E0E3E7"
GREY_MID = "9AA0A8"
INK = "3B3B3B"
INK_SOFT = "6B6F76"
WHITE = "FFFFFF"

F_TITLE = "청정원고딕 B"     # 제목·표 헤더·강조
F_SUB = "청정원고딕 R"       # 부제·경로·캡션·불릿
F_BODY = "청정원명조 R"      # 본문
F_MJ_B = "청정원명조 B"      # 명조 대제목(표지·섹션·액션 타이틀)

SLIDE_W_IN, SLIDE_H_IN = 13.333, 7.5
BODY_TOP, BODY_BOTTOM, BODY_LEFT, BODY_RIGHT = 1.56, 6.82, 0.55, 12.78
FOOTER_TEXT = "Nexus  |  인수인계 보고 2026-09  |  사내 한정"

TODAY = date.today().isoformat()


# ── pptx 헬퍼 ────────────────────────────────────────────────────────────────

def _pptx():
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.oxml.ns import qn
    return Presentation, Inches, Pt, RGBColor, PP_ALIGN, MSO_ANCHOR, MSO_SHAPE, qn


def _rgb(hexs: str):
    from pptx.dml.color import RGBColor
    return RGBColor.from_string(hexs)


def _set_run_font(run, name: str, size_pt: float, bold: bool = False, color: str = INK) -> None:
    """latin + ea + cs 폰트를 모두 지정 — 한글은 ea 폰트로 렌더되므로 필수."""
    from pptx.util import Pt
    from pptx.oxml.ns import qn
    run.font.name = name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.color.rgb = _rgb(color)
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        el = rpr.find(qn(tag))
        if el is None:
            el = rpr.makeelement(qn(tag), {})
            rpr.append(el)
        el.set("typeface", name)


def _textbox(slide, x, y, w, h, text: str, *, font=F_BODY, size=11, bold=False, color=INK,
             align="l", anchor="t", line_spacing=1.15, wrap=True, margin=0.04):
    from pptx.util import Inches, Pt
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.margin_left = tf.margin_right = Inches(margin)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
    lines = str(text).split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[align]
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = line
        _set_run_font(r, font, size, bold, color)
    return tb


def _rect(slide, x, y, w, h, fill: str, line: str | None = None, shape="rect"):
    from pptx.util import Inches
    from pptx.enum.shapes import MSO_SHAPE
    kind = {"rect": MSO_SHAPE.RECTANGLE, "round": MSO_SHAPE.ROUNDED_RECTANGLE,
            "para": MSO_SHAPE.PARALLELOGRAM}[shape]
    s = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = _rgb(fill)
    if line:
        s.line.color.rgb = _rgb(line)
        s.line.width = Inches(0.01)
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    if s.has_text_frame:
        s.text_frame.text = ""
    return s


# ── 높이 추정(레이아웃 엔진) ─────────────────────────────────────────────────

def _chars_per_line(width_in: float, size_pt: float) -> float:
    # 한글 혼합 문장: 전각 글자 폭 ≈ 1.0 × pt/72 in — 보수적 계수(렌더 실측: 0.85는 줄 수를 과소 추정해 겹침 발생)
    return max(8.0, width_in / (1.0 * size_pt / 72.0))


def _text_h(text: str, width_in: float, size_pt: float, spacing: float = 1.2) -> float:
    cpl = _chars_per_line(width_in, size_pt)
    lines = sum(max(1, math.ceil(len(ln) / cpl)) for ln in str(text).split("\n"))
    return lines * size_pt / 72.0 * spacing + 0.06


def _est_block_h(block: tuple, width_in: float, scale: float) -> float:
    kind = block[0]
    if kind == "h":
        return 0.34
    if kind == "p":
        return _text_h(block[1], width_in, 11 * scale) + 0.06
    if kind == "b":
        return sum(_text_h(t, width_in - 0.25, 10.5 * scale) for t in block[1]) + 0.08
    if kind == "panel":
        return _text_h(block[1], width_in - 0.3, 10.5 * scale) + 0.24
    if kind == "t":
        rows = block[1]
        ncol = len(rows[0])
        widths = block[2].get("widths") if len(block) > 2 and block[2] else None
        h = 0.0
        for i, row in enumerate(rows):
            cell_h = 0.0
            for j, cell in enumerate(row):
                cw = (widths[j] / sum(widths) * width_in) if widths else width_in / ncol
                cell_h = max(cell_h, _text_h(str(cell), cw - 0.12, (9.0 if i else 9.0) * scale, 1.15))
            h += cell_h + 0.06
        return h + 0.08
    if kind == "kpi":
        n = len(block[1])
        per_row = 3 if width_in > 6 else 2
        return math.ceil(n / per_row) * 1.12
    if kind == "steps":
        items = block[1]
        n = len(items)
        per_row = min(n, 5 if width_in > 9 else 3)
        cw = width_in / per_row - 0.12
        rows = math.ceil(n / per_row)
        h = 0.0
        for r in range(rows):
            chunk = items[r * per_row:(r + 1) * per_row]
            h += 0.38 + max(_text_h(b, cw - 0.16, 9.5 * scale) for _, b in chunk) + 0.14
        return h
    if kind == "num":
        return sum(0.30 + _text_h(b, width_in - 0.55, 10 * scale) for _, _, b in block[1]) + 0.05
    if kind == "cards":
        items = block[1]
        per_row = min(len(items), 3)
        cw = width_in / per_row - 0.12
        rows = math.ceil(len(items) / per_row)
        h = 0.0
        for r in range(rows):
            chunk = items[r * per_row:(r + 1) * per_row]
            h += 0.36 + max(_text_h(b, cw - 0.2, 9.5 * scale) for _, b in chunk) + 0.16
        return h
    return 0.3


# ── 블록 렌더 ────────────────────────────────────────────────────────────────

def _render_blocks(slide, blocks: list[tuple], x: float, y: float, w: float, scale: float,
                   sources: list[str]) -> float:
    for block in blocks:
        kind = block[0]
        bh = _est_block_h(block, w, scale)
        if kind == "h":
            _rect(slide, x, y + 0.08, 0.06, 0.2, ORANGE)
            _textbox(slide, x + 0.12, y, w - 0.12, 0.32, block[1], font=F_TITLE, size=12 * scale, bold=True, color=INK)
        elif kind == "p":
            _textbox(slide, x, y, w, bh, block[1], font=F_BODY, size=11 * scale, color=INK)
        elif kind == "b":
            yy = y
            for t in block[1]:
                th = _text_h(t, w - 0.25, 10.5 * scale)
                _textbox(slide, x, yy, 0.22, th, "■", font=F_SUB, size=7 * scale, color=ORANGE, margin=0.02)
                _textbox(slide, x + 0.2, yy, w - 0.22, th, t, font=F_SUB, size=10.5 * scale, color=INK)
                yy += th
        elif kind == "panel":
            _rect(slide, x, y, w, bh - 0.06, ORANGE_SOFT)
            _textbox(slide, x + 0.14, y + 0.09, w - 0.28, bh - 0.22, block[1], font=F_BODY,
                     size=10.5 * scale, color=INK)
        elif kind == "t":
            _render_table(slide, block, x, y, w, scale)
        elif kind == "kpi":
            _render_kpi(slide, block[1], x, y, w, scale)
        elif kind == "steps":
            _render_steps(slide, block[1], x, y, w, scale)
        elif kind == "num":
            yy = y
            for no, head, body in block[1]:
                bh1 = _text_h(body, w - 0.55, 10 * scale)
                _rect(slide, x, yy + 0.03, 0.36, 0.36, ORANGE, shape="round")
                _textbox(slide, x, yy + 0.03, 0.36, 0.36, str(no), font=F_TITLE, size=12 * scale, bold=True,
                         color=WHITE, align="c", anchor="m", margin=0.0)
                _textbox(slide, x + 0.48, yy, w - 0.5, 0.3, head, font=F_TITLE, size=11.5 * scale, bold=True, color=INK)
                _textbox(slide, x + 0.48, yy + 0.3, w - 0.5, bh1, body, font=F_BODY, size=10 * scale, color=INK)
                yy += 0.30 + bh1
        elif kind == "cards":
            _render_cards(slide, block[1], x, y, w, scale)
        y += bh + 0.1
    return y


def _render_table(slide, block, x, y, w, scale) -> None:
    from pptx.util import Inches, Pt
    from pptx.enum.text import MSO_ANCHOR
    rows = block[1]
    opts = block[2] if len(block) > 2 and block[2] else {}
    widths = opts.get("widths")
    ncol = len(rows[0])
    est_h = _est_block_h(block, w, scale)
    shape = slide.shapes.add_table(len(rows), ncol, Inches(x), Inches(y), Inches(w), Inches(est_h))
    tbl = shape.table
    tblpr = tbl._tbl.tblPr
    tblpr.set("bandRow", "0")
    tblpr.set("firstRow", "0")
    # 기본 스타일 제거(밝은 스타일 id) — 직접 채색
    style_el = tblpr.find("{http://schemas.openxmlformats.org/drawingml/2006/main}tableStyleId")
    if style_el is not None:
        style_el.text = "{5940675A-B579-460E-94D1-54222C63F5DA}"   # No Style, Table Grid
    if widths:
        total = sum(widths)
        for j, wj in enumerate(widths):
            tbl.columns[j].width = Inches(w * wj / total)
    for i, row in enumerate(rows):
        for j, cell_txt in enumerate(row):
            c = tbl.cell(i, j)
            c.margin_left = c.margin_right = Inches(0.06)
            c.margin_top = c.margin_bottom = Inches(0.03)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE if i == 0 else MSO_ANCHOR.TOP
            c.fill.solid()
            c.fill.fore_color.rgb = _rgb(GREY_DARK if i == 0 else (WHITE if i % 2 else "F6F7F8"))
            tf = c.text_frame
            tf.word_wrap = True
            lines = str(cell_txt).split("\n")
            for k, line in enumerate(lines):
                p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
                p.line_spacing = 1.08
                r = p.add_run()
                r.text = line
                if i == 0:
                    _set_run_font(r, F_TITLE, 9.0 * scale, True, WHITE)
                else:
                    _set_run_font(r, F_BODY if j else F_SUB, 9.0 * scale, j == 0 and opts.get("bold_first", True), INK)
        tbl.rows[i].height = Inches(0.24)


def _render_kpi(slide, items, x, y, w, scale) -> None:
    per_row = 3 if w > 6 else 2
    cw = (w - 0.15 * (per_row - 1)) / per_row
    for k, (big, cap) in enumerate(items):
        cx = x + (k % per_row) * (cw + 0.15)
        cy = y + (k // per_row) * 1.12
        _rect(slide, cx, cy, cw, 1.02, "F6F7F8")
        _rect(slide, cx, cy, 0.06, 1.02, ORANGE)
        _textbox(slide, cx + 0.14, cy + 0.04, cw - 0.2, 0.42, big, font=F_TITLE, size=18 * scale, bold=True, color=ORANGE)
        _textbox(slide, cx + 0.14, cy + 0.46, cw - 0.2, 0.54, cap, font=F_SUB, size=8.5 * scale, color=INK_SOFT)


def _render_steps(slide, items, x, y, w, scale) -> None:
    n = len(items)
    per_row = min(n, 5 if w > 9 else 3)
    cw = (w - 0.12 * (per_row - 1)) / per_row
    rows = math.ceil(n / per_row)
    yy = y
    for r in range(rows):
        chunk = items[r * per_row:(r + 1) * per_row]
        body_h = max(_text_h(b, cw - 0.16, 9.5 * scale) for _, b in chunk)
        for k, (head, body) in enumerate(chunk):
            cx = x + k * (cw + 0.12)
            _rect(slide, cx, yy, cw, 0.36, ORANGE if r == 0 else GREY_DARK)
            _textbox(slide, cx + 0.06, yy, cw - 0.12, 0.36, head, font=F_TITLE, size=10.5 * scale, bold=True,
                     color=WHITE, anchor="m")
            _rect(slide, cx, yy + 0.36, cw, body_h + 0.1, "F6F7F8")
            _textbox(slide, cx + 0.08, yy + 0.41, cw - 0.16, body_h, body, font=F_SUB, size=9.5 * scale, color=INK)
        yy += 0.38 + body_h + 0.14


def _render_cards(slide, items, x, y, w, scale) -> None:
    per_row = min(len(items), 3)
    cw = (w - 0.12 * (per_row - 1)) / per_row
    rows = math.ceil(len(items) / per_row)
    yy = y
    for r in range(rows):
        chunk = items[r * per_row:(r + 1) * per_row]
        body_h = max(_text_h(b, cw - 0.2, 9.5 * scale) for _, b in chunk)
        for k, (head, body) in enumerate(chunk):
            cx = x + k * (cw + 0.12)
            _rect(slide, cx, yy, cw, 0.36 + body_h + 0.12, WHITE, line=GREY_LIGHT)
            _rect(slide, cx, yy, cw, 0.05, ORANGE)
            _textbox(slide, cx + 0.1, yy + 0.08, cw - 0.2, 0.3, head, font=F_TITLE, size=10.5 * scale, bold=True, color=INK)
            _textbox(slide, cx + 0.1, yy + 0.38, cw - 0.2, body_h, body, font=F_BODY, size=9.5 * scale, color=INK)
        yy += 0.36 + body_h + 0.16


# ── 슬라이드 종류 ────────────────────────────────────────────────────────────

def _blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def slide_cover(prs, spec: dict) -> None:
    s = _blank(prs)
    _rect(s, 0, 0, SLIDE_W_IN, SLIDE_H_IN, GREY_DARK)                 # 사진 자리 = 진회색 블록
    _rect(s, 0, 0, SLIDE_W_IN, 0.9, "4B4F56")
    _rect(s, 10.6, 0, 1.5, SLIDE_H_IN, ORANGE, shape="para")          # 우측 주황 사선 띠
    _rect(s, 11.9, 0, 1.45, SLIDE_H_IN, WHITE)
    _textbox(s, 0.7, 0.28, 4, 0.4, "Nexus", font=F_TITLE, size=18, bold=True, color=WHITE)
    _textbox(s, 0.7, 2.0, 9.6, 0.5, spec.get("title_en", ""), font=F_SUB, size=16, color=WHITE)
    _textbox(s, 0.7, 2.55, 9.6, 1.9, spec["title_ko"], font=F_MJ_B, size=40, bold=True, color=WHITE, line_spacing=1.1)
    _textbox(s, 0.7, 4.7, 9.6, 0.6, spec.get("subtitle", ""), font=F_SUB, size=15, color=WHITE)
    _textbox(s, 0.7, 6.45, 9.6, 0.4, spec.get("date_line", ""), font=F_SUB, size=11, color=GREY_LIGHT)
    if spec.get("meta"):
        _textbox(s, 0.7, 6.8, 9.6, 0.5, spec["meta"], font=F_SUB, size=9, color=GREY_LIGHT)


def slide_agenda(prs, items: list[str], footer: str) -> None:
    s = _blank(prs)
    _rect(s, 0, 0, 4.4, SLIDE_H_IN, GREY_LIGHT)
    _rect(s, 0, 0, 4.4, 0.9, GREY_DARK)
    _textbox(s, 0.45, 0.26, 3.5, 0.4, "Nexus", font=F_TITLE, size=14, bold=True, color=WHITE)
    _textbox(s, 5.0, 0.7, 7.5, 0.8, "Agenda", font=F_MJ_B, size=30, bold=True, color=INK)
    y = 1.75
    for i, it in enumerate(items, 1):
        _textbox(s, 5.0, y, 0.7, 0.42, f"{i:02d}", font=F_TITLE, size=16, bold=True, color=ORANGE)
        _textbox(s, 5.75, y + 0.02, 6.9, 0.42, it, font=F_TITLE, size=13, bold=True, color=INK)
        _rect(s, 5.0, y + 0.44, 7.6, 0.012, GREY_LIGHT)
        y += 0.56
    _footer(s, footer, 2)


def slide_section(prs, no: str, title: str, sub: str, footer: str, page: int) -> None:
    s = _blank(prs)
    _rect(s, 0, 0, SLIDE_W_IN, 4.9, GREY_DARK)
    _rect(s, 0, 4.9, SLIDE_W_IN, 0.06, ORANGE)
    _textbox(s, 0.7, 3.7, 3, 0.8, no, font=F_TITLE, size=44, bold=True, color=ORANGE)
    _textbox(s, 0.7, 5.2, 11.5, 0.8, title, font=F_MJ_B, size=28, bold=True, color=INK)
    _textbox(s, 0.7, 6.0, 11.5, 0.6, sub, font=F_SUB, size=13, color=INK_SOFT)
    _footer(s, footer, page)


def _footer(s, footer: str, page: int, source: str | None = None) -> None:
    _rect(s, BODY_LEFT, 6.98, SLIDE_W_IN - 2 * BODY_LEFT, 0.012, GREY_LIGHT)
    if source:
        _textbox(s, BODY_LEFT, 7.02, 8.6, 0.38, source, font=F_SUB, size=8, color=INK_SOFT)
    _textbox(s, 9.2, 7.05, 3.0, 0.3, footer, font=F_SUB, size=8, color=INK_SOFT, align="r")
    _textbox(s, 12.25, 7.05, 0.55, 0.3, str(page), font=F_TITLE, size=9, bold=True, color=ORANGE, align="r")


def slide_content(prs, spec: dict, footer: str, page: int) -> list[str]:
    """본문 슬라이드. 반환: 경고 목록(넘침 등)."""
    warns: list[str] = []
    s = _blank(prs)
    _textbox(s, BODY_LEFT, 0.28, 9, 0.3, spec.get("path", ""), font=F_SUB, size=10, color=INK_SOFT)
    _textbox(s, BODY_LEFT, 0.55, SLIDE_W_IN - 2 * BODY_LEFT, 0.88, spec["title"], font=F_MJ_B, size=18, bold=True,
             color=INK, line_spacing=1.1)
    _rect(s, BODY_LEFT, 1.45, 0.9, 0.04, ORANGE)
    cols = spec.get("cols")
    blocks = spec.get("blocks")
    avail_h = BODY_BOTTOM - BODY_TOP
    full_w = BODY_RIGHT - BODY_LEFT
    # 자동 축소: 11pt → 8.5pt까지 단계적으로 줄여 넘침 방지
    for scale in (1.0, 0.94, 0.88, 0.82, 0.77):
        if cols:
            weights = spec.get("weights") or [1] * len(cols)
            gap = 0.3
            widths = [(full_w - gap * (len(cols) - 1)) * wt / sum(weights) for wt in weights]
            heights = [sum(_est_block_h(b, cw, scale) + 0.1 for b in col) for col, cw in zip(cols, widths)]
            if max(heights) <= avail_h:
                break
        else:
            hsum = sum(_est_block_h(b, full_w, scale) + 0.1 for b in (blocks or []))
            if hsum <= avail_h:
                break
    else:
        warns.append(f"p{page}: 추정 높이 초과(최소 축소 적용) — 검토 필요")
    if cols:
        x = BODY_LEFT
        for col, cw in zip(cols, widths):
            _render_blocks(s, col, x, BODY_TOP, cw, scale, [])
            x += cw + gap
    else:
        _render_blocks(s, blocks or [], BODY_LEFT, BODY_TOP, full_w, scale, [])
    _footer(s, footer, page, spec.get("source"))
    return warns


def build_pptx(deck: dict, out_path: Path) -> list[str]:
    Presentation, Inches, *_ = _pptx()
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W_IN)
    prs.slide_height = Inches(SLIDE_H_IN)
    footer = deck["footer"]
    warns: list[str] = []
    page = 1
    slide_cover(prs, deck["cover"])
    page += 1
    slide_agenda(prs, deck["agenda"], footer)
    page += 1
    for item in deck["slides"]:
        if item["kind"] == "section":
            slide_section(prs, item["no"], item["title"], item.get("sub", ""), footer, page)
        else:
            warns += slide_content(prs, item, footer, page)
        page += 1
    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out_path))
    return warns


# ── md 파싱(docx·xlsx 원천) ───────────────────────────────────────────────────

_MD_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}")


def _strip_md(text: str) -> str:
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    t = re.sub(r"`([^`]*)`", r"\1", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = re.sub(r"(?<!\*)\*(?!\*)([^*]+)\*(?!\*)", r"\1", t)
    return t.replace("\\|", "|").strip()


def parse_md(path: Path) -> list[tuple]:
    """md → [('title', text) | ('h', level, text) | ('p', text) | ('quote', text) | ('b', [items]) | ('t', rows) | ('code', text)]."""
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[tuple] = []
    i = 0
    para: list[str] = []
    bullets: list[str] = []
    quote: list[str] = []

    def flush() -> None:
        nonlocal para, bullets, quote
        if para:
            out.append(("p", _strip_md(" ".join(para))))
            para = []
        if bullets:
            out.append(("b", [_strip_md(b) for b in bullets]))
            bullets = []
        if quote:
            out.append(("quote", _strip_md(" ".join(quote))))
            quote = []

    while i < len(lines):
        ln = lines[i]
        st = ln.strip()
        if st.startswith("```"):
            flush()
            j = i + 1
            code = []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                code.append(lines[j])
                j += 1
            out.append(("code", "\n".join(code)))
            i = j + 1
            continue
        if st.startswith("|") and i + 1 < len(lines) and _MD_TABLE_SEP.match(lines[i + 1]):
            flush()
            rows = []
            j = i
            while j < len(lines) and lines[j].strip().startswith("|"):
                if not _MD_TABLE_SEP.match(lines[j]):
                    cells = [_strip_md(c) for c in re.split(r"(?<!\\)\|", lines[j].strip().strip("|"))]
                    rows.append(cells)
                j += 1
            out.append(("t", rows))
            i = j
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", st)
        if m:
            flush()
            lvl = len(m.group(1))
            if lvl == 1:
                out.append(("title", _strip_md(m.group(2))))
            else:
                out.append(("h", lvl - 1, _strip_md(m.group(2))))
            i += 1
            continue
        if st.startswith(">"):
            if para or bullets:
                flush()
            quote.append(st.lstrip("> ").strip())
            i += 1
            continue
        if re.match(r"^[-*]\s+", st) or re.match(r"^\d+\.\s+", st):
            if para or quote:
                flush()
            bullets.append(re.sub(r"^([-*]|\d+\.)\s+", "", st))
            i += 1
            continue
        if st in ("", "---"):
            flush()
            i += 1
            continue
        if bullets or quote:
            flush()
        para.append(st)
        i += 1
    flush()
    return out


def tables_by_heading(nodes: list[tuple], heading_startswith: str) -> list[list[list[str]]]:
    """지정 제목 아래(다음 같은 급 제목 전) 표들."""
    found: list[list[list[str]]] = []
    active = False
    level = 0
    for n in nodes:
        if n[0] == "h":
            if n[2].startswith(heading_startswith):
                active, level = True, n[1]
                continue
            if active and n[1] <= level:
                active = False
        elif active and n[0] == "t":
            found.append(n[1])
    return found


# ── docx ─────────────────────────────────────────────────────────────────────

def _docx_font(run, name: str, size_pt: float, bold=False, color: str = INK) -> None:
    from docx.shared import Pt, RGBColor
    from docx.oxml.ns import qn
    run.font.name = name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), name)


def _docx_shade(cell, hexs: str) -> None:
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    tcpr = cell._element.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexs)
    tcpr.append(shd)


def build_docx(md_path: Path, out_path: Path, meta: dict) -> None:
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    nodes = parse_md(md_path)
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.27), Inches(11.69)      # A4
    sec.left_margin = sec.right_margin = Inches(0.85)
    sec.top_margin, sec.bottom_margin = Inches(0.9), Inches(0.8)
    # 기본 스타일 폰트
    st = doc.styles["Normal"]
    st.font.name = F_BODY
    st.element.rPr.rFonts.set(qn("w:eastAsia"), F_BODY)
    st.font.size = Pt(10.5)

    # 머리말·꼬리말
    hdr = sec.header.paragraphs[0]
    hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = hdr.add_run(meta["header"])
    _docx_font(r, F_SUB, 8, color=INK_SOFT)
    ftr = sec.footer.paragraphs[0]
    ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = ftr.add_run(meta["footer"] + "  |  ")
    _docx_font(r, F_SUB, 8, color=INK_SOFT)
    # 쪽번호 필드
    run = ftr.add_run()
    for tag, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        if tag:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), tag)
            run._r.append(el)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = txt
            run._r.append(el)
    _docx_font(run, F_SUB, 8, color=INK_SOFT)

    # 표지
    def add_par(text, font, size, bold=False, color=INK, align="l", space_after=6, space_before=0):
        p = doc.add_paragraph()
        p.alignment = {"l": WD_ALIGN_PARAGRAPH.LEFT, "c": WD_ALIGN_PARAGRAPH.CENTER}[align]
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.space_before = Pt(space_before)
        rr = p.add_run(text)
        _docx_font(rr, font, size, bold, color)
        return p

    # 표지 상단 주황 띠(1행 표로 대체)
    band = doc.add_table(rows=1, cols=1)
    band.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = band.cell(0, 0)
    _docx_shade(c, ORANGE)
    c.paragraphs[0].add_run(" ")
    add_par("Nexus", F_TITLE, 14, True, INK_SOFT, space_before=24)
    add_par(meta["doc_no"], F_SUB, 10, color=INK_SOFT)
    title = next((n[1] for n in nodes if n[0] == "title"), meta["title"])
    add_par(title, F_TITLE, 22, True, INK, space_before=12, space_after=10)
    add_par(meta["subtitle"], F_SUB, 12, color=INK_SOFT, space_after=4)
    add_par(meta["date_line"], F_SUB, 10, color=INK_SOFT, space_after=30)
    doc.add_page_break()

    # 본문
    hcount = [0, 0, 0]
    for n in nodes:
        kind = n[0]
        if kind == "title":
            continue
        if kind == "h":
            lvl, text = n[1], n[2]
            if lvl == 1:
                hcount[0] += 1
                hcount[1] = 0
                text = re.sub(r"^\d+\.\s*", "", text)          # md 자체 번호(예: '1. ')는 자동 번호와 중복이라 제거
                p = add_par("", F_TITLE, 14, True, INK, space_before=16, space_after=6)
                rr = p.add_run(f"{hcount[0]:02d}  ")
                _docx_font(rr, F_TITLE, 14, True, ORANGE)
                rr = p.add_run(text)
                _docx_font(rr, F_TITLE, 14, True, INK)
                # 밑줄(경계선)
                pPr = p._p.get_or_add_pPr()
                pbdr = OxmlElement("w:pBdr")
                bottom = OxmlElement("w:bottom")
                bottom.set(qn("w:val"), "single"); bottom.set(qn("w:sz"), "6")
                bottom.set(qn("w:space"), "1"); bottom.set(qn("w:color"), GREY_LIGHT)
                pbdr.append(bottom); pPr.append(pbdr)
            elif lvl == 2:
                add_par(text, F_TITLE, 12, True, INK, space_before=10, space_after=4)
            else:
                add_par(text, F_SUB, 11, True, INK, space_before=6, space_after=3)
        elif kind == "p":
            add_par(n[1], F_BODY, 10.5, space_after=6)
        elif kind == "quote":
            t = doc.add_table(rows=1, cols=1)
            t.alignment = WD_TABLE_ALIGNMENT.CENTER
            cell = t.cell(0, 0)
            _docx_shade(cell, ORANGE_SOFT)
            pp = cell.paragraphs[0]
            rr = pp.add_run(n[1])
            _docx_font(rr, F_BODY, 9.5, color=INK)
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
        elif kind == "b":
            for item in n[1]:
                p = doc.add_paragraph(style="List Bullet")
                p.paragraph_format.space_after = Pt(2)
                rr = p.add_run(item)
                _docx_font(rr, F_BODY, 10.5)
        elif kind == "code":
            p = add_par(n[1], F_SUB, 9, color=INK_SOFT, space_after=6)
        elif kind == "t":
            rows = n[1]
            ncol = max(len(r) for r in rows)
            t = doc.add_table(rows=len(rows), cols=ncol)
            t.style = "Table Grid"
            t.alignment = WD_TABLE_ALIGNMENT.CENTER
            for i, row in enumerate(rows):
                for j in range(ncol):
                    cell = t.cell(i, j)
                    txt = row[j] if j < len(row) else ""
                    cell.paragraphs[0].paragraph_format.space_after = Pt(0)
                    rr = cell.paragraphs[0].add_run(txt)
                    if i == 0:
                        _docx_shade(cell, GREY_DARK)
                        _docx_font(rr, F_TITLE, 8.5, True, WHITE)
                    else:
                        _docx_font(rr, F_BODY if j else F_SUB, 8.5, bold=(j == 0), color=INK)
                        if i % 2 == 0:
                            _docx_shade(cell, "F6F7F8")
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))


# ── xlsx ─────────────────────────────────────────────────────────────────────

def build_xlsx(md_path: Path, out_path: Path, sheets: list[tuple[str, str, int]]) -> list[str]:
    """sheets: (시트명, md 제목 접두, 그 제목 아래 몇 번째 표). 반환: 누락 경고."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    nodes = parse_md(md_path)
    wb = Workbook()
    wb.remove(wb.active)
    warns: list[str] = []
    thin = Side(style="thin", color=GREY_LIGHT)
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    for sheet_name, heading, idx in sheets:
        tabs = tables_by_heading(nodes, heading)
        if len(tabs) <= idx:
            warns.append(f"xlsx: '{heading}' 아래 표 {idx + 1}번 없음 — 시트 '{sheet_name}' 생략")
            continue
        rows = tabs[idx]
        ws = wb.create_sheet(sheet_name)
        ws.sheet_view.showGridLines = False
        ws.append([f"Nexus 인수인계 — {sheet_name}"])
        ws["A1"].font = Font(name=F_TITLE, size=13, bold=True, color=INK)
        ws.append([f"원천: {md_path.name} · '{heading}' · 생성 {TODAY} · 사내 한정"])
        ws["A2"].font = Font(name=F_SUB, size=9, color=INK_SOFT)
        ws.append([])
        for i, row in enumerate(rows):
            ws.append(row)
            r_idx = ws.max_row
            for j in range(1, len(row) + 1):
                cell = ws.cell(row=r_idx, column=j)
                cell.border = border
                cell.alignment = Alignment(wrap_text=True, vertical="top" if i else "center")
                if i == 0:
                    cell.font = Font(name=F_TITLE, size=11, bold=True, color=WHITE)
                    cell.fill = PatternFill("solid", fgColor=GREY_DARK)
                else:
                    cell.font = Font(name=F_SUB if j == 1 else F_BODY, size=10, bold=(j == 1), color=INK)
                    if i % 2 == 0:
                        cell.fill = PatternFill("solid", fgColor="F6F7F8")
        ncol = max(len(r) for r in rows)
        for j in range(1, ncol + 1):
            longest = max(len(str(r[j - 1])) if j - 1 < len(r) else 0 for r in rows)
            ws.column_dimensions[get_column_letter(j)].width = max(10, min(60, longest * 1.1 + 2))
        ws.freeze_panes = "A5"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(str(out_path))
    return warns


# ── 금지어 검사(기밀·코드 주어·조정자 표기) ─────────────────────────────────

_FORBIDDEN = [r"조정자", r"\b(?:A|CE|DQ|D|M|V|R|C|P1)-\d{1,3}\b", r"퇴사", r"인수인계 기간", r"휴가",
              r"Azure|AWS|S3|Snowflake|EC2|ADLS", r"\bAPI[_ ]KEY\b", r"password", r"secret"]


def sweep_texts(texts: list[str]) -> list[str]:
    hits: list[str] = []
    for t in texts:
        for pat in _FORBIDDEN:
            for m in re.finditer(pat, t):
                ctx = t[max(0, m.start() - 25): m.end() + 25].replace("\n", " ")
                hits.append(f"{pat} … {ctx}")
    return hits


def deck_texts(deck: dict) -> list[str]:
    out = [str(v) for v in deck["cover"].values()] + list(deck["agenda"])
    for s in deck["slides"]:
        for k, v in s.items():
            if isinstance(v, str):
                out.append(v)
        for col in (s.get("cols") or [s.get("blocks") or []]):
            for b in col:
                if b[0] in ("h", "p", "panel"):
                    out.append(b[1])
                elif b[0] == "b":
                    out += b[1]
                elif b[0] == "t":
                    out += [c for row in b[1] for c in row]
                elif b[0] in ("kpi", "steps", "cards"):
                    out += [x for pair in b[1] for x in pair]
                elif b[0] == "num":
                    out += [str(x) for tri in b[1] for x in tri]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["pptx", "docx", "xlsx"], default=None)
    ap.add_argument("--out", default=str(ROOT / "docs/handover"))
    args = ap.parse_args()
    out = Path(args.out)
    import handover_content as hc
    warns: list[str] = []
    md = ROOT / "docs/handover/05_PoC_범위_정의서.md"
    if args.only in (None, "pptx"):
        for deck, name in ((hc.DECK_REPORT, "Nexus_인수인계_보고_2026_09.pptx"),
                           (hc.DECK_POC, "05_PoC_범위_정의서_요약.pptx")):
            hits = sweep_texts(deck_texts(deck))
            if hits:
                print(f"[오류] 금지어·기밀 표기 발견({name}):")
                for h in hits:
                    print("   -", h)
                return 1
            w = build_pptx(deck, out / name)
            warns += w
            print(f"[완료] {name} — {len(deck['slides']) + 2}장")
    if args.only in (None, "docx"):
        build_docx(md, out / "05_PoC_범위_정의서.docx", hc.DOCX_META)
        print("[완료] 05_PoC_범위_정의서.docx")
    if args.only in (None, "xlsx"):
        warns += build_xlsx(md, out / "05_PoC_데이터_자산_목록.xlsx", hc.XLSX_SHEETS)
        print("[완료] 05_PoC_데이터_자산_목록.xlsx")
    for w in warns:
        print("[경고]", w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
