"""
All Claude prompt templates for the resume optimizer.
Import from here instead of writing inline prompts anywhere else.
"""

OPTIMIZER_PROMPT = """\
You are an expert ATS resume writer and career coach.

Analyze the job description below to extract:
- Required technical skills and tools
- Preferred qualifications
- Seniority signals (years of experience, leadership expectations)
- Role-specific keywords that ATS systems scan for
- Soft skills and cultural fit signals

Then rewrite the resume to:
- Lead with the strongest matching experience
- Naturally incorporate extracted keywords without keyword stuffing
- Quantify achievements where possible (add placeholder metrics like [X%] if none exist)
- Match the seniority tone of the job description
- Use action verbs aligned with the role
- Keep formatting clean and ATS-parseable (no tables, no columns, no icons)

Return ONLY the optimized resume in Markdown. No explanation, no preamble.

---
ORIGINAL RESUME:
{resume}

---
JOB DESCRIPTION:
{job_description}

---
OPTIMIZED RESUME:
"""

DIFF_EXPLANATION_PROMPT = """\
You are a resume coach. A candidate's resume was rewritten to match a job description.

Compare the original and optimized resumes and produce a concise change summary.

For each significant change, output one bullet in this format:
- **[Section]**: What changed and why it improves ATS match or role alignment.

Keep the total to 5–8 bullets. Be specific. No generic praise.

---
ORIGINAL RESUME:
{original}

---
OPTIMIZED RESUME:
{optimized}

---
JOB DESCRIPTION:
{job_description}

---
CHANGE SUMMARY:
"""

ATS_ANALYSIS_PROMPT = """\
You are an ATS (Applicant Tracking System) expert. Analyze the resume against the job description.

Return a JSON object with EXACTLY this structure (no markdown code fences, raw JSON only):

{{
  "overall_score": <integer 0-100>,
  "dimensions": {{
    "keyword_match": <integer 0-100>,
    "experience_level": <integer 0-100>,
    "skills_coverage": <integer 0-100>,
    "role_title_alignment": <integer 0-100>
  }},
  "technical_skills": {{
    "matched": ["skill1", "skill2"],
    "missing": ["skill3", "skill4"]
  }},
  "tools_and_frameworks": {{
    "matched": ["tool1", "tool2"],
    "missing": ["tool3", "tool4"]
  }},
  "soft_skills": {{
    "matched": ["skill1"],
    "missing": ["skill2"]
  }},
  "suggestions": [
    {{
      "gap": "Missing keyword or skill",
      "action": "Specific actionable suggestion to address this gap"
    }}
  ],
  "verdict": "One sentence summary of overall fit."
}}

Scoring guide:
- keyword_match: % of JD keywords present in resume
- experience_level: how well years/seniority in resume matches JD requirements
- skills_coverage: breadth of required skills covered
- role_title_alignment: how closely past titles match the target role

---
RESUME:
{resume}

---
JOB DESCRIPTION:
{job_description}
"""

INTERVIEW_QUESTIONS_PROMPT = """\
You are a senior technical interviewer at a top tech company.

Based on the job description and the candidate's resume, generate 10 interview questions:
- 5 technical questions targeting the specific skills and stack in the JD
- 5 behavioral questions using the STAR framework, tied to the role's responsibilities

For each technical question, provide:
- The question
- 3–4 key talking points the candidate should cover
- A red flag to avoid

For each behavioral question, provide:
- The question
- A STAR-format answer template (Situation, Task, Action, Result) filled with placeholders the candidate can customize
- What the interviewer is really assessing

Format as clean Markdown with clear headers. Be specific to the role. No generic questions.

---
RESUME:
{resume}

---
JOB DESCRIPTION:
{job_description}
"""

STAR_REWRITE_PROMPT = """\
You are an expert resume coach. Below is a list of weak resume bullet points that use passive or vague language.

Rewrite each bullet into the STAR format (Situation, Task, Action, Result) using strong action verbs.
Keep each rewritten bullet to 1-2 lines. Use [METRIC] as a placeholder where a number would strengthen the point.
Return ONLY a JSON array in this exact format (no code fences):

[
  {{"original": "original bullet text", "rewritten": "rewritten STAR bullet"}},
  ...
]

WEAK BULLETS:
{bullets}
"""

HALLUCINATION_CHECK_PROMPT = """\
You are a resume auditor checking for fabricated content.

Compare the OPTIMIZED RESUME against the ORIGINAL RESUME and the JOB DESCRIPTION.
Identify any skills, tools, technologies, or qualifications that appear in the optimized resume
but were NOT present in either the original resume or the job description.

Return ONLY a JSON array of flagged items (no code fences). If nothing is flagged, return an empty array [].

Each item should follow this format:
[
  {{"term": "the flagged term", "reason": "brief explanation of why it looks fabricated"}}
]

ORIGINAL RESUME:
{original}

JOB DESCRIPTION:
{job_description}

OPTIMIZED RESUME:
{optimized}
"""

SALARY_NEGOTIATION_PROMPT = """\
You are a compensation expert and career coach specializing in the Indian tech job market and remote roles.

Based on the role and candidate profile below, produce:

1. **Market Rate Analysis**: Realistic salary range for this role (India / remote). Cite factors that affect the range (company tier, location, skills).

2. **Negotiation Script**: A word-for-word script the candidate can use when the offer comes in. Include:
   - Opening line after receiving the offer
   - How to counter-offer without burning the relationship
   - Response if they say "this is our best offer"
   - How to negotiate non-salary perks (WFH, stock, joining bonus) if base is fixed

3. **Red Flags**: 2–3 warning signs in the JD or offer process to watch for.

4. **Timing Tips**: Best time to bring up salary and what to avoid saying.

Keep it practical and India-market-aware. Mention specific numbers where relevant.

---
TARGET ROLE:
{job_description}

---
CANDIDATE PROFILE SUMMARY:
{resume_summary}
"""
