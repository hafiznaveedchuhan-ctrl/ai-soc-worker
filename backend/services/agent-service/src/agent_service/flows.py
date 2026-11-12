"""The two flows (feature 05): /ask (handoff pattern) and /triage (agents-as-tools pattern).

Both: mask first (code) → Runner with RunConfig(trace_include_sensitive_data=False) → one trace per
request → hooks price every call → guardrail trips and limits become safe, logged results.
"""

import json
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass, field
from pathlib import Path

from agents import (
    InputGuardrailTripwireTriggered,
    MaxTurnsExceeded,
    OutputGuardrailTripwireTriggered,
    RunConfig,
    Runner,
    SQLiteSession,
    trace,
)
from agents.items import ToolApprovalItem
from soc_shared.masking import MaskEntry, mask_alert, mask_text
from soc_shared.models import DECLINE_MESSAGE, AskAnswer, LlmUsage, TriageNote, WazuhAlert

from agent_service.agents_build import AgentSet
from agent_service.budget import BudgetExceeded, Ledger, RunBudget
from agent_service.context import WorkerContext
from agent_service.deps import Deps, PortError
from agent_service.guardrails import SAFE_FALLBACK
from agent_service.hooks import CostHooks

Approver = Callable[[ToolApprovalItem], Awaitable[bool]]


@dataclass
class FlowConfig:
    prices: dict[str, tuple[float, float]]
    run_budget_usd: float
    max_turns: int
    ledger: Ledger | None = None
    sessions_db: Path | str = ":memory:"
    # One SQLiteSession per analyst conversation. ":memory:" databases live inside the object,
    # so the objects are kept here; a file path survives restarts (ADR-0008: Phase 8 → Postgres).
    _sessions: dict[str, SQLiteSession] = field(default_factory=dict)

    def session(self, key: str) -> SQLiteSession:
        if key not in self._sessions:
            self._sessions[key] = SQLiteSession(key, self.sessions_db)
        return self._sessions[key]


@dataclass
class FlowResult:
    status: str  # ok | declined | blocked | max_turns | budget | error
    request_id: str
    trace_id: str
    answer: AskAnswer | None = None
    note: TriageNote | None = None
    text: str = ""
    usage: list[LlmUsage] = field(default_factory=list)
    mask_entries: list[MaskEntry] = field(default_factory=list)
    tickets: list[str] = field(default_factory=list)
    events: list[str] = field(default_factory=list)


def _ctx(cfg: FlowConfig, flow: str, user_id: str) -> WorkerContext:
    rid = uuid.uuid4().hex[:12]
    if cfg.ledger is not None:
        cfg.ledger.check_open()
    return WorkerContext(
        request_id=rid,
        user_id=user_id,
        flow=flow,  # type: ignore[arg-type]
        budget=RunBudget(cfg.run_budget_usd, cfg.prices, rid, cfg.ledger),
    )


def _run_config(name: str, ctx: WorkerContext) -> RunConfig:
    return RunConfig(
        workflow_name=name,
        trace_include_sensitive_data=False,
        trace_metadata={"request_id": ctx.request_id, "flow": ctx.flow},
    )


def _done(
    ctx: WorkerContext,
    trace_id: str,
    status: str,
    *,
    answer: AskAnswer | None = None,
    note: TriageNote | None = None,
    text: str = "",
) -> FlowResult:
    return FlowResult(
        status=status,
        request_id=ctx.request_id,
        trace_id=trace_id,
        answer=answer,
        note=note,
        text=text,
        usage=list(ctx.budget.usage),
        mask_entries=ctx.mask_map.to_storage(),
        tickets=list(ctx.tickets),
        events=list(ctx.events),
    )


def _fallback_answer(ctx: WorkerContext, text: str) -> AskAnswer:
    scope = ctx.scope.label if ctx.scope and ctx.scope.label != "DECLINE" else "ALLOW_KSOR"
    return AskAnswer(answer=text, scope=scope, not_in_record=True, confidence=0.0)


async def run_ask(
    app: AgentSet, cfg: FlowConfig, question: str, *, user_id: str, session_id: str
) -> FlowResult:
    ctx = _ctx(cfg, "ask", user_id)
    masked = mask_text(question, ctx.mask_map)
    session = cfg.session(f"ask-{session_id}")
    hooks = CostHooks(app.model_names)
    with trace("soc-ask", metadata={"request_id": ctx.request_id}) as t:
        try:
            r = await Runner.run(
                app.ask_entry,
                masked,
                context=ctx,
                hooks=hooks,
                session=session,
                max_turns=cfg.max_turns,
                run_config=_run_config("soc-ask", ctx),
            )
            answer = r.final_output_as(AskAnswer)
            return _done(ctx, t.trace_id, "ok", answer=answer, text=answer.answer)
        except InputGuardrailTripwireTriggered:
            ans = AskAnswer(answer=DECLINE_MESSAGE, scope="DECLINE", confidence=1.0)
            return _done(ctx, t.trace_id, "declined", answer=ans, text=DECLINE_MESSAGE)
        except OutputGuardrailTripwireTriggered:
            ans = _fallback_answer(ctx, SAFE_FALLBACK)
            return _done(ctx, t.trace_id, "blocked", answer=ans, text=SAFE_FALLBACK)
        except MaxTurnsExceeded:
            ans = _fallback_answer(
                ctx, "The assistant took too many steps and stopped. Please rephrase."
            )
            return _done(ctx, t.trace_id, "max_turns", answer=ans, text=ans.answer)
        except BudgetExceeded as exc:
            ans = _fallback_answer(ctx, f"Stopped: {exc}.")
            return _done(ctx, t.trace_id, "budget", answer=ans, text=ans.answer)


