"""FR-03-01…05 — wazuh-mcp over an in-memory MCP client (no network)."""

from datetime import UTC, datetime
from pathlib import Path

import pytest
from mcp import Client
from wazuh_mcp.server import build_server, source_from
from wazuh_mcp.settings import DEFAULT_FIXTURES, WazuhMcpSettings
from wazuh_mcp.sources import FixtureSource, LiveSource

pytestmark = pytest.mark.anyio
SOURCE = FixtureSource(DEFAULT_FIXTURES)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def test_fixture_source_loads_the_40_eval_alerts() -> None:
    assert len(SOURCE) == 40
    assert SOURCE.get("EV-A001") is not None and SOURCE.get("nope") is None


def test_empty_folder_fails_loudly(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        FixtureSource(tmp_path)


def test_live_mode_not_yet() -> None:
    with pytest.raises(NotImplementedError):
        LiveSource()
    with pytest.raises(NotImplementedError):
        source_from(WazuhMcpSettings(mode="live"))


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WAZUH_PORT", "9101")
    assert WazuhMcpSettings().port == 9101


async def test_tool_surface() -> None:
    async with Client(build_server(SOURCE)) as client:
        tools = (await client.list_tools()).tools
    assert sorted(t.name for t in tools) == ["get_alert", "get_new_alerts"]
    for t in tools:
        assert t.annotations is not None
        assert t.annotations.read_only_hint is True and t.annotations.destructive_hint is False


async def test_get_alert_round_trips_every_alert() -> None:
    async with Client(build_server(SOURCE)) as client:
        for aid in [f"EV-A{i:03d}" for i in range(1, 41)]:
            result = await client.call_tool("get_alert", {"alert_id": aid})
            assert not result.is_error, aid
            assert result.structured_content is not None
            assert result.structured_content["id"] == aid


@pytest.mark.parametrize("bad", ["EV-A999", "../etc/passwd", "x" * 65, "a b"])
async def test_get_alert_errors(bad: str) -> None:
    async with Client(build_server(SOURCE)) as client:
        result = await client.call_tool("get_alert", {"alert_id": bad})
    assert result.is_error


async def test_get_new_alerts_filters_orders_and_caps() -> None:
    async with Client(build_server(SOURCE)) as client:
        result = await client.call_tool(
            "get_new_alerts", {"since": "2026-11-11T00:00:00Z", "min_level": 10, "limit": 5}
        )
    data = result.structured_content
    assert data is not None and data["count"] == 5
    times = [a["timestamp"] for a in data["alerts"]]
    assert times == sorted(times)
    assert all(a["rule_level"] >= 10 for a in data["alerts"])
    cutoff = datetime(2026, 11, 11, tzinfo=UTC)
    newest = sorted(a.timestamp for a in SOURCE.since(cutoff, 10))[-1]
    assert times[-1].startswith(newest.strftime("%Y-%m-%dT%H:%M"))


@pytest.mark.parametrize(
    ("args", "ok"),
    [
        ({"min_level": 16}, False),
        ({"limit": 0}, False),
        ({"limit": 101}, False),
        ({"limit": 100}, True),
    ],
)
async def test_get_new_alerts_limits(args: dict[str, int], ok: bool) -> None:
    async with Client(build_server(SOURCE)) as client:
        result = await client.call_tool("get_new_alerts", {"since": "2020-01-01T00:00:00Z", **args})
    assert result.is_error is (not ok)
