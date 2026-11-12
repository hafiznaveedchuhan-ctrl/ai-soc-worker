# progress.md — soc-worker session log

Protocol: `CLAUDE.md` §1. Plan of record: `specs/00-final-plan.txt` (v2). Constitution: `specs/constitution.md`.
**Append-only:** add a new session block at the bottom; never delete or edit an old (closed) block.
Only the "READ ME FIRST" box below is rewritten in place, every session.

> ## READ ME FIRST (rewritten every session — last: session 1, 2026-11-12T07:15Z)
> **Where we are:** Feature 02 (evals-first) **approved** and about 80% implemented. PR #3 (docs + scorer + probes) is already merged by Naveed.
> The rest is on the NEW branch **`feat/02-evals-part2`** (pushed): 30 of 40 alerts, recordings, report, CLI, review sheet. `make eval-dry` passes (oracle: all targets PASS).
> **Blocked on Naveed (explicit "haan" needed):** **Q1** download about 6 OTRF files (MIT) · **Q2** read the Wazuh ruleset v4.14.10 for the port-scan/PowerShell rule IDs.
> Without them, 10 alerts are pending (`test_final_composition` is xfail).
> Also: Naveed verifies the labels with `backend/evals/review/labels-review.md` · decides how PRs are merged (see the PR-rhythm note below).
> **Next step (Claude):** after Q1/Q2 → T02-07/T02-08 (4 alerts) + T02-10 (6 OTRF) → T02-14 docs (ADR-0009 Accepted, LEARNING §8, CAREER-MAP 02) → T02-15 VERIFY → PR.
> **PR rhythm:** Naveed has merged PRs right after a checkpoint push (PR #1, PR #3). After such a merge Claude must continue on a NEW branch from main (guard: `gh pr list --head <branch> --state merged` must be empty before every push).
> **Never push to:** `feat/01-foundation`, `feat/02-evals-first` (both merged).
> **`.env`:** exists (600). Never read or print it.
> **MVP:** features 01–06 + `make demo-ask` / `make demo-triage` by **2026-11-25**.
>
> | # | Feature | State |
> |---|---|---|
> | 01 | foundation | **verified** (merged) |
> | 02 | evals-first | implementing (about 80%) — waiting on Q1/Q2 + label verification |
> | 03–10 | — | not started |

---

## Session 1 — 2026-11-12

## Last updated (ISO date-time, session number)
2026-11-12T07:15Z · session 1 (block updated during the session; the session is still open)

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
- **Feature 01 verified** by Naveed. The PR #2 merge error was caused by its draft status; fixed with `gh pr ready 2`. Naveed merged PR #2 at 06:22Z (main = 9489133). PHR-0006.
- **`backend/.env`** created from `.env.example` (mode 600, gitignored). Naveed filled `OPENAI_API_KEY` and `SOC_DB_URL`.
  Claude filled only the empty non-secret lines with `sed` (WAZUH_MODE, the budgets, HANDBOOK_MCP_URL, AUTH_MODE, CORS_ORIGINS) and generated `MASK_MAP_KEY` without displaying it. The file was never read or printed (only the variable names were listed).
- **Feature 02 docs** on the new branch `feat/02-evals-first` (from main 9489133): INTENT (Q1–Q4), spec, plan, tasks, VERIFY draft, ADR-0009 (Proposed), PHR-0007.
  Checked first (read only): the handbook's Wazuh rule tables (windows-rules-reference, sshd-rules-reference, FIM playbook), the MITRE page list, the event pages, the false-positive pages.
  Licences checked through the GitHub API: OTRF/Security-Datasets = MIT; splunk/botsv1 = CC0-1.0.
- **Feature 02 approved** ("approced"). Q3 (≥ 20 TP) and Q4 (accept both MITRE IDs) accepted as proposed. Q1/Q2 are still open, because they are external calls that need an explicit "haan".
- **Feature 02 implemented on `feat/02-evals-first`:**
  - `faf6ab7`: soc-evals package, Rate, predictions, loader, scorers, targets.
  - `ab9f62f`: KSOR reference snapshot (156 stable_ids, 17 MITRE ids, handbook bc5c680) and 95 scope probes.
  - Naveed merged both as **PR #3** at 06:57Z.
- **Continued on the new branch `feat/02-evals-part2`:**
  - `e358978`: 30 alerts (20 playbook + 10 FP-page) + labels + context.csv, oracle/faulty recordings, report template + renderer, CLI, review sheet, `make eval-*`, the CI eval-dry step.
  - soc-shared fix: built-in group names stay unmasked.

## Current state (feature table 01–10: not started / intent / spec / plan / tasks / implementing / verified)
| # | Feature | State | Branch | Notes |
|---|---|---|---|---|
| 01 | foundation | **verified** (human:naveed, 2026-11-12) — merged | PR #1 + PR #2 merged (main 9489133) | 153 tests, coverage 98.99%, CI green |
| 02 | evals-first | implementing (about 80%) | PR #3 merged · now feat/02-evals-part2 | 30/40 alerts, 95/95 probes, eval-dry green; waiting on Q1/Q2 + label verification |
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
- **Pushed after a merged PR (my mistake):** Naveed merged PR #1 at 05:56Z, when it held only 284b865 and df7976b. I did not check and pushed 5 more commits to `feat/01-foundation`. Nothing was lost, because the 5 commits are in PR #2 (CLEAN, mergeable). Fix: CLAUDE.md now has a guard: before every push, `gh pr list --head <branch> --state merged` must be empty (PHR-0006).
- **Merge button error on PR #2:** it was opened as a draft, and GitHub does not merge drafts. Fix: `gh pr ready 2`. Future PRs are opened ready for review.
- **Pushed checkpoint commits that Naveed then merged at once (PR #3):** the guard found the merged PR before the next push. Fix: the work moved to the new branch `feat/02-evals-part2` from main. Nothing was lost.
- **The oracle eval first failed its leak target:**
  - the label rationale (for humans, with raw lab names) went into the oracle output;
  - the leak check matched substrings ("Oracle" ~ username "oracle");
  - "Administrators" (a GROUP name) was masked as a user.
  Fixes: the rationale is kept out of the output; the leak check uses `find_leaks` with word boundaries; built-in groups stay visible.
- **Wrong test expectation:** the faulty recording misses 2 TPs, not 1, so TP recall is 11/13 = 84.6%. Fixed the test.
- **Hypothesis found an edge case:** `0.0.0.0` and `::ffff:0:0` share one token, so the round-trip test failed. This is intended (FR-01-31). Fix: the round-trip property excludes IPv4-mapped forms, and a new property test proves they share the token.

## Pending / blocked (reason + who acts: Naveed or Claude)
- **Naveed:** say "haan" or "no" to Q1 (OTRF download) and Q2 (read the Wazuh ruleset) — 10 alerts wait on these.
- **Naveed:** verify the labels with `backend/evals/review/labels-review.md` (30 alerts + 95 probes; notes for EV-A002 and EV-A023).
- **Naveed:** PR rhythm — either merge only when a feature is verified, or keep merging per checkpoint (Claude then opens a new branch each time).
- **Naveed (before feature 03):** create a free AbuseIPDB account and put the key in `backend/.env` (`ABUSEIPDB_API_KEY`).
- **Claude:** T02-07, T02-08 (rest), T02-10 after Q1/Q2; T02-14, T02-15.

## Eval results so far (numbers)
- Dry run (oracle recording, 2026-11-12): datasets 125/125 = 100.0% valid (30 alerts, 95 probes).
  Every target PASSES: TP recall 13/13, precision 13/13, cited 85/85, decline 30/30, false declines 0/55, leaks 0, invented MITRE 0.
- Faulty recording: every planted failure is caught (e.g. TP recall 11/13 = 84.6% → FAIL as intended).
- Labels verified by Naveed: alerts 0/30, probes 0/95.
- No paid run yet.

## Exact next step for the next session
1. Read the READ ME FIRST box. `git branch --show-current` should be `feat/02-evals-part2`. Run the guard: `gh pr list --head feat/02-evals-part2 --state merged` must be empty, otherwise make a new branch from main.
2. If Q1/Q2 = haan:
   - Q2: read the Wazuh ruleset v4.14.10 files (GitHub, read only) → record file:line → add 2 port-scan + 2 PowerShell alerts in `build_alerts.py`.
   - Q1: download about 6 small OTRF files into the scratchpad → map them → add EV-A035…A040 with attribution.
   - Then `make eval-recordings && make check`. `test_final_composition` must pass, which means removing the xfail.
3. If Q1/Q2 = no: write those 10 as SYNTHETIC alerts; for port-scan/PowerShell, ask Naveed which rule IDs to use. Never invent them.
4. Then T02-14 (ADR-0009 → Accepted, LEARNING §8, CAREER-MAP row 02) and T02-15 (VERIFY.md §4 real output, progress, PHR) → PR (ready).

## Naveed's manual actions needed
- Rotate the OpenAI and Anthropic keys (pasted in an earlier chat).
- Set a $10 monthly usage limit in the OpenAI dashboard.
- Answer Q1/Q2 (haan/no). Verify the eval labels (review sheet).
- Before feature 03: free AbuseIPDB account → `ABUSEIPDB_API_KEY` in `backend/.env`.
- Later (not now):
  - Neon db `soc_worker` (feature 08);
  - Auth0 tenant (08);
  - `npm run serve` in ../handbook (04).
