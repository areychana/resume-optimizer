"""
Page 3: Interview Prep.
Streams role-specific interview questions (technical + behavioral with STAR
templates) and a salary negotiation script via Claude.
"""

import streamlit as st
from interview import generate_interview_questions, generate_salary_script
from utils.sanitize import sanitize, extract_pdf_text
from utils.session import save_session

st.set_page_config(
    page_title="Interview Prep",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Resume Optimizer")
    st.markdown("---")
    st.page_link("app.py", label="Home", icon="🏠")
    st.page_link("pages/1_optimizer.py", label="Resume Optimizer", icon="✏️")
    st.page_link("pages/2_ats.py", label="ATS Scorer", icon="🎯")
    st.page_link("pages/3_interview.py", label="Interview Prep", icon="🧠")
    st.markdown("---")
    st.markdown("#### Your API Key")
    api_key_input = st.text_input(
        "Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        value=st.session_state.get("api_key", ""),
        help="Your key is only stored in this browser session and never saved anywhere.",
    )
    if api_key_input:
        st.session_state["api_key"] = api_key_input
        st.caption("Key saved for this session.")
    else:
        st.caption("Get your key at [console.anthropic.com](https://console.anthropic.com)")
    st.markdown("---")
    st.markdown(
        "**Tip:** Use your *optimized* resume for more targeted "
        "questions. Run the Optimizer first."
    )

# ── Main ───────────────────────────────────────────────────────────────────
st.title("🧠 Interview Prep")
st.caption(
    "10 role-specific questions with STAR templates and talking points, "
    "plus a salary negotiation script."
)
st.markdown("---")

MAX_RESUME_CHARS = 5_000
MAX_JD_CHARS = 3_000

default_resume = st.session_state.get("optimized_resume", "")
default_jd = st.session_state.get("jd", "")

col_left, col_right = st.columns(2)
with col_left:
    st.markdown("**Your Resume**")
    resume_file = st.file_uploader(
        "Upload PDF (optional, max 10 MB)",
        type=["pdf"],
        key="interview_resume_pdf",
        help="Upload a PDF or paste text below.",
    )
    if resume_file is not None:
        try:
            st.session_state["interview_resume_input"] = extract_pdf_text(resume_file.read())
            st.success("PDF parsed successfully.")
        except Exception as e:
            st.error(f"Could not read PDF: {e}")
    if "interview_resume_input" not in st.session_state and default_resume:
        st.session_state["interview_resume_input"] = default_resume
    resume_input = st.text_area(
        "Or paste Markdown / plain text",
        height=230,
        placeholder="Paste your resume here (optimized preferred)...",
        max_chars=MAX_RESUME_CHARS,
        key="interview_resume_input",
    )
with col_right:
    jd_input = st.text_area(
        "Job Description",
        value=default_jd,
        height=300,
        placeholder="Paste the full job description here...",
        max_chars=MAX_JD_CHARS,
    )

col_q, col_s = st.columns(2)
run_questions = col_q.button(
    "🧠 Generate Interview Questions", type="primary", use_container_width=True
)
run_salary = col_s.button(
    "💰 Generate Salary Script", use_container_width=True
)

# ── Interview questions ────────────────────────────────────────────────────
if run_questions:
    resume_text = sanitize(resume_input.strip())
    jd_text = sanitize(jd_input.strip())

    if not resume_text:
        st.error("Please provide your resume (upload PDF or paste text).")
        st.stop()
    if not jd_text:
        st.error("Please paste the job description.")
        st.stop()

    st.markdown("---")
    st.subheader("Interview Questions")
    placeholder = st.empty()
    full_text = ""

    with st.spinner("Claude is generating your interview questions..."):
        try:
            for chunk in generate_interview_questions(resume_text, jd_text):
                full_text += chunk
                placeholder.markdown(full_text + "▌")
            placeholder.markdown(full_text)
            usage = getattr(generate_interview_questions, "_last_usage", {})
        except (ValueError, RuntimeError) as e:
            st.error(str(e))
            st.stop()

    st.caption(
        f"🔢 Token usage: {usage.get('total_tokens', 0):,} tokens | "
        f"Est. cost: {usage.get('cost_usd', '$0.0000')}"
    )

    save_session({
        "module": "interview",
        "jd_snippet": jd_text[:200],
        "resume_snippet": resume_text[:200],
        "interview_prep": full_text,
        "usage": usage,
    })

# ── Salary negotiation ─────────────────────────────────────────────────────
if run_salary:
    jd_text_salary = sanitize(jd_input.strip())
    if not jd_text_salary:
        st.error("Please paste the job description.")
        st.stop()

    st.markdown("---")
    st.subheader("Salary Negotiation Script")

    # Use first 500 chars of resume as profile summary if provided
    resume_summary = sanitize(resume_input)[:500] if resume_input.strip() else (
        "Candidate profile not provided, so the analysis will be based on the role only."
    )

    placeholder = st.empty()
    full_text = ""

    with st.spinner("Claude is crafting your negotiation script..."):
        try:
            for chunk in generate_salary_script(jd_text_salary, resume_summary):
                full_text += chunk
                placeholder.markdown(full_text + "▌")
            placeholder.markdown(full_text)
            usage = getattr(generate_salary_script, "_last_usage", {})
        except (ValueError, RuntimeError) as e:
            st.error(str(e))
            st.stop()

    st.caption(
        f"🔢 Token usage: {usage.get('total_tokens', 0):,} tokens | "
        f"Est. cost: {usage.get('cost_usd', '$0.0000')}"
    )

    save_session({
        "module": "salary",
        "jd_snippet": jd_text_salary[:200],
        "salary_script": full_text,
        "usage": usage,
    })
