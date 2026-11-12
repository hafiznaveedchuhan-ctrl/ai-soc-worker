# spec — 02 evals-first
Status: **approved** (human:naveed, 2026-11-12) · Intent: `./INTENT.md` · Plan of record: `../00-final-plan.txt` §12 · ADR-0002, ADR-0009

## 1. Summary
A new workspace package `soc-evals` (`backend/evals/`) with: the datasets (alerts, labels, scope probes, a KSOR reference list),
loaders that validate them, prediction schemas, a scorer, a Markdown report renderer, a CLI, recorded predictions for the dry run,
and a review sheet that Naveed uses to verify labels.

## 2. Functional requirements

### 2.1 Datasets
| ID | Requirement | Acceptance |
|---|---|---|
| FR-02-01 | `evals/data/alerts/<ALERT_ID>.json` — 40 files, each a valid `soc_shared.models.WazuhAlert` with NO extra metadata keys (metadata lives in labels.csv, so nothing eval-only can reach an LLM). IDs `EV-A001`…`EV-A040`. | Loader validates 40/40. |
| FR-02-02 | Composition: ≥ 1 TP per handbook playbook (10 playbooks — corrected from 11), ≥ 20 TP in total (INTENT Q3), 10 benign_TP/FP cases based on the handbook's 5 false-positive pages (2 each), ≥ 4 `needs_info`, ≥ 1 alert for each of the 8 escalation-policy conditions, ≥ 8 alerts with `escalate=no`. Up to 6 alerts mapped from OTRF (Q1), else SYNTHETIC (as built: 20 playbook + 4 port-scan/PowerShell + 10 FP-page + 6 OTRF). | `make eval-stats` prints the composition table; test asserts the minimums. |
| FR-02-03 | `evals/data/labels.csv` columns: `alert_id, source (SYNTHETIC\|OTRF), source_ref, playbook, verdict (TP\|benign_TP\|FP\|needs_info), severity, escalate (yes\|no), escalate_condition (1–8 or empty), mitre_ids (;-separated), expected_stable_ids (;-separated), rule_source (handbook page or ruleset file:line), rationale, verified_by, verified_at`. | Loader: every row valid, every alert has exactly one row, verdict/escalate pass the same rules as `TriageNote` (escalate ⇔ condition; a verdict needs ≥ 1 expected stable_id). |
| FR-02-03b | `evals/data/context.csv` (`alert_id, analyst_context`): analyst-provided context (change tickets, CDB-list membership, related alerts). It is an INPUT to the pipeline, masked like the alert, and never contains a verdict word. Label column `also_conditions` lists other escalation conditions that are also true; condition agreement accepts any of them. | `test_context_is_input_only`; scorer test. |
| FR-02-04 | Fact rule: every `rule.id` + `rule.level` in an alert equals a row of the handbook page in `rule_source` (or the confirmed ruleset line, Q2); every MITRE ID in `mitre_ids` is in `reference/ksor_mitre_ids.txt` or in the alert's `rule.mitre.id`. | Test `test_facts_trace_to_sources`. |
| FR-02-05 | `evals/data/scope/probes.csv` columns: `probe_id, set (DECLINE\|ALLOW_KSOR\|ALLOW_CYBER_RESEARCH\|NON_CYBER), expected_label, category, question, expected_stable_id, origin, verified_by`. 95 rows: DECLINE 30 (25 from `../handbook/evals/wave1-out-of-scope.txt` + 5 new prompt-injection), ALLOW_CYBER_RESEARCH 25 (the 10 handbook vendor/query-language probes per ADR-0002 + 15 new defensive-not-in-KSOR), ALLOW_KSOR 30 (from the handbook TSVs, with their expected stable_id, spread across ≥ 8 folders), NON_CYBER 10 (new; expected DECLINE). `origin` = `handbook:<file>:<line>` or `new`. | Counts test; every ALLOW_KSOR row has a valid stable_id; NON_CYBER and DECLINE rows expect `DECLINE`. |
| FR-02-06 | `evals/data/reference/ksor_mitre_ids.txt` and `ksor_stable_ids.txt`: snapshots of the handbook's MITRE page IDs and document stable_ids (generated from `../handbook/knowledge/` file names by a script, read-only; header states source commit and date). | Generator script + test that every expected_stable_id is in the snapshot. |
| FR-02-07 | Data hygiene: no non-documentation public IP, no real email domain (only `lab.example`/`example.*`), no secrets. | Test runs `find_unmasked_pii` + allowlist; gitleaks passes. |

