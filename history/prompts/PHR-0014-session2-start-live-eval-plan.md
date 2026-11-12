# PHR-0014 — Session 2 start + R4 live-eval plan
- Date: 2026-11-12 · Session: 2 · Stage: plan
- Feature: 11 · Branch: feat/11-live-eval · Model: claude-opus-5-5

## Prompt (faithfully condensed)
Start session 2 per CLAUDE.md: read the progress.md handoff box (A–E) and the "Session 1 — FINAL HANDOFF" block. Then run the section-B start steps: fetch, checkout main, pull, status, log -3, `uv sync --all-packages` and `make check` (expect 307 passed).
Give a 3-line Roman-Urdu status.
Then start R4: wire `soc_evals paid` to the live pipeline (`agent_service.flows`) on the new branch `feat/11-live-eval`. Test it offline with ScriptedModel first, and give a cost estimate before any real run. No paid or live call without "haan". The merged-branch guard runs before every push. The plan goes in a .txt file before approval.

## Response summary (what Claude did)
- Start steps: main = `5e41533` (merge of PR #12), clean; `make check` → 307 passed, coverage 93.07%.
- Gave the 3-line status.
- Created the branch `feat/11-live-eval`.
- Read the CLI stub, the predictions, the scorers, the flows, the offline testing and the demo script.
- Wrote the plan: intent, FR-11-01…11, design, tasks T11-01…08, a cost estimate (expected ~$0.36, pessimistic ~$1.00 for the full run) and Q1–Q3.

## Files touched
- `specs/11-live-eval/00-plan.txt` (new)
- this PHR

## Decisions / outcomes (link ADRs)
- Proposed (not yet approved):
  - live KSOR;
  - no AbuseIPDB mock in the eval;
  - a run-wide cap of $1.50;
  - a pilot before the full run;
  - ADR-0010 to come.

## Follow-ups (who acts)
- Naveed: "approved" (or changes) on `specs/11-live-eval/00-plan.txt`, plus answers to Q1–Q3.
- Claude: after approval, T11-01…08, offline only.
