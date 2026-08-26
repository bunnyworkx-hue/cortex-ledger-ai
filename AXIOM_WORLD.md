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
  (the same demo high-risk tool the rest of Axiom OS uses), which the
  real Policy Engine genuinely refuses to run, returning a real pending
  `approval_id`. The panel polls `GET /v1/approvals` every 6s and lists
  every real pending approval (21 in the live system as of this build —
  mostly left over from earlier test runs, a real number, not staged).
  Approve calls the real `POST /v1/approvals/{id}/approve`, which
  actually executes the held action and returns the real mutated record;
  Reject calls the real `.../reject`, which never executes it. Verified
  live end-to-end through the exact same proxy path the component uses.

## What's honestly not built

The original build prompt (39 sections) is much larger than this. Built
here is its own §32 MVP scope (Entry → Agent Fabric → Graphify →
Execution Engine → Talk-Back) with real data throughout. Not built, and
not silently assumed:

- **Hermes as its own dedicated zone/gateway visualization** (§8-9) —
  Hermes shows up as one real backend node in the Execution Engine zone
  (via `/v1/agents`), not as a separate physical gateway with an animated
  request→authorization→budget→approval sequence.
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
- **Policy Engine room, Tool Registry area, MCP area, ORVYN destination**
  (§16-18, §31) — Human Approval (§19) is now real and working (see
  above); these others still have no dedicated representation, in the 3D
  scene or as an overlay panel.
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
