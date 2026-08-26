from typing import Protocol, runtime_checkable

from axiom_core.models.types import ModelRequest, ModelResponse


@runtime_checkable
class ModelBackend(Protocol):
    """The provider-neutral seam every model provider adapter implements.

    CLAUDE.md §26/§27: the Model Gateway must stay separate from any one
    provider, and Anthropic-specific logic must not leak above the
    adapter that implements this protocol.
    """

    provider_name: str

    async def generate(self, request: ModelRequest) -> ModelResponse: ...

    async def is_configured(self) -> bool:
        """Cheap, local, no-network check (e.g. "is an API key present").
        Deliberately does not make a paid API call — see ModelGatewayRegistry
        docstring for why liveness and configuration are checked separately.
        """
        ...


class ModelBackendNotFoundError(KeyError):
    pass


class ModelBackendError(RuntimeError):
    """Raised by a ModelBackend.generate() when the upstream provider call
    itself fails (rate limit, billing, transient outage, ...) — as
    opposed to ModelBackendNotFoundError (no backend registered) or
    AnthropicNotConfiguredError-style errors (no credentials at all).
    Provider-neutral on purpose: callers above the adapter layer (e.g.
    the API router) should never need to import a provider SDK's
    exception types to handle this — see CLAUDE.md §27.
    """


class ModelGatewayRegistry:
    """In-memory registry of configured model backends, composed at
    application startup (apps/api's lifespan) — not a global singleton
    baked into axiom-core, so tests can build an isolated registry per
    case.
    """

    def __init__(self) -> None:
        self._backends: dict[str, ModelBackend] = {}

    def register(self, backend: ModelBackend) -> None:
        self._backends[backend.provider_name] = backend

    def get(self, provider_name: str) -> ModelBackend:
        try:
            return self._backends[provider_name]
        except KeyError as exc:
            available = ", ".join(sorted(self._backends)) or "(none registered)"
            raise ModelBackendNotFoundError(
                f"No model backend registered for provider {provider_name!r}. "
                f"Available: {available}"
            ) from exc

    def list_providers(self) -> list[str]:
        return sorted(self._backends)
