"""`python -m soc_evals {dry,paid,stats,review,recordings}` (FR-02-20…24)."""

import argparse
import subprocess
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from soc_evals import recordings, review
from soc_evals.datasets import DatasetError, EvalData, load
from soc_evals.predictions import AlertPrediction, ProbePrediction
from soc_evals.rate import Rate
from soc_evals.report import RunInfo, render
from soc_evals.scoring.cost import cost_latency
from soc_evals.scoring.scope import score_scope
from soc_evals.scoring.triage import score_triage
from soc_evals.targets import evaluate

REPORTS = Path(__file__).resolve().parents[2] / "reports"


def _git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],  # noqa: S607
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def score_and_report(
    data: EvalData,
    alerts: list[AlertPrediction],
    probes: list[ProbePrediction],
    info: RunInfo,
) -> tuple[str, bool]:
    t = score_triage(data.labels, data.alerts, {p.alert_id: p for p in alerts}, data.ksor_mitre_ids)
    s = score_scope(data.probes, {p.probe_id: p for p in probes})
    targets = evaluate(t, s)
    md = render(info, data, t, s, targets, cost_latency(alerts), cost_latency(probes))
    return md, all(r.passed for r in targets)


def cmd_dry(_: argparse.Namespace) -> int:
    data = load()
    n = len(data.alerts) + len(data.probes)
    print(f"datasets: {Rate(n, n)} valid ({len(data.alerts)} alerts, {len(data.probes)} probes)")
    alerts, probes = recordings.read("oracle")
    today = datetime.now(UTC).date().isoformat()
    md, all_pass = score_and_report(
        data, alerts, probes, RunInfo("dry", today, _git_sha(), "recordings/dry/oracle-*.jsonl")
    )
    path = REPORTS / f"{today}-dry-report.md"
    path.write_text(md, encoding="utf-8")
    print(f"report: {path.relative_to(REPORTS.parents[1])}")
    print("oracle targets:", "all PASS" if all_pass else "SOME FAIL (scorer or dataset bug)")
    return 0 if all_pass else 1


def cmd_paid(args: argparse.Namespace) -> int:
    if not args.yes_paid:
        print("refused: a paid run needs --yes-paid (and Naveed's explicit 'haan').")
        return 1
    print("refused: the agent pipeline arrives in features 05/06; nothing was called.")
    return 1


def cmd_stats(_: argparse.Namespace) -> int:
    d = load()
    labs = list(d.labels.values())
    print(f"alerts: {len(d.alerts)}  (verified {Rate(sum(x.verified for x in labs), len(labs))})")
    for name, counter in (
        ("verdict", Counter(x.verdict.value for x in labs)),
        ("severity", Counter(x.severity.value for x in labs)),
        ("escalate", Counter("yes" if x.escalate else "no" for x in labs)),
        (
            "condition",
            Counter(c for x in labs for c in [x.escalate_condition, *x.also_conditions] if c),
        ),
        ("source", Counter(x.source for x in labs)),
        ("playbook", Counter(x.playbook for x in labs)),
    ):
        print(f"  {name}: " + ", ".join(f"{k}={v}" for k, v in sorted(counter.items(), key=str)))
    ps = list(d.probes.values())
    print(f"probes: {len(ps)}  (verified {Rate(sum(p.verified for p in ps), len(ps))})")
    print("  set: " + ", ".join(f"{k}={v}" for k, v in sorted(Counter(p.set for p in ps).items())))
    return 0


def cmd_review(_: argparse.Namespace) -> int:
    path = review.write(load())
    print(f"review sheet: {path}")
    return 0


def cmd_recordings(_: argparse.Namespace) -> int:
    recordings.write(load())
    print(f"recordings written to {recordings.DRY}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="soc_evals")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("dry", help="free, offline: validate datasets + score recorded predictions")
    paid = sub.add_parser("paid", help="PAID run with the real agents (features 05/06)")
    paid.add_argument("--yes-paid", action="store_true")
    sub.add_parser("stats", help="dataset composition")
    sub.add_parser("review", help="write the label review sheet")
    sub.add_parser("recordings", help="regenerate recordings/dry from the labels")
    args = parser.parse_args(argv)
    handlers = {
        "dry": cmd_dry,
        "paid": cmd_paid,
        "stats": cmd_stats,
        "review": cmd_review,
        "recordings": cmd_recordings,
    }
    try:
        return handlers[args.cmd](args)
    except DatasetError as exc:
        print(f"dataset error: {exc}", file=sys.stderr)
        return 2
