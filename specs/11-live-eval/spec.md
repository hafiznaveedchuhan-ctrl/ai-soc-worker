# spec — 11 live-eval · package `evals` (`soc_evals`)
Source: `00-plan.txt` §2 (approved). Q1: the run-wide cap is $1.50. Q2: the masked paid JSONL files are committed. Q3: AbuseIPDB is used for real only when a key is set.

| ID | Requirement |
|---|---|
| FR-11-01 | `paid` runs only with BOTH `--yes-paid` AND env `CONFIRM=haan`. Otherwise it prints "refused", makes zero calls and exits 1. |
| FR-11-02 | Each alert runs through `run_triage` with its context.csv text. Ticket approvals are always rejected. A fresh session is used per alert. |
| FR-11-03 | Each probe runs through `run_ask` with a fresh session per probe. |
| FR-11-04 | FlowResult → prediction mapping. **ok**: note or answer; output_text = r.text (masked). **declined**: scope_label DECLINE. **blocked / max_turns / budget / error**: error `"<status>: <text>"`; probes keep the fallback scope_label. Each prediction also gets usage and latency_ms. An exception on one item becomes an error on that item only. |
| FR-11-05 | Money guards: the $0.05 per-item budget, the run-wide `--max-usd` (default 1.50; the run stops and keeps its partial results), and the $9 ledger. |
| FR-11-06 | `--only alerts\|probes`, `--ids`, `--limit N`. A partial run is scored on the items it ran; the report says "partial". |
| FR-11-07 | `estimate` (free, offline): the expected and pessimistic cost of a full run. |
| FR-11-08 | Pre-flight: the handbook MCP must answer `list_tools`, else the run stops with a hint. |
| FR-11-09 | Outputs: `evals/recordings/paid/<date>-<sha>-{alerts,probes}.jsonl` and `evals/reports/<date>-paid-report.md`. |
| FR-11-10 | Trace export is OFF by default; `--export-traces` opts in. |
| FR-11-11 | Live dependencies: the live handbook KSOR, the Wazuh fixtures, AbuseIPDB only with a key, Tavily only with a key. |
