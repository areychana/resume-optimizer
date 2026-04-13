"""
PDF generation module. Converts Markdown resume text to a styled PDF
using xhtml2pdf. Pure Python, no system dependencies, works on Windows.
"""

import os
import tempfile
import markdown as md_lib


# Embedded CSS for the PDF: clean, ATS-safe, single-column layout
_PDF_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: Helvetica, Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #1a1a1a;
    padding: 36pt 48pt;
}

h1 {
    font-size: 20pt;
    font-weight: bold;
    color: #111827;
    margin-bottom: 4pt;
    border-bottom: 1pt solid #4F46E5;
    padding-bottom: 4pt;
}

h2 {
    font-size: 12pt;
    font-weight: bold;
    color: #4F46E5;
    margin-top: 14pt;
    margin-bottom: 4pt;
    text-transform: uppercase;
}

h3 {
    font-size: 11pt;
    font-weight: bold;
    color: #111827;
    margin-top: 8pt;
    margin-bottom: 2pt;
}

p {
    margin-bottom: 5pt;
    color: #374151;
}

ul {
    margin-left: 14pt;
    margin-bottom: 5pt;
}

li {
    margin-bottom: 2pt;
    color: #374151;
}

strong {
    font-weight: bold;
    color: #111827;
}

a {
    color: #4F46E5;
}

hr {
    border-top: 1pt solid #e5e7eb;
    margin: 8pt 0;
}

code {
    font-family: Courier, monospace;
    font-size: 9.5pt;
    background: #f3f4f6;
    padding: 1pt 3pt;
}
"""


def build_pdf(md_text: str, output_path: str | None = None) -> str:
    """
    Convert a Markdown resume to a styled PDF file using xhtml2pdf.

    Args:
        md_text: Resume content in Markdown format.
        output_path: Optional file path for the output PDF.
            Defaults to a temp file.

    Returns:
        Absolute path to the generated PDF file.

    Raises:
        ImportError: If xhtml2pdf is not installed.
        RuntimeError: If xhtml2pdf reports a conversion error.
    """
    try:
        from xhtml2pdf import pisa
    except ImportError as e:
        raise ImportError(
            "xhtml2pdf is required for PDF generation. "
            "Install it with: pip install xhtml2pdf"
        ) from e

    body_html = md_lib.markdown(md_text, extensions=["extra", "nl2br"])
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <style>{_PDF_CSS}</style>
</head>
<body>
{body_html}
</body>
</html>"""

    if output_path is None:
        output_path = tempfile.mktemp(suffix=".pdf", prefix="resume_")

    with open(output_path, "wb") as f:
        result = pisa.CreatePDF(full_html.encode("utf-8"), dest=f, encoding="utf-8")

    if result.err:
        raise RuntimeError(f"PDF conversion failed with {result.err} error(s).")

    return os.path.abspath(output_path)
