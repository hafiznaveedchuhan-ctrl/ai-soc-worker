# plan — 02 evals-first
Status: **approved** (human:naveed, 2026-11-12) · Spec: `./spec.md`

## 1. Approach
Build the scorer first (pure functions, tests on hand-made predictions), then the datasets in small batches with the
loaders validating every row, then the report, CLI and review sheet. Labels are drafted by Claude with a rationale and a
handbook source for each, and marked UNVERIFIED; Naveed verifies them from the review sheet.

## 2. Files
```
backend/pyproject.toml                       + member "evals"
backend/evals/
  pyproject.toml  README.md                  package soc-evals (depends on soc-shared)
  src/soc_evals/
    __init__.py  __main__.py  cli.py         python -m soc_evals {dry,paid,stats,review}
    datasets.py                              loaders + validation (alerts, labels, probes, references)
    predictions.py                           AlertPrediction, ProbePrediction, JSONL io
    rate.py                                  Rate(k, n)
    scoring/{triage,scope,cost}.py           metrics
    targets.py                               INTENT targets → PASS/FAIL
    report.py                                Markdown renderer (template below)
    review.py                                labels-review.md generator
  data/alerts/EV-A001.json … EV-A040.json
  data/labels.csv
  data/scope/probes.csv
  data/reference/ksor_mitre_ids.txt  ksor_stable_ids.txt
  recordings/dry/oracle.jsonl  faulty.jsonl
  reports/template.md  (generated reports are committed only for the paid run)
  review/labels-review.md                     generated
  scripts/snapshot_ksor_refs.py               reads ../handbook/knowledge file names (read only)
  tests/…
backend/Makefile                              eval-dry, eval, eval-stats, eval-review
.github/workflows/ci.yml                      + soc-evals in mypy/pytest + "make eval-dry" step
backend/docs/adr/ADR-0009-eval-data-sources.md (Proposed → Accepted on Naveed's Q1 answer)
backend/docs/LEARNING.md §8 "Evals", CAREER-MAP row 02
```

## 3. Design details
- **Why labels live in CSV, not in the alert JSON:** a `_meta` key inside an alert would ride along into masking and into the LLM
  prompt (WazuhAlert allows extra fields). Separate files make leakage of the answer impossible.
- **Synthetic alert recipe:** start from the handbook page's rule row (id, level, description, groups, MITRE) and the event page's
  fields (e.g. 4625 `status`/`subStatus`/`logonType`), build `data.win.*` / `data.*` / `full_log` with lab values, and write the
  rationale: "condition #4 because a 4624 follows rule 60204 within 60 min (escalation-policy row 4)". Multi-event stories
  (brute force → success) are represented as one correlated alert plus the `previous_output`-style context Wazuh itself includes,
  never as invented fields.
- **OTRF mapping (if Q1 = haan):** pick ≈ 8 small Windows Security/Sysmon datasets; convert one event to the Wazuh JSON shape
  (`data.win.system`, `data.win.eventdata`) by a script that keeps field names; rule id/level chosen from the handbook table for that
  event; attribution (dataset path + MIT notice) in `source_ref` and ADR-0009.
- **Scorer:** pure functions over `(labels, predictions)`; `Rate` everywhere; failures collected as `(item_id, check, reason)`.
- **Invented-MITRE check:** allowed = `ksor_mitre_ids.txt` ∪ the alert's `rule.mitre.id` (Q4).
- **Leak check:** `find_unmasked_pii(output_text)` plus a search for the alert's own raw values (from its JSON) in `output_text`.
- **Dry vs paid:** the same scorer and report; only the prediction source differs (recordings vs live pipeline from 05/06).

## 4. Docs to check before coding
| Item | Source | Why |
|---|---|---|
| Wazuh alert JSON field names for Windows eventchannel, sshd, syscheck | handbook `knowledge/wazuh/alert-json-anatomy` (read only) | fixtures must match real shape |
| OTRF dataset format + licence | **checked 2026-11-12**: LICENSE = MIT (text copied into THIRD_PARTY_NOTICES.md); events are flat JSON lines (EventID, Channel, Hostname, Windows XML field names); times: `UtcTime`/`@timestamp` | mapping + attribution |
| Wazuh ruleset v4.14.10 rule IDs for port scan / PowerShell / Sysmon | **checked 2026-11-12**: 0900-firewall_rules.xml L27 (4151, level 10, 18 drops/45 s); 0915-win-powershell_rules.xml L74 (91809, level 10, T1140), L432 (91844, level 12, T1547.001/T1059.001/T1112); 0800-sysmon_id_1.xml L734 (92068, level 3, T1569.002); 0945-sysmon_id_10.xml L10 (92900 needs grantedAccess 0x1010/0x40) | no invented IDs; field paths confirm camelCase `win.eventdata.scriptBlockText` |
| Python `statistics` / nearest-rank percentile | docs.python.org | p95 definition |

## 5. Test strategy
Scorer unit tests with tiny hand-made label/prediction sets (perfect, all wrong, mixed, empty) · dataset tests (schema, counts,
facts trace, hygiene) · oracle and faulty recordings end-to-end · golden report · CLI tests (dry OK, paid refuses).

## 6. Risks + mitigations
| Risk | Mitigation |
|---|---|
| Labels wrong or biased toward what the agent will do | rationale + handbook source per label; Naveed verifies; verified/unverified reported apart |
| Inventing facts in synthetic alerts | FR-02-04 test traces every rule/MITRE ID to a source |
| Small TP set makes recall jumpy | ≥ 20 TP (Q3); report shows k/n, not only % |
| Handbook MITRE renumbering | accept both, report the conflict (Q4) |
| Probe wording leaks the expected label | neutral wording; probes copied verbatim from handbook files where possible |

## 7. ADRs
ADR-0009 eval data sources and licences (Proposed now; Accepted with Q1/Q2 answers). ADR-0002 is used for the probe sets.

## 8. Learning notes (→ LEARNING.md §8)
Why evals come first · confusion matrix, precision vs recall in SOC terms (missed attack vs wasted analyst time) · why count + percent ·
oracle and faulty recordings (testing the tester) · nearest-rank p95 · data provenance and licences.
