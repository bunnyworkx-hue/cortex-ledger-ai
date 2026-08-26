from typing import Protocol

from axiom_core.policy.types import ApprovalRequest


class ApprovalNotFoundError(KeyError):
    pass


class ApprovalStore(Protocol):
    """The provider-neutral seam an approval backend implements — mirrors
    MemoryStore. axiom-db's Postgres implementation is Milestone 16's
    concrete one.
    """

    async def create(self, request: ApprovalRequest) -> ApprovalRequest: ...

    async def get(self, approval_id: str) -> ApprovalRequest: ...

    async def list_pending(self) -> list[ApprovalRequest]: ...

    async def decide(self, approval_id: str, *, approved: bool, decided_by: str) -> ApprovalRequest: ...
