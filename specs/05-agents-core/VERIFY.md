# VERIFY — 05 agents-core · Status: **filled (offline)** — live checks are Naveed's (CONFIRM=haan)
| Command (backend/) | You must see |
|---|---|
| `make check` | all green (290 tests) |
| `make demo-ask` | `[FAKE mode …]`, events scope → handoff → search_handbook → review ok, answer citing knowledge/windows-events/event-4625, cost $0 |
| `make demo-triage` | the approval prompt `APPROVAL NEEDED: create_escalation_ticket … [mock]` → answer y/N → a TriageNote in the handbook template ending "Final decision: human analyst" |
| `make demo-ask LIVE=1 Q="What does event 4625 mean?"` (no CONFIRM) | refused |
| LIVE (later, your "haan"): T1 `npm run serve`; T2 `make demo-ask LIVE=1 CONFIRM=haan Q="What does event 4625 mean?"` | a real gpt-5-nano answer with a stable_id, cost shown |
Real output (Claude, fake mode): demo-ask → `status: ok`, 5 LLM calls (scripted), `$0.000000`; demo-triage --approve → `status: ok`,
`Escalate: yes — condition #4`, `tickets: ['MOCK-…']`.
