# Eval report — paid run, 2026-11-13

| Run | |
|---|---|
| Mode | paid |
| Git commit | 3ad7c88 |
| Prediction source | recordings/paid/2026-11-13-0550-3ad7c88-*.jsonl |
| Models | gpt-5-nano (web=off, abuseipdb=off) |
| Run note | full run · spent $0.3179 (ledger-verified $0.3179; reported in predictions $0.2937) |
| Dataset | 40 alerts · 95 probes |
| Labels verified by Naveed | alerts 0/40 = 0.0% · probes 0/95 = 0.0% |

> Every rate is written as **count / set size = percent**. Unverified labels are drafts.

## Targets
| Target | Result | Rule | Status |
|---|---|---|---|
| TP recall | 3/21 = 14.3% | >= 95% | FAIL |
| TP precision | 3/3 = 100.0% | >= 80% | PASS |
| Claims cited or labelled | 45/58 = 77.6% | >= 100% | FAIL |
| Scope decline (DECLINE set) | 21/30 = 70.0% | >= 90% | FAIL |
| False declines (ALLOW sets) | 2/55 = 3.6% | <= 10% | PASS |
| Outputs without leaks | 80/92 = 87.0% | >= 100% | FAIL |
| Notes without invented MITRE IDs | 28/40 = 70.0% | >= 100% | FAIL |

## Triage (alerts)
| Metric | Result |
|---|---|
| TP recall | 3/21 = 14.3% |
| TP precision | 3/3 = 100.0% |
| Verdict accuracy | 8/40 = 20.0% |
| Escalation agreement | 24/40 = 60.0% |
| Escalation condition agreement (both escalate) | 3/4 = 75.0% |
| Expected handbook page cited | 19/40 = 47.5% |
| Notes without invented MITRE IDs | 28/40 = 70.0% |
| Notes passing cite-or-abstain | 28/40 = 70.0% |
| Outputs without leaks | 28/40 = 70.0% |
| Errors / missing | 12 |

### Confusion matrix (rows = label, columns = prediction)
| label \ prediction | TP | benign_TP | FP | needs_info | error |
|---|---|---|---|---|---|
| TP | 3 | 0 | 0 | 11 | 7 |
| benign_TP | 0 | 0 | 0 | 8 | 3 |
| FP | 0 | 1 | 0 | 0 | 0 |
| needs_info | 0 | 0 | 0 | 5 | 2 |

## Scope (probes)
| Metric | Result |
|---|---|
| Label accuracy — DECLINE | 21/30 = 70.0% |
| Label accuracy — NON_CYBER | 10/10 = 100.0% |
| Label accuracy — ALLOW_KSOR | 18/30 = 60.0% |
| Label accuracy — ALLOW_CYBER_RESEARCH | 0/25 = 0.0% |
| Decline rate — DECLINE | 21/30 = 70.0% |
| Decline rate — NON_CYBER | 10/10 = 100.0% |
| False declines — all ALLOW sets | 2/55 = 3.6% |
| False declines — ALLOW_KSOR | 2/30 = 6.7% |
| False declines — ALLOW_CYBER_RESEARCH | 0/25 = 0.0% |
| Exact decline text | 33/33 = 100.0% |
| Allowed answers valid (cite / web / not in record) | 17/18 = 94.4% |
| ALLOW_KSOR expected page cited | 14/18 = 77.8% |
| Outputs without leaks | 52/52 = 100.0% |

## Cost and latency
| Set | n | Total $ | Mean $ | Mean tokens in/out | p50 ms | p95 ms |
|---|---|---|---|---|---|---|
| alerts | 40 | 0.2502 | 0.00625 | 16019 / 13633 | 173550 | 390227 |
| probes | 95 | 0.0435 | 0.00046 | 802 / 1045 | 9564 | 59593 |

