"""`python -m soc_evals estimate` — a FREE, offline cost estimate of a full paid run (FR-11-07).

Tokens ≈ characters / 4. The call shapes below are assumptions from the flow design (feature 05);
the pilot run replaces them with measured numbers. gpt-5-nano bills reasoning tokens as output.
"""

import json
from dataclasses import dataclass

from soc_shared.models import AskAnswer, ScopeVerdict, TriageNote

from soc_evals.datasets import EvalData

CHARS_PER_TOKEN = 4
BASE_PROMPT_TOKENS = 900  # instructions + tool schemas per call (agents_build.py: ~8 KB / 3 agents)
PESSIMISTIC_FACTOR = 3.0  # reasoning tokens can be several times the visible output


def _tok(n_chars: int) -> int:
    return max(1, n_chars // CHARS_PER_TOKEN)


@dataclass(frozen=True)
class ItemEstimate:
    name: str
    n: int
    input_tokens: int  # per item
    output_tokens: int  # per item

    def cost(self, price_in: float, price_out: float, out_factor: float = 1.0) -> float:
        per = (self.input_tokens * price_in + self.output_tokens * out_factor * price_out) / 1e6
        return per * self.n


def estimate(data: EvalData) -> list[ItemEstimate]:
    note_schema = _tok(len(json.dumps(TriageNote.model_json_schema())))
    ans_schema = _tok(len(json.dumps(AskAnswer.model_json_schema())))
    scope_schema = _tok(len(json.dumps(ScopeVerdict.model_json_schema())))
    alert_tok = (
        sum(_tok(len(a.model_dump_json())) for a in data.alerts.values()) // len(data.alerts)
        if data.alerts
        else 0
    )
    q_tok = (
        sum(_tok(len(p.question)) for p in data.probes.values()) // len(data.probes)
        if data.probes
        else 0
    )
    kb_result = 1200  # one handbook search result (5 chunks)

    # /triage: 5 coordinator turns (history grows), 2 handbook sub-agent turns, 1 reviewer call.
    triage_turn = BASE_PROMPT_TOKENS + note_schema + alert_tok
    t_in = sum(triage_turn + i * 900 for i in range(5)) + 2 * (BASE_PROMPT_TOKENS + kb_result)
    t_in += BASE_PROMPT_TOKENS + note_schema + 800
    t_out = 5 * 1500 + 2 * 1000 + 800

    # /ask allowed: scope classifier, router, 2 specialist turns, reviewer.
    a_in = (
        (BASE_PROMPT_TOKENS + scope_schema + q_tok)
        + (BASE_PROMPT_TOKENS + q_tok)
        + 2 * (BASE_PROMPT_TOKENS + ans_schema + kb_result)
        + (BASE_PROMPT_TOKENS + ans_schema + 300)
    )
    a_out = 500 + 300 + 2 * 1200 + 600

    # /ask declined: the scope classifier only (blocking rules may decline with zero calls).
    d_in = BASE_PROMPT_TOKENS + scope_schema + q_tok
    d_out = 500

    allowed = sum(1 for p in data.probes.values() if p.expected_label != "DECLINE")
    declined = len(data.probes) - allowed
    return [
        ItemEstimate("alerts (/triage)", len(data.alerts), t_in, t_out),
        ItemEstimate("probes allowed (/ask)", allowed, a_in, a_out),
        ItemEstimate("probes declined (/ask)", declined, d_in, d_out),
    ]


def render(items: list[ItemEstimate], model: str, price_in: float, price_out: float) -> str:
    lines = [
        f"Cost estimate — full paid run, model {model} (${price_in}/1M in, ${price_out}/1M out)",
        f"{'item':<26}{'n':>4}{'tok in/item':>13}{'tok out/item':>14}"
        f"{'expected $':>12}{'pessim. $':>11}",
    ]
    exp = pes = 0.0
    for it in items:
        e = it.cost(price_in, price_out)
        p = it.cost(price_in, price_out, PESSIMISTIC_FACTOR)
        exp, pes = exp + e, pes + p
        lines.append(
            f"{it.name:<26}{it.n:>4}{it.input_tokens:>13,}{it.output_tokens:>14,}{e:>12.4f}{p:>11.4f}"
        )
    lines += [
        f"{'TOTAL':<57}{exp:>12.4f}{pes:>11.4f}",
        "Handbook embeddings (handbook side): < $0.001. "
        "Guards: run cap --max-usd, $0.05/item, $9 ledger.",
        "Assumption-based (chars/4, fixed call shapes). Run `make eval-pilot` (PAID) to measure.",
    ]
    return "\n".join(lines)
