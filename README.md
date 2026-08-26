# Axiom OS

Agentic AI operating system — Agent Fabric, Knowledge Fabric, Execution
Engine. See `CLAUDE.md` for the full architecture and engineering rules,
and `docs/` for the audits and implementation plan behind every design
decision here.

## Status

Milestones 6–17 done: Foundation, Model Gateway, Knowledge Gateway, Agent
Runtime, Agent Fabric (a real registry over `agency-agents`, 254/255
agents + a 12-agent curated cohort), Tool Registry + MCP, Hermes
Integration, Memory (`/v1/memory`), Policy + Human Approval
(`/v1/approvals`, gating a real `modify_business_record` demo tool),
Observability (`/v1/observability/executions` and `/metrics` — a real
`executions` table recording every Task → Backend → Result run, success
or failure, with real token usage/cost/duration; not the same thing as
`memories`, which only records successful task content). See
`docs/IMPLEMENTATION_PLAN.md` for what's next (Dashboard, Evaluation,
Security).

## Layout

```
apps/api/                FastAPI app — the Axiom control-plane HTTP surface
packages/axiom-core/      config, logging, Model/Knowledge/Tool Registry abstractions, Agent Runtime
packages/axiom-db/        async SQLAlchemy engine, ORM base, Alembic migrations
packages/axiom-anthropic/ real Anthropic adapter (Model Gateway)
packages/axiom-graphify/  real Graphify MCP adapter (Knowledge Gateway)
packages/axiom-agent-fabric/ real agent registry + invocation gateway over agency-agents
packages/axiom-mcp/       generic MCP client + Tool Registry integration
packages/axiom-hermes/    real Hermes Agent CLI adapter (AgentBackend)
tests/                    unit + integration tests
docs/                     audits (Graphify, Hermes, agent library) + architecture plan
var/                      generated artifacts (graphify-out/graph.json, ...) — gitignored
```

All packages are one `uv` workspace — see `pyproject.toml`.

## Setup

```bash
cp .env.example .env   # fill in AXIOM_DATABASE_URL, AXIOM_ANTHROPIC_API_KEY, etc.
uv sync --all-packages # installs the whole workspace + dev deps
uv run pytest          # or: ./scripts/dev/test.sh
./scripts/dev/run.sh   # starts the API with reload
curl http://127.0.0.1:8000/health
```

### Knowledge Gateway (Graphify)

```bash
uv tool install "graphifyy[mcp,anthropic]"
graphify extract ~/Desktop/agency-agents --backend claude --out var   # rebuild the graph (costs real LLM credits)
./scripts/dev/graphify-serve.sh                                        # serve it over MCP on :8080
```

`AXIOM_GRAPHIFY_MCP_URL` must point at that running server for
`/v1/knowledge/*` to report `"configured"`.

### Hermes Integration

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup --non-interactive
```

Both flags matter: `--skip-setup` alone leaves a separate confirmation
prompt that reads `/dev/tty` directly and hangs forever in a non-interactive
shell (see `docs/hermes/HERMES_INTEGRATION.md` §10). `AXIOM_HERMES_BIN`
should point at the installed binary (`~/.local/bin/hermes` by default) if
it isn't already on the API process's PATH.
