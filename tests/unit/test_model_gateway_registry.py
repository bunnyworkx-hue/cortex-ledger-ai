import pytest

from axiom_core.models import ModelBackendNotFoundError, ModelGatewayRegistry


class _StubBackend:
    provider_name = "stub"

    async def is_configured(self) -> bool:
        return True

    async def generate(self, request):  # pragma: no cover - not exercised here
        raise NotImplementedError


def test_register_and_get():
    registry = ModelGatewayRegistry()
    backend = _StubBackend()
    registry.register(backend)

    assert registry.get("stub") is backend
    assert registry.list_providers() == ["stub"]


def test_get_missing_backend_raises_with_available_list():
    registry = ModelGatewayRegistry()
    registry.register(_StubBackend())

    with pytest.raises(ModelBackendNotFoundError, match="stub"):
        registry.get("anthropic")
