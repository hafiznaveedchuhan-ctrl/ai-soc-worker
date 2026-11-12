# plan — 04 handbook-client
Status: **approved** (human:naveed, 2026-11-12)

## Docs checked (2026-11-12)
| Item | Source | Confirmed |
|---|---|---|
| KSOR tool contract | `../handbook/system/gateways/content.ts` + `node_modules/@panaversity/ksor/dist/gateway-api-*.mjs` (read only) | tool names search/read/outline; SEARCH_OUTPUT/READ_OUTPUT/OUTLINE_OUTPUT fields; GATE = "off" or {floor}; reason ∈ abstained/unavailable/unpublished; k max = MAX_SEARCH_K |
| MCP client | mcp 2.3.0 (`mcp.Client(url)` streamable HTTP; `Client(server)` in memory) — checked in feature 03 | `call_tool(name, args)` → `structured_content`, `is_error` |

## Design
`models.py` (wire models) · `client.py` (`KsorClient`, `SearchOutcome`, `not_in_record`) · `testing.py` (`build_fake_ksor()` — an in-memory MCPServer with the same tools, used by tests and by feature 05 tests) · `scripts/demo_handbook.py`.
The client takes either a URL or an MCPServer object (for in-memory tests).

## Note for feature 05
The SOC Handbook Agent will attach the handbook as `MCPServerStreamableHttp` (Agents SDK). This client is for code paths
(evals, the triage tool code, guardrails) and is the single place that knows the KSOR wire shape.
