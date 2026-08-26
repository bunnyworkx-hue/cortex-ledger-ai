import uuid

import httpx
import pytest


@pytest.mark.asyncio
async def test_save_and_query_memory_via_api(api_client: httpx.AsyncClient):
    owner_id = f"test-owner-{uuid.uuid4()}"

    save_response = await api_client.post(
        "/v1/memory",
        json={
            "scope": "task",
            "owner_id": owner_id,
            "content": "API round trip test.",
            "source": "pytest",
        },
    )

    if save_response.status_code == 503:
        pytest.skip("Memory store not configured in this environment")

    assert save_response.status_code == 200
    saved = save_response.json()
    assert saved["owner_id"] == owner_id

    query_response = await api_client.get("/v1/memory", params={"owner_id": owner_id})
    assert query_response.status_code == 200
    results = query_response.json()
    assert len(results) == 1
    assert results[0]["content"] == "API round trip test."


@pytest.mark.asyncio
async def test_delegate_persists_a_task_memory_record(api_client: httpx.AsyncClient):
    fabric_status = (await api_client.get("/v1/agent-fabric")).json()
    health = (await api_client.get("/health")).json()
    if not fabric_status["configured"] or health["database"] != "ok":
        pytest.skip("Agent Fabric or database not configured in this environment")

    response = await api_client.post(
        "/v1/agent-fabric/agents/engineering/engineering-frontend-developer/delegate",
        json={"input": "Reply with exactly: memory-test-ack"},
    )
    if response.status_code != 200:
        pytest.skip("Live delegation did not succeed in this environment (e.g. no model credit)")

    execution_id = response.json()["execution_id"]

    query_response = await api_client.get(
        "/v1/memory", params={"owner_id": "engineering/engineering-frontend-developer"}
    )
    assert query_response.status_code == 200
    records = query_response.json()
    assert any(r["source"] == f"execution:{execution_id}" for r in records)
