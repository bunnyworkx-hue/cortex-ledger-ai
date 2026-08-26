import httpx
import pytest


@pytest.mark.asyncio
async def test_list_agent_backends_reports_status_honestly(api_client: httpx.AsyncClient):
    response = await api_client.get("/v1/agents")

    assert response.status_code == 200
    backends = response.json()["backends"]
    if "axiom_native" in backends:
        assert backends["axiom_native"] in {"configured", "not_configured"}


@pytest.mark.asyncio
async def test_execute_without_registered_backend_returns_503_not_a_fake_answer(
    api_client: httpx.AsyncClient,
):
    list_response = await api_client.get("/v1/agents")
    backends = list_response.json()["backends"]

    response = await api_client.post(
        "/v1/agents/execute",
        json={
            "agent_id": "test-agent",
            "agent_name": "Test Agent",
            "instructions": "You are a test agent. Reply with exactly: pong",
            "input": "ping",
        },
    )

    if "axiom_native" not in backends:
        assert response.status_code == 503
        assert "axiom_native" in response.json()["detail"]
    else:
        # A real Model Gateway backend is configured — this is the live
        # Task -> Backend -> Execution -> Result path. It must be a
        # genuine result either way: a real completion (200), or a clean
        # 502 (e.g. the account is out of credit) — never an uncaught 500.
        assert response.status_code in {200, 502}
        if response.status_code == 200:
            body = response.json()
            assert body["status"] == "succeeded"
            assert body["backend_name"] == "axiom_native"
            assert body["content"]
        else:
            assert response.json()["detail"]
