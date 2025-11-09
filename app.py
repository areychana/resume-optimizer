import streamlit as st
from optimizer import optimize_resume
from ats import score_resume
from pdf_builder import build_pdf

st.title("🚀 AI Resume Optimizer + ATS Scanner")

resume = st.text_area("Paste your Resume (Markdown)", height=200)
job = st.text_area("Paste Job Description", height=200)

if st.button("Optimize & Score"):
    with st.spinner("Optimizing..."):
        new_resume = optimize_resume(resume, job)
        report = score_resume(new_resume, job)
        pdf = build_pdf(new_resume)

    st.subheader("✅ Optimized Resume")
    st.code(new_resume, language="markdown")

    st.subheader("🎯 ATS Score")
    st.write(f"Match Score: **{report['score']}%**")
    st.write("Matched Keywords:", report["matched_keywords"])
    st.write("Missing Keywords:", report["missing_keywords"])

    with open(pdf, "rb") as f:
        st.download_button("Download PDF", f, pdf)
