# Milestone 4 — Proposed Architecture

This is the architecture proposal `CLAUDE.md` §80/§105 (Step 7) requires
before any implementation code is written. It supersedes the doc's
*speculative* interfaces with the *real* ones found during the audits, and
is meant to be reviewed before Milestone 6 (Foundation) starts.

## 1. How the three pillars map onto real systems

```
                         AXIOM OS (this repo)
                            │
       ┌────────────────────┼────────────────────┐
       ▼                    ▼                    ▼
 AGENT FABRIC          KNOWLEDGE FABRIC      EXECUTION ENGINE
       │                    │                    │
 agency-agents          Graphify              Claude (Anthropic)
 (255 agents,           (Apache-2.0,          Hermes Agent
  MIT, github.com/       github.com/           (MIT, github.com/
  msitarzewski/          Graphify-Labs/        NousResearch/
  agency-agents)         graphify)             hermes-agent)
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                           ORVYN
              (ORVYN-V3 already exists — retrofit
               later, per CLAUDE.md's own sequencing)
```

Every box in this diagram is now a real, inspected system with a real
license and a real API surface, not a placeholder — see the three audit
docs next to this one.

## 2. Agent Fabric — concrete design

**Registry.** `packages/axiom-agent-fabric/registry/` reads `agency-agents`
(pinned to a specific commit, updated deliberately) and produces normalized
records under `agents/registry/`. Since source frontmatter has no
capability/tool/permission fields (confirmed in
`AGENT_LIBRARY_AUDIT.md` §2), normalization is two-phase:

1. **Mechanical**: `agent_id`, `name`, `description`, `category` (from
   `divisions.json`), `instructions` (the prose body), `version` (source
   commit hash) — a straight, lossless transform.
2. **Curated**: `capabilities`, `tools`, `permissions`, `risk_level`,
   `budget` — start these as `status: DRAFT` (per the lifecycle in
   `CLAUDE.md` §69) and populated by hand for a small first cohort (10–20
   agents spanning a few divisions), not auto-inferred from prose for all
   255 on day one. Auto-inference from the description field is a
   reasonable v2, not a v1 requirement — don't let it block the MVP.

