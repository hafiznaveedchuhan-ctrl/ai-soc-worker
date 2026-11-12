"""Regressions from the first paid pilot (2026-11-12, feature 11). Free, offline.

1. OpenAI strict structured output rejected `format: uri` (HTTP 400) → every schema we send
   (agent output types AND function-tool parameters) may only use the documented formats.
2. A blank `AGENT_MODEL_DEFAULT=` line in .env made the model name "" (HTTP 404) → blank = default.
"""

import json
import re
from pathlib import Path

from agent_service.guardrails import ReviewVerdict
from agent_service.settings import AgentSettings
from agent_service.testing import build_offline, scripted
from agents import Agent, FunctionTool
from agents.agent_output import AgentOutputSchema
from soc_shared.models import AskAnswer, ScopeVerdict, TriageNote

# developers.openai.com/api/docs/guides/structured-outputs → "Supported properties" (checked 2026-11-12)
SUPPORTED_FORMATS = {
    "date-time",
    "time",
    "date",
    "duration",
    "email",
    "hostname",
    "ipv4",
    "ipv6",
    "uuid",
}


def _formats(schema: object) -> set[str]:
    return set(re.findall(r'"format": "([^"]+)"', json.dumps(schema)))


def test_agent_output_schemas_use_only_supported_formats() -> None:
    for model in (TriageNote, AskAnswer, ScopeVerdict, ReviewVerdict):
        bad = _formats(AgentOutputSchema(model).json_schema()) - SUPPORTED_FORMATS
        assert not bad, f"{model.__name__}: unsupported format(s) {bad}"


def test_function_tool_schemas_use_only_supported_formats(tmp_path: Path) -> None:
    app, _, _ = build_offline(scripted({}), tmp_path)
    seen: set[int] = set()
    stack: list[Agent[object]] = [app.ask_entry, app.triage_entry]  # type: ignore[list-item]
    n_tools = 0
    while stack:
        agent = stack.pop()
        if id(agent) in seen:
            continue
        seen.add(id(agent))
        for tool in agent.tools:
            if isinstance(tool, FunctionTool):
                n_tools += 1
                bad = _formats(tool.params_json_schema) - SUPPORTED_FORMATS
                assert not bad, f"{agent.name}.{tool.name}: unsupported format(s) {bad}"
        stack.extend(h for h in agent.handoffs if isinstance(h, Agent))
    assert n_tools >= 4


def test_web_source_url_is_a_plain_checked_string() -> None:
    ans = AskAnswer.model_validate(
        {
            "answer": "x (unverified web source (https://attack.mitre.org/))",
            "scope": "ALLOW_CYBER_RESEARCH",
            "web_sources": [{"url": "https://attack.mitre.org/techniques/T1558/003/"}],
            "confidence": 0.5,
        }
    )
    assert (
        ans.web_sources[0].url == "https://attack.mitre.org/techniques/T1558/003/"
    )  # not normalised
    for bad in ("javascript:alert(1)", "ftp://x", "https://a b"):
        try:
            AskAnswer.model_validate(
                {"answer": "x", "scope": "ALLOW_CYBER_RESEARCH", "web_sources": [{"url": bad}]}
            )
        except ValueError:
            continue
        raise AssertionError(f"{bad!r} was accepted")


def test_blank_model_line_in_env_means_default(tmp_path: Path) -> None:
    env = tmp_path / "x.env"
    env.write_text("AGENT_MODEL_DEFAULT=\nAGENT_MODEL_SCOPE=\n", encoding="utf-8")
    s = AgentSettings(_env_file=env)
    assert s.model_for("triage") == s.model_for("scope") == "gpt-5-nano"
