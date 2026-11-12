"""FR-02-05, FR-02-06 — the 95 scope probes and the KSOR reference snapshots."""

import csv
from collections import Counter

import pytest
from pydantic import ValidationError
from soc_evals.datasets import DATA, Probe, read_reference

ROWS = list(csv.DictReader((DATA / "scope/probes.csv").open(encoding="utf-8", newline="")))
PROBES = [Probe.from_row(r) for r in ROWS]
STABLE = read_reference(DATA / "reference/ksor_stable_ids.txt")


def test_counts_per_set() -> None:
    assert len(PROBES) == 95
    assert Counter(p.set for p in PROBES) == {
        "DECLINE": 30,
        "ALLOW_CYBER_RESEARCH": 25,
        "ALLOW_KSOR": 30,
        "NON_CYBER": 10,
    }


def test_unique_ids_and_questions() -> None:
    assert len({p.probe_id for p in PROBES}) == 95
    assert len({p.question.casefold() for p in PROBES}) == 95


def test_injection_probes() -> None:
    assert sum(p.category == "prompt_injection" for p in PROBES) == 5


def test_ksor_probes_point_to_real_pages_across_folders() -> None:
    ksor = [p for p in PROBES if p.set == "ALLOW_KSOR"]
    assert all(p.expected_stable_id in STABLE for p in ksor)
    folders = {p.expected_stable_id.split("/")[1] for p in ksor if p.expected_stable_id}
    assert len(folders) >= 8


def test_handbook_probes_keep_their_origin() -> None:
    from_hb = [p for p in PROBES if p.origin.startswith("handbook:")]
    assert len(from_hb) == 25 + 10 + 30


def test_unverified_until_naveed_signs() -> None:
    assert all(p.verified_by is None for p in PROBES)


@pytest.mark.parametrize(
    ("pset", "expected"),
    [("NON_CYBER", "ALLOW_KSOR"), ("DECLINE", "ALLOW_CYBER_RESEARCH"), ("ALLOW_KSOR", "DECLINE")],
)
def test_set_must_match_expected_label(pset: str, expected: str) -> None:
    with pytest.raises(ValidationError):
        Probe(
            probe_id="EV-P999",
            set=pset,
            expected_label=expected,
            category="c",
            question="a question?",
            origin="new",
        )


def test_ksor_probe_needs_stable_id() -> None:
    with pytest.raises(ValidationError):
        Probe(
            probe_id="EV-P999",
            set="ALLOW_KSOR",
            expected_label="ALLOW_KSOR",
            category="ksor",
            question="a question?",
            origin="new",
        )


def test_mitre_snapshot() -> None:
    mitre = read_reference(DATA / "reference/ksor_mitre_ids.txt")
    assert {"T1110", "T1110.001", "T1078", "T1685.005"} <= mitre
