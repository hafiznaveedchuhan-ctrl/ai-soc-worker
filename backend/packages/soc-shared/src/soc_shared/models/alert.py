"""Wazuh alert shapes (FR-01-10) and the masked form handed to agents (FR-01-11).

Wazuh adds fields between versions and decoders, so the raw alert models allow extra fields.
The masked form is strict: it is built only by `soc_shared.masking.mask_alert`.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from soc_shared.models._base import StrictModel


class _WazuhBase(BaseModel):
    model_config = ConfigDict(extra="allow")


class WazuhMitre(_WazuhBase):
    id: list[str] = Field(default_factory=list)
    tactic: list[str] = Field(default_factory=list)
    technique: list[str] = Field(default_factory=list)


class WazuhRule(_WazuhBase):
    id: str
    level: int = Field(ge=0, le=15)  # Wazuh rule levels are 0–15
    description: str
    groups: list[str] = Field(default_factory=list)
    mitre: WazuhMitre = Field(default_factory=WazuhMitre)


class WazuhAgent(_WazuhBase):
    id: str
    name: str
    ip: str | None = None


class WazuhAlert(_WazuhBase):
    """One alert as stored by the Wazuh indexer (`wazuh-alerts-*`)."""

    id: str
    timestamp: datetime
    rule: WazuhRule
    agent: WazuhAgent
    location: str | None = None
    decoder: dict[str, Any] | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    full_log: str | None = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def _normalise_offset(cls, value: Any) -> Any:
        # Wazuh writes "+0000"; ISO 8601 parsers want "+00:00".
        if isinstance(value, str) and len(value) > 5 and value[-5] in "+-" and value[-4:].isdigit():
            return f"{value[:-2]}:{value[-2:]}"
        return value


class MaskedAlert(StrictModel):
    """An alert after masking. It is the ONLY alert form that may reach an LLM."""

    alert_id: str
    rule_id: str
    rule_level: int = Field(ge=0, le=15)
    payload: dict[str, Any]
    ip_context: dict[str, str] = Field(default_factory=dict)  # "<IP-1>" -> "private 10.0.0.0/8"
    dropped_fields: list[str] = Field(default_factory=list)
