"""wazuh-mcp — read-only SIEM data access over MCP (feature 03).

Two tools, both read-only. It returns RAW alerts to its only caller, agent-service tool code,
which masks them before anything reaches a language model (ADR-0007, feature 05).
"""

import re
from datetime import datetime
from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import BaseModel

from wazuh_mcp.settings import WazuhMcpSettings
from wazuh_mcp.sources import AlertSource, FixtureSource, LiveSource

ALERT_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
READ_ONLY = ToolAnnotations(
    read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=False
)
MAX_LIMIT = 100


class AlertSummary(BaseModel):
    id: str
    timestamp: datetime
    rule_id: str
    rule_level: int
    rule_description: str
    agent_name: str


class AlertList(BaseModel):
    count: int
    alerts: list[AlertSummary]


def build_server(source: AlertSource) -> MCPServer:
    mcp = MCPServer(
        "wazuh-mcp",
        instructions="Read-only access to Wazuh alerts. Never changes anything in the SIEM.",
    )

    @mcp.tool(annotations=READ_ONLY)
    def get_alert(alert_id: str) -> dict[str, Any]:
        """Return one Wazuh alert by its id (read-only).

        Args:
            alert_id: The alert id, e.g. "EV-A001" (letters, digits, '.', '_', '-'; max 64).
        """
        if not ALERT_ID_RE.fullmatch(alert_id):
            raise ToolError("invalid alert_id: use letters, digits, '.', '_' or '-' (max 64)")
        alert = source.get(alert_id)
        if alert is None:
            raise ToolError(f"alert not found: {alert_id}")
        return alert.model_dump(mode="json", exclude_none=True)

    @mcp.tool(annotations=READ_ONLY)
    def get_new_alerts(since: datetime, min_level: int = 3, limit: int = 20) -> AlertList:
        """List alerts at or after `since` with rule level >= min_level, oldest first (read-only).

        Args:
            since: ISO-8601 date-time, e.g. "2026-11-11T00:00:00Z".
            min_level: Lowest Wazuh rule level to include (0-15).
            limit: Maximum number of alerts to return (1-100); the newest are kept.
        """
        if not 0 <= min_level <= 15:
            raise ToolError("min_level must be 0-15")
        if not 1 <= limit <= MAX_LIMIT:
            raise ToolError(f"limit must be 1-{MAX_LIMIT}")
        hits = source.since(since, min_level)[-limit:]
        return AlertList(
            count=len(hits),
            alerts=[
                AlertSummary(
                    id=a.id,
                    timestamp=a.timestamp,
                    rule_id=a.rule.id,
                    rule_level=a.rule.level,
                    rule_description=a.rule.description,
                    agent_name=a.agent.name,
                )
                for a in hits
            ],
        )

    return mcp


def source_from(settings: WazuhMcpSettings) -> AlertSource:
    return FixtureSource(settings.fixtures_dir) if settings.mode == "fixture" else LiveSource()
