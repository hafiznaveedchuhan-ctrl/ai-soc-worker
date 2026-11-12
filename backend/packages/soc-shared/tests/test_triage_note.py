"""FR-01-15, FR-01-16 — TriageNote rules and the handbook template rendering."""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError
from soc_shared.models import FINAL_LINE, Evidence, TriageNote, Verdict, WebSource


def note(**overrides: Any) -> TriageNote:
    base: dict[str, Any] = {
        "alert_id": "1731390000.100001",
        "rule_id": "60122",
        "rule_level": 5,
        "time_window_start": datetime(2026, 11, 12, 3, 0, tzinfo=UTC),
        "time_window_end": datetime(2026, 11, 12, 3, 15, tzinfo=UTC),
        "summary": "Repeated failed network logons for <USER-1> on <HOST-1> from <IP-1>.",
        "evidence": [Evidence(fact="12 failures in 5 minutes", source="rule 60122 / event 4625")],
        "inference": ["Pattern matches password guessing."],
        "mitre_ids": ["T1110.001"],
        "citations": ["knowledge/playbooks/brute-force"],
        "verdict_suggestion": Verdict.TP,
        "confidence": 0.82,
        "severity": "Medium",
        "escalate": False,
    }
    base.update(overrides)
    return TriageNote.model_validate(base)


def test_valid_note() -> None:
    n = note()
    assert n.final_decision_by == "human"
    assert n.confidence_band == "high"


def test_escalate_needs_condition() -> None:
    with pytest.raises(ValidationError, match="escalate_condition"):
        note(escalate=True)
    assert note(escalate=True, escalate_condition=4).escalate_condition == 4


def test_condition_without_escalate_rejected() -> None:
    with pytest.raises(ValidationError):
        note(escalate_condition=2)


@pytest.mark.parametrize("bad", [0, 9])
def test_condition_range(bad: int) -> None:
    with pytest.raises(ValidationError):
        note(escalate=True, escalate_condition=bad)


def test_needs_info_requires_missing_info() -> None:
    with pytest.raises(ValidationError, match="missing_info"):
        note(verdict_suggestion="needs_info", citations=[])
    ok = note(verdict_suggestion="needs_info", citations=[], missing_info=["asset owner"])
    assert ok.verdict_suggestion is Verdict.NEEDS_INFO


def test_verdict_needs_ksor_citation_web_alone_not_enough() -> None:
    with pytest.raises(ValidationError, match="KSOR citation"):
        note(
            citations=[],
            web_sources=[WebSource(url="https://attack.mitre.org/techniques/T1110/")],
        )


def test_escalation_needs_citation_even_when_needs_info() -> None:
    with pytest.raises(ValidationError, match="KSOR citation"):
        note(
            verdict_suggestion="needs_info",
            missing_info=["x"],
            citations=[],
            escalate=True,
            escalate_condition=8,
        )


@pytest.mark.parametrize("bad", ["T110", "t1110", "T1110.1", "1110", "TA0006"])
def test_invalid_mitre_ids(bad: str) -> None:
    with pytest.raises(ValidationError, match="MITRE"):
        note(mitre_ids=[bad])


def test_invalid_citation() -> None:
    with pytest.raises(ValidationError, match="stable_id"):
        note(citations=["playbooks/brute-force"])


def test_time_window_order() -> None:
    with pytest.raises(ValidationError):
        note(time_window_end=datetime(2026, 11, 12, 2, 0, tzinfo=UTC))


def test_final_decision_cannot_be_ai() -> None:
    with pytest.raises(ValidationError):
        note(final_decision_by="ai")


@pytest.mark.parametrize(
    ("value", "band"),
    [(0.0, "low"), (0.39, "low"), (0.4, "medium"), (0.69, "medium"), (0.7, "high"), (1.0, "high")],
)
def test_confidence_bands(value: float, band: str) -> None:
    assert note(confidence=value).confidence_band == band


def test_to_text_golden() -> None:
    text = note(
        escalate=True, escalate_condition=4, escalate_reason="success after failures"
    ).to_text()
    assert text == (
        "Alert ID:        1731390000.100001          Rule: 60122 (level 5)\n"
        "Time window:     2026-11-12T03:00:00Z – 2026-11-12T03:15:00Z\n"
        "Summary:         Repeated failed network logons for <USER-1> on <HOST-1> from <IP-1>.\n"
        "Evidence:\n"
        "  - 12 failures in 5 minutes — source: rule 60122 / event 4625\n"
        "Inference:\n"
        "  - Pattern matches password guessing.\n"
        "MITRE ATT&CK:    T1110.001\n"
        "Handbook:        knowledge/playbooks/brute-force\n"
        "Verdict (suggested): TP\n"
        "Confidence:      0.82 (high)\n"
        "Severity:        Medium\n"
        "Escalate:        yes — condition #4 — success after failures\n"
        "Final decision: human analyst"
    )


def test_to_text_needs_info_and_web_sources() -> None:
    text = note(
        verdict_suggestion="needs_info",
        missing_info=["asset owner", "change ticket"],
        web_sources=[WebSource(url="https://learn.microsoft.com/x")],
        confidence=0.3,
    ).to_text()
    assert "Verdict (suggested): needs-info — missing: asset owner; change ticket" in text
    assert "Web sources:     unverified web source (https://learn.microsoft.com/x)" in text
    assert "Confidence:      0.30 (low)" in text
    assert text.splitlines()[-1] == FINAL_LINE


def test_benign_tp_display() -> None:
    assert Verdict.BENIGN_TP.display == "benign TP"
    assert "Verdict (suggested): benign TP" in note(verdict_suggestion="benign_TP").to_text()
