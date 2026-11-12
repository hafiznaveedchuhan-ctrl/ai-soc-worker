# ksor-client

Typed client for the handbook's KSOR MCP server (`search` / `read` / `outline`, default `http://127.0.0.1:8080/mcp`).
**Backend part:** shared library (no service, no image). The single place that knows the KSOR wire shape
(`@panaversity/ksor` SEARCH_OUTPUT / READ_OUTPUT / OUTLINE_OUTPUT).

```python
from ksor_client.client import KsorClient, not_in_record, search_once

async with KsorClient("http://127.0.0.1:8080/mcp") as k:
    out = await k.search(
        "What does event 4625 mean?"
    )  # SearchOutcome(status="hits", hits=[KsorHit(stable_id=...)])
out = await search_once(url, "query")  # never raises; unreachable → status="unavailable"
```
`status` is one of `hits`, `abstained` (only this means "not in this record"), `unavailable`, `unpublished`, `error`.
Tests use `ksor_client.testing.build_fake_ksor()` (in memory, offline). Live demo: `make demo-handbook Q="..." CONFIRM=haan`
after `npm run serve` in ../handbook (each search embeds the query with OpenAI → tiny cost). No env vars of its own.
