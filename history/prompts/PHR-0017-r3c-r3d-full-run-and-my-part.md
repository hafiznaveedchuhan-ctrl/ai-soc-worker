# PHR-0017 — R3c/R3d fixes, pilot 4, the full run, and "do your part"
- Date: 2026-11-12 · Session: 2 · Stage: fix / verify
- Feature: 11 · Branches: fix/11-r3c-*, docs/11-pilot4, fix/11-r3d-constraints, docs/session2-close · Model: claude-opus-5-5

## Prompts (verbatim, short)
- "merged ni hoparha ha. chk kro kya issue ha.. baqi approved ha mare trf sa" → checked PR #18: MERGEABLE/CLEAN, CI green, no protection; the R3b work was approved and done (PR #19).
- "haan" → diagnostic run ($0.0063).
- "approved" → R3c (PR #21).
- "haan" → pilot 4 ($0.0139).
- "jo best lga wo kro" → option A, code part only (PR #22). A paid run still needs its own "haan".
- "haan but ya to btao kitna percent kaam remaining rhgya ha?" → R5 started (135 items, cap $1.50). Status: code ~95%, live ~80%, the whole project ~75%.
- "aap upna hissa ka sara kam krdo.. or ha,open ai ma credit ha abhi" → this docs work, in a separate git worktree so the running eval is not touched.
- "jo merge ni hwoa uska link bhjdo" → sent the PR #22 link.

## Response summary (what Claude did)
- **R3c:**
  - the LLM reviewer gets the citations;
  - a rule failure gets one retry, plus `policy_hints`;
  - an invalid `/ask` answer gets one retry at the specialist;
  - the scorer counts errors.
- **R3d:** the reviewer gets the masked analyst context; the specialists' first search is forced through `tool_choice`.
- **Docs:**
  - VERIFY.md for 07–10;
  - live evidence in VERIFY 04–06;
  - `specs/DOD-CHECK.md`;
  - LEARNING §15;
  - `.gitignore` now covers the local ledger and the sessions DB.
- **Guard nuance:** the push AND `gh pr create` must sit inside the guard's if-block (saved to memory).

## Files touched
- `backend/services/agent-service/src/agent_service/{flows,guardrails,agents_build,context}.py` and their tests
- `backend/evals/src/soc_evals/scoring/scope.py`
- `specs/0[4-9]*/VERIFY.md`, `specs/10-ci-cd/VERIFY.md`
- `specs/DOD-CHECK.md`
- `specs/11-live-eval/{tasks.md,VERIFY.md,R3c-plan.txt,R3d-decision.txt}`
- `.gitignore`
- `backend/docs/LEARNING.md`

## Decisions / outcomes (link ADRs)
- No model change yet.
- An ADR-0011 (one agent upgrade) will be decided from the R5 data.

## Follow-ups (who acts)
- Claude: analyse R5; propose R6.
- Naveed: merge the PRs; the label review; R7–R10; rotate the keys.
