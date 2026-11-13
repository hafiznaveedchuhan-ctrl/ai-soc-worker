"""R3 fixes from the paid pilot (feature 11, T11-11…13). ScriptedModel only: free, offline."""

from pathlib import Path
from typing import Any

import pytest
from agent_service.flows import rule_problems, run_ask, run_triage
from agent_service.guardrails import ReviewVerdict
from agent_service.testing import build_offline, call, msg, scripted
from agents import set_trace_processors
from soc_shared.models import AskAnswer, ScopeVerdict, TriageNote

pytestmark = pytest.mark.anyio
BRUTE = "knowledge/playbooks/brute-force"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
def _no_export() -> None:
    set_trace_processors([])


def good_note() -> dict[str, Any]:
    return {
        "alert_id": "EV-A003",
        "rule_id": "60106",
        "rule_level": 3,
        "time_window_start": "2026-11-11T02:41:10Z",
        "time_window_end": "2026-11-11T02:53:40Z",
        "summary": "Type 10 logon for <USER-1> from <IP-2> after a brute-force burst.",
        "evidence": [{"fact": "4624 logon type 10", "source": "data.win.eventdata.logonType"}],
        "inference": ["Success after failures from the same source."],
        "mitre_ids": ["T1078"],
        "citations": [BRUTE],
        "verdict_suggestion": "TP",
        "confidence": 0.8,
        "severity": "Critical",
        "escalate": True,
        "escalate_condition": 4,
    }


def bad_note() -> dict[str, Any]:
    return {**good_note(), "escalate_condition": None}  # breaks escalate <-> condition rule


def triage_steps(*finals: dict[str, Any]) -> dict[str, list[Any]]:
    return {
        "triage": [
            call("ask_handbook", {"input": "success after brute force"}, "t1"),
            *[msg(f) for f in finals],
        ],
        "handbook": [
            call("search_handbook", {"query": "brute force"}, "s1"),
            msg(
                AskAnswer(
                    answer="Brute force then success = condition 4.",
                    scope="ALLOW_KSOR",
                    citations=[BRUTE],
                    confidence=0.8,
                )
            ),
        ],
        "reviewer": [msg(ReviewVerdict(ok=True))] * 3,
    }


def test_rule_problems_names_the_rule_but_never_the_values() -> None:
    import json

    probs = rule_problems(json.dumps({**bad_note(), "summary": "from 203.0.113.45"}), TriageNote)
    assert probs and any("escalate" in p for p in probs)
    assert all("203.0.113.45" not in p and "<IP-2>" not in p for p in probs)
    assert rule_problems("{not json", TriageNote)  # unparsable → still a message
    assert rule_problems(json.dumps(good_note()), TriageNote) == []


async def test_invalid_note_gets_one_corrective_retry(tmp_path: Path) -> None:
    models = scripted(triage_steps(bad_note(), good_note()))
    app, cfg, deps = build_offline(models, tmp_path)
    r = await run_triage(app, cfg, deps, "EV-A003", user_id="u")
    assert r.status == "ok" and r.note is not None and r.note.escalate_condition == 4, r.events
    assert any(e.startswith("invalid note:") and "escalate" in e for e in r.events)
    assert "retrying once with the rule messages" in r.events
    retry_input = str(models["triage"].calls[-1].input)
    assert "previous_attempt_rejected_because" in retry_input
    assert "203.0.113.45" not in retry_input  # the retry is masked like the first attempt


async def test_twice_invalid_note_is_an_error_that_keeps_its_usage(tmp_path: Path) -> None:
    models = scripted(triage_steps(bad_note(), bad_note()))
    app, cfg, deps = build_offline(models, tmp_path)
    r = await run_triage(app, cfg, deps, "EV-A003", user_id="u")
    assert r.status == "error" and r.note is None
    assert "broke the template rules twice" in r.text
    assert len(r.usage) >= 3  # F1: the spend of both attempts is reported, not lost


