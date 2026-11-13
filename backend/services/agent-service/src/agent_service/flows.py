"""The two flows (feature 05): /ask (handoff pattern) and /triage (agents-as-tools pattern).

Both: mask first (code) → Runner with RunConfig(trace_include_sensitive_data=False) → one trace per
request → hooks price every call → guardrail trips and limits become safe, logged results.
"""

import json
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agents import (
    AgentsException,
    InputGuardrailTripwireTriggered,
    ItemHelpers,
    MaxTurnsExceeded,
    MessageOutputItem,
    ModelBehaviorError,
    OutputGuardrailTripwireTriggered,
    RunConfig,
    RunErrorHandlerInput,
    RunErrorHandlers,
    Runner,
    SQLiteSession,
    trace,
)
from agents.items import ToolApprovalItem
from pydantic import BaseModel, ValidationError
from soc_shared.masking import MaskEntry, mask_alert, mask_text
from soc_shared.models import DECLINE_MESSAGE, AskAnswer, LlmUsage, TriageNote, WazuhAlert

from agent_service.agents_build import AgentSet
from agent_service.budget import BudgetExceeded, Ledger, RunBudget
from agent_service.context import WorkerContext
from agent_service.deps import Deps, PortError
from agent_service.guardrails import SAFE_FALLBACK
from agent_service.hooks import CostHooks

Approver = Callable[[ToolApprovalItem], Awaitable[bool]]
NOTE_RETRIES = 1  # one corrective retry when the TriageNote breaks a model rule (R3, Naveed Q1)


def rule_problems(text: str, model: type[BaseModel]) -> list[str]:
    """Re-validate a rejected final output and return ONLY the rule messages + field paths.

    The SDK redacts the payload (good); we need the reason to let the model correct itself.
    `include_input=False` keeps every value (masked or not) out of the messages."""
    try:
        model.model_validate_json(text)
    except ValidationError as exc:
        return [
            f"{'.'.join(str(p) for p in e['loc']) or 'note'}: {e['msg']}"[:200]
            for e in exc.errors(include_input=False, include_url=False)
        ][:5]
    except ValueError:
        return ["output is not valid JSON"]
    return []


def _unexpected(exc: Exception) -> str:
    """One masked-safe breadcrumb for an unexpected error (type + the first part of the message;
    API error messages name parameters, not prompt content)."""
    return f"unexpected {type(exc).__name__}: {exc}"[:240]


def policy_hints(rule_level: int | None) -> list[str]:
    """Code-computed escalation-policy facts the model must not miss (pilot: EV-A034)."""
    if rule_level is not None and rule_level >= 12:
        return [
            f"rule level {rule_level} >= 12 → escalation policy condition 1: "
            "escalate=true and escalate_condition=1"
        ]
    return []


def _retry_task(payload: dict[str, Any], problems: list[str]) -> str:
    return json.dumps(
        {
            **payload,
            "previous_attempt_rejected_because": problems,
            "instruction": "Return a corrected TriageNote (follow these rules).",
        }
    )


