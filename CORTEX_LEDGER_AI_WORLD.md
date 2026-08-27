# Cortex Ledger AI World

`apps/world` — a real, scroll-driven 3D operations view of Cortex Ledger AI,
live-wired to the running API. Not a mockup and not built on scroll-world
(see `docs/scroll-word/SCROLL_WORD_AUDIT.md` for why that tool turned out
to be the wrong fit — it's a pre-rendered video generator, not an
interactive engine, and this spec needs live interactivity throughout).
Built directly with react-three-fiber + drei on top of the real Cortex Ledger AI
API instead.

## Run it

```bash
./scripts/dev/run.sh     # API on :8000, in one terminal
./scripts/dev/world.sh   # World on :3000 (or next free port), in another
```

Same same-origin `/api/*` proxy pattern as `apps/dashboard` (see that
app's route handler comment for the full CORS-avoidance rationale) —
`AXIOM_API_ORIGIN` in `apps/world/.env.local` controls where it forwards
to. The proxy is a real Route Handler (`app/api/[...path]/route.ts`),
not `next.config.ts`'s built-in `rewrites()` — that had an undocumented
~30s timeout that cut off genuinely successful, slower real calls (real
Hermes delegations routinely take 10-35s+); the route handler sets an
explicit 130s timeout instead, past `HermesBackend`'s own 120s default.

## What's real

- **Scroll-driven camera.** A single continuous camera path through four
  world-space zones (Entry → Agent Fabric → Knowledge Fabric →
  Execution Engine), built with `@react-three/drei`'s `ScrollControls`/
  `useScroll` and a keyframe interpolator (`components/CameraRig.tsx`) —
  not a hand-rolled scroll listener, and not scroll-world's pre-rendered
  video seek.
- **Agent Fabric zone**: renders the *actual full roster* — every one of
  the 254 real agents, each with a real, individually addressable
  `agent_id` (a new endpoint, `GET /v1/agent-fabric/agents`, added
  alongside the existing aggregate-only status route specifically so the
  scene could give real identity to individual points instead of
  anonymous dots) — as an instanced point cloud, clustered into angular
  sectors sized proportionally to each division's real agent count
  (`lib/layout.ts::agentPositions`, seeded per-agent so a given real
  agent always renders in the same spot).
- **Knowledge Fabric zone**: renders the *actual* Graphify extraction
  (`var/graphify-out/graph.json`, read server-side —
  `lib/graphData.server.ts`) — real node labels, real communities, real
  `EXTRACTED`/`INFERRED` edge confidence, sampled down to the 400
  highest-degree real nodes for a legible scene rather than an
  undifferentiated cloud of all 1,121.
- **Execution Engine zone**: renders whichever Model Gateway / Agent
  Backend / Knowledge Gateway backends are *actually* registered right
  now (`/v1/models`, `/v1/agents`, `/v1/knowledge`) — an unconfigured
  backend renders visibly dim rather than being hidden or faked as
  present.
- **Talk-Back command bar operates the system, not just queries it.**
  Typing a real task — not a fixed canned prompt — calls the real
  `/v1/agent-fabric/search` (Lazy Agent Discovery against the actual
  254-agent registry), then *automatically delegates that same real task*
  to the closest real match via `/v1/agent-fabric/agents/{id}/delegate`
  and shows the real Anthropic completion, no extra click required.
  Other real matches appear as chips you can run the identical real task
  against too — a genuine multi-agent "team" you assemble by clicking,
  not a hypothetical. Submitting also scrolls the camera to the Agent
  Fabric zone (or another zone on a recognized keyword — a literal
  keyword map, `lib/scrollBridge.ts::zoneIdForQuery`, not NLU, named as
  such).
- **The 3D scene visibly reacts to real work — both halves of §7 now.**
  Whichever real agent Talk-Back is currently running lights up gold and
  grows (`activeAgentIds`, lifted from Talk-Back's real in-flight
  delegations). Separately, the moment a real search returns results,
  every agent *not* in that result set fades to a dim, shrunk grey
  (`matchedAgentIds`, `AgentFabricZone`'s `DIM_COLOR`) while the real
  matches stay at full color — "the irrelevant agents fade back, selected
  agents become highlighted," tied to an actual search response, not
  simulated. The fade clears back to normal once a query returns zero
  matches.
- **A real execution pulse between zones.** While any real `delegate()`
  call is in flight — the initial automatic run or a follow-up chip —
  `ExecutionPulse` animates a small light along the line from the Agent
  Fabric zone to the Execution Engine zone, driven by the same real
  `running` set Talk-Back already tracks (`onExecutingChange`), not a
  fake timer. This is deliberately *not* a fabricated multi-stage
  Planner→Backend→Tools→Verify trace (§20) — the real backend doesn't
  report intermediate stages for a single HTTP delegate call — but it
  does make the one real async hop (agent selected → agent executing)
  visible and correctly timed.
- **Human Approval station** (§19, CLAUDE.md §64's Sixth Demo) —
  `ApprovalStation` is a real, working panel, not a mockup: "Propose test
  action" calls the real `POST /v1/tools/modify_business_record/call`
  (the same demo high-risk tool the rest of Cortex Ledger AI uses), which the
  real Policy Engine genuinely refuses to run, returning a real pending
  `approval_id`. The panel polls `GET /v1/approvals` every 6s and lists
  every real pending approval (21 in the live system as of this build —
  mostly left over from earlier test runs, a real number, not staged).
  Approve calls the real `POST /v1/approvals/{id}/approve`, which
  actually executes the held action and returns the real mutated record;
  Reject calls the real `.../reject`, which never executes it. Verified
  live end-to-end through the exact same proxy path the component uses.
- **Tool Registry panel** (§16) — `ToolRegistryPanel` is genuinely
  schema-driven, not a hardcoded subset: it fetches the real
  `GET /v1/tools` (all 12 real tools) and, for each one, builds its input
  fields directly from that tool's own real `input_schema.required`/
  `properties` — so a tool added to the registry later works here with
  no code change. "Call" hits the real `POST /v1/tools/{name}/call` with
  the real constructed arguments; a real high-risk call correctly routes
  to a pending approval (visible in the Human Approval panel) instead of
  executing, exactly like every other real path into the Policy Engine.
- **Real Hermes routing** (§8-9) — Talk-Back's "Run via Hermes" checkbox
  threads `backend: "hermes"` through the same real `delegate()` call,
  which reaches the real `HermesBackend` (a genuine subprocess `hermes`
  CLI call, ~10-35s real overhead, not Cortex Ledger AI's native path). Verified
  live: `sales/sales-deal-strategist` via Hermes returned a real
  completion with `backend_name: "hermes"`. Hermes's node in the
  Execution Engine zone renders with a distinct ring, marking it as an
  external, gated runtime per CLAUDE.md §8-9's own framing ("Hermes
  should never visually appear to own the Cortex Ledger AI environment").
- **Policy Engine panel** (§17) — `PolicyEnginePanel` states the one
  real rule every approval's own `reason` text already spells out in
  words (risk at or above the real configured threshold, `"high"`,
  stops for a human) as its own visible thing: a risk ladder with real
  live tier counts computed from `GET /v1/tools`'s actual risk levels
  (10 low, 1 medium, 1 high, 0 critical at verification time) — no new
  backend endpoint needed, since every number it shows was already being
  fetched by Tool Registry.
- **MCP interoperability panel** (§18) — `McpAreaPanel` renders the real
  `CORTEX LEDGER AI → MCP → [servers]` diagram CLAUDE.md §18 itself describes, with
  a real branch node per connected MCP server and how many real tools it
  contributed on discovery (derived from `GET /v1/tools`'s `source`
  field, e.g. `"mcp:graphify"` → server `graphify`, 10 tools — verified
  live). One real server is connected today; the panel shows an honest
  empty state if none are, rather than inventing placeholder
  connections.
- **Real pointer interactivity in the 3D scene.** Every panel above is
  an HTML overlay — the actual 3D content (agent points, graph nodes,
  backend spheres) had zero pointer interactivity until direct user
  feedback ("its not reactive or interactive") called that out, fairly.
  Closed for the Agent Fabric zone: hovering a real agent point
  brightens it and shows its name/division live in the zone's subtitle
  (real per-instance `onPointerOver`/`onPointerOut`, not custom
  raycasting — drei's built-in `<Instance>` pointer events); clicking one
  opens `SelectedAgentCard`, a real detail panel with that agent's real
  fields and a real "run a task on this specific agent" action through
  the same `api.delegate()` every other panel uses.

  Extended to the Knowledge Fabric zone too: hovering a real graph node
  brightens it and shows its real label/community/degree; clicking opens
  `SelectedNodeCard`, whose "Find real neighbors" button makes a genuine
  live call to the real Graphify MCP tool (`get_neighbors`) and shows the
  actual traversal result — not a canned response, a real query against
  the real graph, through the same generic tool-caller Tool Registry
  uses. Verified live: querying neighbors of the real `RecordingContext`
  node returned its real callers/callees with real
  `source_file:source_location`.

  Extended to the Execution Engine zone last, closing the pattern: hovering
  a real backend sphere (Model Gateway / Agent Backends / Knowledge
  Gateway) brightens it and updates the zone's subtitle with its real
  name/group/status; clicking opens `SelectedBackendCard`. Deliberately
  informational only, not another action button — unlike agents
  (`delegate()`) and graph nodes (`get_neighbors`), there's no
  per-backend endpoint to call; `/v1/models`, `/v1/agents`, and
  `/v1/knowledge` only ever return the aggregate name→status map this
  card is already built from, so it doesn't invent an action that
  doesn't exist.

## What's honestly not built

The original build prompt (39 sections) is much larger than this. Built
here is its own §32 MVP scope (Entry → Agent Fabric → Graphify →
Execution Engine → Talk-Back) with real data throughout. Not built, and
not silently assumed:

- **A full physical Hermes gateway with an animated
  request→authorization→budget→approval sequence** (§8-9) — Hermes
  itself is now real and working, not just present: Talk-Back's "Run via
  Hermes" checkbox actually routes a real `delegate()` call through the
  real `HermesBackend` (a real subprocess `hermes` CLI call, not
  Cortex Ledger AI's native path), and its node in the Execution Engine zone gets a
  distinct visual ring marking it as an external, gated runtime. What's
  still not built is the dedicated multi-step gateway *sequence*
  animation (request → authorization → budget → risk → approval →
  execution as separate visualized stages) — the real path exists and
  is now reachable, it just isn't broken into animated steps.
- **A multi-stage execution-graph animation** (§20) — `ExecutionPulse`
  now shows the one real hop that exists (Agent Fabric → Execution
  Engine, timed to real in-flight state), but there's no separate
  Planner → Backend → Tools → Verify staged sequence, because the real
  backend doesn't emit intermediate progress events for a single
  delegate call to animate honestly.
- **Voice input/output** (§22) — explicitly deferred by the prompt
  itself ("do not implement voice unless the existing architecture
  supports it cleanly... text talk-back is mandatory for MVP"). Text
  only.
- **Business Operations destination** (§31) — Human Approval (§19), Tool Registry
  (§16), Policy Engine (§17), and MCP (§18) are all now real and working
  (see above). Business Operations itself isn't a real project yet — see
  `docs/IMPLEMENTATION_PLAN.md` §7's decision to defer it entirely —
  so there's nothing real to build a destination toward.
- **LOD/instancing tuning beyond drei's `Instances` defaults, formal
  security testing pass** (§27-28, Phase 14-15) — not done.

One real mobile bug is fixed, not the full §27 scope: `AgentListPanel`
and `GraphNodeListPanel` both default *open* on desktop (deliberately —
they exist to compensate for their 3D clusters spinning continuously),
but at a real phone width there isn't room for two persistent side
panels plus Talk-Back without them overlapping. `lib/useOpenByDefault.ts`
now defaults them closed under a `767px` media query instead, via
`useSyncExternalStore` rather than a `useEffect`+`setState` mount check —
the latter is a real anti-pattern (an unconditional `setState` in an
effect forces an extra synchronous render, and the React Compiler's own
`react-hooks/set-state-in-effect` lint rule caught it), and a naive
`useState(() => window.innerWidth < N)` initializer would read `window`
during the server render and mismatch the client's first hydration pass.
Every panel's width was already responsive (`min(Npx, Nvw)` throughout,
predating this pass) — the overlap was the one real gap. Touch-gesture
tuning, viewport-driven LOD, and a genuine phone-in-hand verification
pass are not done.

## A real, honest UX finding from building this

The registry's `/v1/agent-fabric/search` does literal substring matching
against each agent's real description text, not stemming or semantic
search — querying `"finance"` returns zero results because the real FP&A
Analyst's description says "**Financial** Planning & Analysis," not
"finance." `"financial"`, `"security"`, `"frontend"`, `"sales"`,
`"software"` all work. This is existing Agent Fabric behavior, not
something introduced here — Talk-Back's own onboarding message was
written to use a verified-working example query rather than promise
something the real search can't do.
