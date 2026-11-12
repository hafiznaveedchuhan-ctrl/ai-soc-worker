"""api-gateway settings. The gateway holds the DB URL and the mask-map key (nobody else does)."""

from pathlib import Path
from typing import Literal, Self

from pydantic import AliasChoices, Field, SecretStr, model_validator
from pydantic_settings import SettingsConfigDict
from soc_shared.settings import BaseServiceSettings

BACKEND = Path(__file__).resolve().parents[4]


class GatewaySettings(BaseServiceSettings):
    model_config = SettingsConfigDict(env_prefix="GATEWAY_", env_file=None, extra="ignore")

    db_url: SecretStr = Field(
        default=SecretStr(f"sqlite:///{BACKEND / '.gateway-dev.sqlite'}"),
        validation_alias=AliasChoices("SOC_DB_URL", "GATEWAY_DB_URL"),
    )
    mask_map_key: SecretStr | None = Field(
        default=None, validation_alias=AliasChoices("MASK_MAP_KEY")
    )
    auth_mode: Literal["auth0", "dev"] = Field(
        default="dev", validation_alias=AliasChoices("AUTH_MODE")
    )
    auth0_domain: str = Field(default="", validation_alias=AliasChoices("AUTH0_DOMAIN"))
    auth0_audience: str = Field(default="", validation_alias=AliasChoices("AUTH0_AUDIENCE"))
    role_claim: str = (
        "https://soc-worker/roles"  # set by an Auth0 post-login Action (feature 08 guide)
    )
    cors_origins: str = Field(
        default="https://ai-soc-handbook.vercel.app", validation_alias=AliasChoices("CORS_ORIGINS")
    )
    agent_url: str = "http://127.0.0.1:8100"
    agent_internal_token: SecretStr = Field(
        default=SecretStr(""), validation_alias=AliasChoices("AGENT_INTERNAL_TOKEN")
    )
    rate_limit_per_minute: int = Field(default=20, ge=1)
    total_budget_usd: float = 9.0

    @model_validator(mode="after")
    def _dev_auth_only_locally(self) -> Self:
        if self.auth_mode == "dev" and self.env == "production":
            raise ValueError("AUTH_MODE=dev is forbidden when ENV=production")
        if self.auth_mode == "auth0" and not (self.auth0_domain and self.auth0_audience):
            raise ValueError("AUTH_MODE=auth0 needs AUTH0_DOMAIN and AUTH0_AUDIENCE")
        return self

    @property
    def origins(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]
