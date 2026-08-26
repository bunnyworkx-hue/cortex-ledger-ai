# Axiom OS

Agentic AI operating system — Agent Fabric, Knowledge Fabric, Execution
Engine. See `CLAUDE.md` for the full architecture and engineering rules,
and `docs/` for the audits and implementation plan behind every design
decision here.

## Documentation

| | |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design, request/delegation flow diagrams, package graph, what's deliberately not built |
| [SECURITY.md](SECURITY.md) | What's enforced vs. real named gaps — see `docs/security/SECURITY_AUDIT.md` for full evidence |
| [EVALUATION.md](EVALUATION.md) | Benchmark methodology and the last real 20/20 run |
| [HERMES_INTEGRATION.md](HERMES_INTEGRATION.md) | Real install gotchas, provider-detection bug, live-verified call path |
| [GRAPHIFY_INTEGRATION.md](GRAPHIFY_INTEGRATION.md) | Real MCP tool schemas, live extraction cost/result |
| [AGENT_FABRIC.md](AGENT_FABRIC.md) | 255 real agents, corrected count, curation, normalization gaps |
| [KNOWLEDGE_FABRIC.md](KNOWLEDGE_FABRIC.md) | The Knowledge Gateway abstraction and the `KnowledgeAnswer` design correction |
| [DEMO.md](DEMO.md) | A literal, copy-pasteable walkthrough — the honest substitute for a demo video/screenshots (no browser tool in this environment) |
| `docs/IMPLEMENTATION_PLAN.md` | Full milestone-by-milestone build history — every real bug, every fix |

## Status

Milestones 6–21 done (CLAUDE.md's full sequence, §82–§97): Foundation,
Model Gateway, Knowledge Gateway, Agent Runtime, Agent Fabric, Tool
Registry + MCP, Hermes Integration, Memory, Policy + Human Approval,
Observability, a Next.js Dashboard, Evaluation (20/20 on the last real
benchmark run), Security (real findings across all 11 of CLAUDE.md §96's
categories), and Portfolio Release (this doc set). 94/94 tests passing.

### Definition of Done (CLAUDE.md §98) — honest status

Everything on that list is real and working **except** two items the
Security milestone surfaced as genuine, undone gaps rather than checked
off by assumption: **"Agent budgets work"** (usage is captured per call
but never aggregated or gated — see `SECURITY.md`) and **"Agent-to-agent
calls are controlled"** (there is no agent-to-agent delegation path at
all yet, so there's nothing to control). "Screenshots" and "Demo Video"
from §97 are replaced by `DEMO.md` — a real, runnable script, since no
browser/screen-capture tool exists in this environment.

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

### Evaluation

```bash
./scripts/dev/run.sh                              # API must be running
uv run python scripts/evaluation/run_benchmark.py  # 20 real tasks, real cost
```

Every task is a real HTTP call through the live API (delegate, tool
call, or a full propose→approve→execute approval flow) — nothing is
mocked or simulated. Writes a timestamped JSON report to
`var/evaluation/` for comparing runs over time.
