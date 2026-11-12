# plan — 03 mcp-services
Status: **approved** (human:naveed, 2026-11-12) · Spec: `./spec.md`

## Docs checked (2026-11-12)
| Library | Version | Source | Confirmed |
|---|---|---|---|
| MCP Python SDK | 2.3.0 | Context7 `/modelcontextprotocol/python-sdk/v2.3.0` | `from mcp.server.mcpserver import MCPServer` (FastMCP renamed); `@mcp.tool()` decorators unchanged; model returns → `structured_content`; in-memory `Client(server)` for tests; `run(transport="streamable-http", host, port)`; `ToolError` in `mcp.server.mcpserver.exceptions` |
| openai-agents | 0.24.0 | `uv pip compile` with mcp | resolves together with mcp 2.3.0 (needed in feature 05) |
| AbuseIPDB API v2 | — | Context7 `/websites/abuseipdb` (docs.abuseipdb.com) | `GET /api/v2/check`, headers `Key` + `Accept`, params `ipAddress`, `maxAgeInDays`; 429 + `Retry-After`; free check quota 1,000/day |
| httpx | (from mcp) | package docs | `AsyncClient(transport=httpx.MockTransport(handler))` for tests |

## Design
- Each server = `server.py` (builds `MCPServer`, registers tools from a factory so tests inject fakes), `settings.py`, `__main__.py`.
- wazuh-mcp: `sources.py` (FixtureSource/LiveSource); tool functions call `source.get(id)` / `source.since(...)`.
- enrichment-mcp: `abuseipdb.py` (async client, response model, errors), `cache.py` (TTL cache + daily budget with an injected clock), `bands.py`.
- Servers are built by `build_server(settings, deps)` so tests and the demo use in-memory clients; `__main__` uses real settings.

## Risks
mcp v2 API details (annotation kwargs) → confirmed by introspection in T03-01 · AbuseIPDB field drift → schema validation with `extra="ignore"` and optional fields.
