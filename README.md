# Resume Optimizer

Lightweight Streamlit app that optimizes a resume for a target job description and produces an ATS-friendly PDF.

## Features
- Generates an optimized resume using a Generative AI model (Google GenAI / Gemini or OpenAI)
- Simple ATS keyword matching and scoring
- Export optimized resume to PDF (wkhtmltopdf + pdfkit)

## Requirements
- Windows, Python 3.10+
- Virtual environment (recommended)
- wkhtmltopdf (for PDF export)
- A Generative AI API key with billing enabled (Google GenAI recommended)

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

## Quick setup (Windows PowerShell)
1. Clone the repository
```powershell
git clone https://github.com/<areychana>/resume-optimizer.git
cd resume-optimizer
```

2. Create & activate virtual environment
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

3. Install dependencies
```powershell
pip install -r requirements.txt
# If using Google's official client:
pip install --upgrade google-genai
```

4. Install wkhtmltopdf
- Chocolatey (run PowerShell as Administrator):
```powershell
choco install wkhtmltopdf -y
```

5. Add API key(s) to a `.env` file (project root)
```text
# For Google GenAI:
GEMINI_API_KEY=YOUR_API_KEY_HERE

## Run the app
```powershell
.venv\Scripts\Activate.ps1
streamlit run app.py
```
Open http://localhost:8501

## Using Google GenAI
Set `GEMINI_API_KEY` in `.env` and in `optimizer.py` use the official client pattern:
```python
from google import genai
client = genai.Client()  # reads GEMINI_API_KEY from env
resp = client.models.generate_content(model="gemini-2.5-flash", contents="your prompt here")
```

Typical push:
```powershell
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/<your-name>/resume-optimizer.git
git branch -M main
git push -u origin main
```

## Troubleshooting
- python not found: install Python and check "Add to PATH", or use the `py` launcher.
- Model errors: ensure correct model name and that API key has required access and billing enabled.
- PDF blank: confirm wkhtmltopdf path and pass configuration to pdfkit.

## License
Add a LICENSE file (MIT recommended).
