# SDD templates

Copy these into `specs/NN-name/` when a feature starts. Order and owner:

| File | Owner | Answers | Gate |
|---|---|---|---|
| INTENT.md | Naveed (Claude drafts) | WHY and WHAT SUCCESS LOOKS LIKE | approved |
| spec.md | Claude | WHAT the system must do (testable requirements) | approved |
| plan.md | Claude | HOW it will be built (design, libraries, docs checked) | approved |
| tasks.md | Claude | the ordered, small, testable STEPS | approved → code may start |
| VERIFY.md | Naveed (Claude drafts, fills real output) | HOW Naveed proves it works | verified |

Rules: requirement IDs (`FR-NN-xx`, `NFR-NN-xx`) are referenced by tasks and by tests (test names or docstrings).
Every task names the requirement(s) it satisfies. Every requirement has at least one test or one VERIFY step.
