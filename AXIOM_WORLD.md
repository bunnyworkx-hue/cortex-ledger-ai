# Axiom World

`apps/world` — a real, scroll-driven 3D operations view of Axiom OS,
live-wired to the running API. Not a mockup and not built on scroll-world
(see `docs/scroll-word/SCROLL_WORD_AUDIT.md` for why that tool turned out
to be the wrong fit — it's a pre-rendered video generator, not an
interactive engine, and this spec needs live interactivity throughout).
Built directly with react-three-fiber + drei on top of the real Axiom
API instead.

## Run it

```bash
./scripts/dev/run.sh     # API on :8000, in one terminal
./scripts/dev/world.sh   # World on :3000 (or next free port), in another
```

Same same-origin `/api/*` proxy pattern as `apps/dashboard` (see that
app's `next.config.ts` comment for the full CORS-avoidance rationale) —
`AXIOM_API_ORIGIN` in `apps/world/.env.local` controls where it forwards
to.

## What's real

- **Scroll-driven camera.** A single continuous camera path through four
  world-space zones (Entry → Agent Fabric → Knowledge Fabric →
  Execution Engine), built with `@react-three/drei`'s `ScrollControls`/
  `useScroll` and a keyframe interpolator (`components/CameraRig.tsx`) —
  not a hand-rolled scroll listener, and not scroll-world's pre-rendered
  video seek.
- **Agent Fabric zone**: renders the *actual* live division breakdown
  (fetched from `/v1/agent-fabric` at page load — 254 real agents, 17
  real divisions the day this was built) as an instanced point cloud,
  clustered into angular sectors sized proportionally to each division's
  real agent count (`lib/layout.ts::agentClusterPositions`).
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
- **Talk-Back command bar**: a real, working chat — every query calls
  the real `/v1/agent-fabric/search` (Lazy Agent Discovery against the
  actual registry, not a canned response list), and clicking a result
  actually calls `/v1/agent-fabric/agents/{id}/delegate` and shows the
  real Anthropic completion. A query containing a recognized keyword
  also scrolls the camera to the matching zone — a literal keyword map
  (`lib/scrollBridge.ts::zoneIdForQuery`), not NLU, and named as such
  rather than oversold.

## What's honestly not built

The original build prompt (39 sections) is much larger than this. Built
here is its own §32 MVP scope (Entry → Agent Fabric → Graphify →
Execution Engine → Talk-Back) with real data throughout. Not built, and
not silently assumed:

- **Hermes as its own dedicated zone/gateway visualization** (§8-9) —
  Hermes shows up as one real backend node in the Execution Engine zone
  (via `/v1/agents`), not as a separate physical gateway with an animated
  request→authorization→budget→approval sequence.
- **Live-reactive Agent Discovery** (§7) — the real search narrows to
  real matching agents in the chat log, but the 3D agent cloud itself
  doesn't yet visually fade/highlight in response; that's a real,
  reachable next step (the search result already has each agent's real
  `agent_id`, which the Agent Fabric zone could key off of), not built
  in this pass.
- **A live execution-graph animation** (§20) — real delegations happen
  and their real results appear in the chat, but there's no separate
  animated "watch the request travel through Planner → Backend → Tools
  → Verify" sequence.
- **Voice input/output** (§22) — explicitly deferred by the prompt
  itself ("do not implement voice unless the existing architecture
  supports it cleanly... text talk-back is mandatory for MVP"). Text
  only.
- **Human Approval station, Policy Engine room, Tool Registry area,
  MCP area, ORVYN destination** (§16-19, §31) — real endpoints exist for
  approvals/tools (see the Dashboard and DEMO.md for the working
  propose→approve→execute flow) but have no dedicated 3D representation
  here yet.
- **Mobile fallback, LOD/instancing tuning beyond drei's `Instances`
  defaults, formal security testing pass** (§27-28, Phase 14-15) — not
  done.

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
