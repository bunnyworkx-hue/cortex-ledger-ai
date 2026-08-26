from fastapi import Request

from axiom_agent_fabric import AgentInvocationGateway
from axiom_core.agents import AgentBackendRegistry
from axiom_core.knowledge import KnowledgeGatewayRegistry
from axiom_core.memory import MemoryStore
from axiom_core.models import ModelGatewayRegistry
from axiom_core.tools import ToolRegistry


def get_model_gateway(request: Request) -> ModelGatewayRegistry:
    return request.app.state.model_gateway


def get_knowledge_gateway(request: Request) -> KnowledgeGatewayRegistry:
    return request.app.state.knowledge_gateway


def get_agent_backend_gateway(request: Request) -> AgentBackendRegistry:
    return request.app.state.agent_backend_gateway


def get_agent_fabric(request: Request) -> AgentInvocationGateway | None:
    return request.app.state.agent_fabric


def get_tool_registry(request: Request) -> ToolRegistry:
    return request.app.state.tool_registry


def get_memory_store(request: Request) -> MemoryStore | None:
    return request.app.state.memory_store
