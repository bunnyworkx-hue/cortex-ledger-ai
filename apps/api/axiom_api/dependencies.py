from fastapi import Request

from axiom_core.knowledge import KnowledgeGatewayRegistry
from axiom_core.models import ModelGatewayRegistry


def get_model_gateway(request: Request) -> ModelGatewayRegistry:
    return request.app.state.model_gateway


def get_knowledge_gateway(request: Request) -> KnowledgeGatewayRegistry:
    return request.app.state.knowledge_gateway
