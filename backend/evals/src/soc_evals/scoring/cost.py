"""Cost and latency (FR-02-14). p95 uses the nearest-rank method."""

import math
from dataclasses import dataclass

from soc_evals.predictions import AlertPrediction, ProbePrediction


@dataclass(frozen=True)
class CostLatency:
    n: int
    total_cost_usd: float
    mean_cost_usd: float
    mean_input_tokens: float
    mean_output_tokens: float
    p50_ms: float
    p95_ms: float


def nearest_rank(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(1, math.ceil(pct / 100 * len(ordered)))
    return ordered[rank - 1]


def cost_latency(preds: list[AlertPrediction] | list[ProbePrediction]) -> CostLatency:
    n = len(preds)
    costs = [sum(u.cost_usd for u in p.usage) for p in preds]
    tin = [sum(u.input_tokens for u in p.usage) for p in preds]
    tout = [sum(u.output_tokens for u in p.usage) for p in preds]
    lat = [p.latency_ms for p in preds]
    return CostLatency(
        n=n,
        total_cost_usd=sum(costs),
        mean_cost_usd=sum(costs) / n if n else 0.0,
        mean_input_tokens=sum(tin) / n if n else 0.0,
        mean_output_tokens=sum(tout) / n if n else 0.0,
        p50_ms=nearest_rank(lat, 50),
        p95_ms=nearest_rank(lat, 95),
    )
