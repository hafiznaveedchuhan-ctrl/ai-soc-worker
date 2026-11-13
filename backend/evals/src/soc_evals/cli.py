"""`python -m soc_evals {dry,paid,estimate,stats,review,recordings}` (FR-02-20…24, FR-11-*)."""

import argparse
import asyncio
import os
import subprocess
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from soc_evals import estimate, recordings, review
from soc_evals.datasets import DatasetError, EvalData, load
from soc_evals.pipeline import RunOutcome, Selection, run_all, subset
from soc_evals.predictions import AlertPrediction, ProbePrediction, read_jsonl, write_jsonl
from soc_evals.rate import Rate
from soc_evals.report import RunInfo, render
from soc_evals.scoring.common import Failure
from soc_evals.scoring.cost import cost_latency
from soc_evals.scoring.scope import score_scope
from soc_evals.scoring.triage import score_triage
from soc_evals.targets import evaluate

EVALS = Path(__file__).resolve().parents[2]
REPORTS = EVALS / "reports"
PAID = EVALS / "recordings/paid"
ENV_FILE = EVALS.parent / ".env"  # read by the settings classes only — never printed


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
    return md + diagnostics(t.failures + s.failures, [*alerts, *probes]), all(
        r.passed for r in targets
    )


def diagnostics(failures: list[Failure], preds: list[AlertPrediction | ProbePrediction]) -> str:
    """The flow events of every failed item (masked breadcrumbs), so a failure has a reason."""
    failed = {f.item_id for f in failures}
    by_id = {getattr(p, "alert_id", None) or getattr(p, "probe_id", ""): p for p in preds}
    rows = [
        f"- **{i}**: " + " → ".join(e.replace("|", "/") for e in by_id[i].events)
        for i in sorted(failed)
        if i in by_id and by_id[i].events
    ]
    return "\n## Diagnostics (flow events of failed items)\n" + ("\n".join(rows) or "None.") + "\n"


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
    """PAID run through the real flows (feature 11). Needs --yes-paid AND CONFIRM=haan."""
    if not args.yes_paid or os.environ.get("CONFIRM") != "haan":
        print("refused: a paid run needs --yes-paid AND CONFIRM=haan (Naveed's explicit 'haan').")
        print("nothing was called.")
        return 1
    from agents import set_trace_processors

    from soc_evals import live

    data = load()
    selection = Selection(
        only=args.only,
        ids=frozenset(i.strip() for i in args.ids.split(",") if i.strip()),
        limit=args.limit,
    )
    if not args.export_traces:
        set_trace_processors([])  # FR-11-10: no trace export unless asked
    env = ENV_FILE if ENV_FILE.exists() else None
    try:
        n_tools = asyncio.run(live.preflight(live.handbook_url(env)))
    except live.PreflightError as exc:
        print(f"refused: {exc}")
        return 1
    print(f"pre-flight: handbook MCP up ({n_tools} tools)")
    stem = args.resume or f"{datetime.now(UTC):%Y-%m-%d-%H%M}-{_git_sha()}"
    files = {k: PAID / f"{stem}-{k}.jsonl" for k in ("alerts", "probes")}
    if args.resume and not files["alerts"].exists() and not files["probes"].exists():
        print(f"refused: nothing to resume — no recordings/paid/{stem}-*.jsonl")
        return 1
    done = (
        read_jsonl(files["alerts"], AlertPrediction) if files["alerts"].exists() else [],
        read_jsonl(files["probes"], ProbePrediction) if files["probes"].exists() else [],
    )
    PAID.mkdir(parents=True, exist_ok=True)
    print(f"journal: recordings/paid/{stem}-*.jsonl (resume with --resume {stem})", flush=True)
    pipeline, models = live.build_live(env)
    outcome = asyncio.run(
        run_all(
            data,
            pipeline,
            selection,
            args.max_usd,
            progress=lambda m: print(m, flush=True),
            done=done,
            sink=lambda p: append_jsonl(files, p),
        )
    )
    return finish_paid(data, outcome, models, args.max_usd, stem=stem)


