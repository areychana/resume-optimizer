#  Resume Optimizer — AI Powered Resume Tailoring + ATS Score (Gemini)

>  Automatically rewrite your resume to match any job description  
>  Uses **Google Gemini API (Free)**  
>  Outputs: Optimized Resume + ATS Score + Missing Keywords + PDF

---

##  Features

| Feature | Description |
|--------|-------------|
|  AI Resume Rewrite | Tailors your resume to the job description |
|  ATS Score | Checks keyword match percentage |
|  Missing Keywords | Shows what keywords are required but not present |
|  PDF Resume Export | Minimal professional PDF output |
|  Version History | Every generated resume stored in `/versions` |
|  Free API | Uses Google Gemini (no billing or OpenAI quota issues) |

---

##  Project Structure
```
resume-optimizer/
│
├── app.py                     # Main Streamlit UI
├── optimizer.py               # Gemini AI resume optimization logic
├── ats.py                     # ATS keyword scoring & matching
├── pdf_builder.py             # Converts Markdown resume → PDF
├── prompt.py                  # LLM prompt template
├── resume.md                  # Your primary resume in Markdown
├── requirements.txt           # Project dependencies
├── .env                       # Contains GEMINI_API_KEY
│
├── assets/
│   └── style.css              # Custom UI styling (optional)
│
├── versions/                  # Stores previously generated resumes
│   └── (auto-saved files)
│
└── .streamlit/
    └── config.toml            # Streamlit UI theme + settings
```



