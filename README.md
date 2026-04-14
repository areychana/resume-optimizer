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
| **Resume Optimizer** | Claude rewrites your resume to match the JD. ATS-friendly, keyword-targeted, role-toned. Streams output live, explains every change, flags hallucinations, rewrites weak bullets in STAR format, and exports to PDF. |
| **ATS Scorer** | Multi-dimensional scoring: keyword match, skills coverage, experience level, title alignment. Categorized gaps with actionable suggestions. Validated with Pydantic so the UI never breaks on bad output. |
| **Interview Prep** | 10 role-specific questions (5 technical + 5 behavioral), STAR templates, talking points, red flags. Salary negotiation script for India/remote market. |

### What makes it production-ready

- **PDF upload** — upload your resume as a PDF instead of pasting text (pdfplumber, multi-column aware)
- **STAR rewriter** — scans for weak passive bullets ("responsible for", "worked on") and rewrites them in STAR format
- **Hallucination check** — flags any skills or tools Claude added that were not in your original resume or the JD
- **Pydantic validation** — all structured Claude responses are validated before hitting the UI
- **Structured logging** — every API call is logged with duration, token usage, and cost to `logs/optimizer.log`
- **Input limits** — resume capped at 5,000 chars, JD at 3,000 chars to prevent abuse
- **Bring your own API key** — paste your Anthropic key in the sidebar, never stored anywhere
- **Graceful error handling** — overloaded API, bad JSON, and parse failures all show clean messages

---

## Architecture

```
Streamlit App
  app.py (home)
  pages/1_optimizer.py  ->  optimizer.py
  pages/2_ats.py        ->  ats.py
  pages/3_interview.py  ->  interview.py
              |
        prompt.py  (all Claude prompts as named constants)
        models.py  (Pydantic models for structured responses)
              |
       Anthropic Claude API  (claude-sonnet-4-5)

  pdf_builder.py   ->  fpdf2 (cross-platform, no system binaries)
  utils/sanitize.py -> input cleaning + PDF text extraction
  utils/logger.py  ->  rotating file logger
  utils/session.py ->  versions/*.json (session history)
  utils/cost.py    ->  token usage + cost display
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

# Windows
.venv\Scripts\activate
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

Or just paste it in the sidebar when the app is running (bring your own key mode).

### 5. Run

```bash
streamlit run app.py
```

---

## Running Tests

```bash
pytest tests/ -v
```

Tests cover: input sanitization, Pydantic ATS model validation, score clamping, fallback scoring, and PDF generation.

---

## Deploy to Streamlit Cloud

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your fork
3. In **Settings -> Secrets**, add:
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
├── optimizer.py                  # Resume rewrite, STAR rewriter, hallucination check
├── ats.py                        # ATS scoring with Pydantic validation
├── interview.py                  # Interview prep + salary script
├── models.py                     # Pydantic response models
├── pdf_builder.py                # Markdown to PDF via fpdf2
├── prompt.py                     # All Claude prompts as named constants
├── pages/
│   ├── 1_optimizer.py            # Optimizer page
│   ├── 2_ats.py                  # ATS scorer page
│   └── 3_interview.py            # Interview prep page
├── utils/
│   ├── sanitize.py               # Input cleaning + PDF text extraction
│   ├── logger.py                 # Structured rotating file logger
│   ├── cost.py                   # Token usage + cost estimation
│   └── session.py                # Session history (JSON)
├── tests/
│   ├── test_sanitize.py          # Sanitizer edge case tests
│   ├── test_ats.py               # Pydantic model + fallback scoring tests
│   └── test_pdf.py               # PDF generation tests
├── versions/                     # Auto-saved session JSON files
├── logs/                         # Auto-generated API call logs (gitignored)
├── .streamlit/
│   ├── config.toml               # Theme + server config (10 MB upload limit)
│   └── secrets.toml.example      # Streamlit Cloud secrets template
├── .env.example                  # Local env template
├── CONTRIBUTING.md               # Contribution guide
└── requirements.txt              # Pinned dependencies
```

---

## Tech Stack

- **AI:** Anthropic Claude API (`claude-sonnet-4-5`), streaming + structured JSON output
- **UI:** Streamlit multipage app with session state and live streaming
- **Validation:** Pydantic v2 for structured Claude responses
- **PDF input:** pdfplumber (multi-column aware extraction)
- **PDF output:** fpdf2 (pure Python, zero system dependencies)
- **Logging:** Python logging with RotatingFileHandler
- **Storage:** JSON files, no database
- **Config:** python-dotenv + Streamlit secrets

---

## Cost

Each run costs approximately:

- Resume optimization: ~$0.005 to $0.015
- ATS scoring: ~$0.003 to $0.008
- Interview prep: ~$0.008 to $0.020

Costs are shown live in the UI after each generation. Users bring their own API key so there is no shared cost exposure.

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

---

## License

This project is licensed under the [MIT License](LICENSE).
