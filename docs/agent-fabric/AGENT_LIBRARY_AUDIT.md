# Milestone 3 — Agent Library Audit

Source: `~/Desktop/agency-agents`, a git-tracked clone of
`https://github.com/msitarzewski/agency-agents` ("The Agency"). License:
MIT.

## 1. Where and what

Not a private/custom library — a real, public, actively maintained open
source project. Its own README describes it in almost the same language
`CLAUDE.md`'s example categories use (Marketing, Finance, Frontend
Developer, Reddit Community Builder, Whimsy Injector, Reality Checker are
all real agents in this repo, not hypothetical examples). This is the
library `CLAUDE.md` §6 refers to as "the existing agency agent library."

## 2. Format

Every agent is a single Markdown file with YAML frontmatter + a long-form
prose system prompt body. Real example
(`engineering/engineering-frontend-developer.md`):

```yaml
---
name: Frontend Developer
description: Expert frontend developer specializing in modern web technologies, React/Vue/Angular frameworks, UI implementation, and performance optimization
color: cyan
emoji: 🖥️
vibe: Builds responsive, accessible web apps with pixel-perfect precision.
---
```

followed by sections like "Your Identity & Memory," "Your Core Mission,"
etc. — persona and workflow guidance, not structured capability/tool/
permission metadata.

**Gap versus `CLAUDE.md` §8's proposed registry schema:** the source
frontmatter has no `capabilities`, `tools`, `permissions`, `risk_level`,
`budget`, or `backend` fields. Cortex Ledger AI's normalization pipeline
(`CLAUDE.md` §67, Milestone 5) will have to *derive* capability tags from
the `description` field and prose body (or curate them by hand for the
first cohort), not simply parse them out of existing structured fields.
This is real, non-trivial work — flag it now so Milestone 5 doesn't assume
a 1:1 field mapping exists.

## 3. Count — corrected

`CLAUDE.md` assumes "approximately 237." Actual count, tallied directly
from the filesystem across the 17 real divisions (excluding `strategy/`,
which `divisions.json` itself documents as playbooks/runbooks with no
agent frontmatter, and excluding `integrations/`, `examples/`, `scripts/`,
which are tooling, not agents):

| Division | Count |
|---|---|
| engineering | 58 |
| specialized | 57 |
| marketing | 36 |
| gis | 13 |
| security | 12 |
| design | 10 |
| sales | 9 |
| testing | 9 |
| paid-media | 7 |
| project-management | 7 |
| academic | 6 |
| game-development | 6 |
| spatial-computing | 6 |
| support | 6 |
| finance | 5 |
| product | 5 |
| healthcare | 3 |
| **Total** | **255** |

The repo's own `integrations/hermes/README.md` reports "Generated agent
count: 270" — that number is produced by `scripts/convert.sh` when it
generates per-tool bundles and appears to include generated variants
(e.g. tool-specific reformattings), not a second count of source files.
**Use 255 as the source-of-truth count of real agent definitions; use "270
generated" only when specifically talking about `agency-agents-router`'s
output.** Neither number is 237 — the CLAUDE.md's figure is stale and
should not be hardcoded anywhere in Cortex Ledger AI.

## 4. Categories (source of truth: `divisions.json`)

`divisions.json` is explicitly documented in the repo as the canonical
division list, enforced by CI (`scripts/check-divisions.sh`) against both
the actual directories on disk and the `AGENT_DIRS` arrays in
`scripts/convert.sh`/`scripts/lint-agents.sh`. Cortex Ledger AI's category taxonomy
for the Agent Registry should import this file directly rather than
re-deriving categories by hand — it's already the enforced source of truth
upstream, including display label, icon, and brand color per division,
which the Cortex Ledger AI dashboard (§52) can reuse as-is.

## 5. Existing tool integrations (relevant prior art)

