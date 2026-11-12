"""FR-01-10…14, 17…20 — data contracts."""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError
from soc_shared.models import (
    DECLINE_MESSAGE,
    AskAnswer,
    AuditEvent,
    Decision,
    Evidence,
    IpReputation,
    KsorHit,
    LlmUsage,
    MaskedAlert,
    ScopeVerdict,
    WazuhAlert,
    WebSource,
)

NOW = datetime(2026, 11, 12, 3, 15, tzinfo=UTC)


class TestWazuhAlert:
    def test_parses_windows_fixture(self, win_4625: dict[str, Any]) -> None:
        alert = WazuhAlert.model_validate(win_4625)
        assert alert.rule.id == "60122"
        assert alert.rule.level == 5
        assert alert.rule.mitre.id == ["T1110"]
        assert alert.agent.name == "lab-ws01"
        assert alert.timestamp.utcoffset() is not None

    def test_parses_linux_and_keeps_extra_fields(self, linux_sshd: dict[str, Any]) -> None:
        alert = WazuhAlert.model_validate(linux_sshd)
        assert alert.data["srcip"] == "198.51.100.77"
        assert alert.model_extra is not None and "predecoder" in alert.model_extra

    def test_level_above_15_rejected(self, win_4625: dict[str, Any]) -> None:
        win_4625["rule"]["level"] = 16
        with pytest.raises(ValidationError):
            WazuhAlert.model_validate(win_4625)

    def test_missing_rule_rejected(self, win_4625: dict[str, Any]) -> None:
        del win_4625["rule"]
        with pytest.raises(ValidationError):
            WazuhAlert.model_validate(win_4625)


class TestKsorHit:
    def test_valid(self) -> None:
        hit = KsorHit(stable_id="knowledge/windows-events/event-4625", title="4625", snippet="...")
        assert hit.gate == "off"

    @pytest.mark.parametrize("bad", ["windows-events/event-4625", "knowledge/", "http://x", ""])
    def test_invalid_stable_id(self, bad: str) -> None:
        with pytest.raises(ValidationError):
            KsorHit(stable_id=bad, title="t", snippet="s")

    def test_frozen(self) -> None:
        hit = KsorHit(stable_id="knowledge/a", title="t", snippet="s")
        with pytest.raises(ValidationError):
            hit.title = "changed"  # type: ignore[misc]


class TestScope:
    def test_decline_message_exact(self) -> None:
        expected = (
            "This is a SOC Analyst Lab. "
            "Please ask only cybersecurity-related questions. JazakAllah."
        )
        assert expected == DECLINE_MESSAGE

    def test_verdict(self) -> None:
        v = ScopeVerdict(label="DECLINE", reason="offensive", category="offensive")
        assert not v.injection_suspected

    def test_bad_label(self) -> None:
        with pytest.raises(ValidationError):
            ScopeVerdict(label="MAYBE", reason="x")

    def test_reason_length_cap(self) -> None:
        with pytest.raises(ValidationError):
            ScopeVerdict(label="ALLOW_KSOR", reason="x" * 301)


class TestAskAnswer:
    def test_cited(self) -> None:
        a = AskAnswer(
            answer="4625 is a failed logon.",
            scope="ALLOW_KSOR",
            citations=["knowledge/windows-events/event-4625"],
            confidence=0.9,
        )
        assert a.citations

    def test_not_in_record_ok(self) -> None:
        AskAnswer(answer="not in this record", scope="ALLOW_KSOR", not_in_record=True, confidence=0)

    def test_web_only_ok_for_research(self) -> None:
        AskAnswer(
            answer="...",
            scope="ALLOW_CYBER_RESEARCH",
            web_sources=[WebSource(url="https://attack.mitre.org/techniques/T1110/")],
            confidence=0.4,
        )

    def test_uncited_rejected(self) -> None:
        with pytest.raises(ValidationError, match="citation"):
            AskAnswer(answer="trust me", scope="ALLOW_KSOR", confidence=0.9)

    def test_decline_must_use_exact_text(self) -> None:
        AskAnswer(answer=DECLINE_MESSAGE, scope="DECLINE", confidence=1)
        with pytest.raises(ValidationError):
            AskAnswer(answer="No.", scope="DECLINE", confidence=1)

    def test_bad_citation(self) -> None:
        with pytest.raises(ValidationError):
            AskAnswer(answer="x", scope="ALLOW_KSOR", citations=["wikipedia"], confidence=1)


class TestSmallModels:
    def test_evidence_needs_source(self) -> None:
        with pytest.raises(ValidationError):
            Evidence(fact="failed logon", source="")

    def test_web_source_label_fixed(self) -> None:
        w = WebSource(url="https://learn.microsoft.com/")
        assert w.label == "unverified"
        with pytest.raises(ValidationError):
            WebSource(url="not a url")

    def test_ip_reputation_token_only(self) -> None:
        IpReputation(token="<IP-1>", is_public=True, abuse_confidence_score=90)
        with pytest.raises(ValidationError):
            IpReputation(token="203.0.113.45", is_public=True)
        with pytest.raises(ValidationError):
            IpReputation(token="<IP-1>", is_public=True, abuse_confidence_score=101)

    def test_decision(self) -> None:
        Decision(note_id="n1", action="approve", decided_by="auth0|x", decided_at=NOW)
        with pytest.raises(ValidationError):
            Decision(note_id="n1", action="block", decided_by="x", decided_at=NOW)

    def test_audit_and_usage(self) -> None:
        AuditEvent(event="scope_decline", at=NOW, detail={"label": "DECLINE"})
        u = LlmUsage(
            request_id="r", agent="triage", model="m", input_tokens=1, output_tokens=2, cost_usd=0
        )
        assert u.output_tokens == 2
        with pytest.raises(ValidationError):
            LlmUsage(
                request_id="r", agent="a", model="m", input_tokens=-1, output_tokens=0, cost_usd=0
            )

    def test_unknown_field_forbidden(self) -> None:
        with pytest.raises(ValidationError):
            MaskedAlert(alert_id="1", rule_id="1", rule_level=1, payload={}, raw_ip="x")  # type: ignore[call-arg]
