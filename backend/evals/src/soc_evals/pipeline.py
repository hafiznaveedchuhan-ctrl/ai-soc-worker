"""Run eval items through a pipeline (FR-11-04…06). Pure code: no agent imports, so it is tested
with a fake pipeline; `soc_evals.live.AgentPipeline` is the real one."""

import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Literal, Protocol

from soc_shared.models import WazuhAlert

from soc_evals.datasets import EvalData, Probe
from soc_evals.predictions import AlertPrediction, ProbePrediction

Only = Literal["all", "alerts", "probes"]


class Pipeline(Protocol):
    async def run_alert(
        self, alert_id: str, alert: WazuhAlert, context: str
    ) -> AlertPrediction: ...

    async def run_probe(self, probe: Probe) -> ProbePrediction: ...


@dataclass(frozen=True)
class Selection:
    only: Only = "all"
    ids: frozenset[str] = frozenset()
    limit: int | None = None  # per kind (alerts / probes)

    def pick(self, ids: Iterable[str], kind: Literal["alerts", "probes"]) -> list[str]:
        if self.only not in ("all", kind):
            return []
        out = [i for i in sorted(ids) if not self.ids or i in self.ids]
        return out[: self.limit] if self.limit is not None else out


@dataclass
class RunOutcome:
    alerts: list[AlertPrediction] = field(default_factory=list)
    probes: list[ProbePrediction] = field(default_factory=list)
    planned: int = 0
    stopped_at_cap: bool = False
    spent_usd: float = 0.0  # max(sum of reported usage, ledger delta) — see _spent
    reported_usd: float = 0.0  # sum of the usage inside the predictions
    ledger_usd: float | None = None  # ledger delta for this run, when the pipeline has a ledger

    @property
    def ran(self) -> int:
        return len(self.alerts) + len(self.probes)


def _cost(p: AlertPrediction | ProbePrediction) -> float:
    return sum(u.cost_usd for u in p.usage)


async def run_all(
    data: EvalData,
    pipeline: Pipeline,
    selection: Selection,
    max_usd: float,
    progress: Callable[[str], None] = lambda _: None,
    *,
    done: tuple[list[AlertPrediction], list[ProbePrediction]] | None = None,
    sink: Callable[[AlertPrediction | ProbePrediction], None] | None = None,
) -> RunOutcome:
    """Run the selected items one by one. Stops (keeping what it has) once spend reaches max_usd.

    `done` = predictions of an interrupted run (--resume): those items are not run again, and
    their cost counts toward the cap. `sink` is called after EVERY item, so the caller can append
    it to disk at once — an interrupted run keeps everything it paid for (R5 lost $0.017 of work
    when the session ended, 2026-11-12)."""
    prev_a, prev_p = done or ([], [])
    have_a = {x.alert_id for x in prev_a}
    have_p = {x.probe_id for x in prev_p}
    alert_ids = selection.pick(data.alerts, "alerts")
    probe_ids = selection.pick(data.probes, "probes")
    out = RunOutcome(
        alerts=[x for x in prev_a if x.alert_id in alert_ids],
        probes=[x for x in prev_p if x.probe_id in probe_ids],
        planned=len(alert_ids) + len(probe_ids),
    )
    prior = sum(_cost(x) for x in out.alerts) + sum(_cost(x) for x in out.probes)
    out.reported_usd = out.spent_usd = prior
    if out.ran:
        progress(f"resume: {out.ran} items already done (${prior:.4f}), skipping them")
    alert_ids = [i for i in alert_ids if i not in have_a]
    probe_ids = [i for i in probe_ids if i not in have_p]
    ledger = getattr(pipeline, "ledger_total", None)  # optional: AgentPipeline has one
    start = ledger() if ledger else None

    def account(pred: AlertPrediction | ProbePrediction) -> None:
        # The ledger is written per model call by the hooks, so it also counts calls whose
        # prediction lost its usage (pilot 2026-11-12, F1). The cap uses the larger number.
        out.reported_usd += _cost(pred)
        if ledger and start is not None:
            out.ledger_usd = prior + max(0.0, (ledger() or 0.0) - start)
        out.spent_usd = max(out.reported_usd, out.ledger_usd or 0.0)
        if sink is not None:
            sink(pred)

    def over_cap() -> bool:
        if out.spent_usd >= max_usd:
            out.stopped_at_cap = True
            progress(f"STOP: run-wide cap ${max_usd:.2f} reached (spent ${out.spent_usd:.4f})")
        return out.stopped_at_cap

    for aid in alert_ids:
        if over_cap():
            return out
        t0 = time.perf_counter()
        try:
            a = await pipeline.run_alert(aid, data.alerts[aid], data.contexts.get(aid, ""))
        except Exception as exc:
            a = AlertPrediction(alert_id=aid, error=f"exception: {type(exc).__name__}: {exc}"[:300])
        if not a.latency_ms:
            a = a.model_copy(update={"latency_ms": (time.perf_counter() - t0) * 1000})
        out.alerts.append(a)
        account(a)
        progress(f"{aid}: {'ok' if a.error is None else a.error[:60]}  ${out.spent_usd:.4f}")

    for pid in probe_ids:
        if over_cap():
            return out
        t0 = time.perf_counter()
        try:
            p = await pipeline.run_probe(data.probes[pid])
        except Exception as exc:
            p = ProbePrediction(probe_id=pid, error=f"exception: {type(exc).__name__}: {exc}"[:300])
        if not p.latency_ms:
            p = p.model_copy(update={"latency_ms": (time.perf_counter() - t0) * 1000})
        out.probes.append(p)
        account(p)
        progress(f"{pid}: {p.scope_label or p.error}  ${out.spent_usd:.4f}")
    return out


def subset(data: EvalData, outcome: RunOutcome) -> EvalData:
    """The data restricted to the items that ran, so a partial run is scored on what it ran."""
    a = {x.alert_id for x in outcome.alerts}
    p = {x.probe_id for x in outcome.probes}
    return EvalData(
        alerts={k: v for k, v in data.alerts.items() if k in a},
        contexts={k: v for k, v in data.contexts.items() if k in a},
        labels={k: v for k, v in data.labels.items() if k in a},
        probes={k: v for k, v in data.probes.items() if k in p},
        ksor_mitre_ids=data.ksor_mitre_ids,
        ksor_stable_ids=data.ksor_stable_ids,
    )
