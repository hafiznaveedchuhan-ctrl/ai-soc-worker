"""Database (SQLModel on Neon Postgres `soc_worker`; SQLite in tests). Only api-gateway connects.

Text and JSON stored here are MASKED; raw values live only in `mask_map.value_encrypted` (Fernet).
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, Column
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Field, SQLModel, create_engine


def now() -> datetime:
    return datetime.now(UTC)


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    auth0_sub: str = Field(index=True, unique=True, max_length=255)
    email: str | None = Field(default=None, max_length=320)
    role: str = Field(default="analyst", max_length=32)
    created_at: datetime = Field(default_factory=now)


class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    id: str = Field(primary_key=True, max_length=64)
    user_id: int = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=now)
    last_at: datetime = Field(default_factory=now)


class AlertSeen(SQLModel, table=True):
    __tablename__ = "alerts_seen"
    alert_id: str = Field(primary_key=True, max_length=64)
    first_seen: datetime = Field(default_factory=now)
    rule_id: str = Field(max_length=32)
    level: int
    source: str = Field(default="fixture", max_length=16)


class TriageNoteRow(SQLModel, table=True):
    __tablename__ = "triage_notes"
    id: int | None = Field(default=None, primary_key=True)
    alert_id: str = Field(index=True, max_length=64)
    request_id: str = Field(index=True, max_length=32)
    created_by: int = Field(foreign_key="users.id")
    status: str = Field(max_length=16)
    summary: str = ""
    verdict_suggestion: str | None = Field(default=None, max_length=16)
    confidence: float | None = None
    severity: str | None = Field(default=None, max_length=16)
    escalate: bool | None = None
    escalate_condition: int | None = None
    note: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))  # masked TriageNote
    note_text: str = ""  # masked, handbook template
    tickets: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    final_decision_by: str = Field(default="human", max_length=16)
    trace_id: str = Field(default="", max_length=64)
    created_at: datetime = Field(default_factory=now)


class DecisionRow(SQLModel, table=True):
    __tablename__ = "decisions"
    id: int | None = Field(default=None, primary_key=True)
    note_id: int = Field(foreign_key="triage_notes.id", index=True)
    user_id: int = Field(foreign_key="users.id")
    action: str = Field(max_length=16)  # approve | change | escalate
    comment: str | None = Field(default=None, max_length=4000)
    created_at: datetime = Field(default_factory=now)


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"
    id: int | None = Field(default=None, primary_key=True)
    at: datetime = Field(default_factory=now)
    user_id: int | None = Field(default=None, foreign_key="users.id")
    event: str = Field(max_length=64)
    request_id: str | None = Field(default=None, max_length=32)
    trace_id: str | None = Field(default=None, max_length=64)
    detail: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))  # masked only


class LlmUsageRow(SQLModel, table=True):
    __tablename__ = "llm_usage"
    id: int | None = Field(default=None, primary_key=True)
    at: datetime = Field(default_factory=now)
    request_id: str = Field(index=True, max_length=32)
    agent: str = Field(max_length=64)
    model: str = Field(max_length=64)
    input_tokens: int
    output_tokens: int
    cost_usd: float


class MaskMapRow(SQLModel, table=True):
    __tablename__ = "mask_map"
    id: int | None = Field(default=None, primary_key=True)
    request_id: str = Field(index=True, max_length=32)
    token: str = Field(max_length=32)
    kind: str = Field(max_length=8)
    value_encrypted: str  # Fernet token; never stored or logged in clear
    created_at: datetime = Field(default_factory=now)


def make_engine(url: str) -> Engine:
    if url.startswith("sqlite"):
        if url in ("sqlite://", "sqlite:///:memory:"):
            return create_engine(
                url, connect_args={"check_same_thread": False}, poolclass=StaticPool
            )
        return create_engine(url, connect_args={"check_same_thread": False})
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url.removeprefix("postgresql://")  # psycopg 3 driver
    return create_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 10})  # WSL+Neon
