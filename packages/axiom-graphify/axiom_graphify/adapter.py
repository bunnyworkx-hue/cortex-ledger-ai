from axiom_core.knowledge.types import KnowledgeAnswer

from axiom_graphify.client import call_tool, graphify_session


class GraphifyBackend:
    """Knowledge Gateway adapter for Graphify. Talks to a real, running
    Graphify MCP server (started with ``graphify-mcp --transport http``)
    — see docs/graphify/GRAPHIFY_AUDIT.md for the verified tool schemas
    this maps onto.

    Every call opens its own MCP session (see graphify_session) rather
    than holding a long-lived connection — simple and correct for
    Milestone 8's scope; connection pooling is a later optimization, not
    a correctness requirement.
    """

    backend_name = "graphify"

    def __init__(self, mcp_url: str) -> None:
        self._mcp_url = mcp_url

    async def is_configured(self) -> bool:
        # Local-only check — a URL is set. Does not probe the server
        # (that's a network call); see KnowledgeBackend docstring.
        return bool(self._mcp_url)

    async def search(self, question: str, *, token_budget: int | None = None) -> KnowledgeAnswer:
        arguments = {"question": question}
        if token_budget is not None:
            arguments["token_budget"] = token_budget
        return await self._call("query_graph", arguments)

    async def get_node(self, label: str) -> KnowledgeAnswer:
        return await self._call("get_node", {"label": label})

    async def get_neighbors(self, label: str) -> KnowledgeAnswer:
        return await self._call("get_neighbors", {"label": label})

    async def get_path(self, source: str, target: str) -> KnowledgeAnswer:
        return await self._call("shortest_path", {"source": source, "target": target})

    async def _call(self, tool_name: str, arguments: dict) -> KnowledgeAnswer:
        async with graphify_session(self._mcp_url) as session:
            raw = await call_tool(session, tool_name, arguments)
        # Graphify's tools return plain text, not structured JSON
        # (verified live — see axiom_core.knowledge.types.KnowledgeAnswer
        # docstring) — call_tool's fallback wraps that text as {"text": ...}.
        text = raw.get("text") if isinstance(raw, dict) else None
        return KnowledgeAnswer(text=text or "", raw=raw)
