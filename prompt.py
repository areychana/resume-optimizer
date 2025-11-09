RESUME_PROMPT = """
You are an expert ATS resume writer.
Rewrite the following resume based on the job description.
Return ONLY markdown resume. No explanation.

Original Resume:
{resume}

Job Description:
{job_desc}

Optimized Resume:
"""