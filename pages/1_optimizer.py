"""
Page 1: Resume Optimizer.
Streams an ATS-optimized resume rewrite from Claude, shows a diff explanation,
STAR bullet rewrites, hallucination warnings, and provides a PDF download.
"""

import streamlit as st
from optimizer import optimize_resume, explain_diff, rewrite_bullets, hallucination_check
from pdf_builder import build_pdf
from utils.sanitize import sanitize, extract_pdf_text
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

MAX_RESUME_CHARS = 5_000
MAX_JD_CHARS = 3_000

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("**Your Resume**")
    resume_file = st.file_uploader(
        "Upload PDF (optional, max 10 MB)",
        type=["pdf"],
        key="resume_pdf",
        help="Upload a PDF or paste text below.",
    )
    if resume_file is not None:
        try:
            extracted = extract_pdf_text(resume_file.read())
            st.session_state["resume_input"] = extracted
            st.success("PDF parsed successfully.")
        except Exception as e:
            st.error(f"Could not read PDF: {e}")
    resume_input = st.text_area(
        "Or paste Markdown / plain text",
        height=300,
        placeholder="Paste your current resume here...",
        max_chars=MAX_RESUME_CHARS,
        key="resume_input",
    )

with col_right:
    jd_input = st.text_area(
        "Job Description",
        height=380,
        placeholder="Paste the full job description here...",
        max_chars=MAX_JD_CHARS,
        key="jd_input",
    )

run = st.button("Optimize Resume", type="primary", use_container_width=True)

if run:
    resume_text = sanitize(resume_input.strip())
    jd_text = sanitize(jd_input.strip())

    if not resume_text:
        st.error("Please provide your resume (upload PDF or paste text).")
        st.stop()
    if not jd_text:
        st.error("Please paste the job description.")
        st.stop()

    st.markdown("---")

    # ── Stream optimized resume ────────────────────────────────────────────
    st.subheader("Optimized Resume")
    optimized_placeholder = st.empty()
    full_optimized = ""

    with st.spinner("Claude is rewriting your resume..."):
        try:
            for chunk in optimize_resume(resume_text, jd_text):
                full_optimized += chunk
                optimized_placeholder.markdown(full_optimized + "▌")
            optimized_placeholder.markdown(full_optimized)
            opt_usage = getattr(optimize_resume, "_last_usage", {})
        except (ValueError, RuntimeError) as e:
            st.error(str(e))
            st.stop()

    st.session_state["optimized_resume"] = full_optimized
    st.session_state["original_resume"] = resume_text
    st.session_state["jd"] = jd_text

    # ── Hallucination check ────────────────────────────────────────────────
    with st.spinner("Checking for fabricated content..."):
        flagged, hal_usage = hallucination_check(resume_text, full_optimized, jd_text)

    if flagged:
        st.subheader("Hallucination Warning")
        st.warning(
            "The following terms appear in the optimized resume but were **not** in "
            "your original resume or the job description. Review before submitting."
        )
        for item in flagged:
            st.markdown(f"- **`{item.get('term', '')}`**: {item.get('reason', '')}")
    else:
        st.success("No fabricated content detected.")

    # ── STAR bullet rewrites ───────────────────────────────────────────────
    with st.spinner("Scanning for weak bullet points..."):
        rewrites, star_usage = rewrite_bullets(resume_text)

    if rewrites:
        st.subheader("STAR Bullet Rewrites")
        st.caption(
            f"{len(rewrites)} weak bullet(s) found. Suggested rewrites in STAR format:"
        )
        for item in rewrites:
            with st.expander(f"Original: {item.get('original', '')[:80]}"):
                st.markdown(f"**Rewritten:** {item.get('rewritten', '')}")

    # ── Diff explanation ───────────────────────────────────────────────────
    st.subheader("What Changed & Why")
    with st.spinner("Analyzing changes..."):
        diff_text, diff_usage = explain_diff(resume_text, full_optimized, jd_text)
    st.markdown(diff_text)

    # Combined usage across all calls
    all_usages = [opt_usage, hal_usage, star_usage, diff_usage]
    total_input = sum(u.get("input_tokens", 0) for u in all_usages)
    total_output = sum(u.get("output_tokens", 0) for u in all_usages)
    total_cost = sum(u.get("cost_float", 0) for u in all_usages)
    st.caption(
        f"Token usage: {total_input + total_output:,} tokens | "
        f"Est. cost: ${total_cost:.4f}"
    )

    # ── Side-by-side diff view ─────────────────────────────────────────────
    st.subheader("Side-by-Side Comparison")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Original**")
        st.code(resume_text, language="markdown")
    with c2:
        st.markdown("**Optimized**")
        st.code(full_optimized, language="markdown")

    # ── PDF download ───────────────────────────────────────────────────────
    st.subheader("Download PDF")
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
                "fpdf2 is not installed so PDF export is unavailable. "
                "Run `pip install fpdf2` to enable it."
            )
        except Exception as e:
            st.warning(f"PDF generation failed: {e}")

    # ── Save session ───────────────────────────────────────────────────────
    save_session({
        "module": "optimizer",
        "jd_snippet": jd_text[:200],
        "resume_snippet": resume_text[:200],
        "optimized_resume": full_optimized,
        "diff_explanation": diff_text,
        "hallucination_flags": flagged,
        "star_rewrites": rewrites,
        "usage": {
            "input_tokens": total_input,
            "output_tokens": total_output,
            "cost_usd": f"${total_cost:.4f}",
        },
    })
    st.success("Session saved to history.")
