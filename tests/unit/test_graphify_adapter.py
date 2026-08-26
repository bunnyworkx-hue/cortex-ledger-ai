from contextlib import asynccontextmanager

import pytest

import axiom_graphify.adapter as adapter_module
from axiom_graphify.adapter import GraphifyBackend


@pytest.fixture
def fake_call_tool(monkeypatch):
    calls: list[tuple[str, dict]] = []

    @asynccontextmanager
    async def fake_session(mcp_url: str):
        yield object()

    async def fake_call_tool(session, name: str, arguments: dict) -> dict:
        calls.append((name, arguments))
        return {"text": f"result for {name}"}

    monkeypatch.setattr(adapter_module, "graphify_session", fake_session)
    monkeypatch.setattr(adapter_module, "call_tool", fake_call_tool)
    return calls


@pytest.mark.asyncio
async def test_is_configured_reflects_url_presence():
    assert await GraphifyBackend("http://127.0.0.1:8080/mcp").is_configured() is True
    assert await GraphifyBackend("").is_configured() is False


@pytest.mark.asyncio
async def test_search_calls_query_graph(fake_call_tool):
    backend = GraphifyBackend("http://127.0.0.1:8080/mcp")

    answer = await backend.search("frontend developer", token_budget=500)

    assert fake_call_tool == [("query_graph", {"question": "frontend developer", "token_budget": 500})]
    assert answer.text == "result for query_graph"


@pytest.mark.asyncio
async def test_get_node_calls_get_node_with_label(fake_call_tool):
    backend = GraphifyBackend("http://127.0.0.1:8080/mcp")

    await backend.get_node("Frontend Developer")

    assert fake_call_tool == [("get_node", {"label": "Frontend Developer"})]


@pytest.mark.asyncio
async def test_get_neighbors_calls_get_neighbors_with_label(fake_call_tool):
    backend = GraphifyBackend("http://127.0.0.1:8080/mcp")

    await backend.get_neighbors("Frontend Developer")

    assert fake_call_tool == [("get_neighbors", {"label": "Frontend Developer"})]


@pytest.mark.asyncio
async def test_get_path_calls_shortest_path_with_source_and_target(fake_call_tool):
    backend = GraphifyBackend("http://127.0.0.1:8080/mcp")

    await backend.get_path("Frontend Developer", "Core Web Vitals")

    assert fake_call_tool == [
        ("shortest_path", {"source": "Frontend Developer", "target": "Core Web Vitals"})
    ]
