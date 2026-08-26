from typing import Protocol, runtime_checkable

from axiom_core.knowledge.types import KnowledgeAnswer


@runtime_checkable
class KnowledgeBackend(Protocol):
    """The provider-neutral seam every knowledge-graph backend adapter
    implements — mirrors axiom_core.models.gateway.ModelBackend. Graphify
    is the first (and, per CLAUDE.md §108, not the only intended)
    implementation; nothing above this protocol should know it's Graphify
    specifically.
    """

    backend_name: str

    async def search(self, question: str, *, token_budget: int | None = None) -> KnowledgeAnswer: ...

    async def get_node(self, label: str) -> KnowledgeAnswer: ...

    async def get_neighbors(self, label: str) -> KnowledgeAnswer: ...

    async def get_path(self, source: str, target: str) -> KnowledgeAnswer: ...

    async def is_configured(self) -> bool:
        """Cheap, local, no-network check (e.g. "is a backend URL
        configured"). Deliberately does not call the server — see
        ModelGatewayRegistry docstring for the equivalent Model Gateway
        rationale.
        """
        ...


class KnowledgeBackendNotFoundError(KeyError):
    pass


class KnowledgeGatewayRegistry:
    """In-memory registry of configured knowledge backends, composed at
    application startup — mirrors ModelGatewayRegistry.
    """

    def __init__(self) -> None:
        self._backends: dict[str, KnowledgeBackend] = {}

    def register(self, backend: KnowledgeBackend) -> None:
        self._backends[backend.backend_name] = backend

    def get(self, backend_name: str) -> KnowledgeBackend:
        try:
            return self._backends[backend_name]
        except KeyError as exc:
            available = ", ".join(sorted(self._backends)) or "(none registered)"
            raise KnowledgeBackendNotFoundError(
                f"No knowledge backend registered for {backend_name!r}. "
                f"Available: {available}"
            ) from exc

    def list_backends(self) -> list[str]:
        return sorted(self._backends)
