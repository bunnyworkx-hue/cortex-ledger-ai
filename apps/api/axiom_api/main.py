from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from axiom_agent_fabric import AgencyAgentsSourceError, AgentInvocationGateway, AgentRegistry
from axiom_anthropic import AnthropicBackend, build_anthropic_client
from axiom_core.agents import AgentBackendRegistry, AxiomNativeBackend
from axiom_core.config import get_settings
from axiom_core.knowledge import KnowledgeGatewayRegistry
from axiom_core.logging import configure_logging, get_logger
from axiom_core.models import ModelGatewayRegistry
from axiom_db.engine import DatabaseNotConfiguredError, check_database_health
from axiom_graphify import GraphifyBackend

from axiom_api.routers.agent_fabric import router as agent_fabric_router
from axiom_api.routers.agents import router as agents_router
from axiom_api.routers.knowledge import router as knowledge_router
from axiom_api.routers.models import router as models_router

settings = get_settings()
configure_logging(settings)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("axiom.startup", environment=settings.environment, service=settings.service_name)

    registry = ModelGatewayRegistry()
    if settings.anthropic_api_key:
        registry.register(AnthropicBackend(build_anthropic_client(settings)))
        logger.info("axiom.model_gateway.registered", provider="anthropic")
    else:
        logger.warning("axiom.model_gateway.anthropic_not_configured")
    app.state.model_gateway = registry

    knowledge_registry = KnowledgeGatewayRegistry()
    if settings.graphify_mcp_url:
        knowledge_registry.register(GraphifyBackend(settings.graphify_mcp_url))
        logger.info("axiom.knowledge_gateway.registered", backend="graphify")
    else:
        logger.warning("axiom.knowledge_gateway.graphify_not_configured")
    app.state.knowledge_gateway = knowledge_registry

    agent_backend_registry = AgentBackendRegistry()
    if settings.anthropic_api_key:
        agent_backend_registry.register(
            AxiomNativeBackend(registry.get("anthropic"), settings.anthropic_default_model)
        )
        logger.info("axiom.agent_backend.registered", backend="axiom_native")
    else:
        logger.warning("axiom.agent_backend.axiom_native_not_configured")
    app.state.agent_backend_gateway = agent_backend_registry

    app.state.agent_fabric = None
    if settings.agency_agents_path:
        try:
            agent_registry = AgentRegistry.load(Path(settings.agency_agents_path))
        except AgencyAgentsSourceError as exc:
            logger.warning("axiom.agent_fabric.load_failed", error=str(exc))
        else:
            app.state.agent_fabric = AgentInvocationGateway(agent_registry)
            logger.info("axiom.agent_fabric.loaded", agent_count=len(agent_registry))
    else:
        logger.warning("axiom.agent_fabric.not_configured")

    yield
    logger.info("axiom.shutdown")


app = FastAPI(title="Axiom OS API", version="0.1.0", lifespan=lifespan)
app.include_router(models_router)
app.include_router(knowledge_router)
app.include_router(agents_router)
app.include_router(agent_fabric_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Milestone 6's concrete proof of life: config loaded, logging
    configured, and a real (or honestly-reported-missing) database
    round trip — not a hardcoded 200.
    """
    try:
        healthy = await check_database_health()
        database_status = "ok" if healthy else "error: unexpected result"
    except DatabaseNotConfiguredError:
        database_status = "unconfigured"
    except Exception as exc:  # noqa: BLE001 — health check must report, not raise
        logger.warning("axiom.health.database_error", error=str(exc))
        database_status = f"error: {exc}"

    return {
        "status": "ok",
        "service": settings.service_name,
        "environment": settings.environment,
        "database": database_status,
    }
