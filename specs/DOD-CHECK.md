# Definition of Done check (R11) — `specs/00-final-plan.txt` §17
Last checked by Claude: **2026-11-18, session 4**. ✅ done · 🟡 waiting on Naveed

| # | DoD item | State | Evidence |
|---|---|---|---|
| 1 | Features 01–10 approved, implemented, verified via VERIFY.md | 🟡 | All are implemented and every VERIFY.md (01–11) is filled. Naveed has verified 01 himself; 02–11 are waiting for his check. |
| 2 | CI green on a PR | ✅ | PRs #1–#44 green, including the image smoke-imports (PR #44) |
| 3 | eval-dry passes | ✅ | `make eval-dry` → oracle: all PASS (2026-11-18) |
| 4 | One paid eval meets the targets, OR lists the failures with reasons | ✅ | Runs: R5 (135 items), then P1–P4 and R6a–R6c. Every report has a Diagnostics section with the reason for each failure. The details are listed below this table. |
| 5 | All 4 guardrail kinds + masking proven by tests and demos | ✅ | 368 tests; FAKE demos in CI; live: 0 raw values in any journal; Docker demo-up masked → unmasked for the analyst only |
| 6 | Every service builds an image | ✅ | CI builds + Trivy + smoke-import; **GHCR release run 44250254761: all 4 images pushed** |
| 7 | `make up` runs the full flow in the terminal | ✅ | 2026-11-18: 4 containers healthy; `make demo-up`: /ask cited event-4625/4624; /triage EV-A003 note saved (note_id 2) |
| 8 | LEARNING, CAREER-MAP, progress.md, 00-final-plan complete | ✅ | LEARNING §1–15, CAREER-MAP 01–11, progress.md session 4 + handoff |
| 9 | Everything committed | ✅ | main = all PRs merged |

**Item 4, the targets after the runs:**
- **Met:** scope DECLINE 29/30 (target ≥90%) ✅; false declines ≤10% ✅; exact decline text 100%; real leaks 0; TP precision 8/10 ✅.
- **Not met:** TP recall 8/21 (target 95%); cite-or-abstain and MITRE-clean rates are below 100%, because errored items count as fails.

**Also done in session 4 (beyond the DoD):**
- **R7 Neon:** migrated, 8 tables in `neondb`.
- **R9 Auth0:** tenant `dev-78jlhsubimuljjjn.us.auth0.com` and audience `https://soc-worker-api` are in `.env` and checked against the live JWKS.
- **Labels:** approved by delegation (`naveed-delegated`).

**Open:**
- the Auth0 post-login roles Action (Naveed);
- switching `AUTH_MODE=auth0` when a login frontend exists (Phase 4);
- live Wazuh alerts (Phase 1 B/C, later);
- TP recall (more prompt and label work, or a reviewer upgrade, ADR-0013 candidate).
