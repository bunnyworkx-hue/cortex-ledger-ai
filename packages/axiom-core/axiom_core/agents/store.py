from typing import Protocol

from axiom_core.agents.types import Execution


class ExecutionStore(Protocol):
    """The provider-neutral seam an execution-trace backend implements —
    mirrors MemoryStore/ApprovalStore. CLAUDE.md §93: every execution is
    traced, success or failure.
    """

    async def record(self, execution: Execution) -> None: ...

    async def list(
        self, *, agent_id: str | None = None, status: str | None = None, limit: int = 50
    ) -> list[dict]: ...

    async def get(self, execution_id: str) -> dict | None: ...

    async def metrics(self) -> dict: ...
