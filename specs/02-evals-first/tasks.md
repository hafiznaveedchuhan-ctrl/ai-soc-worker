# tasks — 02 evals-first
Status: **draft — awaiting approval** · Plan: `./plan.md` · Branch: `feat/02-evals-first`
Legend: [ ] todo · [x] done · **STOP** = wait for Naveed · ⬆ = commit + push checkpoint (standing rule; guard: no merged PR for this branch)

| ✓ | ID | Task | Satisfies | Done when | Depends |
|---|---|---|---|---|---|
| [x] | T02-00 | Write INTENT, spec, plan, tasks, VERIFY draft, ADR-0009 (Proposed) | Art. VII | files exist | — |
| | **STOP** | **Naveed approves the docs and answers Q1 (OTRF "haan"?), Q2 (ruleset lookup OK?), Q3 (≥ 20 TP), Q4 (MITRE both)** | | "approved" | T02-00 |
| [ ] | T02-01 | Workspace member `evals` (soc-evals package, deps on soc-shared); Makefile targets; CI picks it up | FR-02-20…24, NFR-02-02 | `uv sync`; `import soc_evals` | STOP |
| [ ] | T02-02 | `Rate` + prediction schemas + JSONL io (tests first) | FR-02-10, 11 | tests green | T02-01 |
| [ ] | T02-03 | Triage scorer (confusion, recall/precision, escalation, pages, invented MITRE, cite check, leaks) — tests first | FR-02-12 | tests green | T02-02 |
| | ⬆ | **checkpoint 1** (`feat(02): evals package, Rate, predictions, triage scorer`) | | pushed | |
| [ ] | T02-04 | Scope scorer + cost/latency + targets PASS/FAIL — tests first | FR-02-13…15 | tests green | T02-03 |
| [ ] | T02-05 | KSOR reference snapshots (read-only script over ../handbook file names) | FR-02-06 | files + test | T02-01 |
| [ ] | T02-06 | Scope probes CSV (95 rows) + loader + count/label tests | FR-02-05 | 95/95 valid | T02-05 |
| | ⬆ | **checkpoint 2** | | pushed | |
| [ ] | T02-07 | (if Q2 OK) read Wazuh ruleset v4.14.10 for the missing rule IDs; record file:line | FR-02-04 | source table in plan.md | STOP |
| [ ] | T02-08 | Alerts batch 1: 22 playbook alerts (SYNTHETIC) + label rows with rationale/sources | FR-02-01…04 | loader + fact tests green | T02-05, 07 |
| [ ] | T02-09 | Alerts batch 2: 10 benign/FP alerts (false-positive pages) | FR-02-02…04 | green | T02-08 |
| [ ] | T02-10 | Alerts batch 3: 8 OTRF-mapped (if Q1 "haan", download → map script) else 8 SYNTHETIC; composition test | FR-02-01…04, 07 | 40/40 valid, minimums met | T02-09 |
| | ⬆ | **checkpoint 3** | | pushed | |
| [ ] | T02-11 | Recordings: oracle.jsonl (from labels) + faulty.jsonl (planted mistakes) | FR-02-22 | oracle → all PASS; faulty → exactly the planted fails | T02-04, 10 |
| [ ] | T02-12 | Report template + renderer + `make eval-dry` + `make eval` refusal + `make eval-stats` | FR-02-16, 20, 21, 23 | dry report written; golden test | T02-11 |
| [ ] | T02-13 | Review sheet `make eval-review` → `review/labels-review.md` | FR-02-24 | file generated | T02-10 |
| [ ] | T02-14 | CI: soc-evals in mypy/pytest + `make eval-dry` step; ADR-0009 final; LEARNING §8; CAREER-MAP row 02 | NFR-02-02 | CI green | T02-12 |
| [ ] | T02-15 | Full gate; VERIFY.md §4 with real output; progress.md; PHR | all | gates green | T02-14 |
| | ⬆ | **checkpoint 4** → open PR `feat/02-evals-first → main` (ready for review) | | PR link | |
| | **STOP** | **Naveed verifies labels (review sheet) + runs VERIFY.md → merges** | | merged | |
