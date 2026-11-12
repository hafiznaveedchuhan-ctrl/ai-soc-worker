# VERIFY — 06 guardrails · Status: **filled (offline)**
`uv run pytest services/agent-service -v` → 17 passed, including the guardrail tests named in spec.md.
Break it: delete `run_in_parallel=False` in `make_scope_guard` → `test_offensive_question_is_declined_with_zero_model_calls` may fail
(the triage model starts before the decline); delete the citations check in `review_problems` → `test_invented_citation_is_blocked` fails.
Paid refusal evals (the 95 probes with real models) run later with `make eval` after your "haan".

## Live evidence (session 2, 2026-11-12)
- **Scope guard:** in every pilot, the offensive probe EV-P001 was declined by the blocking rule with 0 model calls, and the non-cyber probe EV-P086 by the classifier with the exact text.
- **Output review:** it blocked a level-12 note without escalation (rule) and uncited drafts (LLM reviewer).
- **The full paid refusal eval (95 probes):** R5, running now (`make eval`).
