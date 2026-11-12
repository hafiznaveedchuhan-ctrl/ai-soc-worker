# PHR-0011 — Feature 04 handbook-client (continued under the blanket approval of PHR-0010)
- Date: 2026-11-12T10:05Z–10:40Z · Session: 1 · Stage: spec → implement → verify
- Feature: 04 · Branch: feat/04-handbook-client · Model: claude-opus-5-5

## Prompt
No new prompt: this continued "continue plz and approved for all your permission" (PHR-0010).

## Response summary
- Read the KSOR gateway output schemas from `../handbook/node_modules/@panaversity/ksor/dist` (read only): SEARCH_OUTPUT (ok, abstained,
  reason ∈ abstained/unavailable/unpublished, gate "off"|{floor}, hits[provenance.stable_id, governance.trust_tier, …], snapshot),
  READ_OUTPUT, OUTLINE_OUTPUT.
- Built `ksor-client`:
  - wire models;
  - KsorClient (search/read/outline with the server's input limits);
  - SearchOutcome with five statuses; `not_in_record()` is true only for abstained;
  - snippet cap; `search_once()`, which never raises;
  - a fake KSOR server for offline tests.
- `make demo-handbook` needs CONFIRM=haan (the handbook embeds each query with OpenAI). Claude ran no live search.
- Removed a placeholder test that asserted nothing, and wrote a real unreachable-server test.

## Files touched
backend/packages/ksor-client/**, backend/scripts/demo_handbook.py, backend/{pyproject.toml,Makefile,uv.lock},
backend/docs/{LEARNING,CAREER-MAP}.md, specs/04-handbook-client/*, progress.md.

## Follow-ups
Naveed: the live 2-terminal demo (`npm run serve` + `make demo-handbook ... CONFIRM=haan`), and merging the PRs. Claude: feature 05.
