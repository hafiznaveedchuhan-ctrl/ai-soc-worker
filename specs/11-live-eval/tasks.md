# tasks — 11 live-eval
Status: **approved** (Naveed, 2026-11-12, PHR-0015) · Plan: ./plan.md
Legend: [ ] todo · [~] in progress · [x] done · ⬆ = commit + push (run the merged-branch guard first)

| ID | Task | Satisfies | Done when |
|---|---|---|---|
| [x] T11-01 | SDD files and ADR-0010 | — | the files exist |
| [x] T11-02 | Docs check, noted in plan.md | rule | noted |
| [x] T11-03 | `pipeline.py` and fake-pipeline tests ⬆ | FR-11-04/05/06 | tests pass |
| [x] T11-04 | `live.py` AgentPipeline and ScriptedModel offline tests | FR-11-02/03/04/10/11 | tests pass |
| [x] T11-05 | `cli.py paid` and `estimate`; refusal tests; end-to-end offline test | FR-11-01/07/09 | tests pass |
| [x] T11-06 | `preflight()` test (server up and down) ⬆ | FR-11-08 | tests pass |
| [x] T11-07 | Makefile, README, LEARNING §14, CAREER-MAP row 11 | — | docs done |
| [x] T11-08 | `make check` green, plus `eval-estimate` and `eval-dry` output in VERIFY.md ⬆ | all | VERIFY filled |

**Added after the first pilot (2026-11-12, R3; Naveed was told the same day):**

| ID | Task | Satisfies | Done when |
|---|---|---|---|
| [x] T11-09 | `WebSource.url`: change `HttpUrl` to a str with a pattern. OpenAI strict output rejects `format: uri` (HTTP 400). Add a schema-format regression test (output types + tool params). | pilot | `test_live_schemas` passes |
| [x] T11-10 | `BaseServiceSettings`: set `env_ignore_empty=True`, so that a blank `AGENT_MODEL_DEFAULT=` falls back to the default (the empty value gave model `` and HTTP 404). Add a test. | pilot | test passes |

**R3 plan (`R3-pilot-findings-plan.txt`), approved by Naveed on 2026-11-12. Q1: one retry. Q2: keep gpt-5-nano.**

| ID | Task | Satisfies | Done when |
|---|---|---|---|
| [x] T11-11 | `flows`: on an `AgentsException`, return status `error` and keep the usage. `run_all` caps on max(reported, ledger delta); the report shows both. | F1 | tests pass |
| [x] T11-12 | An `invalid_final_output` error handler captures the rule messages (never the values). `run_triage` then makes ONE corrective retry. | F2 | tests pass |
| [x] T11-13 | Prompts: no handoff sentence as the answer; a fixed text when web search is unavailable. The deterministic review blocks handoff sentences. | F3 | tests pass |
| [x] T11-14 | Real pilot numbers go into VERIFY §7 and ADR-0010. | — | docs done |

