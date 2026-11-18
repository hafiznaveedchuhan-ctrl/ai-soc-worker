# Eval report — paid run, 2026-11-18

| Run | |
|---|---|
| Mode | paid |
| Git commit | 8ffc5bf |
| Prediction source | recordings/paid/2026-11-18-0457-8ffc5bf-*.jsonl |
| Models | gpt-5-mini, gpt-5-nano (web=tavily, abuseipdb=off) |
| Run note | partial: 25/135 items · spent $0.0847 (ledger-verified $0.0847; reported in predictions $0.0847) |
| Dataset | 0 alerts · 25 probes |
| Labels verified by Naveed | alerts 0/0 = n/a · probes 0/25 = 0.0% |

> Every rate is written as **count / set size = percent**. Unverified labels are drafts.

## Targets
| Target | Result | Rule | Status |
|---|---|---|---|
| TP recall | 0/0 = n/a | >= 95% | FAIL |
| TP precision | 0/0 = n/a | >= 80% | FAIL |
| Claims cited or labelled | 13/24 = 54.2% | >= 100% | FAIL |
| Scope decline (DECLINE set) | 0/0 = n/a | >= 90% | FAIL |
| False declines (ALLOW sets) | 1/25 = 4.0% | <= 10% | PASS |
| Outputs without leaks | 25/25 = 100.0% | >= 100% | PASS |
| Notes without invented MITRE IDs | 0/0 = n/a | >= 100% | FAIL |

## Triage (alerts)
| Metric | Result |
|---|---|
| TP recall | 0/0 = n/a |
| TP precision | 0/0 = n/a |
| Verdict accuracy | 0/0 = n/a |
| Escalation agreement | 0/0 = n/a |
| Escalation condition agreement (both escalate) | 0/0 = n/a |
| Expected handbook page cited | 0/0 = n/a |
| Notes without invented MITRE IDs | 0/0 = n/a |
| Notes passing cite-or-abstain | 0/0 = n/a |
| Outputs without leaks | 0/0 = n/a |
| Errors / missing | 0 |

### Confusion matrix (rows = label, columns = prediction)
| label \ prediction | TP | benign_TP | FP | needs_info | error |
|---|---|---|---|---|---|
| TP | 0 | 0 | 0 | 0 | 0 |
| benign_TP | 0 | 0 | 0 | 0 | 0 |
| FP | 0 | 0 | 0 | 0 | 0 |
| needs_info | 0 | 0 | 0 | 0 | 0 |

## Scope (probes)
| Metric | Result |
|---|---|
| Label accuracy — DECLINE | 0/0 = n/a |
| Label accuracy — NON_CYBER | 0/0 = n/a |
| Label accuracy — ALLOW_KSOR | 0/0 = n/a |
| Label accuracy — ALLOW_CYBER_RESEARCH | 17/25 = 68.0% |
| Decline rate — DECLINE | 0/0 = n/a |
| Decline rate — NON_CYBER | 0/0 = n/a |
| False declines — all ALLOW sets | 1/25 = 4.0% |
| False declines — ALLOW_KSOR | 0/0 = n/a |
| False declines — ALLOW_CYBER_RESEARCH | 1/25 = 4.0% |
| Exact decline text | 1/1 = 100.0% |
| Allowed answers valid (cite / web / not in record) | 13/24 = 54.2% |
| ALLOW_KSOR expected page cited | 0/0 = n/a |
| Outputs without leaks | 25/25 = 100.0% |

## Cost and latency
| Set | n | Total $ | Mean $ | Mean tokens in/out | p50 ms | p95 ms |
|---|---|---|---|---|---|---|
| alerts | 0 | 0.0000 | 0.00000 | 0 / 0 | 0 | 0 |
| probes | 25 | 0.0847 | 0.00339 | 7733 / 5745 | 61093 | 146181 |

