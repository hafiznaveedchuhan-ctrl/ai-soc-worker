"""FR-02-12 — triage metrics on hand-made predictions with known answers."""

from soc_evals.datasets import AlertLabel
from soc_evals.predictions import AlertPrediction
from soc_evals.scoring.triage import TriageScores, score_triage
from soc_evals.testing import alert, apred, label, note
from soc_shared.models import WazuhAlert

KSOR_MITRE = {"T1110", "T1078"}


def run(
    labels: list[AlertLabel],
    preds: list[AlertPrediction],
    alerts: dict[str, WazuhAlert] | None = None,
) -> TriageScores:
    alerts = alerts or {lab.alert_id: alert(lab.alert_id) for lab in labels}
    return score_triage(
        {lab.alert_id: lab for lab in labels}, alerts, {p.alert_id: p for p in preds}, KSOR_MITRE
    )


def test_perfect() -> None:
    labels = [label("EV-A001"), label("EV-A002", "FP"), label("EV-A003", "TP", escalate=4)]
    preds = [
        apred("EV-A001", note("EV-A001")),
        apred("EV-A002", note("EV-A002", "FP")),
        apred("EV-A003", note("EV-A003", escalate=4)),
    ]
    s = run(labels, preds)
    assert str(s.tp_recall) == "2/2 = 100.0%"
    assert str(s.tp_precision) == "2/2 = 100.0%"
    assert str(s.verdict_accuracy) == "3/3 = 100.0%"
    assert str(s.condition_agreement) == "1/1 = 100.0%"
    assert s.failures == []


def test_missed_tp_and_false_tp() -> None:
    labels = [label("EV-A001"), label("EV-A002", "FP")]
    preds = [
        apred("EV-A001", note("EV-A001", "benign_TP")),
        apred("EV-A002", note("EV-A002", "TP")),
    ]
    s = run(labels, preds)
    assert str(s.tp_recall) == "0/1 = 0.0%"
    assert str(s.tp_precision) == "0/1 = 0.0%"
    assert s.confusion["TP"]["benign_TP"] == 1 and s.confusion["FP"]["TP"] == 1


def test_missing_prediction_is_an_error_and_a_tp_miss() -> None:
    s = run([label("EV-A001")], [])
    assert s.errors == 1
    assert str(s.tp_recall) == "0/1 = 0.0%"
    assert {f.check for f in s.failures} == {"prediction", "tp_recall"}
    assert s.confusion["TP"]["error"] == 1


def test_escalation_and_condition() -> None:
    labels = [label("EV-A001", escalate=4), label("EV-A002", escalate=2), label("EV-A003")]
    preds = [
        apred("EV-A001", note("EV-A001", escalate=4)),
        apred("EV-A002", note("EV-A002", escalate=1)),
        apred("EV-A003", note("EV-A003", escalate=1)),
    ]
    s = run(labels, preds)
    assert str(s.escalation_agreement) == "2/3 = 66.7%"
    assert str(s.condition_agreement) == "1/2 = 50.0%"


def test_page_hit() -> None:
    s = run([label("EV-A001")], [apred("EV-A001", note("EV-A001", citations=["knowledge/other"]))])
    assert str(s.page_hit) == "0/1 = 0.0%"


def test_invented_mitre_is_caught_but_alert_mitre_is_allowed() -> None:
    labels = [label("EV-A001"), label("EV-A002")]
    alerts = {"EV-A001": alert("EV-A001"), "EV-A002": alert("EV-A002", mitre=["T1070.004"])}
    preds = [
        apred("EV-A001", note("EV-A001", mitre=["T9999"])),
        apred("EV-A002", note("EV-A002", mitre=["T1070.004"])),
    ]
    s = run(labels, preds, alerts)
    assert str(s.mitre_clean) == "1/2 = 50.0%"
    assert any(f.check == "mitre" and f.item_id == "EV-A001" for f in s.failures)


def test_leaks() -> None:
    labels = [label("EV-A001"), label("EV-A002"), label("EV-A003")]
    preds = [
        apred("EV-A001", note("EV-A001"), text="from <IP-1>"),
        apred("EV-A002", note("EV-A002"), text="from 203.0.113.9"),
        apred("EV-A003", note("EV-A003"), text="host LAB-WS01 did it"),
    ]
    s = run(labels, preds)
    assert str(s.leak_free) == "1/3 = 33.3%"
