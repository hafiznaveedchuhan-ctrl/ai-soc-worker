# VERIFY — 02 evals-first
Status: **draft** (commands fixed now; real output added in T02-15) · Naveed's 10%

## 0. Setup
```bash
cd ~/ai-soc/soc-worker && git fetch && git checkout feat/02-evals-first && git pull
cd backend && make dev
```

## 1. Checks
| # | Command | You must see |
|---|---|---|
| 1.1 | `make check` | lint/types clean; all tests pass; coverage gates met |
| 1.2 | `make eval-stats` | 40 alerts (≥ 20 TP, 10 benign/FP, ≥ 4 needs-info, conditions 1–8 each ≥ 1); 95 probes (30 / 25 / 30 / 10); verified count |
| 1.3 | `make eval-dry` | `datasets: 135/135 valid = 100.0%`, report path printed, exit 0, no network |
| 1.4 | open `evals/reports/<date>-dry-report.md` | targets table, every rate as `k/n = p%`, confusion matrix, "labels verified: k/n" |
| 1.5 | `uv run python -m soc_evals paid` | refuses: needs `--yes-paid` and the pipeline from feature 05/06; exit 1 |
| 1.6 | `make eval-review` → open `evals/review/labels-review.md` | one block per alert with label, rationale, rule source, handbook pages |
| 1.7 | GitHub Actions on the PR | `python` job includes the eval-dry step, green |

## 2. Edge cases to try
- Delete one line from `recordings/dry/oracle.jsonl` → re-run eval-dry → that item is listed as a failure (missing prediction).
- Change a label's verdict in `labels.csv` from TP to FP → the oracle still matches its own labels, but `make eval-stats` counts change.
- Add a probe row with an unknown set name → the loader fails with the row number.

## 3. Break it on purpose
| Change | Expected failure |
|---|---|
| Put `T9999` into an alert's label `mitre_ids` | `test_facts_trace_to_sources` fails |
| Put a real-looking public IP (e.g. 8.8.8.8) in an alert | the hygiene test fails |
| Remove `escalate_condition` from an escalate=yes label | the loader rejects the row |
| In `rate.py` round to 0 decimals | `test_rate.py` fails |

## 4. Real output captured by Claude
_(filled in T02-15)_

## 5. Naveed's verdict
_(labels verified: k/40 alerts, k/95 probes · verified / changes needed)_
