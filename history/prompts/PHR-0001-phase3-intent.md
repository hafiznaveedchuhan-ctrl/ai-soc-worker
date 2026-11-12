# PHR-0001 — Phase 3 intent: soc-worker backend (AI SOC Triage Copilot)
- Date: 2026-11-12T~05:00Z · Session: 1 · Stage: intent
- Feature: all · Branch: main (read only) · Model: claude-opus-5-5

## Prompt (faithfully CONDENSED — the original is a 15-section intent, about 10k characters)
- §0 Context: Naveed is the human principal and only approver (10-80-10). Repo `~/ai-soc/soc-worker` (GitHub ai-soc-worker); sibling
  `../handbook` = finished KSOR v0.0.61 (141 stable docs) over MCP at 127.0.0.1:8080, read only. Goal: AI workers answer SOC questions
  and triage Wazuh alerts using KSOR + IP enrichment + trusted cyber sources; cited triage notes; a human decides. A learning and portfolio
  project for Option 1 (AI Engineer) and Option 2 (SOC Analyst). SDD like a Forward Deployed Engineer, with ADRs and PHRs. Plan mode first.
- §1 Read first: handbook progress HANDOFF, instance.md, invariants, data-handling, note-template, playbooks, content.ts, evals; this repo. 10-bullet summary, then wait for "go".
- §2 Hard rules: never touch .env; no paid/external call without "haan"; the smallest OpenAI model by default, $10 cap, a per-run budget guard,
  log tokens + cost; read-only, AI suggests / human decides; mask IP/user/host/email before any LLM or web call (mask_map in our DB only);
  public IPs only to AbuseIPDB; cite stable_id / "unverified web source" / "not in this record"; web content untrusted; check library APIs in docs;
  never modify ../handbook or ../wazuh-docker; feat/NN branches, push only on "push", Naveed merges; free tiers only.
- §3 Agents: Triage (router/coordinator), SOC Handbook, Cyber Research (trusted domains only, unverified label, writes suggestions/), Scope Classifier
  (in the input guardrail), Note Reviewer (in the output guardrail). /ask = handoff flow; /triage = as_tool flow + tools. All four guardrail kinds; the exact
  decline text. Primitives: function_tool, output_type, MCP, handoff vs as_tool, needs_approval mock ticket, sessions, tracing, model routing,
  context, hooks, run/run_streamed, max_turns. No sandbox (ADR).
- §4 Microservices: api-gateway, agent-service, wazuh-mcp, enrichment-mcp + soc-shared; evals/, suggestions/, docs/.
- §5 DB: Neon `soc_worker`, the tables listed, the TriageNote fields. §6 Auth: ADR (Auth0 vs one alternative), JWT/JWKS, dev mode; Naveed creates the tenant.
- §7 Docker: multi-stage uv, slim 3.12, non-root, HEALTHCHECK, Trivy. §8 CI/CD: ci.yml with path filters; release.yml → GHCR after "haan"; deploy.yml disabled.
- §9 Features 01–10, each INTENT → spec → plan → tasks → approval → implement → VERIFY → check; eval targets (TP recall ≥95%, precision ≥80%,
  100% cited, decline ≥90% / ≤10% false declines). §10 LEARNING.md + CAREER-MAP.md. §11 progress.md protocol (9 exact headings, append-only).
- §12 Final plan as .txt. §13 Manual actions. §14 Done when. §15 Start in plan mode.

## Response summary
Read every listed handbook file READ ONLY; gave the 10-bullet summary; found the conflict between the vendor probes and the new 3-outcome Scope Guard and asked about it (→ PHR-0002).

## Files touched
None in the repos (plan mode). Plan file in `~/.claude/plans/`.

## Decisions / outcomes
The handbook gate OFF ⇒ the worker's Scope Guard must decline (later ADR-0002).

## Follow-ups
Naveed: answer D-01, say "go".
