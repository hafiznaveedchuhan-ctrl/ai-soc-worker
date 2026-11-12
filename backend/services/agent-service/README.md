# agent-service

**Backend part:** the AI brain (internal only). OpenAI Agents SDK 0.24.0: 6 agents, both flows, all four guardrail kinds, sessions,
hooks (cost + budget), tracing (no sensitive data), streaming. HTTP API arrives in feature 07.

| File | What |
|---|---|
| `settings.py` | `AGENT_*` env: models (default gpt-5-nano), budgets, MCP URLs, `WEB_SEARCH_API_KEY` |
| `agents_build.py` | the agents and their wiring (handoffs, as_tool, guardrails, output types) |
| `flows.py` | `run_ask`, `run_ask_streamed`, `run_triage` (approvals) |
| `tools.py` · `guardrails.py` | function tools · the four guardrail kinds |
| `deps.py` | MCP clients (wazuh, enrichment, KSOR), Tavily, fakes |
| `budget.py` · `hooks.py` · `context.py` | cost accounting · RunHooks · WorkerContext |
| `testing.py` | offline wiring: ScriptedModel per agent + in-memory MCP servers |

Run: `make demo-ask`, `make demo-triage` (fake, free) · tests: `uv run pytest services/agent-service`.
Live: `make demo-ask LIVE=1 CONFIRM=haan Q="…"` (needs `OPENAI_API_KEY`; the handbook at `HANDBOOK_MCP_URL`).
