"""enrichment-mcp settings. Holds the ONLY AbuseIPDB key in the system (never logged)."""

from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import SettingsConfigDict
from soc_shared.settings import BaseServiceSettings


class EnrichmentSettings(BaseServiceSettings):
    model_config = SettingsConfigDict(env_prefix="ENRICH_", env_file=None, extra="ignore")

    abuseipdb_api_key: SecretStr | None = Field(
        default=None, validation_alias=AliasChoices("ABUSEIPDB_API_KEY", "ENRICH_ABUSEIPDB_API_KEY")
    )
    base_url: str = "https://api.abuseipdb.com/api/v2"
    max_age_days: int = Field(default=90, ge=1, le=365)
    cache_ttl_seconds: int = Field(default=86_400, ge=0)
    daily_budget: int = Field(default=900, ge=0)  # free tier: 1,000 checks/day; keep a margin
    timeout_seconds: float = Field(default=10.0, gt=0)
    host: str = "127.0.0.1"
    port: int = 8102
