# Eval report — paid run, 2026-11-18

| Run | |
|---|---|
| Mode | paid |
| Git commit | 8ffc5bf |
| Prediction source | recordings/paid/2026-11-18-0428-8ffc5bf-*.jsonl |
| Models | gpt-5-mini, gpt-5-nano (web=tavily, abuseipdb=off) |
| Run note | partial: 40/135 items · spent $0.6666 (ledger-verified $0.6666; reported in predictions $0.6666) |
| Dataset | 40 alerts · 0 probes |
| Labels verified by Naveed | alerts 0/40 = 0.0% · probes 0/0 = n/a |

> Every rate is written as **count / set size = percent**. Unverified labels are drafts.

## Targets
| Target | Result | Rule | Status |
|---|---|---|---|
| TP recall | 3/21 = 14.3% | >= 95% | FAIL |
| TP precision | 3/3 = 100.0% | >= 80% | PASS |
| Claims cited or labelled | 33/40 = 82.5% | >= 100% | FAIL |
| Scope decline (DECLINE set) | 0/0 = n/a | >= 90% | FAIL |
| False declines (ALLOW sets) | 0/0 = n/a | <= 10% | FAIL |
| Outputs without leaks | 33/40 = 82.5% | >= 100% | FAIL |
| Notes without invented MITRE IDs | 33/40 = 82.5% | >= 100% | FAIL |

## Triage (alerts)
| Metric | Result |
|---|---|
| TP recall | 3/21 = 14.3% |
| TP precision | 3/3 = 100.0% |
| Verdict accuracy | 14/40 = 35.0% |
| Escalation agreement | 20/40 = 50.0% |
| Escalation condition agreement (both escalate) | 4/4 = 100.0% |
| Expected handbook page cited | 30/40 = 75.0% |
| Notes without invented MITRE IDs | 33/40 = 82.5% |
| Notes passing cite-or-abstain | 33/40 = 82.5% |
| Outputs without leaks | 33/40 = 82.5% |
| Errors / missing | 7 |

### Confusion matrix (rows = label, columns = prediction)
| label \ prediction | TP | benign_TP | FP | needs_info | error |
|---|---|---|---|---|---|
| TP | 3 | 0 | 0 | 13 | 5 |
| benign_TP | 0 | 6 | 0 | 4 | 1 |
| FP | 0 | 1 | 0 | 0 | 0 |
| needs_info | 0 | 1 | 0 | 5 | 1 |

## Scope (probes)
| Metric | Result |
|---|---|
| Label accuracy — DECLINE | 0/0 = n/a |
| Label accuracy — NON_CYBER | 0/0 = n/a |
| Label accuracy — ALLOW_KSOR | 0/0 = n/a |
| Label accuracy — ALLOW_CYBER_RESEARCH | 0/0 = n/a |
| Decline rate — DECLINE | 0/0 = n/a |
| Decline rate — NON_CYBER | 0/0 = n/a |
| False declines — all ALLOW sets | 0/0 = n/a |
| False declines — ALLOW_KSOR | 0/0 = n/a |
| False declines — ALLOW_CYBER_RESEARCH | 0/0 = n/a |
| Exact decline text | 0/0 = n/a |
| Allowed answers valid (cite / web / not in record) | 0/0 = n/a |
| ALLOW_KSOR expected page cited | 0/0 = n/a |
| Outputs without leaks | 0/0 = n/a |

## Cost and latency
| Set | n | Total $ | Mean $ | Mean tokens in/out | p50 ms | p95 ms |
|---|---|---|---|---|---|---|
| alerts | 40 | 0.6666 | 0.01666 | 28185 / 18898 | 171131 | 363221 |
| probes | 0 | 0.0000 | 0.00000 | 0 / 0 | 0 | 0 |

