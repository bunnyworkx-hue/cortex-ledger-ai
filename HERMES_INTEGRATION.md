# Hermes Integration

Portfolio summary — the full research + install trail (real bugs found
and fixed, not a clean-room writeup) is `docs/hermes/HERMES_INTEGRATION.md`.

## What Hermes is

[Hermes Agent](https://github.com/NousResearch/hermes-agent) (Nous
Research, MIT) is a real, large, actively developed self-hosted
general-purpose AI agent — not a thin wrapper. It has its own CLI/TUI,
messaging gateway, plugin system, session state/search, and provider-
agnostic model routing. Cortex Ledger AI treats it as one of two real `AgentBackend`
implementations (`packages/axiom-hermes`), alongside Cortex Ledger AI's own native
Anthropic-backed path (`AxiomNativeBackend`).

## How Cortex Ledger AI talks to it

One full one-shot Hermes run per Cortex Ledger AI `Execution` — a real subprocess
call, never a shell:

```bash
hermes -z "<prompt>" -m anthropic/claude-sonnet-5 --provider anthropic --usage-file <path>
```

`-z`/`--oneshot` prints only the final response text — no banner, no
spinner — exactly the clean, scriptable surface `axiom_hermes.client.run_oneshot`
needs. `--usage-file` writes a real JSON report (cost, tokens, model,
`completed`/`failed`) even on failure, which is how Cortex Ledger AI distinguishes a
real failure from a successful-but-empty response, rather than trusting
the exit code alone.

## Install

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup --non-interactive
```

Both flags matter. `--skip-setup` alone leaves a separate confirmation
prompt that reads `/dev/tty` directly and hangs forever in a
non-interactive shell — a real bug hit during Milestone 13, root-caused
by reading the installer script itself (see the full audit for the
17-minute debugging trail). `AXIOM_HERMES_BIN` should point at the
installed binary (`~/.local/bin/hermes` by default) if it isn't already
on the API process's `PATH`.

## Real gotcha: provider auto-detection

Hermes's `auto` provider selection did **not** pick Anthropic even with
`ANTHROPIC_API_KEY` set — a live one-shot call failed with `No usable
credentials found for provider 'gmi'`. Fixed by always passing
`--provider anthropic` explicitly; `HermesBackend` never relies on
`auto`.

## What's real vs. what isn't built yet

**Real and verified live**: `POST /v1/agent-fabric/agents/{id}/delegate`
with `"backend": "hermes"` routes through `AgentRegistry` →
`HermesBackend` → a real `hermes` subprocess → a real Anthropic API call
→ a real `Execution` record. First live call: $0.06 / 23,941 tokens (a
real usage report, dominated by Hermes's own cold-start tool-cache
write).

**Not built**: Hermes's own internal subagent delegation
(`delegate_task` — Hermes deciding to spawn its own subagents) is a real,
separate feature this integration does not reach into. `HermesBackend` is
one full run per Cortex Ledger AI `Execution`; Hermes's MCP server mode
(`mcp_serve.py`) and gateway/messaging surfaces are real, unexplored
surface for a future milestone — not fabricated capabilities being
claimed here.
