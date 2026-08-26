import time

from axiom_core.logging import get_logger
from axiom_core.tools.types import (
    ToolCallResult,
    ToolDefinition,
    ToolExecutionError,
    ToolHandler,
    ToolNotFoundError,
    ToolPermissionDeniedError,
)

logger = get_logger(__name__)


class ToolRegistry:
    """CLAUDE.md §31/§32: register/discover/authorize/execute/audit.

    Full policy enforcement (budgets, rate limits, human approval) is
    Milestone 15 — this registry does the part that's real today:
    permission-set checking when a caller supplies one, and an audit log
    line on every call either way. When `granted_permissions` is omitted,
    the call is allowed and the log line says so explicitly — no policy
    layer is configured yet, so this is not silently pretending to
    enforce something it doesn't (CLAUDE.md §56/§57).
    """

    def __init__(self) -> None:
        self._tools: dict[str, tuple[ToolDefinition, ToolHandler]] = {}

    def register(self, definition: ToolDefinition, handler: ToolHandler) -> None:
        self._tools[definition.name] = (definition, handler)

    def get(self, name: str) -> ToolDefinition:
        try:
            return self._tools[name][0]
        except KeyError as exc:
            raise ToolNotFoundError(f"No tool registered with name {name!r}") from exc

    def list(self) -> list[ToolDefinition]:
        return sorted((d for d, _ in self._tools.values()), key=lambda d: d.name)

    async def execute(
        self,
        name: str,
        arguments: dict,
        *,
        granted_permissions: set[str] | None = None,
    ) -> ToolCallResult:
        definition, handler = self._tools.get(name, (None, None))
        if definition is None:
            raise ToolNotFoundError(f"No tool registered with name {name!r}")

        permission_check = "not_enforced"
        if granted_permissions is not None:
            missing = set(definition.permissions) - granted_permissions
            if missing:
                logger.warning(
                    "axiom.tool.audit",
                    tool=name,
                    risk_level=definition.risk_level,
                    permission_check="denied",
                    missing_permissions=sorted(missing),
                )
                raise ToolPermissionDeniedError(
                    f"Tool {name!r} requires permissions {sorted(missing)} that were not granted"
                )
            permission_check = "granted"

        started = time.monotonic()
        try:
            result = await handler(arguments)
        except Exception as exc:
            duration_ms = round((time.monotonic() - started) * 1000, 1)
            logger.warning(
                "axiom.tool.audit",
                tool=name,
                risk_level=definition.risk_level,
                permission_check=permission_check,
                status="error",
                duration_ms=duration_ms,
                error=str(exc),
            )
            raise ToolExecutionError(f"Tool {name!r} execution failed: {exc}") from exc

        duration_ms = round((time.monotonic() - started) * 1000, 1)
        logger.info(
            "axiom.tool.audit",
            tool=name,
            risk_level=definition.risk_level,
            permission_check=permission_check,
            status="error" if result.is_error else "ok",
            duration_ms=duration_ms,
        )
        return result
