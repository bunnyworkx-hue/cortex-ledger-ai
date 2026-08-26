from fastapi import APIRouter, Depends, HTTPException

from axiom_core.agents import (
    Agent,
    AgentBackendNotFoundError,
    AgentBackendRegistry,
    AgentTask,
    ExecutionRunner,
)
from axiom_core.logging import get_logger

from axiom_api.dependencies import get_agent_backend_gateway, get_execution_store
from axiom_api.schemas import ExecuteAgentRequest, ExecutionOut

logger = get_logger(__name__)

router = APIRouter(prefix="/v1/agents", tags=["agents"])


@router.get("")
async def list_agent_backends(
    gateway: AgentBackendRegistry = Depends(get_agent_backend_gateway),
) -> dict[str, dict[str, str]]:
    """Local-only status per registered backend — mirrors GET /v1/models
    and GET /v1/knowledge. There is no Agent Registry yet (Milestone 10);
    this milestone proves the Task -> Backend -> Execution -> Result path.
    """
    backends = {}
    for name in gateway.list_backends():
        backend = gateway.get(name)
        backends[name] = "configured" if await backend.is_configured() else "not_configured"
    return {"backends": backends}


@router.post("/execute", response_model=ExecutionOut)
async def execute(
    body: ExecuteAgentRequest,
    gateway: AgentBackendRegistry = Depends(get_agent_backend_gateway),
    execution_store=Depends(get_execution_store),
) -> ExecutionOut:
    try:
        backend = gateway.get(body.backend or "axiom_native")
    except AgentBackendNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    agent = Agent(
        agent_id=body.agent_id,
        name=body.agent_name,
        instructions=body.instructions,
        backend_name=backend.backend_name,
    )
    task = AgentTask(input=body.input, context=body.context)

    execution = await ExecutionRunner(backend).run(agent, task)

    if execution_store is not None:
        try:
            await execution_store.record(execution)
        except Exception as exc:  # noqa: BLE001 — observability is supplementary, not critical path
            logger.warning("axiom.execution.record_failed", execution_id=execution.execution_id, error=str(exc))

    if execution.status.value == "failed":
        # A real backend failure (e.g. the model call itself failed) —
        # clean 502, not a silently-successful-looking response.
        raise HTTPException(status_code=502, detail=execution.error)

    return ExecutionOut(
        execution_id=execution.execution_id,
        agent_id=execution.agent_id,
        backend_name=execution.backend_name,
        status=execution.status.value,
        content=execution.result.content if execution.result else None,
    )
