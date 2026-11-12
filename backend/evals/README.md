# soc-evals

Labelled eval datasets, scorer and reports for the soc-worker agents (feature 02, evals-first).
Backend part: **quality gate** (not a service, no image). Spec: `../../specs/02-evals-first/`.

```bash
make eval-dry          # free, offline: validate datasets + score recorded predictions → reports/<date>-dry-report.md
make eval-stats        # dataset composition and how many labels Naveed verified
make eval-review       # review/labels-review.md — the sheet Naveed uses to verify labels
make eval-recordings   # rebuild alerts, labels, probes and the dry recordings from scripts/
make eval-estimate     # free, offline: expected + pessimistic cost of a full paid run
make eval-pilot CONFIRM=haan   # PAID: 2 alerts + 4 probes through the real flows (cap $0.10)
make eval CONFIRM=haan         # PAID: all 135 items (cap MAX_USD, default $1.50) → reports/<date>-paid-report.md
```

Data: 40 alerts (34 SYNTHETIC lab, 6 OTRF-derived), 95 probes. All labels are **UNVERIFIED** until `verified_by` is filled.
Attribution: `data/THIRD_PARTY_NOTICES.md` (OTRF Security-Datasets, MIT; Wazuh ruleset v4.14.10 rule lines read).
No environment variables. Explained in `../docs/LEARNING.md` §8.

## Paid run (feature 11, ADR-0010)
- **Guards.** `soc_evals paid` needs `--yes-paid` AND `CONFIRM=haan`. It first checks that the handbook MCP answers `tools/list`. This check is free and does no embedding.
- **Flows.** Items run one by one through `agent_service.flows`:
  - alerts go through `run_triage`, with the context.csv text, and every ticket approval REJECTED;
  - probes go through `run_ask`, with a fresh session per probe.
- **Spend limits.** Three guards apply: the per-item budget of $0.05, the run-wide `--max-usd` cap (the run stops and keeps its partial results), and the $9 ledger.
- **Live dependencies.**
  - the live handbook;
  - the Wazuh fixtures;
  - AbuseIPDB and Tavily only when their keys exist. Otherwise they report "not configured" or "web search unavailable".
- **Outputs.** The predictions go to `recordings/paid/<date>-<sha>-{alerts,probes}.jsonl`; they hold masked text only. A partial run writes `reports/<date>-paid-pilot-report.md`.
- **Tests.** Everything is tested offline with `agents.testing.ScriptedModel` (`tests/test_live.py`).
