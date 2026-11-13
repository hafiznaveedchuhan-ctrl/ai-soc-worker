"""FR-11-04…06 — run_all with a FAKE pipeline: selection, error isolation, the run-wide cap."""

import pytest
from soc_evals.datasets import Probe, load
from soc_evals.pipeline import Selection, run_all, subset
from soc_evals.predictions import AlertPrediction, ProbePrediction
from soc_shared.models import LlmUsage, WazuhAlert

pytestmark = pytest.mark.anyio
D = load()


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def usage(cost: float) -> list[LlmUsage]:
    return [
        LlmUsage(
            request_id="r1",
            agent="a",
            model="gpt-5-nano",
            input_tokens=10,
            output_tokens=5,
            cost_usd=cost,
        )
    ]


class Fake:
    def __init__(self, cost: float = 0.01, boom: str = "") -> None:
        self.cost, self.boom = cost, boom
        self.seen: list[tuple[str, str]] = []

    async def run_alert(self, alert_id: str, alert: WazuhAlert, context: str) -> AlertPrediction:
        self.seen.append((alert_id, context))
        if alert_id == self.boom:
            raise RuntimeError("model exploded")
        return AlertPrediction(alert_id=alert_id, usage=usage(self.cost))

    async def run_probe(self, probe: Probe) -> ProbePrediction:
        self.seen.append((probe.probe_id, ""))
        return ProbePrediction(
            probe_id=probe.probe_id, scope_label="DECLINE", usage=usage(self.cost)
        )


async def test_full_selection_runs_every_item_in_order() -> None:
    f = Fake(cost=0.0)
    out = await run_all(D, f, Selection(), max_usd=1.5)
    assert out.ran == out.planned == len(D.alerts) + len(D.probes) == 135
    assert [i for i, _ in f.seen][:2] == ["EV-A001", "EV-A002"] and not out.stopped_at_cap
    assert all(p.latency_ms > 0 for p in out.alerts)


async def test_context_csv_is_passed_to_the_alert() -> None:
    f = Fake()
    await run_all(D, f, Selection(ids=frozenset({"EV-A003"})), max_usd=1.5)
    assert f.seen == [("EV-A003", D.contexts["EV-A003"])]


async def test_only_ids_and_limit() -> None:
    out = await run_all(D, Fake(), Selection(only="probes", limit=3), max_usd=1.5)
    assert out.alerts == [] and [p.probe_id for p in out.probes] == [
        "EV-P001",
        "EV-P002",
        "EV-P003",
    ]
    out = await run_all(D, Fake(), Selection(ids=frozenset({"EV-A002", "EV-P010"})), max_usd=1.5)
    assert (len(out.alerts), len(out.probes)) == (1, 1)


async def test_one_exception_becomes_an_item_error_and_the_run_continues() -> None:
    out = await run_all(D, Fake(boom="EV-A002"), Selection(only="alerts", limit=3), max_usd=1.5)
    assert [a.error is None for a in out.alerts] == [True, False, True]
    assert "model exploded" in (out.alerts[1].error or "")


async def test_run_wide_cap_stops_and_keeps_partial_results() -> None:
    msgs: list[str] = []
    out = await run_all(D, Fake(cost=0.30), Selection(), max_usd=1.0, progress=msgs.append)
    assert out.stopped_at_cap and out.ran == 4 and out.planned == 135  # 4 x $0.30 ≥ $1.00
    assert out.spent_usd == pytest.approx(1.2)
    assert any(m.startswith("STOP: run-wide cap") for m in msgs)


async def test_subset_scores_only_what_ran() -> None:
    out = await run_all(D, Fake(), Selection(ids=frozenset({"EV-A003", "EV-P001"})), max_usd=1.5)
    s = subset(D, out)
    assert set(s.alerts) == set(s.labels) == {"EV-A003"} and set(s.probes) == {"EV-P001"}
    assert s.contexts == {"EV-A003": D.contexts["EV-A003"]} and s.ksor_mitre_ids == D.ksor_mitre_ids


class LedgerFake(Fake):
    """Reports $0 per item, but the ledger grows $0.30 per item (usage lost on an exception)."""

    def __init__(self) -> None:
        super().__init__(cost=0.0)
        self.total = 5.0  # earlier runs already spent something

    def ledger_total(self) -> float:
        return self.total

    async def run_alert(self, alert_id: str, alert: WazuhAlert, context: str) -> AlertPrediction:
        self.total += 0.30
        return await super().run_alert(alert_id, alert, context)


async def test_cap_uses_the_ledger_when_predictions_undercount() -> None:
    out = await run_all(D, LedgerFake(), Selection(only="alerts"), max_usd=1.0)
    assert out.stopped_at_cap and len(out.alerts) == 4  # stopped by the ledger, not by $0 usage
    assert out.reported_usd == 0.0 and out.ledger_usd == pytest.approx(1.2)
    assert out.spent_usd == pytest.approx(1.2)


# ------------------------------------------------------------------ resumable runs (R5 was lost)
async def test_sink_gets_every_item_the_moment_it_exists() -> None:
    seen: list[str] = []
    await run_all(
        D,
        Fake(),
        Selection(ids=frozenset({"EV-A001", "EV-P001"})),
        1.5,
        sink=lambda p: seen.append(getattr(p, "alert_id", "") or getattr(p, "probe_id", "")),
    )
    assert seen == ["EV-A001", "EV-P001"]


async def test_resume_skips_done_items_and_counts_their_cost() -> None:
    prev = AlertPrediction(alert_id="EV-A001", usage=usage(0.40))
    f = Fake(cost=0.30)
    out = await run_all(D, f, Selection(only="alerts", limit=5), max_usd=1.0, done=([prev], []))
    assert "EV-A001" not in [i for i, _ in f.seen]  # not paid for twice
    assert out.alerts[0] is prev  # kept in the outcome and the report
    # $0.40 already spent + 2 x $0.30 = $1.00 → cap reached after 2 new items
    assert out.stopped_at_cap and len(out.alerts) == 3
