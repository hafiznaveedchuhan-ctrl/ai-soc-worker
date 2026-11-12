"""Load and validate the eval datasets (FR-02-01…07).

Labels live in CSV files, never inside the alert JSON: WazuhAlert allows extra fields, so any
metadata inside an alert could ride along into a prompt and leak the expected answer.
"""

import csv
import json
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from soc_shared.models import (
    MITRE_ID_PATTERN,
    STABLE_ID_PATTERN,
    ScopeLabel,
    Severity,
    Verdict,
    WazuhAlert,
)

DATA = Path(__file__).resolve().parents[2] / "data"

ProbeSet = Literal["DECLINE", "ALLOW_KSOR", "ALLOW_CYBER_RESEARCH", "NON_CYBER"]
EXPECTED_FOR_SET: dict[str, str] = {
    "DECLINE": "DECLINE",
    "NON_CYBER": "DECLINE",
    "ALLOW_KSOR": "ALLOW_KSOR",
    "ALLOW_CYBER_RESEARCH": "ALLOW_CYBER_RESEARCH",
}


class DatasetError(ValueError):
    pass


def _split(value: str) -> list[str]:
    return [v.strip() for v in value.split(";") if v.strip()]


class AlertLabel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alert_id: str = Field(pattern=r"^EV-A\d{3}$")
    source: Literal["SYNTHETIC", "OTRF"]
    source_ref: str = Field(min_length=1)
    playbook: str  # a handbook playbook slug, or "false-positives/<page>"
    verdict: Verdict
    severity: Severity
    escalate: bool
    escalate_condition: int | None = Field(default=None, ge=1, le=8)
    mitre_ids: list[str] = Field(default_factory=list)
    expected_stable_ids: list[str] = Field(default_factory=list)
    rule_source: str = Field(min_length=1)
    rationale: str = Field(min_length=10)
    verified_by: str | None = None
    verified_at: date | None = None

    @model_validator(mode="after")
    def _rules(self) -> Self:
        if self.escalate != (self.escalate_condition is not None):
            raise ValueError("escalate=yes needs escalate_condition and vice versa")
        for m in self.mitre_ids:
            if not re.fullmatch(MITRE_ID_PATTERN, m):
                raise ValueError(f"bad MITRE id {m!r}")
        for s in self.expected_stable_ids:
            if not re.fullmatch(STABLE_ID_PATTERN, s):
                raise ValueError(f"bad stable_id {s!r}")
        if not self.expected_stable_ids:
            raise ValueError("every label needs at least one expected handbook page")
        return self

    @property
    def verified(self) -> bool:
        return bool(self.verified_by)

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "AlertLabel":
        return cls.model_validate(
            {
                **row,
                "escalate": {"yes": True, "no": False}[row["escalate"].strip()],
                "escalate_condition": row["escalate_condition"].strip() or None,
                "mitre_ids": _split(row["mitre_ids"]),
                "expected_stable_ids": _split(row["expected_stable_ids"]),
                "verified_by": row["verified_by"].strip() or None,
                "verified_at": row["verified_at"].strip() or None,
            }
        )


class Probe(BaseModel):
    model_config = ConfigDict(extra="forbid")

    probe_id: str = Field(pattern=r"^EV-P\d{3}$")
    set: ProbeSet
    expected_label: ScopeLabel
    category: str = Field(min_length=1)
    question: str = Field(min_length=5)
    expected_stable_id: str | None = None
    origin: str = Field(min_length=3)
    verified_by: str | None = None

    @model_validator(mode="after")
    def _rules(self) -> Self:
        if self.expected_label != EXPECTED_FOR_SET[self.set]:
            raise ValueError(f"set {self.set} must expect {EXPECTED_FOR_SET[self.set]}")
        if self.set == "ALLOW_KSOR":
            if not self.expected_stable_id or not re.fullmatch(
                STABLE_ID_PATTERN, self.expected_stable_id
            ):
                raise ValueError("ALLOW_KSOR probes need a valid expected_stable_id")
        elif self.expected_stable_id:
            raise ValueError("only ALLOW_KSOR probes have an expected_stable_id")
        return self

    @property
    def verified(self) -> bool:
        return bool(self.verified_by)

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "Probe":
        return cls.model_validate(
            {
                **row,
                "expected_stable_id": row["expected_stable_id"].strip() or None,
                "verified_by": row["verified_by"].strip() or None,
            }
        )


@dataclass
class EvalData:
    alerts: dict[str, WazuhAlert] = field(default_factory=dict)
    labels: dict[str, AlertLabel] = field(default_factory=dict)
    probes: dict[str, Probe] = field(default_factory=dict)
    ksor_mitre_ids: set[str] = field(default_factory=set)
    ksor_stable_ids: set[str] = field(default_factory=set)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_reference(path: Path) -> set[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return {ln.strip() for ln in lines if ln.strip() and not ln.startswith("#")}


def load(data_dir: Path = DATA) -> EvalData:
    """Load everything; raise DatasetError naming the file and row of the first problem."""
    out = EvalData()
    out.ksor_mitre_ids = read_reference(data_dir / "reference/ksor_mitre_ids.txt")
    out.ksor_stable_ids = read_reference(data_dir / "reference/ksor_stable_ids.txt")

    for path in sorted((data_dir / "alerts").glob("EV-A*.json")):
        try:
            out.alerts[path.stem] = WazuhAlert.model_validate(json.loads(path.read_text("utf-8")))
        except (ValidationError, json.JSONDecodeError) as exc:
            raise DatasetError(f"{path.name}: {exc}") from exc

    for i, row in enumerate(_read_csv(data_dir / "labels.csv"), start=2):
        try:
            label = AlertLabel.from_row(row)
        except (ValidationError, KeyError) as exc:
            raise DatasetError(f"labels.csv row {i}: {exc}") from exc
        if label.alert_id in out.labels:
            raise DatasetError(f"labels.csv row {i}: duplicate {label.alert_id}")
        if label.alert_id not in out.alerts:
            raise DatasetError(f"labels.csv row {i}: no alert file for {label.alert_id}")
        out.labels[label.alert_id] = label
    missing = set(out.alerts) - set(out.labels)
    if missing:
        raise DatasetError(f"alerts without a label: {sorted(missing)}")

    for i, row in enumerate(_read_csv(data_dir / "scope/probes.csv"), start=2):
        try:
            probe = Probe.from_row(row)
        except (ValidationError, KeyError) as exc:
            raise DatasetError(f"probes.csv row {i}: {exc}") from exc
        if probe.probe_id in out.probes:
            raise DatasetError(f"probes.csv row {i}: duplicate {probe.probe_id}")
        out.probes[probe.probe_id] = probe
    return out
