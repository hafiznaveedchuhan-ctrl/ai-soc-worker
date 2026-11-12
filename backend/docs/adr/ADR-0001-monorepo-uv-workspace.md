# ADR-0001 — Monorepo with a uv workspace; one folder, one Dockerfile and one image per service
- Status: **Accepted** (human:naveed, 2026-11-12 — plan v2 "approved")
- Date: 2026-11-12 · Feature: 01 · Deciders: human:naveed (approver), Claude (author)
- Related: PHR-0001, PHR-0003, plan v2 §5–6, spec FR-01-01…03

## Context
- The worker has four runtime parts with different trust levels: a public API that owns the database, an internal AI
  brain, a read-only SIEM adapter, and a threat-intel adapter that holds the only AbuseIPDB key.
- They share data contracts (WazuhAlert, TriageNote, …) and the masking engine. Two copies of those would drift — and a
  masking drift is a privacy bug.
- Naveed is learning microservices, Docker and CI for an AI Engineer role, and is the only developer.
- The repo started as a single `uv init` package (`src/soc_worker`), Python 3.12, uv 0.12.6.

## Options considered
1. **Single package, single image** — simplest; but there is no secret isolation (the AbuseIPDB key and DB URL would sit in
   the same process as the LLM agent), no per-service scaling, and it doesn't teach microservices.
2. **Polyrepo (one GitHub repo per service)** — strong isolation; but shared models must be published as a package,
   there are 4× the CI and PR overhead for one developer, and cross-service changes become multi-PR.
3. **Monorepo + uv workspace (chosen)** — one repo and one lockfile; `packages/soc-shared` is consumed by path
   (`workspace = true`); each service has its own `pyproject.toml`, Dockerfile and image; CI path filters build only what changed.

## Decision
One GitHub repo (`ai-soc-worker`). `backend/` is the uv workspace root with members `packages/*` and `services/*`.
Services: api-gateway, agent-service, wazuh-mcp, enrichment-mcp. A shared library: soc-shared. Each service → image `ai-soc/<service>:<git-sha>`.
The root `pyproject.toml` and `src/soc_worker/` scaffold are removed (amendment A7).

## Rationale
- One lockfile = the same dependency versions in every service and in CI (reproducible).
- The shared contracts and masking have one source of truth; changing them triggers the tests of every dependent service.
- Secret isolation by process: only enrichment-mcp gets `ABUSEIPDB_API_KEY`, only api-gateway gets the DB URL and the mask-map key,
  only agent-service gets `OPENAI_API_KEY`.
- It matches how platform teams ship Python microservices, which makes a strong portfolio point.

## Consequences
- (+) Small PRs can still touch shared code and a service together; CI checks both.
- (−) Docker builds need the workspace context (`uv sync --frozen --package <svc>` from `backend/`); this is handled in feature 09.
- (−) A shared-package change can force rebuilding all images; CI path filters (feature 10) keep that to the cases where it is needed.
- Follow-up: feature 09 Dockerfiles; feature 10 path filters.
- Revisit if: a service needs a different Python version, or a team (not one person) owns different services.

## Verification
`uv sync` from `backend/` works; `import soc_shared` works from every service; CI (feature 10) builds only the changed services.
