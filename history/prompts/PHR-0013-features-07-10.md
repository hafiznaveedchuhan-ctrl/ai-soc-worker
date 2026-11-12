# PHR-0013 — Features 07–10 built (continuing PHR-0012: "code first, LLM later")
- Date: 2026-11-12 · Session: 1 · Stage: implement · Features: 07, 08, 09, 10 · Model: claude-opus-5-5

## Prompt
"continue" (after /context): continue the coding of PHR-0012.

## Response summary
- **07 agent-service API:** FastAPI 0.162 with SSE (`fastapi.sse`), `X-Internal-Token`, 7 tests.
- **08 api-gateway:**
  - Auth0 JWT/JWKS (PyJWT 2.15) + dev auth, roles, rate limit, CORS;
  - SQLModel + Alembic (8 tables), Fernet mask map, audit/usage, budget 402;
  - 10 end-to-end tests: gateway → ASGI → agent-service with ScriptedModel; real RS256 tokens;
  - ADR-0005 and the Auth0 guide.
- **09 Docker:** 4 Dockerfiles + compose. Docker is not installed in this WSL distro, so the images are built and scanned in CI.
- **10 CI/CD:** path filters, matrix image build + Trivy, gated manual release to GHCR, Azure placeholder.
- **Bugs found:**
  - SSE errors could not become HTTP status codes (fixed with a pre-stream dependency);
  - Alembic `fileConfig` disabled every app logger;
  - the uv bookworm image tag does not exist for 0.12.6 (trixie used instead);
  - MCP DNS-rebinding protection is off on 0.0.0.0 (MCP_ALLOWED_HOSTS added).
- Generated `AGENT_INTERNAL_TOKEN` into `backend/.env` without displaying it. The file was never read.

## Follow-ups (Naveed)
- Merge the PRs.
- When ready, the LLM tests, each with "haan":
  - `make demo-ask LIVE=1 CONFIRM=haan`;
  - `make demo-triage LIVE=1 CONFIRM=haan`;
  - the paid eval.
- `make db-upgrade CONFIRM=haan` (Neon), the Auth0 setup, and Docker Desktop WSL integration for `make up`.
