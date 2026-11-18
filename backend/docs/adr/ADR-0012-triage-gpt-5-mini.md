# ADR-0012 — triage_coordinator upgraded to gpt-5-mini
- Status: **Accepted** (Naveed "all are approved and haan", 2026-11-18) · Feature 11 · Constitution VI.2

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

## Result (40 alerts each)

| Run | Setup | TP recall | TP precision | Verdict accuracy | Errors | $ |
|---|---|---|---|---|---|---|
| R5 | all nano | 3/21 | 3/3 | 8/40 | 12 | 0.25 |
| R6b | triage mini | 3/21 | 3/3 | 14/40 | 7 | 0.67 |
| **R6c** | + verdict rule (T11-35) + reviewer fix (T11-36) | **8/21 = 38%** | 8/10 = 80% | **17/40** | 9 | 0.84 |

**Reading.**
- Most of the gain came from the PROMPT rule taken from the handbook, not from the model alone.
- The escalation condition agreed in 6/6 cases.
- TP recall is still far from the 95% target. The rest is mostly needs_info (8) and errors (5).
- Next: the Diagnostics of R6c, and the label review of the borderline alerts.
