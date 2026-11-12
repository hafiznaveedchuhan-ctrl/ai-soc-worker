# INTENT — 01 foundation
Status: **approved** by human:naveed 2026-11-12 ("approved for all points" — Q1: do not mask file hashes; Q2: ip_context carries the private range) · Plan of record: `../00-final-plan.txt` §11

## Goal
Build a clean, testable skeleton that every later feature builds on: a uv workspace under `backend/`, a shared package
`soc-shared` with the data contracts (alerts, notes, answers, decisions, usage, scope verdicts), the **masking engine**
that protects every future LLM, web and trace call, and a settings base. Add the project's working tools
(Makefile, `.env.example`, CI skeleton) and the learning docs (LEARNING.md, CAREER-MAP.md) so Naveed can follow every file.

## Users
- **Naveed** — runs `make test`, `make demo-masking`, reads LEARNING.md, verifies with VERIFY.md.
- **Later features** — every service imports `soc_shared` models and masking (03–08); evals (02) use the models.
- **CI** — runs lint, typecheck, tests and gitleaks on every PR.

## Constraints
- Python 3.12, uv workspace (`backend/pyproject.toml` is the workspace root).
- No network, no paid calls, no `.env` reads in tests (settings tests use monkeypatched env only).
- `../handbook` is not touched. Field rules come from its data-handling and note-template pages (read only).
- Every library API (uv workspaces, pydantic v2, pydantic-settings, hypothesis, ruff, mypy, GitHub Actions setup-uv,
  gitleaks) is checked in current docs before use.
- Root scaffold cleanup (approved, A7): delete the root `pyproject.toml` and `src/soc_worker/`.

## Success numbers
| # | Measure | Target |
|---|---|---|
| S1 | `make test` | 0 failures |
| S2 | soc-shared line coverage | ≥ 90% |
| S3 | Masking case tests (IPv4, IPv6, private/public, `DOMAIN\user`, UPN `user@domain`, hostnames/FQDNs, emails, same value → same token, round-trip unmask) | 100% pass (count + percent reported) |
| S4 | Property test: after `mask_text`, no generated raw IP/email is left | 0 leaks in ≥ 500 hypothesis examples |
| S5 | `make lint` (ruff check + format check) | 0 findings |
| S6 | `make typecheck` (mypy --strict on soc-shared) | 0 errors |
| S7 | CI skeleton on the PR | all jobs green |
| S8 | `make demo-masking` | prints before / after / token map; the "after" text has no raw value |

## Out of scope
Services, MCP servers, agents, LLM calls, database, Docker, auth, eval datasets (02).

## Open questions for Naveed
1. Masking of file hashes (SHA-256/MD5 in FIM alerts): they are IOCs that the analyst needs, not personal data.
   **Proposal:** do NOT mask hashes; mask only IP/user/host/email. (The handbook "never" list covers *password* hashes,
   and a password hash in an alert is dropped by the field-aware masker, see spec FR-01-12.)
2. Masking of the private-IP *range* (handbook data-handling row 4): **Proposal:** the masked alert carries
   `ip_context`, e.g. `{"<IP-1>": "private 10.0.0.0/8", "<IP-2>": "public"}`, so the model knows the range but never the value.
