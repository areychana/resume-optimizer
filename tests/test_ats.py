"""
Tests for ATS scoring: Pydantic validation, fallback scoring, and model shape.
"""

import pytest
from models import ATSReport, Dimension, KeywordCategory, Suggestion
from pydantic import ValidationError


VALID_PAYLOAD = {
    "overall_score": 72,
    "dimensions": {
        "keyword_match": 80,
        "experience_level": 65,
        "skills_coverage": 70,
        "role_title_alignment": 75,
    },
    "technical_skills": {"matched": ["Python", "FastAPI"], "missing": ["Kubernetes"]},
    "tools_and_frameworks": {"matched": ["Docker"], "missing": []},
    "soft_skills": {"matched": ["communication"], "missing": []},
    "suggestions": [
        {"gap": "Kubernetes", "action": "Add a project using K8s to your experience."}
    ],
    "verdict": "Good match overall.",
}


def test_ats_report_valid():
    report = ATSReport(**VALID_PAYLOAD)
    assert report.overall_score == 72
    assert report.dimensions.keyword_match == 80
    assert "Python" in report.technical_skills.matched


def test_ats_report_to_dict():
    report = ATSReport(**VALID_PAYLOAD)
    d = report.to_dict()
    assert isinstance(d, dict)
    assert d["overall_score"] == 72
    assert isinstance(d["suggestions"], list)


def test_ats_report_clamps_score():
    payload = VALID_PAYLOAD.copy()
    payload["overall_score"] = 150
    report = ATSReport(**payload)
    assert report.overall_score == 100

    payload["overall_score"] = -10
    report = ATSReport(**payload)
    assert report.overall_score == 0


def test_ats_report_missing_required_field():
    payload = VALID_PAYLOAD.copy()
    del payload["overall_score"]
    with pytest.raises(ValidationError):
        ATSReport(**payload)


def test_ats_report_score_out_of_range_field_validator():
    payload = VALID_PAYLOAD.copy()
    payload["dimensions"]["keyword_match"] = 110
    with pytest.raises(ValidationError):
        ATSReport(**payload)


def test_ats_report_defaults_empty_categories():
    payload = {
        "overall_score": 50,
        "dimensions": {
            "keyword_match": 50,
            "experience_level": 50,
            "skills_coverage": 50,
            "role_title_alignment": 50,
        },
    }
    report = ATSReport(**payload)
    assert report.technical_skills.matched == []
    assert report.suggestions == []
    assert report.verdict == ""


def test_fallback_score_shape():
    anthropic = pytest.importorskip("anthropic", reason="anthropic not installed")
    from ats import _fallback_score
    result = _fallback_score("Python developer with FastAPI experience", "Looking for a Python FastAPI engineer")
    assert "overall_score" in result
    assert "dimensions" in result
    assert result.get("_fallback") is True
    assert 0 <= result["overall_score"] <= 100