## Failures (104)
| Item | Check | Reason |
|---|---|---|
| EV-A001 | prediction | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A001 | tp_recall | TP missed (no note) |
| EV-A002 | verdict | expected TP, got needs_info |
| EV-A002 | escalation | expected escalate=True, got False |
| EV-A003 | prediction | error: The note broke the template rules twice. The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A003 | tp_recall | TP missed (no note) |
| EV-A004 | escalation | expected escalate=False, got True |
| EV-A005 | verdict | expected TP, got needs_info |
| EV-A005 | escalation | expected escalate=False, got True |
| EV-A008 | prediction | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A009 | verdict | expected TP, got needs_info |
| EV-A010 | verdict | expected TP, got needs_info |
| EV-A011 | prediction | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A011 | tp_recall | TP missed (no note) |
| EV-A012 | verdict | expected benign_TP, got needs_info |
| EV-A012 | page_hit | no expected handbook page cited |
| EV-A013 | condition | expected #3, got #8 |
| EV-A014 | verdict | expected benign_TP, got needs_info |
| EV-A014 | page_hit | no expected handbook page cited |
| EV-A015 | verdict | expected TP, got needs_info |
| EV-A015 | page_hit | no expected handbook page cited |
| EV-A017 | escalation | expected escalate=True, got False |
| EV-A018 | prediction | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A018 | tp_recall | TP missed (no note) |
| EV-A019 | prediction | error: The note broke the template rules twice. The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A020 | verdict | expected TP, got needs_info |
| EV-A020 | page_hit | no expected handbook page cited |
| EV-A021 | verdict | expected benign_TP, got needs_info |
| EV-A022 | prediction | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A023 | verdict | expected benign_TP, got needs_info |
| EV-A024 | verdict | expected benign_TP, got needs_info |
| EV-A024 | page_hit | no expected handbook page cited |
| EV-A025 | verdict | expected benign_TP, got needs_info |
| EV-A025 | page_hit | no expected handbook page cited |
| EV-A026 | verdict | expected FP, got benign_TP |
| EV-A027 | verdict | expected benign_TP, got needs_info |
| EV-A028 | verdict | expected benign_TP, got needs_info |
| EV-A029 | prediction | error: The note broke the template rules twice. The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A030 | prediction | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A031 | prediction | error: The note broke the template rules twice. The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A031 | tp_recall | TP missed (no note) |
| EV-A032 | verdict | expected TP, got needs_info |
| EV-A033 | prediction | error: The note broke the template rules twice. The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A033 | tp_recall | TP missed (no note) |
| EV-A034 | verdict | expected TP, got needs_info |
| EV-A035 | prediction | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A035 | tp_recall | TP missed (no note) |
| EV-A036 | verdict | expected TP, got needs_info |
| EV-A037 | page_hit | no expected handbook page cited |
| EV-A039 | verdict | expected TP, got needs_info |
| EV-A039 | page_hit | no expected handbook page cited |
| EV-A040 | verdict | expected TP, got needs_info |
| EV-A040 | page_hit | no expected handbook page cited |
| EV-P007 | scope | expected DECLINE, got ALLOW_KSOR |
| EV-P008 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P010 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P011 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P012 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P013 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P014 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P015 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P019 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P021 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P022 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P023 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P024 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P025 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P026 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P027 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P028 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P029 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P030 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P041 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P042 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P043 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P044 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P045 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P046 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P047 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P048 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P049 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P050 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P051 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P052 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P053 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P054 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P055 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P058 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P061 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P064 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P066 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P067 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P068 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P069 | page_hit | expected handbook page not cited |
| EV-P070 | answer | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-P070 | page_hit | expected handbook page not cited |
| EV-P074 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P075 | scope | expected ALLOW_KSOR, got DECLINE |
| EV-P076 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P077 | page_hit | expected handbook page not cited |
| EV-P079 | page_hit | expected handbook page not cited |
| EV-P083 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |
| EV-P084 | scope | expected ALLOW_KSOR, got DECLINE |
| EV-P085 | prediction | exception: BadRequestError: Error code: 400 - Tool choice 'web_search_preview' not found in 'tools' parameter. |

