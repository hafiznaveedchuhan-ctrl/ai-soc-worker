# api-gateway
**Backend part:** public API + auth + the ONLY database owner. See `../../../specs/08-api-gateway/spec.md` (routes, tables) and
`AUTH0-SETUP.md`. Run: `make serve-gateway` (:8000, dev auth) · migrations: `make db-upgrade CONFIRM=haan` · tests: `uv run pytest services/api-gateway`.
Env: `SOC_DB_URL`, `MASK_MAP_KEY`, `AUTH_MODE`, `AUTH0_DOMAIN`, `AUTH0_AUDIENCE`, `CORS_ORIGINS`, `AGENT_INTERNAL_TOKEN`, `GATEWAY_AGENT_URL`, `GATEWAY_RATE_LIMIT_PER_MINUTE`.