**Discovery/Router v1** (`CLAUDE.md` §10 explicitly says "do not jump
directly to Version 4"): explicit routing over the curated cohort only.
Capability-based search comes once enough agents have real capability tags
to search over.

**Invocation Gateway.** Adapt the `agency-agents-router` plugin's four-verb
shape (`search` / `inspect` / `load` / `delegate`, confirmed real in
`AGENT_LIBRARY_AUDIT.md` §5) as the Gateway's own operation set, rather
than inventing new verb names — it's a working reference implementation of
the exact lazy-discovery workflow `CLAUDE.md` §9 wants.

## 3. Knowledge Fabric — concrete design

`packages/axiom-graphify/adapter/` talks to Graphify over its real MCP
server (`graphify-mcp` entry point / `python -m graphify.serve`), using
HTTP transport (`--transport http`) so one Graphify server can back
multiple agents/tenants rather than spawning a process per session.

Knowledge Gateway operations map onto Graphify's **real** MCP tools,
verified live in Milestone 8 (`GRAPHIFY_AUDIT.md` §4/§9) against a real
graph built from `agency-agents` (1,121 nodes, 1,594 edges):

| Axiom Knowledge Gateway op | Backed by |
|---|---|
| `search` | `query_graph` |
| `get_node` | `get_node` |
| `get_neighbors` | `get_neighbors` |
| `get_path` | `shortest_path` |
| `get_impact` | `get_pr_impact` (PR-scoped only — no general-impact tool exists) |

**Correction from the original (pre-verification) plan:** every one of
these tools returns human-readable text, not structured JSON
(`CallToolResult.structured_content` is `None` on all of them — confirmed
live). `axiom_core.knowledge`'s original `KnowledgeNode`/`Subgraph`/
`PathResult` design assumed a structured graph API that doesn't actually
exist over MCP; it was corrected to a single `KnowledgeAnswer(text, raw)`
shape once this was verified. Callers get LLM-ready context text, not a
graph object to walk in Python — which is the right shape for CLAUDE.md
§108's knowledge→reasoning flow anyway.

`get_dependencies`/`get_dependents`/`get_architecture`/`get_documentation`
from the original speculative list have no direct 1:1 MCP tool and remain
unimplemented — not stubbed as fake pass-throughs.

Freshness tracking (`CLAUDE.md` §70–72) rides on Graphify's own
`graphify hook install` git-commit-triggered rebuild rather than a
separate staleness mechanism.

## 4. Execution Engine — concrete design

**Model Gateway** (`packages/axiom-anthropic/`): thin, provider-neutral
wrapper around the Anthropic API. Single-provider for the MVP per
`CLAUDE.md` §83 — no OpenAI/Gemini gateway work until something actually
needs it.

**Agent Gateway → Hermes** (`packages/axiom-hermes/`): calls Hermes's real
`delegate_task` mechanism (confirmed in `HERMES_INTEGRATION.md` §4) rather
than reimplementing subagent orchestration. Tool exposure to a Hermes
session is scoped using Hermes's own `toolsets.py` composition model
(§5 of that audit) — Axiom grants a named toolset, not a raw tool list.
Sandboxing (`CLAUDE.md` §47) uses Hermes's existing Docker/Singularity/
Modal/Daytona terminal backends rather than Axiom building its own
container isolation layer.

**Backend interface**: `AxiomNativeBackend` (Claude direct) and
`HermesBackend` both implement the same `execute()`/`capabilities()`/
`health()` shape from `CLAUDE.md` §30 — this is the seam that lets the
first two demos (knowledge-grounded research on native Claude, then the
same task routed through Hermes) share one execution path.

## 5. What the MVP actually proves (Demo 1, concretely)

Per `CLAUDE.md` §59, adjusted to real tool calls:

```
User: "Research this repository and explain how authentication works."
  → Axiom creates an execution record
  → Task classified (research/knowledge)
  → Knowledge Gateway: query_graph("authentication") against a Graphify
    server already running over the target repo
  → Agent Discovery: search the curated agent cohort for a matching
    specialist (e.g. a security/backend-review agent)
  → Backend selected: AxiomNativeBackend (Claude)
  → Permission check passes (read-only knowledge + model call, LOW risk)
  → Execute: Claude answers, grounded in the Graphify subgraph
  → Execution trace written (query, agent, backend, tokens, cost, result)
  → Result returned
```

This is achievable without Hermes at all — Demo 2 (the Hermes round trip)
is a deliberately separate milestone so the MVP doesn't block on two
external integrations landing simultaneously.

## 6. Sequencing (Milestones 6–20, unchanged from CLAUDE.md, now with real targets)

1. **Foundation** — config, logging, a **new, independent Supabase
   project** (decided §7 — not shared with ORVYN-V3), test harness.
2. **Model Gateway** — Anthropic only.
3. **Knowledge Gateway** — Graphify adapter over its real MCP server,
   installed and exercised against a real target repo (recommend using
   `agency-agents` itself as the first indexed repo — it's real, sizeable,
   and already on disk).
4. **Agent Runtime** — Agent/Task/Execution/Result primitives.
5. **Agent Fabric** — registry + curated first cohort + explicit-routing
   discovery + gateway adapted from `agency-agents-router`.
6. **Tool Registry / MCP client** — done. `axiom-mcp` consumes any MCP
   server generically (not hand-coded per-tool like axiom-graphify's
   Knowledge Gateway adapter): live-verified by auto-discovering all 10
   real Graphify MCP tools via `/v1/tools`, including `get_community`,
   `god_nodes`, `graph_stats`, `list_prs`, `get_pr_impact`, `triage_prs`
   — six tools the Knowledge Gateway never exposed. `ToolRegistry.execute()`
   has a permission-check hook (used when a caller supplies
   `granted_permissions`) and audit-logs every call (tool, risk_level,
   permission_check outcome, duration_ms) — real today; full Policy
   Engine enforcement is still Milestone 15.
7. **Hermes Integration** — done. Installed for real (hit and fixed a
   genuine installer hang — see `docs/hermes/HERMES_INTEGRATION.md` §10)
   and wired as a second `AgentBackend` (`packages/axiom-hermes/`),
   alongside `AxiomNativeBackend`, both selectable per-call via
   `/v1/agent-fabric/agents/{id}/delegate`'s `backend` field. Uses
   Hermes's real `-z`/`--oneshot` mode over a subprocess — one full
   Hermes run per Axiom `Execution`, not Hermes's own internal
   `delegate_task`/subagent spawning (which is Hermes deciding to
   delegate internally, a different thing from Axiom calling Hermes).
   Live-verified: a real in-character completion from the SEO Specialist
   agent, routed Registry → `HermesBackend` → real `hermes` subprocess →
   real Anthropic call → `Execution`.
8. **Memory** — done. `memories` table (Postgres), the Alembic scaffold's
   first real migration. Real findings along the way: autogenerate's raw
   output would have **dropped the pre-existing shared-core tables**
   (`organizations`/`profiles`/`subscriptions`/`org_product_access`) since
   they're not declared in Axiom's own models — hand-edited the migration
   to touch only `memories` before ever running it. Supabase's own
   advisor flagged RLS as disabled on the new table; not auto-fixed
   (enabling RLS with no policies would lock out all access) — surfaced
   to the user instead. Also found and fixed a real pytest-asyncio bug:
   `axiom_db.engine`'s cached async connection pool binds to whichever
   event loop first created it, which broke the moment a second
   DB-touching test ran in the same session under pytest-asyncio's
   default per-function loop scope — fixed by giving the test session one
   shared loop (`asyncio_default_fixture_loop_scope` /
   `asyncio_default_test_loop_scope = "session"`), matching how the real
   app (one uvicorn loop for its whole life) actually behaves. Every
   successful `/v1/agent-fabric/.../delegate` call now auto-persists a
   `task`-scoped memory record.
9. **Policy + Human Approval** — done, built together since CLAUDE.md's
   own workflow (§37) couples them: Agent → Proposed Action → Policy
   Engine → HIGH RISK → Approval Required → Human Approves → Execute →
   Verify → Audit. `PolicyEngine` v1 is a single risk threshold
   (low/medium auto-allow, high/critical → `requires_approval`) — per
   CLAUDE.md §10's "don't jump to Version 4," not budgets/rate-limits/
   denial yet, which need a real reason to build (an actually-exhausted
   budget) rather than an invented one. A real `modify_business_record`
   native tool (CLAUDE.md §64's own example) is the first — and
   currently only — real high-risk action in the system; every other
   registered tool (Graphify's 10, all read/query) is low/medium and
   auto-allowed. Approving a pending request executes the original
   action for real through `ToolRegistry.execute()`'s existing audit-log
   path — approval isn't a separate code path from normal execution, it
   just gates entry to the same one. `approvals` is the second real
   Alembic migration (same shared-core-table gotcha as `memories`, fixed
   the same way before ever running it).
10. **Observability** — done. A real `executions` table (CLAUDE.md §48,
    §93), distinct from `memories`: every Task → Backend → Result run is
    recorded, success or failure, with real per-backend `raw` usage data
    (Anthropic's token counts, Hermes's cost/token JSON) and a real
    `duration_ms`. Third real Alembic migration (same shared-core-table
    gotcha, fixed the same way). `/v1/observability/executions[/{id}]`
    and `/metrics` (total/succeeded/failed/success_rate/avg_duration_ms/
    top agents by execution count) — all computed from real recorded
    rows, not fabricated. Wired into both execution entry points
    (`/v1/agents/execute` and `/v1/agent-fabric/.../delegate`).
11. **Dashboard** — done, deliberately scoped down from CLAUDE.md §50's
    ~18-view list. Real Next.js 16 + TypeScript + Tailwind app
    (`apps/dashboard`) with 5 pages, all hitting the real running API
    (CORS added to `axiom-api` for `localhost:3000`): Overview (every
    subsystem's live status plus real execution metrics), Agent Fabric
    (search the curated cohort, delegate a real task, pick the backend),
    Execution Trace (list + detail from the real `executions` table),
    Approvals (real approve/reject buttons — approving executes the
    original high-risk action for real, same as the API-only proof in
    Milestone 16), and Tools. Not built: Agent Teams, Execution/Knowledge
    Graph visualizations, a dedicated Knowledge Explorer, MCP-specific
    view, Backends view, Memory view, Evaluations, Security, Settings —
    named here rather than silently absent. `npm run build`/TypeScript/
    ESLint are all clean and every route was curl-verified to serve 200
    with working CORS against the real API; the rendered UI was **not**
    visually verified — no browser/screenshot tool was available in this
    environment, and that gap is stated rather than papered over.
12. **Evaluation, Security** — as originally sequenced in `CLAUDE.md`
    §95–96, no changes proposed here.

## 7. Decisions (confirmed with user, 2026-08-25)

1. **Database**: new, independent Supabase project for Axiom OS — not
   shared with ORVYN-V3. Revisit when Project 2 (ORVYN-on-Axiom) actually
   starts.
2. **Graphify target repo for the first real test**: `agency-agents` —
   already on disk, real size, and it's the same repo Agent Fabric
   normalization reads, giving one shared reference point across two
   milestones.
3. **Hermes install**: hold off. Get the native-Claude path (Model Gateway
   + Knowledge Gateway + Agent Fabric, Demo 1) working first; install and
   test against a live Hermes process only when Milestone 13 starts.
