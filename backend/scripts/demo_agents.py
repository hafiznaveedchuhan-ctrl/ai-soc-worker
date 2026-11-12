"""`make demo-ask Q="..."` / `make demo-triage ID=EV-A003` — the MVP terminal demos (features 05–06).

Default = FAKE mode: scripted models (agents.testing.ScriptedModel) + in-memory MCP servers. Free, offline.
LIVE mode (`--live`, needs CONFIRM=haan + OPENAI_API_KEY in backend/.env): real OpenAI models (gpt-5-nano by
default), the live handbook at HANDBOOK_MCP_URL (run `npm run serve` in ../handbook), fixture Wazuh alerts.
"""

import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Any

from agent_service.agents_build import build_agents
from agent_service.budget import Ledger
from agent_service.deps import McpKsor
from agent_service.flows import FlowConfig, FlowResult, run_ask, run_triage
from agent_service.guardrails import ReviewVerdict
from agent_service.settings import AgentSettings
from agent_service.testing import build_offline, call, msg, offline_deps, scripted
from agents import set_trace_processors
from soc_shared.models import AskAnswer, Evidence, ScopeVerdict, TriageNote

BACKEND = Path(__file__).resolve().parents[1]


def fake_ask_script(q: str) -> dict[str, Any]:
    return {
        "scope": [msg(ScopeVerdict(label="ALLOW_KSOR", reason="SOC L1 question"))],
        "triage": [call("transfer_to_soc_handbook_agent", {}, "h1")],
        "handbook": [
            call("search_handbook", {"query": "event 4625"}, "s1"),
            msg(
                AskAnswer(
                    answer="Event 4625 records a failed logon; 0xC000006A means a bad password.",
                    scope="ALLOW_KSOR",
                    citations=["knowledge/windows-events/event-4625"],
                    confidence=0.8,
                )
            ),
        ],
        "reviewer": [msg(ReviewVerdict(ok=True))],
    }


def fake_triage_script(alert_id: str) -> dict[str, Any]:
    note = TriageNote(
        alert_id=alert_id,
        rule_id="60106",
        rule_level=3,
        time_window_start="2026-11-11T02:41:10Z",
        time_window_end="2026-11-11T02:53:40Z",
        summary="Type 10 logon for <USER-1> from <IP-2> after a brute-force burst.",
        evidence=[Evidence(fact="4624 logon type 10", source="data.win.eventdata.logonType")],
        inference=["Success after failures from the same source."],
        mitre_ids=["T1078"],
        citations=["knowledge/playbooks/brute-force"],
        verdict_suggestion="TP",
        confidence=0.8,
        severity="Critical",
        escalate=True,
        escalate_condition=4,
    )
    return {
        "triage": [
            call("ask_handbook", {"input": "success after brute force"}, "t1"),
            call("ip_reputation", {"ip_token": "<IP-2>"}, "t2"),
            call(
                "create_escalation_ticket",
                {"condition": 4, "summary": "success after brute force"},
                "t3",
            ),
            msg(note),
        ],
        "handbook": [
            call("search_handbook", {"query": "brute force"}, "s1"),
            msg(
                AskAnswer(
                    answer="Success after brute force = escalation condition 4.",
                    scope="ALLOW_KSOR",
                    citations=["knowledge/playbooks/brute-force"],
                    confidence=0.8,
                )
            ),
        ],
        "reviewer": [msg(ReviewVerdict(ok=True)), msg(ReviewVerdict(ok=True))],
    }


def show(r: FlowResult) -> None:
    print(f"status: {r.status}   request: {r.request_id}   trace: {r.trace_id}")
    print("events:", *r.events, sep="\n  - ")
    print("\n" + r.text)
    cost = sum(u.cost_usd for u in r.usage)
    print(
        f"\nLLM calls: {len(r.usage)}  tokens in/out: {sum(u.input_tokens for u in r.usage)}/"
        f"{sum(u.output_tokens for u in r.usage)}  cost: ${cost:.6f}  tickets: {r.tickets or 'none'}"
    )


async def ask_terminal(item: Any) -> bool:
    print(
        f"\n>>> APPROVAL NEEDED: {item.tool_name}({item.raw_item.arguments})  [mock — creates nothing real]"
    )
    return input("    approve? [y/N] ").strip().lower() == "y"


async def main(a: argparse.Namespace) -> None:
    set_trace_processors([])  # demo: do not export traces
    if not a.live:
        script = fake_ask_script(a.q) if a.flow == "ask" else fake_triage_script(a.id)
        app, cfg, deps = build_offline(scripted(script), BACKEND / "suggestions")
        print("[FAKE mode: scripted models, no API calls, $0]\n")
    else:
        if os.environ.get("CONFIRM") != "haan":
            raise SystemExit("refused: live mode makes PAID OpenAI calls — run with CONFIRM=haan")
        env = BACKEND / ".env"
        settings = AgentSettings(_env_file=env if env.exists() else None)
        if os.environ.get("OPENAI_API_KEY") is None and env.exists():
            from dotenv import dotenv_values

            key = dotenv_values(env).get("OPENAI_API_KEY")
            if key:
                os.environ["OPENAI_API_KEY"] = key
        deps = offline_deps()
        deps.ksor = McpKsor(settings.handbook_mcp_url)
        deps.web = None
        app = build_agents(settings.model_for, deps, settings.suggestions_dir)
        cfg = FlowConfig(
            prices=settings.prices,
            run_budget_usd=settings.run_budget_usd,
            max_turns=settings.max_turns,
            ledger=Ledger(settings.ledger_path, settings.total_budget_usd),
        )
        print(
            f"[LIVE mode: model {settings.model_default}, run budget ${settings.run_budget_usd}]\n"
        )
    if a.flow == "ask":
        show(await run_ask(app, cfg, a.q, user_id="naveed-cli", session_id="cli"))
    else:
        r = await run_triage(
            app,
            cfg,
            deps,
            a.id,
            user_id="naveed-cli",
            approve=ask_terminal if a.interactive else _auto(a.approve),
        )
        show(r)
        if r.note:
            print("\nstructured:", json.dumps(r.note.model_dump(mode="json"))[:400], "...")


def _auto(decision: bool) -> Any:
    async def f(item: Any) -> bool:
        print(
            f"\n>>> APPROVAL NEEDED: {item.tool_name} → auto-{'approved' if decision else 'rejected'} (demo)"
        )
        return decision

    return f


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("flow", choices=["ask", "triage"])
    p.add_argument("--q", default="What does event 4625 mean?")
    p.add_argument("--id", default="EV-A003")
    p.add_argument("--live", action="store_true")
    p.add_argument(
        "--interactive", action="store_true", help="ask y/N in the terminal for approvals"
    )
    p.add_argument("--approve", action="store_true", help="auto-approve (non-interactive demo)")
    asyncio.run(main(p.parse_args()))
