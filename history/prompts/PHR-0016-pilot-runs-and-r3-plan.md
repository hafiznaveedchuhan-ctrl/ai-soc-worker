# PHR-0016 — Paid pilot runs, the fixes, and the R3 plan
- Date: 2026-11-12 · Session: 2 · Stage: verify / fix
- Feature: 11 · Branch: fix/11-pilot-fixes · Model: claude-opus-5-5

## Prompt (verbatim)
1. "npm run serve krdya ha .server on hogya ha"
2. "haan" — the pilot
3. "haan" — the re-run of the pilot after the fixes

## Response summary (what Claude did)
- Ran the free pre-flight check (3 tools). Did not treat "server on" as approval; asked for "haan" first.
- **Pilot 1 ($0.00).** 5 of the 6 items were rejected before any tokens:
  - HTTP 400: the `format: uri` from `WebSource.url: HttpUrl`;
  - HTTP 404: the blank `AGENT_MODEL_DEFAULT=` gave an empty model name.
- Fixed both (T11-09, T11-10) with a regression test, and opened PR #15.
- **Pilot 2.** The ledger shows $0.013576 in total.
  - EV-A003 ok, but the verdict was needs_info instead of TP.
  - EV-A034 failed with ModelBehaviorError (a TriageNote rule was broken).
  - The probes scoped correctly. The research answer was a handoff sentence.
  - The report undercounted the spend, because the usage was lost on the exception.
- Wrote the R3 plan: `specs/11-live-eval/R3-pilot-findings-plan.txt`.

## Files touched
- `backend/packages/soc-shared/src/soc_shared/{models/note.py,settings.py}`
- `backend/services/agent-service/tests/test_live_schemas.py`
- `backend/evals/recordings/paid/*`
- `backend/evals/reports/2026-11-12-paid-pilot-report.md`
- `specs/11-live-eval/{tasks.md,R3-pilot-findings-plan.txt}`

## Decisions / outcomes (link ADRs)
- No model change.
- Re-estimate for the full run: about $0.29 (pessimistic $0.60), about 1.5–2 h.

## Follow-ups (who acts)
- Naveed: "approved" (or changes) on the R3 plan, plus Q1 and Q2; merge PR #15.
