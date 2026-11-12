# PHR-0012 — "Finish all coding first, LLM testing later"; features 05 + 06 built offline
- Date: 2026-11-12 · Session: 1 · Stage: implement · Features: 05, 06 (then 07–10) · Model: claude-opus-5-5

## Prompt (verbatim)
"MA CHTA HU PHLA CODING KA COMPLETE KAM KRLO JO REMAINING RHGYJA PHR LLM TESTING KRNA"

## Response summary
- Built every remaining feature with NO live LLM call. Agents are tested with `agents.testing.ScriptedModel` (official SDK test double).
  Live modes exist behind `CONFIRM=haan`.
- **Checked first:**
  - openai-agents 0.24.0, by introspection plus Context7: Model, ScriptedModel, guardrail decorators, ToolGuardrailFunctionOutput,
    RunState approve/reject, SQLiteSession, trace/custom_span/TracingProcessor;
  - OpenAI pricing (gpt-5-nano $0.05/$0.40 per 1M);
  - Tavily /search (free 1,000 credits/month, `include_domains` restrict).
- **Feature 05:** agent-service (settings, budget + ledger, context, hooks, ports, tools, agents, flows, demos); ADR-0003/0004/0008.
- **Feature 06:** guardrails (all 4 kinds) and the mock needs_approval ticket; ADR-0006/0007.
- **Bugs caught by the tests:**
  - guardrail-internal agent runs were not priced;
  - in-memory SQLiteSession objects lost the history between runs.

## Follow-ups
Claude: features 07–10. Naveed: later, the live LLM test (`make demo-ask LIVE=1 CONFIRM=haan`), then the paid eval.
