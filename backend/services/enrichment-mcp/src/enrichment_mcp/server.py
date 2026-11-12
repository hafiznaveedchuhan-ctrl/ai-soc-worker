"""enrichment-mcp — IP reputation over MCP (feature 03). One read-only tool.

Defence in depth: even if a caller asks, only PUBLIC IPs are sent to AbuseIPDB
(constitution Art. III). Logs carry the IP class and a short hash, never the IP.
"""

import hashlib
import logging
import time
from datetime import datetime
from typing import Literal

import httpx
from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations
from pydantic import BaseModel
from soc_shared.masking import classify_ip

from enrichment_mcp.abuseipdb import AbuseIpdbClient, AbuseIpdbError, CheckData
from enrichment_mcp.bands import Band, band
from enrichment_mcp.cache import Clock, DailyBudget, TtlCache
from enrichment_mcp.settings import EnrichmentSettings

log = logging.getLogger("enrichment_mcp")
# httpx logs every request URL at INFO — the URL holds ?ipAddress=<raw IP>. Keep it quiet.
for _noisy in ("httpx", "httpcore"):
    logging.getLogger(_noisy).setLevel(logging.WARNING)
READ_ONLY = ToolAnnotations(
    read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=True
)


class IpReputationResult(BaseModel):
    ip_class: str
    is_public: bool
    status: Literal["ok", "not_queried", "error"]
    reason: str | None = None
    abuse_confidence_score: int | None = None
    handbook_band: Band | None = None
    total_reports: int | None = None
    num_distinct_users: int | None = None
    country_code: str | None = None
    usage_type: str | None = None
    last_reported_at: datetime | None = None
    cached: bool = False
    retry_after: int | None = None
    source: Literal["abuseipdb"] = "abuseipdb"


def _ref(ip: str) -> str:
    return hashlib.sha256(ip.encode()).hexdigest()[:8]


def _ok(ip_class: str, d: CheckData, cached: bool) -> IpReputationResult:
    return IpReputationResult(
        ip_class=ip_class,
        is_public=True,
        status="ok",
        abuse_confidence_score=d.abuseConfidenceScore,
        handbook_band=band(d.abuseConfidenceScore),
        total_reports=d.totalReports,
        num_distinct_users=d.numDistinctUsers,
        country_code=d.countryCode,
        usage_type=d.usageType,
        last_reported_at=d.lastReportedAt,
        cached=cached,
    )


def build_server(
    settings: EnrichmentSettings,
    http: httpx.AsyncClient | None = None,
    clock: Clock | None = None,
) -> MCPServer:
    now: Clock = clock or time.time
    cache: TtlCache[CheckData] = TtlCache(settings.cache_ttl_seconds, now)
    budget = DailyBudget(settings.daily_budget, now)
    client_http = http or httpx.AsyncClient(timeout=settings.timeout_seconds)
    mcp = MCPServer(
        "enrichment-mcp",
        instructions="IP reputation from AbuseIPDB for PUBLIC IPs only. Read-only; never reports.",
    )

    @mcp.tool(annotations=READ_ONLY)
    async def ip_reputation(ip: str) -> IpReputationResult:
        """AbuseIPDB reputation of one IP; private, reserved and documentation IPs are never sent.

        Args:
            ip: An IPv4 or IPv6 address (the real address; callers unmask tokens in their own code).
        """
        ip_class = classify_ip(ip)
        if ip_class != "public":
            log.info("not queried: class=%s", ip_class)
            return IpReputationResult(
                ip_class=ip_class,
                is_public=False,
                status="not_queried",
                reason=f"only public IPs are checked; this one is {ip_class}",
            )
        hit = cache.get(ip)
        if hit is not None:
            return _ok(ip_class, hit, cached=True)
        if settings.abuseipdb_api_key is None or not settings.abuseipdb_api_key.get_secret_value():
            return IpReputationResult(
                ip_class=ip_class,
                is_public=True,
                status="error",
                reason="ABUSEIPDB_API_KEY not configured",
            )
        if not budget.try_spend():
            return IpReputationResult(
                ip_class=ip_class, is_public=True, status="error", reason="daily budget reached"
            )
        client = AbuseIpdbClient(
            client_http,
            settings.base_url,
            settings.abuseipdb_api_key.get_secret_value(),
            settings.max_age_days,
        )
        try:
            data = await client.check(ip)
        except AbuseIpdbError as exc:
            log.warning("abuseipdb error ref=%s reason=%s", _ref(ip), exc.reason)
            return IpReputationResult(
                ip_class=ip_class,
                is_public=True,
                status="error",
                reason=exc.reason,
                retry_after=exc.retry_after,
            )
        cache.put(ip, data)
        log.info("checked ref=%s score=%s", _ref(ip), data.abuseConfidenceScore)
        return _ok(ip_class, data, cached=False)

    return mcp
