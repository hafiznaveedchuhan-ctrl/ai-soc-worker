# ADR-0008 — Sessions: SQLiteSession now, Postgres-backed in Phase 8
- Status: **Accepted** (blanket approval 2026-11-12; amendment A3) · Feature 05
## Decision
`/ask`: one `SQLiteSession` per analyst conversation (`ask-<session_id>`), file `AGENT_SESSIONS_DB` in the agent-service container.
`/triage`: a fresh in-memory session per alert run (no cross-alert memory). Sessions hold masked text only.
## Consequences
Container restarts lose `/ask` history and several replicas would not share it → Phase 8 (Azure Container Apps, replicas) switches to a
Postgres/SQLAlchemy-backed session. In tests the in-memory sessions are cached per conversation (`FlowConfig.session`).
