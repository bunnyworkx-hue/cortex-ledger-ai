from axiom_core.memory import MemoryRecord, MemoryScope
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from axiom_db.models.memory import MemoryRow


def _row_to_record(row: MemoryRow) -> MemoryRecord:
    return MemoryRecord(
        id=str(row.id),
        scope=MemoryScope(row.scope),
        owner_id=row.owner_id,
        content=row.content,
        source=row.source,
        tenant_id=row.tenant_id,
        permissions=tuple(row.permissions or ()),
        retention_days=row.retention_days,
        created_at=row.created_at,
    )


class PostgresMemoryStore:
    """The real implementation of axiom_core.memory.MemoryStore, backed
    by the `memories` table (Milestone 14).
    """

    def __init__(self, sessionmaker: async_sessionmaker) -> None:
        self._sessionmaker = sessionmaker

    async def save(self, record: MemoryRecord) -> MemoryRecord:
        row = MemoryRow(
            id=record.id,
            scope=record.scope.value,
            owner_id=record.owner_id,
            tenant_id=record.tenant_id,
            content=record.content,
            source=record.source,
            permissions=list(record.permissions),
            retention_days=record.retention_days,
        )
        async with self._sessionmaker() as session:
            session.add(row)
            await session.commit()
            await session.refresh(row)
        return _row_to_record(row)

    async def query(
        self,
        *,
        owner_id: str | None = None,
        scope: MemoryScope | None = None,
        tenant_id: str | None = None,
        limit: int = 50,
    ) -> list[MemoryRecord]:
        stmt = select(MemoryRow).order_by(MemoryRow.created_at.desc()).limit(limit)
        if owner_id is not None:
            stmt = stmt.where(MemoryRow.owner_id == owner_id)
        if scope is not None:
            stmt = stmt.where(MemoryRow.scope == scope.value)
        if tenant_id is not None:
            stmt = stmt.where(MemoryRow.tenant_id == tenant_id)

        async with self._sessionmaker() as session:
            result = await session.execute(stmt)
            rows = result.scalars().all()
        return [_row_to_record(row) for row in rows]
