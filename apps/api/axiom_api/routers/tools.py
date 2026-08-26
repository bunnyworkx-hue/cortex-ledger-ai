from fastapi import APIRouter, Depends, HTTPException

from axiom_core.tools import (
    ToolExecutionError,
    ToolNotFoundError,
    ToolPermissionDeniedError,
    ToolRegistry,
)

from axiom_api.dependencies import get_tool_registry
from axiom_api.schemas import ToolCallRequest, ToolCallResultOut, ToolDefinitionOut

router = APIRouter(prefix="/v1/tools", tags=["tools"])


@router.get("", response_model=list[ToolDefinitionOut])
async def list_tools(registry: ToolRegistry = Depends(get_tool_registry)) -> list[ToolDefinitionOut]:
    return [
        ToolDefinitionOut(
            name=d.name,
            description=d.description,
            input_schema=d.input_schema,
            source=d.source,
            permissions=list(d.permissions),
            risk_level=d.risk_level,
        )
        for d in registry.list()
    ]


@router.post("/{name}/call", response_model=ToolCallResultOut)
async def call_tool(
    name: str,
    body: ToolCallRequest,
    registry: ToolRegistry = Depends(get_tool_registry),
) -> ToolCallResultOut:
    # No Policy Engine yet (Milestone 15) — granted_permissions is
    # deliberately omitted, so ToolRegistry.execute() allows the call and
    # logs "permission_check": "not_enforced" rather than pretending to
    # enforce something that isn't built yet.
    try:
        result = await registry.execute(name, body.arguments)
    except ToolNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ToolPermissionDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ToolExecutionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ToolCallResultOut(content=result.content, is_error=result.is_error)
