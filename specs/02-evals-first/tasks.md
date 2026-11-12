# tasks — 02 evals-first
Status: **approved** (human:naveed, 2026-11-12 "approced"; Q3+Q4 proposals accepted; Q1/Q2 need an explicit "haan") · Plan: `./plan.md` · Branch: `feat/02-evals-first`
Legend: [ ] todo · [x] done · **STOP** = wait for Naveed · ⬆ = commit + push checkpoint (standing rule; guard: no merged PR for this branch)

| ✓ | ID | Task | Satisfies | Done when | Depends |
|---|---|---|---|---|---|
| [x] | T02-00 | Write INTENT, spec, plan, tasks, VERIFY draft, ADR-0009 (Proposed) | Art. VII | files exist | — |
| | **STOP** | **Naveed approves the docs and answers Q1 (OTRF "haan"?), Q2 (ruleset lookup OK?), Q3 (≥ 20 TP), Q4 (MITRE both)** | | "approved" | T02-00 |
| [x] | T02-01 | Workspace member `evals` (soc-evals package, deps on soc-shared); Makefile targets; CI picks it up | FR-02-20…24, NFR-02-02 | `uv sync`; `import soc_evals` | STOP |
| [x] | T02-02 | `Rate` + prediction schemas + JSONL io (tests first) | FR-02-10, 11 | tests green | T02-01 |
| [x] | T02-03 | Triage scorer (confusion, recall/precision, escalation, pages, invented MITRE, cite check, leaks) — tests first | FR-02-12 | tests green | T02-02 |
| | ⬆ | **checkpoint 1** (`feat(02): evals package, Rate, predictions, triage scorer`) | | pushed | |
| [x] | T02-04 | Scope scorer + cost/latency + targets PASS/FAIL — tests first | FR-02-13…15 | tests green | T02-03 |
| [x] | T02-05 | KSOR reference snapshots (read-only script over ../handbook file names) | FR-02-06 | files + test | T02-01 |
| [x] | T02-06 | Scope probes CSV (95 rows) + loader + count/label tests | FR-02-05 | 95/95 valid | T02-05 |
| | ⬆ | **checkpoint 2** | | pushed | |
| [x] | T02-07 | (if Q2 OK) read Wazuh ruleset v4.14.10 for the missing rule IDs; record file:line | FR-02-04 | source table in plan.md | STOP |
| [x] | T02-08 | Alerts batch 1: 22 playbook alerts (SYNTHETIC) + label rows with rationale/sources | FR-02-01…04 | loader + fact tests green | T02-05, 07 |
| [x] | T02-09 | Alerts batch 2: 10 benign/FP alerts (false-positive pages) | FR-02-02…04 | green | T02-08 |
| [x] | T02-10 | Alerts batch 3: 8 OTRF-mapped (if Q1 "haan", download → map script) else 8 SYNTHETIC; composition test | FR-02-01…04, 07 | 40/40 valid, minimums met | T02-09 |
| | ⬆ | **checkpoint 3** | | pushed | |
| [x] | T02-11 | Recordings: oracle.jsonl (from labels) + faulty.jsonl (planted mistakes) | FR-02-22 | oracle → all PASS; faulty → exactly the planted fails | T02-04, 10 |
| [x] | T02-12 | Report template + renderer + `make eval-dry` + `make eval` refusal + `make eval-stats` | FR-02-16, 20, 21, 23 | dry report written; golden test | T02-11 |
| [x] | T02-13 | Review sheet `make eval-review` → `review/labels-review.md` | FR-02-24 | file generated | T02-10 |
| [x] | T02-14 | CI: soc-evals in mypy/pytest + `make eval-dry` step; ADR-0009 final; LEARNING §8; CAREER-MAP row 02 | NFR-02-02 | CI green | T02-12 |
| [x] | T02-15 | Full gate; VERIFY.md §4 with real output; progress.md; PHR | all | gates green | T02-14 |
| | ⬆ | **checkpoint 4** → open PR `feat/02-evals-first → main` (ready for review) | | PR link | |
| | **STOP** | **Naveed verifies labels (review sheet) + runs VERIFY.md → merges** | | merged | |

### As-built notes (2026-11-12)
- T02-08 partly done: **20** playbook alerts for 9 playbooks (brute-force ×5, success-after-failures ×3, the others ×2).
  Waiting for Q2: **port-scan ×2** and **suspicious-powershell ×2** (the handbook lists no Wazuh rule IDs for them).
- T02-10 waiting for Q1: **6** OTRF-mapped alerts (not 8). Total stays 40 = 20 + 4 + 10 + 6.
- Added: `data/context.csv` (analyst-provided context such as change tickets — an INPUT, masked like the alert) and
  label column `also_conditions` (other escalation conditions that are also true; the scorer accepts any of them).
- soc-shared fix: built-in GROUP names (Administrators, Domain Admins, …) stay unmasked (condition 6 needs them).
- 2026-11-12 "all haan": Q2 → ruleset read (4 alerts EV-A031…A034); Q1 → OTRF downloaded to the scratchpad only; 6 alerts EV-A035…A040
  from 2 datasets. 4 other datasets produce NO default Wazuh alert (detection gap, ADR-0009). Handbook has **10** playbooks (not 11).