async def test_invalid_ask_answer_is_an_error_that_keeps_its_usage(tmp_path: Path) -> None:
    models = scripted(
        {
            "scope": [msg(ScopeVerdict(label="ALLOW_KSOR", reason="x"))],
            "triage": [call("transfer_to_soc_handbook_agent", {}, "h1")],
            "handbook": [
                call("search_handbook", {"query": "event 4625 meaning"}, "s1"),
                msg({"answer": "x", "scope": "ALLOW_KSOR", "confidence": 7}),  # confidence > 1
                msg({"answer": "x", "scope": "ALLOW_KSOR", "confidence": 7}),  # retry: still bad
            ],
        }
    )
    app, cfg, _ = build_offline(models, tmp_path)
    r = await run_ask(app, cfg, "What does event 4625 mean?", user_id="u", session_id="s")
    assert r.status == "error" and r.answer is not None and r.answer.not_in_record
    assert r.usage and any("ModelBehaviorError" in e for e in r.events)


async def test_handoff_sentence_as_answer_is_blocked(tmp_path: Path) -> None:
    """Pilot EV-P021: with web search off, the final answer was 'Transferring to …' (T11-13)."""
    models = scripted(
        {
            "scope": [msg(ScopeVerdict(label="ALLOW_CYBER_RESEARCH", reason="not in KSOR"))],
            "triage": [call("transfer_to_cyber_research_agent", {}, "h1")],
            "research": [
                msg(
                    {
                        "answer": "Transferring to a cyber research specialist for this topic.",
                        "scope": "ALLOW_CYBER_RESEARCH",
                        "not_in_record": True,
                        "confidence": 0.1,
                    }
                )
            ],
            "reviewer": [msg(ReviewVerdict(ok=True))],
        }
    )
    app, cfg, _ = build_offline(models, tmp_path)
    r = await run_ask(app, cfg, "How do I tune Cisco ASA ACL logging?", user_id="u", session_id="s")
    assert r.status == "blocked" and "Transferring" not in r.text


async def test_web_unavailable_gets_the_plain_not_in_record_answer(tmp_path: Path) -> None:
    text = "Not in this record: web search is unavailable, so this cannot be researched right now."
    models = scripted(
        {
            "scope": [msg(ScopeVerdict(label="ALLOW_CYBER_RESEARCH", reason="not in KSOR"))],
            "triage": [call("transfer_to_cyber_research_agent", {}, "h1")],
            "research": [
                call("web_search", {"query": "kerberoasting detection"}, "w1"),
                msg(
                    {
                        "answer": text,
                        "scope": "ALLOW_CYBER_RESEARCH",
                        "not_in_record": True,
                        "confidence": 0,
                    }
                ),
            ],
            "reviewer": [msg(ReviewVerdict(ok=True))],
        }
    )
    app, cfg, deps = build_offline(models, tmp_path)
    deps.web = None  # like the pilot: no Tavily key
    r = await run_ask(app, cfg, "How can a SOC detect Kerberoasting?", user_id="u", session_id="s")
    assert r.status == "ok" and r.text == text
    assert "unavailable" in str(models["research"].calls[1].input)  # the tool said so
    instructions = app.ask_entry.handoffs[1].instructions  # type: ignore[union-attr]
    assert "never a sentence about transferring" in str(instructions)


