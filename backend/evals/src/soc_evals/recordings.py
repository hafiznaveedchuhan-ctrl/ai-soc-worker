"""Recorded predictions for the dry run (FR-02-22).

* oracle — predictions equal to the labels: proves the pipeline and scorer end to end
  (every target must PASS on it).
* faulty — the oracle plus planted mistakes: proves every check actually fires.
"""

from pathlib import Path

from soc_shared.models import (
    DECLINE_MESSAGE,
    AskAnswer,
    Evidence,
    TriageNote,
    Verdict,
    WazuhAlert,
    WebSource,
)

from soc_evals.datasets import AlertLabel, EvalData, Probe
from soc_evals.predictions import AlertPrediction, ProbePrediction, read_jsonl, write_jsonl

DRY = Path(__file__).resolve().parents[2] / "recordings/dry"
RESEARCH_URL = "https://attack.mitre.org/"

# Planted mistakes in faulty.jsonl: (item id, expected failing check).
PLANTED_ALERTS = {
    "EV-A001": "verdict",  # TP predicted as benign_TP → missed TP
    "EV-A005": "mitre",  # invented MITRE id
    "EV-A009": "leak",  # raw IP in the output text
    "EV-A011": "prediction",  # pipeline error
}
PLANTED_PROBES = {
    "EV-P001": "scope",  # offensive question answered (missed decline)
    "EV-P002": "decline_text",  # declined with the wrong text
    "EV-P061": "scope",  # in-scope question declined (false decline)
}


def oracle_note(label: AlertLabel, alert: WazuhAlert) -> TriageNote:
    return TriageNote(
        alert_id=label.alert_id,
        rule_id=alert.rule.id,
        rule_level=alert.rule.level,
        time_window_start=alert.timestamp,
        time_window_end=alert.timestamp,
        summary=f"Reference note for {label.alert_id} (masked tokens only).",
        evidence=[Evidence(fact=f"rule {alert.rule.id} fired", source="rule.id")],
        inference=["Reference inference (the label rationale is for the human reviewer only)."],
        mitre_ids=label.mitre_ids,
        citations=label.expected_stable_ids,
        verdict_suggestion=label.verdict,
        confidence=0.9,
        severity=label.severity,
        escalate=label.escalate,
        escalate_condition=label.escalate_condition,
        missing_info=["see rationale"] if label.verdict.value == "needs_info" else [],
    )


def oracle_answer(probe: Probe) -> ProbePrediction:
    if probe.expected_label == "DECLINE":
        ans = AskAnswer(answer=DECLINE_MESSAGE, scope="DECLINE", confidence=1.0)
        return ProbePrediction(
            probe_id=probe.probe_id, scope_label="DECLINE", answer=ans, output_text=DECLINE_MESSAGE
        )
    if probe.expected_label == "ALLOW_KSOR":
        ans = AskAnswer(
            answer="Reference answer.",
            scope="ALLOW_KSOR",
            citations=[probe.expected_stable_id or ""],
            confidence=0.9,
        )
    else:
        ans = AskAnswer(
            answer="Reference answer (unverified web source).",
            scope="ALLOW_CYBER_RESEARCH",
            web_sources=[WebSource(url=RESEARCH_URL)],
            confidence=0.5,
        )
    return ProbePrediction(
        probe_id=probe.probe_id, scope_label=ans.scope, answer=ans, output_text=ans.answer
    )


def oracle(data: EvalData) -> tuple[list[AlertPrediction], list[ProbePrediction]]:
    alerts = []
    for aid, label in sorted(data.labels.items()):
        n = oracle_note(label, data.alerts[aid])
        alerts.append(AlertPrediction(alert_id=aid, note=n, output_text=n.to_text()))
    probes = [oracle_answer(p) for _, p in sorted(data.probes.items())]
    return alerts, probes


def faulty(data: EvalData) -> tuple[list[AlertPrediction], list[ProbePrediction]]:
    alerts, probes = oracle(data)
    out_a: list[AlertPrediction] = []
    for p in alerts:
        if p.alert_id == "EV-A001" and p.note:
            note = p.note.model_copy(update={"verdict_suggestion": Verdict.BENIGN_TP})
            p = p.model_copy(update={"note": note})
        elif p.alert_id == "EV-A005" and p.note:
            p = p.model_copy(update={"note": p.note.model_copy(update={"mitre_ids": ["T9999"]})})
        elif p.alert_id == "EV-A009":
            p = p.model_copy(update={"output_text": p.output_text + "\nSource: 203.0.113.45"})
        elif p.alert_id == "EV-A011":
            p = AlertPrediction(alert_id=p.alert_id, error="timeout after 60 s")
        out_a.append(p)
    out_p: list[ProbePrediction] = []
    for q in probes:
        if q.probe_id == "EV-P001":
            q = q.model_copy(update={"scope_label": "ALLOW_CYBER_RESEARCH", "output_text": "x"})
        elif q.probe_id == "EV-P002":
            q = q.model_copy(update={"output_text": "No."})
        elif q.probe_id == "EV-P061":
            ans = AskAnswer(answer=DECLINE_MESSAGE, scope="DECLINE", confidence=1.0)
            q = q.model_copy(
                update={"scope_label": "DECLINE", "answer": ans, "output_text": DECLINE_MESSAGE}
            )
        out_p.append(q)
    return out_a, out_p


def write(data: EvalData, directory: Path = DRY) -> None:
    for name, (a, p) in (("oracle", oracle(data)), ("faulty", faulty(data))):
        write_jsonl(directory / f"{name}-alerts.jsonl", a)
        write_jsonl(directory / f"{name}-probes.jsonl", p)


def read(name: str, directory: Path = DRY) -> tuple[list[AlertPrediction], list[ProbePrediction]]:
    return (
        read_jsonl(directory / f"{name}-alerts.jsonl", AlertPrediction),
        read_jsonl(directory / f"{name}-probes.jsonl", ProbePrediction),
    )
