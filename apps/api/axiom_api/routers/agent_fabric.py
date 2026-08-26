from fastapi import APIRouter, Depends, HTTPException

from axiom_agent_fabric import AgentInvocationGateway, AgentNotFoundError
from axiom_core.agents import AgentBackendNotFoundError, AgentBackendRegistry
from axiom_core.logging import get_logger
from axiom_core.memory import MemoryRecord, MemoryScope, MemoryStore

from axiom_api.dependencies import get_agent_backend_gateway, get_agent_fabric, get_memory_store
from axiom_api.schemas import AgentRecordDetailOut, AgentRecordOut, DelegateRequest, ExecutionOut

router = APIRouter(prefix="/v1/agent-fabric", tags=["agent-fabric"])
logger = get_logger(__name__)


def _require_gateway(gateway: AgentInvocationGateway | None) -> AgentInvocationGateway:
    if gateway is None:
        raise HTTPException(
            status_code=503,
            detail="Agent Fabric is not configured — set AXIOM_AGENCY_AGENTS_PATH.",
        )
    return gateway


def _to_out(record) -> AgentRecordOut:
    return AgentRecordOut(
        agent_id=record.agent_id,
        name=record.name,
        description=record.description,
        division=record.division,
        category=record.category,
        status=record.status.value,
        is_curated=record.is_curated,
        capabilities=list(record.capabilities) if record.capabilities else None,
        permissions=list(record.permissions) if record.permissions else None,
        risk_level=record.risk_level,
        frontmatter_tools=list(record.frontmatter_tools),
    )


@router.get("")
async def status(gateway: AgentInvocationGateway | None = Depends(get_agent_fabric)) -> dict:
    if gateway is None:
        return {"configured": False, "total_agents": 0, "curated_agents": 0}
    all_records = gateway.list()
    curated = [r for r in all_records if r.is_curated]
    by_division: dict[str, int] = {}
    for record in all_records:
        by_division[record.division] = by_division.get(record.division, 0) + 1
    return {
        "configured": True,
        "total_agents": len(all_records),
        "curated_agents": len(curated),
        "by_division": by_division,
    }


@router.get("/search", response_model=list[AgentRecordOut])
async def search(
    q: str,
    division: str | None = None,
    limit: int = 10,
    gateway: AgentInvocationGateway | None = Depends(get_agent_fabric),
) -> list[AgentRecordOut]:
    gateway = _require_gateway(gateway)
    results = gateway.search(q, division=division, limit=limit)
    return [_to_out(r) for r in results]


@router.get("/agents/{agent_id:path}", response_model=AgentRecordDetailOut)
async def inspect(
    agent_id: str,
    gateway: AgentInvocationGateway | None = Depends(get_agent_fabric),
) -> AgentRecordDetailOut:
    gateway = _require_gateway(gateway)
    try:
        record = gateway.inspect(agent_id)
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return AgentRecordDetailOut(**_to_out(record).model_dump(), instructions=record.instructions,
                                 source_path=record.source_path, source_commit=record.source_commit)


@router.post("/agents/{agent_id:path}/delegate", response_model=ExecutionOut)
async def delegate(
    agent_id: str,
    body: DelegateRequest,
    gateway: AgentInvocationGateway | None = Depends(get_agent_fabric),
    backend_registry: AgentBackendRegistry = Depends(get_agent_backend_gateway),
    memory_store: MemoryStore | None = Depends(get_memory_store),
) -> ExecutionOut:
    gateway = _require_gateway(gateway)
    try:
        backend = backend_registry.get(body.backend or "axiom_native")
    except AgentBackendNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    try:
        execution = await gateway.delegate(agent_id, body.input, backend=backend, context=body.context)
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if execution.status.value == "failed":
        raise HTTPException(status_code=502, detail=execution.error)

    if memory_store is not None and execution.result is not None:
        # CLAUDE.md §38: task memory, deliberately written — not every
        # execution auto-becomes long-term memory, just this run's
        # record. Best-effort: a memory write failure must not fail a
        # successful delegation.
        try:
            await memory_store.save(
                MemoryRecord.new(
                    scope=MemoryScope.TASK,
                    owner_id=agent_id,
                    content=f"Task: {body.input}\n\nResult: {execution.result.content}",
                    source=f"execution:{execution.execution_id}",
                )
            )
        except Exception as exc:  # noqa: BLE001 — memory is supplementary, not critical path
            logger.warning("axiom.memory.save_failed", execution_id=execution.execution_id, error=str(exc))

    return ExecutionOut(
        execution_id=execution.execution_id,
        agent_id=execution.agent_id,
        backend_name=execution.backend_name,
        status=execution.status.value,
        content=execution.result.content if execution.result else None,
    )
