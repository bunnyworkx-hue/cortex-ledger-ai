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
delegation semantics before Cortex Ledger AI builds an Agent Gateway around it. Grep
across the source confirms `delegate_task` is a real, implemented concept,
touched by `toolsets.py`, `run_agent.py`, `cli.py`, `model_tools.py`,
`hermes_state.py`, and dedicated modules `tools/async_delegation.py` and
`tools/delegation_live_log.py`. The README independently confirms this at
the feature level: "Spawn isolated subagents for parallel workstreams.
Write Python scripts that call tools via RPC, collapsing multi-step
pipelines into zero-context-cost turns." This is the real hook the Cortex Ledger AI
Hermes Adapter (`packages/axiom-hermes/`) should call through — not
something Cortex Ledger AI needs to build itself.

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
Cortex Ledger AI has to invent from scratch — the Cortex Ledger AI Tool Registry's
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
  — Docker/Singularity/Modal/Daytona give Cortex Ledger AI a real sandboxing option to
  point at, rather than building container isolation itself.
- §2.3 **Credential scoping**
- §2.4 **In-process heuristics**
- §2.5 **Plugin trust model** — directly relevant since the
  `agency-agents-router` plugin (and any future Cortex Ledger AI-authored plugin)
  runs inside this exact trust boundary.
- §2.6 **External surfaces**
- §3 explicitly scopes what is/isn't covered by Hermes's own security
  posture.

This means Cortex Ledger AI's "Hermes must never receive unrestricted access"
requirement (`CLAUDE.md` §12, §56) is enforceable on two layers: Cortex Ledger AI's
own gateway (which is Cortex Ledger AI's responsibility to build), and Hermes's native
plugin trust model + terminal isolation (which already exists and can be
configured rather than reimplemented).

## 8. State management

Hermes has substantial native state handling: `hermes_state.py` (666KB),
`hermes_state_common.py`, `hermes_state_portability.py`,
`hermes_state_schema.py`, `hermes_state_search.py` (115KB, FTS5-backed
search per the README's "session search" feature). This is Hermes's own
session/memory persistence — separate from, and not a substitute for,
Cortex Ledger AI Memory (`CLAUDE.md` §38, §24). The two must stay distinct per the
doc's own instruction; Cortex Ledger AI should not attempt to read/write Hermes's
internal state files directly, only interact with Hermes through its CLI/
API/plugin surface.

## 9. What was not verified (as of the original audit)

The original pass (Milestone 2) read the README, file layout, and grepped
source for keywords. It did not install Hermes or run it. That gap is
closed — see §10.

## 10. Milestone 13 — real install and live integration

Installed for real via `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`,
not simulated. Two real problems hit and fixed along the way, neither
anticipated by the original audit:

1. **The installer hung indefinitely on `--skip-setup` alone.** Root
   cause, found by reading the installer script after 17+ minutes of
   zero CPU / zero child processes: `--skip-setup` only skips the
   *setup wizard* stage. A separate `prompt_yes_no()` confirmation
   (unrelated to setup, e.g. optional package choices) falls through to
   reading `/dev/tty` directly — bypassing stdin redirection entirely —
   whenever a real controlling terminal is attached but no `NON_INTERACTIVE`
   flag was set, hanging forever with no one to answer it. Fixed by
   passing both `--skip-setup --non-interactive` (a separate flag,
   confirmed in the script's own `--help`). A `kill -9` on the parent
   bash process during the first hung attempt did **not** kill its
   detached Homebrew grandchild (a `cmake`-from-source compile, needed
   because this test machine's macOS 12 has no prebuilt Homebrew bottle
   for ripgrep's dependency chain) — it kept running independently and
   later collided with the second install attempt's own `brew install
   ripgrep` via a stale lock. The installer's own retry logic handled
   that collision gracefully (logged a warning, moved on) — real,
   working resilience on Hermes's side, not something Cortex Ledger AI had to work
   around.
2. **`auto` provider detection did not pick Anthropic even with
   `ANTHROPIC_API_KEY` set** — a first live one-shot call
   (`hermes -z "..." -m anthropic/claude-sonnet-5`) failed with
   `No usable credentials found for provider 'gmi'. Set GMI_API_KEY.`
   despite `"anthropic"` being an explicitly documented provider in
   `~/.hermes/config.yaml` requiring only `ANTHROPIC_API_KEY`. Fixed by
   passing `--provider anthropic` explicitly — `axiom_hermes.HermesBackend`
   always passes it, never relies on `auto`.

Once both were fixed, the real one-shot invocation is:

```bash
hermes -z "<prompt>" -m anthropic/claude-sonnet-5 --provider anthropic --usage-file <path>
```

`-z`/`--oneshot` (found live in `hermes --help`, not in the earlier
source read — the installed CLI's flag surface differs from what
`cli.py`'s `fire`-based signature suggested) prints only the final
response text to stdout: no banner, no spinner, no session-id line —
exactly the clean, scriptable surface `axiom_hermes.client.run_oneshot`
needed. `--usage-file` writes a real JSON report (cost, token counts,
model, provider, `completed`/`failed`/`failure`) **even on failure**,
which is how `axiom_hermes` distinguishes a real failure from a
successful empty response, rather than trusting the exit code alone.

Verified live end-to-end through the full Cortex Ledger AI stack: `POST
/v1/agent-fabric/agents/marketing/marketing-seo-specialist/delegate`
with `"backend": "hermes"` returned a real, in-character completion from
the SEO Specialist agent, routed through Registry → `HermesBackend` →
real `hermes` subprocess → real Anthropic API call → `Execution`. First
call cost $0.06 / 23,941 tokens (a real usage report), dominated by
Hermes's own tool-definition cache write on cold start — subsequent
calls would hit that cache.

**What Milestone 13 did *not* build**: Hermes's own subagent delegation
(`delegate_task`, confirmed real in §4) is Hermes deciding internally to
spawn its own subagents — it is not the same thing as Cortex Ledger AI calling
Hermes. `HermesBackend` is one full one-shot Hermes run per Cortex Ledger AI
`Execution` (CLAUDE.md §30's `HermesBackend`); it does not yet reach into
Hermes's internal delegation, MCP server mode (`mcp_serve.py`), or
gateway/messaging surfaces — those remain real, unexplored surface for a
future milestone, not fabricated capabilities being claimed here.
