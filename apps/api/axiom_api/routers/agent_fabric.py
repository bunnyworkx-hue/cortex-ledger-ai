from fastapi import APIRouter, Depends, HTTPException

from axiom_agent_fabric import AgentInvocationGateway, AgentNotFoundError
from axiom_core.agents import AgentBackendNotFoundError, AgentBackendRegistry
from axiom_core.memory import MemoryStore
from axiom_core.policy import ApprovalRequest, ApprovalStore, PolicyEngine, PolicyStatus

from axiom_api.delegation import run_delegation
from axiom_api.dependencies import (
    get_agent_backend_gateway,
    get_agent_fabric,
    get_approval_store,
    get_execution_store,
    get_memory_store,
    get_policy_engine,
)
from axiom_api.schemas import (
    AgentRecordDetailOut,
    AgentRecordOut,
    DelegateRequest,
    ExecutionOut,
    PendingApprovalOut,
)

router = APIRouter(prefix="/v1/agent-fabric", tags=["agent-fabric"])


def _require_gateway(gateway: AgentInvocationGateway | None) -> AgentInvocationGateway:
    if gateway is None:
        raise HTTPException(
            status_code=503,
            detail="Agent Fabric is not configured — set AXIOM_AGENCY_AGENTS_PATH.",
        )
    return gateway


def _to_out(record) -> AgentRecordOut:
    return AgentRecordOut(
        agent_id=record.agent_id,
        name=record.name,
        description=record.description,
        division=record.division,
        category=record.category,
        status=record.status.value,
        is_curated=record.is_curated,
        capabilities=list(record.capabilities) if record.capabilities else None,
        permissions=list(record.permissions) if record.permissions else None,
        risk_level=record.risk_level,
        frontmatter_tools=list(record.frontmatter_tools),
    )


@router.get("")
async def status(gateway: AgentInvocationGateway | None = Depends(get_agent_fabric)) -> dict:
    if gateway is None:
        return {"configured": False, "total_agents": 0, "curated_agents": 0}
    all_records = gateway.list()
    curated = [r for r in all_records if r.is_curated]
    by_division: dict[str, int] = {}
    for record in all_records:
        by_division[record.division] = by_division.get(record.division, 0) + 1
    return {
        "configured": True,
        "total_agents": len(all_records),
        "curated_agents": len(curated),
        "by_division": by_division,
    }


@router.get("/agents", response_model=list[AgentRecordOut])
async def list_agents(
    division: str | None = None,
    gateway: AgentInvocationGateway | None = Depends(get_agent_fabric),
) -> list[AgentRecordOut]:
    """The full real roster (all 254, not just the 12 curated) — unlike
    GET /v1/agent-fabric's aggregate by_division counts, this gives every
    agent a real, addressable agent_id. Built for Cortex Ledger AI World's 3D view
    (Milestone: Cortex Ledger AI World) to assign real identity to individual
    rendered points instead of anonymous dots, but generically useful
    anywhere a real roster (not just a search-scoped subset) is needed.
    """
    gateway = _require_gateway(gateway)
    return [_to_out(r) for r in gateway.list(division=division)]


@router.get("/search", response_model=list[AgentRecordOut])
async def search(
    q: str,
    division: str | None = None,
    limit: int = 10,
    gateway: AgentInvocationGateway | None = Depends(get_agent_fabric),
) -> list[AgentRecordOut]:
    gateway = _require_gateway(gateway)
    results = gateway.search(q, division=division, limit=limit)
    return [_to_out(r) for r in results]


@router.get("/agents/{agent_id:path}", response_model=AgentRecordDetailOut)
async def inspect(
    agent_id: str,
    gateway: AgentInvocationGateway | None = Depends(get_agent_fabric),
) -> AgentRecordDetailOut:
    gateway = _require_gateway(gateway)
    try:
        record = gateway.inspect(agent_id)
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return AgentRecordDetailOut(**_to_out(record).model_dump(), instructions=record.instructions,
                                 source_path=record.source_path, source_commit=record.source_commit)


@router.post("/agents/{agent_id:path}/delegate", response_model=ExecutionOut | PendingApprovalOut)
async def delegate(
    agent_id: str,
    body: DelegateRequest,
    gateway: AgentInvocationGateway | None = Depends(get_agent_fabric),
    backend_registry: AgentBackendRegistry = Depends(get_agent_backend_gateway),
    memory_store: MemoryStore | None = Depends(get_memory_store),
    execution_store=Depends(get_execution_store),
    policy: PolicyEngine = Depends(get_policy_engine),
    approvals: ApprovalStore | None = Depends(get_approval_store),
) -> ExecutionOut | PendingApprovalOut:
    gateway = _require_gateway(gateway)

    # Milestone 22: Agent Authorization — the real gap
    # docs/security/SECURITY_AUDIT.md §8 named: only tool *execution* was
    # policy-gated, not agent *invocation* itself. Same real gate tools
    # already go through, applied here too — CLAUDE.md's own curation
    # model tops out at "medium" for all 12 curated agents today (the
    # other 242 have no risk_level at all, treated as "medium" — see
    # PolicyEngine.evaluate's docstring), so this is a real, structural
    # control with no agent currently able to trip the REQUIRES_APPROVAL
    # branch — the same honest category as the delegate_to_agent depth
    # cap: forward-compatible, not exercised by today's data.
    try:
        record = gateway.inspect(agent_id)
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    decision = policy.evaluate(record.risk_level, action=f"agent:{agent_id}")
    if decision.status == PolicyStatus.REQUIRES_APPROVAL:
        if approvals is None:
            raise HTTPException(
                status_code=503,
                detail="This delegation requires approval but no approval store is configured "
                "(set AXIOM_DATABASE_URL).",
            )
        request = ApprovalRequest.new(
            action=f"agent:{agent_id}",
            risk_level=record.risk_level,
            reason=decision.reason,
            payload={
                "agent_id": agent_id,
                "task_input": body.input,
                "backend": body.backend or "axiom_native",
                "context": body.context,
            },
        )
        saved = await approvals.create(request)
        return PendingApprovalOut(approval_id=saved.id, status=saved.status.value, reason=saved.reason)

    try:
        execution = await run_delegation(
            gateway,
            backend_registry,
            memory_store,
            execution_store,
            agent_id=agent_id,
            task_input=body.input,
            backend_name=body.backend or "axiom_native",
            context=body.context,
        )
    except AgentBackendNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AgentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if execution.status.value == "failed":
        raise HTTPException(status_code=502, detail=execution.error)

    return ExecutionOut(
        execution_id=execution.execution_id,
        agent_id=execution.agent_id,
        backend_name=execution.backend_name,
        status=execution.status.value,
        content=execution.result.content if execution.result else None,
    )
