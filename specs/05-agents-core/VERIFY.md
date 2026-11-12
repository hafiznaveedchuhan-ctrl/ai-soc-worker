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

## Live evidence (session 2, 2026-11-12, Naveed "haan")
Both flows ran LIVE with gpt-5-nano in pilots 2–4 (`make eval-pilot`).
- **Handoff and tools:** `/ask` handed off to the handbook and research agents; `/triage` used `ask_handbook`, `ask_research` and the MOCK ticket. The ticket was REJECTED by the eval approver.
- **Masking held:** 0 raw IPs in every recording.
- **Spend matched:** spend per item was recorded and equals the ledger (from R3, T11-11).
- **Live problems found and fixed:**
  - the `format: uri` schema (HTTP 400);
  - the blank model env (HTTP 404);
  - lost usage on errors;
  - invalid notes and answers: one corrective retry;
  - the reviewer missed citations and context;
  - specialists did not search.
  
  See feature 11 tasks T11-09…23.
