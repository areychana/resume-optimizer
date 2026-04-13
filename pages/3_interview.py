"""
Page 3: Interview Prep.
Streams role-specific interview questions (technical + behavioral with STAR
templates) and a salary negotiation script via Claude.
"""

import streamlit as st
from interview import generate_interview_questions, generate_salary_script
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

default_resume = st.session_state.get("optimized_resume", "")
default_jd = st.session_state.get("jd", "")

col_left, col_right = st.columns(2)
with col_left:
    resume_input = st.text_area(
        "Resume (Markdown or plain text)",
        value=default_resume,
        height=300,
        placeholder="Paste your resume here (optimized preferred)...",
    )
with col_right:
    jd_input = st.text_area(
        "Job Description",
        value=default_jd,
        height=300,
        placeholder="Paste the full job description here...",
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
    if not resume_input.strip():
        st.error("Please paste your resume.")
        st.stop()
    if not jd_input.strip():
        st.error("Please paste the job description.")
        st.stop()

    st.markdown("---")
    st.subheader("🧠 Interview Questions")
    placeholder = st.empty()
    full_text = ""

    with st.spinner("Claude is generating your interview questions..."):
        try:
            for chunk in generate_interview_questions(resume_input, jd_input):
                full_text += chunk
                placeholder.markdown(full_text + "▌")
            placeholder.markdown(full_text)
            usage = getattr(generate_interview_questions, "_last_usage", {})
        except ValueError as e:
            st.error(str(e))
            st.stop()

    st.caption(
        f"🔢 Token usage: {usage.get('total_tokens', 0):,} tokens | "
        f"Est. cost: {usage.get('cost_usd', '$0.0000')}"
    )

    save_session({
        "module": "interview",
        "jd_snippet": jd_input[:200],
        "resume_snippet": resume_input[:200],
        "interview_prep": full_text,
        "usage": usage,
    })

# ── Salary negotiation ─────────────────────────────────────────────────────
if run_salary:
    if not jd_input.strip():
        st.error("Please paste the job description.")
        st.stop()

    st.markdown("---")
    st.subheader("💰 Salary Negotiation Script")

    # Use first 500 chars of resume as profile summary if provided
    resume_summary = resume_input[:500] if resume_input.strip() else (
        "Candidate profile not provided, so the analysis will be based on the role only."
    )

    placeholder = st.empty()
    full_text = ""

    with st.spinner("Claude is crafting your negotiation script..."):
        try:
            for chunk in generate_salary_script(jd_input, resume_summary):
                full_text += chunk
                placeholder.markdown(full_text + "▌")
            placeholder.markdown(full_text)
            usage = getattr(generate_salary_script, "_last_usage", {})
        except ValueError as e:
            st.error(str(e))
            st.stop()

    st.caption(
        f"🔢 Token usage: {usage.get('total_tokens', 0):,} tokens | "
        f"Est. cost: {usage.get('cost_usd', '$0.0000')}"
    )

    save_session({
        "module": "salary",
        "jd_snippet": jd_input[:200],
        "salary_script": full_text,
        "usage": usage,
    })
