from contextlib import asynccontextmanager
from dataclasses import dataclass, field

import pytest

import axiom_mcp.registrar as registrar_module
from axiom_mcp.client import call_mcp_tool, discover_mcp_tools
from axiom_mcp.registrar import register_mcp_server
from axiom_core.tools import ToolRegistry


@dataclass
class _FakeTool:
    name: str
    description: str | None
    input_schema: dict


@dataclass
class _FakeListToolsResult:
    tools: list[_FakeTool]


@dataclass
class _FakeTextBlock:
    text: str
    type: str = "text"


@dataclass
class _FakeCallToolResult:
    content: list[_FakeTextBlock] = field(default_factory=list)
    structured_content: dict | None = None
    is_error: bool = False


class _FakeSession:
    def __init__(self, tools: list[_FakeTool], call_result: _FakeCallToolResult) -> None:
        self._tools = tools
        self._call_result = call_result
        self.last_call: tuple[str, dict] | None = None

    async def list_tools(self) -> _FakeListToolsResult:
        return _FakeListToolsResult(tools=self._tools)

    async def call_tool(self, name: str, arguments: dict) -> _FakeCallToolResult:
        self.last_call = (name, arguments)
        return self._call_result


@pytest.mark.asyncio
async def test_discover_mcp_tools_maps_real_schema_and_infers_risk():
    session = _FakeSession(
        tools=[
            _FakeTool(name="query_graph", description="Search the graph.", input_schema={"type": "object"}),
            _FakeTool(name="prs", description=None, input_schema={}),
        ],
        call_result=_FakeCallToolResult(),
    )

    definitions = await discover_mcp_tools(session, "graphify")

    assert len(definitions) == 2
    query = next(d for d in definitions if d.name == "query_graph")
    assert query.description == "Search the graph."
    assert query.source == "mcp:graphify"
    assert query.risk_level == "low"  # "query_" prefix

    prs = next(d for d in definitions if d.name == "prs")
    assert prs.description == ""  # None coerced to empty string
    assert prs.risk_level == "medium"  # no recognized read-only prefix


@pytest.mark.asyncio
async def test_call_mcp_tool_prefers_structured_content():
    session = _FakeSession(tools=[], call_result=_FakeCallToolResult(structured_content={"a": 1}))

    result = await call_mcp_tool(session, "some_tool", {"x": 1})

    assert result.content == {"a": 1}
    assert result.is_error is False
    assert session.last_call == ("some_tool", {"x": 1})


@pytest.mark.asyncio
async def test_call_mcp_tool_falls_back_to_text():
    session = _FakeSession(
        tools=[], call_result=_FakeCallToolResult(content=[_FakeTextBlock(text="plain text answer")])
    )

    result = await call_mcp_tool(session, "some_tool", {})

    assert result.content == {"text": "plain text answer"}


@pytest.mark.asyncio
async def test_register_mcp_server_registers_every_discovered_tool_and_routes_calls(monkeypatch):
    session = _FakeSession(
        tools=[
            _FakeTool(name="get_node", description="Get a node.", input_schema={"type": "object"}),
            _FakeTool(name="do_thing", description="Does a thing.", input_schema={"type": "object"}),
        ],
        call_result=_FakeCallToolResult(structured_content={"result": "ok"}),
    )

    @asynccontextmanager
    async def fake_mcp_session(mcp_url: str):
        yield session

    monkeypatch.setattr(registrar_module, "mcp_session", fake_mcp_session)

    registry = ToolRegistry()
    count = await register_mcp_server(registry, "graphify", "http://fake/mcp")

    assert count == 2
    names = {d.name for d in registry.list()}
    assert names == {"get_node", "do_thing"}
    assert registry.get("get_node").risk_level == "low"
    assert registry.get("do_thing").risk_level == "medium"

    # Each registered handler must call the *correct* tool name — a
    # classic late-binding closure bug would make every handler call the
    # last-registered tool instead.
    result_a = await registry.execute("get_node", {"label": "X"})
    assert session.last_call == ("get_node", {"label": "X"})
    assert result_a.content == {"result": "ok"}

    result_b = await registry.execute("do_thing", {"y": 2})
    assert session.last_call == ("do_thing", {"y": 2})
    assert result_b.content == {"result": "ok"}
