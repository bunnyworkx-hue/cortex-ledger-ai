from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    """CLAUDE.md §31's Tool Registry entry: name, description, schema,
    permissions, risk level. `source` records provenance (`"mcp:<server>"`
    or `"native"`) so a caller can tell an auto-discovered MCP tool from
    a hand-registered one.
    """

    name: str
    description: str
    input_schema: dict
    source: str
    permissions: tuple[str, ...] = ()
    risk_level: str = "low"


@dataclass(frozen=True, slots=True)
class ToolCallResult:
    content: dict
    is_error: bool = False


class ToolHandler(Protocol):
    async def __call__(self, arguments: dict) -> ToolCallResult: ...


class ToolNotFoundError(KeyError):
    pass


class ToolPermissionDeniedError(PermissionError):
    pass


class ToolExecutionError(RuntimeError):
    pass
