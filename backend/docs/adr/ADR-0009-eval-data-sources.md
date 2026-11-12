# ADR-0009 — Eval data sources and licences
- Status: **Proposed** (becomes Accepted with Naveed's answers to feature 02 INTENT Q1 and Q2)
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
