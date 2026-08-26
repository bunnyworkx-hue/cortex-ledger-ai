# Milestone 2 — Hermes Research

Source: `https://github.com/NousResearch/hermes-agent` (cloned shallow for
inspection; not vendored into this repo). Built by Nous Research. License:
**MIT**.

## 1. What it actually is

Hermes Agent is a real, actively developed, self-hosted general-purpose AI
agent — much closer to "Claude Code" or "OpenClaw" in scope than to a
narrow task-runner. It is not a thin wrapper; it's a large project (155
files under `agent/`, 218 under `hermes_cli/`, 65 under `gateway/`, its own
web UI, TUI, and messaging gateway).

Its own pitch: a self-improving agent with a persistent learning loop
(creates and refines its own skills from experience, periodic memory
nudges, cross-session FTS5 conversation search, `Honcho`-based user
modeling). It runs from a CLI/TUI, or as a always-on gateway process bridged
to Telegram/Discord/Slack/WhatsApp/Signal/Email. Provider-agnostic: OpenAI,
OpenRouter, Nous Portal, or any custom endpoint, switchable with
`hermes model` — no code changes.

## 2. Relationship to the "Hermes" agency-agents already integrates with

`~/Desktop/agency-agents/integrations/hermes/README.md` describes a
generated plugin (`agency-agents-router`) that installs to
`${HERMES_HOME:-~/.hermes}/plugins/agency-agents-router` and is enabled via
`plugins.enabled` in "the Hermes config." That plugin directory convention,
the `~/.hermes` home, and the `hermes` CLI name all match this repo
exactly — **this is the same Hermes**, not a different, lighter-weight
tool. The agency-agents plugin is one small consumer of Hermes's plugin
system (`plugins/` — 23 real subdirectories including `browser`,
`memory`, `model-providers`, `observability`, `security-guidance`), not a
description of the whole runtime. Earlier framing in this project's
planning that treated "Hermes" as necessarily a thin CLI-tool integration
was based on only having seen the plugin's README, not the runtime itself
— corrected now that the runtime has been inspected directly.

## 3. Installation / runtime

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash   # macOS/Linux/WSL2/Termux
# or PowerShell one-liner for native Windows
```

Installer provisions `uv`, Python 3.11, Node.js, ripgrep, ffmpeg, and (on
Windows) a portable Git Bash. Config lives under `~/.hermes` (Linux/macOS)
or `%LOCALAPPDATA%\hermes` (native Windows).

CLI entry points confirmed from the README: `hermes`, `hermes model`,
`hermes tools`, `hermes config set/get`, `hermes gateway`, `hermes setup`,
`hermes claw migrate`, `hermes update`, `hermes doctor`.

## 4. Delegation / subagents — real, not assumed

`CLAUDE.md` §28 requires "first-class external agent runtime" with real
delegation semantics before Axiom builds an Agent Gateway around it. Grep
across the source confirms `delegate_task` is a real, implemented concept,
touched by `toolsets.py`, `run_agent.py`, `cli.py`, `model_tools.py`,
`hermes_state.py`, and dedicated modules `tools/async_delegation.py` and
`tools/delegation_live_log.py`. The README independently confirms this at
the feature level: "Spawn isolated subagents for parallel workstreams.
Write Python scripts that call tools via RPC, collapsing multi-step
pipelines into zero-context-cost turns." This is the real hook the Axiom
Hermes Adapter (`packages/axiom-hermes/`) should call through — not
something Axiom needs to build itself.

## 5. Tool access model — maps directly onto CLAUDE.md's Tool Access Control

`toolsets.py` implements exactly the kind of named, composable tool
grouping `CLAUDE.md` §32 describes conceptually. Real example from the
source: a shared `_HERMES_CORE_TOOLS` list (web, terminal/process,
file read/write/patch/search, vision, image generation, skills,
full browser automation, TTS, todo/memory) that different platforms/toolsets
compose and restrict from — including a documented, deliberate exclusion
(`desktop_ui` tools are withheld from non-GUI sessions, gated on the actual
session source rather than an env var, per an inline `NOTE:` in the code).
This is a real precedent for permission-scoped tool grants, not something
Axiom has to invent from scratch — the Axiom Tool Registry's
per-agent/per-backend tool grants (§31–32) can borrow this toolset
composition model directly.

## 6. MCP support — real, both directions worth checking further

README confirms Hermes can act as an **MCP client** ("Connect any MCP
server for extended capabilities" — this is exactly what would let a Hermes
session reach Graphify's MCP server directly). The repo also ships
`mcp_serve.py` at the root and an `optional-mcps/` directory (67 entries),
suggesting Hermes can also expose its own capabilities as an MCP server.
Neither direction was exercised live in this audit — confirm the exact
tool schema Hermes exposes/consumes before Milestone 13 wiring.

## 7. Security / trust model — real and directly relevant to CLAUDE.md §46–47

`SECURITY.md` (15.7KB, not a placeholder) documents an actual trust model,
not just a vulnerability-reporting address:
- §2.2 **OS-level isolation boundary** — covers both "terminal-backend
  isolation" and "whole-process wrapping" as two distinct isolation
  strategies. Hermes explicitly supports seven terminal backends (local,
  Docker, SSH, Singularity, Modal, Daytona, Vercel Sandbox per the README)
  — Docker/Singularity/Modal/Daytona give Axiom a real sandboxing option to
  point at, rather than building container isolation itself.
- §2.3 **Credential scoping**
- §2.4 **In-process heuristics**
- §2.5 **Plugin trust model** — directly relevant since the
  `agency-agents-router` plugin (and any future Axiom-authored plugin)
  runs inside this exact trust boundary.
- §2.6 **External surfaces**
- §3 explicitly scopes what is/isn't covered by Hermes's own security
  posture.

This means Axiom's "Hermes must never receive unrestricted access"
requirement (`CLAUDE.md` §12, §56) is enforceable on two layers: Axiom's
own gateway (which is Axiom's responsibility to build), and Hermes's native
plugin trust model + terminal isolation (which already exists and can be
configured rather than reimplemented).

## 8. State management

Hermes has substantial native state handling: `hermes_state.py` (666KB),
`hermes_state_common.py`, `hermes_state_portability.py`,
`hermes_state_schema.py`, `hermes_state_search.py` (115KB, FTS5-backed
search per the README's "session search" feature). This is Hermes's own
session/memory persistence — separate from, and not a substitute for,
Axiom Memory (`CLAUDE.md` §38, §24). The two must stay distinct per the
doc's own instruction; Axiom should not attempt to read/write Hermes's
internal state files directly, only interact with Hermes through its CLI/
API/plugin surface.

## 9. What was not verified

This audit read the README, top-level file/directory layout, `SECURITY.md`
section headers, and grepped for `delegate_task`/MCP keywords across the
source. It did **not** install Hermes, start a session, actually invoke
`delegate_task`, start `mcp_serve.py` and inspect its live tool schema, or
read `hermes_state_schema.py`/`toolsets.py` in full. Before Milestone 13
(Hermes Integration) claims this works, it must be installed, run, and the
Axiom Agent Gateway → Hermes → Agent Fabric round trip exercised for real
against a live `hermes` process — per `CLAUDE.md` §56/§57.
