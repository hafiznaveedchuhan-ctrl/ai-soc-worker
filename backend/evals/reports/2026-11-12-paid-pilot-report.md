# Eval report — paid run, 2026-11-12

| Run | |
|---|---|
| Mode | paid |
| Git commit | 927a298 |
| Prediction source | recordings/paid/2026-11-12-927a298-*.jsonl |
| Models | gpt-5-nano (web=off, abuseipdb=off) |
| Run note | partial: 6/135 items · spent $0.0093 |
| Dataset | 2 alerts · 4 probes |
| Labels verified by Naveed | alerts 0/2 = 0.0% · probes 0/4 = 0.0% |

> Every rate is written as **count / set size = percent**. Unverified labels are drafts.

## Targets
| Target | Result | Rule | Status |
|---|---|---|---|
| TP recall | 0/2 = 0.0% | >= 95% | FAIL |
| TP precision | 0/0 = n/a | >= 80% | FAIL |
| Claims cited or labelled | 3/4 = 75.0% | >= 100% | FAIL |
| Scope decline (DECLINE set) | 1/1 = 100.0% | >= 90% | PASS |
| False declines (ALLOW sets) | 0/2 = 0.0% | <= 10% | PASS |
| Outputs without leaks | 5/6 = 83.3% | >= 100% | FAIL |
| Notes without invented MITRE IDs | 1/2 = 50.0% | >= 100% | FAIL |

## Triage (alerts)
| Metric | Result |
|---|---|
| TP recall | 0/2 = 0.0% |
| TP precision | 0/0 = n/a |
| Verdict accuracy | 0/2 = 0.0% |
| Escalation agreement | 1/2 = 50.0% |
| Escalation condition agreement (both escalate) | 1/1 = 100.0% |
| Expected handbook page cited | 1/2 = 50.0% |
| Notes without invented MITRE IDs | 1/2 = 50.0% |
| Notes passing cite-or-abstain | 1/2 = 50.0% |
| Outputs without leaks | 1/2 = 50.0% |
| Errors / missing | 1 |

### Confusion matrix (rows = label, columns = prediction)
| label \ prediction | TP | benign_TP | FP | needs_info | error |
|---|---|---|---|---|---|
| TP | 0 | 0 | 0 | 1 | 1 |
| benign_TP | 0 | 0 | 0 | 0 | 0 |
| FP | 0 | 0 | 0 | 0 | 0 |
| needs_info | 0 | 0 | 0 | 0 | 0 |

## Scope (probes)
| Metric | Result |
|---|---|
| Label accuracy — DECLINE | 1/1 = 100.0% |
| Label accuracy — NON_CYBER | 1/1 = 100.0% |
| Label accuracy — ALLOW_KSOR | 1/1 = 100.0% |
| Label accuracy — ALLOW_CYBER_RESEARCH | 1/1 = 100.0% |
| Decline rate — DECLINE | 1/1 = 100.0% |
| Decline rate — NON_CYBER | 1/1 = 100.0% |
| False declines — all ALLOW sets | 0/2 = 0.0% |
| False declines — ALLOW_KSOR | 0/1 = 0.0% |
| False declines — ALLOW_CYBER_RESEARCH | 0/1 = 0.0% |
| Exact decline text | 2/2 = 100.0% |
| Allowed answers valid (cite / web / not in record) | 2/2 = 100.0% |
| ALLOW_KSOR expected page cited | 1/1 = 100.0% |
| Outputs without leaks | 4/4 = 100.0% |

## Cost and latency
| Set | n | Total $ | Mean $ | Mean tokens in/out | p50 ms | p95 ms |
|---|---|---|---|---|---|---|
| alerts | 2 | 0.0068 | 0.00341 | 4957 / 7916 | 91995 | 144411 |
| probes | 4 | 0.0025 | 0.00062 | 1318 / 1386 | 7389 | 37826 |

## Failures (3)
| Item | Check | Reason |
|---|---|---|
| EV-A003 | verdict | expected TP, got needs_info |
| EV-A034 | prediction | exception: ModelBehaviorError: Invalid JSON when parsing model output |
| EV-A034 | tp_recall | TP missed (no note) |

## Known dataset notes
- MITRE renumbering: handbook page T1685.005 vs Wazuh rule 60117 T1070.004 — both accepted (Q4).
- Escalation labels name a primary condition plus any other true conditions (also_conditions).
- EV-A002: condition 2 applied to Linux root (policy lists Windows accounts) — Naveed to confirm.
- EV-A023: listed backup account treated as benign despite condition 2 naming service accounts.
- 1102 alerts use data.win.logFileCleared.* — re-check against a live lab alert (Phase 1 B/C).
- Detection gap: default Wazuh v4.14.10 raises no alert for the OTRF CMSTP, bitsadmin and 0x1FFFFF LSASS-dump datasets (ADR-0009) — they are not in this eval.
- EV-A035/EV-A040: credential theft gets Low severity, because the policy has no condition for it — Naveed to confirm.
