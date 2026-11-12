"""Cost accounting: a per-run budget + a global ledger (hard cap). Every LLM call is priced."""

import json
from dataclasses import dataclass, field
from pathlib import Path

from soc_shared.models import LlmUsage


class BudgetExceeded(RuntimeError):
    pass


def price(
    prices: dict[str, tuple[float, float]], model: str, tokens_in: int, tokens_out: int
) -> float:
    pin, pout = prices.get(
        model, max(prices.values())
    )  # unknown model → priced at the dearest known
    return (tokens_in * pin + tokens_out * pout) / 1_000_000


class Ledger:
    """Cumulative spend across runs, in a small JSON file (local; the DB copy is feature 08)."""

    def __init__(self, path: Path, cap_usd: float) -> None:
        self.path = path
        self.cap = cap_usd

    def total(self) -> float:
        if not self.path.exists():
            return 0.0
        return float(json.loads(self.path.read_text("utf-8")).get("total_usd", 0.0))

    def add(self, usd: float) -> float:
        new = self.total() + usd
        self.path.write_text(json.dumps({"total_usd": round(new, 6)}), "utf-8")
        return new

    def check_open(self) -> None:
        if self.total() >= self.cap:
            raise BudgetExceeded(f"global LLM budget reached (${self.total():.4f} ≥ ${self.cap})")


@dataclass
class RunBudget:
    limit_usd: float
    prices: dict[str, tuple[float, float]]
    request_id: str
    ledger: Ledger | None = None
    spent_usd: float = 0.0
    usage: list[LlmUsage] = field(default_factory=list)

    def record(self, agent: str, model: str, tokens_in: int, tokens_out: int) -> LlmUsage:
        cost = price(self.prices, model, tokens_in, tokens_out)
        entry = LlmUsage(
            request_id=self.request_id,
            agent=agent,
            model=model,
            input_tokens=tokens_in,
            output_tokens=tokens_out,
            cost_usd=cost,
        )
        self.usage.append(entry)
        self.spent_usd += cost
        if self.ledger is not None:
            self.ledger.add(cost)
        if self.spent_usd > self.limit_usd:
            raise BudgetExceeded(f"run budget exceeded (${self.spent_usd:.4f} > ${self.limit_usd})")
        return entry
