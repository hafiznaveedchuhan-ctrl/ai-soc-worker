# INTENT — 03 mcp-services
Status: **approved** by human:naveed 2026-11-12 ("continue plz and approved for all your permission") · Plan of record: `../00-final-plan.txt` §5, §10

## Goal
Two small, read-only MCP servers that the agents will call (from tool code in feature 05):
- **wazuh-mcp** (SIEM data access): `get_alert(alert_id)` and `get_new_alerts(since, min_level, limit)`, in **fixture mode** now
  (it serves the 40 eval alerts), with a LIVE mode reserved for a read-only indexer user after Phase 1 B/C.
- **enrichment-mcp** (threat intel): `ip_reputation(ip)` through the AbuseIPDB free tier, with a cache, a daily-quota guard and
  response-schema validation. It is the only service that holds `ABUSEIPDB_API_KEY`.

## Users
Feature 05 tool code (agent-service), Naveed (terminal demo), CI (tests).

## Constraints
- Read-only: no tool writes, deletes, blocks or changes anything. The tool list is fixed and tested.
- Only PUBLIC IPs are ever sent to AbuseIPDB (server-side check, as well as the guardrail in 06). Private, reserved and documentation IPs → "not_queried".
- No live AbuseIPDB call in tests or CI (an httpx mock transport). A live check needs the key in `.env` + Naveed's "haan" for that run.
- mcp 2.3.0 (`MCPServer`, the v2 API; checked in Context7), compatible with openai-agents 0.24.0 (resolved together).
- Raw IPs are never logged (the logs carry the IP class only).

## Success numbers
| # | Measure | Target |
|---|---|---|
| S1 | Tests for both servers | 100% pass, coverage ≥ 85% per service |
| S2 | wazuh-mcp serves the eval alerts | 40/40 alerts load; `get_alert` round-trips every one |
| S3 | Non-public IPs sent to AbuseIPDB | 0 (test over all RFC 1918 / special ranges) |
| S4 | Cache | the second lookup of an IP makes 0 HTTP calls |
| S5 | Tool surface | exactly 2 tools (wazuh) + 1 tool (enrichment), all `read_only_hint=True` |
| S6 | `make demo-mcp` | prints an alert summary list, one alert, and reputation results (mocked) |

## Out of scope
Masking (done in agent-service tool code, 05), guardrails (06), the HTTP API (07/08), Docker (09), live Wazuh.
