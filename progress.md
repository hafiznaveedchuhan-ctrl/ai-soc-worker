# progress.md — soc-worker session log

Protocol: `CLAUDE.md` §1. Plan of record: `specs/00-final-plan.txt` (v2). Constitution: `specs/constitution.md`.
**Append-only:** add a new session block at the bottom; never delete or edit an old (closed) block.
Only the "READ ME FIRST" box below is rewritten in place, every session.

> ## READ ME FIRST (rewritten every session — last: session 1 end, 2026-11-12)
> **Where we are:** ALL CODE for features 01–10 is written and tested OFFLINE. This follows Naveed's order: "code first, LLM testing later" (PHR-0012).
> - 307 tests pass, coverage 93%. No live LLM call has been made.
> - Branches: 05/06 → PR #9; 07 → `feat/07-agent-service-api`; 08–10 → `feat/08-api-gateway`. The branch chain is 04 → 05 → 07 → 08.
>   Naveed merges; if a PR is open for each branch, merge them in order.
> **Next step (needs Naveed):**
> 1. Merge the open PRs.
> 2. LIVE LLM test, with "haan" for each:
>    - T1 `npm run serve` (../handbook);
>    - T2 `make demo-ask LIVE=1 CONFIRM=haan Q="What does event 4625 mean?"`;
>    - then `make demo-triage LIVE=1 CONFIRM=haan`.
> 3. Paid eval: wire the live pipeline into `soc_evals paid` (Claude), then run it with "haan".
> 4. `make db-upgrade CONFIRM=haan` (Neon) · Auth0 (specs/08-api-gateway/AUTH0-SETUP.md) · Docker Desktop WSL integration → `make up`.
> **Blocked on Naveed:** the label review (0/40, 0/95) · AbuseIPDB + Tavily free keys · rotate the old keys · the $10 OpenAI limit.
> **PR rhythm:** Naveed merges each push. Before EVERY push: `gh pr list --head <branch> --state merged` must be empty, else make a new branch.
> **`.env`:** never read or print it. Claude added only generated secrets (MASK_MAP_KEY, AGENT_INTERNAL_TOKEN) and non-secret defaults.
>
> | # | Feature | State |
> |---|---|---|
> | 01 | foundation | **verified** |
> | 02 | evals-first | implemented (labels unverified) |
> | 03 | mcp-services | implemented, VERIFY filled |
> | 04 | handbook-client | implemented, VERIFY filled (live demo pending) |
> | 05 | agents-core | implemented offline; live test pending ("haan") |
> | 06 | guardrails | implemented offline; paid refusal eval pending |
> | 07 | agent-service API | implemented |
> | 08 | api-gateway | implemented (Neon migration + Auth0 pending) |
> | 09 | docker | implemented; 4 images built + Trivy-scanned in CI run 43228002776 (green) |
> | 10 | ci-cd | implemented; first GHCR release needs "haan" |

---

## Session 1 — 2026-11-12

## Last updated (ISO date-time, session number)
2026-11-12T10:40Z · session 1 (block updated during the session; the session is still open)

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
- Naveed merged that work as **PR #4** at 07:06Z.
- **"all haan" (Q1 + Q2):**
  - **Q2:** read the Wazuh ruleset v4.14.10 (0900 L27 rule 4151; 0915 L74 rule 91809 and L432 rule 91844; 0800 L734 rule 92068; 0945 L10 rule 92900).
  - **Q1:** downloaded 6 OTRF datasets (about 480 KB) into the scratchpad only, parsed with `python3 -I`.
    6 alerts mapped from 2 datasets; the MIT notice is in `THIRD_PARTY_NOTICES.md`.
  - **Detection gap:** the 4 other datasets (CMSTP, bitsadmin, 2× LSASS dump with 0x1FFFFF) raise no default Wazuh alert.
- **On the new branch `feat/02-evals-part3`:**
  - `bd11d95`: the complete 40-alert set; ADR-0009 Accepted.
  - Then: LEARNING §8, CAREER-MAP row 02, evals README, VERIFY.md §4 real output, this progress, PHR-0009.
  - Merged as PR #5.
