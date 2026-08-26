# Demo

CLAUDE.md §97 asks for a demo video and screenshots. Neither is
producible in this environment — no browser or screen-capture tool was
available (the same honest gap noted for the Dashboard in Milestone 18).
Rather than skip the deliverable, this is the real substitute: a literal,
copy-pasteable walkthrough using the actual endpoints, agent ids, and
flows verified live throughout this build. Anyone with the repo running
locally can run this exact script and get the exact real behavior
described.

Prerequisites: `./scripts/dev/run.sh` (API on :8000), `./scripts/dev/graphify-serve.sh`
(Graphify MCP on :8080, optional — knowledge/tool_use steps skip cleanly
without it), a configured `.env` (see `README.md` Setup).

## Demo 1 — Knowledge-grounded delegation (CLAUDE.md §59)

Ask a real curated agent a question, grounded by a real query against the
Graphify knowledge graph built from `agency-agents`:

```bash
curl -s http://127.0.0.1:8000/v1/knowledge/search \
  -G --data-urlencode "question=frontend developer" | python3 -m json.tool

curl -s -X POST http://127.0.0.1:8000/v1/agent-fabric/agents/engineering/engineering-frontend-developer/delegate \
  -H "Content-Type: application/json" \
  -d '{"input": "Explain how you approach Core Web Vitals optimization."}' | python3 -m json.tool
```

Expect a real `EXTRACTED`/`INFERRED` graph excerpt from the first call,
and a real, in-character completion from the second, routed through
`AgentInvocationGateway` → `AxiomNativeBackend` → the real Anthropic API.

## Demo 2 — Hermes delegation (CLAUDE.md §60)

The same delegate endpoint, routed through the real `hermes` CLI instead
of Axiom's native backend:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/agent-fabric/agents/sales/sales-deal-strategist/delegate \
  -H "Content-Type: application/json" \
  -d '{"input": "Reply with exactly: hermes-demo-ack", "backend": "hermes"}' | python3 -m json.tool
```

A real subprocess call to `hermes -z ... --provider anthropic`
underneath — expect several seconds of latency (real CLI startup +
subprocess overhead), not the ~2s a native call takes.

## Demo 3 — Cross-agent team (CLAUDE.md §63)

Delegate the same kind of task to three agents from different divisions
to show the registry spans real, unrelated personas, not one hardcoded
prompt:

```bash
for agent in "finance/finance-fpa-analyst" "marketing/marketing-seo-specialist" "project-management/project-management-project-shepherd"; do
  echo "--- $agent ---"
  curl -s -X POST "http://127.0.0.1:8000/v1/agent-fabric/agents/$agent/delegate" \
    -H "Content-Type: application/json" \
    -d '{"input": "In one sentence, what is your primary responsibility?"}' | python3 -c "import json,sys; print(json.load(sys.stdin)['content'])"
done
```

## Demo 4 — Human approval (CLAUDE.md §64)

A mutating tool call that must not execute until a human approves it —
the real propose → approve → execute → audit loop:

```bash
RECORD_ID="demo-$(date +%s)"

# 1. Propose — this does NOT execute yet
PROPOSE=$(curl -s -X POST http://127.0.0.1:8000/v1/tools/modify_business_record/call \
  -H "Content-Type: application/json" \
  -d "{\"arguments\": {\"record_id\": \"$RECORD_ID\", \"fields\": {\"status\": \"demo\"}}}")
echo "$PROPOSE" | python3 -m json.tool
APPROVAL_ID=$(echo "$PROPOSE" | python3 -c "import json,sys; print(json.load(sys.stdin)['approval_id'])")

# 2. Check it's really pending, not silently applied
curl -s http://127.0.0.1:8000/v1/approvals/$APPROVAL_ID | python3 -m json.tool

# 3. A human approves — this is what actually executes the change
curl -s -X POST http://127.0.0.1:8000/v1/approvals/$APPROVAL_ID/approve \
  -H "Content-Type: application/json" \
  -d '{"decided_by": "demo-operator"}' | python3 -m json.tool
```

The final response's `content.record.status` will be `"demo"` — proof
the mutation only happened after the explicit approve call, not at
propose time.

## Demo 5 — Observability (CLAUDE.md §40)

Every execution above left a real trace:

```bash
curl -s http://127.0.0.1:8000/v1/observability/executions | python3 -m json.tool
curl -s http://127.0.0.1:8000/v1/observability/metrics | python3 -m json.tool
```

## Demo 6 — Dashboard (CLAUDE.md §50-52)

```bash
./scripts/dev/dashboard.sh   # http://localhost:3000
```

Overview, Agents, Executions, Approvals, and Tools pages all read from
the same live API these curl calls just exercised — approving a pending
approval from Demo 4 in the dashboard's Approvals page and watching the
Executions page update is the closest thing to the missing screen
recording.

## Live, interactive API reference

```
http://127.0.0.1:8000/docs
```

FastAPI's auto-generated Swagger UI — every one of the 24 real endpoints
above (and every other route) is browsable and directly callable there
while the API is running.
