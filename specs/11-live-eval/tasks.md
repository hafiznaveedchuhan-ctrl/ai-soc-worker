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
