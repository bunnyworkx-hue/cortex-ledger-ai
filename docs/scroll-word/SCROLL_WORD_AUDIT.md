# Scroll-World Audit (build prompt's "Scroll-Word")

Source: [`github.com/oso95/scroll-world`](https://github.com/oso95/scroll-world)
(MIT, ~3,587 stars). "Scroll-Word" in the build prompt is almost
certainly this — no repository literally named "Scroll-Word" exists;
`scroll-world` is the real, well-known match (Higgsfield-powered,
scroll-scrubbed 3D landing pages — exactly the concept described).
Inspected live via the real README, repo tree, and `SKILL.md` — not
assumed. This is the audit the build prompt itself requires before any
implementation ("First inspect the actual Scroll-Word GitHub repository.
DO NOT assume its APIs.").

## 1. What it actually is

**Not a JavaScript 3D engine or camera-rig library you `npm install` into
a React app.** It's a **Claude Code skill** (`.claude-plugin/`,
`skills/scroll-world/SKILL.md`) — a procedure an agent *executes*, once,
to produce one fixed landing page. The 8-step procedure: bootstrap tools
→ interview the user → generate stills (AI images) → optionally float
scenes → pick a camera architecture → render connector clips → encode
for scrubbing → assemble + QA.

**The output is pre-rendered video, not live 3D.** Each "scene" is an AI
image generated once (Higgsfield's GPT Image 2, or Codex if available);
each "dive" and "connector" between scenes is an AI-generated video clip
(Monid's `seedance_2_0`/`kling3_0`, or Higgsfield credits as fallback).
The scroll engine (`scrub-engine.js`, framework-agnostic vanilla JS)
never renders 3D geometry at runtime — it plays a chain of `.mp4` clips
and seeks through them via `video.currentTime`, driven by scroll
position. Scroll position maps to *playback time in a fixed video*, the
same technique Apple's product pages use.

**Real cost, real human approval, baked in.** Step 1's interview
requires a **budget approval** before any rendering happens (video tier,
backend, stills source) — "~N image gens + ~2N-1 video gens" per the
README, doubled for a mobile chain. This is a real, metered AI-generation
cost per scene, not a one-time library install.

**Scenes are fixed at generation time.** The engine's config
(`mountScrollWorld(el, { sections: [...], connectors: [...] })`) is a
static array set once during assembly — `{id, label, still, clip,
scroll, linger, title, body, tags}` per section, 5–7 sections per the
interview's own guidance. There is no schema field, hook, or runtime API
for injecting live application data into a scene.

## 2. The load-bearing mismatch with the build prompt

The build prompt's acceptance criteria (§37) and its most emphasized
sections (§7 Agent Discovery, §12 Graphify Search, §18-19 Policy/Approval,
§21-23 Talk-Back, §26 World Map) all require the 3D world to react, at
runtime, to arbitrary live input: a real Agent Registry search
highlighting the matching agents out of 254 real records, a chat command
("show me the finance agents") moving the camera to an *arbitrary* point
the pre-render never anticipated, a live execution trace animating as it
actually happens, an [APPROVE]/[REJECT] button that actually calls
`POST /v1/approvals/{id}/approve`.

**None of that is representable in scroll-world's model.** Its only
runtime input is scroll position, mapped onto a video timeline that was
finished rendering before the page ever loaded. It cannot:

- highlight a *subset* of agents chosen by a real, data-dependent search
  result (the "agents" in the video are pixels in a diorama image, not
  addressable objects)
- move the camera to a point selected by free-text chat input (camera
  paths are baked into specific rendered clips, chosen during the
  8-step procedure, not computed at runtime)
- reflect a live execution trace, a live approval queue, or any other
  state that changes after the video was rendered
- regenerate itself when the underlying data changes (254 agents,
  89 executions, 16 pending approvals) without a human re-running the
  entire interview-and-render procedure and paying for new clips

This isn't a performance-tuning problem (§27's instancing/LOD/lazy-load
guidance) — it's that the tool's fundamental capability (a fixed,
pre-rendered cinematic sequence) and the spec's fundamental requirement
(a live, interactive, data-bound operations console) are two different
kinds of software.

## 3. What scroll-world is genuinely good for here

Its actual sweet spot matches §4 (World Entry) closely: a cinematic,
non-interactive "flying into the Axiom facility" opening sequence with
the wordmark and tagline, built once, that plays the same way every
time. That's exactly an Apple-product-page-style intro — real value, and
the one place in the spec where "fixed pre-rendered narrative" is
actually the right tool, not a compromise.

## 4. Recommendation (not yet built — needs a decision before Phase 2)

Two honest paths, not a false choice hidden behind one silently-built
answer:

- **(a) Cinematic wrapper + real interactive core.** Use scroll-world
  only for a fixed intro sequence (§4) and the between-zone cinematic
  transitions as non-interactive backdrop; build the actual operational
  surface — agent discovery, live execution graph, talk-back chat, human
  approval — with a genuinely interactive 3D stack (react-three-fiber /
  Three.js) wired to the real Axiom API, matching every one of §37's
  acceptance criteria for real. This means most of the spec (§5-23,
  §26, §34-35) is built *without* scroll-world, contrary to "use the
  existing Scroll-Word architecture wherever appropriate" — because
  where appropriate turns out to be narrow (one intro sequence).
- **(b) Skip scroll-world entirely.** Build the whole interface with an
  interactive 3D stack from the start, including the entry sequence as a
  real (if simpler) camera animation instead of pre-rendered video. Less
  cinematic polish on the intro, but one consistent, live, data-bound
  system throughout — no real-money Higgsfield/Monid spend, no fixed
  video assets to regenerate every time agent data changes.

Either path is a genuinely large build (react-three-fiber scene graph,
camera state machine, a chat-to-camera command parser, live data binding
to the real 254-agent registry / 89-execution trace / 16-approval
queue) — realistically many hours of real engineering, not a single-pass
build, and CLAUDE.md §56/§57 rule out silently shipping mock data dressed
up as live. Recommend (b) unless the cinematic intro is specifically
wanted enough to justify real Higgsfield/Monid spend and a human budget
approval for it — surfacing that choice explicitly rather than assuming
it.
