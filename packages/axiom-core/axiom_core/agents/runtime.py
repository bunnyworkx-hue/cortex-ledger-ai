from datetime import UTC, datetime

from axiom_core.agents.backend import AgentBackend, AgentBackendError
from axiom_core.agents.types import Agent, AgentTask, Execution, ExecutionStatus
from axiom_core.logging import bind_execution_context, clear_execution_context, get_logger

logger = get_logger(__name__)


class ExecutionRunner:
    """Ties an Agent + Task to a specific Backend and produces a tracked
    Execution — the Agent/Task/Execution/Result primitives CLAUDE.md §85
    calls for. In-memory only; DB persistence is layered on later without
    changing this shape (see Execution's docstring).
    """

    def __init__(self, backend: AgentBackend) -> None:
        self._backend = backend

    async def run(self, agent: Agent, task: AgentTask) -> Execution:
        execution = Execution.new(agent, task)
        execution.status = ExecutionStatus.RUNNING

        bind_execution_context(
            execution_id=execution.execution_id, agent_id=agent.agent_id, backend=self._backend.backend_name
        )
        logger.info("axiom.execution.started")
        try:
            result = await self._backend.execute(agent, task)
        except AgentBackendError as exc:
            execution.status = ExecutionStatus.FAILED
            execution.error = str(exc)
            logger.warning("axiom.execution.failed", error=str(exc))
        else:
            execution.status = ExecutionStatus.SUCCEEDED
            execution.result = result
            logger.info("axiom.execution.succeeded")
        finally:
            execution.completed_at = datetime.now(UTC)
            clear_execution_context()

        return execution
