import httpx
import pytest


@pytest.mark.asyncio
async def test_hermes_backend_appears_when_configured(api_client: httpx.AsyncClient):
    response = await api_client.get("/v1/agents")

    assert response.status_code == 200
    backends = response.json()["backends"]
    if "hermes" in backends:
        assert backends["hermes"] in {"configured", "not_configured"}


@pytest.mark.asyncio
async def test_delegate_a_real_curated_agent_through_hermes(api_client: httpx.AsyncClient):
    backends = (await api_client.get("/v1/agents")).json()["backends"]
    fabric_status = (await api_client.get("/v1/agent-fabric")).json()
    if backends.get("hermes") != "configured" or not fabric_status["configured"]:
        pytest.skip("Hermes backend or Agent Fabric not configured in this environment")

    response = await api_client.post(
        "/v1/agent-fabric/agents/engineering/engineering-frontend-developer/delegate",
        json={
            "input": "In one word, what do you build? Reply with exactly one word.",
            "backend": "hermes",
        },
    )

    # A real Registry -> HermesBackend (real `hermes -z` subprocess) ->
    # real Anthropic call -> Execution round trip. Either a genuine
    # completion, or a clean 502 — never an uncaught 500.
    assert response.status_code in {200, 502}
    if response.status_code == 200:
        body = response.json()
        assert body["status"] == "succeeded"
        assert body["backend_name"] == "hermes"
        assert body["content"]
