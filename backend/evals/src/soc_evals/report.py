"""Markdown report renderer (FR-02-16). Deterministic except the date and commit."""

from dataclasses import dataclass
from pathlib import Path
from string import Template

from soc_evals.datasets import EvalData
from soc_evals.rate import Rate
from soc_evals.scoring.common import Failure
from soc_evals.scoring.cost import CostLatency
from soc_evals.scoring.scope import ScopeScores
from soc_evals.scoring.triage import VERDICTS, TriageScores
from soc_evals.targets import TargetResult

TEMPLATE = Path(__file__).resolve().parents[2] / "reports/template.md"
NOTES = [
    "MITRE renumbering: handbook page T1685.005 vs Wazuh rule 60117 T1070.004 — "
    "both accepted (Q4).",
    "Escalation labels name a primary condition plus any other true conditions (also_conditions).",
    "EV-A002: condition 2 applied to Linux root (policy lists Windows accounts) — "
    "Naveed to confirm.",
    "EV-A023: listed backup account treated as benign despite condition 2 naming service accounts.",
    "1102 alerts use data.win.logFileCleared.* — re-check against a live lab alert (Phase 1 B/C).",
    "Detection gap: default Wazuh v4.14.10 raises no alert for the OTRF CMSTP, bitsadmin and "
    "0x1FFFFF LSASS-dump datasets (ADR-0009) — they are not in this eval.",
    "EV-A035/EV-A040: credential theft gets Low severity, because the policy has no condition "
    "for it — Naveed to confirm.",
]


@dataclass(frozen=True)
class RunInfo:
    mode: str
    date: str
    git_sha: str
    source: str
    models: str = "none (recorded predictions)"
    note: str = "full run"


def _table(header: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(lines)


def render(
    info: RunInfo,
    data: EvalData,
    triage: TriageScores,
    scope: ScopeScores,
    targets: list[TargetResult],
    cost_alerts: CostLatency,
    cost_probes: CostLatency,
) -> str:
    verified = (
        f"alerts {Rate(sum(lab.verified for lab in data.labels.values()), len(data.labels))} · "
        f"probes {Rate(sum(p.verified for p in data.probes.values()), len(data.probes))}"
    )
    failures: list[Failure] = triage.failures + scope.failures
    t = triage
    values = {
        "mode": info.mode,
        "date": info.date,
        "git_sha": info.git_sha,
        "source": info.source,
        "models": info.models,
        "note": info.note,
        "dataset_sizes": f"{len(data.alerts)} alerts · {len(data.probes)} probes",
        "verified": verified,
        "targets_table": _table(
            ["Target", "Result", "Rule", "Status"],
            [
                [
                    r.name,
                    str(r.rate),
                    f"{r.op} {r.threshold_pct:g}%",
                    "PASS" if r.passed else "FAIL",
                ]
                for r in targets
            ],
        ),
        "triage_table": _table(
            ["Metric", "Result"],
            [
                ["TP recall", str(t.tp_recall)],
                ["TP precision", str(t.tp_precision)],
                ["Verdict accuracy", str(t.verdict_accuracy)],
                ["Escalation agreement", str(t.escalation_agreement)],
                ["Escalation condition agreement (both escalate)", str(t.condition_agreement)],
                ["Expected handbook page cited", str(t.page_hit)],
                ["Notes without invented MITRE IDs", str(t.mitre_clean)],
                ["Notes passing cite-or-abstain", str(t.cite_ok)],
                ["Outputs without leaks", str(t.leak_free)],
                ["Errors / missing", str(t.errors)],
            ],
        ),
        "confusion_table": _table(
            ["label \\ prediction", *VERDICTS, "error"],
            [[lv, *[str(t.confusion[lv][c]) for c in [*VERDICTS, "error"]]] for lv in VERDICTS],
        ),
        "scope_table": _table(
            ["Metric", "Result"],
            [
                *[[f"Label accuracy — {k}", str(v)] for k, v in scope.label_accuracy.items()],
                *[[f"Decline rate — {k}", str(v)] for k, v in scope.decline_rate.items()],
                ["False declines — all ALLOW sets", str(scope.false_decline)],
                *[[f"False declines — {k}", str(v)] for k, v in scope.false_decline_by_set.items()],
                ["Exact decline text", str(scope.exact_decline_text)],
                ["Allowed answers valid (cite / web / not in record)", str(scope.answered_ok)],
                ["ALLOW_KSOR expected page cited", str(scope.ksor_page_hit)],
                ["Outputs without leaks", str(scope.leak_free)],
            ],
        ),
        "cost_table": _table(
            ["Set", "n", "Total $", "Mean $", "Mean tokens in/out", "p50 ms", "p95 ms"],
            [
                [
                    name,
                    str(c.n),
                    f"{c.total_cost_usd:.4f}",
                    f"{c.mean_cost_usd:.5f}",
                    f"{c.mean_input_tokens:.0f} / {c.mean_output_tokens:.0f}",
                    f"{c.p50_ms:.0f}",
                    f"{c.p95_ms:.0f}",
                ]
                for name, c in (("alerts", cost_alerts), ("probes", cost_probes))
            ],
        ),
        "failure_count": str(len(failures)),
        "failures_table": _table(
            ["Item", "Check", "Reason"], [[f.item_id, f.check, f.reason] for f in failures]
        )
        if failures
        else "None.",
        "notes": "\n".join(f"- {n}" for n in NOTES),
    }
    return Template(TEMPLATE.read_text(encoding="utf-8")).substitute(values)