`agency-agents/scripts/convert.sh` and `scripts/install.sh` already
generate and install per-tool bundles for: Claude Code, Cursor, Codex,
Gemini CLI, GitHub Copilot, OpenCode, Windsurf, Aider, Kimi, Osaurus,
Antigravity, OpenClaw, Qwen, Hermes, and Mistral Vibe (`integrations/`
has one subdirectory per tool). The Hermes bundle specifically
(`integrations/hermes/`) is the most relevant prior art for Cortex Ledger AI's own
Agent Invocation Gateway: it deliberately avoids preloading all agents as
static skills, instead exposing four narrow tools —
`agency_agents_search`, `agency_agents_inspect`, `agency_agents_load`,
`agency_agents_delegate` — that search/inspect/compose/delegate to one
specialist at a time. This is a working implementation of exactly the
"Lazy Agent Discovery" workflow `CLAUDE.md` §9 specifies conceptually
(search → registry → top candidates → load → execute). The Cortex Ledger AI Agent
Router/Invocation Gateway (Milestones 9–10) should treat this plugin as a
reference implementation to adapt, not a novel design to invent from
scratch.

## 6. Dependencies / duplicates / incomplete agents

Not exhaustively checked in this pass — the repo has CI
(`.github/workflows`, `scripts/lint-agents.sh`,
`scripts/check-divisions.sh`) that already enforces frontmatter
completeness and division consistency, so gross structural problems (a
missing `name`/`description`, a division not in `divisions.json`) are
unlikely to have slipped through on `main`. What has *not* been checked:
semantic duplicates (two agents with overlapping capability descriptions
that Cortex Ledger AI's router would have trouble disambiguating between) and how
much each agent's prose body actually varies. That analysis belongs in the
normalization pipeline itself (Milestone 5), where each agent gets
processed anyway.

## 7. Preservation requirement

Per `CLAUDE.md` §67 ("preserve original definitions... do not destroy
source information") and §57, the normalization pipeline must treat these
255 files as read-only source-of-truth and write *derived* Cortex Ledger AI registry
records elsewhere (e.g. `agents/registry/` in this repo, per the layout in
§53) rather than editing or forking the upstream `agency-agents` files in
place. That also means picking up upstream updates (new agents, edited
personas) by re-running normalization against `agency-agents`, not by
hand-maintaining a divergent copy.

## 8. Milestone 10 — live registry load results

Ran for real against the actual repo (commit `ebe9c99a`), not simulated:

- **254/255 agents loaded**, one skipped and logged:
  `engineering/engineering-developer-tooling-engineer.md` has an
  unquoted `description:` containing a bare `": "` ("...with great DX:
  intuitive command design...") — invalid plain-scalar YAML under strict
  parsing (`yaml.safe_load`). This is a genuine quirk in the real source
  file, not a parsing bug on Cortex Ledger AI's side; the fix was resilience, not a
  workaround — `axiom_agent_fabric.normalize` skips and logs a single
  malformed file rather than failing the whole registry load (one bad
  file in 255 must not take down the whole Agent Fabric). Division
  counts in §3 above are unaffected as a source-of-truth (still 255 real
  files); the live registry's `engineering` count is 57 instead of 58
  because of this one skip.
- **17/255 agents (~7%) have a real `tools:` frontmatter field**
  (comma-separated, e.g. `WebFetch, WebSearch, Read, Write, Edit` on
  `marketing-seo-specialist.md`) — a partial exception to §2's "no
  structured metadata" finding. The mechanical pass now captures these
  as `frontmatter_tools`, separate from curated `capabilities`/
  `permissions`, which the vast majority of agents (238/255) still lack.
- **12-agent curated cohort** (`axiom_agent_fabric.curated`), spanning 10
  divisions, hand-tagged from each agent's real description — verified
  live via `/v1/agent-fabric/agents/security/security-appsec-engineer/
  delegate`, which returned a real, in-character Anthropic completion
  from the actual Application Security Engineer persona.
