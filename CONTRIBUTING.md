# Contributing to Resume Optimizer

Thanks for your interest in contributing! This is an open project and contributions are welcome.

---

## What you can contribute

- Bug fixes
- New features (see ideas below)
- Prompt improvements (better ATS optimization, STAR rewrites, etc.)
- UI/UX improvements
- Tests
- Documentation

### Feature ideas (good first issues)
- Cover letter generator
- LinkedIn summary rewriter
- Multi-language resume support
- Resume scoring history / comparison view
- Dark mode improvements

---

## Getting started locally

**Requirements:** Python 3.10+

```bash
# 1. Clone the repo
git clone https://github.com/areychana/resume-optimizer.git
cd resume-optimizer

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Anthropic API key
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then open secrets.toml and paste your key

# 5. Run the app
streamlit run app.py
```

---

## Project structure

```
resume-optimizer/
├── app.py                  # Home page
├── optimizer.py            # Resume rewrite logic
├── ats.py                  # ATS scoring logic
├── interview.py            # Interview prep logic
├── models.py               # Pydantic response models
├── prompt.py               # All Claude prompt templates
├── pdf_builder.py          # PDF export
├── pages/
│   ├── 1_optimizer.py
│   ├── 2_ats.py
│   └── 3_interview.py
├── utils/
│   ├── sanitize.py         # Input cleaning + PDF parsing
│   ├── logger.py           # Structured logging
│   ├── cost.py             # Token cost calculator
│   └── session.py          # Session history saving
└── tests/
    ├── test_sanitize.py
    ├── test_ats.py
    └── test_pdf.py
```

---

## Running tests

```bash
pip install pytest
pytest tests/ -v
```

---

## How to submit a PR

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Run tests: `pytest tests/ -v`
5. Push and open a pull request against `main`

Please keep PRs focused on one thing. A small, clean PR is much easier to review than a large one touching everything.

---

## Prompts and Claude

All prompts live in `prompt.py`. If you want to improve how Claude rewrites resumes or scores ATS, that is the place to start. Keep prompts clean and add a comment explaining what the prompt is trying to achieve if it is not obvious.

---

## Code style

- Python 3.10+
- No external formatting tools enforced, just keep it readable
- No inline API calls outside of `optimizer.py`, `ats.py`, and `interview.py`
- All Claude prompts go in `prompt.py`

---

## Questions?

Open a GitHub issue and tag it `question`. Happy to help.
