# 07 agent-service API — INTENT/spec/plan/tasks/VERIFY (compact) · Status: **implemented** (blanket approval; PHR-0012)
**Goal:** expose the flows to api-gateway over an INTERNAL HTTP API. FastAPI 0.162.5 (SSE via `fastapi.sse.EventSourceResponse`,
checked in Context7 2026-11-12), uvicorn 0.54.

| Route | Auth | Behaviour |
|---|---|---|
| `GET /health` · `GET /ready` | none | liveness / readiness (web search configured?) |
| `POST /v1/ask` {question, user_id, session_id} | `X-Internal-Token` (constant-time compare) | `FlowResponse` (status, answer, text, usage, mask_entries, tickets, events, trace_id) |
| `POST /v1/ask/stream` | token | SSE: `delta` events, one `final` (AskAnswer JSON), `done` `[DONE]` |
| `POST /v1/triage` {alert_id, user_id, analyst_context, approve_escalation_ticket=false} | token | `FlowResponse` with the TriageNote; a proposed ticket is approved only if the analyst said so |

Input validation: ids by regex, lengths capped (422 on bad input). `python -m agent_service` needs `AGENT_INTERNAL_TOKEN` and real URLs; it uses
REAL models (paid) — only the gateway calls it.
**Tests (7, ASGITransport, ScriptedModel):** health, token required, ask ok (+ mask entries + usage), decline, SSE stream, validation, unknown alert.
**VERIFY:** `uv run pytest services/agent-service/tests/test_api.py` → 7 passed (Claude, 2026-11-12). Full stack demo: feature 09 `make up`.
