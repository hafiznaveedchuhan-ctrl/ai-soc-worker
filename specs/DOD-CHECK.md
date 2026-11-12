# Definition of Done check (R11) — `specs/00-final-plan.txt` §17
Checked by Claude on 2026-11-12, session 2. ✅ = done · ⏳ = running · 🟡 = waiting on Naveed

| # | DoD item | State | Evidence / who acts |
|---|---|---|---|
| 1 | Features 01–10 approved, implemented, verified via VERIFY.md | 🟡 | All 10 implemented; VERIFY.md filled for 01–11 (07–10 added in session 2). **Naveed has verified only 01.** |
| 2 | CI green on a PR | ✅ | PRs #13–#23 green |
| 3 | eval-dry passes | ✅ | `make eval-dry` → oracle: all PASS |
| 4 | One paid eval meets the targets, OR lists the failures with reasons | ⏳ | R5 (`make eval`, 135 items) is running. The report now has a Diagnostics section (reasons per failure). |
| 5 | All 4 guardrail kinds + masking proven by tests and demos | ✅ | 350 tests; FAKE demos run in CI; live pilots: 0 raw IPs |
| 6 | Every service builds an image | ✅ | CI run 43228002776: 4 images + Trivy success |
| 7 | `make up` runs the full flow in the terminal | 🟡 | R8: Docker Desktop WSL integration (Naveed) |
| 8 | LEARNING, CAREER-MAP, progress.md, 00-final-plan complete | ⏳ | LEARNING §1–15 and CAREER-MAP 01–11 done; progress.md is updated at the session end |
| 9 | Everything committed | ✅ | Each session ends with commit + push + PR |

**Also open, outside the DoD but in the plan:**
- R7: Neon migration
- R9: Auth0
- R10: first GHCR release
- the label review (0/40 + 0/95)
- rotating the keys and setting the $10 limit
