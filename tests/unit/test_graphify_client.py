from dataclasses import dataclass, field
from typing import Any

import pytest

from axiom_graphify.client import GraphifyMcpError, call_tool


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
    def __init__(self, result: _FakeCallToolResult) -> None:
        self._result = result
        self.last_call: tuple[str, dict[str, Any]] | None = None

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> _FakeCallToolResult:
        self.last_call = (name, arguments)
        return self._result


@pytest.mark.asyncio
async def test_call_tool_prefers_structured_content():
    session = _FakeSession(_FakeCallToolResult(structured_content={"nodes": [], "edges": []}))

    result = await call_tool(session, "query_graph", {"question": "auth flow"})

    assert result == {"nodes": [], "edges": []}
    assert session.last_call == ("query_graph", {"question": "auth flow"})


@pytest.mark.asyncio
async def test_call_tool_falls_back_to_parsing_text_content_as_json():
    session = _FakeSession(
        _FakeCallToolResult(content=[_FakeTextBlock(text='{"node_id": "Foo"}')])
    )

    result = await call_tool(session, "get_node", {"node_id": "Foo"})

    assert result == {"node_id": "Foo"}


@pytest.mark.asyncio
async def test_call_tool_raises_on_error_result():
    session = _FakeSession(
        _FakeCallToolResult(content=[_FakeTextBlock(text="graph not found")], is_error=True)
    )

    with pytest.raises(GraphifyMcpError, match="graph not found"):
        await call_tool(session, "get_node", {"node_id": "missing"})
