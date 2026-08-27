# Graphify Integration

Portfolio summary — the full audit (real MCP tool schemas, live query
results, exact costs) is `docs/graphify/GRAPHIFY_AUDIT.md`.

## What Graphify is

[Graphify](https://github.com/Graphify-Labs/graphify) (Graphify Labs,
Apache 2.0, PyPI package `graphifyy`) turns a repository — code, docs,
PDFs, images, video — into a local **knowledge graph**, not a vector
index. Code is parsed with tree-sitter (deterministic AST parsing, fully
local, no LLM); an optional semantic pass over docs/media calls an LLM
backend if configured. Every edge is tagged `EXTRACTED` (read directly
from source) or `INFERRED` (resolved by Graphify's own logic) —
explainable relationships, not opaque embeddings.

## How Cortex Ledger AI talks to it

Cortex Ledger AI's Knowledge Gateway (`packages/axiom-graphify`) is a real MCP
client against a running `graphify-mcp --transport http` server — one
session per call, verified against a live server, not simulated.

```bash
uv tool install "graphifyy[mcp,anthropic]"
graphify extract <path> --backend claude --out var   # build the graph — costs real LLM credit
./scripts/dev/graphify-serve.sh                       # serve it over MCP on :8080
```

## Real finding: Graphify's tools return text, not structured JSON

`CallToolResult.structured_content` was `None` on every one of
`query_graph`/`get_node`/`get_neighbors`/`shortest_path`/`graph_stats` in
a live test — confirmed by direct inspection, not assumed. The text is
formatted for LLM context insertion (`NODE X [src=... community=N]` /
`EDGE A --relation [EXTRACTED]--> B`), which is right for feeding an
agent's context but meant Cortex Ledger AI's original, speculative
`KnowledgeNode`/`Subgraph`/`PathResult` design had to be corrected to a
single `KnowledgeAnswer(text, raw)` shape once this was verified live
(`axiom_core/knowledge/types.py`) — a real course-correction driven by
inspection, not planning in advance.

## Real result — a live extraction against agency-agents

```bash
graphify extract ~/agency-agents --backend claude --out var
```

**1,121 nodes, 1,594 edges, 138 communities**, real cost **$5.54**
(1,028,869 input / 163,435 output tokens). Verified live through
`/v1/knowledge/*`: `search?question=frontend+developer` returned a real
`INFERRED` cross-file semantic link (`Core Web Vitals Optimization
(Frontend)` → `semantically_similar_to` [INFERRED] → `Core Web Vitals
(LCP/INP/CLS)`, from two unrelated agent files) — exactly the
"explainable relationships across a large corpus" case Graphify exists
for.

## Access scope (see also SECURITY.md)

All 10 tools the live server advertises
(`query_graph`, `get_node`, `get_neighbors`, `get_community`,
`god_nodes`, `graph_stats`, `shortest_path`, `list_prs`, `get_pr_impact`,
`triage_prs`) are read-only by name — there is no write/mutate tool.
Cortex Ledger AI's own adapter (`axiom_graphify/adapter.py`) independently exposes
only 4 read methods. Verified live in
`tests/integration/test_graphify_access_security.py`.

## Known gap in the current graph

1/19 semantic chunks failed mid-extraction on a real Anthropic billing
state (insufficient credit at the time), leaving 17/323 source files with
no nodes. Not a Graphify or Cortex Ledger AI defect — re-running `graphify extract`
retries only the missing pieces (completed chunks are cached). Doesn't
block Knowledge Gateway functionality: querying the graph over MCP is
local and free, no LLM calls at query time.
