# progress.md — soc-worker session log

Protocol: `CLAUDE.md` §1. Plan of record: `specs/00-final-plan.txt` (v2). Constitution: `specs/constitution.md`.
**Append-only:** add a new session block at the bottom; never delete or edit an old (closed) block.
Only the "READ ME FIRST" box below is rewritten in place, every session.

> ## READ ME FIRST (rewritten every session — last: session 1, 2026-11-12T06:20Z)
> **Where we are:** Feature 01 (foundation) is **implemented and VERIFY.md is filled** → **waiting for Naveed to verify**.
> Branch `feat/01-foundation` is pushed, CI is green, and a **draft PR to main** is open (link in the session-1 block).
> **Next step:** Naveed runs `specs/01-foundation/VERIFY.md` → says "verified" → marks the PR ready and merges it himself →
> Claude starts **feature 02 (evals-first)**: a NEW branch `feat/02-evals-first` from the updated main → INTENT (draft in plan v2 §12) → spec → plan → tasks → STOP.
> **Blocked on Naveed:** verify 01 + merge the PR · rotate the old OpenAI/Anthropic keys · set the $10 OpenAI limit.
> **Push rule:** commit + push the feature branch every 3–4 tasks (standing, PHR-0004); never main; Naveed merges.
> **After the PR is merged: NEVER push to `feat/01-foundation` again.**
> **MVP:** features 01–06 + `make demo-ask` / `make demo-triage` by **2026-11-25**.
> **Never:** read `.env` · make a paid call without "haan" · touch ../handbook.
>
> | # | Feature | State |
> |---|---|---|
> | 01 | foundation | implementing → VERIFY filled, awaiting Naveed's verification |
> | 02 | evals-first | not started (next) |
> | 03–10 | — | not started |

---

## Session 1 — 2026-11-12

## Last updated (ISO date-time, session number)
2026-11-12T06:20Z · session 1

## Done this session (items + files + commit hashes)
- **Read the handbook handoff (READ ONLY):** `../handbook/progress.md` HANDOFF — FINAL, `instance.md`,
  `knowledge/rules-map/{invariants,data-handling,escalation-policy}.md`, `knowledge/triage-note/note-template.md`,
  `knowledge/playbooks/` (11 playbooks), `system/gateways/content.ts`, `evals/` (80 in-scope Qs, 35 OOC probes).
- **Gave the 10-bullet summary.** Asked about D-01 and got the answer (vendor/query-language probes → ALLOW_CYBER_RESEARCH).
- **Checked in Context7** (official Agents SDK docs):
  - blocking input guardrails (`run_in_parallel=False`);
  - `function_tool` with `needs_approval`, `tool_input_guardrails`, `tool_output_guardrails`;
  - the guardrail parameters of `MCPServerStreamableHttp`;
  - hosted tools and `Agent.as_tool()` skip tool guardrails;
  - `RunConfig.trace_include_sensitive_data` (default True) and the env var `OPENAI_AGENTS_TRACE_INCLUDE_SENSITIVE_DATA`.
  Also checked uv workspaces and pydantic-settings.
- **Plan:** wrote v1 to `specs/00-final-plan.txt`. Naveed approved it with amendments A1–A7, which became v2. Naveed "approved" v2.
- **Feature 01 docs, approved** ("approved for all points"; Q1: do not mask file hashes; Q2: `ip_context` carries the private range).
- **Feature 01 implemented** on `feat/01-foundation`:

  | Commit | Content |
  |---|---|
  | `284b865` | docs: CLAUDE.md, constitution, progress, templates, ADR-0001/0002, PHR-0001…0004, 01 INTENT/spec/plan/tasks/VERIFY |
  | `df7976b` | T01-01..04: root scaffold removed (A7), .gitignore, .gitleaks.toml, uv workspace (`backend/`), Python pinned 3.12, soc-shared skeleton, lab fixtures, no-network guard |
  | `25d81b8` | T01-05..07: models (WazuhAlert, MaskedAlert, KsorHit, ScopeVerdict + DECLINE_MESSAGE, AskAnswer, TriageNote + validators + `to_text()`, Decision/AuditEvent/LlmUsage), `classify_ip` / `is_public_ip` |
  | `b8d54c9` | T01-08..10: masking engine (MaskMap, `mask_text`, `unmask`, `find_leaks`, `find_unmasked_pii`, `mask_alert`) + property and performance tests |
  | `9d2cd6f` | T01-11..13: settings base, Makefile, `.env.example`, `scripts/demo_masking.py`, repo-hygiene tests, `.github/workflows/ci.yml` |
  | checkpoint 5 (this commit) | T01-14..15: LEARNING.md, CAREER-MAP.md, architecture.md, READMEs, VERIFY.md §4 real output, this progress update, PHR-0005 |

- **CI:** run 43166277801 on `9d2cd6f`. `python` succeeded, `secrets` (gitleaks over full history) succeeded.
- **Memory saved:** "plans as .txt before approval" and "push every 3–4 tasks".

