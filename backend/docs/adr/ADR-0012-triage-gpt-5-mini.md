# ADR-0012 — triage_coordinator upgraded to gpt-5-mini
- Status: **Proposed** (waiting for Naveed) · Feature 11 · Constitution VI.2

## Context
R5 (gpt-5-nano) results:
- TP recall 3/21 and verdict accuracy 8/40.
- The model chose "needs_info" for 19 of 32 TP/benign_TP notes.
- ADR-0011 (the scope classifier on mini) fixed the scope target in P3, which shows that the smallest model is the bottleneck for judgement-heavy agents.

## Decision
- `AgentSettings.model_triage` defaults to `gpt-5-mini`.
- All other agents keep their models.
- Re-run the 40 alerts with a cap of $2.00.

## Consequences
- **Cost:** about $0.023 per alert for the coordinator (measured tokens × mini price), about $1.1 per 40-alert run. This may be real money if it is not on the incentivized tier.
- **Success:** TP recall clearly up, TP precision not down, leaks 0. Otherwise revisit the prompt and the rules before further upgrades.
