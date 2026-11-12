"""The REAL pipeline for `soc_evals paid` (feature 11): agent_service.flows → predictions.

`AgentPipeline` is model-agnostic: tests give it ScriptedModel agents (free); `build_live` gives it
real OpenAI models + the live handbook (PAID — only behind --yes-paid AND CONFIRM=haan, ADR-0010).
"""

import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_service.agents_build import AgentSet
from agent_service.deps import Deps
from agent_service.flows import FlowConfig, FlowResult, run_ask, run_triage
from agents.items import ToolApprovalItem
from mcp import Client
from soc_shared.masking import find_unmasked_pii
from soc_shared.masking.patterns import TOKEN_RE
from soc_shared.models import WazuhAlert

from soc_evals.datasets import Probe
from soc_evals.predictions import AlertPrediction, ProbePrediction

EVAL_USER = "soc-evals"


class PreflightError(RuntimeError):
    pass


async def reject_all(item: ToolApprovalItem) -> bool:
    """Evals never approve a ticket, not even the MOCK one (FR-11-02)."""
    return False


def safe_events(events: list[str]) -> list[str]:
    """Events are masked by design; still, never store one that holds a raw IP or email."""
    return [
        "[event withheld: unmasked data]" if find_unmasked_pii(TOKEN_RE.sub(" ", e)) else e[:400]
        for e in events
    ][:30]


def _error(r: FlowResult) -> str | None:
    return None if r.status in ("ok", "declined") else f"{r.status}: {r.text}"[:300]


def alert_prediction(alert_id: str, r: FlowResult, latency_ms: float) -> AlertPrediction:
    return AlertPrediction(
        alert_id=alert_id,
        note=r.note if r.status == "ok" else None,
        error=_error(r) or (None if r.note else "ok without a note"),
        latency_ms=latency_ms,
        usage=r.usage,
        output_text=r.text,  # masked: the gateway unmasks for the analyst, the eval does not
        events=safe_events(r.events),
    )


def probe_prediction(probe_id: str, r: FlowResult, latency_ms: float) -> ProbePrediction:
    label = "DECLINE" if r.status == "declined" else (r.answer.scope if r.answer else None)
    return ProbePrediction(
        probe_id=probe_id,
        scope_label=label,
        answer=r.answer,
        error=_error(r),
        latency_ms=latency_ms,
        usage=r.usage,
        output_text=r.text,
        events=safe_events(r.events),
    )


@dataclass
class AgentPipeline:
    app: AgentSet
    cfg: FlowConfig
    deps: Deps

    def ledger_total(self) -> float | None:
        """Cumulative spend from the $9 ledger (None in tests without a ledger)."""
        return self.cfg.ledger.total() if self.cfg.ledger is not None else None

    async def run_alert(self, alert_id: str, alert: WazuhAlert, context: str) -> AlertPrediction:
        t0 = time.perf_counter()
        r = await run_triage(
            self.app,
            self.cfg,
            self.deps,
            alert_id,
            user_id=EVAL_USER,
            analyst_context=context,
            approve=reject_all,
        )
        return alert_prediction(alert_id, r, (time.perf_counter() - t0) * 1000)

    async def run_probe(self, probe: Probe) -> ProbePrediction:
        t0 = time.perf_counter()
        r = await run_ask(
            self.app,
            self.cfg,
            probe.question,
            user_id=EVAL_USER,
            session_id=f"eval-{probe.probe_id}-{uuid.uuid4().hex[:8]}",  # fresh per probe
        )
        return probe_prediction(probe.probe_id, r, (time.perf_counter() - t0) * 1000)


async def preflight(target: Any, timeout_s: float = 5) -> int:
    """Free check: the handbook MCP answers tools/list (no search → no embedding cost)."""
    try:
        async with Client(target, read_timeout_seconds=timeout_s) as client:
            tools = await client.list_tools()
    except Exception as exc:
        raise PreflightError(
            f"handbook MCP not reachable ({type(exc).__name__}). "
            "Start it: cd ../handbook && npm run serve"
        ) from exc
    return len(tools.tools)


def build_live(env_file: Path | None) -> tuple[AgentPipeline, str]:  # pragma: no cover — PAID path
    """Real models + live handbook + fixture Wazuh; AbuseIPDB/Tavily only with keys (ADR-0010).
    The .env file is read by the settings classes only; nothing from it is printed."""
    import httpx
    from agent_service.agents_build import build_agents
    from agent_service.budget import Ledger
    from agent_service.deps import McpEnrichment, McpKsor, McpWazuh, TavilySearch
    from agent_service.settings import AgentSettings
    from enrichment_mcp.server import build_server as build_enrichment
    from enrichment_mcp.settings import EnrichmentSettings
    from wazuh_mcp.server import build_server as build_wazuh
    from wazuh_mcp.settings import DEFAULT_FIXTURES
    from wazuh_mcp.sources import FixtureSource

    s = AgentSettings(_env_file=env_file)
    if os.environ.get("OPENAI_API_KEY") is None and env_file is not None:
        from dotenv import dotenv_values

        key = dotenv_values(env_file).get("OPENAI_API_KEY")
        if key:
            os.environ["OPENAI_API_KEY"] = key
    web = (
        TavilySearch(s.web_search_api_key.get_secret_value(), httpx.AsyncClient(timeout=15))
        if s.web_search_api_key
        else None
    )
    enrich = EnrichmentSettings(_env_file=env_file)
    deps = Deps(
        wazuh=McpWazuh(build_wazuh(FixtureSource(DEFAULT_FIXTURES))),
        enrichment=McpEnrichment(build_enrichment(enrich)),
        ksor=McpKsor(s.handbook_mcp_url),
        web=web,
    )
    app = build_agents(s.model_for, deps, s.suggestions_dir)
    cfg = FlowConfig(
        prices=s.prices,
        run_budget_usd=s.run_budget_usd,
        max_turns=s.max_turns,
        ledger=Ledger(s.ledger_path, s.total_budget_usd),
    )
    models = ", ".join(
        sorted({s.model_for(k) for k in ("triage", "handbook", "research", "scope", "reviewer")})
    )
    extras = (
        f"web={'tavily' if web else 'off'}, abuseipdb={'on' if enrich.abuseipdb_api_key else 'off'}"
    )
    return AgentPipeline(app, cfg, deps), f"{models} ({extras})"


def handbook_url(env_file: Path | None) -> str:  # pragma: no cover — trivial
    from agent_service.settings import AgentSettings

    return AgentSettings(_env_file=env_file).handbook_mcp_url
