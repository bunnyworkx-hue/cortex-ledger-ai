import uuid

import httpx
import pytest


@pytest.mark.asyncio
async def test_high_risk_tool_requires_approval_and_is_not_executed_immediately(
    api_client: httpx.AsyncClient,
):
    record_id = f"test-record-{uuid.uuid4()}"

    response = await api_client.post(
        "/v1/tools/modify_business_record/call",
        json={"arguments": {"record_id": record_id, "fields": {"status": "active"}}},
    )

    assert response.status_code == 200
    body = response.json()
    # A high-risk native tool must never execute inline — it must come
    # back as a pending approval, not a ToolCallResult.
    assert "approval_id" in body
    assert body["status"] == "pending"


@pytest.mark.asyncio
async def test_full_propose_approve_execute_audit_loop(api_client: httpx.AsyncClient):
    record_id = f"test-record-{uuid.uuid4()}"

    propose = await api_client.post(
        "/v1/tools/modify_business_record/call",
        json={"arguments": {"record_id": record_id, "fields": {"status": "active"}}},
    )
    approval_id = propose.json()["approval_id"]

    # Not executed yet — the demo mutating tool must not have run.
    pending = await api_client.get(f"/v1/approvals/{approval_id}")
    assert pending.status_code == 200
    assert pending.json()["status"] == "pending"

    # A human (simulated here) approves it.
    approve = await api_client.post(
        f"/v1/approvals/{approval_id}/approve", json={"decided_by": "test-human"}
    )
    assert approve.status_code == 200
    result = approve.json()
    assert result["content"]["record_id"] == record_id
    assert result["content"]["record"]["status"] == "active"

    decided = await api_client.get(f"/v1/approvals/{approval_id}")
    assert decided.json()["status"] == "approved"
    assert decided.json()["decided_by"] == "test-human"

    # Approving twice must not re-execute (409, not a silent no-op).
    reapprove = await api_client.post(
        f"/v1/approvals/{approval_id}/approve", json={"decided_by": "test-human"}
    )
    assert reapprove.status_code == 409


@pytest.mark.asyncio
async def test_rejecting_an_approval_never_executes_the_action(api_client: httpx.AsyncClient):
    record_id = f"test-record-{uuid.uuid4()}"

    propose = await api_client.post(
        "/v1/tools/modify_business_record/call",
        json={"arguments": {"record_id": record_id, "fields": {"status": "should-not-apply"}}},
    )
    approval_id = propose.json()["approval_id"]

    reject = await api_client.post(f"/v1/approvals/{approval_id}/reject", json={"decided_by": "test-human"})
    assert reject.status_code == 200
    assert reject.json()["status"] == "rejected"

    # Approving after rejection must fail, not execute retroactively.
    approve = await api_client.post(
        f"/v1/approvals/{approval_id}/approve", json={"decided_by": "test-human"}
    )
    assert approve.status_code == 409


@pytest.mark.asyncio
async def test_low_risk_tool_executes_immediately_without_approval(api_client: httpx.AsyncClient):
    tools = (await api_client.get("/v1/tools")).json()
    if not any(t["name"] == "graph_stats" for t in tools):
        pytest.skip("graphify MCP server not reachable in this environment")

    response = await api_client.post("/v1/tools/graph_stats/call", json={"arguments": {}})

    assert response.status_code == 200
    body = response.json()
    assert "content" in body and "approval_id" not in body
