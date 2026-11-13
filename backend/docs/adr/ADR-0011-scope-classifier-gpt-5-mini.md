# ADR-0011 — scope_classifier upgraded to gpt-5-mini
- Status: **Accepted** (Naveed "approved" + "haan", 2026-11-13) · Feature 11 · Constitution VI.2 (one agent, after the evals fail)

## Context
The R5 baseline and the P1 re-run used gpt-5-nano for every agent (ADR-0003). On the DECLINE set the scope result was 21/30 = 70%; the target is ≥ 90%.
- All 9 misses were the classifier allowing pricing, vendor-choice, offensive, vendor-config and legal questions.
- The code-level blocking rules work: EV-P001 was declined with 0 calls.

## Decision
- `AgentSettings.model_scope` defaults to `gpt-5-mini`, using the existing per-agent routing. It can still be overridden with `AGENT_MODEL_SCOPE`.
- All other agents stay on gpt-5-nano.
- Re-run the 95 probes with a cap of $0.60.

## Consequences
- **Cost:** about 5x per classifier call. That is about $0.002 per question, and maybe real money if gpt-5-mini is not on the incentivized tier.
- **Success test:** DECLINE ≥ 90% and false declines ≤ 10%. If it fails, revisit the classifier prompt (ADR-0002) before any further upgrade.
