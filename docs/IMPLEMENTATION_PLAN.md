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
12. **Evaluation** — done. `scripts/evaluation/run_benchmark.py`: a real
    20-task benchmark (CLAUDE.md §75's own "at least 20 tasks" spec)
    covering all 12 required categories, run entirely as real HTTP calls
    against the live API — no internals imported directly, no simulated
    results. Scoring is deliberately simple and stated as such (CLAUDE.md
    §45's "never fabricate metrics"): most tasks ask an agent to reply
    with an exact token, a real deterministic pipeline check rather than
    a fuzzy quality judgment; tool/knowledge/approval tasks check a real
    structural signal instead. 20/20 passed on the last real run
    (research/analysis/planning/marketing/finance/operations/tool_use/
    agent_delegation ~2-3s each, hermes_delegation ~10.8s — real
    subprocess overhead, not a bug — tool/knowledge/graphify_query
    140-509ms since no LLM call is involved). Reports land in
    `var/evaluation/` as timestamped JSON for regression comparison
    across runs, rather than a new `evaluation_runs` DB table — reusing
    `var/`'s existing generated-artifact convention (same as
    `graphify-out/`) instead of adding schema for a v1 that doesn't need
    it yet.
13. **Security** — done. Full writeup in `docs/security/SECURITY_AUDIT.md`,
    organized by all 11 of CLAUDE.md §96's named categories. Real,
    live-verified enforcement for Tool Authorization (the propose→approve
    gate lives at the API router layer, not inside `ToolRegistry` itself
    — documented as a real architectural boundary, not fixed, since the
    only two current callers of `execute()` are both policy-aware),
    Approval Bypass (double-decision, nonexistent-id, and
    unregistered-tool paths all correctly rejected), Hermes Security (no
    shell interpretation of the prompt — proven against a real
    subprocess with shell-metacharacter payloads — and the API key
    travels via subprocess `env`, never argv), and Graphify Access (the
    adapter exposes only 4 read methods; the live MCP server's 10
    advertised tools are all read-only by name and now correctly
    classified `"low"` risk). One real bug found and fixed along the way:
    `shortest_path` was misclassified `"medium"` by
    `axiom_mcp.client._infer_risk_level`'s naming heuristic even though
    the Graphify audit had already confirmed it's genuinely read-only —
    added `"shortest_"`/`"find_"` to the recognized prefixes and
    re-verified live (all 10 tools now report `"low"`). Prompt Injection
    was live-probed against the real Anthropic-backed model (not
    unit-tested — CLAUDE.md §45 rules out a fabricated pass/fail
    assertion for a non-deterministic property): 2 of 3 payloads were
    correctly refused, but a `SYSTEM OVERRIDE`-style payload succeeded
    and the agent broke character entirely, output only `PWNED` — a real,
    reported result, not smoothed over. Five categories are named as
    real, undone gaps rather than claimed as covered: Memory/Tenant
    Isolation (`owner_id`/`tenant_id` are caller-supplied query params
    with no auth deriving them from a real identity — proven live, any
    caller can read any other owner's memory), Agent Authorization (no
    authN/authZ layer exists in this build at all), Budget enforcement
    (usage data is captured per-call but never aggregated or gated),
    Knowledge Isolation (Graphify is one shared graph, no tenant
    partitioning), and Recursive Delegation (not applicable — no code
    path has one agent invoke another yet, so there's nothing to guard).
    94/94 tests passing after this milestone (88 pre-existing + 6 new
    security-focused files).

## 6a. Post-Milestone-21 — closing the two real Definition of Done gaps (2026-08-26)

The Security milestone (§13 above) named two CLAUDE.md §98 Definition of
Done items as genuine, undone gaps rather than checked off by assumption:
"Agent budgets work" and "Agent-to-agent calls are controlled." At the
user's request to keep going, both were closed for real:

**Agent budgets**: `Agent` gained a `budget: dict` field
(`packages/axiom-core/axiom_core/agents/types.py`), threaded from
`AgentRecord.budget` through `AgentInvocationGateway.delegate()`.
`AxiomNativeBackend` enforces `max_tokens` as the literal
`ModelRequest.max_tokens` sent to the model API and `max_seconds` via
`asyncio.wait_for`. `HermesBackend` enforces `max_seconds` by overriding
`run_oneshot`'s own safe (subprocess-killing) timeout; `max_tokens` is
explicitly **not** enforced for Hermes since its usage-report JSON schema
was never precisely verified live in this build — named, not guessed at.

Enforcing this for real immediately surfaced a genuine bug: the installed
`anthropic` SDK refuses any non-streaming call where
`3600 * max_tokens / 128_000 > 600s`, i.e. `max_tokens > 21,333`. Every
one of the 12 curated agents' budgets (25,000-50,000, set during
Milestone 10's curation but never actually enforced until now) exceeded
that ceiling — every curated-agent delegation started failing with the
SDK's own `ValueError` the moment enforcement went live. Fixed by
clamping to a 20,000-token ceiling in `AxiomNativeBackend`, live-verified
afterward (`engineering/engineering-frontend-developer`, `max_tokens:
40000` in its curated budget, delegates successfully post-fix).

**Agent-to-agent delegation control**: a new native tool,
`delegate_to_agent` (`apps/api/axiom_api/native_tools.py`), lets a caller
have one agent's task delegate a sub-task to another registered agent —
through the exact same path a direct API delegation uses
(`apps/api/axiom_api/delegation.py::run_delegation`, factored out of the
router so the tool path isn't a shortcut with different tracing/memory
behavior). A real, tested hard cap (`_MAX_DELEGATION_DEPTH = 3`) refuses
further delegation once reached — live-verified: depth 3 returns
`is_error: true` rather than recursing.

Named honestly, not oversold: `AxiomNativeBackend` has no tool-calling
loop, so no agent's own model output can invoke `delegate_to_agent`
autonomously yet — only a direct `POST /v1/tools/delegate_to_agent/call`
reaches it today. The depth cap is a forward-compatible guard, and
`_delegation_depth` is caller-supplied rather than derived from a real
execution context, so it's a cooperative control, not a cryptographic
one — the same class of boundary as every unauthenticated gap already
named in `docs/security/SECURITY_AUDIT.md`.

Both changes are covered by new real tests (`tests/unit/test_native_backend.py`,
`tests/unit/test_hermes_adapter.py`, `tests/unit/test_delegate_to_agent_depth.py`)
and one refactor (the router's delegate endpoint now calls the same
`run_delegation` helper, with existing integration tests confirming no
behavior regression). 104/104 tests passing (up from 94). Full details
and honest remaining limits in `docs/security/SECURITY_AUDIT.md` §9/§11.

## 6b. Dashboard: cross-origin fetch failing in the browser only (2026-08-26)

A real user testing the dashboard hit "Failed to reach the Axiom API" on
every page — but every server-side check came back clean: `/health` and
every `/v1/*` route the Overview page calls returned 200 with valid
JSON, a simulated browser request with the real `Origin: http://localhost:3000`
header got the correct `Access-Control-Allow-Origin` response back on
both the preflight `OPTIONS` and the actual `GET`, no 307/308 redirects
existed on any of those paths (a known CORS-breaking gotcha in
FastAPI/Starlette routing), and `curl` to the dashboard's own origin
returned 200. The uvicorn access log showed clean, complete traffic
patterns matching full page loads with zero errors. Every plausible
server-side cause was ruled out live, one at a time, not assumed clean.

Root cause was never pinned to an exact browser mechanism (no console
error text was available to inspect) — the leading candidate is a
browser extension or an embedded-webview context blocking a cross-origin
`fetch()` to a non-standard local port (`:8000`) even though CORS itself
was correctly configured, which is a real, known class of problem
`curl`-based verification structurally cannot reproduce.

Rather than keep guessing at the exact mechanism, fixed it by
eliminating the cross-origin request entirely: `apps/dashboard/next.config.ts`
now proxies `/api/*` through Next's own server to `AXIOM_API_ORIGIN`
(server-side, same machine, exactly like `curl` was already doing
successfully), and `lib/api.ts` now calls `/api` by default instead of
`http://127.0.0.1:8000` directly — the browser's fetches are same-origin,
so CORS (and whatever was blocking it) no longer applies. A real,
previously-orphaned `next dev` process on port 3000 (surviving from an
earlier restart attempt whose `pkill` pattern missed it) was also found
and killed during this fix — a real, separate finding, not assumed to be
the cause of the original bug but worth naming since it could have
caused a stale-config red herring on a future debugging pass. Verified
after the fix: clean `tsc --noEmit`, clean `next build`, clean `eslint`,
and `curl http://localhost:3000/api/v1/tools` returning the real 12-tool
list through the new proxy path.

## 6c. Axiom World — the 3D operations view (2026-08-26)

The user handed over a large (39-section) build prompt for a cinematic
scroll-driven 3D interface, explicitly built on a tool named
"Scroll-Word," with its own instruction not to assume that tool's APIs
and to audit it first. No repository named "Scroll-Word" exists;
`docs/scroll-word/SCROLL_WORD_AUDIT.md` inspected the real, obvious match
(`oso95/scroll-world`, ~3,587 stars) live — its README, repo tree, and
real `SKILL.md` — before writing any code, per the same discipline the
Graphify/Hermes audits followed at the very start of this project.

**Real, load-bearing finding**: scroll-world is a Claude Code *skill*
that runs an 8-step procedure once (interview → generate AI stills via
Higgsfield → render AI video clips via Monid/Higgsfield, real metered
cost, human budget approval required → encode → assemble) to produce one
fixed, pre-rendered video that scroll position seeks through. Its only
runtime input is scroll position mapped to playback time — it cannot
highlight a live search result, move the camera to an arbitrary
chat-driven point, or reflect any state that changes after the video
finished rendering. That's the opposite of what most of the build
prompt's own acceptance criteria (§37) require: live Agent Discovery
against the real 254-agent registry, a chat-driven camera, a live
execution trace. Presented this fork to the user via AskUserQuestion
rather than silently picking a side or force-fitting the tool; the user
chose to skip scroll-world entirely and build a genuinely interactive
scene instead.

**Built**: `apps/world`, a new Next.js + react-three-fiber + drei app,
same `/api/*` same-origin proxy pattern that fixed the dashboard's
connectivity bug (`next.config.ts` rewrite to `AXIOM_API_ORIGIN`). Scope
matches the build prompt's own §32 MVP list (Entry → Agent Fabric →
Graphify → Execution Engine → Talk-Back), built with real data
throughout rather than the placeholder/mock data the prompt's own §34/§35
explicitly forbid presenting as live:

- Scroll-driven camera (`components/CameraRig.tsx`) built on drei's
  `ScrollControls`/`useScroll` with a keyframe interpolator — a real
  library primitive, not a hand-rolled scroll listener.
- Agent Fabric zone: the real, live `by_division` breakdown from
  `/v1/agent-fabric` (254 agents / 17 divisions the day this was built),
  rendered as an instanced point cloud clustered by real division size.
- Knowledge Fabric zone: the real Graphify extraction
  (`var/graphify-out/graph.json`) read directly server-side rather than
  through the MCP tools — those return LLM-formatted text, not bulk
  structured JSON, a real finding from Milestone 8 that still holds here
  — sampled to the 400 highest-degree real nodes, real `EXTRACTED`/
  `INFERRED` edge confidence preserved.
- Execution Engine zone: whichever Model/Agent/Knowledge backends are
  actually registered right now (`/v1/models`, `/v1/agents`,
  `/v1/knowledge`), with an unconfigured backend rendered visibly dim
  rather than hidden.
- Talk-Back: a real working chat calling the real
  `/v1/agent-fabric/search` and `/v1/agent-fabric/{id}/delegate` — not a
  canned response list. A recognized keyword also scrolls the camera to
  the matching zone, explicitly documented as a literal keyword map
  (`lib/scrollBridge.ts`), not NLU.

**Real bug found while wiring Talk-Back's own onboarding example**:
`/v1/agent-fabric/search` does literal substring matching against each
agent's real description, not stemming — `"finance"` returns zero
results because the FP&A Analyst's real description says "**Financial**
Planning & Analysis," not "finance." Existing Agent Fabric behavior, not
introduced here; fixed by rewriting the onboarding hint to a verified-
working query (`"security"`, `"frontend"`) instead of promising something
the real search can't do.

**Not built**, named honestly in `AXIOM_WORLD.md` rather than silently
assumed: a dedicated Hermes gateway visualization (§8-9 — Hermes appears
as one real backend node in Execution Engine, not its own zone), live
visual highlighting of the agent cloud in response to search (§7 — the
chat surfaces real matches today, the 3D cloud doesn't yet react),
animated execution-graph playback (§20), voice I/O (§22 — explicitly
deferred by the prompt's own text), and dedicated Policy/Approval/Tool
Registry/MCP/ORVYN zones (§16-19, §31). Verified: clean `tsc --noEmit`,
clean `next build`, clean ESLint (one known App-Router false-positive
warning about `<link>`-based font loading, harmless), and every real
endpoint the app calls curl-verified through the new proxy including a
live `delegate` call returning a real Anthropic completion. Not visually
verified in a browser — same environment limitation as the dashboard.

## 6d. Axiom World — operate the system, don't just view it (2026-08-26)

The user's follow-up: "I want it to function like an agentic OS system"
— matching CLAUDE.md §39's own "I am operating an AI organization, not
chatting with an AI." The gap: Talk-Back could search real agents, but
clicking a result always ran the same fixed placeholder prompt ("In one
sentence, what do you do?") instead of whatever the user actually asked
for, and the 3D scene had no way to show *which* real agent was doing
real work, because the only Agent Fabric data available
(`/v1/agent-fabric`'s aggregate `by_division` counts) had no individual
agent identity to key off of.

**New, real, small backend addition**: `GET /v1/agent-fabric/agents`
(`apps/api/axiom_api/routers/agent_fabric.py`), returning the full real
254-agent roster via the same `gateway.list()` the aggregate endpoint
already calls internally — every record gets a real, addressable
`agent_id`, unlike the aggregate-only status route. Two new real
integration tests confirm it returns the same total as the aggregate
count and correctly filters by division. 106/106 tests passing (up from
104).

**Frontend rewrite**: `lib/layout.ts::agentPositions` now seeds each
point's position by real `agent_id` (not division+index), so a specific
real agent always renders in the same spot — a stable identity Talk-Back
can look up. Talk-Back no longer sends a canned prompt: submitting a
real task searches the real registry, then *automatically delegates that
same real task* to the closest match and shows the real result, with
other real matches offered as one-click "also run this same task" chips
— a genuine multi-agent team assembled by clicking, not simulated.
`World.tsx` now lifts an `activeAgentIds` set from Talk-Back's real
in-flight delegations into `AgentFabricZone`, so whichever specific real
agent is actually working right now visibly lights up gold and grows in
the point cloud — the first real link between the chat and the 3D scene,
closing half of §7's original Agent Discovery ask (highlighting the
selected agent; dimming the non-matching rest is still not built, named
honestly in `AXIOM_WORLD.md` rather than claimed).

## 6e. Axiom World — fade-back and a real execution pulse (2026-08-26)

Immediate follow-up: closed the other half of §7 and added an honest
stand-in for §20. `AgentFabricZone` now takes a real `matchedAgentIds`
set (Talk-Back's real search-result ids, reported via a new
`onMatchedAgentsChange` callback) — every non-matching real agent dims
to grey and shrinks the moment a search returns results, matching "the
irrelevant agents fade back" from the original spec, tied to a genuine
search response rather than simulated. A new `ExecutionPulse` component
animates a light along the real line between the Agent Fabric and
Execution Engine zone centers while any real `delegate()` call is
in-flight (`onExecutingChange`, driven by the same `running` set
Talk-Back already tracked for the chip-disable UI) — deliberately not a
fabricated multi-stage Planner/Backend/Tools/Verify trace, since the
real backend doesn't emit intermediate progress for one HTTP call, but a
real, correctly-timed visualization of the one hop that does exist.
Clean `tsc`/`build`/`lint`; 106/106 backend tests unaffected (no backend
changes this pass).

## 6f. Axiom World — a real Human Approval station (2026-08-26)

Continuing the build after the user's "proceed with the next step":
picked the highest-value remaining real gap — §19's Human Approval
station, CLAUDE.md §64's own Sixth Demo — since the backend flow it
needs (propose → pending → approve/reject → execute) was already fully
real and tested, just absent from the 3D world.

New `ApprovalStation.tsx`: a fixed HTML overlay panel (same pattern as
Talk-Back — real interaction needs real DOM buttons, not raycasted 3D
meshes). "Propose test action" calls the real
`POST /v1/tools/modify_business_record/call`; the real Policy Engine
genuinely refuses to run it, returning a real pending `approval_id`.
The panel polls `GET /v1/approvals` every 6s (real polling, not a fake
timer) and lists every real pending approval — 21 in the live system at
verification time, mostly left over from earlier test runs across this
whole project, a real number. Approve calls the real
`POST /v1/approvals/{id}/approve` (which actually executes the held
action and returns the real mutated record); Reject calls the real
`.../reject` (which never executes it). `lib/api.ts` gained
`listApprovals`/`approve`/`reject`/`proposeDemoAction`, typed against
the real `ApprovalOut`/`PendingApprovalOut`/`ToolCallResultOut` schemas
in `apps/api/axiom_api/schemas.py`, not guessed.

**Real lint error hit and fixed, not just a warning this time**: the
first draft called a `useCallback`-wrapped `refresh()` directly inside a
`useEffect` body, which `eslint-plugin-react-hooks`'s
`set-state-in-effect` rule flags as an error (cascading-render risk) —
`next build` genuinely failed on it. Fixed by inlining the poll function
inside the effect with its own `cancelled` guard (the same pattern
`World.tsx`'s own data-loading effect already used), keeping a separate
plain `refresh()` for the two call sites outside any effect
(`proposeDemoAction`, `decide`) where the rule doesn't apply. Verified
live end-to-end through the real proxy path: propose → real pending
approval appears in a live `GET /v1/approvals` → approve → real mutated
record returned — the exact same calls the component makes. Clean
`tsc`/`build`/`lint`; 106/106 backend tests unaffected (no backend
changes this pass).

## 6g. Axiom World — a real, schema-driven Tool Registry panel (2026-08-26)

Next real gap on "next": §16's Tool Registry. Built `ToolRegistryPanel.tsx`
to be genuinely schema-driven rather than a hardcoded per-tool UI —
it fetches the real `GET /v1/tools` (all 12) and, for each one, builds
its input fields directly from that tool's own real
`input_schema.required`/`properties`, coercing `integer`/`number`
properties with `Number()`. This means every real tool works, including
ones with zero required args (`graph_stats`, `god_nodes`, `list_prs`,
`triage_prs` — a bare "Call" button), one required arg
(`query_graph`'s `question`, `get_node`'s `label`), two
(`shortest_path`'s `source`/`target`, `delegate_to_agent`'s
`agent_id`/`task_input`), and a high-risk one
(`modify_business_record`) — which correctly routes to a real pending
approval via the exact same Policy Engine path the Human Approval panel
already demonstrates, rather than a separate, redundant code path.
`lib/api.ts` gained `listTools`/`callTool`, typed against the real
`ToolDefinition` schema.

Verified live through the real proxy for all three real shapes: a
zero-arg call (`graph_stats` → real node/edge/community stats), a
one-required-arg call (`query_graph` → real graph traversal text), and
the high-risk call (`modify_business_record` → a real pending
`approval_id`, confirmed it'll surface in the same `GET /v1/approvals`
the Approval panel polls). Clean `tsc`/`build`/`lint`; 106/106 backend
tests unaffected (no backend changes this pass).

## 6h. Axiom World — a real crash, finally diagnosed and fixed (2026-08-26)

For the first time in this whole debugging saga, the user sent real
screenshots of the actual browser errors instead of "still the error
message" — and they showed two genuinely different, previously
undiagnosable bugs, not the CORS/extension mystery assumed from the
dashboard's earlier symptom.

**Axiom World (localhost:3001)**: a real, unambiguous React crash —
Next.js's own dev error overlay, not a network failure: `"You are
calling ReactDOMClient.createRoot() on a container that has already
been passed to createRoot() before"`, thrown from `ZoneOverlay.tsx`'s
use of `@react-three/drei`'s `<Scroll html>`. Root cause: `<Scroll
html>` calls `ReactDOM.createRoot()` internally to portal HTML content
outside the R3F canvas tree, and that doesn't survive React 19 Strict
Mode's deliberate double-invoke of effects in Next.js dev — the second
mount pass calls `createRoot` again on the same container. This had
been silently breaking the zone-label overlay (and possibly more) since
Milestone 6a first introduced it, undetectable without literally seeing
the browser's error overlay.

Fixed at the root, not papered over with `reactStrictMode: false` (which
would have silenced Strict Mode's legitimate bug-catching everywhere
else too): removed `<Scroll html>` entirely. `ZoneOverlay.tsx` now
renders as a plain HTML sibling outside the `<Canvas>` (same pattern as
Talk-Back), and a new `ZoneOverlaySync.tsx` (mounted inside
`<ScrollControls>`) drives each label's opacity imperatively via
`useFrame` + a small ref bridge (`lib/zoneOverlayBridge.ts`) — matching
`CameraRig.tsx`'s own existing pattern of never routing high-frequency
scroll-driven updates through React state. `activeZone`/`zoneProgress`
helpers already existed in `lib/zones.ts` (written earlier, unused until
now) and slotted in directly.

**Dashboard (localhost:3000)**: a real, still-open, narrower mystery —
the page itself loads correctly (nav renders, no crash), but `/api/*`
fetch calls still fail in the user's browser despite being same-origin
now and despite an identical `curl` to the exact same path succeeding.
Not yet root-caused; needs the browser's Network tab detail (status
code / error type for the specific failing request) to go further, not
guessed at.

Verified after the World fix: clean `tsc`/`build`/`lint`, confirmed
`<Scroll` is no longer imported anywhere in the app, clean server logs
across multiple real page loads. Backend suite unaffected: 106/106
passing.

## 6i. Axiom World — Tool Registry: a real UX gap, not a broken app (2026-08-26)

More real screenshots — this time of the Tool Registry panel showing
"multiple errors." Investigated each one rather than assuming a repeat
of the crash pattern: `graph_stats`/`god_nodes` (zero-arg tools) worked
perfectly when re-verified live via curl; `list_prs`/`triage_prs`
correctly report a real environment limitation ("gh CLI not found or
not authenticated") that has nothing to do with this panel. The actual
finding, visible in the screenshots: every "error" came from clicking
Call before filling in a tool's required field.

Two real, distinct problems that produced confusing output rather than
a clean stop: `Number("")` evaluates to `0` in JavaScript, not `NaN` —
so an empty `community_id` field silently became a genuinely "valid"
call (`get_community` with id 0), returning a real but unintended
result. And an empty required `label` reached `get_neighbors` and
crashed *Graphify's own* handler with a raw Python "not enough values
to unpack (expected 4, got 0)" exception instead of a clean validation
message — a real bug in Graphify's tool implementation, not something
fixable from this panel, but also not something that should ever reach
the API in the first place.

Fixed in `ToolRegistryPanel.tsx`: `call()` now validates required
fields *before* touching the network — empty fields short-circuit with
"Fill in: `<names>`" and non-numeric input to an integer/number field
short-circuits with "`<name>` must be a number," neither of which
makes an API call at all. Inputs for integer/number schema properties
now render as `type="number"` for a better native input experience.
Clean `tsc`/`build`/`lint`; 106/106 backend tests unaffected (no
backend changes — both real underlying issues, the JS empty-string
coercion and Graphify's unpacking crash, are now prevented from being
reachable rather than patched after the fact).

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
