# tasks — 01 foundation
Status: **draft — awaiting approval** · Plan: `./plan.md` · Branch: `feat/01-foundation`
Legend: [ ] todo · [~] in progress · [x] done · **STOP** = wait for Naveed
Push rhythm (Naveed, 2026-11-12, PHR-0004): commit + push this feature branch after every 3–4 tasks (checkpoints ⬆ below).

| ✓ | ID | Task | Satisfies | Files | Done when | Depends |
|---|---|---|---|---|---|---|
| [x] | T01-00 | Write the SDD docs: constitution, CLAUDE.md, progress.md, templates, ADR-0001/0002, PHRs, INTENT/spec/plan/tasks/VERIFY | Art. VII | specs/, history/, backend/docs/adr/ | files exist | — |
| | **STOP** | **Naveed approves INTENT + spec + plan + tasks (and answers the 2 open questions in INTENT)** | | | "approved" | T01-00 |
| [ ] | T01-01 | Check the docs (Context7/official) for uv workspaces, pydantic, pydantic-settings, hypothesis, pytest-socket, ruff, mypy, setup-uv, gitleaks; fill in plan.md §4 | Engineering rule | plan.md | table filled with versions + dates | STOP |
| [ ] | T01-02 | Root scaffold cleanup (delete root `pyproject.toml`, `src/soc_worker/`); update `.gitignore`; add `.gitleaks.toml` | FR-01-03, 07, 08 | root | `git status` shows the deletions; check-ignore tests | T01-01 |
| [ ] | T01-03 | Create the workspace: `backend/pyproject.toml` (members, dev group, ruff/mypy/pytest/coverage config), `packages/soc-shared` skeleton + `py.typed`, `.gitkeep` dirs; `uv sync`; commit `uv.lock` | FR-01-01, 02 | backend/ | `uv sync` OK; `import soc_shared` OK | T01-02 |
| [ ] | T01-04 | No-network guard + `conftest.py` + the 3 lab fixtures (documentation IPs / RFC 1918 / invented names) | NFR-01-01, 06 | tests/ | a test that opens a socket fails | T01-03 |
| | ⬆ | **checkpoint 1: commit + push** (`chore(01): uv workspace + soc-shared skeleton`) | | | pushed | T01-04 |
| [ ] | T01-05 | Tests first, then models: alert, ksor, scope (+ DECLINE_MESSAGE), audit/usage/decision, answer | FR-01-10…14, 17…20 | models/, test_models.py | tests green | T01-04 |
| [ ] | T01-06 | Tests first, then TriageNote + validators + `to_text()` golden test | FR-01-15, 16 | note.py, test_triage_note.py | tests green | T01-05 |
| [ ] | T01-07 | Tests first, then `ipclass` (classify_ip, is_public_ip) | FR-01-34, 35 | ipclass.py, test_ipclass.py | all listed IPs classified correctly | T01-04 |
| | ⬆ | **checkpoint 2: commit + push** (`feat(01): shared models, TriageNote, ip classification`) | | | pushed | T01-07 |
| [ ] | T01-08 | Tests first, then MaskMap + `mask_text`/`unmask`/`find_leaks`/`find_unmasked_pii` + edge cases (spec §4) | FR-01-30…32, 36…38 | maskmap.py, text.py, patterns.py | case tests green (count + %) | T01-07 |
| [ ] | T01-09 | Tests first, then `mask_alert` (field-aware + recursive + dropped secrets + ip_context); golden tests on 3 fixtures | FR-01-11, 12, 33, 34 | alert.py, test_mask_alert.py | golden tests green | T01-08 |
| [ ] | T01-10 | Property tests (≥ 500 examples: no leak, round-trip, idempotent) + perf budget test | S4, NFR-01-04 | test_masking_properties.py, test_masking_perf.py | green | T01-09 |
| | ⬆ | **checkpoint 3: commit + push** (`feat(01): masking engine with property tests`) | | | pushed | T01-10 |
| [ ] | T01-11 | Settings base + tests (env via monkeypatch; production refuses sensitive tracing) | FR-01-40, 41 | settings.py, test_settings.py | green | T01-04 |
| [ ] | T01-12 | Makefile (all targets + stubs), `.env.example`, `demo_masking.py`, `tests/test_repo_hygiene.py` | FR-01-04, 05, S8 | backend/ | `make help`, `make demo-masking` OK | T01-09, T01-11 |
| [ ] | T01-13 | CI skeleton `.github/workflows/ci.yml` (python + secrets jobs) | FR-01-06 | .github/ | YAML valid; runs on the push | T01-12 |
| | ⬆ | **checkpoint 4: commit + push** → CI runs on the branch | | | CI green | T01-13 |
| [ ] | T01-14 | Docs: LEARNING.md, CAREER-MAP.md (row 01), architecture.md (Mermaid), soc-shared README, root README | FR-01-50…53 | backend/docs/, READMEs | Naveed can follow it | T01-13 |
| [ ] | T01-15 | Run the full gate (`make lint typecheck test cov demo-masking`), paste the REAL output into VERIFY.md §4, update progress.md + PHR | S1–S8 | VERIFY.md, progress.md | all gates green | T01-14 |
| | ⬆ | **checkpoint 5: commit + push**; open the PR `feat/01-foundation → main` (draft) | | | PR link given to Naveed | T01-15 |
| | **STOP** | **Naveed runs VERIFY.md and says verified → he merges the PR.** After the merge: never push to this branch again. | | | merged | T01-15 |
