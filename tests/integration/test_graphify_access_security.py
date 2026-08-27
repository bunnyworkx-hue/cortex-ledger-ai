"""Milestone 20 (Security) — Graphify Access Tests, CLAUDE.md §96.

Graphify is Cortex Ledger AI's Knowledge Gateway backend (packages/axiom-graphify) —
a real, running MCP server over a knowledge graph built from the agent
library. Its own client adapter only exposes four read methods (search /
get_node / get_neighbors / get_path — see axiom_graphify/adapter.py), and
the generic MCP auto-discovery layer (packages/axiom-mcp/client.py)
independently confirms this at the transport level: every tool the live
server actually advertises is verified here to be read-only-shaped and
classified "low" risk, with no create/update/delete tool present at all.

This is real, live-server coverage, not a static assumption — it skips
cleanly if the Graphify MCP server isn't reachable in this environment
(see docs/graphify/GRAPHIFY_AUDIT.md for how to start it).
"""

import httpx
import pytest

_KNOWN_WRITE_VERBS = ("create_", "delete_", "update_", "write_", "remove_", "set_", "insert_", "drop_")


@pytest.mark.asyncio
async def test_every_graphify_tool_is_read_only_and_low_risk(api_client: httpx.AsyncClient):
    tools = (await api_client.get("/v1/tools")).json()
    graphify_tools = [t for t in tools if t["source"] == "mcp:graphify"]
    if not graphify_tools:
        pytest.skip("graphify MCP server not reachable in this environment")

    for tool in graphify_tools:
        assert tool["risk_level"] == "low", f"{tool['name']} was not classified low-risk"
        assert not tool["name"].startswith(_KNOWN_WRITE_VERBS), (
            f"{tool['name']} looks like a mutating tool but Graphify is expected to be read-only"
        )


@pytest.mark.asyncio
async def test_graph_stats_call_executes_immediately_without_approval(api_client: httpx.AsyncClient):
    tools = (await api_client.get("/v1/tools")).json()
    if not any(t["name"] == "graph_stats" for t in tools):
        pytest.skip("graphify MCP server not reachable in this environment")

    response = await api_client.post("/v1/tools/graph_stats/call", json={"arguments": {}})
    assert response.status_code == 200
    body = response.json()
    assert "approval_id" not in body
    assert "content" in body
