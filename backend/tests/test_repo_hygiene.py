"""FR-01-05, FR-01-07 — secrets hygiene of the repo."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

BACKEND = Path(__file__).parents[1]
REPO = BACKEND.parent
ALLOWED_VALUE = "OPENAI_AGENTS_TRACE_INCLUDE_SENSITIVE_DATA=0"


def test_env_example_has_names_only() -> None:
    lines = (BACKEND / ".env.example").read_text(encoding="utf-8").splitlines()
    entries = [ln for ln in lines if ln.strip() and not ln.lstrip().startswith("#")]
    assert entries, "no variables found"
    for line in entries:
        if line == ALLOWED_VALUE:
            continue
        name = line.split("=")[0]
        assert re.fullmatch(r"[A-Z][A-Z0-9_]*=", line), f"value or bad name in: {name}"


def test_env_example_mentions_required_names() -> None:
    text = (BACKEND / ".env.example").read_text(encoding="utf-8")
    for name in ("OPENAI_API_KEY=", "ABUSEIPDB_API_KEY=", "SOC_DB_URL=", ALLOWED_VALUE):
        assert name in text


@pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")
@pytest.mark.parametrize(
    ("path", "ignored"),
    [
        (".env", True),
        ("backend/.env", True),
        ("backend/.env.local", True),
        ("backend/.env.example", False),
        ("backend/x.sqlite", True),
    ],
)
def test_gitignore(path: str, ignored: bool) -> None:
    result = subprocess.run(  # noqa: S603 — fixed arguments, no user input
        ["git", "check-ignore", "-q", path],  # noqa: S607
        cwd=REPO,
        check=False,
    )
    assert (result.returncode == 0) is ignored
