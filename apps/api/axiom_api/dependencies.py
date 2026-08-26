from fastapi import Request

from axiom_agent_fabric import AgentInvocationGateway
from axiom_core.agents import AgentBackendRegistry
from axiom_core.knowledge import KnowledgeGatewayRegistry
from axiom_core.models import ModelGatewayRegistry


def get_model_gateway(request: Request) -> ModelGatewayRegistry:
    return request.app.state.model_gateway


def get_knowledge_gateway(request: Request) -> KnowledgeGatewayRegistry:
    return request.app.state.knowledge_gateway


def get_agent_backend_gateway(request: Request) -> AgentBackendRegistry:
    return request.app.state.agent_backend_gateway


def get_agent_fabric(request: Request) -> AgentInvocationGateway | None:
    return request.app.state.agent_fabric
