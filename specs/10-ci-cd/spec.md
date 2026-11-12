# 10 ci-cd — compact SDD · Status: **implemented**
`ci.yml`: changes (paths-filter) → python (lint, types, ~300 tests + coverage, demos, eval-dry) · secrets (gitleaks) · images (matrix build + Trivy).
`release.yml`: manual, `confirm=haan`, main only → ghcr.io/<owner>/ai-soc-<svc>:<sha>. `deploy.yml`: Azure placeholder, `if: false`.
All third-party actions pinned by SHA (checked 2026-11-12 via the GitHub API). Docs: LEARNING §13.
**VERIFY:** the PR checks list `python`, `secrets`, and one `image <svc>` job per changed service — all green.
