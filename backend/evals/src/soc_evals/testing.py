"""Builders for tiny hand-made labels and predictions (used by tests and the oracle recording)."""

from datetime import UTC, datetime
from typing import Any

from soc_shared.models import (
    DECLINE_MESSAGE,
    AskAnswer,
    Evidence,
    LlmUsage,
    TriageNote,
    WazuhAlert,
)

from soc_evals.datasets import AlertLabel, Probe
from soc_evals.predictions import AlertPrediction, ProbePrediction

T0 = datetime(2026, 11, 12, 3, 0, tzinfo=UTC)


def alert(aid: str, mitre: list[str] | None = None) -> WazuhAlert:
    return WazuhAlert.model_validate(
        {
            "id": aid,
            "timestamp": "2026-11-12T03:00:00Z",
            "rule": {"id": "60122", "level": 5, "description": "x", "mitre": {"id": mitre or []}},
            "agent": {"id": "001", "name": "lab-ws01", "ip": "10.0.0.5"},
            "data": {"srcip": "203.0.113.9"},
        }
    )


def label(aid: str, verdict: str = "TP", escalate: int | None = None, **kw: Any) -> AlertLabel:
    base: dict[str, Any] = {
        "alert_id": aid,
        "source": "SYNTHETIC",
        "source_ref": "synthetic: test",
        "playbook": "brute-force",
        "verdict": verdict,
        "severity": "Medium",
        "escalate": escalate is not None,
        "escalate_condition": escalate,
        "mitre_ids": ["T1110"],
        "expected_stable_ids": ["knowledge/playbooks/brute-force"],
        "rule_source": "knowledge/wazuh/windows-rules-reference",
        "rationale": "hand-made test label",
    }
    base.update(kw)
    return AlertLabel.model_validate(base)


def note(
    aid: str,
    verdict: str = "TP",
    escalate: int | None = None,
    citations: list[str] | None = None,
    mitre: list[str] | None = None,
) -> TriageNote:
    return TriageNote.model_validate(
        {
            "alert_id": aid,
            "rule_id": "60122",
            "rule_level": 5,
            "time_window_start": T0,
            "time_window_end": T0,
            "summary": "failures for <USER-1> from <IP-1>",
            "evidence": [Evidence(fact="f", source="s")],
            "mitre_ids": mitre if mitre is not None else ["T1110"],
            "citations": citations
            if citations is not None
            else ["knowledge/playbooks/brute-force"],
            "verdict_suggestion": verdict,
            "confidence": 0.8,
            "severity": "Medium",
            "escalate": escalate is not None,
            "escalate_condition": escalate,
            "missing_info": ["x"] if verdict == "needs_info" else [],
        }
    )


def usage(cost: float = 0.001) -> list[LlmUsage]:
    return [
        LlmUsage(
            request_id="r",
            agent="triage",
            model="m",
            input_tokens=100,
            output_tokens=20,
            cost_usd=cost,
        )
    ]


def apred(
    aid: str, n: TriageNote | None, text: str = "masked <IP-1>", ms: float = 10
) -> AlertPrediction:
    return AlertPrediction(alert_id=aid, note=n, output_text=text, latency_ms=ms, usage=usage())


def probe(pid: str, pset: str, expected: str, cat: str = "c", sid: str | None = None) -> Probe:
    return Probe(
        probe_id=pid,
        set=pset,
        expected_label=expected,
        category=cat,
        question="a question?",
        expected_stable_id=sid,
        origin="new",
    )


def ppred(pid: str, lbl: str, cite: str | None = None, text: str | None = None) -> ProbePrediction:
    if lbl == "DECLINE":
        ans = AskAnswer(answer=DECLINE_MESSAGE, scope="DECLINE", confidence=1)
        return ProbePrediction(
            probe_id=pid, scope_label="DECLINE", answer=ans, output_text=text or DECLINE_MESSAGE
        )
    ans = AskAnswer(
        answer="ok",
        scope=lbl,
        citations=[cite] if cite else [],
        not_in_record=cite is None,
        confidence=0.7,
    )
    return ProbePrediction(probe_id=pid, scope_label=lbl, answer=ans, output_text=text or "ok")
