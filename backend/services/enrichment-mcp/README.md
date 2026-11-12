# enrichment-mcp

**Backend part:** threat-intel enrichment — a read-only MCP server with one tool, `ip_reputation(ip)`, backed by the
AbuseIPDB v2 CHECK endpoint (free tier: 1,000 checks a day). It is the **only** service that holds `ABUSEIPDB_API_KEY`.

Rules it enforces itself (defence in depth; the agent's tool guardrail in 06 checks again):
- Only **public** IPs are sent. Private (RFC 1918, fc00::/7), loopback, link-local, multicast, CGNAT, documentation and
  invalid inputs return `status="not_queried"` with the reason; no request is made.
- A TTL cache (24 h), so a repeated lookup costs nothing. A daily budget (900) stays under the free quota.
- Every failure (no key, 401/403, 429 + `Retry-After`, 5xx, timeout, unexpected JSON) is returned as `status="error"` + `reason`, never a crash.
- `handbook_band` follows the handbook IP-reputation policy: 0 none · 1–24 low · 25–74 suspicious · 75–100 likely_malicious.
- Logs never contain the IP: they carry the class and an 8-character hash, and the httpx URL logging is silenced.

**Run alone (from `backend/`):** `make serve-enrichment-mcp` → `http://127.0.0.1:8102/mcp` · tests: `uv run pytest services/enrichment-mcp` ·
one real lookup (needs the key in `backend/.env` and your permission): `make demo-enrichment-live IP=<public ip> CONFIRM=haan`

| Env var | Default | Meaning |
|---|---|---|
| `ABUSEIPDB_API_KEY` | — | your AbuseIPDB key (secret) |
| `ENRICH_MAX_AGE_DAYS` | 90 | report window sent as `maxAgeInDays` |
| `ENRICH_CACHE_TTL_SECONDS` | 86400 | cache lifetime |
| `ENRICH_DAILY_BUDGET` | 900 | max live requests per UTC day |
| `ENRICH_TIMEOUT_SECONDS` | 10 | HTTP timeout |
| `ENRICH_HOST` / `ENRICH_PORT` | `127.0.0.1` / `8102` | listen address |