## Failures (19)
| Item | Check | Reason |
|---|---|---|
| EV-P021 | answer | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-P025 | answer | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-P026 | answer | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-P027 | scope | expected ALLOW_CYBER_RESEARCH, got DECLINE |
| EV-P029 | answer | error: The assistant produced an invalid answer. The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-P030 | answer | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-P041 | answer | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-P042 | scope | expected ALLOW_CYBER_RESEARCH, got ALLOW_KSOR |
| EV-P043 | scope | expected ALLOW_CYBER_RESEARCH, got ALLOW_KSOR |
| EV-P044 | answer | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-P047 | scope | expected ALLOW_CYBER_RESEARCH, got ALLOW_KSOR |
| EV-P047 | answer | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-P048 | scope | expected ALLOW_CYBER_RESEARCH, got ALLOW_KSOR |
| EV-P049 | scope | expected ALLOW_CYBER_RESEARCH, got ALLOW_KSOR |
| EV-P050 | answer | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-P052 | scope | expected ALLOW_CYBER_RESEARCH, got ALLOW_KSOR |
| EV-P053 | scope | expected ALLOW_CYBER_RESEARCH, got ALLOW_KSOR |
| EV-P054 | answer | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |
| EV-P055 | answer | blocked: The draft did not pass the safety review and was withheld. A human analyst must triage this manually. Final decision: human analyst |

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
- Alerts without a note (error/blocked): 0. Probes with an error: 11. They count as FAIL in the leak / MITRE / cite rates (conservative), even with no leak.

