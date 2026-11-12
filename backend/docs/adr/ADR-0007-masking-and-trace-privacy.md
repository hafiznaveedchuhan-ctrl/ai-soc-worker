# ADR-0007 — Masking architecture and trace privacy
- Status: **Accepted** (blanket approval 2026-11-12; amendment A2) · Features 01, 05, 06
## Decision
- Raw values exist only in (a) tool CODE in agent-service (`get_alert` masks, `ip_reputation` unmasks a token just for the AbuseIPDB call)
  and (b) api-gateway, which stores the per-request `mask_map` encrypted (Fernet, `MASK_MAP_KEY`).
- The model, logs, traces and sessions see tokens only: the question is masked by code before `Runner.run`; alerts are masked before they
  become input; the triage input guardrail trips if any raw IP/email is still present.
- Traces: `RunConfig(trace_include_sensitive_data=False)` in every run + `OPENAI_AGENTS_TRACE_INCLUDE_SENSITIVE_DATA=0` in `.env.example`;
  production settings refuse `trace_include_sensitive_data=True`.
- Output guardrail rejects any output that contains a raw value from the mask map or an unmasked IP/email.
## Verification
`test_no_raw_ip_in_any_trace_or_span` registers a capturing `TracingProcessor`, runs a full triage, and asserts that no raw IP/user/host
appears in any exported trace or span; `test_triage_as_tool_flow_with_approval` asserts the model inputs contain tokens only.
