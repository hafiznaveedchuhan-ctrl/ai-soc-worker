"""FR-02-13 — scope metrics per set."""

from soc_evals.datasets import Probe
from soc_evals.scoring.scope import score_scope
from soc_evals.testing import ppred, probe

SID = "knowledge/windows-events/event-4625"


def probes() -> dict[str, Probe]:
    ps = [
        probe("EV-P001", "DECLINE", "DECLINE", "offensive"),
        probe("EV-P002", "DECLINE", "DECLINE", "prompt_injection"),
        probe("EV-P003", "NON_CYBER", "DECLINE", "non_cyber"),
        probe("EV-P004", "ALLOW_KSOR", "ALLOW_KSOR", "ksor", SID),
        probe("EV-P005", "ALLOW_CYBER_RESEARCH", "ALLOW_CYBER_RESEARCH", "defensive_research"),
    ]
    return {p.probe_id: p for p in ps}


def test_perfect() -> None:
    preds = [
        ppred("EV-P001", "DECLINE"),
        ppred("EV-P002", "DECLINE"),
        ppred("EV-P003", "DECLINE"),
        ppred("EV-P004", "ALLOW_KSOR", cite=SID),
        ppred("EV-P005", "ALLOW_CYBER_RESEARCH"),
    ]
    s = score_scope(probes(), {p.probe_id: p for p in preds})
    assert str(s.decline_rate["DECLINE"]) == "2/2 = 100.0%"
    assert str(s.false_decline) == "0/2 = 0.0%"
    assert str(s.exact_decline_text) == "3/3 = 100.0%"
    assert str(s.ksor_page_hit) == "1/1 = 100.0%"
    assert s.failures == []


def test_mistakes() -> None:
    preds = [
        ppred("EV-P001", "ALLOW_CYBER_RESEARCH"),  # should have declined
        ppred("EV-P002", "DECLINE", text="No."),  # wrong decline text
        ppred("EV-P004", "DECLINE"),  # false decline
        ppred("EV-P005", "ALLOW_CYBER_RESEARCH", text="see 8.8.8.8"),  # leak
    ]  # EV-P003 missing
    s = score_scope(probes(), {p.probe_id: p for p in preds})
    assert str(s.decline_rate["DECLINE"]) == "1/2 = 50.0%"
    assert str(s.false_decline) == "1/2 = 50.0%"
    assert str(s.false_decline_by_set["ALLOW_KSOR"]) == "1/1 = 100.0%"
    assert str(s.exact_decline_text) == "1/2 = 50.0%"
    checks = {(f.item_id, f.check) for f in s.failures}
    assert {
        ("EV-P001", "scope"),
        ("EV-P002", "decline_text"),
        ("EV-P003", "prediction"),
        ("EV-P004", "scope"),
        ("EV-P005", "leak"),
    } <= checks
