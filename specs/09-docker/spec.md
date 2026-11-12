# 09 docker — compact SDD · Status: **implemented**; images are built + Trivy-scanned in CI (no Docker inside this WSL distro)
Deliverables: `backend/services/<svc>/Dockerfile` ×4 (multi-stage uv 0.12.6 trixie → python:3.12-slim-trixie, non-root uid 10001, HEALTHCHECK,
exec CMD), `backend/.dockerignore`, `backend/compose.yaml` (network `soc`, only `127.0.0.1:8000` published, read_only + no-new-privileges,
per-service env), `soc_shared.mcp_security` (`MCP_ALLOWED_HOSTS`), make `docker-build / up / down / demo-up / trivy`. Docs: LEARNING §12.
Checked: uv image tags on ghcr.io (`0.12.6-python3.12-bookworm-slim` = 404, `0.12.6-python3.12-trixie-slim` = 200); mcp transport security source.
**VERIFY (Naveed, needs Docker Desktop WSL integration):** `make up` → `docker compose ps` all healthy → `make demo-up` (ask + triage through the
gateway; the agents then use REAL models → needs your "haan" and OPENAI_API_KEY) → `make down`. CI job `images` = build + Trivy per service.
