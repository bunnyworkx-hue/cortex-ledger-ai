from typing import Protocol

from axiom_core.memory.types import MemoryRecord, MemoryScope


class MemoryStore(Protocol):
    """The provider-neutral seam a memory backend implements — mirrors
    ModelBackend/KnowledgeBackend/AgentBackend. axiom-db's Postgres
    implementation is the first (and, for Milestone 14's scope, only)
    one; nothing above this protocol should know it's Postgres.
    """

    async def save(self, record: MemoryRecord) -> MemoryRecord: ...

    async def query(
        self,
        *,
        owner_id: str | None = None,
        scope: MemoryScope | None = None,
        tenant_id: str | None = None,
        limit: int = 50,
    ) -> list[MemoryRecord]: ...
