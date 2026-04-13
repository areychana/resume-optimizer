"""
Home page for the resume optimizer app.
Provides an overview and links to the three modules.
"""

import streamlit as st
from utils.session import list_sessions

st.set_page_config(
    page_title="Resume Optimizer",
    page_icon="💼",
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

    st.markdown("#### Recent Sessions")
    sessions = list_sessions(limit=5)
    if sessions:
        for s in sessions:
            label = f"{s['module'].title()} on {s['timestamp'][:10]}"
            snippet = s.get("jd_snippet", "")
            if snippet:
                label += f"\n_{snippet[:40]}..._"
            st.caption(label)
    else:
        st.caption("No sessions yet.")

# ── Hero ───────────────────────────────────────────────────────────────────
st.title("Resume Optimizer")
st.subheader("AI-powered resume optimization, ATS scoring, and interview prep.")
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### ✏️ Resume Optimizer")
    st.markdown(
        "Paste your resume and a job description. "
        "Claude rewrites your resume to be ATS-optimized and role-targeted, "
        "then shows you exactly what changed and why."
    )
    st.page_link("pages/1_optimizer.py", label="Open Optimizer →")

with col2:
    st.markdown("### 🎯 ATS Scorer")
    st.markdown(
        "Get a multi-dimensional score across keyword match, skills coverage, "
        "experience level, and role alignment. See matched and missing keywords "
        "by category with actionable suggestions."
    )
    st.page_link("pages/2_ats.py", label="Open ATS Scorer →")

with col3:
    st.markdown("### 🧠 Interview Prep")
    st.markdown(
        "Generate 10 role-specific interview questions with STAR templates "
        "for behavioral rounds and key talking points for technical rounds. "
        "Includes a salary negotiation script for India/remote roles."
    )
    st.page_link("pages/3_interview.py", label="Open Interview Prep →")

st.markdown("---")

st.markdown(
    """
    **How to use:**
    1. Start with **Resume Optimizer**: paste your resume and the JD to get an ATS-ready rewrite.
    2. Run **ATS Scorer** on the optimized resume to validate keyword coverage.
    3. Use **Interview Prep** to get ready for the call.

    **Powered by** [Claude (Anthropic)](https://anthropic.com) · Built with [Streamlit](https://streamlit.io)
    """
)
