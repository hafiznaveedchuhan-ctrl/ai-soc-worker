"""All four guardrail kinds (feature 06, ADR-0002, ADR-0007).

1 INPUT  scope guard (blocking: run_in_parallel=False → no tool or model cost before it decides)
2 OUTPUT note/answer reviewer (deterministic checks + optional LLM reflection)
3 TOOL INPUT  ksor query · ip token · web query
4 TOOL OUTPUT web content · ip reputation schema
"""

import json
import re
from collections.abc import Awaitable, Callable
from typing import Any

from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    ToolGuardrailFunctionOutput,
    ToolInputGuardrailData,
    ToolOutputGuardrailData,
    TResponseInputItem,
    input_guardrail,
    output_guardrail,
    tool_input_guardrail,
    tool_output_guardrail,
)
from pydantic import BaseModel, ValidationError
from soc_shared.masking import classify_ip, find_leaks, find_unmasked_pii
from soc_shared.masking.patterns import TOKEN_RE
from soc_shared.models import AskAnswer, ScopeVerdict, TriageNote

from agent_service.context import WorkerContext

# ------------------------------------------------------------------ shared patterns
INJECTION_RE = re.compile(
    r"(ignore (all |the )?(previous|prior|above) (instructions|rules)|disregard (the )?(system|previous)"
    r"|you are now (in )?(developer|dan|jailbreak)|system override|reveal (your|the) (system prompt|"
    r"api[_ ]?key|openai_api_key)|print (your|the) system prompt|new instruction:|</?context>"
    r"|skip the masking|without citations)",
    re.IGNORECASE,
)
OFFENSIVE_RE = re.compile(
    r"\b(write (a |an )?(working )?(exploit|shellcode|ransomware|malware|keylogger|encryptor)"
    r"|bypass (windows defender|edr|antivirus|amsi)|crack (ntlm|password|hashes)|hashcat|mimikatz"
    r"|cobalt strike|metasploit module|command[- ]and[- ]control server|build a botnet"
    r"|kerberoasting attack|pass-the-hash|reverse engineer(ing)? (a |the )?malware|decompile)\b",
    re.IGNORECASE,
)
SECRET_RE = re.compile(
    r"(sk-[A-Za-z0-9_-]{10,}|AKIA[0-9A-Z]{16}|password\s*[:=]|api[_-]?key\s*[:=])", re.IGNORECASE
)
INSTRUCTION_LIKE_RE = re.compile(
    r"^.*(ignore (all |any )?(previous|prior) instructions|you are (an? )?(ai|assistant|chatgpt)"
    r"|system prompt|do not tell the user|disregard|assistant:|<script|begin prompt).*$",
    re.IGNORECASE | re.MULTILINE,
)
ACTION_CLAIM_RE = re.compile(
    r"\b(i|we|the ai|ai|this agent)\s+(have\s+|has\s+)?(blocked|disabled|deleted|quarantined|isolated"
    r"|removed|reset|locked)\b|\bhas been (blocked|disabled|deleted|quarantined|isolated)\b",
    re.IGNORECASE,
)
MITRE_FROM_STABLE_ID = re.compile(r"knowledge/mitre/t(\d{4})(?:-(\d{3}))?-")

SAFE_FALLBACK = (
    "The draft did not pass the safety review and was withheld. A human analyst must triage this "
    "manually. Final decision: human analyst"
)


def rules_scope(text: str) -> ScopeVerdict | None:
    """Cheap, deterministic pre-check. Returns a DECLINE verdict, or None to ask the classifier."""
    if INJECTION_RE.search(text):
        return ScopeVerdict(
            label="DECLINE",
            reason="prompt injection pattern",
            injection_suspected=True,
            category="prompt_injection",
        )
    if OFFENSIVE_RE.search(text):
        return ScopeVerdict(
            label="DECLINE", reason="offensive security request", category="offensive"
        )
    return None


def _input_text(data: str | list[TResponseInputItem]) -> str:
    if isinstance(data, str):
        return data
    parts = []
    for item in data:
        content = item.get("content") if isinstance(item, dict) else None
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            parts += [c.get("text", "") for c in content if isinstance(c, dict)]
    return "\n".join(parts)


Classifier = Callable[[str, WorkerContext], Awaitable[ScopeVerdict]]