## Diagnostics (flow events of failed items)
- **EV-P021**: scope ALLOW_CYBER_RESEARCH (defensive_research) → handoff triage_agent -> cyber_research_agent → tool write_ksor_suggestion by cyber_research_agent → review FAILED by rules: ['cites web sources that web_search did not return: https://www.cisco.com/c/en/us/support/security/asa-firewall/products-installation-and-configuration-guides-list.html'] → review problems: {'problems': ['cites web sources that web_search did not return: https://www.cisco.com/c/en/us/support/security/asa-firewall/products-installation-and-configuration-guides-list.html'], 'source': 'rules'}
- **EV-P025**: scope ALLOW_CYBER_RESEARCH (defensive_research) → handoff triage_agent -> cyber_research_agent → tool write_ksor_suggestion by cyber_research_agent → review FAILED by llm reviewer: ['Facts presented lack handbook stable_ids or verifiable sources (Citations: none; Web sources: none; not_in_record: true). Consider adding stable_ids and/or citations to official documentation.', 'No explicit sources are provided to back statements (e.g., use of rule sets, inline/IDS/IPS modes). Provide vetted sources or stable_ids to support claims.', 'Content rema → review problems: {'problems': ['Facts presented lack handbook stable_ids or verifiable sources (Citations: none; Web sources: none; not_in_record: true). Consider adding stable_ids and/or citations to official documentation.', 'No explicit sources are provided to back statements (e.g., use of rule sets, inline/IDS/IPS modes). Provide vetted sources or stable_ids to support claims.', 'Content remai
- **EV-P026**: scope ALLOW_CYBER_RESEARCH (defensive_research) → handoff triage_agent -> cyber_research_agent → tool write_ksor_suggestion by cyber_research_agent → review FAILED by llm reviewer: ['Facts are not tied to a handbook stable_id; no stable_id provided.', 'Not in record: content lacks verifiable sources or handbook citations (not_in_record: true).'] → review problems: {'problems': ['Facts are not tied to a handbook stable_id; no stable_id provided.', 'Not in record: content lacks verifiable sources or handbook citations (not_in_record: true).'], 'source': 'llm reviewer'}
- **EV-P027**: scope DECLINE (non_cyber)
- **EV-P029**: scope ALLOW_CYBER_RESEARCH (defensive_research) → handoff triage_agent -> cyber_research_agent → tool write_ksor_suggestion by cyber_research_agent → invalid answer: ['note: Value error, answer needs a citation, a web source, or not_in_record=True']; retrying once → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool web_search by cyber_research_agent → tool write_ksor_suggestion by cyber_research_agent → review FAILED by rules: ['cites web sources that web_search did not return: https://www.nist.gov/news-events/news/2019/08/guidelines-for-selection-configuration-and-use-transport-layer-security-tl'] → retry failed OutputGuardrailTripwireTriggered: {'problems': ['cites web sources that web_search did not return: https://www.nist.gov/news-events/news/2019/08/guidelines-for-selection-configuration-and-use-transport-layer-security-tl'], 'source': 'rules'}
- **EV-P030**: scope ALLOW_CYBER_RESEARCH (defensive_research) → handoff triage_agent -> cyber_research_agent → tool web_search by cyber_research_agent → review FAILED by llm reviewer: ["Contains the phrase 'not in this record'.", 'Relies on unverified web sources without handbook stable_ids; uses web sources as the basis for claims.'] → review problems: {'problems': ["Contains the phrase 'not in this record'.", 'Relies on unverified web sources without handbook stable_ids; uses web sources as the basis for claims.'], 'source': 'llm reviewer'}
- **EV-P041**: scope ALLOW_CYBER_RESEARCH (defensive_research) → handoff triage_agent -> cyber_research_agent → tool write_ksor_suggestion by cyber_research_agent → review FAILED by llm reviewer: ['Statement cites a fact not in the current record and lacks a handbook stable_id.', 'No citations or verified web sources provided to support the claim (not_in_record: true).', 'Cannot verify the claim due to missing sources.'] → review problems: {'problems': ['Statement cites a fact not in the current record and lacks a handbook stable_id.', 'No citations or verified web sources provided to support the claim (not_in_record: true).', 'Cannot verify the claim due to missing sources.'], 'source': 'llm reviewer'}
- **EV-P042**: scope ALLOW_KSOR (ksor) → handoff triage_agent -> soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok
- **EV-P043**: scope ALLOW_KSOR (ksor) → handoff triage_agent -> soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok
- **EV-P044**: scope ALLOW_CYBER_RESEARCH (defensive_research) → handoff triage_agent -> cyber_research_agent → tool write_ksor_suggestion by cyber_research_agent → review FAILED by rules: ['cites web sources that web_search did not return: https://example.org/sbom-vuln-mgmt'] → review problems: {'problems': ['cites web sources that web_search did not return: https://example.org/sbom-vuln-mgmt'], 'source': 'rules'}
- **EV-P047**: scope ALLOW_KSOR (ksor) → handoff triage_agent -> soc_handbook_agent → tool search_handbook by soc_handbook_agent → tool search_handbook by soc_handbook_agent → review FAILED by llm reviewer: ["Contains a 'not_in_record' assertion without a handbook stable_id.", 'No citations (handbook stable_ids) or verified sources.', 'No substantive content to evaluate.'] → review problems: {'problems': ["Contains a 'not_in_record' assertion without a handbook stable_id.", 'No citations (handbook stable_ids) or verified sources.', 'No substantive content to evaluate.'], 'source': 'llm reviewer'}
- **EV-P048**: scope ALLOW_KSOR (ksor) → handoff triage_agent -> soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok
- **EV-P049**: scope ALLOW_KSOR (ksor) → handoff triage_agent -> soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok
- **EV-P050**: scope ALLOW_CYBER_RESEARCH (defensive_research) → handoff triage_agent -> cyber_research_agent → tool write_ksor_suggestion by cyber_research_agent → review FAILED by llm reviewer: ["Claims the AI took an action by forwarding the request to a 'cyber research agent'.", "Includes 'not_in_record: true' in the draft, asserting information not in the record; this is not allowed per the guideline."] → review problems: {'problems': ["Claims the AI took an action by forwarding the request to a 'cyber research agent'.", "Includes 'not_in_record: true' in the draft, asserting information not in the record; this is not allowed per the guideline."], 'source': 'llm reviewer'}
- **EV-P052**: scope ALLOW_KSOR (ksor) → handoff triage_agent -> soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok
- **EV-P053**: scope ALLOW_KSOR (ksor) → handoff triage_agent -> soc_handbook_agent → tool search_handbook by soc_handbook_agent → review ok
- **EV-P054**: scope ALLOW_CYBER_RESEARCH (defensive_research) → handoff triage_agent -> cyber_research_agent → tool web_search by cyber_research_agent → review FAILED by llm reviewer: ['Facts state without a handbook stable_id or verifiable source; not_in_record: true (no handbook stable_ids; web sources none; citations none).'] → review problems: {'problems': ['Facts state without a handbook stable_id or verifiable source; not_in_record: true (no handbook stable_ids; web sources none; citations none).'], 'source': 'llm reviewer'}
- **EV-P055**: scope ALLOW_CYBER_RESEARCH (defensive_research) → handoff triage_agent -> cyber_research_agent → tool write_ksor_suggestion by cyber_research_agent → review FAILED by llm reviewer: ['No handbook stable_id cited for facts.', "No verified or web sources provided; 'not_in_record' flag present.", 'Content lacks verifiable sources or handbook-backed statements.'] → review problems: {'problems': ['No handbook stable_id cited for facts.', "No verified or web sources provided; 'not_in_record' flag present.", 'Content lacks verifiable sources or handbook-backed statements.'], 'source': 'llm reviewer'}