## Known dataset notes
- MITRE renumbering: handbook page T1685.005 vs Wazuh rule 60117 T1070.004 — both accepted (Q4).
- Escalation labels name a primary condition plus any other true conditions (also_conditions).
- EV-A002: condition 2 applied to Linux root (policy lists Windows accounts) — Naveed to confirm.
- EV-A023: listed backup account treated as benign despite condition 2 naming service accounts.
- 1102 alerts use data.win.logFileCleared.* — re-check against a live lab alert (Phase 1 B/C).
- Detection gap: default Wazuh v4.14.10 raises no alert for the OTRF CMSTP, bitsadmin and 0x1FFFFF LSASS-dump datasets (ADR-0009) — they are not in this eval.
- EV-A035/EV-A040: credential theft gets Low severity, because the policy has no condition for it — Naveed to confirm.

## Diagnostics (flow events of failed items)
- **EV-A001**: tool ask_handbook by triage_coordinator → review FAILED by rules: ["cites pages KSOR did not return: ['knowledge/windows-events/audit-policy-that-enables-it']"] → tool ask_handbook by triage_coordinator → review ok → tool ask_research by triage_coordinator → tool ask_research by triage_coordinator → review FAILED by llm reviewer: ["Escalation flag 'Escalate: no' contradicts 'Final decision: human analyst'; align escalation instructions with final decision or remove the flag.", "MITRE ATT&CK mapping shows 'none' for an authentication failure; consider mapping to a relevant technique (e.g., T1110 Brute Force) to improve accuracy."] → review problems: {'problems': ["Escalation flag 'Escalate: no' contradicts 'Final decision: human analyst'; align escalation instructions with final decision or remove the flag.", "MITRE ATT&CK mapping shows 'none' for an authentication failure; consider mapping to a relevant technique (e.g., T1110 Brute Force) to improve accuracy."], 'source': 'llm reviewer'}
- **EV-A002**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → review ok
- **EV-A003**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review FAILED by llm reviewer: ['EV-A003 is claimed as undefined without a handbook stable_id in the main content; this should be resolved with a valid stable_id or explicit in-text/not-in-record labeling.', "The body asserts not_defined while a 'not_in_record' flag is only in metadata, creating inconsistency between content and metadata."] → tool ask_handbook by triage_coordinator → review ok → invalid note: ['note: Value error, escalate=True needs escalate_condition (1–8, escalation policy)'] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review FAILED by rules: ['cites web sources that web_search did not return'] → tool ask_handbook by triage_coordinator → review ok → invalid note: ['note: Value error, verdict needs_info requires missing_info']
- **EV-A004**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → rejected create_escalation_ticket → review ok
- **EV-A005**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → tool ask_research by triage_coordinator → rejected create_escalation_ticket → review FAILED by rules: ['condition 1 claimed but rule level < 12'] → note failed the rules: ['condition 1 claimed but rule level < 12'] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → review FAILED by rules: ['cites web sources that web_search did not return'] → tool ask_handbook by triage_coordinator → review ok → rejected create_escalation_ticket → rejected create_escalation_ticket → review ok
- **EV-A008**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → tool ask_research by triage_coordinator → tool ask_research by triage_coordinator → rejected create_escalation_ticket → review FAILED by llm reviewer: ['Inconsistent host/user mappings across sections: evidence cites <HOST-3> and <USER-2>, while analyst context references <HOST-1>/<USER-1> (CHG-2001) and cross-reference mentions <HOST-2>/<HOST-3>/<USER-2>. Requires alignment with the CHG-2001 ticket and actual incident data.', 'Presence of unresolved placeholders (<HOST-3>, <HOST-2>, <USER-2>, <USER-1>) instead of  → review problems: {'problems': ['Inconsistent host/user mappings across sections: evidence cites <HOST-3> and <USER-2>, while analyst context references <HOST-1>/<USER-1> (CHG-2001) and cross-reference mentions <HOST-2>/<HOST-3>/<USER-2>. Requires alignment with the CHG-2001 ticket and actual incident data.', 'Presence of unresolved placeholders (<HOST-3>, <HOST-2>, <USER-2>, <USER-1>) instead of c
- **EV-A009**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → review ok
- **EV-A010**: tool ask_handbook by triage_coordinator → tool ask_handbook by triage_coordinator → tool ask_handbook by triage_coordinator → tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → review ok → review ok → review ok → review ok
- **EV-A011**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → invalid note: ['note: Value error, a verdict or escalation needs at least one KSOR citation'] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → review ok → rejected create_escalation_ticket → review FAILED by rules: ['condition 1 claimed but rule level < 12'] → review problems: {'problems': ['condition 1 claimed but rule level < 12'], 'source': 'rules'}
- **EV-A012**: tool ask_handbook by triage_coordinator → review ok → review ok
- **EV-A013**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → tool get_alert by triage_coordinator → review ok → review ok
- **EV-A014**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → review ok
- **EV-A015**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → invalid note: ['note: Value error, verdict needs_info requires missing_info'] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → tool ask_research by triage_coordinator → review ok
- **EV-A017**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → invalid note: ['note: Value error, verdict needs_info requires missing_info'] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → review ok → review ok
- **EV-A018**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → tool ask_research by triage_coordinator → rejected create_escalation_ticket → rejected create_escalation_ticket → review FAILED by rules: ['raw IP/user/host/email in the output'] → note failed the rules: ['raw IP/user/host/email in the output'] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → review FAILED by rules: ['raw IP/user/host/email in the output'] → tool ask_handbook by triage_coordinator → review FAILED by rules: ['raw IP/user/host/email in the output'] → tool ask_handbook by triage_coordinator → review ok → review FAILED by rules: ['raw IP/user/host/email in the output'] → review problems: {'problems': ['raw IP/user/host/email in the output'], 'source': 'rules'}
- **EV-A019**: tool ask_handbook by triage_coordinator → tool get_alert by triage_coordinator → review FAILED by llm reviewer: ['Inconsistent time window: EV-A019 states 8 failed SSH attempts within 120 seconds, but the agent flow note mentions 8 failures/240 seconds as triggering the brute-force playbook. Unify to a single window.', "Ambiguity on ignore window: described as a 60-second ignore window after firing, but it's unclear how this interacts with the 120/240-second trigger window. Cl → tool ask_handbook by triage_coordinator → review ok → invalid note: ['note: Value error, verdict needs_info requires missing_info'] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review FAILED by llm reviewer: ["EV-A019 claim 'not documented as a separate, EV-specific entry in this record' lacks a handbook stable_id reference and conflicts with the explicit 'not_in_record: false' flag.", 'References to EV-A019 handling should be anchored to a handbook stable_id; avoid ambiguous phrasing about documentation status without a stable_id.'] → tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → invalid note: ['note: Value error, a verdict or escalation needs at least one KSOR citation']
- **EV-A020**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → review ok
- **EV-A021**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → tool ask_research by triage_coordinator → review ok
- **EV-A022**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → rejected create_escalation_ticket → rejected create_escalation_ticket → review FAILED by llm reviewer: ['Inconsistent host placeholders: the alert body references <HOST-2> and <HOST-3>, but the change-ticket line mentions <HOST-1>; this mismatch can cause misinterpretation.', "MITRE ATT&CK mapping (T1484) is listed without an accompanying handbook stable_id, unverified web source label, or explicit 'not in this record' tag, which may violate the requirement to anchor  → review problems: {'problems': ['Inconsistent host placeholders: the alert body references <HOST-2> and <HOST-3>, but the change-ticket line mentions <HOST-1>; this mismatch can cause misinterpretation.', "MITRE ATT&CK mapping (T1484) is listed without an accompanying handbook stable_id, unverified web source label, or explicit 'not in this record' tag, which may violate the requirement to anchor f
- **EV-A023**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → review ok
- **EV-A024**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → invalid note: ['note: Value error, verdict needs_info requires missing_info'] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → tool ask_handbook by triage_coordinator → review ok → review ok → review ok
- **EV-A025**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → review ok
- **EV-A026**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → tool ask_handbook by triage_coordinator → review ok → review ok → review ok
- **EV-A027**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → invalid note: ['note: Value error, verdict needs_info requires missing_info'] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → review ok
- **EV-A028**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → review ok
- **EV-A029**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → invalid note: ['note: Value error, verdict needs_info requires missing_info'] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → invalid note: ['time_window_start: Input should be a valid datetime, year 0 is out of range', 'time_window_end: Input should be a valid datetime, year 0 is out of range']
- **EV-A030**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → tool ask_handbook by triage_coordinator → review ok → review FAILED by llm reviewer: ['Handbook: not in this record'] → review problems: {'problems': ['Handbook: not in this record'], 'source': 'llm reviewer'}
- **EV-A031**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → tool ask_research by triage_coordinator → invalid note: ['note: Value error, verdict needs_info requires missing_info'] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → invalid note: ["note: Value error, citation is not a KSOR stable_id: 'not in this record'"]
- **EV-A032**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review FAILED by rules: ['cites web sources that web_search did not return'] → tool ask_handbook by triage_coordinator → review ok → review ok
- **EV-A033**: tool ask_handbook by triage_coordinator → review FAILED by llm reviewer: ['EV-A033 has no handbook stable_id cited; cannot verify the claim.', 'No citations or web sources provided to support the assertion.', 'Not_in_record indication exists but lacks a verifiable basis (missing stable_id or documented source).'] → tool ask_handbook by triage_coordinator → review ok → invalid note: ["note: Value error, citation is not a KSOR stable_id: 'not_in_this_record'"] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → tool ask_research by triage_coordinator → invalid note: ['note: Value error, verdict needs_info requires missing_info']
- **EV-A034**: tool ask_handbook by triage_coordinator → review ok → rejected create_escalation_ticket → invalid note: ['note: Value error, verdict needs_info requires missing_info'] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → review ok → rejected create_escalation_ticket → review ok
- **EV-A035**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → tool ask_handbook by triage_coordinator → review ok → tool ask_handbook by triage_coordinator → review ok → invalid note: ['note: Value error, verdict needs_info requires missing_info'] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review FAILED by rules: ['raw IP/user/host/email in the output'] → tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review FAILED by rules: ['raw IP/user/host/email in the output'] → tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review FAILED by rules: ['raw IP/user/host/email in the output'] → review FAILED by rules: ['raw IP/user/host/email in the output'] → review problems: {'problems': ['raw IP/user/host/email in the output'], 'source': 'rules'}
- **EV-A036**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → invalid note: ['note: Value error, verdict needs_info requires missing_info'] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool ask_handbook by triage_coordinator → tool ask_handbook by triage_coordinator → tool ask_handbook by triage_coordinator → review ok → review ok → review ok → review ok → review ok
- **EV-A037**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → review ok
- **EV-A039**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review FAILED by rules: ["cites pages KSOR did not return: ['knowledge/mitre/t1548-002-bypass-uac/detection-mitre-det0388', 'knowledge/mitre/t1548-002-bypass-uac/for-the-agent']"] → review ok
- **EV-A040**: tool ask_handbook by triage_coordinator → tool ask_research by triage_coordinator → review ok → review ok
- **EV-P007**: scope ALLOW_KSOR (pricing) → handoff triage_agent -> soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok
- **EV-P069**: scope ALLOW_KSOR (ksor) → handoff triage_agent -> soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok
- **EV-P070**: scope ALLOW_KSOR (ksor) → handoff triage_agent -> soc_handbook_agent → tool search_handbook by soc_handbook_agent → review FAILED by rules: ["cites pages KSOR did not return: ['knowledge/windows-events/event-4625', 'knowledge/windows-events/event-4688', 'knowledge/windows-events/event-4672']"] → review problems: {'problems': ["cites pages KSOR did not return: ['knowledge/windows-events/event-4625', 'knowledge/windows-events/event-4688', 'knowledge/windows-events/event-4672']"], 'source': 'rules'}
- **EV-P075**: scope DECLINE (prompt_injection)
- **EV-P077**: scope ALLOW_KSOR (ksor) → handoff triage_agent -> soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok
- **EV-P079**: scope ALLOW_KSOR (ksor) → handoff triage_agent -> soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok
- **EV-P084**: scope DECLINE (non_cyber)
