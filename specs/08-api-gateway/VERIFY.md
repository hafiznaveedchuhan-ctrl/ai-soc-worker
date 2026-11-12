# VERIFY — 08 api-gateway
**Status:** filled by Claude, 2026-11-12, session 2, from real output · awaiting Naveed's verification · Neon (R7) and Auth0 (R9) are Naveed's

## Tests (offline: SQLite, a locally generated RS256 key, a fake agent-service)
`uv run pytest services/api-gateway/tests -q` → `10 passed`

| Test | Proves |
|---|---|
| `test_health_and_me` | dev auth works; `/me` returns the user and the roles |
| `test_ask_stream_persists_usage_and_encrypted_mask_map` | usage is stored; the mask map is Fernet-encrypted at rest |
| `test_triage_note_decision_flow` | Approve / Change / Escalate are stored and audited (the human decides) |
| `test_invalid_decision_and_alert_id` | strict validation |
| `test_rate_limit` | rate limiting returns 429 |
| `test_dev_auth_forbidden_in_production` | dev auth cannot run when ENV=production |
| `test_auth0_jwt_validation` | real RS256 JWTs are checked: wrong audience, wrong issuer, expired and wrong-key tokens are all rejected |
| `test_ask_other_users_conversation_is_forbidden` | users cannot read each other's conversations |
| `test_budget_exhausted_returns_402` | the budget guard returns 402 |
| `test_alembic_migration_matches_models` | the Alembic migration equals the SQLModel models |

## Not done (needs Naveed)
- **R7** — `make db-upgrade CONFIRM=haan` (Neon). This creates the 8 tables in `soc_worker`.
- **R9** — an Auth0 tenant per `AUTH0-SETUP.md`, then `AUTH_MODE=auth0`.
