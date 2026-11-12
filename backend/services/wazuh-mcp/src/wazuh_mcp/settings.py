"""wazuh-mcp settings (env prefix WAZUH_)."""

from pathlib import Path
from typing import Literal

from pydantic_settings import SettingsConfigDict
from soc_shared.settings import BaseServiceSettings

DEFAULT_FIXTURES = Path(__file__).resolve().parents[4] / "evals/data/alerts"


class WazuhMcpSettings(BaseServiceSettings):
    model_config = SettingsConfigDict(env_prefix="WAZUH_", env_file=None, extra="ignore")

    mode: Literal["fixture", "live"] = "fixture"
    fixtures_dir: Path = DEFAULT_FIXTURES
    host: str = "127.0.0.1"
    port: int = 8101
