# VERIFY — 09 docker
**Status:** filled by Claude, 2026-11-12, session 2 · images verified in CI · the local `make up` is Naveed's (R8)

## Image builds + Trivy (CI)
GitHub Actions run 43228002776 → `success`:
```
image wazuh-mcp (build + Trivy): success
image api-gateway (build + Trivy): success
image enrichment-mcp (build + Trivy): success
image agent-service (build + Trivy): success
```

## Hardening (see `spec.md`)
- multi-stage uv images
- non-root user
- read-only containers
- healthchecks
- per-service secrets in compose
- one published port (the gateway, :8000)
- the MCP allowed-hosts are set for the container network

## Not done (needs Naveed)
**R8.** Docker is not installed in this WSL distro. Steps:
1. Docker Desktop → Settings → Resources → WSL integration: turn it on for this distro.
2. Then run `make up`, then `make demo-up`, then `make down`.
