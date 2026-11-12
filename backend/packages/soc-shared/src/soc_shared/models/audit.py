"""Human decisions, the audit trail and LLM usage records (FR-01-19)."""

from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from soc_shared.models._base import StrictModel, ValueModel


class Decision(StrictModel):
    note_id: str
    action: Literal["approve", "change", "escalate"]
    comment: str | None = None
    decided_by: str  # the human's user id — the AI never decides
    decided_at: datetime


class AuditEvent(StrictModel):
    event: str
    at: datetime
    user_id: str | None = None
    request_id: str | None = None
    trace_id: str | None = None
    detail: dict[str, Any] = Field(default_factory=dict)  # masked values only


class LlmUsage(ValueModel):
    request_id: str
    agent: str
    model: str
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    cost_usd: float = Field(ge=0.0)
