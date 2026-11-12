# ADR-0009 — Eval data sources and licences
- Status: **Accepted** (human:naveed, 2026-11-12 — "all haan" to Q1 OTRF download and Q2 ruleset read)
- Date: 2026-11-12 · Feature: 02 · Deciders: human:naveed (approver), Claude (author)
- Related: specs/02-evals-first/{INTENT,spec,plan}.md, ADR-0002

## Context
- The evals need 40 Wazuh-shaped alerts with trusted labels and 95 scope probes. The Wazuh lab is offline (Phase 1 Part B/C),
  so there is no live data, and the worker must never see real organisation data.
- Every fact in a fixture (rule id, level, MITRE ID) must be traceable to a source; inventing IDs is forbidden (constitution IV.2).
- Licences checked on 2026-11-12 via the GitHub API: **OTRF/Security-Datasets = MIT**; **splunk/botsv1 = CC0-1.0**.

## Options considered
1. **All SYNTHETIC from the handbook** — fully controlled, fact-traceable to handbook pages, zero download; but less "real" noise.
2. **SYNTHETIC + a few OTRF events mapped to the Wazuh shape (proposed)** — real Windows/Sysmon field noise from public, MIT-licensed lab
   recordings; a small download (needs "haan"); the mapping script keeps field names; rule ids still come from the handbook.
3. **Splunk BOTS v1** — CC0 and rich, but Splunk-indexed formats and very large downloads; mapping cost is high for 40 alerts.

## Decision (proposed)
Option 2: 32 SYNTHETIC alerts built from handbook pages + up to 8 events from OTRF Security-Datasets (MIT), mapped to the Wazuh
alert shape, each with `source_ref` = dataset path + MIT attribution. Rule ids not present in the handbook are taken only from the
official Wazuh ruleset at tag v4.14.10 (the source the handbook itself cites), with file:line recorded. If Q1 = no → Option 1.
Scope probes: copied from `../handbook/evals/` (origin recorded per row) plus new probes written for this project.

## Consequences
- (+) Every label is explainable from a cited source; the dataset is safe to publish in a public repo.
- (−) Synthetic alerts can be "too clean"; the OTRF share and the FP cases add realism.
- Follow-up: an attribution section in `evals/README.md`; re-check licences if more datasets are added.

## Verification
`test_facts_trace_to_sources` (FR-02-04) and the hygiene test (FR-02-07) pass; Naveed verifies every label.

## Outcome (2026-11-12, as built)
- 40 alerts: 34 SYNTHETIC (30 from handbook pages, 4 with rule ids read from the Wazuh ruleset v4.14.10:
  4151 firewall drops, 91809 PowerShell Base64, 91844 Run-key via PowerShell; 5731 from the handbook) + **6 OTRF**
  events from 2 datasets (PsExec LSA-secrets dump, Covenant SharpSC remote service). Attribution and the MIT notice:
  `evals/data/THIRD_PARTY_NOTICES.md`.
- **Detection-gap finding:** 4 other OTRF datasets were downloaded (CMSTP UAC bypass, bitsadmin download, comsvcs and
  Dumpert LSASS dumps). The default ruleset v4.14.10 has **no rule** that fires on them: rule 92900 (LSASS access) matches
  only `grantedAccess` 0x1010/0x40, while these dumps use 0x1FFFFF; there is no cmstp or bitsadmin rule. They are not used
  as alerts, because a default Wazuh would not raise them. This is recorded as a lesson for the later live lab and custom rules.
- Raw downloads stay in the session scratchpad only; no OTRF or Wazuh file is committed.
