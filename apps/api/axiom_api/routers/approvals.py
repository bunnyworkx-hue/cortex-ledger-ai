from fastapi import APIRouter, Depends, HTTPException

from axiom_core.policy import ApprovalNotFoundError, ApprovalStatus, ApprovalStore
from axiom_core.tools import ToolExecutionError, ToolRegistry

from axiom_api.dependencies import get_approval_store, get_tool_registry
from axiom_api.schemas import ApprovalOut, DecideApprovalRequest, ToolCallResultOut

router = APIRouter(prefix="/v1/approvals", tags=["approvals"])


def _require_store(store: ApprovalStore | None) -> ApprovalStore:
    if store is None:
        raise HTTPException(status_code=503, detail="Approval store is not configured — set AXIOM_DATABASE_URL.")
    return store


def _to_out(request) -> ApprovalOut:
    return ApprovalOut(
        id=request.id,
        action=request.action,
        risk_level=request.risk_level,
        reason=request.reason,
        payload=request.payload,
        status=request.status.value,
        created_at=request.created_at.isoformat(),
        decided_at=request.decided_at.isoformat() if request.decided_at else None,
        decided_by=request.decided_by,
    )


@router.get("", response_model=list[ApprovalOut])
async def list_pending(store: ApprovalStore | None = Depends(get_approval_store)) -> list[ApprovalOut]:
    store = _require_store(store)
    return [_to_out(r) for r in await store.list_pending()]


@router.get("/{approval_id}", response_model=ApprovalOut)
async def get_approval(
    approval_id: str, store: ApprovalStore | None = Depends(get_approval_store)
) -> ApprovalOut:
    store = _require_store(store)
    try:
        return _to_out(await store.get(approval_id))
    except ApprovalNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{approval_id}/reject", response_model=ApprovalOut)
async def reject(
    approval_id: str,
    body: DecideApprovalRequest,
    store: ApprovalStore | None = Depends(get_approval_store),
) -> ApprovalOut:
    store = _require_store(store)
    try:
        request = await store.get(approval_id)
        if request.status != ApprovalStatus.PENDING:
            raise HTTPException(status_code=409, detail=f"Approval {approval_id!r} already {request.status.value}")
        decided = await store.decide(approval_id, approved=False, decided_by=body.decided_by)
    except ApprovalNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _to_out(decided)


@router.post("/{approval_id}/approve", response_model=ToolCallResultOut)
async def approve(
    approval_id: str,
    body: DecideApprovalRequest,
    store: ApprovalStore | None = Depends(get_approval_store),
    registry: ToolRegistry = Depends(get_tool_registry),
) -> ToolCallResultOut:
    """Approving doesn't just flip a status flag — it actually executes
    the originally-proposed action for real (CLAUDE.md §37: Approve ->
    Execute -> Verify -> Audit), through the same ToolRegistry.execute()
    audit-logging path any other tool call takes.
    """
    store = _require_store(store)
    try:
        request = await store.get(approval_id)
    except ApprovalNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if request.status != ApprovalStatus.PENDING:
        raise HTTPException(status_code=409, detail=f"Approval {approval_id!r} already {request.status.value}")

    await store.decide(approval_id, approved=True, decided_by=body.decided_by)

    try:
        result = await registry.execute(request.payload["tool_name"], request.payload["arguments"])
    except ToolExecutionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ToolCallResultOut(content=result.content, is_error=result.is_error)
