"""Scope labels and the Scope Guard verdict (FR-01-18, ADR-0002)."""

from typing import Literal

from pydantic import Field

from soc_shared.models._base import ValueModel

ScopeLabel = Literal["ALLOW_KSOR", "ALLOW_CYBER_RESEARCH", "DECLINE"]

ScopeCategory = Literal[
    "ksor",
    "defensive_research",
    "non_cyber",
    "offensive",
    "legal_compliance",
    "pricing",
    "prompt_injection",
]

# The exact decline reply (constitution Art. V). Tests compare it byte for byte.
DECLINE_MESSAGE = (
    "This is a SOC Analyst Lab. Please ask only cybersecurity-related questions. JazakAllah."
)


class ScopeVerdict(ValueModel):
    label: ScopeLabel
    reason: str = Field(max_length=300)
    injection_suspected: bool = False
    category: ScopeCategory | None = None
