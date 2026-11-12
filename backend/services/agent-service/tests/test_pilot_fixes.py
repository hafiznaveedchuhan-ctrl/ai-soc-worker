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
