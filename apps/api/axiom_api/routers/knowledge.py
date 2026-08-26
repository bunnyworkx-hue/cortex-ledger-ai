from fastapi import APIRouter, Depends, HTTPException

from axiom_core.knowledge import KnowledgeBackendNotFoundError, KnowledgeGatewayRegistry
from axiom_graphify import GraphifyMcpError

from axiom_api.dependencies import get_knowledge_gateway
from axiom_api.schemas import KnowledgeAnswerOut

router = APIRouter(prefix="/v1/knowledge", tags=["knowledge"])


@router.get("")
async def list_knowledge_backends(
    gateway: KnowledgeGatewayRegistry = Depends(get_knowledge_gateway),
) -> dict[str, dict[str, str]]:
    """Local-only status per registered backend — no network calls to the
    MCP server itself, mirrors GET /v1/models.
    """
    backends = {}
    for name in gateway.list_backends():
        backend = gateway.get(name)
        backends[name] = "configured" if await backend.is_configured() else "not_configured"
    return {"backends": backends}


def _get_graphify(gateway: KnowledgeGatewayRegistry):
    try:
        return gateway.get("graphify")
    except KnowledgeBackendNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/search", response_model=KnowledgeAnswerOut)
async def search(
    question: str,
    token_budget: int | None = None,
    gateway: KnowledgeGatewayRegistry = Depends(get_knowledge_gateway),
) -> KnowledgeAnswerOut:
    backend = _get_graphify(gateway)
    try:
        answer = await backend.search(question, token_budget=token_budget)
    except GraphifyMcpError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return KnowledgeAnswerOut(text=answer.text)


@router.get("/node", response_model=KnowledgeAnswerOut)
async def get_node(
    label: str,
    gateway: KnowledgeGatewayRegistry = Depends(get_knowledge_gateway),
) -> KnowledgeAnswerOut:
    backend = _get_graphify(gateway)
    try:
        answer = await backend.get_node(label)
    except GraphifyMcpError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return KnowledgeAnswerOut(text=answer.text)


@router.get("/neighbors", response_model=KnowledgeAnswerOut)
async def get_neighbors(
    label: str,
    gateway: KnowledgeGatewayRegistry = Depends(get_knowledge_gateway),
) -> KnowledgeAnswerOut:
    backend = _get_graphify(gateway)
    try:
        answer = await backend.get_neighbors(label)
    except GraphifyMcpError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return KnowledgeAnswerOut(text=answer.text)


@router.get("/path", response_model=KnowledgeAnswerOut)
async def get_path(
    source: str,
    target: str,
    gateway: KnowledgeGatewayRegistry = Depends(get_knowledge_gateway),
) -> KnowledgeAnswerOut:
    backend = _get_graphify(gateway)
    try:
        answer = await backend.get_path(source, target)
    except GraphifyMcpError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return KnowledgeAnswerOut(text=answer.text)
