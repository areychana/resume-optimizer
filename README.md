# Resume Optimizer

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/areychana/resume-optimizer/main/app.py)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Claude](https://img.shields.io/badge/AI-Claude%20Sonnet-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

An AI-powered resume optimizer built on [Anthropic's Claude API](https://anthropic.com).
Optimize your resume for ATS, score keyword coverage across dimensions, and walk into interviews prepared.

---

## Features

| Module | What it does |
|---|---|
| **Resume Optimizer** | Claude rewrites your resume to match the JD. ATS-friendly, keyword-targeted, role-toned. Shows a diff with explanation and exports to PDF. |
| **ATS Scorer** | Multi-dimensional scoring: keyword match, skills coverage, experience level, title alignment. Categorized gaps with actionable suggestions. |
| **Interview Prep** | 10 role-specific questions (5 technical + 5 behavioral), STAR templates, talking points, red flags. Salary negotiation script for India/remote. |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Streamlit App                            │
│                                                              │
│  app.py (home)                                               │
│  pages/1_optimizer.py ──► optimizer.py                       │
│  pages/2_ats.py       ──► ats.py                             │
│  pages/3_interview.py ──► interview.py                       │
│                │                                             │
│          prompt.py  (all Claude prompts as named constants)  │
│                │                                             │
│         Anthropic Claude API  (claude-sonnet-4-5)            │
│                                                              │
│  pdf_builder.py ──► fpdf2 (cross-platform, no binaries)      │
│  utils/session.py ──► versions/*.json  (session history)     │
│  utils/cost.py    ──► token usage + cost display             │
└──────────────────────────────────────────────────────────────┘
```

---

## Local Setup

Works on macOS, Linux, and Windows. No system binaries required.

### 1. Clone

```bash
git clone https://github.com/areychana/resume-optimizer.git
cd resume-optimizer
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your API key

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

Get your key at [console.anthropic.com](https://console.anthropic.com).

### 5. Run

```bash
streamlit run app.py
```

---

## Deploy to Streamlit Cloud

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=areychana/resume-optimizer&branch=main&mainModule=app.py)

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app → select your fork
3. In **Settings → Secrets**, add:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
4. Deploy. No other configuration needed.

See `.streamlit/secrets.toml.example` for the secrets template.

---

## Project Structure

```
resume-optimizer/
├── app.py                        # Home page
├── optimizer.py                  # Resume rewrite logic (Claude streaming)
├── ats.py                        # ATS scoring (Claude structured JSON)
├── interview.py                  # Interview prep + salary script
├── pdf_builder.py                # Markdown → PDF via fpdf2
├── prompt.py                     # All Claude prompts as named constants
├── pages/
│   ├── 1_optimizer.py            # Optimizer page
│   ├── 2_ats.py                  # ATS scorer page
│   └── 3_interview.py            # Interview prep page
├── utils/
│   ├── cost.py                   # Token usage + cost estimation
│   └── session.py                # Session history (JSON, versions/)
├── versions/                     # Auto-saved session JSON files
├── .streamlit/
│   ├── config.toml               # Theme + server config
│   └── secrets.toml.example      # Streamlit Cloud secrets template
├── .env.example                  # Local env template
└── requirements.txt              # Pinned dependencies
```

---

## Tech Stack

- **AI:** [Anthropic Claude API](https://anthropic.com) (`claude-sonnet-4-5`), with streaming and structured JSON output
- **UI:** [Streamlit](https://streamlit.io) multipage app with session state and streaming display
- **PDF:** [fpdf2](https://github.com/py-pdf/fpdf2), pure Python with no binary dependencies
- **Storage:** JSON files (no database)
- **Config:** python-dotenv + Streamlit secrets

---

## Cost

Each run costs approximately:
- Resume optimization: ~$0.005–0.015 (depends on resume/JD length)
- ATS scoring: ~$0.003–0.008
- Interview prep: ~$0.008–0.020

Costs shown live in the UI after each generation.

---

## License

This project is licensed under the [MIT License](LICENSE).
