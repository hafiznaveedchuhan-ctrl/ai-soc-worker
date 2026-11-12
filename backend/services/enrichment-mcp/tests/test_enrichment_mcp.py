"""FR-03-10…17 — enrichment-mcp with a mocked AbuseIPDB (httpx.MockTransport, no network)."""

import logging
from collections.abc import Callable
from typing import Any

import httpx
import pytest
from enrichment_mcp.bands import band
from enrichment_mcp.cache import DailyBudget, TtlCache
from enrichment_mcp.server import build_server
from enrichment_mcp.settings import EnrichmentSettings
from mcp import Client
from pydantic import SecretStr

pytestmark = pytest.mark.anyio
PUBLIC = "8.8.8.8"
GOOD = {
    "data": {
        "ipAddress": PUBLIC,
        "isPublic": True,
        "abuseConfidenceScore": 88,
        "totalReports": 41,
        "numDistinctUsers": 12,
        "countryCode": "US",
        "usageType": "Data Center",
        "lastReportedAt": "2026-11-10T08:00:00+00:00",
        "extraField": "ignored",
    }
}


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


class Fake:
    """Records every request; answers with the given handler."""

    def __init__(self, handler: Callable[[httpx.Request], httpx.Response]) -> None:
        self.requests: list[httpx.Request] = []
        self._handler = handler

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self._handler(request)

    def client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(transport=httpx.MockTransport(self))


def settings(**kw: Any) -> EnrichmentSettings:
    return EnrichmentSettings(abuseipdb_api_key=SecretStr("test-key"), **kw)


async def call(server: Any, ip: str) -> dict[str, Any]:
    async with Client(server) as client:
        result = await client.call_tool("ip_reputation", {"ip": ip})
    assert not result.is_error
    assert result.structured_content is not None
    out: dict[str, Any] = dict(result.structured_content)
    return out


async def test_ok_request_shape_and_result() -> None:
    fake = Fake(lambda r: httpx.Response(200, json=GOOD))
    out = await call(build_server(settings(), fake.client()), PUBLIC)
    assert out["status"] == "ok" and out["abuse_confidence_score"] == 88
    assert out["handbook_band"] == "likely_malicious" and out["cached"] is False
    (req,) = fake.requests
    assert req.url.path == "/api/v2/check"
    assert req.url.params["ipAddress"] == PUBLIC and req.url.params["maxAgeInDays"] == "90"
    assert req.headers["Key"] == "test-key" and req.headers["Accept"] == "application/json"


@pytest.mark.parametrize(
    "ip",
    [
        "10.0.0.5",
        "172.16.1.1",
        "192.168.1.1",
        "127.0.0.1",
        "169.254.1.1",
        "::1",
        "fe80::1",
        "fd00::1",
        "192.0.2.10",
        "203.0.113.45",
        "198.51.100.7",
        "100.64.0.1",
        "224.0.0.1",
        "0.0.0.0",
        "not-an-ip",
    ],
)
async def test_never_queries_non_public(ip: str) -> None:
    fake = Fake(lambda r: httpx.Response(200, json=GOOD))
    out = await call(build_server(settings(), fake.client()), ip)
    assert out["status"] == "not_queried" and out["is_public"] is False
    assert fake.requests == []


async def test_cache_hit_makes_no_request() -> None:
    fake = Fake(lambda r: httpx.Response(200, json=GOOD))
    server = build_server(settings(), fake.client())
    first = await call(server, PUBLIC)
    second = await call(server, PUBLIC)
    assert first["cached"] is False and second["cached"] is True
    assert len(fake.requests) == 1


async def test_cache_expires() -> None:
    t = [1000.0]
    fake = Fake(lambda r: httpx.Response(200, json=GOOD))
    server = build_server(settings(cache_ttl_seconds=60), fake.client(), clock=lambda: t[0])
    await call(server, PUBLIC)
    t[0] += 61
    await call(server, PUBLIC)
    assert len(fake.requests) == 2


