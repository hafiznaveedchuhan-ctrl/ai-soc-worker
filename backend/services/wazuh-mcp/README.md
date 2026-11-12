# wazuh-mcp

**Backend part:** SIEM data access — a read-only MCP server. Its only caller is agent-service tool code (feature 05),
which masks the alert before anything reaches a language model.

| Tool | Input | Output |
|---|---|---|
| `get_alert` | `alert_id` (≤ 64 chars, `[A-Za-z0-9._-]`) | the full Wazuh alert JSON |
| `get_new_alerts` | `since` (ISO 8601), `min_level` 0–15 (default 3), `limit` 1–100 (default 20) | `{count, alerts:[{id, timestamp, rule_id, rule_level, rule_description, agent_name}]}`, oldest first |

Both tools carry `read_only_hint=True`, `destructive_hint=False`. There is no write tool, and a test keeps it that way.

**Modes:** `fixture` (now) serves `backend/evals/data/alerts/*.json` (40 lab alerts). `live` is reserved for a read-only
Wazuh indexer user after Phase 1 B/C and raises `NotImplementedError` today.

**Run alone (from `backend/`):** `make serve-wazuh-mcp` → `http://127.0.0.1:8101/mcp` · tests: `uv run pytest services/wazuh-mcp`

| Env var | Default | Meaning |
|---|---|---|
| `WAZUH_MODE` | `fixture` | `fixture` \| `live` |
| `WAZUH_FIXTURES_DIR` | `backend/evals/data/alerts` | folder of alert JSON files |
| `WAZUH_HOST` / `WAZUH_PORT` | `127.0.0.1` / `8101` | listen address |
| `WAZUH_INDEXER_URL`, `WAZUH_INDEXER_USER`, `WAZUH_INDEXER_PASSWORD` | — | live mode later (read-only user) |
