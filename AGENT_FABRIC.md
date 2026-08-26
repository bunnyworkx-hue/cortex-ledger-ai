# Agent Fabric

Portfolio summary — the full audit (real counts, real division breakdown,
real gaps found while normalizing) is
`docs/agent-fabric/AGENT_LIBRARY_AUDIT.md`.

## Source

[`agency-agents`](https://github.com/msitarzewski/agency-agents) ("The
Agency"), MIT — a real, public, actively maintained persona library, not
a private/custom set. Each agent is one Markdown file: YAML frontmatter
(`name`, `description`, `color`, `emoji`, `vibe`) plus a long-form prose
system prompt body. Most agents have no structured `capabilities`/
`tools`/`permissions`/`risk_level`/`budget` fields — that metadata had to
be derived or hand-curated, not parsed out of an existing schema.

## Real count — corrected from CLAUDE.md's assumption

CLAUDE.md assumed "approximately 237." The real, filesystem-tallied count
across 17 divisions is **255** real agent definitions (`divisions.json`
is the enforced, canonical division list upstream — Axiom imports it
rather than re-deriving categories by hand).

| Division | Count | Division | Count |
|---|---|---|---|
| engineering | 58 | testing | 9 |
| specialized | 57 | paid-media | 7 |
| marketing | 36 | project-management | 7 |
| gis | 13 | academic | 6 |
| security | 12 | game-development | 6 |
| design | 10 | spatial-computing | 6 |
| sales | 9 | support | 6 |
| finance | 5 | product | 5 |
| healthcare | 3 | **Total** | **255** |

## Live registry load

254/255 loaded at runtime — one skipped and logged, not silently dropped:
`engineering-developer-tooling-engineer.md` has invalid plain-scalar YAML
in its `description` field (an unquoted `": "`), a genuine quirk in the
real upstream source. `axiom_agent_fabric.normalize` treats one malformed
file as a skip-and-log event, not a fatal error for the other 254.

17/255 agents (~7%) carry a real `tools:` frontmatter field, captured
separately as `frontmatter_tools` from Axiom's own curated
`capabilities`/`permissions`.

## Curation

A 12-agent curated cohort spans 10 divisions, hand-tagged with
`capabilities`/`permissions`/`risk_level` from each agent's real
description — this is the set of agents CLAUDE.md's demos and the
evaluation benchmark actually exercise. The other ~242 agents are
discoverable and loaded but not yet individually risk-tagged; extending
curation to the full library is future work, not something quietly
assumed done.

## How Axiom invokes them

`AgentInvocationGateway` (`packages/axiom-agent-fabric/axiom_agent_fabric/gateway.py`)
looks an agent up by id, picks a backend (`axiom_native` by default, or
`hermes`), runs the task, and persists both a real `MemoryRecord` and a
real `ExecutionRow` for every invocation — verified live via
`POST /v1/agent-fabric/agents/security/security-appsec-engineer/delegate`,
which returned a genuine, in-character Anthropic completion from the real
Application Security Engineer persona.

## Preservation

Per CLAUDE.md §67/§57, the 255 source files are treated as read-only —
Axiom's registry writes derived records, it never edits or forks
`agency-agents` in place. Picking up upstream changes means re-running
normalization, not hand-maintaining a divergent copy.
