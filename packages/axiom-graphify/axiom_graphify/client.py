import json
from contextlib import asynccontextmanager
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


class GraphifyMcpError(RuntimeError):
    """Raised when a Graphify MCP tool call fails or returns no usable content."""


@asynccontextmanager
async def graphify_session(mcp_url: str):
    """Open one MCP session against a running Graphify HTTP server
    (started with ``graphify-mcp --transport http``). One session per
    call is simple and correct for Milestone 8's scope; pooling/reuse is
    a later optimization, not a correctness requirement.
    """
    async with streamable_http_client(mcp_url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            yield session


async def call_tool(session: ClientSession, name: str, arguments: dict[str, Any]) -> dict:
    """Call an MCP tool and return its result as a plain dict.

    Prefers ``structured_content`` (the MCP result field that carries a
    real JSON object, confirmed present on this SDK's CallToolResult —
    see docs/graphify/GRAPHIFY_AUDIT.md), and falls back to parsing the
    first text content block as JSON for tools that only return text.
    """
    result = await session.call_tool(name, arguments)

    if result.is_error:
        detail = "; ".join(
            block.text for block in result.content if getattr(block, "type", None) == "text"
        )
        raise GraphifyMcpError(f"Graphify tool {name!r} failed: {detail or 'unknown error'}")

    if result.structured_content is not None:
        return dict(result.structured_content)

    for block in result.content:
        if getattr(block, "type", None) == "text":
            try:
                return json.loads(block.text)
            except json.JSONDecodeError:
                return {"text": block.text}

    raise GraphifyMcpError(f"Graphify tool {name!r} returned no usable content")
