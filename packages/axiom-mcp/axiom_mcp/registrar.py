from axiom_core.tools import ToolCallResult, ToolRegistry

from axiom_mcp.client import call_mcp_tool, discover_mcp_tools, mcp_session


async def register_mcp_server(registry: ToolRegistry, server_name: str, mcp_url: str) -> int:
    """Consume a real MCP server generically (CLAUDE.md §33): discover
    its real tools and register each one in the Tool Registry, so any
    agent can find and call them — not just the hand-picked subset a
    specialized adapter (like axiom_graphify's KnowledgeBackend) exposes.
    Returns the number of tools registered.
    """
    async with mcp_session(mcp_url) as session:
        definitions = await discover_mcp_tools(session, server_name)

    for definition in definitions:

        async def handler(arguments: dict, *, _name: str = definition.name) -> ToolCallResult:
            async with mcp_session(mcp_url) as call_session:
                return await call_mcp_tool(call_session, _name, arguments)

        registry.register(definition, handler)

    return len(definitions)
