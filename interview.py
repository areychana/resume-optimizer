"""
Interview preparation module. Generates tailored interview questions,
STAR-format behavioral answer templates, technical talking points, and
a salary negotiation script using Claude.
"""

import os
import anthropic
from dotenv import load_dotenv
from prompt import INTERVIEW_QUESTIONS_PROMPT, SALARY_NEGOTIATION_PROMPT
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


def generate_interview_questions(resume: str, job_description: str):
    """
    Stream role-specific interview questions with answer guidance.

    Generates 5 technical questions (with talking points + red flags) and
    5 behavioral questions (with STAR templates and interviewer intent).

    Args:
        resume: The candidate's resume text (preferably the optimized version).
        job_description: The full job description text.

    Yields:
        str: Successive text chunks from the Claude stream.

    After exhausting the generator, usage stats are available via
    generate_interview_questions._last_usage.
    """
    client = _get_client()
    prompt = INTERVIEW_QUESTIONS_PROMPT.format(
        resume=resume,
        job_description=job_description,
    )
    with client.messages.stream(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            yield text
        final_msg = stream.get_final_message()
        generate_interview_questions._last_usage = calculate_cost(
            MODEL,
            final_msg.usage.input_tokens,
            final_msg.usage.output_tokens,
        )


def generate_salary_script(job_description: str, resume_summary: str):
    """
    Stream a salary negotiation script tailored to the role and India/remote market.

    Includes market rate analysis, word-for-word negotiation scripts,
    red flags to watch for, and timing guidance.

    Args:
        job_description: The full job description text.
        resume_summary: A short summary of the candidate's profile
            (e.g. first 500 chars of the resume, or a manual summary).

    Yields:
        str: Successive text chunks from the Claude stream.

    After exhausting the generator, usage stats are available via
    generate_salary_script._last_usage.
    """
    client = _get_client()
    prompt = SALARY_NEGOTIATION_PROMPT.format(
        job_description=job_description,
        resume_summary=resume_summary,
    )
    with client.messages.stream(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            yield text
        final_msg = stream.get_final_message()
        generate_salary_script._last_usage = calculate_cost(
            MODEL,
            final_msg.usage.input_tokens,
            final_msg.usage.output_tokens,
        )
