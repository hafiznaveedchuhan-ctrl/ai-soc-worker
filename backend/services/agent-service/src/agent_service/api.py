"""agent-service internal HTTP API (feature 07).

NOT public: only api-gateway calls it, on the compose network, with the shared `X-Internal-Token`
header. Raw mask values travel only on this internal hop, to the gateway that stores them
encrypted (ADR-0007)."""

import hmac
import json
from collections.abc import AsyncIterable
from typing import Any

from agents.items import ToolApprovalItem
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.sse import EventSourceResponse, ServerSentEvent
from pydantic import BaseModel, Field
from soc_shared.models import AskAnswer, LlmUsage, TriageNote

from agent_service.agents_build import AgentSet
from agent_service.deps import Deps
from agent_service.flows import FlowConfig, FlowResult, run_ask, run_ask_streamed, run_triage


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    user_id: str = Field(min_length=1, max_length=128)
    session_id: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")


class TriageRequest(BaseModel):
    alert_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9._-]+$")
    user_id: str = Field(min_length=1, max_length=128)
    analyst_context: str = Field(default="", max_length=4000)
    # The analyst's decision on a proposed escalation ticket (the CLI asks interactively; the HTTP
    # caller decides up front). False = every proposed ticket is rejected (default, safe).
    approve_escalation_ticket: bool = False


class MaskEntryOut(BaseModel):
    token: str
    kind: str
    value: str


class FlowResponse(BaseModel):
    status: str
    request_id: str
    trace_id: str
    text: str
    answer: AskAnswer | None = None
    note: TriageNote | None = None
    usage: list[LlmUsage]
    mask_entries: list[MaskEntryOut]
    tickets: list[str]
    events: list[str]


def to_response(r: FlowResult) -> FlowResponse:
    return FlowResponse(
        status=r.status,
        request_id=r.request_id,
        trace_id=r.trace_id,
        text=r.text,
        answer=r.answer,
        note=r.note,
        usage=r.usage,
        tickets=r.tickets,
        events=r.events,
        mask_entries=[
            MaskEntryOut(token=e.token, kind=e.kind.value, value=e.value) for e in r.mask_entries
        ],
    )


def create_app(agent_set: AgentSet, cfg: FlowConfig, deps: Deps, internal_token: str) -> FastAPI:
    app = FastAPI(
        title="soc-worker agent-service (internal)",
        version="0.1.0",
        description="Internal only. Called by api-gateway with X-Internal-Token.",
    )

    def check_token(x_internal_token: str = Header(default="")) -> None:
        if not internal_token or not hmac.compare_digest(x_internal_token, internal_token):
            raise HTTPException(status_code=401, detail="invalid internal token")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    async def ready() -> dict[str, Any]:
        return {"status": "ready", "web_search": deps.web is not None}

    @app.post("/v1/ask", response_model=FlowResponse, dependencies=[Depends(check_token)])
    async def ask(req: AskRequest) -> FlowResponse:
        return to_response(
            await run_ask(
                agent_set, cfg, req.question, user_id=req.user_id, session_id=req.session_id
            )
        )

    @app.post(
        "/v1/ask/stream", response_class=EventSourceResponse, dependencies=[Depends(check_token)]
    )
    async def ask_stream(req: AskRequest) -> AsyncIterable[ServerSentEvent]:
        async for chunk in run_ask_streamed(
            agent_set, cfg, req.question, user_id=req.user_id, session_id=req.session_id
        ):
            if chunk.startswith('{"final"'):
                yield ServerSentEvent(data=json.loads(chunk)["final"], event="final")
            else:
                yield ServerSentEvent(data=chunk, event="delta")
        yield ServerSentEvent(raw_data="[DONE]", event="done")

    @app.post("/v1/triage", response_model=FlowResponse, dependencies=[Depends(check_token)])
    async def triage(req: TriageRequest) -> FlowResponse:
        async def decide(item: ToolApprovalItem) -> bool:
            return req.approve_escalation_ticket and item.tool_name == "create_escalation_ticket"

        r = await run_triage(
            agent_set,
            cfg,
            deps,
            req.alert_id,
            user_id=req.user_id,
            analyst_context=req.analyst_context,
            approve=decide,
        )
        return to_response(r)

    return app
