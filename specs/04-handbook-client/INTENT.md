# INTENT — 04 handbook-client
Status: **approved** by human:naveed 2026-11-12 (blanket approval, PHR-0010) · Plan of record: `../00-final-plan.txt` §10

## Goal
A typed Python client for the handbook's KSOR MCP server (`search` / `read` / `outline` at `http://127.0.0.1:8080/mcp`) that
turns every search hit into a `KsorHit` with its `provenance.stable_id`, handles `gate: "off"` and the three "no answer" cases
honestly (abstained ≠ unavailable ≠ unpublished), and caps what reaches a prompt. Plus a 2-terminal smoke demo.

## Constraints
- The wire shape is taken from the installed `@panaversity/ksor` gateway (`SEARCH_OUTPUT`, `READ_OUTPUT`, `OUTLINE_OUTPUT`; read only).
- Tests use a FAKE KSOR server (an in-memory MCPServer with the same tool names and output shape) → free, offline.
- A live `search` embeds the query with OpenAI (the handbook's key; tiny cost) → `make demo-handbook` refuses unless `CONFIRM=haan`, and Naveed must run `npm run serve` in ../handbook first.
- KSOR content is untrusted: the client never interprets it; it only caps size and keeps the stable_id.

## Success numbers
S1 tests 100% pass, coverage ≥ 85% · S2 every hit maps to a valid `knowledge/...` stable_id · S3 abstained/unavailable/unpublished are three different results · S4 the demo prints hits with stable_ids from the live record (Naveed runs it).

## Out of scope
Agent wiring (05), tool guardrails (06).
