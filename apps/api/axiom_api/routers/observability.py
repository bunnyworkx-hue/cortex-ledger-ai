from fastapi import APIRouter, Depends, HTTPException

from axiom_core.agents import ExecutionStore

from axiom_api.dependencies import get_execution_store
from axiom_api.schemas import ExecutionTraceOut, ObservabilityMetricsOut

router = APIRouter(prefix="/v1/observability", tags=["observability"])


def _require_store(store: ExecutionStore | None) -> ExecutionStore:
    if store is None:
        raise HTTPException(
            status_code=503, detail="Execution store is not configured — set AXIOM_DATABASE_URL."
        )
    return store


@router.get("/executions", response_model=list[ExecutionTraceOut])
async def list_executions(
    agent_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
    store: ExecutionStore | None = Depends(get_execution_store),
) -> list[ExecutionTraceOut]:
    store = _require_store(store)
    records = await store.list(agent_id=agent_id, status=status, limit=limit)
    return [ExecutionTraceOut(**r) for r in records]


@router.get("/executions/{execution_id}", response_model=ExecutionTraceOut)
async def get_execution(
    execution_id: str, store: ExecutionStore | None = Depends(get_execution_store)
) -> ExecutionTraceOut:
    store = _require_store(store)
    record = await store.get(execution_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"No execution with id {execution_id!r}")
    return ExecutionTraceOut(**record)


@router.get("/metrics", response_model=ObservabilityMetricsOut)
async def metrics(store: ExecutionStore | None = Depends(get_execution_store)) -> ObservabilityMetricsOut:
    store = _require_store(store)
    return ObservabilityMetricsOut(**await store.metrics())