**R3b plan (`R3b-diagnosis-plan.txt`, PR #18), approved by Naveed on 2026-11-12.**

| ID | Task | Satisfies | Done when |
|---|---|---|---|
| [x] T11-15 | Store `events` in the predictions, scrubbed by `safe_events`. A failed review says which check failed: `review FAILED by rules` or `by llm reviewer`, plus the problems. `run_ask` logs the review problems. The report gets a "Diagnostics" section. The dry recordings were regenerated; the only change is `events: []`, which a script proved. | diagnosis | tests pass |
| [x] T11-16 | Pilot-2 P056 text against `HANDOFF_RE`: NOT matched. The pilot-3 block of P056 therefore has another cause. The next diagnostic run will show which. P021's "Transferring…" text matches, as intended. | regression check | done (offline) |
| [x] T11-17 | Pilot-3 recordings and report committed (PR #18). | — | done |

**R3c plan (`R3c-plan.txt`), approved by Naveed on 2026-11-12.**

| ID | Task | Satisfies | Done when |
|---|---|---|---|
| [x] T11-18 | The LLM reviewer gets the full AskAnswer draft (`reviewer_text`): answer, citations, web sources, not_in_record. | EV-P056 | `test_llm_reviewer_sees_the_citations` |
| [x] T11-19 | A deterministic-rules review failure gets the ONE corrective retry; LLM-reviewer rejections are not retried. Adds the code-computed `policy_hints` (level ≥ 12 → condition 1). | EV-A034 | `test_rules_failure_gets_one_corrective_retry_then_ok`, `test_llm_reviewer_rejection_is_not_retried` |
| [x] T11-20 | `/ask`: ONE retry at the chosen specialist on an invalid AskAnswer; no second scope classifier call. | EV-P021 | `test_invalid_ask_answer_gets_one_retry_at_the_specialist` |
| [x] T11-21 | Scorer: a probe with an `error` is never "answered ok". | scorer gap | `test_a_fallback_answer_after_an_error_is_not_answered_ok` |

**R3d (`R3d-decision.txt`, PR from `docs/11-pilot4`). Naveed: "jo best lga wo kro" → option A, the code part. The full run still needs its own "haan".**

| ID | Task | Satisfies | Done when |
|---|---|---|---|
| [x] T11-22 | The TriageNote LLM reviewer also gets the masked rule facts and the analyst context (`ctx.review_input`). | EV-A003 | `test_triage_reviewer_sees_the_masked_analyst_context` |
| [x] T11-23 | The handbook and research agents must call their search tool first (`tool_choice`), and the SDK resets it afterwards. Checked: `openai_responses.py:1833` maps a tool name to `{"type": "function", "name": …}`; `tool_execution.py:562` resets it. | EV-P056 | `test_specialists_must_search_first_then_choice_resets` |

**Found in session 3: R5 was lost when the Claude session ended.** About $0.017 was spent, and no prediction was saved, because the journal was written only at the end. Naveed had already said "do your part" and "continue"; this is a free robustness fix.

| ID | Task | Satisfies | Done when |
|---|---|---|---|
| [x] T11-24 | Resumable paid runs: `run_all(sink=…)` appends each prediction to `recordings/paid/<date-HHMM-sha>-*.jsonl` at once. `--resume <stem>` / `make eval RESUME=<stem>` skips the done items, and their cost counts toward the cap. Output is unbuffered. The run is started with `setsid nohup`, so it survives the session. | R5 robustness | 4 new tests; `make check` 354 passed |

**Found by validating against Naveed's OpenAI usage CSV (2026-11-13):**
- The CSV shows gpt-5-nano at 583k in / 411k out tokens, about $0.18 at list price. The ledger held about $0.12 at the same time.
- The R5 log showed 0 `soc_handbook_agent` calls inside `/triage`.

| ID | Task | Satisfies | Done when |
|---|---|---|---|
| [x] T11-25 | `handbook.as_tool(..., hooks=nested_hooks)` and the same for research, so the sub-agent calls reach the ledger, the per-item budget and the run cap. `openai expense/` is gitignored. | cost guard accuracy | `test_as_tool_sub_agent_calls_are_priced` (fails without the fix); 355 passed |
| [x] T11-26 | R5 bug (my T11-23 mistake): `tool_choice="web_search"` is a name the SDK reserves for the HOSTED tool → HTTP 400 for every research probe. Research now uses `tool_choice="required"`. A new test runs the SDK's real `Converter.convert_tool_choice` on every agent (it FAILS on the old code). | R5 400s | 356 passed |

**R6 plan (`R6-plan.txt`), approved by Naveed on 2026-11-13. Free part:**

| ID | Task | Satisfies | Done when |
|---|---|---|---|
| [x] T11-27 | `run_ask` and `run_triage` catch ANY exception (e.g. an `openai.BadRequestError`) → status error, with the usage and events kept (`unexpected <Type>: …`). | R5 gap 2a | 2 tests |
| [x] T11-28 | The report gets a "How to read the rates" section: real leaks found, errored alerts and probes. | R5 misread 87% | 1 test; 359 passed |
- ADR-0011 accepted (2026-11-13): scope_classifier → gpt-5-mini (settings default); probes re-run P2.

**After P2. Naveed said "jo best lga wo kro".**
- The labels are NOT changed: they come from ADR-0002 and the handbook's `wave1-out-of-scope.txt`.
- EV-P014 (the Palo Alto policy is DECLINE while the Cisco ASA ACL is research) is an ADR-0002 inconsistency, left for Naveed's label review.

| ID | Task | Satisfies | Done when |
|---|---|---|---|
| [x] T11-29 | The scope prompt names the ADR-0002 DECLINE categories that it missed: malware-sample analysis (unpack, decompile, YARA for a malware family), phishing campaigns against people, product/vendor comparisons and buying advice. The near-miss vendor configuration stays research. | P2 misses | prompt test |
| [x] T11-30 | Eval runs write KSOR-suggestion drafts into a temp folder, never into `backend/suggestions/`. The 33 untracked eval drafts of 2026-11-13 were deleted (`.gitkeep` kept). | hygiene | 360 passed |
| [x] T11-31 | Paid runs go faster and cannot hang. `--concurrency` (default 5) uses a semaphore; the cap is checked before each item starts; results are sorted. `--item-timeout` (default 900 s) uses `asyncio.wait_for`; a timeout becomes an item error. Background: P3 hung for 14+ min on one HTTP call, and R5 took 3.5 h one item at a time. | speed + robustness | 3 tests; 363 passed |