## Current state (feature table 01–10: not started / intent / spec / plan / tasks / implementing / verified)
| # | Feature | State | Branch | Notes |
|---|---|---|---|---|
| 01 | foundation | implementing — done, VERIFY filled, **awaiting Naveed's verification** | feat/01-foundation (draft PR) | 153 tests, coverage 98.99%, CI green |
| 02 | evals-first | not started | — | INTENT draft is in plan v2 §12; needs OK before any OTRF download |
| 03 | mcp-services | not started | — | |
| 04 | handbook-client | not started | — | live demo needs "haan" (embedding cost) |
| 05 | agents-core | not started | — | model name + price to verify |
| 06 | guardrails | not started | — | MVP ends here (+ CLI demos) |
| 07 | agent-service | not started | — | after the MVP |
| 08 | api-gateway | not started | — | Auth0 + Neon (Naveed sets them up) |
| 09 | docker | not started | — | |
| 10 | ci-cd | not started | — | first GHCR push needs "haan" |

## Decisions taken (link ADRs)
- **D-01 scope taxonomy:** vendor config and query-language questions → ALLOW_CYBER_RESEARCH, concepts and defensive detection logic only — `backend/docs/adr/ADR-0002-scope-taxonomy.md` (Accepted).
- **Monorepo:** uv workspace, one folder and one image per service — `backend/docs/adr/ADR-0001-monorepo-uv-workspace.md` (Accepted).
- **Plan amendments A1–A7** — `specs/00-final-plan.txt` v2, PHR-0003:
  - A1: MVP = features 01–06 by 2026-11-25;
  - A2: tracing privacy;
  - A3: SQLite sessions in Phase 3, Postgres in Phase 8;
  - A4: D-01 approved;
  - A5: every rate reported as count + percent;
  - A6: +5 prompt-injection probes;
  - A7: root scaffold cleanup.
- **Feature 01 design decisions** (approved by Naveed or recorded in spec/LEARNING):
  - File hashes are NOT masked; they are IOCs (Q1).
  - `ip_context` gives the private range only (Q2).
  - Built-in principals (Administrator, root, SYSTEM …) stay unmasked, because escalation condition 2 needs to see a privileged account.
  - A NetBIOS domain gets a HOST token.
  - IPv6 is masked before IPv4.
  - Workspace members are `packages/*` only for now (uv needs a pyproject.toml in each member).
  - The masking demo lives in `backend/scripts/`, not inside the package.
  - Ruff allows the handbook's en and em dashes.
- **Standing push rule** (PHR-0004).
- **Planned ADRs (not written yet):**
  - 0003 model;
  - 0004 web search;
  - 0005 auth;
  - 0006 no sandbox;
  - 0007 masking + trace privacy;
  - 0008 sessions;
  - 0009 eval data sources and licences.

## Errors hit + fixes
- **uv picked Python 3.13**, because `backend/` had no `.python-version`. Fix: added `backend/.python-version` = 3.12 and recreated the venv.
- **pytest-socket warning in the no-network test.** Fix: the test filters that expected warning.
- **Ruff RUF001 on the handbook's en dash, E501, and S104/S106 in tests.** Fix: `allowed-confusables`; split the long lines; allowed S104/S106 for tests only.
- **Wrong test case:** `a::b` is a valid IPv6 address. Fix: changed the test to `x::y`.
- **Token order:** the user token was created before the domain token. Fix: the domain token is now created first.
- **Masking was too slow:** the learned-names regex was recompiled for every text segment, so a 50 KB alert took 98 ms. Fix: compile it once per step; now 19–29 ms.
- **Ruff 0.17 formats Python code blocks inside Markdown**, so the README failed `format --check`. Fix: `make fmt`.
- **Hypothesis found an edge case:** `0.0.0.0` and `::ffff:0:0` share one token, so the round-trip test failed. This is intended (FR-01-31). Fix: the round-trip property excludes IPv4-mapped forms, and a new property test proves they share the token.

## Pending / blocked (reason + who acts: Naveed or Claude)
- **Naveed:** run `specs/01-foundation/VERIFY.md` (sections 0–3), write the verdict in §5 or tell Claude, then mark the draft PR "Ready for review" and merge it.
- **Claude (after merge):** start feature 02 on a NEW branch `feat/02-evals-first` from the updated `main`.
- **Naveed (for 02):** decide whether OTRF Security-Datasets may be downloaded (free public GitHub). Claude checks the licence first.

## Eval results so far (numbers)
- None yet; feature 02 defines the sets.
- Feature 01 quality numbers:
  - tests 153/153 = 100% pass;
  - soc-shared coverage 98.99%;
  - property tests 1,700 generated examples with 0 leaks;
  - 50 KB alert masked in 18.8–29.0 ms.
- Handbook retrieval evals, for reference: in-scope 80/80 = 100%.

## Exact next step for the next session
1. Read this block and run `git status` and `git branch --show-current`.
2. If Naveed has verified and merged PR #1 (feature 01): `git checkout main && git pull`, then `git checkout -b feat/02-evals-first`.
   Copy the templates into `specs/02-evals-first/` and write INTENT.md from plan v2 §12. Write spec.md, plan.md and tasks.md (also draft ADR-0009 on data sources and licences). STOP for approval.
3. If he has not verified yet: help him run VERIFY.md and fix anything he finds, on `feat/01-foundation`. This is allowed only while its PR is unmerged.

## Naveed's manual actions needed
- Rotate the OpenAI and Anthropic keys (pasted in an earlier chat).
- Set a $10 monthly usage limit in the OpenAI dashboard.
- Verify feature 01 with `specs/01-foundation/VERIFY.md`, then merge the PR.
- Later (not now):
  - Neon db `soc_worker` (feature 08);
  - Auth0 tenant (08);
  - keys in `backend/.env`;
  - `npm run serve` in ../handbook (04).