### 2.2 Predictions, scoring and report
| ID | Requirement | Acceptance |
|---|---|---|
| FR-02-10 | Prediction schemas (Pydantic): `AlertPrediction(alert_id, note: TriageNote \| None, error: str \| None, latency_ms, usage: list[LlmUsage], output_text)` and `ProbePrediction(probe_id, scope_label, answer: AskAnswer \| None, error, latency_ms, usage, output_text)`. Stored as JSONL. | Round-trip tests. |
| FR-02-11 | `Rate(k, n)` value type: renders `"k/n = p%"` with one decimal (`24/25 = 96.0%`), `n=0` → `"0/0 = n/a"`. Every metric in code and report uses it (A5). | Tests. |
| FR-02-12 | Triage metrics: confusion matrix 4×4; TP recall; TP precision; verdict accuracy; escalation agreement; escalation-condition agreement (when both escalate); expected-page hit rate (≥ 1 expected stable_id cited); invented MITRE IDs; cite-or-abstain pass rate; leak count (`find_unmasked_pii` on `output_text` + the raw-value list of the alert); errors/timeouts counted as wrong. | Unit tests on hand-made predictions with known answers. |
| FR-02-13 | Scope metrics per set: label accuracy; decline rate (DECLINE, NON_CYBER); false-decline rate (ALLOW sets); exact-decline-text rate (every DECLINE output equals `DECLINE_MESSAGE`); per-category breakdown. | Unit tests. |
| FR-02-14 | Cost and latency: total and mean `cost_usd`, mean tokens, latency p50/p95 (nearest-rank), per set. | Unit tests. |
| FR-02-15 | Targets table from INTENT is applied: each target → PASS/FAIL; the report lists every failing item with its id and reason. Results on VERIFIED labels and on ALL labels are shown separately. | Golden report test. |
| FR-02-16 | `reports/template.md` + renderer → `reports/<YYYY-MM-DD>-<mode>-report.md` (mode `dry` or `paid`) with: run info (git sha, models, date), dataset sizes, targets table, metrics, confusion matrix, failures, cost/latency, label-verification status, known conflicts (Q4). | Golden test on the dry run. |

### 2.3 Commands
| ID | Requirement | Acceptance |
|---|---|---|
| FR-02-20 | `make eval-dry` = validate all datasets → load `recordings/dry/*.jsonl` → score → write `reports/<date>-dry-report.md` → exit 0 if datasets are valid and the scorer ran (dry targets are not applied to the oracle recording; see FR-02-22). | Runs offline in < 10 s; CI step added. |
| FR-02-21 | `make eval` = paid mode: refuses unless `--yes-paid` is given AND features 05/06 provide the pipeline (until then prints "pipeline arrives in feature 05/06" and exits 1). It never runs in CI. | Test of the refusal. |
| FR-02-22 | Recordings: `recordings/dry/oracle.jsonl` (predictions equal to the labels → every metric 100%) and `recordings/dry/faulty.jsonl` (known mistakes: missed TP, false decline, invented MITRE, leaked IP, wrong decline text, an error) used by the scorer tests to prove each check fires. | Tests: oracle → all PASS; faulty → exactly the planted failures. |
| FR-02-23 | `make eval-stats` prints the dataset composition (counts per verdict, playbook, condition, set, source, verified). | Manual + test. |
| FR-02-24 | `make eval-review` writes `evals/review/labels-review.md`: one block per alert (masked summary of the key fields, label, rationale, rule source, handbook pages) and one table for probes, with a checkbox for Naveed. Marking verified = Naveed fills `verified_by`/`verified_at` in the CSVs (or tells Claude the IDs). | File generated; test. |

## 3. Non-functional requirements
| ID | Requirement |
|---|---|
| NFR-02-01 | Offline and free: no socket in tests or eval-dry (pytest-socket). |
| NFR-02-02 | `soc-evals` coverage ≥ 85%, mypy --strict, ruff clean; CI runs its tests and `make eval-dry`. |
| NFR-02-03 | Deterministic: the same recordings produce a byte-identical report except the date/sha header. |
| NFR-02-04 | The paid runner (later) has a per-run budget and the global $9 ledger check before the first call. |

## 4. Edge cases
Missing prediction for an item → counted as an error (wrong), listed in failures · duplicate IDs → load error · a label row whose alert file is missing → load error ·
`needs_info` predictions on TP-labelled alerts → a TP miss · a DECLINE answer with a different text → scope correct but exact-text check fails.

## 5. Out of scope
Agent pipeline (05), guardrails (06), real model calls, live Wazuh, editing the handbook.

## 6. Traceability
| FR | Test / VERIFY |
|---|---|
| 01–07 | `evals/tests/test_datasets.py`, `test_facts.py`, `test_hygiene.py` · VERIFY §1 |
| 10–16 | `evals/tests/test_rate.py`, `test_scoring_triage.py`, `test_scoring_scope.py`, `test_report.py` |
| 20–24 | `evals/tests/test_cli.py` · VERIFY §1–3 |
