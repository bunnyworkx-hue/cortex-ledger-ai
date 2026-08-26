import httpx
import pytest


@pytest.mark.asyncio
async def test_list_tools_reflects_real_mcp_discovery(api_client: httpx.AsyncClient):
    response = await api_client.get("/v1/tools")

    assert response.status_code == 200
    tools = response.json()
    names = {t["name"] for t in tools}

    if not names:
        pytest.skip("No MCP server configured/reachable in this environment")

    # Graphify's real, verified tool set (docs/graphify/GRAPHIFY_AUDIT.md
    # §4) — this must include tools /v1/knowledge never exposed
    # (get_community, god_nodes, graph_stats, list_prs, get_pr_impact,
    # triage_prs), proving generic MCP discovery goes beyond the
    # hand-picked subset the Knowledge Gateway adapter cherry-picked.
    assert "graph_stats" in names
    assert "god_nodes" in names
    assert all(t["source"] == "mcp:graphify" for t in tools)


@pytest.mark.asyncio
async def test_call_graph_stats_returns_real_data(api_client: httpx.AsyncClient):
    tools = (await api_client.get("/v1/tools")).json()
    if not any(t["name"] == "graph_stats" for t in tools):
        pytest.skip("graphify MCP server not reachable in this environment")

    response = await api_client.post("/v1/tools/graph_stats/call", json={"arguments": {}})

    assert response.status_code == 200
    body = response.json()
    assert body["is_error"] is False
    text = body["content"].get("text", "")
    assert "Nodes:" in text or "nodes" in text.lower()


@pytest.mark.asyncio
async def test_call_unknown_tool_returns_404(api_client: httpx.AsyncClient):
    response = await api_client.post("/v1/tools/does-not-exist/call", json={"arguments": {}})
    assert response.status_code == 404
