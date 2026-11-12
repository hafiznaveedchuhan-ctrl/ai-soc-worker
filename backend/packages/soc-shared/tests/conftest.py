"""Shared pytest fixtures for soc-shared.

Network is disabled for every test by `--disable-socket` (pytest-socket, configured in
backend/pyproject.toml) — NFR-01-01. Fixture data uses only lab values: documentation IPs
(RFC 5737), RFC 1918 ranges and invented names (NFR-01-06).
"""

import json
from pathlib import Path
from typing import Any

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))
    return data


@pytest.fixture
def win_4625() -> dict[str, Any]:
    return load_fixture("win_4625")


@pytest.fixture
def linux_sshd() -> dict[str, Any]:
    return load_fixture("linux_sshd")


@pytest.fixture
def sysmon_1() -> dict[str, Any]:
    return load_fixture("sysmon_1")
