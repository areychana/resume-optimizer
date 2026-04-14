"""
Input sanitization for resume and job description text.
Cleans messy input before sending to Claude to save tokens and improve accuracy.
"""

import re
import unicodedata


def sanitize(text: str) -> str:
    """
    Clean raw text from paste or PDF extraction before sending to Claude.

    Steps:
    - Normalize unicode (NFKC) to fix ligatures and special chars
    - Replace common non-ASCII quotes/dashes with ASCII equivalents
    - Strip null bytes and other control characters (except newlines/tabs)
    - Collapse runs of more than 2 consecutive blank lines into one
    - Strip trailing whitespace from each line
    - Strip leading/trailing whitespace from the full text

    Args:
        text: Raw input text from user paste or PDF extraction.

    Returns:
        Cleaned text string.
    """
    if not text:
        return ""

    # Unicode normalization: fixes ligatures (ﬁ -> fi), weird spaces, etc.
    text = unicodedata.normalize("NFKC", text)

    # Common encoding artifacts
    replacements = {
        "\u2018": "'", "\u2019": "'",   # curly single quotes
        "\u201c": '"', "\u201d": '"',   # curly double quotes
        "\u2013": "-", "\u2014": "-",   # en dash, em dash
        "\u2022": "-",                  # bullet •
        "\u00a0": " ",                  # non-breaking space
        "\u200b": "",                   # zero-width space
        "\ufeff": "",                   # BOM
        "\u2026": "...",               # ellipsis
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)

    # Strip control characters except newline (\n), carriage return (\r), tab (\t)
    text = re.sub(r"[^\S\n\r\t ]+", " ", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Strip trailing whitespace per line
    lines = [line.rstrip() for line in text.split("\n")]

    # Collapse more than 2 consecutive blank lines into 1
    cleaned = []
    blank_count = 0
    for line in lines:
        if line == "":
            blank_count += 1
            if blank_count <= 2:
                cleaned.append(line)
        else:
            blank_count = 0
            cleaned.append(line)

    return "\n".join(cleaned).strip()


def extract_pdf_text(file_bytes: bytes) -> str:
    """
    Extract plain text from a PDF file using pdfplumber.
    Handles multi-column layouts and tables better than basic parsers.

    Args:
        file_bytes: Raw bytes of the PDF file.

    Returns:
        Extracted and sanitized text string.

    Raises:
        ImportError: If pdfplumber is not installed.
        ValueError: If no text could be extracted from the PDF.
    """
    try:
        import pdfplumber
        import io
    except ImportError as e:
        raise ImportError(
            "pdfplumber is required for PDF parsing. "
            "Install it with: pip install pdfplumber"
        ) from e

    import io
    text_parts = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(x_tolerance=2, y_tolerance=2)
            if page_text:
                text_parts.append(page_text)

    if not text_parts:
        raise ValueError(
            "Could not extract text from this PDF. "
            "It may be scanned or image-based. Please paste the text manually."
        )

    raw = "\n\n".join(text_parts)
    return sanitize(raw)
