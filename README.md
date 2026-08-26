# Axiom OS

Agentic AI operating system — Agent Fabric, Knowledge Fabric, Execution
Engine. See `CLAUDE.md` for the full architecture and engineering rules,
and `docs/` for the audits and implementation plan behind every design
decision here.

## Status

Milestones 6–18 done: Foundation, Model Gateway, Knowledge Gateway, Agent
Runtime, Agent Fabric, Tool Registry + MCP, Hermes Integration, Memory,
Policy + Human Approval, Observability, and a real Next.js Dashboard
(`apps/dashboard`) — Overview (live subsystem status), Agent Fabric
(search + live delegate), Execution Trace, Approvals (real approve/
reject buttons that call the API), and Tools. A deliberate subset of
CLAUDE.md §50's ~18-view list, not all of it — Agent Teams, Execution/
Knowledge Graph visualizations, a dedicated Knowledge Explorer/MCP/
Backends/Memory/Evaluations/Security/Settings view are not built; see
`docs/IMPLEMENTATION_PLAN.md` for what's next (Evaluation, Security).

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
apps/dashboard/           Next.js operations dashboard
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

### Dashboard

```bash
cd apps/dashboard && npm install   # first time only
./scripts/dev/run.sh               # API on :8000, in one terminal
./scripts/dev/dashboard.sh         # dashboard on :3000, in another
```

The API's CORS policy only allows `localhost:3000`/`127.0.0.1:3000` — see
`apps/api/axiom_api/main.py`. Build/typecheck/lint are verified
(`npm run build`, clean TypeScript, clean ESLint) and every route was
curl-verified to serve 200 with working CORS; the rendered UI itself
was not visually verified — no browser/screenshot tool was available in
this environment.
