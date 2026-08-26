import httpx
import pytest


@pytest.mark.asyncio
async def test_list_knowledge_backends_reports_status_honestly(api_client: httpx.AsyncClient):
    response = await api_client.get("/v1/knowledge")

    assert response.status_code == 200
    backends = response.json()["backends"]
    if "graphify" in backends:
        assert backends["graphify"] in {"configured", "not_configured"}


@pytest.mark.asyncio
async def test_search_without_registered_backend_returns_503_not_a_fake_answer(
    api_client: httpx.AsyncClient,
):
    list_response = await api_client.get("/v1/knowledge")
    backends = list_response.json()["backends"]

    response = await api_client.get("/v1/knowledge/search", params={"question": "frontend developer"})

    if "graphify" not in backends:
        assert response.status_code == 503
        assert "graphify" in response.json()["detail"]
    else:
        # A real MCP server URL is configured in this environment — this
        # is the live integration path. Querying graph.json over MCP is
        # local/free (no LLM call), so unlike the Model Gateway this
        # should always succeed once configured, not just sometimes.
        assert response.status_code == 200
        text = response.json()["text"]
        assert text
        assert "nodes found" in text or "No " in text
