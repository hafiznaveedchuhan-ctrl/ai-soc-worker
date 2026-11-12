"""Label review sheet for Naveed (FR-02-24). Values are shown MASKED, as the AI will see them."""

import json
from pathlib import Path

from soc_shared.masking import MaskMap, mask_alert, mask_text

from soc_evals.datasets import EvalData

OUT = Path(__file__).resolve().parents[2] / "review/labels-review.md"


def render(data: EvalData) -> str:
    out = [
        "# Labels review sheet (generated — do not edit by hand)",
        "",
        "How to verify: read each block. If you agree, put your id in `verified_by` and the",
        "date in `verified_at` (labels.csv) or `verified_by` (probes.csv) — or tell Claude",
        "the ids you approve.",
        "",
        "## Alerts",
    ]
    for aid, label in sorted(data.labels.items()):
        m = MaskMap()
        masked = mask_alert(data.alerts[aid], m)
        ctx = mask_text(data.contexts.get(aid, ""), m)
        esc = (
            f"yes — condition #{label.escalate_condition}"
            + (
                f" (also {', '.join(map(str, label.also_conditions))})"
                if label.also_conditions
                else ""
            )
            if label.escalate
            else "no"
        )
        out += [
            "",
            f"### [ ] {aid} — {label.playbook} — rule {masked.rule_id} (level {masked.rule_level})",
            f"- **What happened (masked):** {masked.payload.get('full_log', '')}",
            f"- **Analyst context (masked):** {ctx or '—'}",
            f"- **Label:** verdict **{label.verdict.value}** · "
            f"severity **{label.severity.value}** · escalate **{esc}** · "
            f"MITRE {', '.join(label.mitre_ids) or '—'}",
            f"- **Why:** {label.rationale}",
            f"- **Handbook pages:** {', '.join(label.expected_stable_ids)} · "
            f"rule source: {label.rule_source}",
            f"- verified: {label.verified_by or 'NO'}",
        ]
        _ = json.dumps(masked.payload)  # masked payload is what an agent receives
    out += [
        "",
        "## Probes",
        "",
        "| ✓ | id | set | category | question | expected page | origin |",
        "|---|---|---|---|---|---|---|",
    ]
    for pid, p in sorted(data.probes.items()):
        q = p.question.replace("|", "\\|")
        out.append(
            f"| {'x' if p.verified else ' '} | {pid} | {p.set} | {p.category} | {q} | "
            f"{p.expected_stable_id or '—'} | {p.origin} |"
        )
    return "\n".join(out) + "\n"


def write(data: EvalData, path: Path = OUT) -> Path:
    path.write_text(render(data), encoding="utf-8")
    return path
