# spec — 03 mcp-services
Status: **approved** (human:naveed, 2026-11-12) · Intent: `./INTENT.md`

## 1. wazuh-mcp (`backend/services/wazuh-mcp`, package `wazuh_mcp`)
| ID | Requirement | Acceptance |
|---|---|---|
| FR-03-01 | Settings `WazuhMcpSettings` (prefix `WAZUH_`): `mode` (`fixture`\|`live`, default fixture), `fixtures_dir` (default `backend/evals/data/alerts`), `host`, `port` (8101). | Settings tests (monkeypatch). |
| FR-03-02 | `AlertSource` protocol; `FixtureSource` loads every `*.json` as `WazuhAlert` once at start; `LiveSource` raises `NotImplementedError("live mode arrives after Phase 1 B/C")`. | Tests. |
| FR-03-03 | Tool `get_alert(alert_id)`: `alert_id` ≤ 64 chars, `[A-Za-z0-9._-]`; returns the alert JSON (structured); unknown id → tool error "alert not found". | In-memory client tests. |
| FR-03-04 | Tool `get_new_alerts(since, min_level=3, limit=20)`: `since` ISO-8601 datetime; `min_level` 0–15; `limit` 1–100; returns summaries (`id, timestamp, rule_id, rule_level, rule_description, agent_name`) sorted by time, newest last. | Tests (filtering, ordering, caps). |
| FR-03-05 | Exactly these 2 tools; both annotated read-only (`read_only_hint=True`, `destructive_hint=False`). | Test lists the tools. |
| FR-03-06 | `python -m wazuh_mcp` serves streamable HTTP at `http://127.0.0.1:8101/mcp`. | Manual (VERIFY). |

## 2. enrichment-mcp (`backend/services/enrichment-mcp`, package `enrichment_mcp`)
| ID | Requirement | Acceptance |
|---|---|---|
| FR-03-10 | Settings `EnrichmentSettings`: `ABUSEIPDB_API_KEY` (SecretStr, optional), `ENRICH_MAX_AGE_DAYS` (90), `ENRICH_CACHE_TTL_SECONDS` (86400), `ENRICH_DAILY_BUDGET` (900, below the free 1,000/day), `ENRICH_TIMEOUT_SECONDS` (10), host/port (8102). | Tests. |
| FR-03-11 | Tool `ip_reputation(ip)` returns `IpReputationResult(ip_class, is_public, status: ok\|not_queried\|error, abuse_confidence_score, total_reports, num_distinct_users, country_code, usage_type, last_reported_at, cached, reason, handbook_band)`. | Tests. |
| FR-03-12 | Non-public or invalid IPs → `status=not_queried`, reason names the class (e.g. `private 10.0.0.0/8`), **no HTTP request**. | A test over every special range asserts 0 requests. |
| FR-03-13 | HTTP: `GET https://api.abuseipdb.com/api/v2/check?ipAddress=<ip>&maxAgeInDays=<n>` with headers `Key`, `Accept: application/json` (AbuseIPDB docs, Context7). The response is validated with a Pydantic model; a schema mismatch → `status=error, reason="unexpected response schema"`. | MockTransport tests. |
| FR-03-14 | Errors never crash the tool: missing key → `error "ABUSEIPDB_API_KEY not configured"` (no request); 429 → `error "rate limited"` + `retry_after`; timeout / 5xx → `error`. | Tests. |
| FR-03-15 | Cache: an in-memory TTL cache per IP; a hit → `cached=true`, 0 requests. Daily budget: after `ENRICH_DAILY_BUDGET` live requests in a UTC day → `error "daily budget reached"` (no request). | Tests (with an injected clock). |
| FR-03-16 | `handbook_band` follows `knowledge/enrichment/ip-reputation-policy`: 0 → `none`, 1–24 → `low`, 25–74 → `suspicious`, 75–100 → `likely_malicious`. | Tests at each edge. |
| FR-03-17 | Exactly 1 tool, read-only (`read_only_hint=True`, `open_world_hint=True`). Logs never contain the raw IP (class + a short hash only). | Tests (tool list; caplog). |
| FR-03-18 | `python -m enrichment_mcp` serves streamable HTTP at `http://127.0.0.1:8102/mcp`. | Manual. |

## 3. Demo and tooling
| ID | Requirement | Acceptance |
|---|---|---|
| FR-03-20 | `make demo-mcp`: in-memory clients for both servers, prints 5 newest alerts ≥ level 10, one full alert id, and reputation for a private, a documentation and a (mocked) public IP. Offline and free. | Runs in CI. |
| FR-03-21 | `make serve-wazuh-mcp`, `make serve-enrichment-mcp` start the HTTP servers. `make demo-enrichment-live IP=<public ip>` makes ONE real AbuseIPDB call — only after Naveed's "haan". | Manual. |
| FR-03-22 | Workspace members gain `services/*`; each service has its own README (what, backend part, how to run alone, env vars). | Review. |

## 4. Non-functional
NFR-03-01 offline tests (pytest-socket; httpx MockTransport) · NFR-03-02 mypy --strict, ruff · NFR-03-03 coverage ≥ 85% per service.
