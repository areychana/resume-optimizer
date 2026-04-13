"""
ATS scoring module. Uses Claude to perform multi-dimensional analysis of
how well a resume matches a job description, with keyword categorization
and actionable gap recommendations.
"""

import json
import os
import re
import anthropic
from dotenv import load_dotenv
from prompt import ATS_ANALYSIS_PROMPT
from utils.cost import calculate_cost

load_dotenv()

MODEL = "claude-sonnet-4-5"

# Common English stopwords to filter from naive keyword extraction fallback
_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "must", "we", "you",
    "they", "he", "she", "it", "this", "that", "these", "those", "as",
    "if", "than", "then", "so", "yet", "both", "either", "not", "no",
    "our", "your", "their", "its", "my", "his", "her", "also", "into",
    "about", "through", "during", "before", "after", "above", "below",
    "up", "down", "out", "off", "over", "under", "again", "further",
    "once", "what", "which", "who", "whom", "when", "where", "why", "how",
    "all", "each", "every", "some", "any", "few", "more", "most", "other",
    "such", "only", "own", "same", "too", "very", "just", "because",
    "while", "although", "since", "unless", "until", "whether", "both",
    "role", "work", "team", "company", "experience", "strong", "good",
    "well", "new", "use", "using", "used", "working", "job", "position",
}


def _get_client() -> anthropic.Anthropic:
    """Instantiate the Anthropic client from env or Streamlit secrets."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("ANTHROPIC_API_KEY")
        except Exception:
            pass
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not found. Set it in .env or Streamlit secrets."
        )
    return anthropic.Anthropic(api_key=api_key)


def _fallback_score(resume: str, job_desc: str) -> dict:
    """
    Simple keyword-overlap fallback used only when the Claude call fails.
    Filters stopwords and focuses on tokens of 3+ characters.

    Args:
        resume: Resume text.
        job_desc: Job description text.

    Returns:
        Minimal ATS report dict compatible with the full Claude report shape.
    """
    def extract(text: str) -> set:
        tokens = set(re.findall(r"[a-zA-Z0-9#+.]{3,}", text.lower()))
        return tokens - _STOPWORDS

    job_words = extract(job_desc)
    resume_words = extract(resume)
    if not job_words:
        return {"overall_score": 0, "error": "Could not extract keywords from JD."}

    matched = job_words & resume_words
    missing = job_words - resume_words
    score = int(len(matched) / len(job_words) * 100)

    return {
        "overall_score": score,
        "dimensions": {
            "keyword_match": score,
            "experience_level": 0,
            "skills_coverage": score,
            "role_title_alignment": 0,
        },
        "technical_skills": {"matched": list(matched)[:15], "missing": list(missing)[:15]},
        "tools_and_frameworks": {"matched": [], "missing": []},
        "soft_skills": {"matched": [], "missing": []},
        "suggestions": [
            {"gap": kw, "action": f"Add '{kw}' to your resume where relevant."}
            for kw in list(missing)[:5]
        ],
        "verdict": f"Fallback scoring: {score}% keyword overlap (Claude unavailable).",
        "_fallback": True,
    }


def score_resume(resume: str, job_description: str) -> tuple[dict, dict]:
    """
    Run ATS analysis on the resume against the job description using Claude.

    Sends the ATS_ANALYSIS_PROMPT to Claude and parses the returned JSON.
    Falls back to simple keyword overlap if the Claude call or JSON parse fails.

    Args:
        resume: Resume text (Markdown or plain text).
        job_description: Job description text.

    Returns:
        Tuple of (ats_report_dict, usage_dict).
        ats_report_dict keys: overall_score, dimensions, technical_skills,
            tools_and_frameworks, soft_skills, suggestions, verdict.
    """
    client = _get_client()
    prompt = ATS_ANALYSIS_PROMPT.format(
        resume=resume,
        job_description=job_description,
    )
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        # Strip accidental markdown code fences if Claude adds them
        if raw.startswith("```"):
            raw = re.sub(r"^```[a-z]*\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)
        report = json.loads(raw)
        usage = calculate_cost(
            MODEL,
            response.usage.input_tokens,
            response.usage.output_tokens,
        )
        return report, usage
    except (json.JSONDecodeError, anthropic.APIError, Exception):
        report = _fallback_score(resume, job_description)
        usage = calculate_cost(MODEL, 0, 0)
        return report, usage
