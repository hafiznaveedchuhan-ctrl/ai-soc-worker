# Eval report — paid run, 2026-11-18

| Run | |
|---|---|
| Mode | paid |
| Git commit | 12a8cf9 |
| Prediction source | recordings/paid/2026-11-18-0507-12a8cf9-*.jsonl |
| Models | gpt-5-mini, gpt-5-nano (web=tavily, abuseipdb=off) |
| Run note | partial: 40/135 items · spent $0.8424 (ledger-verified $0.8424; reported in predictions $0.8424) |
| Dataset | 40 alerts · 0 probes |
| Labels verified by Naveed | alerts 0/40 = 0.0% · probes 0/0 = n/a |

> Every rate is written as **count / set size = percent**. Unverified labels are drafts.

## Targets
| Target | Result | Rule | Status |
|---|---|---|---|
| TP recall | 8/21 = 38.1% | >= 95% | FAIL |
| TP precision | 8/10 = 80.0% | >= 80% | PASS |
| Claims cited or labelled | 31/40 = 77.5% | >= 100% | FAIL |
| Scope decline (DECLINE set) | 0/0 = n/a | >= 90% | FAIL |
| False declines (ALLOW sets) | 0/0 = n/a | <= 10% | FAIL |
| Outputs without leaks | 31/40 = 77.5% | >= 100% | FAIL |
| Notes without invented MITRE IDs | 31/40 = 77.5% | >= 100% | FAIL |

## Triage (alerts)
| Metric | Result |
|---|---|
| TP recall | 8/21 = 38.1% |
| TP precision | 8/10 = 80.0% |
| Verdict accuracy | 17/40 = 42.5% |
| Escalation agreement | 24/40 = 60.0% |
| Escalation condition agreement (both escalate) | 6/6 = 100.0% |
| Expected handbook page cited | 28/40 = 70.0% |
| Notes without invented MITRE IDs | 31/40 = 77.5% |
| Notes passing cite-or-abstain | 31/40 = 77.5% |
| Outputs without leaks | 31/40 = 77.5% |
| Errors / missing | 9 |

### Confusion matrix (rows = label, columns = prediction)
| label \ prediction | TP | benign_TP | FP | needs_info | error |
|---|---|---|---|---|---|
| TP | 8 | 0 | 0 | 8 | 5 |
| benign_TP | 1 | 7 | 0 | 2 | 1 |
| FP | 0 | 0 | 1 | 0 | 0 |
| needs_info | 1 | 0 | 2 | 1 | 3 |

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
| alerts | 40 | 0.8424 | 0.02106 | 47253 / 21893 | 211711 | 449731 |
| probes | 0 | 0.0000 | 0.00000 | 0 / 0 | 0 | 0 |

## Failures (38)
| Item | Check | Reason |
|---|---|---|
| EV-A001 | verdict | expected TP, got needs_info |
| EV-A002 | escalation | expected escalate=True, got False |
| EV-A003 | verdict | expected TP, got needs_info |
| EV-A004 | verdict | expected needs_info, got TP |
| EV-A004 | escalation | expected escalate=False, got True |
| EV-A005 | escalation | expected escalate=False, got True |
| EV-A006 | verdict | expected needs_info, got FP |
| EV-A010 | verdict | expected TP, got needs_info |
| EV-A011 | escalation | expected escalate=True, got False |
| EV-A012 | page_hit | no expected handbook page cited |
| EV-A013 | prediction | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A013 | tp_recall | TP missed (no note) |
| EV-A015 | prediction | error: The note broke the template rules twice. The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A015 | tp_recall | TP missed (no note) |
| EV-A016 | prediction | error: The note broke the template rules twice. The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A019 | verdict | expected needs_info, got FP |
| EV-A019 | escalation | expected escalate=True, got False |
| EV-A020 | verdict | expected TP, got needs_info |
| EV-A022 | prediction | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A023 | verdict | expected benign_TP, got needs_info |
| EV-A024 | verdict | expected benign_TP, got TP |
| EV-A025 | verdict | expected benign_TP, got needs_info |
| EV-A027 | escalation | expected escalate=False, got True |
| EV-A030 | prediction | error: The note broke the template rules twice. The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A031 | page_hit | no expected handbook page cited |
| EV-A032 | verdict | expected TP, got needs_info |
| EV-A033 | prediction | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A033 | tp_recall | TP missed (no note) |
| EV-A034 | verdict | expected TP, got needs_info |
| EV-A035 | prediction | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A035 | tp_recall | TP missed (no note) |
| EV-A036 | prediction | budget: Stopped: run budget exceeded ($0.0568 > $0.05). The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A036 | tp_recall | TP missed (no note) |
| EV-A037 | page_hit | no expected handbook page cited |
| EV-A038 | prediction | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-A039 | verdict | expected TP, got needs_info |
| EV-A039 | escalation | expected escalate=False, got True |
| EV-A040 | verdict | expected TP, got needs_info |

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
- Alerts without a note (error/blocked): 9. Probes with an error: 0. They count as FAIL in the leak / MITRE / cite rates (conservative), even with no leak.

