"""Settings base for every service (FR-01-40, 41).

Each service subclasses `BaseServiceSettings`, sets its own `env_prefix`, and may opt in to a
`.env` file. Tests never read `.env`: they set variables with `monkeypatch.setenv`.
Secrets are typed `SecretStr`, so they are hidden in `repr()` and logs.
"""

from typing import Literal, Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    env: Literal["local", "test", "production"] = "local"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    # Agents SDK traces are exported to the OpenAI platform; raw inputs/outputs must not be
    # included (plan v2 A2, ADR-0007). The SDK's own env default is
    # OPENAI_AGENTS_TRACE_INCLUDE_SENSITIVE_DATA=0, set in .env.example.
    trace_include_sensitive_data: bool = False

    @model_validator(mode="after")
    def _no_sensitive_tracing_in_production(self) -> Self:
        if self.env == "production" and self.trace_include_sensitive_data:
            raise ValueError("trace_include_sensitive_data must be False in production")
        return self