## Failures (47)
| Item | Check | Reason |
|---|---|---|
| EV-A001 | escalation | expected escalate=False, got True |
| EV-A002 | verdict | expected TP, got needs_info |
| EV-A002 | escalation | expected escalate=True, got False |
| EV-A005 | prediction | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A005 | tp_recall | TP missed (no note) |
| EV-A008 | verdict | expected benign_TP, got needs_info |
| EV-A009 | prediction | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A009 | tp_recall | TP missed (no note) |
| EV-A010 | verdict | expected TP, got needs_info |
| EV-A010 | escalation | expected escalate=False, got True |
| EV-A011 | verdict | expected TP, got needs_info |
| EV-A011 | escalation | expected escalate=True, got False |
| EV-A012 | page_hit | no expected handbook page cited |
| EV-A013 | verdict | expected TP, got needs_info |
| EV-A013 | escalation | expected escalate=True, got False |
| EV-A015 | verdict | expected TP, got needs_info |
| EV-A016 | escalation | expected escalate=False, got True |
| EV-A017 | verdict | expected TP, got needs_info |
| EV-A017 | escalation | expected escalate=True, got False |
| EV-A018 | verdict | expected TP, got needs_info |
| EV-A019 | escalation | expected escalate=True, got False |
| EV-A020 | verdict | expected TP, got needs_info |
| EV-A021 | verdict | expected benign_TP, got needs_info |
| EV-A022 | escalation | expected escalate=False, got True |
| EV-A023 | verdict | expected benign_TP, got needs_info |
| EV-A023 | escalation | expected escalate=False, got True |
| EV-A024 | verdict | expected benign_TP, got needs_info |
| EV-A024 | escalation | expected escalate=False, got True |
| EV-A025 | prediction | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A026 | verdict | expected FP, got benign_TP |
| EV-A026 | escalation | expected escalate=False, got True |
| EV-A030 | page_hit | no expected handbook page cited |
| EV-A031 | prediction | error: The note broke the template rules twice. The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A031 | tp_recall | TP missed (no note) |
| EV-A032 | verdict | expected TP, got needs_info |
| EV-A033 | verdict | expected TP, got needs_info |
| EV-A033 | escalation | expected escalate=False, got True |
| EV-A034 | prediction | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A034 | tp_recall | TP missed (no note) |
| EV-A035 | prediction | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A035 | tp_recall | TP missed (no note) |
| EV-A036 | verdict | expected TP, got needs_info |
| EV-A037 | verdict | expected needs_info, got benign_TP |
| EV-A038 | prediction | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A039 | verdict | expected TP, got needs_info |
| EV-A040 | verdict | expected TP, got needs_info |
| EV-A040 | page_hit | no expected handbook page cited |

## Known dataset notes
- MITRE renumbering: handbook page T1685.005 vs Wazuh rule 60117 T1070.004 — both accepted (Q4).
- Escalation labels name a primary condition plus any other true conditions (also_conditions).
- EV-A002: condition 2 applied to Linux root (policy lists Windows accounts) — Naveed to confirm.
- EV-A023: listed backup account treated as benign despite condition 2 naming service accounts.
- 1102 alerts use data.win.logFileCleared.* — re-check against a live lab alert (Phase 1 B/C).
- Detection gap: default Wazuh v4.14.10 raises no alert for the OTRF CMSTP, bitsadmin and 0x1FFFFF LSASS-dump datasets (ADR-0009) — they are not in this eval.
- EV-A035/EV-A040: credential theft gets Low severity, because the policy has no condition for it — Naveed to confirm.

## How to read the rates
- **Real leaks found: 0** (raw IP/user/host/email in an output shown to the analyst).
- Alerts without a note (error/blocked): 7. Probes with an error: 0. They count as FAIL in the leak / MITRE / cite rates (conservative), even with no leak.