def append_jsonl(files: dict[str, Path], pred: AlertPrediction | ProbePrediction) -> None:
    """Journal one prediction the moment it exists (resumable runs)."""
    kind = "alerts" if isinstance(pred, AlertPrediction) else "probes"
    with files[kind].open("a", encoding="utf-8") as f:
        f.write(pred.model_dump_json() + "\n")


def finish_paid(
    data: EvalData,
    outcome: RunOutcome,
    models: str,
    max_usd: float,
    reports: Path | None = None,
    recordings_dir: Path | None = None,
    stem: str | None = None,
) -> int:
    """Write the JSONL + report for a paid run (FR-11-09). Separate so tests can call it."""
    reports = reports or REPORTS
    recordings_dir = recordings_dir or PAID
    recordings_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now(UTC).date().isoformat()
    sha = _git_sha()
    stem = stem or f"{today}-{sha}"
    # rewrite the journal in a clean, sorted form (same predictions)
    write_jsonl(recordings_dir / f"{stem}-alerts.jsonl", outcome.alerts)
    write_jsonl(recordings_dir / f"{stem}-probes.jsonl", outcome.probes)
    full = len(data.alerts) + len(data.probes)
    note = "full run" if outcome.ran == full else f"partial: {outcome.ran}/{full} items"
    if outcome.stopped_at_cap:
        note += (
            f" · STOPPED at the run cap ${max_usd:.2f} ({outcome.ran}/{outcome.planned} planned)"
        )
    note += f" · spent ${outcome.spent_usd:.4f}"
    if outcome.ledger_usd is not None:
        note += (
            f" (ledger-verified ${outcome.ledger_usd:.4f}; "
            f"reported in predictions ${outcome.reported_usd:.4f})"
        )
    info = RunInfo("paid", today, sha, f"recordings/paid/{stem}-*.jsonl", models, note)
    md, all_pass = score_and_report(subset(data, outcome), outcome.alerts, outcome.probes, info)
    name = "paid-report" if outcome.ran == full else "paid-pilot-report"
    path = reports / f"{today}-{name}.md"
    path.write_text(md, encoding="utf-8")
    print(f"{note}\nreport: {path}")
    print("targets:", "all PASS" if all_pass else "SOME FAIL (see the report)")
    return 0 if all_pass else 3


def cmd_estimate(_: argparse.Namespace) -> int:
    from agent_service.settings import DEFAULT_PRICES, AgentSettings

    model = AgentSettings().model_default
    price_in, price_out = DEFAULT_PRICES[model]
    print(estimate.render(estimate.estimate(load()), model, price_in, price_out))
    return 0


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
    paid.add_argument("--only", choices=["all", "alerts", "probes"], default="all")
    paid.add_argument("--ids", default="", help="comma-separated EV-A…/EV-P… ids")
    paid.add_argument("--limit", type=int, default=None, help="max items per kind")
    paid.add_argument("--max-usd", type=float, default=1.50, help="run-wide spend cap")
    paid.add_argument("--export-traces", action="store_true")
    paid.add_argument("--resume", default="", help="journal stem of an interrupted run")
    sub.add_parser("estimate", help="FREE offline cost estimate of a full paid run")
    sub.add_parser("stats", help="dataset composition")
    sub.add_parser("review", help="write the label review sheet")
    sub.add_parser("recordings", help="regenerate recordings/dry from the labels")
    args = parser.parse_args(argv)
    handlers = {
        "dry": cmd_dry,
        "paid": cmd_paid,
        "estimate": cmd_estimate,
        "stats": cmd_stats,
        "review": cmd_review,
        "recordings": cmd_recordings,
    }
    try:
        return handlers[args.cmd](args)
    except DatasetError as exc:
        print(f"dataset error: {exc}", file=sys.stderr)
        return 2
