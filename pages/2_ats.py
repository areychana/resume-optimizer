"""
Page 2: ATS Scorer.
Multi-dimensional ATS analysis via Claude: keyword match, skills coverage,
experience level alignment, and role title fit, with per-category breakdowns
and actionable improvement suggestions.
"""

import streamlit as st
from ats import score_resume
from utils.session import save_session

st.set_page_config(
    page_title="ATS Scorer",
    page_icon="🎯",
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
        "**Tip:** For best results, score the *optimized* resume "
        "from the Optimizer, not your original."
    )

# ── Main ───────────────────────────────────────────────────────────────────
st.title("🎯 ATS Scorer")
st.caption("Multi-dimensional analysis of how well your resume matches the job description.")
st.markdown("---")

# Pre-fill from session state if coming from the optimizer
default_resume = st.session_state.get("optimized_resume", "")
default_jd = st.session_state.get("jd", "")

col_left, col_right = st.columns(2)
with col_left:
    resume_input = st.text_area(
        "Resume (Markdown or plain text)",
        value=default_resume,
        height=340,
        placeholder="Paste your resume here (or run the Optimizer first)...",
    )
with col_right:
    jd_input = st.text_area(
        "Job Description",
        value=default_jd,
        height=340,
        placeholder="Paste the full job description here...",
    )

run = st.button("🎯 Run ATS Analysis", type="primary", use_container_width=True)

if run:
    if not resume_input.strip():
        st.error("Please paste your resume.")
        st.stop()
    if not jd_input.strip():
        st.error("Please paste the job description.")
        st.stop()

    st.markdown("---")

    with st.spinner("Claude is analyzing your resume against the JD..."):
        try:
            report, usage = score_resume(resume_input, jd_input)
        except ValueError as e:
            st.error(str(e))
            st.stop()

    if report.get("_fallback"):
        st.warning("Claude was unavailable so this is a fallback keyword-overlap score.")

    # ── Overall score ──────────────────────────────────────────────────────
    score = report.get("overall_score", 0)
    color = "#22c55e" if score >= 75 else "#f59e0b" if score >= 50 else "#ef4444"
    st.markdown(
        f"""
        <div style="text-align:center; padding: 24px 0 8px 0;">
            <span style="font-size:64px; font-weight:700; color:{color};">{score}</span>
            <span style="font-size:32px; color:#6b7280;">/100</span>
            <p style="color:#6b7280; margin-top:4px;">Overall ATS Match Score</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(score / 100)
    st.markdown(f"> {report.get('verdict', '')}")

    # ── Dimensional scores ─────────────────────────────────────────────────
    st.subheader("📊 Score Breakdown")
    dims = report.get("dimensions", {})
    d_cols = st.columns(4)
    dim_labels = {
        "keyword_match": "Keyword Match",
        "experience_level": "Experience Level",
        "skills_coverage": "Skills Coverage",
        "role_title_alignment": "Title Alignment",
    }
    for i, (key, label) in enumerate(dim_labels.items()):
        val = dims.get(key, 0)
        d_cols[i].metric(label=label, value=f"{val}%")

    # ── Keyword categories ─────────────────────────────────────────────────
    st.subheader("🔑 Keyword Analysis by Category")

    def render_keyword_section(title: str, data: dict) -> None:
        matched = data.get("matched", [])
        missing = data.get("missing", [])
        with st.expander(f"{title} ({len(matched)} matched, {len(missing)} missing)", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**✅ Matched**")
                if matched:
                    st.markdown(" ".join(f"`{k}`" for k in matched))
                else:
                    st.caption("None found.")
            with c2:
                st.markdown("**❌ Missing**")
                if missing:
                    st.markdown(" ".join(f"`{k}`" for k in missing))
                else:
                    st.caption("Nothing missing, great coverage!")

    render_keyword_section("🛠️ Technical Skills", report.get("technical_skills", {}))
    render_keyword_section("⚙️ Tools & Frameworks", report.get("tools_and_frameworks", {}))
    render_keyword_section("🤝 Soft Skills", report.get("soft_skills", {}))

    # ── Suggestions ────────────────────────────────────────────────────────
    suggestions = report.get("suggestions", [])
    if suggestions:
        st.subheader("💡 Actionable Suggestions")
        for s in suggestions:
            gap = s.get("gap", "")
            action = s.get("action", "")
            st.markdown(f"- **{gap}**: {action}")

    # ── Token usage ────────────────────────────────────────────────────────
    st.caption(
        f"🔢 Token usage: {usage.get('total_tokens', 0):,} tokens | "
        f"Est. cost: {usage.get('cost_usd', '$0.0000')}"
    )

    # ── Save session ───────────────────────────────────────────────────────
    save_session({
        "module": "ats",
        "jd_snippet": jd_input[:200],
        "resume_snippet": resume_input[:200],
        "ats_report": report,
        "usage": usage,
    })
