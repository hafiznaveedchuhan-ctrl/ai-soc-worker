# 08 api-gateway — INTENT/spec/plan/tasks/VERIFY (compact) · Status: **implemented** (blanket approval; PHR-0012)
Public FastAPI (`services/api-gateway`): Auth0 JWT/JWKS or dev auth, roles analyst/admin, per-user rate limit (20/min), CORS for the handbook
origin, SQLModel + Alembic (Neon `soc_worker`; SQLite in tests), Fernet-encrypted `mask_map`, audit + usage persistence, global $9 budget (402).
Docs checked: PyJWT 2.15 (`PyJWKClient`, `jwt.decode` audience/issuer), SQLModel 0.0.49, Alembic 1.20, FastAPI SSE (Context7), cryptography Fernet.

| Route | Who | What |
|---|---|---|
| `GET /health`, `GET /ready` (DB + agent-service) | anyone | liveness / readiness |
| `GET /me` | logged in | user row (upserted from the token) |
| `POST /ask` {question, conversation_id?} (SSE: status → final → done) | analyst/admin | calls agent `/v1/ask`, stores usage + encrypted mask map + audit, returns the answer **unmasked for the human** |
| `POST /triage/{alert_id}` {analyst_context, approve_escalation_ticket} | analyst/admin | stores the MASKED note; returns it unmasked |
| `GET /notes`, `GET /notes/{id}` | own notes (admin: all) | list / detail with decisions |
| `POST /notes/{id}/decision` {approve\|change\|escalate, comment} | analyst/admin | the human decision + audit |
Tables (Alembic `08999efb4189`): users, conversations, alerts_seen, triage_notes, decisions, audit_log, llm_usage, mask_map.
Widget contract: `GET /openapi.json` on the running gateway; examples: `curl -N -X POST localhost:8000/ask -H "X-Dev-User: naveed:analyst" -H "Content-Type: application/json" -d '{"question":"What does event 4625 mean?"}'`.
**Tests (10):** health/me/ready; ask SSE persists usage + encrypted mask map (no clear value at rest); triage → note → decision → detail, other user 404, admin 200;
validation; rate limit 429; dev auth refused in production; real RS256 JWT path; 403 for another user's conversation; 402 budget; Alembic upgrade + `check` = models.
**Bugs found:** errors raised inside an SSE generator never became HTTP status codes → checks moved to a pre-stream dependency; Alembic's
`fileConfig` disabled every other logger in the process → `disable_existing_loggers=False`.
**Naveed (needs "haan"):** `make db-upgrade CONFIRM=haan` (Neon) · Auth0 per AUTH0-SETUP.md.
