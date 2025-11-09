import re

def score_resume(resume: str, job_desc: str):
    resume = resume.lower()
    job = job_desc.lower()

    job_words = set(re.findall(r"[a-zA-Z0-9+#]+", job))
    resume_words = set(re.findall(r"[a-zA-Z0-9+#]+", resume))

    matched = job_words.intersection(resume_words)
    score = int(len(matched) / len(job_words) * 100)

    missing = job_words - resume_words

    return {
        "score": score,
        "matched_keywords": list(matched)[:20],
        "missing_keywords": list(missing)[:20]
    }