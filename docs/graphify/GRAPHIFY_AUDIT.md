# Milestone 1 — Graphify Audit

Source: `https://github.com/Graphify-Labs/graphify` (cloned shallow for
inspection; not vendored into this repo). Company: Graphify Labs (YC S26).
License: **Apache License 2.0** (relicensed from MIT; original MIT text
retained in `LICENSE-MIT` for pre-relicense contributions — both are
permissive, no action needed to depend on it).

## 1. What it actually is

Graphify is a CLI + Python library (PyPI package name **`graphifyy`**, note
the double "y" — the plain `graphify` name was already taken) that turns a
repository (code, docs, PDFs, images, video) into a **local knowledge
graph**, not a vector index. Code is parsed with tree-sitter (deterministic
AST parsing, no LLM, fully local, ~40 languages); the semantic pass over
docs/media optionally calls an LLM backend if one is configured.

Every edge in the graph is tagged `EXTRACTED` (read directly from source)
or `INFERRED` (resolved by Graphify's own resolution logic) — this
directly satisfies `CLAUDE.md` §17's requirement for "explainable graph
relationships."

## 2. Installation

```bash
uv tool install graphifyy      # or: pipx install graphifyy
graphify install               # registers a skill/integration with your AI assistant
```

Entry points (from `pyproject.toml`):
- `graphify` → `graphify.__main__:main` (the CLI)
- `graphify-mcp` → `graphify.serve:_main` (the MCP server)

## 3. CLI surface (real commands, not inferred)

Core:
- `graphify extract <path>` — build/update the graph (`--code-only`,
  `--mode deep`, `--force`, `--google-workspace`)
- `graphify query "<question>"` — scoped subgraph for a plain-language
  question
- `graphify path A B` — shortest path between two concepts
- `graphify explain <node>` — connections, source location, community, degree
- `graphify cluster-only <path> [--no-viz]`
- `graphify merge-graphs a.json b.json`

Integration lifecycle (per-tool installers — this is how it plugs into an
AI assistant):
- `graphify install` / `graphify uninstall [--purge]`
- `graphify claude install` — writes CLAUDE.md integration + a Claude Code
  `PreToolUse` hook
- `graphify cursor install`, `graphify codex install`,
  `graphify opencode install`, `graphify kilo install`,
  `graphify codebuddy install`, and more (15+ platforms total per the
  README)

Other real subsystems: `graphify hook install` (git post-commit/checkout
auto-rebuild), `graphify prs` / `graphify prs --triage` /
`graphify prs --conflicts` (PR dashboard with graph-informed merge-risk
detection), `graphify export callflow-html` (Mermaid call-flow diagrams),
`graphify save-result` / `graphify reflect` (a working-memory / lessons
system that scores past Q&A as `useful | dead_end | corrected` and distills
`LESSONS.md`).

## 4. MCP support — real, not assumed

This directly answers `CLAUDE.md` §34 ("Claude Code must inspect and
validate... before relying on MCP"):

- `uv tool install "graphifyy[mcp]"` installs the MCP extra.
- Stdio transport (default): `python -m graphify.serve graphify-out/graph.json`
  or `kimi mcp add --transport stdio graphify -- python -m graphify.serve ...`
- HTTP transport (`--transport http --path /mcp`): one shared server for a
  whole team, at `http://<host>:8080/mcp`, instead of one local process per
  developer.
- Exposed MCP tools, **verified live** against a running server
  (`session.list_tools()`, Milestone 8): `query_graph`, `get_node`,
  `get_neighbors`, `get_community`, `god_nodes`, `graph_stats`,
  `shortest_path`, `list_prs`, `get_pr_impact`, `triage_prs` — three more
  than the README's summary list (`get_community`, `god_nodes`,
  `graph_stats`).
- **Every one of these tools returns human-readable text, not structured
  JSON.** `CallToolResult.structured_content` was `None` on all of
  `query_graph`/`get_node`/`get_neighbors`/`shortest_path`/`graph_stats`
  in a live test against the agency-agents graph — confirmed by direct
  inspection, not assumed. The text is formatted for LLM context
  insertion (e.g. `query_graph` returns lines like
  `NODE X [src=... community=N]` / `EDGE A --relation [EXTRACTED]--> B`),
  which is exactly right for CLAUDE.md §108's "knowledge → reasoning"
  flow, but it means **`axiom_core.knowledge` cannot expose a structured
  Node/Edge graph API** without writing a bespoke parser for this text
  format. Milestone 8 corrected the original (speculative)
  `KnowledgeNode`/`Subgraph`/`PathResult` types to a single
  `KnowledgeAnswer(text, raw)` shape once this was verified — see
  `axiom_core/knowledge/types.py`. `CLAUDE.md` §19's `get_dependencies`/
  `get_dependents`/`get_architecture`/`get_documentation` still have no
  direct 1:1 tool and remain unimplemented; `get_impact` maps to
  `get_pr_impact` for the PR-scoped case only.

## 5. Config surface worth knowing before wiring the adapter

- `GRAPHIFY_MAX_CONTEXTS` — max number of non-default project graphs one
  multi-project MCP server retains (default 8). Relevant if Axiom points
  many agents/tenants at one shared Graphify MCP server.
- Query logging: every `query`/`path`/`explain`/`query_graph` call is
  logged to `~/.cache/graphify-queries.log` (JSONL: timestamp, question,
  corpus, node count, duration — **not** full subgraph payloads by
  default). This is a ready-made source for the "knowledge query" traces
  `CLAUDE.md` §40 asks Axiom to track — Axiom's Knowledge Gateway should
  tap or mirror this rather than re-implement query logging from scratch.
  Can be disabled (`GRAPHIFY_QUERY_LOG_DISABLE=1`) or redirected.

## 6. Output artifacts

A `graphify extract` run produces `graphify-out/`:
- `graph.html` — interactive force-directed graph, browsable standalone
- `GRAPH_REPORT.md` — key concepts, notable connections, suggested questions
- `graph.json` — the full graph, queryable offline without re-reading files

`graph.json` is the artifact the Axiom Graphify Adapter (`CLAUDE.md` §20,
`packages/axiom-graphify/`) should treat as the canonical knowledge
snapshot when not going through the MCP server directly.

## 7. Freshness / staleness

Graphify has real git-hook-driven incremental rebuild
(`graphify hook install`), which maps directly onto `CLAUDE.md` §70–72's
knowledge lifecycle (`INDEXED` / `STALE` / `UPDATING`) — Axiom can drive
staleness detection off the same git-commit signal Graphify's own hook
uses, rather than inventing a separate mechanism.

## 8. What was not verified (as of the original audit)

The original pass (Milestone 1) read the README, `pyproject.toml`, license
files, and top-level module list. It did **not** install the tool, run
`graphify extract` against a real repo, or start the MCP server. That gap
is closed — see §9.

## 9. Milestone 8 — live run against agency-agents

Ran for real, not simulated:

```bash
uv tool install "graphifyy[mcp,anthropic]"   # first attempt used [mcp] only;
                                              # --backend claude needs the
                                              # anthropic extra too — real
                                              # error hit and fixed, not
                                              # anticipated in advance
graphify extract ~/Desktop/agency-agents --backend claude --out ~/Desktop/axiom-os/var
graphify-mcp var/graphify-out/graph.json --transport http --host 127.0.0.1 --port 8080
```

Result: **1,121 nodes, 1,594 edges, 138 communities**, real cost
**$5.54** (1,028,869 input / 163,435 output tokens, Claude). Verified live
via `axiom-api`'s `/v1/knowledge/*` endpoints (`GET /v1/knowledge/search`,
`/node`, `/neighbors`, `/path`), each proxying through a real MCP session
to the running server — e.g. `search?question=frontend+developer`
returned real `EXTRACTED` and `INFERRED` edges, including a genuine
cross-file semantic link (`Core Web Vitals Optimization (Frontend)`
[engineering-frontend-developer.md] `--semantically_similar_to
[INFERRED]-->` `Core Web Vitals (LCP/INP/CLS)`
[engineering-drupal-performance.md]) — exactly the "explainable
relationships across a large corpus" case Graphify is for.

**Known gaps in this specific graph, both retryable once resolved:**
- 1/19 semantic chunks failed mid-run: `Your credit balance is too low to
  access the Anthropic API`. This is an account billing state, not a
  Graphify or Axiom defect — 17/323 files consequently produced no nodes.
  Re-running `graphify extract` once credit is available will retry only
  the missing pieces (Graphify caches completed chunks).
- Community labels are still placeholder `Community N` — `graphify
  cluster-only` (or `graphify label`) needs a further, smaller LLM pass
  (blocked on the same credit issue) to name them.

Neither gap blocks Knowledge Gateway functionality: querying `graph.json`
over MCP is local and free — no LLM calls are made by `query_graph`,
`get_node`, `get_neighbors`, or `shortest_path` at query time.
