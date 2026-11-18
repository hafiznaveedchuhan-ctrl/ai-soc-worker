# progress.md — soc-worker session log

Protocol: `CLAUDE.md` §1. Plan of record: `specs/00-final-plan.txt` (v2). Constitution: `specs/constitution.md`.
**Append-only:** add a new session block at the bottom; never delete or edit an old (closed) block.
Only the "READ ME FIRST" box below is rewritten in place, every session.

> ## READ ME FIRST — HANDOFF after SESSION 4 (rewritten 2026-11-18, final for MVP; next = SESSION 5)
>
> ### A. Status
> **MVP done.** Features 01–11 are merged (PRs #1–#44); 368 tests pass; coverage ≈ 94%; CI green; **GHCR release pushed** (all 4 images).
>
> Infrastructure:
> - **`make up` + `make demo-up`** work end to end in Docker;
> - **Neon** is migrated (`neondb`, 8 tables);
> - **Auth0** is configured: tenant `dev-78jlhsubimuljjjn.us.auth0.com`, audience `https://soc-worker-api`;
> - local runs stay on `AUTH_MODE=dev` until a login frontend exists.
>
> Evals:
> - **scope target met** (DECLINE 29/30, false declines ≤ 10%, leaks 0);
> - **triage** TP recall 8/21, precision 8/10 (R6c);
> - ledger $2.56 (OpenAI billing ≈ $0 on the incentivized tier).
>
> Models: scope + triage = gpt-5-mini (ADR-0011 / 0012); everything else = gpt-5-nano.
>
> `specs/DOD-CHECK.md`: 8/9 ✅. Item 1 waits on Naveed's VERIFY checks.
>
> ### B. Start session 5 (Claude)
> 1. Read this box.
> 2. `git checkout main && git pull`, then `cd backend && uv sync --all-packages && make check` → 368 passed.
> 3. Push guard: push AND `gh pr create` go inside `if [ -z "$(gh pr list --head $B --state merged)" ]`.
> 4. **Handbook for Docker/evals.** Start it with:
>    ```
>    NODE_OPTIONS="--network-family-autoselection-attempt-timeout=3000" KSOR_ALLOWED_HOSTS=localhost,127.0.0.1,host.docker.internal,localhost:8080,127.0.0.1:8080,host.docker.internal:8080 npm run serve
>    ```
> 5. **Paid runs:**
>    - run them detached, with `--concurrency 5`;
>    - run them from the MAIN folder, because a worktree has no `.env`;
>    - ask Naveed for "haan" first.
>
> ### C. Next (after the MVP)
> | # | Task | Who |
> |---|---|---|
> | N1 | TP recall: the R6c Diagnostics → prompt/rule work, or ADR-0013 (note_reviewer → gpt-5-mini) | Claude + Naveed "haan" |
> | N2 | Auth0 post-login Action for roles (`specs/08-api-gateway/AUTH0-SETUP.md`) | Naveed |
> | N3 | Phase 1 B/C: wazuh-mcp reads LIVE Wazuh alerts (the lab is at `../wazuh-docker/single-node`; never `down -v`) | plan first |
> | N4 | Phase 4: the handbook chat widget + login (then `AUTH_MODE=auth0`) | plan first |
> | N5 | Phase 8: Azure deploy from the GHCR images | plan first |
>
> ### D. Waiting on Naveed
> 1. **Rotate the Tavily key** (pasted in chat) and the old OpenAI/Anthropic keys.
> 2. Verify VERIFY.md 02–11 (DoD item 1).
> 3. N2 (Auth0 roles Action).

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


---

## Session 1 — FINAL HANDOFF (2026-11-12, written at ~82% context, before Naveed clears the session)

## Last updated (ISO date-time, session number)
2026-11-12T13:45Z · session 1 (closed) · next: session 2

## Done this session (items + files + commit hashes)
**Planning and SDD (main from aa6468b):**
- Read the handbook (read only).
- Plan v1 → v2 (A1–A7) in `specs/00-final-plan.txt`.
- `CLAUDE.md`, `specs/constitution.md`, templates, PHR-0001…0013, ADR-0001…0009 (all Accepted).

| Feature | What | Commits / PRs |
|---|---|---|
| 01 foundation | uv workspace; soc-shared models (TriageNote rules), masking engine (field-aware + free text + property tests), settings; CI skeleton | `284b865`…`749a610` · PR #1, #2 |
| 02 evals-first | soc-evals: Rate (k/n = p%), scorers, targets, report, CLI; 40 alerts (34 synthetic + 6 OTRF, MIT), 95 probes, oracle/faulty recordings, review sheet; detection-gap finding (ADR-0009) | `faf6ab7`, `ab9f62f`, `e358978`, `bd11d95`, `2515540` · PR #3–#5 |
| 03 mcp-services | wazuh-mcp (fixture, 2 read-only tools), enrichment-mcp (AbuseIPDB, public IPs only, cache, budget) | `6282383`, `3e41e4c` · PR #6, #7 |
| 04 handbook-client | ksor-client (real KSOR wire shape, 5 statuses, `not_in_record` only on abstain), fake KSOR | `708bbc5` · PR #8 |
| 05 + 06 | agent-service: 6 agents, /ask handoff + /triage as_tool, all SDK primitives, all 4 guardrail kinds, MOCK ticket with approval, trace privacy | `89eb8bd` · PR #9 |
| 07 | agent-service internal FastAPI (SSE, internal token) | `aef382f` · PR #10 |
| 08 | api-gateway (Auth0/dev auth, roles, rate limit, CORS, SQLModel + Alembic, Fernet mask_map, audit, usage, budget) | `cdc9e15` · PR #11 |
| 09 + 10 | 4 Dockerfiles, compose, full CI (path filters, images, Trivy), gated release, deploy placeholder | `eb88573` · PR #11 |
| docs | LEARNING §1–13, CAREER-MAP rows 01–10, progress, PHRs | PR #12 |

## Current state (feature table 01–10: not started / intent / spec / plan / tasks / implementing / verified)
- 01 is verified.
- 02–10 are done; their tests pass in CI.
- Their human verification and the paid or live steps are pending (see the READ ME FIRST box, sections C and D).

## Decisions taken (link ADRs)
| ADR | Decision |
|---|---|
| 0001 | monorepo + uv workspace |
| 0002 | scope taxonomy, D-01 |
| 0003 | gpt-5-nano |
| 0004 | Tavily, wrapped in our own function tool |
| 0005 | Auth0 |
| 0006 | no sandbox |
| 0007 | masking + trace privacy |
| 0008 | SQLiteSession now, Postgres in Phase 8 |
| 0009 | eval data: synthetic + OTRF |

**Owner decisions:**
- the A1–A7 amendments;
- Q1–Q4 of feature 02, all "haan";
- blanket approval (PHR-0010);
- "code first, LLM later" (PHR-0012).

## Errors hit + fixes
All of them are listed in the two blocks above. The main ones:
- **Pushes to merged branches:** caught by the guard each time; new branches were made.
- **Masking:** the "Administrators" group was masked as a user.
- **httpx logged raw IPs** in request URLs.
- **Guardrail runs were not priced.**
- **In-memory sessions lost history** between runs.
- **SSE status codes:** errors inside the stream never became HTTP codes.
- **Alembic disabled the app loggers.**
- **The uv image tag did not exist.**
- **MCP host protection was off** inside containers.

## Pending / blocked (reason + who acts: Naveed or Claude)
See the READ ME FIRST box: section C (R1–R11) and section D (Naveed's manual actions).
The only CODE still missing: **R4 `soc_evals paid`** (Claude, session 2).

## Eval results so far (numbers)
- **Dry eval:** 135/135 = 100.0% valid. The oracle passes all 7 targets; the faulty recording fails exactly the planted checks.
- **Paid eval:** not run yet.
- **Labels verified:** 0/40 alerts, 0/95 probes.
- **Tests:** 307 pass, coverage 93.07%.
- **Spend so far:** $0.00 LLM (nothing paid has run).

## Exact next step for the next session
Follow the READ ME FIRST box, section B (start steps 1–5), then C/R1: ask Naveed for "haan" and run the first LIVE /ask while the handbook is running.
In parallel, if Naveed prefers, start R4 (`soc_evals paid` wiring, offline-tested with ScriptedModel) on a new branch `feat/11-live-eval`.

## Naveed's manual actions needed
See the READ ME FIRST box, section D:
- rotate the keys and set the $10 limit;
- the label review;
- the AbuseIPDB and Tavily keys;
- "haan" for R1, R2, R5, R7 and R10;
- Docker Desktop WSL integration;
- Auth0 when you want real login.


---

## Sessions 2–3 — 2026-11-12 / 2026-11-13

## Last updated (ISO date-time, session number)
2026-11-13T06:00Z · sessions 2–3 (session 3 began after a Claude Code restart). R5 running.

## Done this session (items + files + commit hashes)
**Feature 11 live-eval** (`specs/11-live-eval/`), PRs #13–#25:

| PR | What |
|---|---|
| #13/#14 | pipeline + AgentPipeline + estimate + pre-flight + guards (T11-01…08) |
| #15 | pilot-1 fixes: `format: uri` → str+pattern; `env_ignore_empty` (T11-09/10) |
| #16/#17 | pilot-2 findings; usage kept on errors; ledger-verified cap; one note retry; no handoff answers (T11-11…14) |
| #18/#19 | pilot-3 recordings; events in predictions + report Diagnostics (T11-15…17) |
| #20/#21 | diagnostic run; reviewer sees citations; rule-failure retry + policy_hints; /ask retry; scorer counts errors (T11-18…21) |
| #22/#23 | pilot 4; reviewer sees the masked analyst context; forced first search (T11-22/23) |
| #24 | VERIFY.md 07–10, live evidence 04–06, `specs/DOD-CHECK.md`, LEARNING §15, PHR-0017, .gitignore ledger |
| #25 | resumable paid runs: per-item journal, `--resume` (T11-24) |

PHRs: 0014, 0015, 0016, 0017. ADR: 0010 (accepted, updated).

## Current state (feature table 01–10: not started / intent / spec / plan / tasks / implementing / verified)
- 01 is verified.
- 02–10 are implemented, VERIFY filled, waiting for Naveed.
- 11 is implemented and live-piloted; R5 is running.

## Decisions taken (link ADRs)
- **ADR-0010:** two-key paid run, run cap $1.50, live KSOR, no AbuseIPDB mock, pilot first.
- **Naveed's answers:**
  - Q1: one corrective retry;
  - Q2: keep gpt-5-nano until the R5 data;
  - "jo best lga wo kro" → option A (code constraints, then a full baseline).

## Errors hit + fixes
- **Push to a merged branch** (`&&` after `gh`). Fixed by testing the output; PR create also goes inside the if-block (memory).
- **Live bugs T11-09…23.** See `tasks.md`.
- **First R5 attempt lost** with the session (~$0.017). Fixed with T11-24 (resumable, detached run).

## Pending / blocked (reason + who acts: Naveed or Claude)
- R5 → Claude.
- See the box, sections C and D.

## Eval results so far (numbers)
- **Pilots (6 items):**
  - the scope declines are exact every time;
  - masking holds: 0 raw IPs;
  - triage verdict quality is variable (needs_info vs TP);
  - the full escalation was correct after policy_hints.
- **R5:** pending.
- **Tests:** 354 passed, coverage 93.64%.
- **Spend:** $0.0765 before R5.

## Exact next step for the next session
Box §B3: finish or resume R5, then analyse it (Diagnostics) → the R6 plan (.txt) → Naveed "approved".

## Naveed's manual actions needed
See the box, section D.


---

## Session 4 — 2026-11-13 (late) / 2026-11-18

## Last updated (ISO date-time, session number)
2026-11-18 · session 4

## Done this session (items + files + commit hashes)

| PR | What |
|---|---|
| #25 | resumable runs |
| #26 | progress |
| #27 | `as_tool` sub-agents priced (the ledger was about 1/3 low; checked against the OpenAI CSV) |
| #28 | research `tool_choice` web_search → "required" |
| #29 | R5 report + R6 plan |
| #30 | no exception escapes the flows; report states the real leaks |
| #31 | P1 + P2 plan / ADR-0011 |
| #32 | **ADR-0011 scope → gpt-5-mini** |
| #33 | P2 results; one report per journal |
| #34 | the scope prompt follows ADR-0002; eval drafts go to a temp dir |
| #35 | `--concurrency`, `--item-timeout` |
| #36 (open) | URLs repaired out of citations; P3/P4 results; normalized URL check |

## Current state (feature table 01–10: not started / intent / spec / plan / tasks / implementing / verified)
- 01 is verified.
- 02–11 are implemented, with VERIFY filled.
- 11: the scope target is met in P3. Triage quality is open (R6b).

## Decisions taken (link ADRs)
- **ADR-0011:** scope_classifier → gpt-5-mini. Accepted, and its result is recorded.
- **"jo best lga wo kro":**
  - the labels are NOT changed (they come from ADR-0002 and the handbook);
  - the prompt is aligned with them;
  - the eval drafts are deleted.

## Errors hit + fixes
1. The first R5 attempt was lost with the session → resumable, detached runs.
2. The ledger undercounted (as_tool) → hooks.
3. `tool_choice` "web_search" gave HTTP 400 → "required"; a test now runs the real SDK converter.
4. The watcher matched itself → `[p]ython3`.
5. P3 hung on one HTTP call → a timeout per item.
6. URLs ended up in citations → a deterministic repair.
7. The URL check was exact-string → normalized.

## Pending / blocked (reason + who acts: Naveed or Claude)
See the box, sections C and D.

## Eval results so far (numbers)

| Run | Model setup | DECLINE | KSOR | RESEARCH | False declines | Leaks | $ |
|---|---|---|---|---|---|---|---|
| R5 | nano | 21/30 | 18/30 | — | 2/55 | 0 | 0.32 |
| P2 | scope = mini | 26/30 | 27/30 | 19/25 | 1/55 | — | 0.18 |
| P3 | + ADR-0002 prompt + Tavily | 29/30 | 26/30 | 19/25 | 3/55 | 0 | 0.19 |
| P4 | research only | — | — | 23/25 label; 11 ok, 11 blocked (9 = URL check, fixed in #36) | — | — | 0.11 |

Triage (R5): TP recall 3/21, precision 3/3, verdict accuracy 8/40.

## Exact next step for the next session
R6a: merge #36, then (with "haan") re-run the 25 research probes. Then write the ADR-0012 plan for triage.

## Naveed's manual actions needed
See the box, section D.


---

## Session 4 (continued) — 2026-11-18, MVP close

## Last updated (ISO date-time, session number)
2026-11-18 · session 4 (closing)

## Done this session (items + files + commit hashes)

| PR | What |
|---|---|
| #36 | citation-URL repair and URL normalization |
| #38 / #39 | ADR-0012 (triage → gpt-5-mini); the router key split |
| #40 | the handbook verdict rule |
| #41 | the reviewer accepts drafts that our rules allow |
| #42 | labels approved by delegation; EV-P014 → research |
| #43 | R6c results |
| #44 | Docker: the httpx dependency; gateway timeout 900 s; CI smoke-import |

Infrastructure:
- R7 Neon migrated.
- R8 `make up` / `demo-up` passed.
- R9 Auth0 configured.
- R10 GHCR release run 44250254761: success.

## Current state (feature table 01–10: not started / intent / spec / plan / tasks / implementing / verified)
- 01 is verified.
- 02–11 are implemented, with VERIFY filled (waiting for Naveed).
- MVP DoD 8/9.

## Decisions taken (link ADRs)
- ADR-0012 accepted.
- Labels approved by delegation (PHR-0018).
- Auth0 kept, instead of our own password store (Naveed, 2026-11-18).
- Wazuh lab later.

## Errors hit + fixes
1. The agent-service image crashed (missing httpx) → declared, plus a CI smoke-import.
2. The gateway ReadTimeout → 900 s.
3. The handbook gave 421 to containers → `KSOR_ALLOWED_HOSTS`.
4. The handbook lost Neon → `NODE_OPTIONS`.
5. A worktree run had no `.env` → $0, now documented.
6. A self-matching watcher → watch by PID.

## Pending / blocked (reason + who acts: Naveed or Claude)
See the box, sections C and D.

## Eval results so far (numbers)
- **R6c (triage = mini + verdict rule):**
  - TP recall 8/21;
  - precision 8/10;
  - verdict accuracy 17/40;
  - escalation condition 6/6.
- **P3 scope:**
  - DECLINE 29/30;
  - false declines 3/55;
  - leaks 0.
- **Ledger:** $2.56.

## Exact next step for the next session
N1 (TP recall, from the R6c Diagnostics), or Naveed picks the next phase (N3, N4 or N5).

## Naveed's manual actions needed
See the box, section D.