## Diagnostics (flow events of failed items)
- **EV-A001**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A002**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A003**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → rejected create_escalation_ticket → review ok
- **EV-A004**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A005**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → rejected create_escalation_ticket → review ok
- **EV-A006**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A010**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A011**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review FAILED by rules: ['raw IP/user/host/email in the output', "cites pages KSOR did not return: ['knowledge/windows-events/when-windows-writes-it']"] → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review FAILED by llm reviewer: ["Inconsistent not_in_record flag: body states 'Not in this record' while not_in_record is false.", 'Mismatch between narrative claim and flag may cause record-keeping confusion.'] → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A012**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A013**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → invalid note: ["note: Value error, citation is not a KSOR stable_id: 'ask_handbook: not in this record'"] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → rejected create_escalation_ticket → review FAILED by rules: ["MITRE ids not in the alert or cited handbook pages: ['T1685.005']"] → review problems: {'problems': ["MITRE ids not in the alert or cited handbook pages: ['T1685.005']"], 'source': 'rules'}
- **EV-A015**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → invalid note: ["note: Value error, citation is not a KSOR stable_id: 'not in this record'"] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → invalid note: ["note: Value error, citation is not a KSOR stable_id: 'not in this record'"]
- **EV-A016**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → invalid note: ["note: Value error, citation is not a KSOR stable_id: 'not in this record (handbook playbook absent for this specific event lookup)'"] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → invalid note: ["note: Value error, citation is not a KSOR stable_id: 'not in this record (handbook playbook absent for this specific event lookup)'"]
- **EV-A019**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A020**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A022**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_research by triage_coordinator → tool web_search by cyber_research_agent → tool write_ksor_suggestion by cyber_research_agent → review ok → invalid note: ["note: Value error, citation is not a KSOR stable_id: 'unverified web source (https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4672)'"] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review FAILED by llm reviewer: ['MITRE ATT&CK mapping (T1484) is stated without an anchored handbook stable_id or a not_in_record label; verify against the current ATT&CK matrix or attach a stable_id/not_in_record tag.', "Evidence line 1 ends with '— source: not in this record', which is inconsistent with the rest of the cited sources and should be corrected."] → review problems: {'problems': ['MITRE ATT&CK mapping (T1484) is stated without an anchored handbook stable_id or a not_in_record label; verify against the current ATT&CK matrix or attach a stable_id/not_in_record tag.', "Evidence line 1 ends with '— source: not in this record', which is inconsistent with the rest of the cited sources and should be corrected."], 'source': 'llm reviewer'}
- **EV-A023**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review FAILED by rules: ["cites pages KSOR did not return: ['knowledge/windows-events/event-4624', 'knowledge/windows-events/event-4625']"] → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A024**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → invalid note: ["note: Value error, citation is not a KSOR stable_id: 'not in this record'"] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A025**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_research by triage_coordinator → tool web_search by cyber_research_agent → review ok → invalid note: ["note: Value error, citation is not a KSOR stable_id: 'https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4625'"] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A027**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → rejected create_escalation_ticket → review ok
- **EV-A030**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_research by triage_coordinator → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → review FAILED by rules: ['raw IP/user/host/email in the output', 'cites web sources that web_search did not return: https://documentation.wazuh.com/current/user-manual/ruleset/rules.html'] → tool ask_research by triage_coordinator → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → review ok → invalid note: ["note: Value error, citation is not a KSOR stable_id: 'https://attack.mitre.org/techniques/T1110'"] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → invalid note: ["note: Value error, citation is not a KSOR stable_id: 'not in this record'"]
- **EV-A031**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_research by triage_coordinator → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent
- **EV-A032**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review FAILED by rules: ["cites pages KSOR did not return: ['knowledge/linux-auth/ssh-invalid-user']"] → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_research by triage_coordinator → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → review ok → invalid note: ["note: Value error, citation is not a KSOR stable_id: 'not in this record'"] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A033**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_research by triage_coordinator → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → review ok → invalid note: ["note: Value error, citation is not a KSOR stable_id: 'handbook:knowledge/mitre/t1059-001-powershell'"] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent
- **EV-A034**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → rejected create_escalation_ticket → review ok
- **EV-A035**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review FAILED by rules: ['raw IP/user/host/email in the output'] → note failed the rules: ['raw IP/user/host/email in the output'] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → rejected create_escalation_ticket → review FAILED by rules: ['raw IP/user/host/email in the output'] → review problems: {'problems': ['raw IP/user/host/email in the output'], 'source': 'rules'}
- **EV-A036**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review FAILED by rules: ["cites pages KSOR did not return: ['knowledge/windows-events/event-4697']"] → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review FAILED by rules: ["cites pages KSOR did not return: ['knowledge/windows-events/event-4697']"] → tool ask_research by triage_coordinator → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → review ok → invalid note: ["note: Value error, citation is not a KSOR stable_id: 'https://learn.microsoft.com/en-us/answers/questions/621426/psexec-told-couldnt-install-psexesvc-service'"] → retrying once with the rule messages → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator
- **EV-A037**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review FAILED by llm reviewer: ["Typo/incorrect event code in Condition 4: mentions 'a 4624 for the same account ... within 60 minutes after 8+ failures (or after a 60204 event)'. There is no standard Windows event 60204; this should reference a known event (e.g., 4625 or explicit credentials events like 4648) or be clearly explained. This fact is not backed by a handbook stable_id in the record." → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review FAILED by llm reviewer: ["Typo in Condition 4: '60204' is not a valid Windows event ID; likely intended to reference 4625 (failed logon) or clarify the exact pattern. Please verify and correct."] → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review ok
- **EV-A038**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → review FAILED by llm reviewer: ["MITRE ATT&CK mapping (T1484) is stated without a handbook stable_id, an 'unverified web source' label, or 'not in this record' indicator.", 'Escalate: no is inconsistent with the Final decision: human analyst (escalation expectation is unclear).'] → review problems: {'problems': ["MITRE ATT&CK mapping (T1484) is stated without a handbook stable_id, an 'unverified web source' label, or 'not in this record' indicator.", 'Escalate: no is inconsistent with the Final decision: human analyst (escalation expectation is unclear).'], 'source': 'llm reviewer'}
- **EV-A039**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → rejected create_escalation_ticket → review ok
- **EV-A040**: tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → tool ask_handbook by triage_coordinator → tool search_handbook by soc_handbook_agent → review ok → review ok