# ------------------------------------------------------------------ R3c (diagnostic run findings)
async def test_llm_reviewer_sees_the_citations(tmp_path: Path) -> None:
    """T11-18 / EV-P056: the reviewer was given only the answer text and called it uncited."""
    e4625 = "knowledge/windows-events/event-4625"  # a page the fake KSOR really returns
    models = scripted(
        {
            "scope": [msg(ScopeVerdict(label="ALLOW_KSOR", reason="event meaning"))],
            "triage": [call("transfer_to_soc_handbook_agent", {}, "h1")],
            "handbook": [
                call("search_handbook", {"query": "event 4625 meaning"}, "s1"),
                msg(
                    AskAnswer(
                        answer="Event 4625 is a failed logon.",
                        scope="ALLOW_KSOR",
                        citations=[e4625],
                        confidence=0.8,
                    )
                ),
            ],
            "reviewer": [msg(ReviewVerdict(ok=True))],
        }
    )
    app, cfg, _ = build_offline(models, tmp_path)
    r = await run_ask(app, cfg, "What does event 4625 mean?", user_id="u", session_id="s")
    seen = str(models["reviewer"].calls[0].input)
    assert "Citations (handbook stable_ids)" in seen and e4625 in seen
    assert "not_in_record: false" in seen
    assert r.status == "ok"


async def test_rules_failure_gets_one_corrective_retry_then_ok(tmp_path: Path) -> None:
    """T11-19 / EV-A034: escalate=false on a level >= 12 alert → rule problem → retry → fixed."""
    from agent_service.flows import policy_hints

    assert policy_hints(12) and policy_hints(3) == []
    lvl12 = {
        **good_note(),
        "alert_id": "EV-A034",
        "rule_id": "91844",
        "rule_level": 12,
        "mitre_ids": ["T1059.001"],
    }
    no_esc = {**lvl12, "escalate": False, "escalate_condition": None}
    fixed = {**lvl12, "escalate": True, "escalate_condition": 1}
    models = scripted(triage_steps(no_esc, fixed))
    app, cfg, deps = build_offline(models, tmp_path)
    r = await run_triage(app, cfg, deps, "EV-A034", user_id="u")
    assert r.status == "ok" and r.note is not None and r.note.escalate_condition == 1, r.events
    assert any(e.startswith("note failed the rules:") and "condition 1" in e for e in r.events)
    assert "previous_attempt_rejected_because" in str(models["triage"].calls[-1].input)


async def test_llm_reviewer_rejection_is_not_retried(tmp_path: Path) -> None:
    script = triage_steps(good_note(), good_note())
    script["reviewer"] = [msg(ReviewVerdict(ok=True)), msg(ReviewVerdict(ok=False, problems=["x"]))]
    models = scripted(script)
    app, cfg, deps = build_offline(models, tmp_path)
    r = await run_triage(app, cfg, deps, "EV-A003", user_id="u")
    assert r.status == "blocked" and "retrying once with the rule messages" not in r.events


async def test_invalid_ask_answer_gets_one_retry_at_the_specialist(tmp_path: Path) -> None:
    """T11-20 / EV-P021: no citation, no web source, no not_in_record → retry → valid."""
    nir = "Not in this record: web search is unavailable, so this cannot be researched right now."
    models = scripted(
        {
            "scope": [msg(ScopeVerdict(label="ALLOW_CYBER_RESEARCH", reason="not in KSOR"))],
            "triage": [call("transfer_to_cyber_research_agent", {}, "h1")],
            "research": [
                msg({"answer": "ACL logging helps.", "scope": "ALLOW_CYBER_RESEARCH"}),
                msg(
                    {
                        "answer": nir,
                        "scope": "ALLOW_CYBER_RESEARCH",
                        "not_in_record": True,
                        "confidence": 0,
                    }
                ),
            ],
            "reviewer": [msg(ReviewVerdict(ok=True))],
        }
    )
    app, cfg, _ = build_offline(models, tmp_path)
    r = await run_ask(app, cfg, "How do I tune ASA ACL logging?", user_id="u", session_id="s")
    assert r.status == "ok" and r.text == nir, r.events
    assert len(models["scope"].calls) == 1  # the retry skips the scope classifier
    assert "previous answer was rejected" in str(models["research"].calls[-1].input)


