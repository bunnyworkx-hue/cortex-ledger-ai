from fastapi import APIRouter, Depends, HTTPException

from axiom_core.memory import MemoryRecord, MemoryScope, MemoryStore

from axiom_api.auth import AuthenticatedCaller, require_caller
from axiom_api.dependencies import get_memory_store
from axiom_api.schemas import MemoryRecordOut, SaveMemoryRequest

router = APIRouter(prefix="/v1/memory", tags=["memory"])


def _require_store(store: MemoryStore | None) -> MemoryStore:
    if store is None:
        raise HTTPException(status_code=503, detail="Memory store is not configured — set AXIOM_DATABASE_URL.")
    return store


def _to_out(record: MemoryRecord) -> MemoryRecordOut:
    return MemoryRecordOut(
        id=record.id,
        scope=record.scope.value,
        owner_id=record.owner_id,
        tenant_id=record.tenant_id,
        content=record.content,
        source=record.source,
        permissions=list(record.permissions),
        retention_days=record.retention_days,
        created_at=record.created_at.isoformat(),
    )


@router.post("", response_model=MemoryRecordOut)
async def save_memory(
    body: SaveMemoryRequest,
    caller: AuthenticatedCaller = Depends(require_caller),
    store: MemoryStore | None = Depends(get_memory_store),
) -> MemoryRecordOut:
    store = _require_store(store)
    # owner_id/tenant_id come from the authenticated caller, never the
    # request body — a caller can no longer write a record under any
    # owner_id it merely names (docs/security/SECURITY_AUDIT.md §6-7).
    record = MemoryRecord.new(
        scope=MemoryScope(body.scope),
        owner_id=caller.owner_id,
        content=body.content,
        source=body.source,
        tenant_id=caller.tenant_id,
        permissions=tuple(body.permissions),
        retention_days=body.retention_days,
    )
    saved = await store.save(record)
    return _to_out(saved)


@router.get("", response_model=list[MemoryRecordOut])
async def query_memory(
    scope: str | None = None,
    limit: int = 50,
    caller: AuthenticatedCaller = Depends(require_caller),
    store: MemoryStore | None = Depends(get_memory_store),
) -> list[MemoryRecordOut]:
    store = _require_store(store)
    # Same fix, read side: owner_id/tenant_id are the authenticated
    # caller's own identity, not a caller-supplied filter — a caller can
    # no longer read another owner's records by naming their owner_id.
    records = await store.query(
        owner_id=caller.owner_id,
        scope=MemoryScope(scope) if scope else None,
        tenant_id=caller.tenant_id,
        limit=limit,
    )
    return [_to_out(r) for r in records]
