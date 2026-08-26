import pytest

from axiom_core.tools import (
    ToolCallResult,
    ToolDefinition,
    ToolExecutionError,
    ToolNotFoundError,
    ToolPermissionDeniedError,
    ToolRegistry,
)


def _echo_definition(name: str = "echo", permissions: tuple[str, ...] = ()) -> ToolDefinition:
    return ToolDefinition(
        name=name,
        description="Echoes its input.",
        input_schema={"type": "object"},
        source="native",
        permissions=permissions,
        risk_level="low",
    )


@pytest.mark.asyncio
async def test_register_get_and_list():
    registry = ToolRegistry()
    definition = _echo_definition()

    async def handler(arguments: dict) -> ToolCallResult:
        return ToolCallResult(content=arguments)

    registry.register(definition, handler)

    assert registry.get("echo") is definition
    assert registry.list() == [definition]


def test_get_missing_tool_raises():
    registry = ToolRegistry()
    with pytest.raises(ToolNotFoundError):
        registry.get("does-not-exist")


@pytest.mark.asyncio
async def test_execute_calls_the_handler_and_returns_its_result():
    registry = ToolRegistry()

    async def handler(arguments: dict) -> ToolCallResult:
        return ToolCallResult(content={"echoed": arguments["value"]})

    registry.register(_echo_definition(), handler)

    result = await registry.execute("echo", {"value": "hi"})

    assert result.content == {"echoed": "hi"}
    assert result.is_error is False


@pytest.mark.asyncio
async def test_execute_missing_tool_raises_not_found():
    registry = ToolRegistry()
    with pytest.raises(ToolNotFoundError):
        await registry.execute("does-not-exist", {})


@pytest.mark.asyncio
async def test_execute_without_granted_permissions_allows_the_call():
    # No Policy Engine yet (Milestone 15) — omitting granted_permissions
    # must not block execution, only skip the check.
    registry = ToolRegistry()

    async def handler(arguments: dict) -> ToolCallResult:
        return ToolCallResult(content={})

    registry.register(_echo_definition(permissions=("secret.read",)), handler)

    result = await registry.execute("echo", {})
    assert result.content == {}


@pytest.mark.asyncio
async def test_execute_denies_when_granted_permissions_are_insufficient():
    registry = ToolRegistry()

    async def handler(arguments: dict) -> ToolCallResult:
        return ToolCallResult(content={})

    registry.register(_echo_definition(permissions=("secret.read",)), handler)

    with pytest.raises(ToolPermissionDeniedError):
        await registry.execute("echo", {}, granted_permissions=set())


@pytest.mark.asyncio
async def test_execute_allows_when_granted_permissions_are_sufficient():
    registry = ToolRegistry()

    async def handler(arguments: dict) -> ToolCallResult:
        return ToolCallResult(content={"ok": True})

    registry.register(_echo_definition(permissions=("secret.read",)), handler)

    result = await registry.execute("echo", {}, granted_permissions={"secret.read", "other"})
    assert result.content == {"ok": True}


@pytest.mark.asyncio
async def test_execute_wraps_handler_exceptions():
    registry = ToolRegistry()

    async def handler(arguments: dict) -> ToolCallResult:
        raise RuntimeError("boom")

    registry.register(_echo_definition(), handler)

    with pytest.raises(ToolExecutionError, match="boom"):
        await registry.execute("echo", {})
