# spec — 06 guardrails (as built) · `agent_service/guardrails.py`
| Kind | Guardrail | Behaviour | Test |
|---|---|---|---|
| 1 INPUT | `scope_guard` (`run_in_parallel=False`) | rules pre-check (injection, offensive) → else Scope Classifier agent; DECLINE → tripwire → exact DECLINE_MESSAGE; **zero model/tool calls downstream** | `test_offensive…zero_model_calls`, `test_prompt_injection_declined`, `test_classifier_declines_non_cyber…` |
| 1 INPUT | `triage_input_guard` | never declines an alert; flags injected text; trips if any raw IP/email reached the input | covered by triage tests |
| 2 OUTPUT | `note_reviewer` (reflection) | deterministic: leaks, action claims, citations ⊆ pages KSOR returned, web URLs ⊆ returned, MITRE ⊆ alert ∪ cited MITRE pages, level ≥ 12 ⇒ escalate, condition 1 ⇒ level ≥ 12; then the LLM reviewer | `test_invented_citation_is_blocked`, `test_raw_ip_in_answer_is_blocked`, `test_triage_level12…`, `test_triage_invented_mitre…` |
| 3 TOOL INPUT | `ksor_query_guard`, `ip_token_guard`, `web_query_guard` | length/charset/PII; only `<IP-n>` tokens of PUBLIC IPs (else a correction message, not a crash); no alert data/secrets/offensive in web queries | `test_triage_as_tool…` (documentation IP corrected), `test_web_query_with_alert_data_is_rejected` |
| 4 TOOL OUTPUT | `web_output_guard`, `ip_output_guard` (+ in-code sanitising) | untrusted domains dropped, instruction-like text removed, size cap, URL kept; reputation schema-validated | `test_research_flow_web_untrusted_and_suggestion` |
| approval | `create_escalation_ticket(needs_approval=True)` MOCK | run pauses; approve → MOCK id; reject → nothing | approval + rejection tests |
