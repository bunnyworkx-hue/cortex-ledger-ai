from fastapi import APIRouter, Depends, HTTPException

from axiom_core.policy import ApprovalRequest, ApprovalStore, PolicyEngine, PolicyStatus
from axiom_core.tools import (
    ToolExecutionError,
    ToolNotFoundError,
    ToolPermissionDeniedError,
    ToolRegistry,
)

from axiom_api.dependencies import get_approval_store, get_policy_engine, get_tool_registry
from axiom_api.schemas import PendingApprovalOut, ToolCallRequest, ToolCallResultOut, ToolDefinitionOut

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


@router.post("/{name}/call", response_model=ToolCallResultOut | PendingApprovalOut)
async def call_tool(
    name: str,
    body: ToolCallRequest,
    registry: ToolRegistry = Depends(get_tool_registry),
    policy: PolicyEngine = Depends(get_policy_engine),
    approvals: ApprovalStore | None = Depends(get_approval_store),
) -> ToolCallResultOut | PendingApprovalOut:
    try:
        definition = registry.get(name)
    except ToolNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    decision = policy.evaluate(definition.risk_level, action=f"tool:{name}")

    if decision.status == PolicyStatus.REQUIRES_APPROVAL:
        if approvals is None:
            raise HTTPException(
                status_code=503,
                detail="This action requires approval but no approval store is configured "
                "(set AXIOM_DATABASE_URL).",
            )
        request = ApprovalRequest.new(
            action=f"tool:{name}",
            risk_level=definition.risk_level,
            reason=decision.reason,
            payload={"tool_name": name, "arguments": body.arguments},
        )
        saved = await approvals.create(request)
        return PendingApprovalOut(approval_id=saved.id, status=saved.status.value, reason=saved.reason)

    # PolicyStatus.ALLOW (DENY isn't reachable yet — v1's threshold rule
    # never denies outright, see PolicyEngine's docstring).
    try:
        result = await registry.execute(name, body.arguments)
    except ToolPermissionDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ToolExecutionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ToolCallResultOut(content=result.content, is_error=result.is_error)
