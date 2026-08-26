from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from axiom_core.agents import Execution
from axiom_db.models.execution import ExecutionRow


def _row_to_dict(row: ExecutionRow) -> dict:
    return {
        "execution_id": str(row.id),
        "agent_id": row.agent_id,
        "backend_name": row.backend_name,
        "status": row.status,
        "input": row.input,
        "output": row.output,
        "error": row.error,
        "raw": row.raw,
        "started_at": row.started_at.isoformat(),
        "completed_at": row.completed_at.isoformat() if row.completed_at else None,
        "duration_ms": row.duration_ms,
    }


class PostgresExecutionStore:
    """CLAUDE.md §93's execution traces, backed by the real `executions`
    table (Milestone 17). Records every Task -> Backend -> Result run —
    success or failure — as distinct, operational data from `memories`.
    """

    def __init__(self, sessionmaker: async_sessionmaker) -> None:
        self._sessionmaker = sessionmaker

    async def record(self, execution: Execution) -> None:
        duration_ms = None
        if execution.completed_at is not None:
            duration_ms = (execution.completed_at - execution.started_at).total_seconds() * 1000

        row = ExecutionRow(
            id=execution.execution_id,
            agent_id=execution.agent_id,
            backend_name=execution.backend_name,
            status=execution.status.value,
            input=execution.task.input,
            output=execution.result.content if execution.result else None,
            error=execution.error,
            raw=execution.result.raw if execution.result else {},
            started_at=execution.started_at,
            completed_at=execution.completed_at,
            duration_ms=duration_ms,
        )
        async with self._sessionmaker() as session:
            session.add(row)
            await session.commit()

    async def list(self, *, agent_id: str | None = None, status: str | None = None, limit: int = 50) -> list[dict]:
        stmt = select(ExecutionRow).order_by(ExecutionRow.started_at.desc()).limit(limit)
        if agent_id is not None:
            stmt = stmt.where(ExecutionRow.agent_id == agent_id)
        if status is not None:
            stmt = stmt.where(ExecutionRow.status == status)
        async with self._sessionmaker() as session:
            result = await session.execute(stmt)
            rows = result.scalars().all()
        return [_row_to_dict(row) for row in rows]

    async def get(self, execution_id: str) -> dict | None:
        async with self._sessionmaker() as session:
            row = await session.get(ExecutionRow, execution_id)
        return _row_to_dict(row) if row else None

    async def metrics(self) -> dict:
        async with self._sessionmaker() as session:
            total = await session.scalar(select(func.count()).select_from(ExecutionRow))
            succeeded = await session.scalar(
                select(func.count()).select_from(ExecutionRow).where(ExecutionRow.status == "succeeded")
            )
            failed = await session.scalar(
                select(func.count()).select_from(ExecutionRow).where(ExecutionRow.status == "failed")
            )
            avg_duration_ms = await session.scalar(select(func.avg(ExecutionRow.duration_ms)))

            by_agent_stmt = select(
                ExecutionRow.agent_id, func.count().label("count")
            ).group_by(ExecutionRow.agent_id).order_by(func.count().desc()).limit(10)
            by_agent_result = await session.execute(by_agent_stmt)
            by_agent = {agent_id: count for agent_id, count in by_agent_result.all()}

        return {
            "total_executions": total or 0,
            "succeeded": succeeded or 0,
            "failed": failed or 0,
            "success_rate": round((succeeded or 0) / total, 4) if total else None,
            "avg_duration_ms": round(avg_duration_ms, 1) if avg_duration_ms is not None else None,
            "top_agents_by_execution_count": by_agent,
        }
