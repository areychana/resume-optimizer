"""
PDF generation module. Converts Markdown resume text to a styled PDF
using fpdf2. Pure Python, zero system dependencies, works everywhere.
"""

import os
import re
import tempfile


def _strip_inline(text: str) -> str:
    """Remove bold/italic markdown markers from a line of text."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    return text.strip()


def build_pdf(md_text: str, output_path: str | None = None) -> str:
    """
    Convert a Markdown resume to a styled PDF file using fpdf2.

    Handles headings (h1/h2/h3), bullet points, horizontal rules,
    and paragraphs. Inline bold/italic markers are stripped cleanly.

    Args:
        md_text: Resume content in Markdown format.
        output_path: Optional file path for the output PDF.
            Defaults to a temp file.

    Returns:
        Absolute path to the generated PDF file.

    Raises:
        ImportError: If fpdf2 is not installed.
    """
    try:
        from fpdf import FPDF
    except ImportError as e:
        raise ImportError(
            "fpdf2 is required for PDF generation. "
            "Install it with: pip install fpdf2"
        ) from e

    pdf = FPDF(format="A4")
    pdf.set_margins(18, 18, 18)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=18)

    page_w = pdf.w - pdf.l_margin - pdf.r_margin

    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        i += 1

        # Skip fenced code blocks
        if raw.strip().startswith("```"):
            while i < len(lines) and not lines[i].strip().startswith("```"):
                i += 1
            i += 1
            continue

        # H1
        if raw.startswith("# "):
            text = _strip_inline(raw[2:])
            pdf.set_font("Helvetica", "B", 18)
            pdf.set_text_color(17, 24, 39)
            pdf.multi_cell(page_w, 8, text)
            # Underline via line
            pdf.set_draw_color(79, 70, 229)
            pdf.set_line_width(0.5)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + page_w, pdf.get_y())
            pdf.ln(3)
            continue

        # H2
        if raw.startswith("## "):
            text = _strip_inline(raw[3:]).upper()
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(79, 70, 229)
            pdf.ln(3)
            pdf.multi_cell(page_w, 6, text)
            pdf.set_draw_color(229, 231, 235)
            pdf.set_line_width(0.3)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + page_w, pdf.get_y())
            pdf.ln(2)
            continue

        # H3
        if raw.startswith("### "):
            text = _strip_inline(raw[4:])
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(17, 24, 39)
            pdf.ln(2)
            pdf.multi_cell(page_w, 5, text)
            continue

        # Horizontal rule
        if raw.strip() in ("---", "***", "___"):
            pdf.set_draw_color(229, 231, 235)
            pdf.set_line_width(0.3)
            pdf.line(pdf.l_margin, pdf.get_y() + 1, pdf.l_margin + page_w, pdf.get_y() + 1)
            pdf.ln(3)
            continue

        # Bullet point
        if raw.strip().startswith(("- ", "* ", "+ ")):
            text = _strip_inline(raw.strip()[2:])
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(55, 65, 81)
            x = pdf.get_x()
            y = pdf.get_y()
            # bullet dot
            pdf.set_xy(pdf.l_margin + 2, y)
            pdf.cell(4, 5, chr(149))
            pdf.set_xy(pdf.l_margin + 7, y)
            pdf.multi_cell(page_w - 7, 5, text)
            continue

        # Blank line
        if not raw.strip():
            pdf.ln(2)
            continue

        # Regular paragraph
        text = _strip_inline(raw)
        if text:
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(55, 65, 81)
            pdf.multi_cell(page_w, 5, text)

    if output_path is None:
        output_path = tempfile.mktemp(suffix=".pdf", prefix="resume_")

    pdf.output(output_path)
    return os.path.abspath(output_path)
