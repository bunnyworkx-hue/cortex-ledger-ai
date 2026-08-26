import os

from axiom_core.config import AxiomSettings


def test_defaults_with_no_env(monkeypatch):
    for key in list(os.environ):
        if key.startswith("AXIOM_"):
            monkeypatch.delenv(key, raising=False)

    settings = AxiomSettings(_env_file=None)

    assert settings.environment == "dev"
    assert settings.service_name == "axiom-os"
    assert settings.log_format == "console"
    assert settings.database_url is None


def test_env_override(monkeypatch):
    monkeypatch.setenv("AXIOM_ENVIRONMENT", "staging")
    monkeypatch.setenv("AXIOM_SERVICE_NAME", "axiom-test")
    monkeypatch.setenv("AXIOM_DATABASE_URL", "postgresql://u:p@host:5432/db")

    settings = AxiomSettings(_env_file=None)

    assert settings.environment == "staging"
    assert settings.service_name == "axiom-test"
    assert settings.database_url == "postgresql://u:p@host:5432/db"


def test_prod_forces_json_logging(monkeypatch):
    monkeypatch.setenv("AXIOM_ENVIRONMENT", "prod")
    monkeypatch.setenv("AXIOM_LOG_FORMAT", "console")

    settings = AxiomSettings(_env_file=None)

    assert settings.log_format == "json"
