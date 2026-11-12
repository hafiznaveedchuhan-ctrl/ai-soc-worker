# ADR-0010 — Live eval: run-wide cap and live dependencies
- Status: **Accepted** (Naveed "approved", 2026-11-12, PHR-0015) · Feature 11

## Context
`soc_evals paid` sends 135 items through the real flows, and this costs money. Two things therefore have to be settled:
- how to bound the spend;
- which dependencies are real and which are fake.

## Decision
- **Guards.** A paid run needs both `--yes-paid` and `CONFIRM=haan`. Spend is bounded three ways:
  - a run-wide cap `--max-usd`, default $1.50 (the run stops and keeps its partial results);
  - the per-item run budget of $0.05;
  - the $9 ledger.
- **Dependencies.**
  - **KSOR** is the LIVE handbook, because the fake KSOR does not hold every expected page.
  - **Wazuh** uses the fixtures.
  - **AbuseIPDB** is real only with a key; otherwise it reports "not configured". The test mock is never used, because it returns score 88 for every IP and would bias verdicts.
  - **Tavily** is used only with a key.
- **Pilot first.** The full run comes only after a pilot (2 alerts + 4 probes). Each run needs its own "haan".
- **Privacy.** Trace export is off by default. The masked prediction JSONL files are committed.

## Consequences
- The research probes score "web search unavailable" until a Tavily key exists. They still count as valid answers.
- The scores depend on the handbook content at run time, so the report records the commit and the date.

## Update after the pilots (2026-11-12, R3)
- **Measured cost of the pilot:** $0.0068 per alert (144 s), $0.0006–0.0015 per allowed probe, and $0–0.0004 per declined probe.
- **Full run:** about $0.29 (pessimistic $0.60), so the $1.50 cap is kept.
- **The cap now uses `max(reported usage, ledger delta)`.** The ledger is written per call by the hooks, so it also catches spend that a failed item's prediction lost.
- **One corrective retry per alert (Naveed Q1).** It runs when the TriageNote breaks a model rule. Only the rule messages are fed back; the values never are.
