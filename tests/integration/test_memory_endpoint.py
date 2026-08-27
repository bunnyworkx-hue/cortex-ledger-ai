import uuid

import httpx
import pytest

from axiom_api.main import app


@pytest.mark.asyncio
async def test_save_and_query_memory_via_api(api_client: httpx.AsyncClient):
    # Milestone 22: owner_id is derived from the API key, not supplied —
    # a unique piece of content is the correlation key instead of a
    # unique owner_id, since every call here authenticates as the same
    # configured caller.
    content = f"API round trip test {uuid.uuid4()}."
    headers = {"Authorization": "Bearer dev-key-alice"}

    save_response = await api_client.post(
        "/v1/memory",
        json={"scope": "task", "content": content, "source": "pytest"},
        headers=headers,
    )

    if save_response.status_code == 503:
        pytest.skip("Memory store not configured in this environment")
    if save_response.status_code == 401:
        pytest.skip("AXIOM_API_KEYS not configured with dev-key-alice in this environment")

    assert save_response.status_code == 200
    saved = save_response.json()
    assert saved["owner_id"] == "alice"

    query_response = await api_client.get("/v1/memory", headers=headers)
    assert query_response.status_code == 200
    results = query_response.json()
    assert content in [r["content"] for r in results]


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

    # Milestone 22: GET /v1/memory no longer accepts an arbitrary
    # owner_id filter (that was the isolation gap — see
    # test_memory_isolation_security.py), so a public API caller can no
    # longer query another owner's (here, the agent's) task memory this
    # way. That's the fix working, not a regression. Verify the write
    # actually happened the way an internal/admin tool would: read the
    # real store directly, not through the now-owner-scoped public
    # endpoint.
    memory_store = app.state.memory_store
    records = await memory_store.query(owner_id="engineering/engineering-frontend-developer", limit=50)
    assert any(r.source == f"execution:{execution_id}" for r in records)
