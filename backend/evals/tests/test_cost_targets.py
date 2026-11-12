"""FR-02-14, 15 — cost/latency and target PASS/FAIL."""

from soc_evals.rate import Rate
from soc_evals.scoring.cost import cost_latency, nearest_rank
from soc_evals.scoring.scope import score_scope
from soc_evals.scoring.triage import score_triage
from soc_evals.targets import TargetResult, evaluate
from soc_evals.testing import alert, apred, label, note, ppred, probe


def test_nearest_rank() -> None:
    vals = [float(v) for v in range(1, 21)]
    assert nearest_rank(vals, 95) == 19.0
    assert nearest_rank(vals, 50) == 10.0
    assert nearest_rank([], 95) == 0.0


def test_cost_latency() -> None:
    preds = [apred(f"EV-A00{i}", None, ms=float(i * 10)) for i in range(1, 5)]
    c = cost_latency(preds)
    assert c.n == 4 and round(c.total_cost_usd, 6) == 0.004
    assert c.mean_input_tokens == 100 and c.p95_ms == 40.0


def test_target_ops() -> None:
    assert TargetResult("x", Rate(19, 20), ">=", 95.0).passed
    assert not TargetResult("x", Rate(15, 16), ">=", 95.0).passed
    assert TargetResult("x", Rate(1, 10), "<=", 10.0).passed
    assert not TargetResult("x", Rate(0, 0), ">=", 95.0).passed


def test_evaluate_all_pass() -> None:
    t = score_triage(
        {"EV-A001": label("EV-A001")},
        {"EV-A001": alert("EV-A001")},
        {"EV-A001": apred("EV-A001", note("EV-A001"))},
        {"T1110"},
    )
    p = {
        "EV-P001": probe("EV-P001", "DECLINE", "DECLINE"),
        "EV-P002": probe("EV-P002", "ALLOW_CYBER_RESEARCH", "ALLOW_CYBER_RESEARCH"),
    }
    s = score_scope(
        p,
        {
            "EV-P001": ppred("EV-P001", "DECLINE"),
            "EV-P002": ppred("EV-P002", "ALLOW_CYBER_RESEARCH"),
        },
    )
    results = evaluate(t, s)
    assert len(results) == 7
    assert all(r.passed for r in results), [(r.name, str(r.rate)) for r in results]
