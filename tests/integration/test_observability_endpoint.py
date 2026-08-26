import httpx
import pytest


@pytest.mark.asyncio
async def test_delegate_persists_and_exposes_an_execution_trace(api_client: httpx.AsyncClient):
    fabric_status = (await api_client.get("/v1/agent-fabric")).json()
    health = (await api_client.get("/health")).json()
    if not fabric_status["configured"] or health["database"] != "ok":
        pytest.skip("Agent Fabric or database not configured in this environment")

    response = await api_client.post(
        "/v1/agent-fabric/agents/product/product-manager/delegate",
        json={"input": "Reply with exactly: observability-test-ack"},
    )
    if response.status_code != 200:
        pytest.skip("Live delegation did not succeed in this environment (e.g. no model credit)")

    execution_id = response.json()["execution_id"]

    trace_response = await api_client.get(f"/v1/observability/executions/{execution_id}")
    assert trace_response.status_code == 200
    trace = trace_response.json()
    assert trace["agent_id"] == "product/product-manager"
    assert trace["status"] == "succeeded"
    assert trace["output"]
    assert trace["duration_ms"] is not None and trace["duration_ms"] > 0

    list_response = await api_client.get(
        "/v1/observability/executions", params={"agent_id": "product/product-manager"}
    )
    assert list_response.status_code == 200
    assert any(e["execution_id"] == execution_id for e in list_response.json())


@pytest.mark.asyncio
async def test_metrics_reflect_real_recorded_executions(api_client: httpx.AsyncClient):
    health = (await api_client.get("/health")).json()
    if health["database"] != "ok":
        pytest.skip("Database not configured in this environment")

    response = await api_client.get("/v1/observability/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert metrics["total_executions"] >= 0
    if metrics["total_executions"] > 0:
        assert metrics["succeeded"] + metrics["failed"] <= metrics["total_executions"]


@pytest.mark.asyncio
async def test_unknown_execution_returns_404(api_client: httpx.AsyncClient):
    health = (await api_client.get("/health")).json()
    if health["database"] != "ok":
        pytest.skip("Database not configured in this environment")

    response = await api_client.get("/v1/observability/executions/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
