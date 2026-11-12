"""`python -m agent_service` — serve the internal API (default 0.0.0.0:8100 inside compose).

Uses REAL models (paid); the gateway decides when to call it.
Needs OPENAI_API_KEY and AGENT_INTERNAL_TOKEN.
"""

import os

import uvicorn

from agent_service.agents_build import build_agents
from agent_service.api import create_app
from agent_service.budget import Ledger
from agent_service.deps import Deps, McpEnrichment, McpKsor, McpWazuh, TavilySearch
from agent_service.flows import FlowConfig
from agent_service.settings import AgentSettings


def main() -> None:
    import httpx

    s = AgentSettings()
    token = os.environ.get("AGENT_INTERNAL_TOKEN", "")
    if not token:
        raise SystemExit("AGENT_INTERNAL_TOKEN is required")
    web = (
        TavilySearch(s.web_search_api_key.get_secret_value(), httpx.AsyncClient(timeout=15))
        if s.web_search_api_key
        else None
    )
    deps = Deps(
        wazuh=McpWazuh(s.wazuh_mcp_url),
        enrichment=McpEnrichment(s.enrichment_mcp_url),
        ksor=McpKsor(s.handbook_mcp_url),
        web=web,
    )
    agent_set = build_agents(s.model_for, deps, s.suggestions_dir)
    cfg = FlowConfig(
        prices=s.prices,
        run_budget_usd=s.run_budget_usd,
        max_turns=s.max_turns,
        ledger=Ledger(s.ledger_path, s.total_budget_usd),
        sessions_db=s.sessions_db,
    )
    uvicorn.run(
        create_app(agent_set, cfg, deps, token),
        host=os.environ.get("AGENT_HOST", "127.0.0.1"),
        port=int(os.environ.get("AGENT_PORT", "8100")),
    )


if __name__ == "__main__":
    main()
