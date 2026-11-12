# INTENT — 02 evals-first
Status: **approved** (human:naveed, 2026-11-12; Q3 ≥ 20 TP and Q4 accept both MITRE IDs = proposals accepted; Q1 OTRF download and Q2 ruleset read still need an explicit "haan") · Plan of record: `../00-final-plan.txt` §12 (v2) · ADRs: 0002, 0009 (draft)

## Goal
Define "good" BEFORE any agent exists: a labelled set of Wazuh-shaped alerts and scope probes, a scorer that turns
predictions into the target metrics (every rate as **count/n = percent**), a report template, and two commands:
`make eval-dry` (free, offline, runs in CI) and `make eval` (paid, needs "haan", only usable after features 05–06).

## Users
- **Naveed** — labels are his decision: he verifies every label (40 alerts + 95 probes) using a review sheet.
- **CI** — `make eval-dry` must pass on every PR (dataset integrity + scorer correctness on recorded predictions).
- **Features 05–06** — plug the real agent pipeline into the same runner; the final paid run fills `report.md`.

## Constraints
- No LLM, no network in eval-dry. Recorded predictions only.
- Every label is **UNVERIFIED** until Naveed fills `verified_by`. The paid run reports verified and unverified results separately.
- Facts in fixtures come from the handbook only: every `rule.id`, `rule.level` and MITRE ID in a synthetic alert is
  taken from a handbook page (named in the label row). Nothing is invented. Where the handbook has no rule ID → open question Q2.
- Lab data only: documentation IPs (RFC 5737), RFC 1918, invented names (`lab-*`). SYNTHETIC cases are clearly marked.
- Public datasets only with their licence recorded (ADR-0009): OTRF Security-Datasets = MIT; Splunk BOTS v1 = CC0-1.0 (not planned; Splunk format, very large).
- Read-only use of `../handbook/evals/*` (copied into our eval set with origin noted; the handbook is not changed).

## Success numbers
For **this feature** (dry): every dataset row passes schema validation (count/n = 100%); `make eval-dry` exit 0 locally and in CI;
the scorer unit tests prove each metric on hand-made predictions (perfect, all-wrong, mixed); `make eval` refuses to run without
an explicit `--yes-paid` flag and the budget settings.

Targets that the **paid run** (after 06) must meet — defined here, measured later:
| Metric | Target | Set size |
|---|---|---|
| TP recall (alerts labelled TP that the AI also calls TP) | ≥ 95% | n = TP-labelled alerts (≥ 16) |
| TP precision | ≥ 80% | n = alerts the AI calls TP |
| Claims cited or labelled (notes + answers that pass the cite-or-abstain check) | 100% | n = 40 + 95 |
| Scope decline rate on the DECLINE set | ≥ 90% | n = 30 |
| False declines on the ALLOW sets | ≤ 10% | n = 55 (30 KSOR + 25 research) |
| Raw-value leaks in outputs | 0 | n = 135 |
| Invented MITRE IDs (not in the alert and not in the handbook's MITRE pages) | 0 | n = 40 |
| Escalation agreement, verdict accuracy, expected-page hit rate | reported | per set |
| Cost per request (mean, total), latency p50 / p95 | reported | per set |

## Out of scope
Running any model; building agents; changing the handbook's evals; live Wazuh data.

## Open questions for Naveed
1. **OTRF download (needs your "haan"):** may I download about 8 small OTRF Security-Datasets files (MIT licence, public GitHub, free)
   and map them to the Wazuh shape? If "no" → those 8 become SYNTHETIC alerts too.
2. **Rule IDs the handbook does not list** (port-scan, PowerShell 4104 / Sysmon process events): the handbook has no Wazuh rule ID
   for them. **Proposal:** read the official Wazuh ruleset at tag v4.14.10 on GitHub (the same source the handbook cites, free,
   read-only) and record the file and line for each ID used. Alternative: give those alerts `rule.id` values from the ruleset only
   after you confirm them.
3. **Size of the TP class:** with 16 TP alerts, one miss gives 15/16 = 93.75% (< 95%). **Proposal:** make at least 20 of the 40
   alerts TP (so one miss = 95.0% still passes; two misses fail), by giving each of the 11 playbooks ≥ 1 TP plus 9 more.
4. **MITRE version conflict:** the handbook's MITRE page uses **T1685.005** for clearing Windows event logs, while its Wazuh rule table
   shows **T1070.004** for rule 60117. **Proposal:** labels accept both (handbook page = preferred, the alert's own `rule.mitre` = allowed),
   and the report notes the conflict for you.
