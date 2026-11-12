"""KsorClient — search / read / outline over MCP, with honest "no answer" handling (feature 04).

Handbook rule (instance.md): "not in this record" is a correct answer — but ONLY when the record
abstained. "unavailable" (retrieval failed) and "unpublished" (nothing ingested) say nothing about
coverage, so they must never be reported as absence.
KSOR content is UNTRUSTED data: this client never interprets it; it only caps its size.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

from mcp import Client
from mcp.server.mcpserver import MCPServer
from pydantic import ValidationError
from soc_shared.models import KsorHit

from ksor_client.models import KsorOutlineResponse, KsorReadResponse, KsorSearchResponse

Status = Literal["hits", "abstained", "unavailable", "unpublished", "error"]
SNIPPET_CAP = 1200
TRUNCATED = " …[truncated]"


@dataclass(frozen=True)
class SearchOutcome:
    status: Status
    hits: list[KsorHit] = field(default_factory=list)
    gate: Literal["off", "on"] = "off"
    snapshot_token: str | None = None
    reason: str | None = None


def not_in_record(outcome: SearchOutcome) -> bool:
    """True only when the record itself said it does not cover the question."""
    return outcome.status == "abstained"


def _cap(text: str, cap: int) -> str:
    return text if len(text) <= cap else text[: cap - len(TRUNCATED)] + TRUNCATED


class KsorError(Exception):
    """A read/outline problem (search never raises; it returns a SearchOutcome)."""


class KsorClient:
    def __init__(
        self, target: str | MCPServer, timeout: float = 20.0, snippet_cap: int = SNIPPET_CAP
    ) -> None:
        self._target = target
        self._timeout = timeout
        self._cap = snippet_cap
        self._client: Client | None = None

    async def __aenter__(self) -> "KsorClient":
        self._client = Client(self._target, read_timeout_seconds=self._timeout)
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc: object) -> None:
        if self._client is not None:
            await self._client.__aexit__(*exc)  # type: ignore[arg-type]
            self._client = None

    async def _call(self, tool: str, args: Mapping[str, Any]) -> dict[str, Any]:
        if self._client is None:
            raise KsorError("use `async with KsorClient(...)`")
        result = await self._client.call_tool(tool, dict(args))
        if result.is_error or result.structured_content is None:
            text = " ".join(getattr(c, "text", "") for c in result.content)[:300]
            raise KsorError(f"{tool} failed: {text or 'no structured content'}")
        return dict(result.structured_content)

    async def search(self, query: str, k: int = 5) -> SearchOutcome:
        if not 1 <= len(query) <= 2000:
            return SearchOutcome("error", reason="query must be 1-2000 characters")
        if not 1 <= k <= 10:
            return SearchOutcome("error", reason="k must be 1-10")
        try:
            raw = await self._call("search", {"query": query, "k": k})
            resp = KsorSearchResponse.model_validate(raw)
        except KsorError as exc:
            return SearchOutcome("error", reason=str(exc))
        except ValidationError:
            return SearchOutcome("error", reason="unexpected KSOR response shape")
        except Exception as exc:  # transport: connection refused, timeout, …
            return SearchOutcome("unavailable", reason=f"KSOR unreachable ({type(exc).__name__})")
        gate: Literal["off", "on"] = "off" if resp.gate == "off" else "on"
        token = resp.snapshot.token if resp.snapshot else None
        if resp.reason in ("unavailable", "unpublished"):
            return SearchOutcome(resp.reason, gate=gate, reason=resp.degraded_reason or resp.note)
        if resp.abstained or not resp.hits:
            return SearchOutcome("abstained", gate=gate, snapshot_token=token)
        hits = [
            KsorHit(
                stable_id=h.provenance.stable_id,
                title=h.heading_path,
                snippet=_cap(h.content, self._cap),
                score=h.rrf_score,
                gate=gate,
                heading=h.heading_path,
            )
            for h in resp.hits
        ]
        return SearchOutcome("hits", hits=hits, gate=gate, snapshot_token=token)

    async def read(
        self,
        slug: str,
        heading: str | None = None,
        snapshot_token: str | None = None,
        token_budget: int | None = None,
    ) -> KsorReadResponse:
        if token_budget is not None and not 100 <= token_budget <= 70000:
            raise KsorError("token_budget must be 100-70000")
        args: dict[str, Any] = {"slug": slug}
        for key, value in (
            ("heading", heading),
            ("snapshot_token", snapshot_token),
            ("token_budget", token_budget),
        ):
            if value is not None:
                args[key] = value
        return KsorReadResponse.model_validate(await self._call("read", args))

    async def outline(
        self, node: str | None = None, depth: int | None = None, limit: int = 50
    ) -> KsorOutlineResponse:
        args: dict[str, Any] = {"limit": limit}
        if node is not None:
            args["node"] = node
        if depth is not None:
            args["depth"] = depth
        return KsorOutlineResponse.model_validate(await self._call("outline", args))


async def search_once(
    target: str | MCPServer, query: str, k: int = 5, timeout: float = 20.0
) -> SearchOutcome:
    """Connect, search, disconnect. Never raises: an unreachable server is `unavailable`."""
    try:
        async with KsorClient(target, timeout=timeout) as client:
            return await client.search(query, k)
    except Exception as exc:
        return SearchOutcome("unavailable", reason=f"KSOR unreachable ({type(exc).__name__})")
