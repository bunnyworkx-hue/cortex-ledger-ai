from axiom_core.agents import Agent, AgentBackend, AgentTask, Execution, ExecutionRunner

from axiom_agent_fabric.registry import AgentRegistry
from axiom_agent_fabric.types import AgentRecord


class AgentInvocationGateway:
    """The Agent Invocation Gateway (CLAUDE.md §11), adapted from the
    real `agency-agents-router` plugin's four-verb shape — search /
    inspect / load / delegate — confirmed in AGENT_LIBRARY_AUDIT.md §5 as
    a working reference implementation of the lazy-discovery workflow
    CLAUDE.md §9 wants, rather than a novel design invented here.

    Permission/budget/policy enforcement (CLAUDE.md §11's fuller list —
    authentication, tenant isolation, rate limits, ...) is Milestone 15
    (Policy Engine); this gateway only does discovery and execution.
    """

    def __init__(self, registry: AgentRegistry) -> None:
        self._registry = registry

    def search(self, query: str, *, division: str | None = None, limit: int = 10) -> list[AgentRecord]:
        return self._registry.search(query, division=division, limit=limit)

    def list(self, *, division: str | None = None) -> list[AgentRecord]:
        return self._registry.list(division=division)

    def inspect(self, agent_id: str) -> AgentRecord:
        return self._registry.get(agent_id)

    def load(self, agent_id: str, *, task: str | None = None) -> str:
        """Compose one specialist's system prompt for the current task —
        the same "load" semantics as agency-agents-router's
        `agency_agents_load`."""
        record = self._registry.get(agent_id)
        if task:
            return f"{record.instructions}\n\nCurrent task:\n{task}"
        return record.instructions

    async def delegate(
        self,
        agent_id: str,
        task_input: str,
        *,
        backend: AgentBackend,
        context: str | None = None,
    ) -> Execution:
        """Delegate a task to a registered agent, executed through the
        given backend (AxiomNativeBackend for now; HermesBackend in
        Milestone 13) — the same "delegate" semantics as
        agency-agents-router's `agency_agents_delegate`.
        """
        record = self._registry.get(agent_id)
        agent = Agent(
            agent_id=record.agent_id,
            name=record.name,
            instructions=record.instructions,
            backend_name=backend.backend_name,
            budget=record.budget,
        )
        task = AgentTask(input=task_input, context=context)
        return await ExecutionRunner(backend).run(agent, task)
