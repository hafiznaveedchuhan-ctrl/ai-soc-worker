"""`make demo-handbook Q="..." CONFIRM=haan` — one live search against the handbook KSOR server.

Terminal 1 (Naveed): cd ../handbook && npm run serve   (127.0.0.1:8080)
Each live search embeds the query with OpenAI on the handbook side (tiny cost) → needs CONFIRM=haan.
"""

import argparse
import asyncio
import os

from ksor_client.client import not_in_record, search_once

DEFAULT_URL = "http://127.0.0.1:8080/mcp"


async def main(query: str, url: str) -> None:
    if os.environ.get("CONFIRM") != "haan":
        raise SystemExit(
            "refused: a live handbook search costs an embedding call — run with CONFIRM=haan"
        )
    out = await search_once(url, query)
    print(
        f"query : {query}\nstatus: {out.status}   gate: {out.gate}   snapshot: {out.snapshot_token}"
    )
    if out.reason:
        print(f"reason: {out.reason}")
    if not_in_record(out):
        print("→ not in this record (the handbook abstained)")
    for i, h in enumerate(out.hits[:5], start=1):
        print(f"\n{i}. {h.stable_id}   score={h.score:.4f}\n   {h.heading}\n   {h.snippet[:200]}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("query")
    p.add_argument("--url", default=os.environ.get("HANDBOOK_MCP_URL", DEFAULT_URL))
    a = p.parse_args()
    asyncio.run(main(a.query, a.url))
