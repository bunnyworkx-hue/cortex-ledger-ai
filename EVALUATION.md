# Evaluation

`scripts/evaluation/run_benchmark.py` — a real 20-task benchmark against
a live, already-running Axiom API. Every task is a genuine HTTP call
through the same endpoints a real client would use (agent delegation, a
tool call, or a full propose→approve→execute approval flow). Nothing is
mocked, nothing imports Python internals directly — a task fails if the
real backend fails.

## Run it

```bash
./scripts/dev/run.sh                              # API must be running
uv run python scripts/evaluation/run_benchmark.py  # 20 real tasks, real cost
```

Writes a timestamped JSON report to `var/evaluation/` (gitignored, like
every other generated artifact — see `var/`) so runs are comparable over
time without a dedicated database table for it.

## Methodology

CLAUDE.md §75 asks for at least 20 tasks across a defined set of
categories, scored honestly rather than with a fabricated quality metric
(§45). Most tasks ask an agent to "reply with exactly: `<token>`" — a
real, deterministic, end-to-end pipeline check (Agent Fabric → Backend →
Model → real response), not a fuzzy judgment of output quality.
Tool/knowledge/approval tasks check a real structural signal instead (a
field present, a substring in real tool output, a record's field
actually changed after approval).

## Categories covered (all 12 CLAUDE.md §75 names)

research · analysis · planning · marketing · finance · operations ·
tool_use · agent_delegation · hermes_delegation · knowledge_query ·
graphify_query · human_approval

## Last real run

20/20 passed. Representative timings from the last run:

| category | typical duration | why |
|---|---|---|
| research/analysis/planning/marketing/finance/operations/agent_delegation | ~2–3s | one real Anthropic completion via `AxiomNativeBackend` |
| hermes_delegation | ~10.8s | real Hermes CLI subprocess overhead (cold-start tool-definition cache write), not a bug |
| tool_use/knowledge_query/graphify_query | 140–509ms | no LLM call — a local, cached Graphify MCP query |
| human_approval | varies | a real propose → approve → execute round trip through Postgres |

Reports aren't committed (they're per-run artifacts in `var/`, which is
gitignored) — regenerate one locally with the command above to see a
current result on your own machine/API keys.
