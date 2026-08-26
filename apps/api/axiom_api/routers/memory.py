from fastapi import APIRouter, Depends, HTTPException

from axiom_core.memory import MemoryRecord, MemoryScope, MemoryStore

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
    store: MemoryStore | None = Depends(get_memory_store),
) -> MemoryRecordOut:
    store = _require_store(store)
    record = MemoryRecord.new(
        scope=MemoryScope(body.scope),
        owner_id=body.owner_id,
        content=body.content,
        source=body.source,
        tenant_id=body.tenant_id,
        permissions=tuple(body.permissions),
        retention_days=body.retention_days,
    )
    saved = await store.save(record)
    return _to_out(saved)


@router.get("", response_model=list[MemoryRecordOut])
async def query_memory(
    owner_id: str | None = None,
    scope: str | None = None,
    tenant_id: str | None = None,
    limit: int = 50,
    store: MemoryStore | None = Depends(get_memory_store),
) -> list[MemoryRecordOut]:
    store = _require_store(store)
    records = await store.query(
        owner_id=owner_id,
        scope=MemoryScope(scope) if scope else None,
        tenant_id=tenant_id,
        limit=limit,
    )
    return [_to_out(r) for r in records]
