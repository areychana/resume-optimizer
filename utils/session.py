"""
Session history management. Saves and loads resume optimizer runs as JSON
files in the versions/ directory. One file per session, named by timestamp.
"""

import json
import os
from datetime import datetime
from pathlib import Path

VERSIONS_DIR = Path(__file__).parent.parent / "versions"


def _ensure_dir() -> None:
    """Create versions/ directory if it does not exist."""
    VERSIONS_DIR.mkdir(exist_ok=True)


def save_session(data: dict) -> Path:
    """
    Persist a session to disk as a timestamped JSON file.

    Args:
        data: dict containing any subset of:
            - module (str): 'optimizer' | 'ats' | 'interview'
            - jd_snippet (str): first 200 chars of the job description
            - resume_snippet (str): first 200 chars of the resume
            - optimized_resume (str): full optimized resume text
            - ats_report (dict): ATS score report
            - interview_prep (str): interview prep markdown
            - usage (dict): token/cost data from calculate_cost()

    Returns:
        Path to the saved JSON file.
    """
    _ensure_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = VERSIONS_DIR / f"{timestamp}.json"
    payload = {
        "timestamp": datetime.now().isoformat(),
        **data,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return filepath


def list_sessions(limit: int = 10) -> list[dict]:
    """
    Return the most recent sessions from versions/, newest first.

    Args:
        limit: Maximum number of sessions to return.

    Returns:
        List of dicts, each with at minimum 'timestamp', 'module',
        'jd_snippet', and the filename stem as 'id'.
    """
    _ensure_dir()
    files = sorted(VERSIONS_DIR.glob("*.json"), reverse=True)[:limit]
    sessions = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            sessions.append({
                "id": f.stem,
                "timestamp": data.get("timestamp", f.stem),
                "module": data.get("module", "unknown"),
                "jd_snippet": data.get("jd_snippet", ""),
            })
        except (json.JSONDecodeError, OSError):
            continue
    return sessions


def load_session(session_id: str) -> dict | None:
    """
    Load a full session by its ID (the timestamp stem of the filename).

    Args:
        session_id: Filename stem, e.g. '20250413_143022'.

    Returns:
        Parsed session dict, or None if not found.
    """
    filepath = VERSIONS_DIR / f"{session_id}.json"
    if not filepath.exists():
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
