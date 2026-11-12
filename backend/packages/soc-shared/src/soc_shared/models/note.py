"""TriageNote — the handbook's triage-note template as a typed model (FR-01-14…16).

Source: ../handbook/knowledge/triage-note/note-template.md (field order and allowed values)
and knowledge/rules-map/escalation-policy.md (conditions 1–8).
"""

import re
from datetime import datetime
from enum import StrEnum
from typing import Literal, Self

from pydantic import Field, model_validator

from soc_shared.models._base import StrictModel, ValueModel
from soc_shared.models.ksor import STABLE_ID_PATTERN

MITRE_ID_PATTERN = r"^T\d{4}(\.\d{3})?$"
FINAL_LINE = "Final decision: human analyst"


class Verdict(StrEnum):
    TP = "TP"
    BENIGN_TP = "benign_TP"
    FP = "FP"
    NEEDS_INFO = "needs_info"

    @property
    def display(self) -> str:
        """The spelling used in the handbook template."""
        return {"benign_TP": "benign TP", "needs_info": "needs-info"}.get(self.value, self.value)


class Severity(StrEnum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class Evidence(ValueModel):
    fact: str = Field(min_length=1)
    source: str = Field(min_length=1)  # the alert field or event ID the fact comes from


class WebSource(ValueModel):
    # A plain string with a pattern, not HttpUrl: OpenAI strict structured output rejects
    # JSON-schema `format: uri` (pilot 2026-11-12, HTTP 400). Exact strings also compare exactly
    # with the URLs the web_search tool returned (HttpUrl would normalise them).
    url: str = Field(pattern=r"^https?://[^\s<>\"]+$", max_length=2000)
    title: str | None = None
    label: Literal["unverified"] = "unverified"


class IpReputation(ValueModel):
    token: str = Field(pattern=r"^<IP-\d+>$")  # masked — never the raw IP
    is_public: bool
    abuse_confidence_score: int | None = Field(default=None, ge=0, le=100)
    total_reports: int | None = Field(default=None, ge=0)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    checked_at: datetime | None = None


class TriageNote(StrictModel):
    alert_id: str
    rule_id: str
    rule_level: int = Field(ge=0, le=15)
    time_window_start: datetime
    time_window_end: datetime
    summary: str = Field(min_length=1)
    evidence: list[Evidence] = Field(min_length=1)
    inference: list[str] = Field(default_factory=list)
    mitre_ids: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    web_sources: list[WebSource] = Field(default_factory=list)
    ip_reputation: list[IpReputation] = Field(default_factory=list)
    verdict_suggestion: Verdict
    confidence: float = Field(ge=0.0, le=1.0)
    severity: Severity
    escalate: bool
    escalate_condition: int | None = Field(default=None, ge=1, le=8)
    escalate_reason: str | None = None
    missing_info: list[str] = Field(default_factory=list)
    final_decision_by: Literal["human"] = "human"

    @model_validator(mode="after")
    def _check_rules(self) -> Self:
        for mid in self.mitre_ids:
            if not re.fullmatch(MITRE_ID_PATTERN, mid):
                raise ValueError(f"invalid MITRE technique ID: {mid!r}")
        for cid in self.citations:
            if not re.fullmatch(STABLE_ID_PATTERN, cid):
                raise ValueError(f"citation is not a KSOR stable_id: {cid!r}")
        if self.time_window_end < self.time_window_start:
            raise ValueError("time_window_end is before time_window_start")
        # (a) escalate <=> a handbook escalation condition number
        if self.escalate and self.escalate_condition is None:
            raise ValueError("escalate=True needs escalate_condition (1–8, escalation policy)")
        if not self.escalate and self.escalate_condition is not None:
            raise ValueError("escalate_condition is set but escalate=False")
        # (b) needs-info must say what is missing
        if self.verdict_suggestion is Verdict.NEEDS_INFO and not self.missing_info:
            raise ValueError("verdict needs_info requires missing_info")
        # (c) a verdict or an escalation needs a KSOR citation; web sources alone are never enough
        if (
            self.verdict_suggestion is not Verdict.NEEDS_INFO or self.escalate
        ) and not self.citations:
            raise ValueError("a verdict or escalation needs at least one KSOR citation")
        return self

    @property
    def confidence_band(self) -> Literal["low", "medium", "high"]:
        if self.confidence < 0.40:
            return "low"
        if self.confidence < 0.70:
            return "medium"
        return "high"

    def to_text(self) -> str:
        """Render the handbook template, fields in the fixed order; the last line is fixed."""

        def iso(dt: datetime) -> str:
            return dt.isoformat().replace("+00:00", "Z")

        verdict = self.verdict_suggestion.display
        if self.missing_info:
            verdict += " — missing: " + "; ".join(self.missing_info)
        escalate = f"yes — condition #{self.escalate_condition}" if self.escalate else "no"
        if self.escalate and self.escalate_reason:
            escalate += f" — {self.escalate_reason}"
        lines = [
            f"Alert ID:        {self.alert_id}          "
            f"Rule: {self.rule_id} (level {self.rule_level})",
            f"Time window:     {iso(self.time_window_start)} – {iso(self.time_window_end)}",
            f"Summary:         {self.summary}",
            "Evidence:",
            *[f"  - {e.fact} — source: {e.source}" for e in self.evidence],
            "Inference:",
            *[f"  - {i}" for i in self.inference],
            f"MITRE ATT&CK:    {', '.join(self.mitre_ids) or 'none'}",
            f"Handbook:        {', '.join(self.citations) or 'not in this record'}",
        ]
        if self.web_sources:
            lines.append(
                "Web sources:     "
                + ", ".join(f"unverified web source ({w.url})" for w in self.web_sources)
            )
        lines += [
            f"Verdict (suggested): {verdict}",
            f"Confidence:      {self.confidence:.2f} ({self.confidence_band})",
            f"Severity:        {self.severity.value}",
            f"Escalate:        {escalate}",
            FINAL_LINE,
        ]
        return "\n".join(lines)
