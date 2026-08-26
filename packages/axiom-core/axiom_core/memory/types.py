import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class MemoryScope(str, Enum):
    """CLAUDE.md §38's four memory kinds."""

    TASK = "task"
    WORKING = "working"
    LONG_TERM = "long_term"
    BUSINESS_KNOWLEDGE = "business_knowledge"


@dataclass(frozen=True, slots=True)
class MemoryRecord:
    """CLAUDE.md §38: memory must include tenant, scope, owner,
    permissions, retention, source — "do not automatically store
    everything." Nothing in Axiom writes a MemoryRecord implicitly;
    every write is a deliberate call (see ExecutionRunner's post-run
    save in Milestone 14's wiring).
    """

    id: str
    scope: MemoryScope
    owner_id: str
    content: str
    source: str
    tenant_id: str | None = None
    permissions: tuple[str, ...] = ()
    retention_days: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @staticmethod
    def new(
        *,
        scope: MemoryScope,
        owner_id: str,
        content: str,
        source: str,
        tenant_id: str | None = None,
        permissions: tuple[str, ...] = (),
        retention_days: int | None = None,
    ) -> "MemoryRecord":
        return MemoryRecord(
            id=str(uuid.uuid4()),
            scope=scope,
            owner_id=owner_id,
            content=content,
            source=source,
            tenant_id=tenant_id,
            permissions=permissions,
            retention_days=retention_days,
        )
