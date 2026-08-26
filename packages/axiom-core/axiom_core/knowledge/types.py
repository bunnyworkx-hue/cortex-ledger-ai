from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class KnowledgeAnswer:
    """A text-context answer from a knowledge backend.

    Graphify's MCP tools (query_graph, get_node, get_neighbors,
    shortest_path, ...) all return human-readable text formatted for LLM
    consumption, not structured JSON — verified live against a running
    server (see docs/graphify/GRAPHIFY_AUDIT.md §4, updated post-verification).
    This type reflects that reality: `text` is the payload meant to be
    inserted directly into an agent's prompt context, matching the
    knowledge -> reasoning -> execution flow in CLAUDE.md §108, rather
    than a structured graph model the real API doesn't provide.
    """

    text: str
    raw: dict = field(default_factory=dict)
