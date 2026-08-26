import json
from contextlib import asynccontextmanager

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from axiom_core.tools import ToolCallResult, ToolDefinition

_READ_ONLY_PREFIXES = ("get_", "list_", "query_", "search_", "graph_", "god_", "triage_")


@asynccontextmanager
async def mcp_session(mcp_url: str):
    """Open one MCP session against a running server (HTTP transport).
    One session per call is simple and correct — verified against a real
    server in Milestone 8 (Graphify); this is the generic version any
    MCP server can use.
    """
    async with streamable_http_client(mcp_url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            yield session


def _infer_risk_level(tool_name: str) -> str:
    """A heuristic, not a real risk assessment — CLAUDE.md §36's actual
    risk levels come from human curation (Milestone 15's Policy Engine),
    the same way AgentRecord.risk_level works for curated agents. A
    read-only-looking tool name defaults to "low"; anything else defaults
    to "medium" as the conservative choice for an unrecognized,
    auto-discovered tool.
    """
    return "low" if tool_name.startswith(_READ_ONLY_PREFIXES) else "medium"


async def discover_mcp_tools(session: ClientSession, server_name: str) -> list[ToolDefinition]:
    result = await session.list_tools()
    return [
        ToolDefinition(
            name=tool.name,
            description=tool.description or "",
            input_schema=tool.input_schema or {},
            source=f"mcp:{server_name}",
            risk_level=_infer_risk_level(tool.name),
        )
        for tool in result.tools
    ]


async def call_mcp_tool(session: ClientSession, name: str, arguments: dict) -> ToolCallResult:
    """Call an MCP tool and return its result. Prefers `structured_content`
    when the server provides it; falls back to parsing the first text
    block as JSON, or wrapping raw text — verified against a real server
    in Milestone 8, where most Graphify tools return text, not structured
    JSON.
    """
    result = await session.call_tool(name, arguments)

    if result.structured_content is not None:
        return ToolCallResult(content=dict(result.structured_content), is_error=result.is_error)

    for block in result.content:
        if getattr(block, "type", None) == "text":
            try:
                return ToolCallResult(content=json.loads(block.text), is_error=result.is_error)
            except json.JSONDecodeError:
                return ToolCallResult(content={"text": block.text}, is_error=result.is_error)

    return ToolCallResult(content={}, is_error=result.is_error)