# ------------------------------------------------------------------ R3d (pilot 4 findings)
async def test_triage_reviewer_sees_the_masked_analyst_context(tmp_path: Path) -> None:
    """T11-22 / EV-A003: the reviewer called the (real) 60204 reference an invention."""
    models = scripted(triage_steps(good_note()))
    app, cfg, deps = build_offline(models, tmp_path)
    ctx_text = "Wazuh rule 60204 fired for the same account from 203.0.113.45 (alert EV-A001)."
    r = await run_triage(app, cfg, deps, "EV-A003", user_id="u", analyst_context=ctx_text)
    assert r.status == "ok", r.events
    seen = " ".join(str(c.input) for c in models["reviewer"].calls)
    assert "INPUT GIVEN WITH THE ALERT" in seen and "rule 60204" in seen and "Rule 60106" in seen
    assert "203.0.113.45" not in seen  # masked like everything else the model sees


async def test_specialists_must_search_first_then_choice_resets(tmp_path: Path) -> None:
    """T11-23 / EV-P056: the handbook agent answered without calling search_handbook."""
    models = scripted(
        {
            "scope": [msg(ScopeVerdict(label="ALLOW_KSOR", reason="event meaning"))],
            "triage": [call("transfer_to_soc_handbook_agent", {}, "h1")],
            "handbook": [
                call("search_handbook", {"query": "event 4625 meaning"}, "s1"),
                msg(
                    AskAnswer(
                        answer="Event 4625 is a failed logon.",
                        scope="ALLOW_KSOR",
                        citations=["knowledge/windows-events/event-4625"],
                        confidence=0.8,
                    )
                ),
            ],
            "reviewer": [msg(ReviewVerdict(ok=True))],
        }
    )
    app, cfg, _ = build_offline(models, tmp_path)
    r = await run_ask(app, cfg, "What does event 4625 mean?", user_id="u", session_id="s")
    assert r.status == "ok"
    first, second = models["handbook"].calls
    assert first.model_settings.tool_choice == "search_handbook"  # forced on the first turn
    assert second.model_settings.tool_choice is None  # reset by the SDK → no loop
    assert app.research.model_settings.tool_choice == "required"


async def test_as_tool_sub_agent_calls_are_priced(tmp_path: Path) -> None:
    """OpenAI usage CSV (2026-11-13) showed ~1/3 more gpt-5-nano tokens than our ledger: the
    handbook/research sub-agents run through Agent.as_tool, which had no cost hooks."""
    models = scripted(triage_steps(good_note()))
    app, cfg, deps = build_offline(models, tmp_path)
    r = await run_triage(app, cfg, deps, "EV-A003", user_id="u")
    assert r.status == "ok", r.events
    agents = [u.agent for u in r.usage]
    assert "soc_handbook_agent" in agents  # 2 sub-agent turns (search + answer)
    assert agents.count("soc_handbook_agent") == len(models["handbook"].calls)


def test_every_forced_tool_choice_maps_to_one_of_our_function_tools(tmp_path: Path) -> None:
    """R5 (2026-11-13): tool_choice="web_search" became the HOSTED web_search tool in the real
    request → 400 "Tool choice 'web_search_preview' not found". ScriptedModel never converts, so this
    runs the SDK's real Responses converter on every agent's tool_choice."""
    from agents.models.openai_responses import Converter

    app, _, _ = build_offline(scripted({}), tmp_path)
    agents = [app.ask_entry, app.triage_entry, app.handbook, app.research, app.scope_classifier]
    checked = 0
    for agent in agents:
        choice = agent.model_settings.tool_choice
        if choice is None:
            continue
        checked += 1
        converted = Converter.convert_tool_choice(choice, tools=agent.tools)
        if converted in ("required", "auto", "none"):
            continue
        assert isinstance(converted, dict) and converted.get("type") == "function", (
            f"{agent.name}: tool_choice {choice!r} became {converted!r} (a hosted tool?)"
        )
        assert dict(converted).get("name") in {t.name for t in agent.tools}
    assert checked >= 2
