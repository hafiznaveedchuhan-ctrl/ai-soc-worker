# VERIFY — 07 agent-service (internal API)
**Status:** filled by Claude, 2026-11-12, session 2, from real output · awaiting Naveed's verification

## Tests (offline, ASGITransport + ScriptedModel)
`uv run pytest services/agent-service/tests/test_api.py -q` → `7 passed`

| Test | Proves |
|---|---|
| `test_health_needs_no_token` | `/health` is open for container healthchecks |
| `test_token_required` | every other route needs the internal token (constant-time compare) |
| `test_ask_ok_returns_usage_and_mask_entries` | `/ask` returns the answer, the usage and the mask entries for the gateway |
| `test_ask_decline` | an off-scope question gets the exact decline text |
| `test_ask_stream_sse` | SSE streaming through `fastapi.sse` |
| `test_input_validation` | bad bodies are rejected with 422 |
| `test_triage_unknown_alert_is_error` | an unknown alert becomes a safe error, not a crash |

## Live evidence (session 2)
The same flows ran LIVE through `soc_evals paid` in pilots 2–4, with gpt-5-nano and the live handbook (feature 11, VERIFY §7–8).
The HTTP layer itself has not been run live; it runs only with `make serve-agent` or `make up` (R8).

## For Naveed
Optional: `make serve-agent` (PAID when called), or wait for `make up` (R8).
