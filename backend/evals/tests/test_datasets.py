"""FR-02-01…07 — the alert dataset: schema, composition, fact tracing, hygiene."""

import json
import re
from collections import Counter

import pytest
from soc_evals.datasets import DATA, load
from soc_shared.masking import find_unmasked_pii
from soc_shared.masking.ipclass import classify_ip

D = load()
LABELS = list(D.labels.values())
TARGET_ALERTS = 40
COMPLETE = len(D.alerts) == TARGET_ALERTS
PENDING = "10 alerts wait for INTENT Q1 (OTRF download) and Q2 (ruleset rule IDs)"


def test_every_alert_has_one_label_and_valid_schema() -> None:
    assert set(D.alerts) == set(D.labels)
    assert all(a.id == aid for aid, a in D.alerts.items())


def test_alert_json_has_no_eval_metadata() -> None:
    forbidden = {"_meta", "label", "verdict", "expected", "rationale", "escalate"}
    for path in (DATA / "alerts").glob("*.json"):
        assert not forbidden & set(json.loads(path.read_text("utf-8"))), path.name


def test_facts_trace_to_sources() -> None:
    for lab in LABELS:
        alert = D.alerts[lab.alert_id]
        allowed = D.ksor_mitre_ids | set(alert.rule.mitre.id)
        assert set(lab.mitre_ids) <= allowed, lab.alert_id
        assert set(lab.expected_stable_ids) <= D.ksor_stable_ids, lab.alert_id
        assert lab.rule_source in D.ksor_stable_ids, lab.alert_id


def test_every_escalation_condition_is_covered() -> None:
    covered = {c for lab in LABELS for c in [lab.escalate_condition, *lab.also_conditions] if c}
    assert covered == set(range(1, 9))


def test_minimums_so_far() -> None:
    v = Counter(lab.verdict.value for lab in LABELS)
    assert v["needs_info"] >= 4
    assert sum(not lab.escalate for lab in LABELS) >= 8
    assert sum(lab.playbook.startswith("false-positives/") for lab in LABELS) == 10


@pytest.mark.xfail(not COMPLETE, reason=PENDING, strict=True)
def test_final_composition() -> None:
    assert len(D.alerts) == TARGET_ALERTS
    assert sum(lab.verdict.value == "TP" for lab in LABELS) >= 20
    playbooks = {lab.playbook for lab in LABELS if lab.verdict.value == "TP"}
    assert len({p for p in playbooks if not p.startswith("false-positives/")}) >= 11


def test_context_is_input_only() -> None:
    assert set(D.contexts) <= set(D.alerts)
    for text in D.contexts.values():
        assert not re.search(r"\b(TP|FP|benign|verdict|escalate)\b", text, re.IGNORECASE)


def test_hygiene_only_lab_values() -> None:
    blob = "\n".join(p.read_text("utf-8") for p in (DATA / "alerts").glob("*.json"))
    blob += "\n".join(D.contexts.values())
    for ip in re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", blob):
        kind = classify_ip(ip)
        assert kind.startswith(("private", "special documentation")), f"non-lab IP {ip}"
    emails = [h for h in find_unmasked_pii(blob) if "@" in h]
    assert all(e.endswith((".example", ".lab")) for e in emails), emails


def test_all_labels_unverified_until_naveed_signs() -> None:
    assert all(not lab.verified for lab in LABELS)
