from axiom_agent_fabric import AgentInvocationGateway
from axiom_core.agents import AgentBackendRegistry, Execution, ExecutionStore
from axiom_core.logging import get_logger
from axiom_core.memory import MemoryRecord, MemoryScope, MemoryStore

logger = get_logger(__name__)


async def run_delegation(
    gateway: AgentInvocationGateway,
    backend_registry: AgentBackendRegistry,
    memory_store: MemoryStore | None,
    execution_store: ExecutionStore | None,
    *,
    agent_id: str,
    task_input: str,
    backend_name: str = "axiom_native",
    context: str | None = None,
) -> Execution:
    """The one real path from (agent_id, task_input) to a persisted
    Execution — shared by ``POST /v1/agent-fabric/agents/{id}/delegate``
    and the ``delegate_to_agent`` native tool (Milestone 21's
    agent-to-agent orchestration), so a delegation triggered through the
    tool path gets identical tracing/memory persistence to one triggered
    directly through the API, not a shortcut. Callers translate
    ``AgentNotFoundError``/``AgentBackendNotFoundError`` themselves — the
    right response shape (HTTP status vs. ``ToolCallResult(is_error=True)``)
    differs per caller.
    """
    backend = backend_registry.get(backend_name)
    execution = await gateway.delegate(agent_id, task_input, backend=backend, context=context)

    if execution_store is not None:
        # CLAUDE.md §93: every execution is traced, success or failure.
        # Best-effort: an observability write must not fail a delegation
        # that otherwise succeeded (or mask why one failed).
        try:
            await execution_store.record(execution)
        except Exception as exc:  # noqa: BLE001 — observability is supplementary, not critical path
            logger.warning("axiom.execution.record_failed", execution_id=execution.execution_id, error=str(exc))

    if memory_store is not None and execution.result is not None:
        # CLAUDE.md §38: task memory, deliberately written — not every
        # execution auto-becomes long-term memory, just this run's
        # record. Best-effort: a memory write failure must not fail a
        # successful delegation.
        try:
            await memory_store.save(
                MemoryRecord.new(
                    scope=MemoryScope.TASK,
                    owner_id=agent_id,
                    content=f"Task: {task_input}\n\nResult: {execution.result.content}",
                    source=f"execution:{execution.execution_id}",
                )
            )
        except Exception as exc:  # noqa: BLE001 — memory is supplementary, not critical path
            logger.warning("axiom.memory.save_failed", execution_id=execution.execution_id, error=str(exc))

    return execution