- **"continue plz and approved for all your permission"** (PHR-0010):
  - Feature 03 docs + implementation on `feat/03-mcp-services`.
    - `6282383`: wazuh-mcp + enrichment-mcp + tests.
    - Then: demo, `make serve-*`, READMEs, LEARNING §9, CAREER-MAP 03, the CI demo step, VERIFY, progress.
  - Checked first: mcp 2.3.0 (Context7; `MCPServer` = the renamed FastMCP), AbuseIPDB v2 CHECK docs (Context7), and that openai-agents 0.24.0 resolves with mcp 2.3.0.
  - A local HTTP smoke test of wazuh-mcp passed.
  - PR #6 was merged during the work, so the demo and docs went to `feat/03-mcp-services-part2` (`3e41e4c`, PR #7, CI green).
- **Feature 04 handbook-client** on `feat/04-handbook-client`:
  - `packages/ksor-client`: wire models copied from the installed `@panaversity/ksor` gateway (read only), KsorClient, SearchOutcome, `search_once`, the fake KSOR server;
  - 16 tests;
  - `make demo-handbook` (CONFIRM=haan guard);
  - docs: LEARNING §10, CAREER-MAP 04, VERIFY offline, PHR-0011.

## Current state (feature table 01–10: not started / intent / spec / plan / tasks / implementing / verified)
| # | Feature | State | Branch | Notes |
|---|---|---|---|---|
| 01 | foundation | **verified** (human:naveed, 2026-11-12) — merged | PR #1 + PR #2 merged (main 9489133) | 153 tests, coverage 98.99%, CI green |
| 02 | evals-first | merged (PR #3–#5); continuing approved | main | 40/40 alerts, 95/95 probes; labels 0/40 + 0/95 verified by Naveed |
| 03 | mcp-services | implemented; VERIFY filled | PR #6 merged + PR #7 | 2 servers, 53 tests, demo in CI, no live call |
| 04 | handbook-client | implemented; VERIFY filled (offline) | feat/04-handbook-client | live demo is Naveed's (needs npm serve + CONFIRM=haan) |
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
- **pytest-socket blocked asyncio's self-pipe** (`SocketBlockedError` in the MCP tests). Fix: `--allow-unix-socket`; internet sockets stay blocked.
- **A placeholder test slipped in** (`test_unreachable…` did nothing). Replaced with a real test of `search_once` against a blocked connect.
- **Raw IP in logs (found by the demo):** httpx logs request URLs (`?ipAddress=<IP>`) at INFO. Fix: the httpx/httpcore loggers are set to WARNING in enrichment-mcp, and a test captures all loggers.
- **Guard caught merged PR #4** before the next push. Fix: new branch `feat/02-evals-part3`. Naveed's rhythm is now known (he merges each push), and the memory is updated.
- **Default ruleset has no alert for 4 of the 6 OTRF attacks** (cmstp, bitsadmin, LSASS 0x1FFFFF). These were not faked as alerts; recorded as a detection gap (ADR-0009).
- **Label error caught by the scorer:** EV-A036 had T1569.002, which is neither in the alert nor in the handbook. Removed.
- **Miscount:** the handbook has 10 playbooks, not 11. Fixed in the tests and specs.
- **Wrong test expectation:** the faulty recording misses 2 TPs, not 1, so TP recall is 11/13 = 84.6%. Fixed the test.
- **Hypothesis found an edge case:** `0.0.0.0` and `::ffff:0:0` share one token, so the round-trip test failed. This is intended (FR-01-31). Fix: the round-trip property excludes IPv4-mapped forms, and a new property test proves they share the token.

## Pending / blocked (reason + who acts: Naveed or Claude)
- **Naveed:** run `specs/02-evals-first/VERIFY.md`; verify the labels with `backend/evals/review/labels-review.md` (40 alerts + 95 probes). The NOTE items are listed in VERIFY §4.
- **Naveed (before feature 03):** create a free AbuseIPDB account and put the key in `backend/.env` (`ABUSEIPDB_API_KEY`).
- **Naveed:** merge PR #7 and the 04 PR; run the live demos (each needs his "haan").
- **Claude:** feature 05 (agents-core) docs + ADR-0003/0004/0008 on a new branch from main.

## Eval results so far (numbers)
- Dry run (oracle recording, 2026-11-12): datasets 135/135 = 100.0% valid (40 alerts, 95 probes). Every target PASSES:
  - TP recall 21/21 = 100.0%;
  - TP precision 21/21;
  - claims cited 95/95;
  - decline 30/30;
  - false declines 0/55 = 0.0%;
  - leak-free outputs 135/135;
  - invented MITRE 0/40.
- This proves the pipeline, not an agent.
- Faulty recording: TP recall 19/21 = 90.5% → FAIL, as planted; all 7 planted mistakes are detected.
- Labels verified by Naveed: alerts 0/40, probes 0/95.
- No paid run yet.

## Exact next step for the next session
1. Read the READ ME FIRST box. `git fetch`; check that PR #7 and the 04 PR are merged; `git checkout main && git pull && git checkout -b feat/05-agents-core`.
2. Feature 05 agents-core. Check first in Context7:
   - openai-agents 0.24.0: Agent, Runner, handoff, as_tool, function_tool, output_type, RunContextWrapper, RunHooks, SQLiteSession, tracing, run_streamed, MaxTurnsExceeded, MCPServerStreamableHttp;
   - the smallest current OpenAI model name and price (ADR-0003; read the official docs page).
   Choose the free-tier web search API (ADR-0004).
3. Write INTENT/spec/plan/tasks. Tests use the SDK's fake model, ksor_client.testing.build_fake_ksor and the MCP servers from 03 (in memory). The first real LLM call needs Naveed's "haan".

## Naveed's manual actions needed
- Rotate the OpenAI and Anthropic keys (pasted in an earlier chat).
- Set a $10 monthly usage limit in the OpenAI dashboard.
- Verify feature 02 and review the eval labels (review sheet).
- Before the live demo of feature 03: free AbuseIPDB account → `ABUSEIPDB_API_KEY` in `backend/.env`.
- Before feature 03: free AbuseIPDB account → `ABUSEIPDB_API_KEY` in `backend/.env`.
- Later (not now):
  - Neon db `soc_worker` (feature 08);
  - Auth0 tenant (08);
  - `npm run serve` in ../handbook (04).


---

## Session 1 — continuation block (2026-11-12, features 03–10)

## Last updated (ISO date-time, session number)
2026-11-12T13:00Z · session 1 (end)

## Done this session (items + files + commit hashes)
- **03 mcp-services:**
  - `6282383` servers (PR #6);
  - `3e41e4c` demo + docs (PR #7).
- **04 handbook-client:** `708bbc5` (PR #8).
- **05 + 06 agents-core + guardrails:** `89eb8bd` (PR #9).
  - `services/agent-service`: agents, flows, tools, guardrails, hooks, budget, deps, testing.
  - ADR-0003/0004/0006/0007/0008.
- **07 agent-service API:** `aef382f`.
- **08 api-gateway:** `cdc9e15`.
  - `services/api-gateway`: app, auth, db, crypto, ratelimit, the Alembic migration `08999efb4189`.
  - ADR-0005, AUTH0-SETUP.md.
- **09 + 10:** `eb88573`.
  - Dockerfiles ×4, `compose.yaml`, `.dockerignore`.
  - `ci.yml` (path filters, images + Trivy), `release.yml` (manual, confirm=haan), `deploy.yml` (disabled).
- **Docs:** LEARNING §9–13, CAREER-MAP rows 03–10, specs 03–10, PHR-0010…0013.

## Current state (feature table 01–10: not started / intent / spec / plan / tasks / implementing / verified)
| # | Feature | State |
|---|---|---|
| 01 | foundation | verified |
| 02 | evals-first | implementing → done; labels unverified |
| 03 | mcp-services | implementing → done; VERIFY filled |
| 04 | handbook-client | implementing → done; live demo pending |
| 05 | agents-core | implementing → done offline; live pending |
| 06 | guardrails | implementing → done offline; paid eval pending |
| 07 | agent-service API | implementing → done |
| 08 | api-gateway | implementing → done; Neon + Auth0 pending |
| 09 | docker | implementing → done; built in CI |
| 10 | ci-cd | implementing → done |

## Decisions taken (link ADRs)
- **ADR-0003:** gpt-5-nano is the default model ($0.05/$0.40 per 1M tokens).
- **ADR-0004:** web search via Tavily, wrapped in our own function tool.
- **ADR-0005:** Auth0 (free tier).
- **ADR-0006:** no sandbox.
- **ADR-0007:** masking + trace privacy.
- **ADR-0008:** SQLiteSession now, Postgres in Phase 8.
- **Other choices:**
  - mcp 2.3.0;
  - openai-agents 0.24.0;
  - tests with `agents.testing.ScriptedModel`;
  - an HTTP triage approval is decided up front (`approve_escalation_ticket`); the CLI asks interactively.

## Errors hit + fixes
- **Guardrail-internal agent runs were not priced:** they now use `CostHooks`.
- **`SQLiteSession(":memory:")` lost history between runs:** sessions are now cached per conversation.
- **SSE generator errors could not become HTTP status codes:** the checks now run in a pre-stream dependency.
- **Alembic `fileConfig` disabled the app loggers:** fixed with `disable_existing_loggers=False`.
- **The uv bookworm tag does not exist for 0.12.6:** switched to the trixie images.
- **MCP DNS-rebinding protection is off on 0.0.0.0:** fixed with `MCP_ALLOWED_HOSTS`.
- **httpx logged URLs that contain the raw IP:** silenced.
- **pytest-socket blocked asyncio's self-pipe:** fixed with `--allow-unix-socket`.
- **Placeholder test removed:** it asserted nothing.
- **No Docker in this WSL distro:** images are built in CI instead.

## Pending / blocked (reason + who acts: Naveed or Claude)
- **Naveed:**
  - merge the PRs;
  - the live LLM demos, the paid eval, the Neon migration and the first GHCR release — each needs "haan";
  - the Auth0 tenant; AbuseIPDB and Tavily keys; Docker Desktop WSL integration;
  - the label review; rotate the old keys; the $10 OpenAI limit.
- **Claude:**
  - wire `soc_evals paid` to the live pipeline (cost estimate before the run);
  - fix anything the live runs reveal.

## Eval results so far (numbers)
- Dry: 135/135 = 100.0% valid; the oracle passes every target. No paid run yet.
- Offline flow tests: 17 agent flows, 7 agent API, 10 gateway.
- Total: 307 tests, coverage 93.07%.

## Exact next step for the next session
1. Read the READ ME FIRST box.
2. `git fetch`; check which PRs are merged; continue on a new branch from main.
3. If Naveed says "haan" for the LIVE test:
   - check the price table again;
   - run `make demo-ask LIVE=1 CONFIRM=haan`, with the handbook running;
   - report tokens and cost.
4. Implement `soc_evals paid`, which runs the 40 alerts + 95 probes through the live pipeline.
   - Estimate the cost first (expected well under $1 with gpt-5-nano).
   - Run only after "haan"; write `evals/reports/<date>-paid-report.md`.

## Naveed's manual actions needed
- Merge the PRs (oldest first).
- Rotate the OpenAI and Anthropic keys; set the $10 OpenAI limit.
- Free keys into `backend/.env`: AbuseIPDB, Tavily.
- Auth0 (when you want real login).
- Enable Docker Desktop WSL integration (for `make up`).
- Review the labels (`backend/evals/review/labels-review.md`).
