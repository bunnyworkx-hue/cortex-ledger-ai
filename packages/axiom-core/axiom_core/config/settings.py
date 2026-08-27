from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AxiomSettings(BaseSettings):
    """Process-wide configuration, sourced from environment variables
    (prefix ``AXIOM_``) or a local ``.env`` file. See ``.env.example`` at
    the repo root for the full list of variables.
    """

    model_config = SettingsConfigDict(
        env_prefix="AXIOM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["dev", "staging", "prod"] = "dev"
    service_name: str = "axiom-os"

    log_level: str = "INFO"
    log_format: Literal["console", "json"] = "console"

    # Database (Supabase Postgres). Optional until Milestone 6's project
    # provisioning step is complete; downstream code must fail loudly
    # rather than silently no-op when it's missing and a DB is required.
    database_url: str | None = None
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None

    # Milestone 7 (Model Gateway).
    anthropic_api_key: str | None = None
    anthropic_default_model: str = "claude-sonnet-5"

    # Milestone 8 (Knowledge Gateway). URL of a running Graphify MCP
    # server started with --transport http (see docs/graphify/GRAPHIFY_AUDIT.md
    # §4) — None means the Knowledge Gateway has no backend registered.
    graphify_mcp_url: str | None = None

    # Milestone 10 (Agent Fabric). Path to a real agency-agents checkout
    # (see docs/agent-fabric/AGENT_LIBRARY_AUDIT.md) — None means the
    # Agent Fabric registry is empty.
    agency_agents_path: str | None = None

    # Milestone 13 (Hermes Integration). Path/name of the real installed
    # `hermes` CLI (github.com/NousResearch/hermes-agent) — see
    # docs/hermes/HERMES_INTEGRATION.md. Defaults to relying on PATH.
    hermes_bin: str = "hermes"
    hermes_default_model: str = "anthropic/claude-sonnet-5"

    # Milestone 22 (Security — Memory/Tenant Isolation). Comma-separated
    # "key:owner_id" or "key:owner_id:tenant_id" entries — see
    # apps/api/axiom_api/auth.py. None means /v1/memory has no
    # configured caller identities and returns 503, not an open door.
    api_keys: str | None = None

    def model_post_init(self, __context: object) -> None:
        # Prod should never fall back to human-readable console logging.
        if self.environment == "prod" and self.log_format == "console":
            object.__setattr__(self, "log_format", "json")


@lru_cache
def get_settings() -> AxiomSettings:
    return AxiomSettings()
