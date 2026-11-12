"""A FAKE KSOR server with the real tool names and output shape (for offline tests).

Responses follow @panaversity/ksor SEARCH_OUTPUT / READ_OUTPUT / OUTLINE_OUTPUT. The passages are
short hand-written lab text, not the real handbook; feature 05 tests reuse this server.
"""

from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

PAGES: dict[str, tuple[str, str]] = {
    "knowledge/windows-events/event-4625": (
        "Event 4625 — An account failed to log on",
        "Event 4625 records a failed logon. Status 0xC000006A means a bad password.",
    ),
    "knowledge/playbooks/brute-force": (
        "Playbook — Brute force",
        "Many 4625 failures from one source in a short time suggest brute force (T1110).",
    ),
}


def _gov() -> dict[str, Any]:
    return {
        "status": "stable",
        "trust_tier": "human-reviewed",
        "verified": None,
        "effective_from": None,
        "stale_after": None,
        "approval": {"by": "human:naveed", "at": "2026-11-10T09:30:32Z", "checked": "policy"},
    }


def _prov(stable_id: str) -> dict[str, Any]:
    return {
        "corpus_id": "soc-handbook",
        "stable_id": stable_id,
        "slug": stable_id.split("/")[-1],
        "generation": 7,
        "retrieved_at": "2026-11-12T08:00:00Z",
    }


def build_fake_ksor(mode: str = "normal") -> MCPServer:
    """mode: normal | abstain | unavailable | unpublished | broken | long"""
    mcp = MCPServer("soc-handbook-fake")

    @mcp.tool()
    def search(query: str, k: int = 5) -> dict[str, Any]:
        """Search the record (fake)."""
        if mode == "broken":
            return {"unexpected": True}
        base: dict[str, Any] = {
            "ok": True,
            "abstained": False,
            "gate": "off",
            "top_cosine": 0.71,
            "hits": [],
            "snapshot": {
                "corpus_id": "soc-handbook",
                "generation": 7,
                "token": "snap-7",
                "expires_at": "2026-11-12T09:00:00Z",
            },
        }
        if mode == "abstain":
            return {**base, "abstained": True, "reason": "abstained"}
        if mode in ("unavailable", "unpublished"):
            return {
                **base,
                "ok": False,
                "reason": mode,
                "snapshot": None,
                "degraded_reason": "embed_unavailable" if mode == "unavailable" else None,
            }
        words = {w.strip("?.,").casefold() for w in query.split()}
        hits = []
        for sid, (title, text) in PAGES.items():
            if words & {w.casefold().strip(".,()") for w in text.split()}:
                content = text * 200 if mode == "long" else text
                hits.append(
                    {
                        "slug": sid.split("/")[-1],
                        "heading_path": title,
                        "content": content,
                        "rrf_score": 0.03,
                        "provenance": _prov(sid),
                        "governance": _gov(),
                        "extra_future_field": 1,
                    }
                )
        return {**base, "hits": hits[:k]}

    @mcp.tool()
    def read(
        slug: str, heading: str | None = None, token_budget: int | None = None
    ) -> dict[str, Any]:
        """Read a document (fake)."""
        for sid, (title, text) in PAGES.items():
            if sid.endswith("/" + slug) or sid == slug:
                return {
                    "slug": slug,
                    "title": title,
                    "text": text,
                    "frontmatter": None,
                    "governance": _gov(),
                    "sections": [title],
                    "provenance": _prov(sid),
                    "snapshot_status": "unpinned",
                    "next": None,
                }
        raise ToolError(f"no document {slug!r}")

    @mcp.tool()
    def outline(
        node: str | None = None, depth: int | None = None, limit: int = 50
    ) -> dict[str, Any]:
        """Outline the record (fake)."""
        nodes = [
            {
                "slug": sid.split("/")[-1],
                "kind": "doc",
                "title": t,
                "heading_path": t,
                "position": i,
                "depth": 1,
                "child_count": 0,
                "permalink": None,
                "has_content": True,
            }
            for i, (sid, (t, _)) in enumerate(PAGES.items())
        ]
        return {
            "nodes": nodes[:limit],
            "limit": limit,
            "offset": 0,
            "next_offset": None,
            "has_more": False,
        }

    return mcp
