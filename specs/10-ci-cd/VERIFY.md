# VERIFY — 10 ci-cd
**Status:** filled by Claude, 2026-11-12, session 2, from real output · the first GHCR release (R10) is Naveed's

## CI on every PR
Example: PR #18–#23 in session 2, all green. The jobs:

| Job | Proves |
|---|---|
| `changes (path filters)` | only changed services rebuild; a change to soc-shared rebuilds all |
| `python (lint · types · tests · demos · eval-dry)` | ruff, mypy, 350 tests, the FAKE demos and the free eval-dry |
| `secrets (gitleaks)` | no secret in the full history |
| `image <svc> (build + Trivy)` | the 4 images build and are scanned (skipped when no service changed) |

## Repo hygiene
`uv run pytest tests -q` → `7 passed`:
- `.env.example` holds names only;
- the required names are listed;
- `.gitignore` covers the secrets.

## Not done (needs Naveed)
**R10.** GitHub → Actions → release → Run workflow → type `haan`. This is the first GHCR push.
`deploy.yml` stays disabled until Phase 8.
