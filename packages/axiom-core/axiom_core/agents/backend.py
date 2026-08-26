from typing import Protocol, runtime_checkable

from axiom_core.agents.types import Agent, AgentResult, AgentTask


@runtime_checkable
class AgentBackend(Protocol):
    """The provider-neutral seam every agent execution backend
    implements — mirrors ModelBackend/KnowledgeBackend. Per CLAUDE.md
    §30: potential implementations are AxiomNativeBackend (this
    milestone), HermesBackend (Milestone 13), and future external agent
    runtimes. Nothing above this protocol should know which backend ran
    the task.
    """

    backend_name: str

    async def execute(self, agent: Agent, task: AgentTask) -> AgentResult: ...

    async def is_configured(self) -> bool:
        """Cheap, local, no-network check — mirrors ModelBackend /
        KnowledgeBackend.is_configured()."""
        ...


class AgentBackendError(RuntimeError):
    """Raised when a backend's execute() fails for an upstream reason
    (the underlying model/agent-runtime call itself failed) — as opposed
    to AgentBackendNotFoundError (no backend registered)."""


class AgentBackendNotFoundError(KeyError):
    pass


class AgentBackendRegistry:
    """In-memory registry of configured agent execution backends —
    mirrors ModelGatewayRegistry / KnowledgeGatewayRegistry.
    """

    def __init__(self) -> None:
        self._backends: dict[str, AgentBackend] = {}

    def register(self, backend: AgentBackend) -> None:
        self._backends[backend.backend_name] = backend

    def get(self, backend_name: str) -> AgentBackend:
        try:
            return self._backends[backend_name]
        except KeyError as exc:
            available = ", ".join(sorted(self._backends)) or "(none registered)"
            raise AgentBackendNotFoundError(
                f"No agent backend registered for {backend_name!r}. Available: {available}"
            ) from exc

    def list_backends(self) -> list[str]:
        return sorted(self._backends)
