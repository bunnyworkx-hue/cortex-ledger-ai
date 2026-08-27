# Cortex Ledger AI

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
| [CORTEX_LEDGER_AI_WORLD.md](CORTEX_LEDGER_AI_WORLD.md) | The scroll-driven 3D operations view (`apps/world`) — real data throughout, honest about what's not built |
| `docs/IMPLEMENTATION_PLAN.md` | Full milestone-by-milestone build history — every real bug, every fix |

## Status

Milestones 6–21 done (CLAUDE.md's full sequence, §82–§97): Foundation,
Model Gateway, Knowledge Gateway, Agent Runtime, Agent Fabric, Tool
Registry + MCP, Hermes Integration, Memory, Policy + Human Approval,
Observability, a Next.js Dashboard, Evaluation (20/20 on the last real
benchmark run), Security (real findings across all 11 of CLAUDE.md §96's
categories, including real budget enforcement and a bounded
agent-to-agent delegation tool added after the initial pass), and
Portfolio Release (this doc set), and Milestone 22 — a real
instruction-hierarchy mitigation for Prompt Injection, a real API-key
auth layer closing Memory/Tenant Isolation, and a real risk-based
approval gate on agent delegation closing Agent Authorization, all
live-verified against the running system (see
`docs/security/SECURITY_AUDIT.md` §5-8). Knowledge Isolation is now the
only open item of CLAUDE.md §96's eleven security categories. 108 tests
passing; 2 skip when there's no live Anthropic model credit available
(`test_observability_endpoint.py`, `test_memory_endpoint.py`),
not a code fault.

### Definition of Done (CLAUDE.md §98) — honest status

Every item on that list is real and working, including the two the
Security milestone originally surfaced as gaps: **"Agent budgets work"**
(`agent.budget.max_tokens`/`max_seconds` are enforced for real by both
backends — see `SECURITY.md`, including a real Anthropic SDK
non-streaming ceiling bug found and fixed while wiring it in) and
**"Agent-to-agent calls are controlled"** (the `delegate_to_agent` native
tool, with a real, tested recursion depth cap — see
`docs/security/SECURITY_AUDIT.md` §11 for the honest limits of "bounded"
here: a cooperative depth cap on a tool no agent's own model output can
invoke autonomously yet, not a cryptographic guarantee against an
adversarial caller). One narrower, still-real gap remains inside Budget
Tests: Hermes's `max_tokens` isn't enforced, since its usage-report JSON
schema was never precisely verified live in this build — named plainly
rather than guessed at. "Screenshots" and "Demo Video" from §97 are
replaced by `DEMO.md` — a real, runnable script, since no browser/
screen-capture tool exists in this environment.

## Layout

```
apps/api/                FastAPI app — the Cortex Ledger AI control-plane HTTP surface
packages/axiom-core/      config, logging, Model/Knowledge/Tool Registry abstractions, Agent Runtime
packages/axiom-db/        async SQLAlchemy engine, ORM base, Alembic migrations
packages/axiom-anthropic/ real Anthropic adapter (Model Gateway)
packages/axiom-graphify/  real Graphify MCP adapter (Knowledge Gateway)
packages/axiom-agent-fabric/ real agent registry + invocation gateway over agency-agents
packages/axiom-mcp/       generic MCP client + Tool Registry integration
packages/axiom-hermes/    real Hermes Agent CLI adapter (AgentBackend)
apps/dashboard/           Next.js operations dashboard
apps/world/               scroll-driven 3D operations view (react-three-fiber, live API data)
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

The browser never calls the API directly — the dashboard proxies every
`/api/*` request through its own Next.js server to `AXIOM_API_ORIGIN`
(default `http://127.0.0.1:8000`) via a real Route Handler
(`apps/dashboard/app/api/[...path]/route.ts`), so the browser's fetches
are same-origin. This replaced an earlier direct-cross-origin design:
the API's CORS policy (still present, `apps/api/axiom_api/main.py`) was
verified correct — including a simulated browser preflight with the
right `Origin` header — but a real user still hit a browser-side "failed
to fetch" that no server-side check could reproduce or explain (likely
an extension or embedded-webview context blocking a cross-origin fetch
to a non-standard local port). Proxying through Next's own server
sidesteps that whole class of problem by construction, rather than
chasing the exact browser-side cause. The route handler itself replaced
an even earlier version built on `next.config.ts`'s `rewrites()`, which
had an undocumented ~30s timeout that cut off genuinely slow real calls
(found live via Cortex Ledger AI World's real Hermes delegations, which routinely
take 10-35s+) — the route handler sets an explicit 130s timeout instead.
Build/typecheck/lint are verified (`npm run build`, clean TypeScript,
clean ESLint) and every route was curl-verified to serve 200 through the
proxy; the rendered UI itself was not visually verified — no browser/
screenshot tool was available in this environment.

### Cortex Ledger AI World (3D operations view)

```bash
cd apps/world && npm install   # first time only
./scripts/dev/run.sh           # API on :8000, in one terminal
./scripts/dev/world.sh         # world on the next free port, in another
```

See [CORTEX_LEDGER_AI_WORLD.md](CORTEX_LEDGER_AI_WORLD.md) for what's real (live agent/graph/
backend data throughout, a working Talk-Back chat wired to real search
and delegation) versus what's honestly not built yet from the original
39-section spec. Same `/api/*` same-origin proxy pattern as the
dashboard. Clean `tsc --noEmit`, clean `next build`, clean ESLint; not
visually verified in a browser for the same reason as the dashboard.

### Evaluation

```bash
./scripts/dev/run.sh                              # API must be running
uv run python scripts/evaluation/run_benchmark.py  # 20 real tasks, real cost
```

Every task is a real HTTP call through the live API (delegate, tool
call, or a full propose→approve→execute approval flow) — nothing is
mocked or simulated. Writes a timestamped JSON report to
`var/evaluation/` for comparing runs over time.