def make_scope_guard(classify: Classifier) -> Any:
    """1 INPUT guardrail for /ask. Blocking, so a declined question costs nothing downstream."""

    @input_guardrail(name="scope_guard", run_in_parallel=False)
    async def scope_guard(
        ctx: RunContextWrapper[WorkerContext],
        agent: Agent[Any],
        data: str | list[TResponseInputItem],
    ) -> GuardrailFunctionOutput:
        text = _input_text(data)
        verdict = rules_scope(text) or await classify(text, ctx.context)
        ctx.context.scope = verdict
        ctx.context.injection_suspected = verdict.injection_suspected
        ctx.context.events.append(f"scope {verdict.label} ({verdict.category or '-'})")
        return GuardrailFunctionOutput(
            output_info=verdict.model_dump(), tripwire_triggered=verdict.label == "DECLINE"
        )

    return scope_guard


@input_guardrail(name="triage_input_guard", run_in_parallel=False)
async def triage_input_guard(
    ctx: RunContextWrapper[WorkerContext], agent: Agent[Any], data: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """1 INPUT guardrail for /triage: an alert is never declined, but injected text inside it
    (attackers control log fields) is flagged so the reviewer is stricter and nothing in it is obeyed."""
    text = _input_text(data)
    ctx.context.injection_suspected = bool(INJECTION_RE.search(text))
    leaks = find_unmasked_pii(TOKEN_RE.sub(" ", text))
    return GuardrailFunctionOutput(
        output_info={"unmasked": len(leaks)}, tripwire_triggered=bool(leaks)
    )  # raw data must never reach the model


# ------------------------------------------------------------------ 2 OUTPUT review
HANDOFF_RE = re.compile(
    r"\s*(transferring|handing (you )?(off|over)|i(?: will|'ll| am going to) (transfer|hand))\b",
    re.IGNORECASE,
)


def review_problems(output: TriageNote | AskAnswer, ctx: WorkerContext) -> list[str]:
    text = output.to_text() if isinstance(output, TriageNote) else output.answer
    if isinstance(output, AskAnswer):
        text += " " + " ".join(output.citations)
    problems: list[str] = []
    if isinstance(output, AskAnswer) and HANDOFF_RE.match(output.answer):
        problems.append("the answer is a handoff sentence, not an answer (pilot 2026-11-12)")
    if find_leaks(text, ctx.mask_map) or find_unmasked_pii(TOKEN_RE.sub(" ", text)):
        problems.append("raw IP/user/host/email in the output")
    if ACTION_CLAIM_RE.search(text):
        problems.append("claims the AI acted on a system (the AI is read-only)")
    citations = output.citations
    invented = [c for c in citations if c not in ctx.seen_stable_ids]
    if invented:
        problems.append(f"cites pages KSOR did not return: {invented}")
    web = [str(w.url) for w in output.web_sources]
    if any(u not in ctx.web_urls for u in web):
        problems.append("cites web sources that web_search did not return")
    if isinstance(output, TriageNote):
        allowed = set(ctx.alert_mitre)
        for sid in ctx.seen_stable_ids:
            m = MITRE_FROM_STABLE_ID.match(sid)
            if m:
                allowed.add(f"T{m[1]}" + (f".{m[2]}" if m[2] else ""))
        if set(output.mitre_ids) - allowed:
            problems.append(
                f"MITRE ids not in the alert or cited handbook pages: "
                f"{sorted(set(output.mitre_ids) - allowed)}"
            )
        level = ctx.alert_rule_level
        if level is not None and level >= 12 and not output.escalate:
            problems.append("rule level >= 12 but no escalation (escalation policy condition 1)")
        if output.escalate_condition == 1 and level is not None and level < 12:
            problems.append("condition 1 claimed but rule level < 12")
    return problems


class ReviewVerdict(BaseModel):
    ok: bool
    problems: list[str] = []


Reviewer = Callable[[str, WorkerContext], Awaitable[ReviewVerdict]]


def make_output_guardrail(llm_review: Reviewer | None) -> Any:
    """2 OUTPUT guardrail (reflection pattern): deterministic checks first, then the small reviewer agent."""

    @output_guardrail(name="note_reviewer")
    async def note_reviewer(
        ctx: RunContextWrapper[WorkerContext], agent: Agent[Any], output: Any
    ) -> GuardrailFunctionOutput:
        if not isinstance(output, TriageNote | AskAnswer):
            return GuardrailFunctionOutput(
                output_info={"problems": ["unexpected output type"]}, tripwire_triggered=True
            )
        if isinstance(output, AskAnswer) and output.scope == "DECLINE":
            return GuardrailFunctionOutput(output_info={"problems": []}, tripwire_triggered=False)
        problems = review_problems(output, ctx.context)
        if not problems and llm_review is not None:
            text = output.to_text() if isinstance(output, TriageNote) else output.answer
            verdict = await llm_review(text, ctx.context)
            problems = [] if verdict.ok else verdict.problems or ["reviewer rejected the draft"]
        ctx.context.events.append(f"review {'ok' if not problems else 'FAILED'}")
        return GuardrailFunctionOutput(
            output_info={"problems": problems}, tripwire_triggered=bool(problems)
        )

    return note_reviewer


# ------------------------------------------------------------------ 3 TOOL INPUT
def _args(data: ToolInputGuardrailData) -> dict[str, Any]:
    try:
        parsed = json.loads(data.context.tool_arguments or "{}")
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


@tool_input_guardrail(name="ksor_query_guard")
def ksor_query_guard(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    q = str(_args(data).get("query", ""))
    if not 3 <= len(q) <= 500:
        return ToolGuardrailFunctionOutput.reject_content(
            "query must be 3-500 characters; rephrase"
        )
    if any(ord(ch) < 32 and ch not in "\n\t" for ch in q):
        return ToolGuardrailFunctionOutput.reject_content("query contains control characters")
    if find_unmasked_pii(TOKEN_RE.sub(" ", q)):
        return ToolGuardrailFunctionOutput.reject_content(
            "query contains a raw IP/email; use tokens"
        )
    return ToolGuardrailFunctionOutput.allow()


def make_ip_token_guard() -> Any:
    @tool_input_guardrail(name="ip_token_guard")
    def ip_token_guard(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
        token = str(_args(data).get("ip_token", ""))
        ctx: WorkerContext = data.context.context
        if not re.fullmatch(r"<IP-\d+>", token) or token not in ctx.mask_map:
            return ToolGuardrailFunctionOutput.reject_content(
                "pass an <IP-n> token from the masked alert, not a raw address"
            )
        kind = classify_ip(ctx.mask_map.value_of(token) or "")
        if kind != "public":
            return ToolGuardrailFunctionOutput.reject_content(
                f"{token} is {kind}: reputation lookups are only for public IPs. Say so in the note."
            )
        return ToolGuardrailFunctionOutput.allow()

    return ip_token_guard


@tool_input_guardrail(name="web_query_guard")
def web_query_guard(data: ToolInputGuardrailData) -> ToolGuardrailFunctionOutput:
    q = str(_args(data).get("query", ""))
    if not 3 <= len(q) <= 300:
        return ToolGuardrailFunctionOutput.reject_content("web query must be 3-300 characters")
    if TOKEN_RE.search(q) or find_unmasked_pii(q):
        return ToolGuardrailFunctionOutput.reject_content(
            "never put alert data (tokens, IPs, emails) into a web query; ask about the concept"
        )
    if SECRET_RE.search(q):
        return ToolGuardrailFunctionOutput.reject_content(
            "the query looks like it contains a secret"
        )
    if OFFENSIVE_RE.search(q):
        return ToolGuardrailFunctionOutput.reject_content(
            "offensive how-to searches are not allowed"
        )
    return ToolGuardrailFunctionOutput.allow()


# ------------------------------------------------------------------ 4 TOOL OUTPUT
WEB_CAP = 6000


@tool_output_guardrail(name="web_output_guard")
def web_output_guard(data: ToolOutputGuardrailData) -> ToolGuardrailFunctionOutput:
    text = str(data.output)
    if len(text) > WEB_CAP:
        return ToolGuardrailFunctionOutput.reject_content(
            "web results too large; ask a narrower question"
        )
    if INSTRUCTION_LIKE_RE.search(text):
        return ToolGuardrailFunctionOutput.reject_content(
            "web result contained instruction-like text"
        )
    return ToolGuardrailFunctionOutput.allow()


class _Rep(BaseModel):
    ip_token: str
    status: str
    ip_class: str
    abuse_confidence_score: int | None = None


@tool_output_guardrail(name="ip_output_guard")
def ip_output_guard(data: ToolOutputGuardrailData) -> ToolGuardrailFunctionOutput:
    try:
        rep = _Rep.model_validate_json(str(data.output))
    except ValidationError:
        return ToolGuardrailFunctionOutput.reject_content(
            "reputation unavailable (unexpected result)"
        )
    if find_unmasked_pii(str(data.output)):
        return ToolGuardrailFunctionOutput.reject_content(
            "reputation result contained a raw address"
        )
    _ = rep
    return ToolGuardrailFunctionOutput.allow()
