# Architecture Decision Records (ADRs)

An ADR records ONE significant decision: the context, the options, the choice, and its consequences.
ADRs are never edited after they are Accepted — a later change is a NEW ADR that "Supersedes ADR-NNNN".
Status values: Proposed → Accepted (by human:naveed) → Superseded by ADR-NNNN / Deprecated.

## Index
| ADR | Title | Status | Feature |
|---|---|---|---|
| [0001](ADR-0001-monorepo-uv-workspace.md) | Monorepo, uv workspace, one folder + image per service | Accepted 2026-11-12 | 01 |
| [0002](ADR-0002-scope-taxonomy.md) | Scope taxonomy: ALLOW_KSOR / ALLOW_CYBER_RESEARCH / DECLINE (D-01) | Accepted 2026-11-12 | 02, 06 |
| 0003 | Model choice: the smallest current OpenAI model per agent | planned | 05 |
| 0004 | Web-search tool: a free-tier API wrapped as a function tool vs hosted web search | planned | 05 |
| 0005 | Auth provider: Auth0 vs Clerk | planned | 08 |
| 0006 | No sandbox (the worker never runs generated code) | planned | 06 |
| 0007 | Masking architecture + trace privacy | planned | 06 |
| 0008 | Sessions: SQLiteSession for Phase 3; Postgres in Phase 8 | planned | 05 |
| [0009](ADR-0009-eval-data-sources.md) | Eval data sources and licences (synthetic + OTRF MIT) | Accepted 2026-11-12 | 02 |

## Template
```markdown
# ADR-NNNN — <title>
- Status: Proposed | Accepted (human:naveed, <date>) | Superseded by ADR-XXXX
- Date: <YYYY-MM-DD> · Feature: NN · Deciders: human:naveed (approver), Claude (author)
- Related: PHR-NNNN, spec FR-..., plan §...

## Context            (the problem, the forces, the constraints — facts with sources)
## Options considered (≥ 2; for each: pros, cons, cost, risk)
## Decision           (the option, in one sentence)
## Rationale          (why this option wins under our constraints)
## Consequences       (positive, negative, follow-up work, what would make us revisit it)
## Verification       (how we will know it was right: a test, an eval number, a demo)
```
