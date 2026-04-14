"""
Resume optimization module. Uses Claude to rewrite a resume for a specific
job description with ATS-focused improvements and streaming output.
"""

import json
import os
import re
import anthropic
from dotenv import load_dotenv
from prompt import (
    OPTIMIZER_PROMPT,
    DIFF_EXPLANATION_PROMPT,
    STAR_REWRITE_PROMPT,
    HALLUCINATION_CHECK_PROMPT,
)
from utils.cost import calculate_cost
from utils.logger import get_logger, log_call, log_usage

load_dotenv()

MODEL = "claude-sonnet-4-5"
logger = get_logger("optimizer")

# Patterns that indicate weak, passive bullet points
_WEAK_PATTERNS = re.compile(
    r"^[\-\*\•]?\s*(responsible for|worked on|helped with|assisted in|"
    r"involved in|contributed to|participated in|tasked with|in charge of)",
    re.IGNORECASE | re.MULTILINE,
)


def _get_client() -> anthropic.Anthropic:
    """Instantiate the Anthropic client.

    Priority: user-provided key in session_state > .env > Streamlit secrets.
    """
    api_key = None
    try:
        import streamlit as st
        api_key = st.session_state.get("api_key") or st.secrets.get("ANTHROPIC_API_KEY")
    except Exception:
        pass
    api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "No API key found. Enter your Anthropic API key in the sidebar."
        )
    return anthropic.Anthropic(api_key=api_key)


def optimize_resume(resume_text: str, job_description: str):
    """
    Stream an ATS-optimized rewrite of the resume for the given job description.

    Args:
        resume_text: The candidate's original resume in Markdown.
        job_description: The full job description text.

    Yields:
        str: Successive text chunks from the Claude stream.

    After the stream is exhausted, usage stats are stored on the function
    as optimize_resume._last_usage.
    """
    client = _get_client()
    prompt = OPTIMIZER_PROMPT.format(
        resume=resume_text,
        job_description=job_description,
    )
    try:
        with log_call(logger, "optimize_resume"):
            with client.messages.stream(
                model=MODEL,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                for text in stream.text_stream:
                    yield text
                final_msg = stream.get_final_message()
                usage = calculate_cost(
                    MODEL,
                    final_msg.usage.input_tokens,
                    final_msg.usage.output_tokens,
                )
                optimize_resume._last_usage = usage
                log_usage(logger, "optimize_resume", usage)
    except anthropic.APIStatusError as e:
        if e.status_code == 529 or "overloaded" in str(e).lower():
            raise RuntimeError(
                "Claude is currently overloaded. Wait a few seconds and try again."
            ) from e
        raise RuntimeError(f"API error: {e.message}") from e


def optimize_resume_full(resume_text: str, job_description: str) -> tuple[str, dict]:
    """
    Non-streaming wrapper that collects the full optimized resume and usage stats.

    Args:
        resume_text: The candidate's original resume in Markdown.
        job_description: The full job description text.

    Returns:
        Tuple of (optimized_resume_markdown, usage_dict).
    """
    client = _get_client()
    prompt = OPTIMIZER_PROMPT.format(
        resume=resume_text,
        job_description=job_description,
    )
    with log_call(logger, "optimize_resume_full"):
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
    optimized = response.content[0].text
    usage = calculate_cost(
        MODEL,
        response.usage.input_tokens,
        response.usage.output_tokens,
    )
    log_usage(logger, "optimize_resume_full", usage)
    return optimized, usage


def explain_diff(original: str, optimized: str, job_description: str) -> tuple[str, dict]:
    """
    Generate a bullet-point explanation of what changed between the original
    and optimized resume, and why each change improves ATS alignment.

    Args:
        original: The candidate's original resume text.
        optimized: The Claude-optimized resume text.
        job_description: The job description used for optimization.

    Returns:
        Tuple of (explanation_markdown, usage_dict).
    """
    client = _get_client()
    prompt = DIFF_EXPLANATION_PROMPT.format(
        original=original,
        optimized=optimized,
        job_description=job_description,
    )
    with log_call(logger, "explain_diff"):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
    explanation = response.content[0].text
    usage = calculate_cost(
        MODEL,
        response.usage.input_tokens,
        response.usage.output_tokens,
    )
    log_usage(logger, "explain_diff", usage)
    return explanation, usage


def rewrite_bullets(resume_text: str) -> tuple[list[dict], dict]:
    """
    Find weak bullet points in the resume and rewrite them in STAR format.

    Scans for passive phrases like "responsible for", "worked on", etc.
    Sends them to Claude for STAR-format rewrites in a single batched call.

    Args:
        resume_text: The resume text to scan (Markdown or plain text).

    Returns:
        Tuple of (rewrites, usage_dict).
        rewrites: List of dicts with 'original' and 'rewritten' keys.
        Returns empty list if no weak bullets are found.
    """
    lines = resume_text.splitlines()
    weak = [
        line.strip()
        for line in lines
        if _WEAK_PATTERNS.search(line.strip())
    ]

    if not weak:
        logger.info("rewrite_bullets: no weak bullets found")
        return [], calculate_cost(MODEL, 0, 0)

    client = _get_client()
    bullets_text = "\n".join(f"- {b.lstrip('-* •').strip()}" for b in weak)
    prompt = STAR_REWRITE_PROMPT.format(bullets=bullets_text)

    with log_call(logger, "rewrite_bullets"):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)

    usage = calculate_cost(
        MODEL,
        response.usage.input_tokens,
        response.usage.output_tokens,
    )
    log_usage(logger, "rewrite_bullets", usage)

    try:
        rewrites = json.loads(raw)
        return rewrites, usage
    except json.JSONDecodeError:
        logger.warning("rewrite_bullets: failed to parse JSON response")
        return [], usage


def hallucination_check(
    original: str, optimized: str, job_description: str
) -> tuple[list[dict], dict]:
    """
    Check the optimized resume for skills or terms that Claude may have fabricated.

    Compares the optimized resume against the original resume and JD.
    Any term that appears in neither is flagged as a potential hallucination.

    Args:
        original: The candidate's original resume text.
        optimized: The Claude-optimized resume text.
        job_description: The job description text.

    Returns:
        Tuple of (flagged_items, usage_dict).
        flagged_items: List of dicts with 'term' and 'reason' keys.
    """
    client = _get_client()
    prompt = HALLUCINATION_CHECK_PROMPT.format(
        original=original,
        job_description=job_description,
        optimized=optimized,
    )

    with log_call(logger, "hallucination_check"):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```[a-z]*\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)

    usage = calculate_cost(
        MODEL,
        response.usage.input_tokens,
        response.usage.output_tokens,
    )
    log_usage(logger, "hallucination_check", usage)

    try:
        flagged = json.loads(raw)
        return flagged if isinstance(flagged, list) else [], usage
    except json.JSONDecodeError:
        logger.warning("hallucination_check: failed to parse JSON response")
        return [], usage
