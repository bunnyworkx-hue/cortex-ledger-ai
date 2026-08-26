import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


@dataclass(frozen=True, slots=True)
class Agent:
    """Minimal runtime identity for something executable.

    The full Agent Fabric registry (capabilities, tools, permissions,
    imported from the agency-agents library) is Milestone 10 — this is
    deliberately just enough for the Agent Runtime to execute a task
    against a backend. Milestone 10 populates real Agent records from the
    registry instead of callers constructing them ad hoc.

    ``budget`` (``{"max_tokens": int, "max_seconds": float}``, both
    optional) is enforced by each ``AgentBackend`` — see
    ``AxiomNativeBackend``/``HermesBackend`` docstrings for exactly what
    each backend can and can't actually enforce (CLAUDE.md §56: never
    claim enforcement that isn't real).
    """

    agent_id: str
    name: str
    instructions: str
    backend_name: str = "axiom_native"
    budget: dict = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AgentTask:
    input: str
    context: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AgentResult:
    content: str
    raw: dict = field(default_factory=dict)


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(slots=True)
class Execution:
    """A tracked run of a task. In-memory only for Milestone 9 — DB
    persistence (the `executions`/`execution_events` tables from
    CLAUDE.md §48) is layered on in the Observability milestone without
    changing this shape.
    """

    execution_id: str
    agent_id: str
    backend_name: str
    task: AgentTask
    status: ExecutionStatus = ExecutionStatus.PENDING
    result: AgentResult | None = None
    error: str | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    @staticmethod
    def new(agent: Agent, task: AgentTask) -> "Execution":
        return Execution(
            execution_id=str(uuid.uuid4()),
            agent_id=agent.agent_id,
            backend_name=agent.backend_name,
            task=task,
        )