async def test_missing_key_no_request() -> None:
    fake = Fake(lambda r: httpx.Response(200, json=GOOD))
    out = await call(build_server(EnrichmentSettings(), fake.client()), PUBLIC)
    assert out["status"] == "error" and "not configured" in out["reason"]
    assert fake.requests == []


async def test_daily_budget() -> None:
    fake = Fake(lambda r: httpx.Response(200, json={"data": {**GOOD["data"], "ipAddress": "x"}}))
    server = build_server(settings(daily_budget=1, cache_ttl_seconds=0), fake.client())
    assert (await call(server, "8.8.8.8"))["status"] == "ok"
    out = await call(server, "1.1.1.1")
    assert out["status"] == "error" and out["reason"] == "daily budget reached"
    assert len(fake.requests) == 1


@pytest.mark.parametrize(
    ("response", "reason"),
    [
        (httpx.Response(429, headers={"Retry-After": "120"}, json={"errors": []}), "rate limited"),
        (httpx.Response(401, json={"errors": []}), "key rejected by AbuseIPDB"),
        (httpx.Response(503, text="down"), "http 503"),
        (httpx.Response(200, json={"data": {"ipAddress": PUBLIC}}), "unexpected response schema"),
        (
            httpx.Response(200, json={"data": {**GOOD["data"], "abuseConfidenceScore": 150}}),
            "unexpected response schema",
        ),
        (httpx.Response(200, text="<html>"), "unexpected response schema"),
    ],
)
async def test_errors_are_results_not_crashes(response: httpx.Response, reason: str) -> None:
    out = await call(build_server(settings(), Fake(lambda r: response).client()), PUBLIC)
    assert out["status"] == "error" and out["reason"] == reason
    if reason == "rate limited":
        assert out["retry_after"] == 120


async def test_network_errors() -> None:
    def boom(r: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("t")

    def down(r: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("x")

    assert (await call(build_server(settings(), Fake(boom).client()), PUBLIC))[
        "reason"
    ] == "timeout"
    assert (await call(build_server(settings(), Fake(down).client()), PUBLIC))[
        "reason"
    ] == "network error"


async def test_tool_surface() -> None:
    async with Client(build_server(settings())) as client:
        tools = (await client.list_tools()).tools
    assert [t.name for t in tools] == ["ip_reputation"]
    assert tools[0].annotations is not None and tools[0].annotations.read_only_hint is True


async def test_logs_never_contain_the_ip(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="enrichment_mcp")
    fake = Fake(lambda r: httpx.Response(200, json=GOOD))
    await call(build_server(settings(), fake.client()), PUBLIC)
    await call(build_server(settings(), fake.client()), "10.0.0.5")
    assert PUBLIC not in caplog.text and "10.0.0.5" not in caplog.text
    assert "ref=" in caplog.text


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0, "none"),
        (1, "low"),
        (24, "low"),
        (25, "suspicious"),
        (74, "suspicious"),
        (75, "likely_malicious"),
        (100, "likely_malicious"),
    ],
)
def test_bands(score: int, expected: str) -> None:
    assert band(score) == expected


def test_settings_reads_the_plain_key_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ABUSEIPDB_API_KEY", "k-from-env")
    s = EnrichmentSettings()
    assert (
        s.abuseipdb_api_key is not None and s.abuseipdb_api_key.get_secret_value() == "k-from-env"
    )
    assert "k-from-env" not in repr(s)


def test_cache_and_budget_units() -> None:
    t = [0.0]
    c: TtlCache[int] = TtlCache(10, lambda: t[0])
    c.put("a", 1)
    assert c.get("a") == 1 and c.get("b") is None
    b = DailyBudget(2, lambda: t[0])
    assert b.try_spend() and b.try_spend() and not b.try_spend() and b.used == 2
    t[0] += 86_400  # next UTC day resets
    assert b.try_spend() and b.used == 1
