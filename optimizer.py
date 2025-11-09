import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# client picks up GEMINI_API_KEY from env
client = genai.Client()
MODEL = "gemini-2.5-flash"  # or a model you have access to

def optimize_resume(resume_text: str, job_description: str) -> str:
    prompt = f"""Given this resume:
{resume_text}

And this job description:
{job_description}

Optimize the resume to match the job requirements and make it ATS-friendly.
Return only the optimized resume text.
"""
    try:
        resp = client.models.generate_content(model=MODEL, contents=prompt)  # <- use contents
        # Extract text robustly for different client versions
        if hasattr(resp, "text") and resp.text:
            return resp.text
        if getattr(resp, "candidates", None):
            # older response shape
            return resp.candidates[0].content if resp.candidates[0].content else str(resp)
        if getattr(resp, "outputs", None):
            # newer response shape
            out_texts = []
            for out in resp.outputs:
                if getattr(out, "text", None):
                    out_texts.append(out.text)
            return "\n".join(out_texts) if out_texts else str(resp)
        return str(resp)
    except Exception as e:
        return f"Error: {e}"