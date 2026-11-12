"""Ports to the outside world. Each takes a URL (live) or an in-memory MCP server (tests/demo).

The model never touches these directly: only tool CODE does, which masks and unmasks around them.
"""

from dataclasses import dataclass
from typing import Any, Protocol

import httpx
from ksor_client.client import SearchOutcome, search_once
from mcp import Client
from mcp.server.mcpserver import MCPServer
from pydantic import BaseModel, ConfigDict, ValidationError

TRUSTED_DOMAINS: tuple[str, ...] = (
    "attack.mitre.org",
    "learn.microsoft.com",
    "nist.gov",
    "csrc.nist.gov",
    "cisa.gov",
    "documentation.wazuh.com",
    "github.com",
    "rfc-editor.org",
)
GITHUB_ALLOWED_PREFIX = "https://github.com/wazuh/"  # github.com is allowed only for the wazuh org

Target = str | MCPServer


class PortError(Exception):
    pass


async def _call(target: Target, tool: str, args: dict[str, Any]) -> dict[str, Any]:
    async with Client(target, read_timeout_seconds=20) as client:
        result = await client.call_tool(tool, args)
    if result.is_error or result.structured_content is None:
        text = " ".join(getattr(c, "text", "") for c in result.content)[:200]
        raise PortError(f"{tool} failed: {text}")
    return dict(result.structured_content)


class WazuhPort(Protocol):
    async def get_alert(self, alert_id: str) -> dict[str, Any]: ...


class EnrichmentPort(Protocol):
    async def ip_reputation(self, ip: str) -> dict[str, Any]: ...


class KsorPort(Protocol):
    async def search(self, query: str, k: int = 5) -> SearchOutcome: ...


class WebResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    url: str
    title: str = ""
    content: str = ""


class WebSearchPort(Protocol):
    async def search(self, query: str, domains: tuple[str, ...]) -> list[WebResult]: ...


@dataclass
class McpWazuh:
    target: Target

    async def get_alert(self, alert_id: str) -> dict[str, Any]:
        return await _call(self.target, "get_alert", {"alert_id": alert_id})


@dataclass
class McpEnrichment:
    target: Target

    async def ip_reputation(self, ip: str) -> dict[str, Any]:
        return await _call(self.target, "ip_reputation", {"ip": ip})


@dataclass
class McpKsor:
    target: Target

    async def search(self, query: str, k: int = 5) -> SearchOutcome:
        return await search_once(self.target, query, k)


class _TavilyResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    results: list[WebResult]


@dataclass
class TavilySearch:
    """Tavily /search (docs.tavily.com, checked 2026-11-12; free 1,000 credits/month — ADR-0004)."""

    api_key: str
    http: httpx.AsyncClient
    max_results: int = 5
    url: str = "https://api.tavily.com/search"

    async def search(self, query: str, domains: tuple[str, ...]) -> list[WebResult]:
        body = {
            "query": query,
            "search_depth": "basic",
            "max_results": self.max_results,
            "include_domains": list(domains),
            "include_domains_mode": "restrict",
            "include_answer": False,
            "include_raw_content": False,
        }
        try:
            resp = await self.http.post(
                self.url, json=body, headers={"Authorization": f"Bearer {self.api_key}"}
            )
        except httpx.HTTPError as exc:
            raise PortError(f"web search unreachable ({type(exc).__name__})") from exc
        if resp.status_code != 200:
            raise PortError(f"web search http {resp.status_code}")
        try:
            return _TavilyResponse.model_validate_json(resp.content).results
        except ValidationError as exc:
            raise PortError("unexpected web search response") from exc


@dataclass
class FakeWebSearch:
    results: list[WebResult]
    calls: int = 0

    async def search(self, query: str, domains: tuple[str, ...]) -> list[WebResult]:
        self.calls += 1
        return list(self.results)


@dataclass
class Deps:
    wazuh: WazuhPort
    enrichment: EnrichmentPort
    ksor: KsorPort
    web: WebSearchPort | None
