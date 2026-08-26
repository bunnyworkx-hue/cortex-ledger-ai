from datetime import UTC, datetime

from axiom_core.policy import ApprovalNotFoundError, ApprovalRequest, ApprovalStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from axiom_db.models.approval import ApprovalRow


def _row_to_record(row: ApprovalRow) -> ApprovalRequest:
    return ApprovalRequest(
        id=str(row.id),
        action=row.action,
        risk_level=row.risk_level,
        reason=row.reason,
        payload=row.payload,
        status=ApprovalStatus(row.status),
        created_at=row.created_at,
        decided_at=row.decided_at,
        decided_by=row.decided_by,
    )


class PostgresApprovalStore:
    """The real implementation of axiom_core.policy.ApprovalStore, backed
    by the `approvals` table (Milestone 16).
    """

    def __init__(self, sessionmaker: async_sessionmaker) -> None:
        self._sessionmaker = sessionmaker

    async def create(self, request: ApprovalRequest) -> ApprovalRequest:
        row = ApprovalRow(
            id=request.id,
            action=request.action,
            risk_level=request.risk_level,
            reason=request.reason,
            payload=request.payload,
            status=request.status.value,
        )
        async with self._sessionmaker() as session:
            session.add(row)
            await session.commit()
            await session.refresh(row)
        return _row_to_record(row)

    async def get(self, approval_id: str) -> ApprovalRequest:
        async with self._sessionmaker() as session:
            row = await session.get(ApprovalRow, approval_id)
        if row is None:
            raise ApprovalNotFoundError(f"No approval request with id {approval_id!r}")
        return _row_to_record(row)

    async def list_pending(self) -> list[ApprovalRequest]:
        stmt = select(ApprovalRow).where(ApprovalRow.status == "pending").order_by(ApprovalRow.created_at)
        async with self._sessionmaker() as session:
            result = await session.execute(stmt)
            rows = result.scalars().all()
        return [_row_to_record(row) for row in rows]

    async def decide(self, approval_id: str, *, approved: bool, decided_by: str) -> ApprovalRequest:
        async with self._sessionmaker() as session:
            row = await session.get(ApprovalRow, approval_id)
            if row is None:
                raise ApprovalNotFoundError(f"No approval request with id {approval_id!r}")
            row.status = ApprovalStatus.APPROVED.value if approved else ApprovalStatus.REJECTED.value
            row.decided_at = datetime.now(UTC)
            row.decided_by = decided_by
            await session.commit()
            await session.refresh(row)
        return _row_to_record(row)