async def run_ask_streamed(
    app: AgentSet, cfg: FlowConfig, question: str, *, user_id: str, session_id: str
) -> AsyncIterator[str]:
    """Streaming variant (future chat widget): yields text deltas, then the final answer JSON."""
    ctx = _ctx(cfg, "ask", user_id)
    masked = mask_text(question, ctx.mask_map)
    session = cfg.session(f"ask-{session_id}")
    with trace("soc-ask-stream", metadata={"request_id": ctx.request_id}):
        try:
            result = Runner.run_streamed(
                app.ask_entry,
                masked,
                context=ctx,
                hooks=CostHooks(app.model_names),
                session=session,
                max_turns=cfg.max_turns,
                run_config=_run_config("soc-ask-stream", ctx),
            )
            async for event in result.stream_events():
                if (
                    event.type == "raw_response_event"
                    and getattr(event.data, "type", "") == "response.output_text.delta"
                ):
                    yield str(getattr(event.data, "delta", ""))
            yield json.dumps({"final": result.final_output_as(AskAnswer).model_dump()})
        except InputGuardrailTripwireTriggered:
            yield json.dumps(
                {
                    "final": AskAnswer(
                        answer=DECLINE_MESSAGE, scope="DECLINE", confidence=1.0
                    ).model_dump()
                }
            )
        except (OutputGuardrailTripwireTriggered, MaxTurnsExceeded, BudgetExceeded):
            yield json.dumps({"final": _fallback_answer(ctx, SAFE_FALLBACK).model_dump()})


async def _deny_all(item: ToolApprovalItem) -> bool:
    return False


async def run_triage(
    app: AgentSet,
    cfg: FlowConfig,
    deps: Deps,
    alert_id: str,
    *,
    user_id: str,
    analyst_context: str = "",
    approve: Approver = _deny_all,
) -> FlowResult:
    ctx = _ctx(cfg, "triage", user_id)
    with trace("soc-triage", metadata={"request_id": ctx.request_id}) as t:
        try:
            raw = await deps.wazuh.get_alert(alert_id)
        except PortError as exc:
            return _done(ctx, t.trace_id, "error", text=f"alert unavailable: {exc}")
        masked = mask_alert(WazuhAlert.model_validate(raw), ctx.mask_map)
        ctx.alert_rule_level = masked.rule_level
        ctx.alert_mitre = list(WazuhAlert.model_validate(raw).rule.mitre.id)
        payload = {
            "alert": masked.payload,
            "ip_context": masked.ip_context,
            "analyst_context": mask_text(analyst_context, ctx.mask_map) or None,
        }
        session = SQLiteSession(f"triage-{alert_id}-{ctx.request_id}")  # a fresh session per alert
        hooks = CostHooks(app.model_names)
        try:
            r = await Runner.run(
                app.triage_entry,
                json.dumps(payload),
                context=ctx,
                hooks=hooks,
                session=session,
                max_turns=cfg.max_turns,
                run_config=_run_config("soc-triage", ctx),
            )
            while (
                r.interruptions
            ):  # needs_approval: the human approves or rejects in the terminal/UI
                state = r.to_state()
                for item in r.interruptions:
                    if await approve(item):
                        state.approve(item)
                        ctx.events.append(f"approved {item.tool_name}")
                    else:
                        state.reject(item)
                        ctx.events.append(f"rejected {item.tool_name}")
                r = await Runner.run(
                    app.triage_entry,
                    state,
                    context=ctx,
                    hooks=hooks,
                    session=session,
                    max_turns=cfg.max_turns,
                    run_config=_run_config("soc-triage", ctx),
                )
            note = r.final_output_as(TriageNote)
            return _done(ctx, t.trace_id, "ok", note=note, text=note.to_text())
        except InputGuardrailTripwireTriggered:
            return _done(ctx, t.trace_id, "blocked", text="input contained unmasked data; not sent")
        except OutputGuardrailTripwireTriggered as exc:
            problems = exc.guardrail_result.output.output_info
            ctx.events.append(f"review problems: {problems}")
            return _done(ctx, t.trace_id, "blocked", text=SAFE_FALLBACK)
        except MaxTurnsExceeded:
            return _done(
                ctx, t.trace_id, "max_turns", text="Stopped after too many steps. " + SAFE_FALLBACK
            )
        except BudgetExceeded as exc:
            return _done(ctx, t.trace_id, "budget", text=f"Stopped: {exc}. " + SAFE_FALLBACK)
