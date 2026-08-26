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
from axiom_core.policy import PolicyEngine
from axiom_core.tools import ToolRegistry
from axiom_db.approvals import PostgresApprovalStore
from axiom_db.engine import DatabaseNotConfiguredError, check_database_health, get_sessionmaker
from axiom_db.executions import PostgresExecutionStore
from axiom_db.memory import PostgresMemoryStore
from axiom_graphify import GraphifyBackend
from axiom_hermes import HermesBackend
from axiom_mcp import register_mcp_server

from axiom_api.native_tools import register_native_tools
from axiom_api.routers.agent_fabric import router as agent_fabric_router
from axiom_api.routers.agents import router as agents_router
from axiom_api.routers.approvals import router as approvals_router
from axiom_api.routers.knowledge import router as knowledge_router
from axiom_api.routers.memory import router as memory_router
from axiom_api.routers.models import router as models_router
from axiom_api.routers.observability import router as observability_router
from axiom_api.routers.tools import router as tools_router

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

    if settings.anthropic_api_key:
        hermes_backend = HermesBackend(
            settings.anthropic_api_key,
            hermes_bin=settings.hermes_bin,
            default_model=settings.hermes_default_model,
        )
        if await hermes_backend.is_configured():
            agent_backend_registry.register(hermes_backend)
            logger.info("axiom.agent_backend.registered", backend="hermes")
        else:
            logger.warning("axiom.agent_backend.hermes_binary_not_found", hermes_bin=settings.hermes_bin)
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

    tool_registry = ToolRegistry()
    if settings.graphify_mcp_url:
        try:
            count = await register_mcp_server(tool_registry, "graphify", settings.graphify_mcp_url)
        except Exception as exc:  # noqa: BLE001 — optional external MCP server may be down at startup
            logger.warning("axiom.tools.mcp_registration_failed", server="graphify", error=str(exc))
        else:
            logger.info("axiom.tools.mcp_registered", server="graphify", tool_count=count)
    else:
        logger.warning("axiom.tools.graphify_mcp_not_configured")
    register_native_tools(tool_registry)
    app.state.tool_registry = tool_registry

    app.state.memory_store = None
    if settings.database_url:
        app.state.memory_store = PostgresMemoryStore(get_sessionmaker())
        logger.info("axiom.memory_store.registered", backend="postgres")
    else:
        logger.warning("axiom.memory_store.not_configured")

    app.state.policy_engine = PolicyEngine(approval_threshold="high")

    app.state.approval_store = None
    if settings.database_url:
        app.state.approval_store = PostgresApprovalStore(get_sessionmaker())
        logger.info("axiom.approval_store.registered", backend="postgres")
    else:
        logger.warning("axiom.approval_store.not_configured")

    app.state.execution_store = None
    if settings.database_url:
        app.state.execution_store = PostgresExecutionStore(get_sessionmaker())
        logger.info("axiom.execution_store.registered", backend="postgres")
    else:
        logger.warning("axiom.execution_store.not_configured")

    yield
    logger.info("axiom.shutdown")


app = FastAPI(title="Axiom OS API", version="0.1.0", lifespan=lifespan)
app.include_router(models_router)
app.include_router(knowledge_router)
app.include_router(agents_router)
app.include_router(agent_fabric_router)
app.include_router(tools_router)
app.include_router(memory_router)
app.include_router(approvals_router)
app.include_router(observability_router)


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
