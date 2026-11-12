# PHR-0003 — Plan v1 approved with amendments A1–A7 → plan v2
- Date: 2026-11-12 · Session: 1 · Stage: plan
- Feature: all · Branch: main · Model: claude-opus-5-5

## Prompt (verbatim, condensed formatting only)
"Plan reviewed. Approved WITH these amendments — add them, then write specs/00-final-plan.txt and STOP:
1. MVP MILESTONE: Features 01–06 + a terminal demo of both flows (/ask and /triage via CLI with mocked + one real run) = MVP, target date 2026-11-25. Features 07–10 come after the MVP. Add this milestone to sections 10 and 13.
2. TRACING PRIVACY: Agents SDK tracing exports to the OpenAI platform. Only masked data may appear in traces; disable sensitive-data capture in traces (verify the exact SDK setting in current docs). Record in ADR-0007 and add a test that a raw IP never appears in a trace/span payload.
3. SESSIONS: SQLiteSession in agent-service is fine for Phase 3 (local). In ADR-0008 note that container restarts lose it and Phase 8 (Azure, replicas) needs a Postgres/SQLAlchemy-backed session.
4. D-01 APPROVED by me: vendor configuration/query-language questions (KQL, SPL, etc.) = ALLOW_CYBER_RESEARCH, concepts and defensive detection logic only, never step-by-step device configuration and never offensive use.
5. EVAL REPORTING: every rate is reported as count AND percent (e.g. 24/25 = 96%), with the size of each set.
6. Prompt-injection probes (+5 DECLINE): approved.
7. Root scaffold cleanup (delete root pyproject.toml and src/soc_worker/): approved, in feature 01.
Everything else stays as written. Write the .txt, show me its full content, then STOP for my 'approved'."

## Response summary
Checked in Context7: `RunConfig.trace_include_sensitive_data` (default True) + env `OPENAI_AGENTS_TRACE_INCLUDE_SENSITIVE_DATA`. Added A1–A7 to the
plan (header, §2, §3, §4, §6, §10, §12, §13, §16); wrote v2 to `specs/00-final-plan.txt`; showed the full content; stopped.

## Files touched
`specs/00-final-plan.txt` (v2).

## Decisions / outcomes
MVP = 01–06 + CLI demos by 2026-11-25; tracing privacy (code + env) → ADR-0007; SQLite sessions now / Postgres in Phase 8 → ADR-0008; D-01 approved → ADR-0002;
count+percent reporting; +5 injection probes; root cleanup in 01.

## Follow-ups
Naveed: "approved" for v2.
