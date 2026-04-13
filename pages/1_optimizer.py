"""
Page 1: Resume Optimizer.
Streams an ATS-optimized resume rewrite from Claude, shows a diff explanation,
and provides a PDF download.
"""

import streamlit as st
from optimizer import optimize_resume, explain_diff
from pdf_builder import build_pdf
from utils.session import save_session

st.set_page_config(
    page_title="Resume Optimizer",
    page_icon="✏️",
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
        "**Tip:** Use the optimized resume output as input to the "
        "ATS Scorer for the most accurate keyword analysis."
    )

# ── Main ───────────────────────────────────────────────────────────────────
st.title("✏️ Resume Optimizer")
st.caption("Claude rewrites your resume to be ATS-optimized and role-targeted.")
st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    resume_input = st.text_area(
        "Your Resume (Markdown or plain text)",
        height=380,
        placeholder="Paste your current resume here...",
        key="resume_input",
    )

with col_right:
    jd_input = st.text_area(
        "Job Description",
        height=380,
        placeholder="Paste the full job description here...",
        key="jd_input",
    )

run = st.button("✨ Optimize Resume", type="primary", use_container_width=True)

if run:
    if not resume_input.strip():
        st.error("Please paste your resume.")
        st.stop()
    if not jd_input.strip():
        st.error("Please paste the job description.")
        st.stop()

    st.markdown("---")

    # ── Stream optimized resume ────────────────────────────────────────────
    st.subheader("✅ Optimized Resume")
    optimized_placeholder = st.empty()
    full_optimized = ""

    with st.spinner("Claude is rewriting your resume..."):
        try:
            for chunk in optimize_resume(resume_input, jd_input):
                full_optimized += chunk
                optimized_placeholder.markdown(full_optimized + "▌")
            optimized_placeholder.markdown(full_optimized)
            opt_usage = getattr(optimize_resume, "_last_usage", {})
        except ValueError as e:
            st.error(str(e))
            st.stop()

    st.session_state["optimized_resume"] = full_optimized
    st.session_state["original_resume"] = resume_input
    st.session_state["jd"] = jd_input

    # ── Diff explanation ───────────────────────────────────────────────────
    st.subheader("🔍 What Changed & Why")
    with st.spinner("Analyzing changes..."):
        diff_text, diff_usage = explain_diff(resume_input, full_optimized, jd_input)
    st.markdown(diff_text)

    # Combined usage across both calls
    total_input = opt_usage.get("input_tokens", 0) + diff_usage.get("input_tokens", 0)
    total_output = opt_usage.get("output_tokens", 0) + diff_usage.get("output_tokens", 0)
    total_cost = opt_usage.get("cost_float", 0) + diff_usage.get("cost_float", 0)
    st.caption(
        f"🔢 Token usage: {total_input + total_output:,} tokens | "
        f"Est. cost: ${total_cost:.4f}"
    )

    # ── Side-by-side diff view ─────────────────────────────────────────────
    st.subheader("📄 Side-by-Side Comparison")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Original**")
        st.code(resume_input, language="markdown")
    with c2:
        st.markdown("**Optimized**")
        st.code(full_optimized, language="markdown")

    # ── PDF download ───────────────────────────────────────────────────────
    st.subheader("📥 Download PDF")
    with st.spinner("Generating PDF..."):
        try:
            pdf_path = build_pdf(full_optimized)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="Download Optimized Resume (PDF)",
                    data=f,
                    file_name="resume_optimized.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
        except ImportError:
            st.warning(
                "xhtml2pdf is not installed so PDF export is unavailable. "
                "Run `pip install xhtml2pdf` to enable it."
            )
        except Exception as e:
            st.warning(f"PDF generation failed: {e}")

    # ── Save session ───────────────────────────────────────────────────────
    save_session({
        "module": "optimizer",
        "jd_snippet": jd_input[:200],
        "resume_snippet": resume_input[:200],
        "optimized_resume": full_optimized,
        "diff_explanation": diff_text,
        "usage": {
            "input_tokens": total_input,
            "output_tokens": total_output,
            "cost_usd": f"${total_cost:.4f}",
        },
    })
    st.success("Session saved to history.")
