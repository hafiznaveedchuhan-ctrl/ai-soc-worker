"""agent-service settings (prefix AGENT_). Model names, budgets, endpoints."""

from pathlib import Path

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import SettingsConfigDict
from soc_shared.settings import BaseServiceSettings

BACKEND = Path(__file__).resolve().parents[4]

# USD per 1M tokens (input, output) — developers.openai.com/api/docs/pricing,
# checked 2026-11-12 (ADR-0003).
DEFAULT_PRICES: dict[str, tuple[float, float]] = {
    "gpt-5-nano": (0.05, 0.40),
    "gpt-5-mini": (0.25, 2.00),
    "gpt-4o-mini": (0.15, 0.60),
}


class AgentSettings(BaseServiceSettings):
    model_config = SettingsConfigDict(env_prefix="AGENT_", env_file=None, extra="ignore")

    model_default: str = "gpt-5-nano"  # the smallest current OpenAI model (ADR-0003)
    model_triage: str | None = None
    model_handbook: str | None = None
    model_research: str | None = None
    # ADR-0011 (2026-11-13): the scope classifier on gpt-5-nano let 9/30 out-of-scope questions
    # through (R5+P1). ONE agent upgraded per constitution VI.2; the rest stay on model_default.
    model_scope: str | None = "gpt-5-mini"
    model_reviewer: str | None = None
    prices: dict[str, tuple[float, float]] = Field(default_factory=lambda: dict(DEFAULT_PRICES))

    run_budget_usd: float = Field(default=0.05, gt=0)
    total_budget_usd: float = Field(default=9.0, gt=0)  # hard cap $10 with headroom
    ledger_path: Path = BACKEND / ".agent-ledger.json"
    max_turns: int = Field(default=12, ge=2, le=40)

    handbook_mcp_url: str = Field(
        default="http://127.0.0.1:8080/mcp",
        validation_alias=AliasChoices("HANDBOOK_MCP_URL", "AGENT_HANDBOOK_MCP_URL"),
    )
    wazuh_mcp_url: str = "http://127.0.0.1:8101/mcp"
    enrichment_mcp_url: str = "http://127.0.0.1:8102/mcp"
    web_search_api_key: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("WEB_SEARCH_API_KEY", "AGENT_WEB_SEARCH_API_KEY"),
    )
    sessions_db: Path = BACKEND / ".agent-sessions.sqlite"
    suggestions_dir: Path = BACKEND / "suggestions"

    def model_for(self, agent: str) -> str:
        override: str | None = getattr(self, f"model_{agent}", None)
        return override or self.model_default
