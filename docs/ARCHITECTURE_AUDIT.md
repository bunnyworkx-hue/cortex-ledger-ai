# Milestone 0 — Repository Audit

Status: complete. No application code has been written yet.

## 1. What exists today

Cortex Ledger AI does not exist yet. This audit inventories the real, pre-existing
pieces on this machine that Cortex Ledger AI is meant to wrap, per `CLAUDE.md`.

| Component | Location | State |
|---|---|---|
| Cortex Ledger AI itself | `~/Desktop/axiom-os` (this repo) | Freshly initialized, empty except docs |
| Candidate 237-agent library | `~/Desktop/agency-agents` | Real, git-tracked clone of `github.com/msitarzewski/agency-agents` |
| Graphify (Knowledge Fabric candidate) | `github.com/Graphify-Labs/graphify` (cloned for inspection, not vendored) | Real, active, Apache-2.0 |
| Hermes (Execution Engine candidate) | `github.com/NousResearch/hermes-agent` (cloned for inspection, not vendored) | Real, active, MIT |
| Business Operations | `~/Desktop/ORVYN-V3` | Real, early-stage Next.js + Supabase app (auth + shift-claim MVP) |

Two unrelated projects also live on this Desktop and were checked and ruled
out during discovery: `workx-ai-label-sim` (an AI record-label game
simulator with its own unrelated "Agent Architecture" doc) and `OpenMontage`
(a video-montage tool with its own unrelated `AGENTS.md`). Neither is part
of Cortex Ledger AI.

## 2. Environment

- Python: repo-local `.python-version`/`pyproject.toml` present in both
  Graphify and Hermes Agent (both target modern CPython 3.10+/3.11+; exact
  pin not re-verified against the machine's installed interpreter yet).
- Node: Hermes Agent ships `.nvmrc`, `package.json`, `package-lock.json` —
  it has a real JS/TS surface (web UI, TUI gateway) alongside its Python
  core.
- Package managers in play: `uv` (both Graphify and Hermes Agent use
  `uv.lock`), `npm` (Hermes Agent's JS side).
- Database: nothing provisioned yet for Cortex Ledger AI. ORVYN-V3 already runs on
  Supabase (Postgres) — see `~/Desktop/ORVYN-V3/supabase/schema.sql`.
- Git: `agency-agents`, Graphify, and Hermes Agent are each independent git
  repos with their own remotes. Cortex Ledger AI is a new, separate repo — it does
  not vendor or submodule the other three; it will integrate with them as
  external dependencies/adapters per `CLAUDE.md` §20/§29.

## 3. Corrections to CLAUDE.md's assumptions

`CLAUDE.md` repeatedly says "do not assume, inspect first." Here is what the
inspection actually found that differs from the doc's working assumptions:

1. **Agent count.** The doc assumes "approximately 237" agents. The real
   `agency-agents` repo currently defines **~255 frontmatter agent files**
   across 17 divisions (see `docs/agent-fabric/AGENT_LIBRARY_AUDIT.md` for
   the exact breakdown), and its own tooling reports **270** when it
   generates per-tool integration bundles (that number includes generated
   variants, not just source files). Treat "237" as stale; use the live
   count from the source repo, not a hardcoded constant, anywhere Cortex Ledger AI
   reports agent totals.
2. **Graphify's citation was broken.** The version of `CLAUDE.md` handed to
   Claude Code had `:contentReference[oaicite:1]{index=1}` placeholders
   instead of a real Graphify URL — an artifact of citation stripping from
   whatever tool produced the doc. The user supplied the real URL directly:
   `https://github.com/Graphify-Labs/graphify`. Full findings in
   `docs/graphify/GRAPHIFY_AUDIT.md`.
3. **"Hermes" is ambiguous across two different things.** `agency-agents`
   ships a lightweight integration for a tool it also calls "Hermes"
   (`agency-agents/integrations/hermes/`), which installs a small
   router *plugin* into a Hermes install — it is not itself the runtime.
   The user confirmed the actual runtime is Nous Research's
   `hermes-agent` (`https://github.com/NousResearch/hermes-agent`), which
   is the same tool `agency-agents`'s plugin targets (same name, same
   `hermes` CLI, same plugin directory convention) — so the two findings
   are consistent, not competing. Full findings in
   `docs/hermes/HERMES_INTEGRATION.md`.
4. **Business Operations already exists.** `CLAUDE.md` §99 frames Business Operations as something to
   build *after* Cortex Ledger AI is stable, on top of it. In reality `ORVYN-V3`
   already exists as a working (if early) prototype with its own auth,
   Supabase schema, and realtime shift-claim logic, built independently of
   Cortex Ledger AI. This audit does not change the roadmap ordering (Cortex Ledger AI first,
   per explicit user instruction), but the eventual Business Operations integration will
   be "retrofit an existing app onto Cortex Ledger AI," not "build Business Operations fresh on top
   of Cortex Ledger AI" — worth remembering when Project 2 starts.

## 4. Scope of this audit

This pass inspected repo structure, README/docs, license files, entry
points (`pyproject.toml` scripts, `package.json`), top-level module layout,
and targeted greps for MCP/delegation/security-model keywords in both
Graphify and Hermes Agent. It did **not** install either tool, run their
CLIs, or read their source line-by-line — that level of verification
belongs to the implementation milestones that actually integrate each
system (Milestones 7–8 for Graphify, Milestone 13 for Hermes), where
integration code will be tested against the real running tools before any
claim of "it works" is made, per `CLAUDE.md` §56/§57.
