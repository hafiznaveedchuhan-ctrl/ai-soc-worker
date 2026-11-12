"""FR-01-40, 41 — settings base. Env vars come from monkeypatch only; .env is never read."""

import pytest
from pydantic import SecretStr, ValidationError
from pydantic_settings import SettingsConfigDict
from soc_shared.settings import BaseServiceSettings


class DemoSettings(BaseServiceSettings):
    model_config = SettingsConfigDict(env_prefix="DEMO_", env_file=None, extra="ignore")
    api_key: SecretStr = SecretStr("")


def test_defaults() -> None:
    s = DemoSettings()
    assert (s.env, s.log_level, s.trace_include_sensitive_data) == ("local", "INFO", False)


def test_reads_prefixed_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEMO_ENV", "test")
    monkeypatch.setenv("DEMO_API_KEY", "not-a-real-key")
    s = DemoSettings()
    assert s.env == "test"
    assert s.api_key.get_secret_value() == "not-a-real-key"
    assert "not-a-real-key" not in repr(s)


def test_production_refuses_sensitive_tracing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEMO_ENV", "production")
    monkeypatch.setenv("DEMO_TRACE_INCLUDE_SENSITIVE_DATA", "true")
    with pytest.raises(ValidationError, match="production"):
        DemoSettings()


def test_local_may_enable_it_for_debugging(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEMO_TRACE_INCLUDE_SENSITIVE_DATA", "true")
    assert DemoSettings().trace_include_sensitive_data is True


def test_bad_env_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEMO_ENV", "staging")
    with pytest.raises(ValidationError):
        DemoSettings()
