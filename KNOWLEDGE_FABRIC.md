# Knowledge Fabric

The Knowledge Gateway is the provider-neutral abstraction Cortex Ledger AI's API
routes through to reach a knowledge backend — today that's Graphify (see
`GRAPHIFY_INTEGRATION.md` for the specific backend). This document is
about the abstraction itself: `axiom_core.knowledge`.

## The shape

```python
class KnowledgeBackend(Protocol):
    backend_name: str
    async def is_configured(self) -> bool: ...
    async def search(self, question: str, *, token_budget: int | None = None) -> KnowledgeAnswer: ...
    async def get_node(self, label: str) -> KnowledgeAnswer: ...
    async def get_neighbors(self, label: str) -> KnowledgeAnswer: ...
    async def get_path(self, source: str, target: str) -> KnowledgeAnswer: ...
```

`packages/axiom-core` defines this Protocol with zero concrete SDK
dependency; `packages/axiom-graphify` is the one real implementation
today, wired up in `apps/api/axiom_api/main.py`'s startup lifespan and
looked up by name through `KnowledgeGatewayRegistry` — the same
register-by-name pattern the Model Gateway and Agent Backend registries
use, so adding a second knowledge backend later doesn't touch any router.

## `KnowledgeAnswer` — a real design correction, not an upfront plan

```python
@dataclass(frozen=True, slots=True)
class KnowledgeAnswer:
    text: str
    raw: dict
```

The original design (before any live testing) proposed structured
`KnowledgeNode`/`Subgraph`/`PathResult` types — a typed graph API. Once
Graphify's real MCP server was queried live, `CallToolResult.structured_content`
came back `None` on every query-shaped tool; the actual payload is
human-readable text formatted for LLM context insertion (`NODE X
[src=... community=N]` / `EDGE A --relation [EXTRACTED]--> B`). Cortex Ledger AI's
type was corrected to match the real API rather than force a structured
shape the backend doesn't provide — `text` is what belongs in an agent's
prompt context, `raw` keeps the underlying MCP payload for anything that
needs it.

## Exposed via the API

```
GET /v1/knowledge            backend status (configured / not_configured)
GET /v1/knowledge/search     ?question=...&token_budget=...
GET /v1/knowledge/node       ?label=...
GET /v1/knowledge/neighbors  ?label=...
GET /v1/knowledge/path       ?source=...&target=...
```

Every route proxies straight to the registered backend and returns
`{"text": "..."}` — thin routing, no business logic in the router layer
(`apps/api/axiom_api/routers/knowledge.py`).

## What's not implemented

CLAUDE.md §19 names `get_dependencies`/`get_dependents`/`get_architecture`/
`get_documentation` as knowledge operations — none have a direct 1:1
Graphify MCP tool today; `get_impact` maps onto Graphify's `get_pr_impact`
only for the PR-scoped case. Correlating the knowledge graph with Cortex Ledger AI's
own execution trace (CLAUDE.md §43's "knowledge → reasoning → execution →
verification") is a stated future direction, not built — see
`ARCHITECTURE.md`'s "What's deliberately not built" section.
