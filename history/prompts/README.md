# PHR — Prompt History Records

One file per significant prompt from Naveed (an intent, approval, amendment, decision, correction or bug report).
Name: `PHR-NNNN-<slug>.md` (4 digits, never reused). PHRs are append-only; a correction is a new PHR.
Never put secrets, keys or unmasked personal data in a PHR.

## Index
| PHR | Date | Stage | Feature | Title |
|---|---|---|---|---|
| [0001](PHR-0001-phase3-intent.md) | 2026-11-12 | intent | all | Phase 3 intent: soc-worker backend |
| [0002](PHR-0002-summary-and-d01.md) | 2026-11-12 | clarify | 02/06 | Read-first summary, Roman Urdu recap, D-01 scope decision |
| [0003](PHR-0003-plan-v2-amendments.md) | 2026-11-12 | plan | all | Plan v1 approved with amendments A1–A7 → v2 |
| [0004](PHR-0004-v2-approved-sdd-push-rhythm.md) | 2026-11-12 | plan → spec | 01 | v2 approved; strong SDD docs; push every 3–4 steps |
| [0005](PHR-0005-feature01-approved-implemented.md) | 2026-11-12 | implement → verify | 01 | Feature 01 docs approved; implemented T01-01…15 |
| [0006](PHR-0006-verified-merge-error.md) | 2026-11-12 | verify → fix | 01 | Verified; draft-PR merge error fixed; pushed-after-merge incident + guard |
| [0007](PHR-0007-env-and-feature02-docs.md) | 2026-11-12 | spec | 02 | .env created/filled safely; PR #2 merged; feature 02 docs |
| [0008](PHR-0008-feature02-implementation.md) | 2026-11-12 | implement | 02 | 02 approved; scorer, probes, 30 alerts; PR #3 merged mid-feature → part2 branch |
| [0009](PHR-0009-all-haan-otrf-ruleset.md) | 2026-11-12 | implement → verify | 02 | "all haan": ruleset + OTRF → 40 alerts; detection gap; VERIFY filled |
| [0010](PHR-0010-feature03-mcp-services.md) | 2026-11-12 | spec → implement → verify | 03 | Blanket approval; wazuh-mcp + enrichment-mcp; httpx log leak fixed |
| [0011](PHR-0011-feature04-handbook-client.md) | 2026-11-12 | implement → verify | 04 | ksor-client from the real wire shape; three kinds of no-answer |
| [0012](PHR-0012-code-first-then-llm.md) | 2026-11-12 | implement | 05–10 | Code first, LLM later; agents + guardrails offline |
| [0013](PHR-0013-features-07-10.md) | 2026-11-12 | implement | 07–10 | agent API, gateway, Docker, CI/CD |

## Template
```markdown
# PHR-NNNN — <title>
- Date: <ISO> · Session: <n> · Stage: intent | clarify | plan | spec | tasks | implement | verify | fix | retro
- Feature: NN · Branch: <branch> · Model: <model id>

## Prompt (verbatim if short; faithfully condensed if long — mark which)
## Response summary (what Claude did)
## Files touched
## Decisions / outcomes (link ADRs)
## Follow-ups (who acts)
```
