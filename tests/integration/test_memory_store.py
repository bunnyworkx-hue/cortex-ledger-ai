import uuid

import pytest

from axiom_core.memory import MemoryRecord, MemoryScope
from axiom_db.engine import get_sessionmaker
from axiom_db.memory import PostgresMemoryStore
from axiom_db.models.memory import MemoryRow


@pytest.fixture
async def memory_store():
    store = PostgresMemoryStore(get_sessionmaker())
    yield store


@pytest.mark.asyncio
async def test_save_and_query_round_trip_against_the_real_database(memory_store):
    owner_id = f"test-owner-{uuid.uuid4()}"
    record = MemoryRecord.new(
        scope=MemoryScope.TASK,
        owner_id=owner_id,
        content="Real DB round trip test.",
        source="pytest",
        permissions=("test.read",),
    )

    try:
        saved = await memory_store.save(record)
        assert saved.id == record.id
        assert saved.created_at is not None

        results = await memory_store.query(owner_id=owner_id)
        assert len(results) == 1
        assert results[0].content == "Real DB round trip test."
        assert results[0].scope == MemoryScope.TASK
        assert results[0].permissions == ("test.read",)

        scoped = await memory_store.query(owner_id=owner_id, scope=MemoryScope.LONG_TERM)
        assert scoped == []
    finally:
        # Clean up: this is a real database, not a throwaway test fixture.
        sessionmaker = get_sessionmaker()
        async with sessionmaker() as session:
            row = await session.get(MemoryRow, uuid.UUID(record.id))
            if row is not None:
                await session.delete(row)
                await session.commit()
