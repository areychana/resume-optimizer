"""
Tests for utils/sanitize.py: input cleaning and PDF extraction.
"""

import pytest
from utils.sanitize import sanitize


def test_sanitize_empty():
    assert sanitize("") == ""
    assert sanitize(None) == ""


def test_sanitize_strips_curly_quotes():
    result = sanitize("\u201cHello\u201d and \u2018world\u2019")
    assert '"Hello"' in result
    assert "'world'" in result


def test_sanitize_replaces_em_dash():
    result = sanitize("senior \u2014 engineer")
    assert "-" in result
    assert "\u2014" not in result


def test_sanitize_collapses_blank_lines():
    text = "line1\n\n\n\n\nline2"
    result = sanitize(text)
    # sanitize allows up to 2 consecutive blank lines; 3+ in a row is collapsed
    assert "\n\n\n\n" not in result


def test_sanitize_strips_trailing_whitespace():
    result = sanitize("hello   \nworld   ")
    for line in result.splitlines():
        assert line == line.rstrip()


def test_sanitize_normalizes_line_endings():
    result = sanitize("line1\r\nline2\rline3")
    assert "\r" not in result


def test_sanitize_removes_zero_width_space():
    result = sanitize("hello\u200bworld")
    assert "\u200b" not in result


def test_sanitize_strips_bom():
    result = sanitize("\ufeffcontent")
    assert result == "content"


def test_sanitize_strips_null_bytes():
    result = sanitize("hello\x00world")
    assert "\x00" not in result


def test_sanitize_strips_outer_whitespace():
    result = sanitize("   hello world   ")
    assert result == "hello world"
