# progress.md — soc-worker session log

Protocol: `CLAUDE.md` §1. Plan of record: `specs/00-final-plan.txt` (v2). Constitution: `specs/constitution.md`.
**Append-only:** add a new session block at the bottom; never delete or edit an old block.
Only the "READ ME FIRST" box below is rewritten in place, every session.

> ## READ ME FIRST (rewritten every session — last: session 1, 2026-11-12)
> **Where we are:** Plan v2 APPROVED. Branch `feat/01-foundation` pushed to origin (SDD docs only, no code).
> Feature 01 docs are written (INTENT, spec, plan, tasks, VERIFY draft) → **waiting for Naveed's "approved"** before any code.
> **Next step:** Naveed approves `specs/01-foundation/{INTENT,spec,plan,tasks}.md` → Claude implements tasks T01-01…T01-14.
> **Blocked on Naveed:** approve 01 docs + answer the 2 open questions in `specs/01-foundation/INTENT.md` · rotate the old OpenAI/Anthropic keys · set the $10 OpenAI limit.
> **Push rule:** commit + push the feature branch every 3–4 tasks (standing, PHR-0004); never main; Naveed merges.
> **MVP:** features 01–06 + `make demo-ask` / `make demo-triage` by **2026-11-25**.
> **Never:** read `.env` · make a paid call without "haan" · push without "push" · touch ../handbook.
>
> | # | Feature | State |
> |---|---|---|
> | 01 | foundation | tasks (awaiting approval) |
> | 02–10 | — | not started |

---

## Session 1 — 2026-11-12

## Last updated (ISO date-time, session number)
2026-11-12T05:45Z · session 1

## Done this session (items + files + commit hashes)
- Read the handbook handoff (READ ONLY): `../handbook/progress.md` HANDOFF — FINAL, `instance.md`,
  `knowledge/rules-map/{invariants,data-handling,escalation-policy}.md`, `knowledge/triage-note/note-template.md`,
  `knowledge/playbooks/` (11 playbooks), `system/gateways/content.ts`, `evals/` (80 in-scope Qs, 35 OOC probes).
- Gave Naveed the 10-bullet summary. Decision D-01 (vendor/query-language probes → ALLOW_CYBER_RESEARCH) asked and answered.
- Checked in Context7 (official Agents SDK docs): blocking input guardrails (`run_in_parallel=False`); `function_tool`
  `needs_approval` / `tool_input_guardrails` / `tool_output_guardrails`; `MCPServerStreamableHttp` guardrail params;
  hosted tools and `Agent.as_tool()` skip tool guardrails; `RunConfig.trace_include_sensitive_data` (default True)
  and env `OPENAI_AGENTS_TRACE_INCLUDE_SENSITIVE_DATA`.
- Plan v1 → `specs/00-final-plan.txt`; Naveed approved with amendments A1–A7 → plan v2 (same file); Naveed "approved" v2.
- Created branch `feat/01-foundation` from `main` (aa6468b).
- Wrote: `CLAUDE.md`, `progress.md`, `specs/constitution.md`, `specs/_templates/*` (6 templates),
  `specs/01-foundation/{INTENT,spec,plan,tasks,VERIFY}.md`, `backend/docs/adr/{README,ADR-0001,ADR-0002}.md`,
  `history/prompts/{README,PHR-0001…PHR-0004}.md` (PHR index in `history/prompts/README.md`).
- Memory saved: "plans as .txt before approval".
- Naveed's standing push rule recorded (CLAUDE.md §2, constitution Art. X, PHR-0004).
- Commit: `docs(01): SDD foundation docs` on `feat/01-foundation` → pushed to origin (hash: see `git log -1 feat/01-foundation`; written in session 2's block).

## Current state (feature table 01–10: not started / intent / spec / plan / tasks / implementing / verified)
| # | Feature | State | Branch | Notes |
|---|---|---|---|---|
| 01 | foundation | tasks — awaiting approval | feat/01-foundation | docs written; no code |
| 02 | evals-first | not started | — | INTENT draft is in plan v2 §12 |
| 03 | mcp-services | not started | — | |
| 04 | handbook-client | not started | — | live demo needs "haan" (embedding cost) |
| 05 | agents-core | not started | — | model name + price to verify |
| 06 | guardrails | not started | — | MVP ends here (+ CLI demos) |
| 07 | agent-service | not started | — | after the MVP |
| 08 | api-gateway | not started | — | Auth0 + Neon (Naveed sets them up) |
| 09 | docker | not started | — | |
| 10 | ci-cd | not started | — | first GHCR push needs "haan" |

## Decisions taken (link ADRs)
- D-01 scope taxonomy: vendor config/query-language → ALLOW_CYBER_RESEARCH (concepts + defensive detection logic only) — `backend/docs/adr/ADR-0002-scope-taxonomy.md` (Accepted).
- Monorepo, uv workspace, one folder + image per service — `backend/docs/adr/ADR-0001-monorepo-uv-workspace.md` (Accepted).
- Plan amendments A1–A7 (MVP 2026-11-25; tracing privacy; SQLite sessions for Phase 3; count+percent reporting;
  +5 injection probes; root scaffold cleanup) — `specs/00-final-plan.txt` v2, `history/prompts/PHR-0003`.
- Planned ADRs (not written yet): 0003 model, 0004 web search, 0005 auth, 0006 no sandbox, 0007 masking + trace privacy,
  0008 sessions, 0009 eval data sources/licences.

## Errors hit + fixes
- None.

## Pending / blocked (reason + who acts: Naveed or Claude)
- **Naveed:** approve `specs/01-foundation/{INTENT,spec,plan,tasks}.md` (STOP point before code).
- **Naveed:** answer INTENT open questions Q1 (do not mask file hashes) and Q2 (`ip_context` with the private range).
- **Claude (after approval):** T01-01 … T01-14 in `specs/01-foundation/tasks.md`.

## Eval results so far (numbers)
- None yet (feature 02 defines the sets; handbook retrieval evals for reference: in-scope 80/80 = 100%).

## Exact next step for the next session
1. Read this block. 2. If Naveed approved feature 01 docs → start T01-01 (check uv workspace + pydantic-settings docs in Context7),
then follow tasks.md in order. If not approved → ask him to review `specs/01-foundation/`.

## Naveed's manual actions needed
- Rotate the OpenAI and Anthropic keys (pasted in an earlier chat).
- Set a $10 monthly usage limit in the OpenAI dashboard.
- Review and approve the feature 01 docs.
- Later (not now): Neon db `soc_worker` (feature 08), Auth0 tenant (08), keys in `backend/.env`, `npm run serve` in ../handbook (04).
