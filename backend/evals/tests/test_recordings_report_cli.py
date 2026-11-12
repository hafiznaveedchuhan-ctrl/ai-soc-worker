"""FR-02-16, 20…24 — recordings, report, CLI and review sheet."""

from pathlib import Path

import pytest
from soc_evals import recordings, review
from soc_evals.cli import main, score_and_report
from soc_evals.datasets import load
from soc_evals.predictions import AlertPrediction, read_jsonl
from soc_evals.report import RunInfo
from soc_evals.scoring.scope import score_scope
from soc_evals.scoring.triage import alert_mask_map, score_triage
from soc_shared.masking import find_leaks

D = load()
INFO = RunInfo("dry", "2026-01-01", "abc1234", "test")


def test_committed_recordings_match_the_labels(tmp_path: Path) -> None:
    recordings.write(D, tmp_path)
    for name in ("oracle-alerts", "oracle-probes", "faulty-alerts", "faulty-probes"):
        assert (tmp_path / f"{name}.jsonl").read_text() == (
            recordings.DRY / f"{name}.jsonl"
        ).read_text(), f"{name}.jsonl is stale: run `make eval-recordings`"


def test_oracle_passes_every_target() -> None:
    alerts, probes = recordings.read("oracle")
    md, all_pass = score_and_report(D, alerts, probes, INFO)
    assert all_pass
    assert "## Failures (0)" in md


def test_faulty_fails_exactly_the_planted_checks() -> None:
    alerts, probes = recordings.read("faulty")
    t = score_triage(D.labels, D.alerts, {p.alert_id: p for p in alerts}, D.ksor_mitre_ids)
    s = score_scope(D.probes, {p.probe_id: p for p in probes})
    got_alerts = {(f.item_id, f.check) for f in t.failures}
    got_probes = {(f.item_id, f.check) for f in s.failures}
    assert {(k, v) for k, v in recordings.PLANTED_ALERTS.items()} <= got_alerts
    assert {f[0] for f in got_alerts} == set(recordings.PLANTED_ALERTS)
    assert {(k, v) for k, v in recordings.PLANTED_PROBES.items()} <= got_probes
    assert {f[0] for f in got_probes} == set(recordings.PLANTED_PROBES)
    md, all_pass = score_and_report(D, alerts, probes, INFO)
    assert not all_pass and "| TP recall | 19/21 = 90.5% |" in md


def test_report_shapes() -> None:
    alerts, probes = recordings.read("oracle")
    md, _ = score_and_report(D, alerts, probes, INFO)
    for section in (
        "## Targets",
        "## Triage",
        "### Confusion matrix",
        "## Scope",
        "## Cost",
        "## Known",
    ):
        assert section in md
    assert "Labels verified by Naveed | alerts 0/40 = 0.0%" in md
    assert "$" not in md.replace("Total $", "").replace("Mean $", "")  # no unfilled placeholders


def test_oracle_outputs_are_masked() -> None:
    for p in read_jsonl(recordings.DRY / "oracle-alerts.jsonl", AlertPrediction):
        assert find_leaks(p.output_text, alert_mask_map(D.alerts[p.alert_id])) == []


def test_cli_dry_ok(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["dry"]) == 0
    assert "all PASS" in capsys.readouterr().out


def test_cli_paid_refuses(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["paid"]) == 1
    assert main(["paid", "--yes-paid"]) == 1
    assert "nothing was called" in capsys.readouterr().out


def test_cli_stats(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["stats"]) == 0
    assert "probes: 95" in capsys.readouterr().out


def test_review_sheet_is_masked(tmp_path: Path) -> None:
    path = review.write(D, tmp_path / "r.md")
    text = path.read_text()
    assert text.count("### [ ] EV-A") == len(D.labels)
    assert "203.0.113.45" not in text and "<IP-" in text
