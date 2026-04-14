"""
Tests for pdf_builder.py: markdown parsing and PDF generation.
Requires fpdf2: pip install fpdf2
"""

import os
import tempfile
import pytest

fpdf2 = pytest.importorskip("fpdf", reason="fpdf2 not installed")

from pdf_builder import build_pdf


SAMPLE_RESUME = """\
# Jane Doe
jane@example.com | github.com/janedoe

## Summary
Backend engineer with 3 years of experience in Python and FastAPI.

## Experience

### Senior Software Engineer - Acme Corp
Jan 2022 - Present

- Led migration of monolith to microservices, reducing latency by 40%
- Designed REST APIs serving 2M+ requests/day

### Software Engineer - Beta Inc
Jun 2020 - Dec 2021

- Built data pipelines using Apache Kafka and Python

## Skills
Python, FastAPI, Docker, Kubernetes, PostgreSQL, Redis

---

## Education
B.Tech Computer Science - IIT Delhi, 2020
"""


def test_build_pdf_creates_file():
    path = build_pdf(SAMPLE_RESUME)
    assert os.path.exists(path)
    assert path.endswith(".pdf")


def test_build_pdf_nonzero_size():
    path = build_pdf(SAMPLE_RESUME)
    assert os.path.getsize(path) > 1000  # at least 1 KB


def test_build_pdf_custom_output_path():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name
    path = build_pdf(SAMPLE_RESUME, output_path=tmp_path)
    assert path == tmp_path
    assert os.path.exists(path)


def test_build_pdf_handles_minimal_resume():
    minimal = "# John Smith\n\n## Experience\n\nNo experience listed.\n"
    path = build_pdf(minimal)
    assert os.path.exists(path)


def test_build_pdf_handles_special_chars():
    resume_with_special = SAMPLE_RESUME + "\n## Notes\nAmpersand & test\n"
    path = build_pdf(resume_with_special)
    assert os.path.exists(path)
