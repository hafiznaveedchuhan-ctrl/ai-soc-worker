# PHR-0008 — Feature 02 approved and mostly implemented; PR #3 merged mid-feature
- Date: 2026-11-12T06:50Z–07:15Z · Session: 1 · Stage: implement
- Feature: 02 · Branch: feat/02-evals-first → feat/02-evals-part2 · Model: claude-opus-5-5

## Prompt (verbatim)
"approced"

## Response summary
- Took "approced" to approve the 02 docs, with the Q3 (≥ 20 TP) and Q4 (both MITRE ids) proposals. Did NOT take it as a "haan" for Q1 (OTRF download)
  or Q2 (reading the Wazuh ruleset), because both are external calls that the hard rules say need an explicit "haan".
- Built `soc-evals`:
  - Rate (k/n = p%), prediction schemas, the dataset loader;
  - triage, scope and cost scorers, targets;
  - the KSOR reference snapshot (read only);
  - 95 probes (builder script, handbook origin per row);
  - 30 alerts from a builder script, with every fact traced to handbook pages;
  - context.csv, also_conditions;
  - oracle and faulty recordings, the report template, CLI, review sheet, Makefile targets, the CI eval-dry step.
- Read only from the handbook: severity model, false-positive "Handbook rule" sections, rule tables, Linux useradd table.
- Naveed merged PR #3 (the first 3 commits) during the work. The guard caught it, so the remaining work went to the new branch `feat/02-evals-part2`.

## Files touched
backend/evals/** (new package, data, scripts, tests), backend/{pyproject.toml,Makefile}, .github/workflows/ci.yml,
soc-shared masking/patterns.py (+ test), specs/02-evals-first/{spec,tasks}.md (as-built), progress.md.

## Decisions / outcomes
Labels stay out of the alert JSON; analyst context is a separate, masked input; also_conditions for alerts where several conditions are true;
the severity label is computed from the handbook model; built-in groups stay unmasked.
Handbook ambiguities are flagged for Naveed (EV-A002 root, EV-A023 service account vs condition 2, 1102 field path).

## Follow-ups
Naveed: Q1/Q2 haan or no; verify the labels; choose the PR rhythm. Claude: the remaining 10 alerts, docs, VERIFY, PR.
