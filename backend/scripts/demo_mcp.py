"""`make demo-mcp` — call both MCP servers in memory (free, offline; AbuseIPDB is mocked).

`--live IP` makes ONE real AbuseIPDB call through enrichment-mcp. It needs ABUSEIPDB_API_KEY
in backend/.env and CONFIRM=haan (Naveed's explicit permission for that paid/external call).
"""

import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Any

import httpx
from enrichment_mcp.server import build_server as build_enrichment
from enrichment_mcp.settings import EnrichmentSettings
from mcp import Client
from pydantic import SecretStr
from wazuh_mcp.server import build_server as build_wazuh
from wazuh_mcp.settings import DEFAULT_FIXTURES
from wazuh_mcp.sources import FixtureSource

MOCK_REPLY = {
    "data": {
        "ipAddress": "8.8.8.8",
        "isPublic": True,
        "abuseConfidenceScore": 88,
        "totalReports": 41,
        "numDistinctUsers": 12,
        "countryCode": "US",
        "usageType": "Data Center",
        "lastReportedAt": "2026-11-10T08:00:00+00:00",
    }
}


def show(title: str, data: Any) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(data, indent=2, default=str)[:1500])


async def demo() -> None:
    async with Client(build_wazuh(FixtureSource(DEFAULT_FIXTURES))) as wazuh:
        tools = [t.name for t in (await wazuh.list_tools()).tools]
        print("wazuh-mcp tools (read-only):", tools)
        new = await wazuh.call_tool(
            "get_new_alerts", {"since": "2026-11-11T00:00:00Z", "min_level": 10, "limit": 5}
        )
        show("get_new_alerts(since 2026-11-11, min_level 10, limit 5)", new.structured_content)
        one = await wazuh.call_tool("get_alert", {"alert_id": "EV-A003"})
        show(
            "get_alert(EV-A003)  [RAW: agent-service masks it before any LLM]",
            one.structured_content,
        )

    mock = httpx.AsyncClient(
        transport=httpx.MockTransport(lambda r: httpx.Response(200, json=MOCK_REPLY))
    )
    settings = EnrichmentSettings(abuseipdb_api_key=SecretStr("demo-not-a-real-key"))
    async with Client(build_enrichment(settings, mock)) as enrich:
        print(
            "\nenrichment-mcp tools (read-only):",
            [t.name for t in (await enrich.list_tools()).tools],
        )
        for ip in ("10.10.20.15", "203.0.113.45", "8.8.8.8", "8.8.8.8"):
            r = await enrich.call_tool("ip_reputation", {"ip": ip})
            show(f"ip_reputation({ip})  [AbuseIPDB MOCKED]", r.structured_content)


async def live(ip: str) -> None:
    if os.environ.get("CONFIRM") != "haan":
        raise SystemExit("refused: a live AbuseIPDB call needs CONFIRM=haan (Naveed's permission)")
    env = Path(__file__).resolve().parents[1] / ".env"
    settings = EnrichmentSettings(_env_file=env if env.exists() else None)
    async with Client(build_enrichment(settings)) as enrich:
        r = await enrich.call_tool("ip_reputation", {"ip": ip})
        show(f"LIVE ip_reputation({ip})", r.structured_content)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", metavar="IP")
    args = parser.parse_args()
    asyncio.run(live(args.live) if args.live else demo())


if __name__ == "__main__":
    main()
