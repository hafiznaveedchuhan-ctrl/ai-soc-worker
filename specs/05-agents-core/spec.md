# spec — 05 agents-core (as built) · package `services/agent-service` (`agent_service`)
| Primitive / requirement | Where | Test |
|---|---|---|
| Agents: triage_agent (/ask router), triage_coordinator (/triage), soc_handbook_agent, cyber_research_agent, scope_classifier, note_reviewer | `agents_build.py` | all flow tests |
| `@function_tool` (schemas from type hints + docstrings): search_handbook, get_alert, ip_reputation, web_search, create_escalation_ticket, write_ksor_suggestion | `tools.py` | flow tests |
| `output_type` structured output: TriageNote, AskAnswer, ScopeVerdict, ReviewVerdict | `agents_build.py` | `test_triage_as_tool_flow_with_approval` |
| `handoff()` (/ask) vs `Agent.as_tool()` (/triage, coordinator keeps control) | `agents_build.py` | `test_ask_handoff…`, triage tests |
| dynamic instructions routing on the Scope Guard verdict | `_route` | `test_ask_handoff…` |
| `needs_approval=True` MOCK ticket → interruptions → `RunState.approve/reject` | `tools.py`, `flows.run_triage` | approval + rejection tests |
| Sessions: SQLiteSession per conversation (/ask), fresh per alert (/triage) | `flows.py`, ADR-0008 | `test_session_keeps_conversation` |
| `RunContextWrapper[WorkerContext]` (mask map, budget, user, request, seen stable_ids/URLs) | `context.py` | all |
| `RunHooks` cost + budget (also for guardrail-internal runs) | `hooks.py`, `budget.py` | `test_budget_guard_stops_the_run` |
| Tracing: one trace per request, custom spans (ksor_search, wazuh_get_alert, enrichment_ip_reputation, web_search), `trace_include_sensitive_data=False` | `flows.py`, `tools.py`, ADR-0007 | `test_no_raw_ip_in_any_trace_or_span` |
| `Runner.run` / `Runner.run_streamed` | `flows.py` | `test_streaming_yields_final_answer` |
| `max_turns` + `MaxTurnsExceeded` → safe result | `flows.py` | `test_max_turns` |
| per-agent model routing (`AGENT_MODEL_<AGENT>`, default gpt-5-nano) | `settings.py`, ADR-0003 | settings + demo |
| Ports: MCP clients to wazuh-mcp / enrichment-mcp / KSOR; Tavily (ADR-0004) | `deps.py` | flow tests (in-memory servers) |
| CLI demos fake/live | `scripts/demo_agents.py` | CI runs fake mode |
