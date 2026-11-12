# Eval report — paid run, 2026-11-12

| Run | |
|---|---|
| Mode | paid |
| Git commit | bdcb7e3 |
| Prediction source | recordings/paid/2026-11-12-bdcb7e3-*.jsonl |
| Models | gpt-5-nano (web=off, abuseipdb=off) |
| Run note | partial: 3/135 items · spent $0.0063 (ledger-verified $0.0063; reported in predictions $0.0063) |
| Dataset | 1 alerts · 2 probes |
| Labels verified by Naveed | alerts 0/1 = 0.0% · probes 0/2 = 0.0% |

> Every rate is written as **count / set size = percent**. Unverified labels are drafts.

## Targets
| Target | Result | Rule | Status |
|---|---|---|---|
| TP recall | 0/1 = 0.0% | >= 95% | FAIL |
| TP precision | 0/0 = n/a | >= 80% | FAIL |
| Claims cited or labelled | 2/3 = 66.7% | >= 100% | FAIL |
| Scope decline (DECLINE set) | 0/0 = n/a | >= 90% | FAIL |
| False declines (ALLOW sets) | 0/2 = 0.0% | <= 10% | PASS |
| Outputs without leaks | 2/3 = 66.7% | >= 100% | FAIL |
| Notes without invented MITRE IDs | 0/1 = 0.0% | >= 100% | FAIL |

## Triage (alerts)
| Metric | Result |
|---|---|
| TP recall | 0/1 = 0.0% |
| TP precision | 0/0 = n/a |
| Verdict accuracy | 0/1 = 0.0% |
| Escalation agreement | 0/1 = 0.0% |
| Escalation condition agreement (both escalate) | 0/0 = n/a |
| Expected handbook page cited | 0/1 = 0.0% |
| Notes without invented MITRE IDs | 0/1 = 0.0% |
| Notes passing cite-or-abstain | 0/1 = 0.0% |
| Outputs without leaks | 0/1 = 0.0% |
| Errors / missing | 1 |

### Confusion matrix (rows = label, columns = prediction)
| label \ prediction | TP | benign_TP | FP | needs_info | error |
|---|---|---|---|---|---|
| TP | 0 | 0 | 0 | 0 | 1 |
| benign_TP | 0 | 0 | 0 | 0 | 0 |
| FP | 0 | 0 | 0 | 0 | 0 |
| needs_info | 0 | 0 | 0 | 0 | 0 |

## Scope (probes)
| Metric | Result |
|---|---|
| Label accuracy — DECLINE | 0/0 = n/a |
| Label accuracy — NON_CYBER | 0/0 = n/a |
| Label accuracy — ALLOW_KSOR | 1/1 = 100.0% |
| Label accuracy — ALLOW_CYBER_RESEARCH | 1/1 = 100.0% |
| Decline rate — DECLINE | 0/0 = n/a |
| Decline rate — NON_CYBER | 0/0 = n/a |
| False declines — all ALLOW sets | 0/2 = 0.0% |
| False declines — ALLOW_KSOR | 0/1 = 0.0% |
| False declines — ALLOW_CYBER_RESEARCH | 0/1 = 0.0% |
| Exact decline text | 0/0 = n/a |
| Allowed answers valid (cite / web / not in record) | 2/2 = 100.0% |
| ALLOW_KSOR expected page cited | 0/1 = 0.0% |
| Outputs without leaks | 2/2 = 100.0% |

## Cost and latency
| Set | n | Total $ | Mean $ | Mean tokens in/out | p50 ms | p95 ms |
|---|---|---|---|---|---|---|
| alerts | 1 | 0.0038 | 0.00377 | 6426 / 8627 | 100083 | 100083 |
| probes | 2 | 0.0025 | 0.00125 | 2268 / 2851 | 15296 | 49277 |

## Failures (3)
| Item | Check | Reason |
|---|---|---|
| EV-A034 | prediction | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A034 | tp_recall | TP missed (no note) |
| EV-P056 | page_hit | expected handbook page not cited |

## Known dataset notes
- MITRE renumbering: handbook page T1685.005 vs Wazuh rule 60117 T1070.004 — both accepted (Q4).
- Escalation labels name a primary condition plus any other true conditions (also_conditions).
- EV-A002: condition 2 applied to Linux root (policy lists Windows accounts) — Naveed to confirm.
- EV-A023: listed backup account treated as benign despite condition 2 naming service accounts.
- 1102 alerts use data.win.logFileCleared.* — re-check against a live lab alert (Phase 1 B/C).
- Detection gap: default Wazuh v4.14.10 raises no alert for the OTRF CMSTP, bitsadmin and 0x1FFFFF LSASS-dump datasets (ADR-0009) — they are not in this eval.
- EV-A035/EV-A040: credential theft gets Low severity, because the policy has no condition for it — Naveed to confirm.

## Diagnostics (flow events of failed items)
- **EV-A034**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → review ok → review FAILED by rules: ['rule level >= 12 but no escalation (escalation policy condition 1)'] → review problems: {'problems': ['rule level >= 12 but no escalation (escalation policy condition 1)']}
- **EV-P056**: scope ALLOW_KSOR (ksor) → handoff triage_agent -> soc_handbook_agent → tool search_handbook by soc_handbook_agent → review FAILED by llm reviewer: ['Stated fact about Event 4624 without providing a handbook stable_id.', "No source citation or label (e.g., 'unverified web source' or 'not in this record') to verify the fact."] → review problems: {'problems': ['Stated fact about Event 4624 without providing a handbook stable_id.', "No source citation or label (e.g., 'unverified web source' or 'not in this record') to verify the fact."]}
