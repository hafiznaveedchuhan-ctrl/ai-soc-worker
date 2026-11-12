"""Triage metrics (FR-02-12)."""

from dataclasses import dataclass, field

from soc_shared.masking import MaskMap, find_leaks, find_unmasked_pii, mask_alert
from soc_shared.models import Verdict, WazuhAlert

from soc_evals.datasets import AlertLabel
from soc_evals.predictions import AlertPrediction
from soc_evals.rate import Rate
from soc_evals.scoring.common import Failure

VERDICTS = [v.value for v in Verdict]


@dataclass
class TriageScores:
    n: int
    confusion: dict[str, dict[str, int]]
    tp_recall: Rate
    tp_precision: Rate
    verdict_accuracy: Rate
    escalation_agreement: Rate
    condition_agreement: Rate
    page_hit: Rate
    mitre_clean: Rate
    cite_ok: Rate
    leak_free: Rate
    errors: int
    failures: list[Failure] = field(default_factory=list)


def alert_mask_map(alert: WazuhAlert) -> MaskMap:
    """The alert's raw IP/user/host/email values, found by masking it once."""
    m = MaskMap()
    mask_alert(alert, m)
    return m


def score_triage(
    labels: dict[str, AlertLabel],
    alerts: dict[str, WazuhAlert],
    preds: dict[str, AlertPrediction],
    ksor_mitre_ids: set[str],
) -> TriageScores:
    confusion = {lv: dict.fromkeys([*VERDICTS, "error"], 0) for lv in VERDICTS}
    failures: list[Failure] = []
    tp_hits = pred_tp = verdict_ok = esc_ok = cond_k = cond_n = 0
    page_k = mitre_k = cite_k = leak_k = errors = 0

    for aid, label in sorted(labels.items()):
        pred = preds.get(aid)
        note = pred.note if pred else None
        if note is None:
            errors += 1
            reason = "missing prediction" if pred is None else (pred.error or "no note")
            confusion[label.verdict.value]["error"] += 1
            failures.append(Failure(aid, "prediction", reason))
            if label.verdict is Verdict.TP:
                failures.append(Failure(aid, "tp_recall", "TP missed (no note)"))
            continue

        v = note.verdict_suggestion
        confusion[label.verdict.value][v.value] += 1
        if v is Verdict.TP:
            pred_tp += 1
        if v is label.verdict:
            verdict_ok += 1
            if v is Verdict.TP:
                tp_hits += 1
        else:
            failures.append(Failure(aid, "verdict", f"expected {label.verdict}, got {v}"))
        if note.escalate == label.escalate:
            esc_ok += 1
        else:
            failures.append(
                Failure(
                    aid, "escalation", f"expected escalate={label.escalate}, got {note.escalate}"
                )
            )
        if note.escalate and label.escalate:
            cond_n += 1
            if note.escalate_condition in {label.escalate_condition, *label.also_conditions}:
                cond_k += 1
            else:
                failures.append(
                    Failure(
                        aid,
                        "condition",
                        f"expected #{label.escalate_condition}, got #{note.escalate_condition}",
                    )
                )
        if set(note.citations) & set(label.expected_stable_ids):
            page_k += 1
        else:
            failures.append(Failure(aid, "page_hit", "no expected handbook page cited"))
        allowed = ksor_mitre_ids | set(alerts[aid].rule.mitre.id)
        invented = sorted(set(note.mitre_ids) - allowed)
        if invented:
            failures.append(Failure(aid, "mitre", f"not in alert or handbook: {invented}"))
        else:
            mitre_k += 1
        cite_k += 1  # a parsed TriageNote already passed the cite-or-abstain validators
        text = pred.output_text if pred else ""
        leaked = bool(find_unmasked_pii(text)) or bool(
            find_leaks(text, alert_mask_map(alerts[aid]))
        )
        if leaked:
            failures.append(Failure(aid, "leak", "raw IP/user/host/email in output"))
        else:
            leak_k += 1

    n = len(labels)
    n_tp = sum(1 for lab in labels.values() if lab.verdict is Verdict.TP)
    return TriageScores(
        n=n,
        confusion=confusion,
        tp_recall=Rate(tp_hits, n_tp),
        tp_precision=Rate(tp_hits, pred_tp),
        verdict_accuracy=Rate(verdict_ok, n),
        escalation_agreement=Rate(esc_ok, n),
        condition_agreement=Rate(cond_k, cond_n),
        page_hit=Rate(page_k, n),
        mitre_clean=Rate(mitre_k, n),
        cite_ok=Rate(cite_k, n),
        leak_free=Rate(leak_k, n),
        errors=errors,
        failures=failures,
    )
