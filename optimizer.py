"""
Resume optimization module. Uses Claude to rewrite a resume for a specific
job description with ATS-focused improvements and streaming output.
"""

import os
import anthropic
from dotenv import load_dotenv
from prompt import OPTIMIZER_PROMPT, DIFF_EXPLANATION_PROMPT
from utils.cost import calculate_cost

load_dotenv()

MODEL = "claude-sonnet-4-5"


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

    After the stream is exhausted the generator stores usage on itself;
    callers can access it via .usage after consuming the generator, but
    the idiomatic way is to use optimize_resume_full() for non-streaming use.
    """
    client = _get_client()
    prompt = OPTIMIZER_PROMPT.format(
        resume=resume_text,
        job_description=job_description,
    )
    with client.messages.stream(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            yield text
        # Store final usage on the stream object for callers that need it
        final_msg = stream.get_final_message()
        optimize_resume._last_usage = calculate_cost(
            MODEL,
            final_msg.usage.input_tokens,
            final_msg.usage.output_tokens,
        )


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
    return explanation, usage
