"""A passage returned by the handbook (KSOR) MCP `search` tool (FR-01-13)."""

from typing import Literal

from pydantic import Field

from soc_shared.models._base import ValueModel

STABLE_ID_PATTERN = r"^knowledge/[a-z0-9][a-z0-9/_-]*$"


class KsorHit(ValueModel):
    stable_id: str = Field(pattern=STABLE_ID_PATTERN)  # provenance.stable_id — what we cite
    title: str
    snippet: str
    score: float | None = None
    gate: Literal["off", "on"] = "off"  # the handbook's abstention gate is OFF (decision C)
    heading: str | None = None