def _capture_problems(model: type[BaseModel]) -> RunErrorHandlers[WorkerContext]:
    def on_invalid(data: RunErrorHandlerInput[WorkerContext]) -> None:
        msgs = [i for i in data.run_data.new_items if isinstance(i, MessageOutputItem)]
        text = ItemHelpers.text_message_output(msgs[-1]) if msgs else ""
        data.context.context.output_problems = rule_problems(text, model) or ["invalid output"]
        return None  # keep the SDK behaviour: raise ModelBehaviorError; the flow decides

    return {"invalid_final_output": on_invalid}


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
                error_handlers=_capture_problems(AskAnswer),
            )
            answer = r.final_output_as(AskAnswer)
            return _done(ctx, t.trace_id, "ok", answer=answer, text=answer.answer)
        except InputGuardrailTripwireTriggered:
            ans = AskAnswer(answer=DECLINE_MESSAGE, scope="DECLINE", confidence=1.0)
            return _done(ctx, t.trace_id, "declined", answer=ans, text=DECLINE_MESSAGE)
        except OutputGuardrailTripwireTriggered as exc:
            ctx.events.append(f"review problems: {exc.guardrail_result.output.output_info}"[:400])
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
        except ModelBehaviorError:
            # ONE corrective retry (R3c, T11-20): straight to the specialist the Scope Guard chose,
            # so the scope classifier does not run (or charge) twice. Masked question + rule text.
            problems = ctx.output_problems or ["invalid output"]
            ctx.events.append(f"invalid answer: {problems}; retrying once")
            ctx.output_problems = []
            specialist = (
                app.research
                if ctx.scope and ctx.scope.label == "ALLOW_CYBER_RESEARCH"
                else app.handbook
            )
            retry_input = (
                f"{masked}\n\n(Your previous answer was rejected: {'; '.join(problems)}. "
                "Return a valid answer: cite a handbook stable_id, list web sources, or set "
                "not_in_record=true.)"
            )
            try:
                r = await Runner.run(
                    specialist,
                    retry_input,
                    context=ctx,
                    hooks=hooks,
                    max_turns=cfg.max_turns,
                    run_config=_run_config("soc-ask", ctx),
                    error_handlers=_capture_problems(AskAnswer),
                )
                answer = r.final_output_as(AskAnswer)
                return _done(ctx, t.trace_id, "ok", answer=answer, text=answer.answer)
            except Exception as exc:  # guardrail, agent or API error on the retry
                ctx.events.append(f"retry failed {type(exc).__name__}: {ctx.output_problems}")
                ans = _fallback_answer(
                    ctx, "The assistant produced an invalid answer. " + SAFE_FALLBACK
                )
                return _done(ctx, t.trace_id, "error", answer=ans, text=ans.answer)
        except AgentsException as exc:  # other agent errors: keep the usage already spent
            ctx.events.append(f"agent error {type(exc).__name__}: {ctx.output_problems}")
            ans = _fallback_answer(
                ctx, "The assistant produced an invalid answer. " + SAFE_FALLBACK
            )
            return _done(ctx, t.trace_id, "error", answer=ans, text=ans.answer)
        except Exception as exc:  # e.g. openai.BadRequestError (R5: 43 probes left
            # no trace because a 400 escaped the flow). Keep usage + events; never crash the caller.
            ctx.events.append(_unexpected(exc))
            ans = _fallback_answer(ctx, "The assistant failed. " + SAFE_FALLBACK)
            return _done(ctx, t.trace_id, "error", answer=ans, text=ans.answer)


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
        payload: dict[str, Any] = {
            "alert": masked.payload,
            "ip_context": masked.ip_context,
            "analyst_context": mask_text(analyst_context, ctx.mask_map) or None,
        }
        rule = WazuhAlert.model_validate(raw).rule
        rule_text = mask_text(rule.description, ctx.mask_map)
        ctx.review_input = f"Rule {rule.id} (level {masked.rule_level}): {rule_text}" + (
            f"\nAnalyst context: {payload['analyst_context']}" if payload["analyst_context"] else ""
        )
        hints = policy_hints(masked.rule_level)
        if hints:
            payload["policy_hints"] = hints
        hooks = CostHooks(app.model_names)
        handlers = _capture_problems(TriageNote)
        retries = NOTE_RETRIES
        task = json.dumps(payload)
        try:
            while True:
                # a fresh session per alert attempt: no memory across alerts or attempts
                session = SQLiteSession(f"triage-{alert_id}-{ctx.request_id}-{retries}")
                try:
                    r = await Runner.run(
                        app.triage_entry,
                        task,
                        context=ctx,
                        hooks=hooks,
                        session=session,
                        max_turns=cfg.max_turns,
                        run_config=_run_config("soc-triage", ctx),
                        error_handlers=handlers,
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
                            error_handlers=handlers,
                        )
                    break
                except OutputGuardrailTripwireTriggered as exc:
                    info = exc.guardrail_result.output.output_info or {}
                    if info.get("source") != "rules" or retries <= 0:
                        raise  # LLM-reviewer problems (softer) or no retry left → blocked below
                    problems = list(info.get("problems", []))
                    ctx.events.append(f"note failed the rules: {problems}"[:400])
                    retries -= 1
                    ctx.events.append("retrying once with the rule messages")
                    task = _retry_task(payload, problems)
                except ModelBehaviorError:
                    problems = ctx.output_problems or ["invalid output"]
                    ctx.events.append(f"invalid note: {problems}")
                    if retries <= 0:
                        return _done(
                            ctx,
                            t.trace_id,
                            "error",
                            text="The note broke the template rules twice. " + SAFE_FALLBACK,
                        )
                    retries -= 1
                    ctx.output_problems = []
                    ctx.events.append("retrying once with the rule messages")
                    task = _retry_task(payload, problems)
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
        except AgentsException as exc:  # keep the usage already spent (R3 F1)
            ctx.events.append(f"agent error {type(exc).__name__}")
            return _done(ctx, t.trace_id, "error", text="Agent error. " + SAFE_FALLBACK)
        except Exception as exc:  # API/transport errors keep usage + events too
            ctx.events.append(_unexpected(exc))
            return _done(ctx, t.trace_id, "error", text="Agent error. " + SAFE_FALLBACK)
