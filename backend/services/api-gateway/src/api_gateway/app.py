"""api-gateway — the public API (feature 08). Auth, roles, rate limit, CORS, persistence, audit.

Contract for the future handbook widget: OpenAPI at /openapi.json;
send `Authorization: Bearer <Auth0 JWT>`.
Stored text is MASKED; responses to the analyst are UNMASKED here (the analyst may see real values —
they are in his own SIEM — but the AI never did).
"""

import re
import uuid
from collections.abc import AsyncIterable
from typing import Any, Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel, Field
from soc_shared.masking.patterns import TOKEN_RE
from sqlalchemy import func, text
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, select

from api_gateway.agent_client import AgentClient
from api_gateway.auth import Authenticator, Principal
from api_gateway.crypto import MaskVault
from api_gateway.db import (
    AlertSeen,
    AuditLog,
    Conversation,
    DecisionRow,
    LlmUsageRow,
    MaskMapRow,
    TriageNoteRow,
    User,
    now,
)
from api_gateway.ratelimit import RateLimiter
from api_gateway.settings import GatewaySettings


class AskIn(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = Field(default=None, pattern=r"^[A-Za-z0-9_-]{1,64}$")


class TriageIn(BaseModel):
    analyst_context: str = Field(default="", max_length=4000)
    approve_escalation_ticket: bool = False


class DecisionIn(BaseModel):
    action: Literal["approve", "change", "escalate"]
    comment: str | None = Field(default=None, max_length=4000)


def create_app(
    settings: GatewaySettings,
    engine: Engine,
    agent: AgentClient,
    authenticator: Authenticator | None = None,
) -> FastAPI:
    app = FastAPI(
        title="soc-worker API",
        version="0.1.0",
        description="AI SOC Triage Copilot. The AI suggests; a human analyst decides.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )
    SQLModel.metadata.create_all(engine)  # no-op on Neon once Alembic has migrated
    auth = authenticator or Authenticator(
        settings.auth_mode, settings.auth0_domain, settings.auth0_audience, settings.role_claim
    )
    vault = MaskVault(settings.mask_map_key.get_secret_value()) if settings.mask_map_key else None
    limiter = RateLimiter(settings.rate_limit_per_minute)

    def session() -> Any:
        with Session(engine) as s:
            yield s

    def audit(
        s: Session,
        user: User | None,
        event: str,
        request_id: str | None = None,
        trace_id: str | None = None,
        **detail: Any,
    ) -> None:
        s.add(
            AuditLog(
                user_id=user.id if user else None,
                event=event,
                request_id=request_id,
                trace_id=trace_id,
                detail=detail,
            )
        )

    def current_user(
        authorization: str | None = Header(default=None),
        x_dev_user: str | None = Header(default=None),
        s: Session = Depends(session),
    ) -> User:
        p: Principal = auth.authenticate(authorization, x_dev_user)
        user = s.exec(select(User).where(User.auth0_sub == p.sub)).first()
        if user is None:
            user = User(auth0_sub=p.sub, email=p.email, role=p.role)
            s.add(user)
            audit(s, None, "user_created", sub=p.sub)
        elif user.role != p.role or (p.email and user.email != p.email):
            user.role, user.email = p.role, p.email or user.email
        s.commit()
        s.refresh(user)
        return user

    def limited(user: User = Depends(current_user)) -> User:
        if not limiter.allow(str(user.id)):
            raise HTTPException(429, "rate limit: too many requests per minute")
        return user

    def store_run(s: Session, data: dict[str, Any]) -> dict[str, str]:
        rid = data["request_id"]
        for u in data.get("usage", []):
            s.add(
                LlmUsageRow(
                    request_id=rid,
                    agent=u["agent"],
                    model=u["model"],
                    input_tokens=u["input_tokens"],
                    output_tokens=u["output_tokens"],
                    cost_usd=u["cost_usd"],
                )
            )
        mapping: dict[str, str] = {}
        for e in data.get("mask_entries", []):
            mapping[e["token"]] = e["value"]
            if vault is None:
                raise HTTPException(500, "MASK_MAP_KEY is not configured")
            s.add(
                MaskMapRow(
                    request_id=rid,
                    token=e["token"],
                    kind=e["kind"],
                    value_encrypted=vault.seal(e["value"]),
                )
            )
        return mapping

    def load_mapping(s: Session, request_id: str) -> dict[str, str]:
        if vault is None:
            return {}
        rows = s.exec(select(MaskMapRow).where(MaskMapRow.request_id == request_id)).all()
        return {r.token: v for r in rows if (v := vault.open(r.value_encrypted)) is not None}

    def unmask(text_: str, mapping: dict[str, str]) -> str:
        return TOKEN_RE.sub(lambda m: mapping.get(m.group(), m.group()), text_)

    def budget_left(s: Session) -> None:
        spent = s.exec(select(func.coalesce(func.sum(LlmUsageRow.cost_usd), 0.0))).one()
        if float(spent) >= settings.total_budget_usd:
            raise HTTPException(402, f"LLM budget reached (${float(spent):.2f})")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    async def ready(s: Session = Depends(session)) -> dict[str, Any]:
        db_ok = s.exec(select(text("1"))).first() is not None
        agent_ok = await agent.healthy()
        if not (db_ok and agent_ok):
            raise HTTPException(503, {"db": db_ok, "agent_service": agent_ok})
        return {"status": "ready", "db": db_ok, "agent_service": agent_ok}

    @app.get("/me")
    def me(user: User = Depends(current_user)) -> dict[str, Any]:
        return {"id": user.id, "sub": user.auth0_sub, "email": user.email, "role": user.role}

    def ask_prepare(
        body: AskIn, user: User = Depends(limited), s: Session = Depends(session)
    ) -> str:
        """Runs BEFORE the stream starts, so 402/403 become real HTTP status codes."""
        budget_left(s)
        conv_id = body.conversation_id or uuid.uuid4().hex[:16]
        conv = s.get(Conversation, conv_id)
        if conv is None:
            conv = Conversation(id=conv_id, user_id=user.id or 0)
        elif conv.user_id != user.id:
            raise HTTPException(403, "not your conversation")
        conv.last_at = now()
        s.add(conv)
        s.commit()
        return conv_id

    @app.post("/ask", response_class=EventSourceResponse)
    async def ask(
        body: AskIn,
        conv_id: str = Depends(ask_prepare),
        user: User = Depends(limited),
        s: Session = Depends(session),
    ) -> AsyncIterable[ServerSentEvent]:
        yield ServerSentEvent(
            data={"conversation_id": conv_id, "status": "thinking"}, event="status"
        )
        data = await agent.ask(body.question, str(user.id), conv_id)
        mapping = store_run(s, data)
        audit(
            s,
            user,
            f"ask_{data['status']}",
            data["request_id"],
            data["trace_id"],
            scope=(data.get("answer") or {}).get("scope"),
        )
        s.commit()
        answer = dict(data.get("answer") or {})
        answer["answer"] = unmask(answer.get("answer", data["text"]), mapping)
        yield ServerSentEvent(
            data={
                "status": data["status"],
                "request_id": data["request_id"],
                "conversation_id": conv_id,
                "answer": answer,
            },
            event="final",
        )
        yield ServerSentEvent(raw_data="[DONE]", event="done")

    @app.post("/triage/{alert_id}")
    async def triage(
        alert_id: str, body: TriageIn, user: User = Depends(limited), s: Session = Depends(session)
    ) -> dict[str, Any]:
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,64}", alert_id):
            raise HTTPException(422, "invalid alert id")
        budget_left(s)
        data = await agent.triage(
            alert_id, str(user.id), body.analyst_context, body.approve_escalation_ticket
        )
        mapping = store_run(s, data)
        note = data.get("note")
        if note and s.get(AlertSeen, alert_id) is None:
            s.add(AlertSeen(alert_id=alert_id, rule_id=note["rule_id"], level=note["rule_level"]))
        row = TriageNoteRow(
            alert_id=alert_id,
            request_id=data["request_id"],
            created_by=user.id or 0,
            status=data["status"],
            summary=(note or {}).get("summary", ""),
            verdict_suggestion=(note or {}).get("verdict_suggestion"),
            confidence=(note or {}).get("confidence"),
            severity=(note or {}).get("severity"),
            escalate=(note or {}).get("escalate"),
            escalate_condition=(note or {}).get("escalate_condition"),
            note=note,
            note_text=data["text"],
            tickets=data.get("tickets", []),
            trace_id=data["trace_id"],
        )
        s.add(row)
        audit(
            s,
            user,
            f"triage_{data['status']}",
            data["request_id"],
            data["trace_id"],
            alert_id=alert_id,
            tickets=data.get("tickets", []),
        )
        s.commit()
        s.refresh(row)
        return {
            "note_id": row.id,
            "status": row.status,
            "alert_id": alert_id,
            "note_text": unmask(row.note_text, mapping),
            "note": note,
            "tickets": row.tickets,
            "final_decision_by": "human",
        }

    def visible(s: Session, user: User, note_id: int) -> TriageNoteRow:
        row = s.get(TriageNoteRow, note_id)
        if row is None or (user.role != "admin" and row.created_by != user.id):
            raise HTTPException(404, "note not found")
        return row

    @app.get("/notes")
    def notes(
        user: User = Depends(current_user), s: Session = Depends(session), limit: int = 50
    ) -> list[dict[str, Any]]:
        q = select(TriageNoteRow).order_by(TriageNoteRow.id.desc()).limit(min(max(limit, 1), 200))  # type: ignore[union-attr]
        if user.role != "admin":
            q = q.where(TriageNoteRow.created_by == user.id)
        return [
            {
                "id": r.id,
                "alert_id": r.alert_id,
                "status": r.status,
                "verdict": r.verdict_suggestion,
                "severity": r.severity,
                "escalate": r.escalate,
                "created_at": r.created_at.isoformat(),
            }
            for r in s.exec(q).all()
        ]

    @app.get("/notes/{note_id}")
    def note_detail(
        note_id: int, user: User = Depends(current_user), s: Session = Depends(session)
    ) -> dict[str, Any]:
        row = visible(s, user, note_id)
        decisions = s.exec(select(DecisionRow).where(DecisionRow.note_id == note_id)).all()
        audit(s, user, "note_viewed", row.request_id, note_id=note_id)
        s.commit()
        return {
            "id": row.id,
            "alert_id": row.alert_id,
            "status": row.status,
            "note_text": unmask(row.note_text, load_mapping(s, row.request_id)),
            "note": row.note,
            "tickets": row.tickets,
            "final_decision_by": "human",
            "decisions": [
                {
                    "action": d.action,
                    "comment": d.comment,
                    "by": d.user_id,
                    "at": d.created_at.isoformat(),
                }
                for d in decisions
            ],
        }

    @app.post("/notes/{note_id}/decision")
    def decide(
        note_id: int, body: DecisionIn, user: User = Depends(limited), s: Session = Depends(session)
    ) -> dict[str, Any]:
        row = visible(s, user, note_id)
        d = DecisionRow(
            note_id=note_id, user_id=user.id or 0, action=body.action, comment=body.comment
        )
        s.add(d)
        audit(s, user, f"decision_{body.action}", row.request_id, note_id=note_id)
        s.commit()
        s.refresh(d)
        return {
            "decision_id": d.id,
            "note_id": note_id,
            "action": d.action,
            "decided_by": user.auth0_sub,
        }

    @app.exception_handler(Exception)
    async def _safe_errors(request: Request, exc: Exception) -> Any:  # never leak internals
        from fastapi.responses import JSONResponse

        return JSONResponse({"detail": "internal error"}, status_code=500)

    return app
