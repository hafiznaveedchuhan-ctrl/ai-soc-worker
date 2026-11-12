# ADR-0003 — Default model: gpt-5-nano for every agent
- Status: **Accepted** (human:naveed blanket approval 2026-11-12, PHR-0010/0012) · Feature 05
## Context
Hard LLM cap $10 total; constitution VI.2: the smallest current OpenAI model by default, upgrade one agent only after failing evals.
Pricing checked 2026-11-12 (developers.openai.com/api/docs/pricing, via Context7), USD per 1M tokens in/out:
gpt-5-nano 0.05/0.40 · gpt-4o-mini 0.15/0.60 · gpt-5.4-nano 0.20/1.25 · gpt-5-mini 0.25/2.00.
## Options
1. **gpt-5-nano everywhere (chosen)** — cheapest; ~20k in + 3k out per triage ≈ $0.0022. 2. gpt-4o-mini — 3× input cost, older.
3. gpt-5-mini for the coordinator — 5× cost; only if evals fail.
## Decision
`AGENT_MODEL_DEFAULT=gpt-5-nano`; per-agent overrides `AGENT_MODEL_<AGENT>` exist but stay empty. Prices live in `settings.DEFAULT_PRICES`;
an unknown model is priced at the dearest known price (so the budget guard errs on the safe side).
## Consequences
Small models are weaker at structured output and citation discipline → the output guardrail checks deterministically; the paid eval decides
if one agent must be upgraded (a new ADR). Re-check the price before the paid eval run.