## Diagnostics (flow events of failed items)
- **EV-A001**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A002**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → rejected create_escalation_ticket → review FAILED by rules: ['condition 1 claimed but rule level < 12'] → note failed the rules: ['condition 1 claimed but rule level < 12'] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A005**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review FAILED by llm reviewer: ["Evidence bullet 1 includes 'source: not in this record', which states a fact without a handbook stable_id, an 'unverified web source' label, or 'not in this record'—this is a violation.", "Confidence value is 0.70 labeled as 'high', which is inconsistent; 0.70 should correspond to at most 'medium-high' rather than 'high'."] → review problems: {'problems': ["Evidence bullet 1 includes 'source: not in this record', which states a fact without a handbook stable_id, an 'unverified web source' label, or 'not in this record'—this is a violation.", "Confidence value is 0.70 labeled as 'high', which is inconsistent; 0.70 should correspond to at most 'medium-high' rather than 'high'."], 'source': 'llm reviewer'}
- **EV-A008**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A009**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review FAILED by llm reviewer: ['Inconsistent host/source data: alert metadata shows computers/hosts that conflict with the event text (HOST-2 vs HOST-1) and TargetDomainName HOST-1; need to confirm which host actually recorded the event.', 'MITRE mapping appears off: 4720 is account creation; typical technique is Create Account (e.g., T1136); verify the handbook mapping (T1098) for accuracy.', "E → review problems: {'problems': ['Inconsistent host/source data: alert metadata shows computers/hosts that conflict with the event text (HOST-2 vs HOST-1) and TargetDomainName HOST-1; need to confirm which host actually recorded the event.', 'MITRE mapping appears off: 4720 is account creation; typical technique is Create Account (e.g., T1136); verify the handbook mapping (T1098) for accuracy.', "Ev
- **EV-A010**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → rejected create_escalation_ticket → review ok
- **EV-A011**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A012**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review FAILED by rules: ['raw IP/user/host/email in the output'] → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review FAILED by rules: ['raw IP/user/host/email in the output'] → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A013**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → invalid note: ['note: Value error, escalate=True needs escalate_condition (1–8, escalation policy)'] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A015**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A016**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → rejected create_escalation_ticket → review ok
- **EV-A017**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A018**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → rejected create_escalation_ticket → review ok
- **EV-A019**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review FAILED by llm reviewer: ['Contains prescriptive, step-by-step containment actions (e.g., rate-limiting or blocking the source IP and rotating credentials) which constitute device configuration guidance.', 'Defense actions are too prescriptive for a non-actionable review and should be generalized to policy-level recommendations only.'] → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A020**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A021**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A022**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → invalid note: ["note: Value error, invalid MITRE technique ID: 'T1484 (listed in alert payload; not in this record)'"] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → rejected create_escalation_ticket → review ok
- **EV-A023**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → rejected create_escalation_ticket → review ok
- **EV-A024**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → invalid note: ['note: Value error, escalate=True needs escalate_condition (1–8, escalation policy)'] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A025**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → review FAILED by llm reviewer: ['No defensive actions or containment/eradication recommendations provided (only assessment; lacks triage playbook steps).', "Ambiguity in verdict labeling (use of 'benign TP' and unclear next steps; no explicit follow-up actions for analysts).", "Evidence includes items labeled 'source: not in this record' which weakens reliability of those statements; consider sour → review problems: {'problems': ['No defensive actions or containment/eradication recommendations provided (only assessment; lacks triage playbook steps).', "Ambiguity in verdict labeling (use of 'benign TP' and unclear next steps; no explicit follow-up actions for analysts).", "Evidence includes items labeled 'source: not in this record' which weakens reliability of those statements; consider sourc
- **EV-A026**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → rejected create_escalation_ticket → review ok
- **EV-A030**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A031**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review FAILED by llm reviewer: ['Not in this KSOR record: lacks a handbook stable_id or any verifiable external source to support the assertion.', "No handbook stable_id, or 'unverified web source' label provided; the claim 'not in record' is not independently verifiable.", 'No citations or stable_ids; cannot verify the claim.'] → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_research by triage_coordinator → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → review ok → rejected create_escalation_ticket → invalid note: ["note: Value error, citation is not a KSOR stable_id: 'not in this record (KSOR) for Wazuh rule 4151'"] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → invalid note: ["note: Value error, citation is not a KSOR stable_id: 'not in this record (KSOR) for Wazuh rule 4151'"]
- **EV-A032**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A033**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review FAILED by llm reviewer: ["Statement 'Not in this record' is asserted without a verified handbook stable_id.", 'No citations (handbook stable_ids) or web sources are provided to support the claim.', "The draft relies on a 'not_in_record' indicator rather than substantiated evidence."] → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A034**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → rejected create_escalation_ticket → review FAILED by llm reviewer: ["Evidence contains a fact (ScriptBlock text) with 'source: not in this record', indicating the fact is not verifiably sourced from the record's handbook or a verified source."] → review problems: {'problems': ["Evidence contains a fact (ScriptBlock text) with 'source: not in this record', indicating the fact is not verifiably sourced from the record's handbook or a verified source."], 'source': 'llm reviewer'}
- **EV-A035**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → rejected create_escalation_ticket → review FAILED by rules: ['raw IP/user/host/email in the output'] → note failed the rules: ['raw IP/user/host/email in the output'] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review FAILED by rules: ["cites pages KSOR did not return: ['knowledge/detection-mitre-det0363']"] → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → review FAILED by rules: ['raw IP/user/host/email in the output'] → review problems: {'problems': ['raw IP/user/host/email in the output'], 'source': 'rules'}
- **EV-A036**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review FAILED by rules: ['raw IP/user/host/email in the output'] → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A037**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A038**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review FAILED by llm reviewer: ['Missing defensive/remediation guidance. The review does not provide mitigations or containment steps for privilege escalation (e.g., verify legitimacy of SeDebugPrivilege, audit privilege grants, restrict privileges on hosts, monitor/suppress anomalous logons).', 'Potential factual error: MITRE ATT&CK mapping cited as T1484 without a handbook stable_id or a verifie → review problems: {'problems': ['Missing defensive/remediation guidance. The review does not provide mitigations or containment steps for privilege escalation (e.g., verify legitimacy of SeDebugPrivilege, audit privilege grants, restrict privileges on hosts, monitor/suppress anomalous logons).', 'Potential factual error: MITRE ATT&CK mapping cited as T1484 without a handbook stable_id or a verified
- **EV-A039**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review FAILED by llm reviewer: ['Contains step-by-step host-level triage commands (e.g., Get-WinEvent, sc qc, Get-CimInstance) which constitutes actionable operational guidance and should not be included in a review draft.'] → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A040**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → review ok
