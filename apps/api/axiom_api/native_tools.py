from axiom_agent_fabric import AgentInvocationGateway, AgentNotFoundError
from axiom_core.agents import AgentBackendNotFoundError, AgentBackendRegistry, ExecutionStore
from axiom_core.memory import MemoryStore
from axiom_core.tools import ToolCallResult, ToolDefinition, ToolRegistry

from axiom_api.delegation import run_delegation

# CLAUDE.md §64's own demo: an in-memory mock "business record" store —
# deliberately not a real business system. The point is to prove the
# Policy Engine + Human Approval pipeline actually gates a real mutating
# call, not to model real business data.
_BUSINESS_RECORDS: dict[str, dict] = {}

# Milestone 21's real, minimal answer to CLAUDE.md §98's "agent-to-agent
# calls are controlled": a hard depth cap so a chain of delegate_to_agent
# calls can't recurse unboundedly. `_delegation_depth` is caller-supplied
# in the tool arguments (there's no execution-context threading in this
# build to derive it server-side) — a cooperative control, not a
# cryptographic one. See its docstring below for the honest boundary.
_MAX_DELEGATION_DEPTH = 3


def register_native_tools(
    registry: ToolRegistry,
    *,
    agent_fabric: AgentInvocationGateway | None = None,
    agent_backend_gateway: AgentBackendRegistry | None = None,
    memory_store: MemoryStore | None = None,
    execution_store: ExecutionStore | None = None,
) -> None:
    async def modify_business_record(arguments: dict) -> ToolCallResult:
        record_id = arguments["record_id"]
        fields = arguments.get("fields", {})
        _BUSINESS_RECORDS.setdefault(record_id, {}).update(fields)
        return ToolCallResult(content={"record_id": record_id, "record": _BUSINESS_RECORDS[record_id]})

    registry.register(
        ToolDefinition(
            name="modify_business_record",
            description="Create or update fields on a business record (demo — in-memory only).",
            input_schema={
                "type": "object",
                "properties": {
                    "record_id": {"type": "string"},
                    "fields": {"type": "object"},
                },
                "required": ["record_id"],
            },
            source="native",
            permissions=("business_record.write",),
            risk_level="high",
        ),
        modify_business_record,
    )

    if agent_fabric is not None and agent_backend_gateway is not None:

        async def delegate_to_agent(arguments: dict) -> ToolCallResult:
            """Agent-to-agent orchestration: lets a caller (a script, an
            operator, or — once a tool-calling loop exists — an agent's
            own reasoning) have one agent's task delegate a sub-task to
            another registered agent, through the exact same
            AgentInvocationGateway + persistence path as a direct API
            delegation (``run_delegation``), not a shortcut.

            Real, honest boundary: AxiomNativeBackend has no
            tool-calling loop today (CLAUDE.md §30's `AxiomNativeBackend`
            is a single generate() call, no function-calling), so no
            agent's own model output can invoke this tool autonomously
            yet — it's reachable only via a direct
            `POST /v1/tools/delegate_to_agent/call`. `_delegation_depth`
            is therefore a forward-compatible guard against future
            automatic chaining, not a live exploitable recursion path
            today. It's also caller-supplied, not derived from a real
            execution context, so it's a cooperative control (like every
            other unauthenticated boundary named in
            docs/security/SECURITY_AUDIT.md), not a cryptographic one.
            """
            depth = int(arguments.get("_delegation_depth", 0))
            if depth >= _MAX_DELEGATION_DEPTH:
                return ToolCallResult(
                    content={"error": f"delegation depth limit ({_MAX_DELEGATION_DEPTH}) reached"},
                    is_error=True,
                )

            target_agent_id = arguments["agent_id"]
            task_input = arguments["task_input"]
            backend_name = arguments.get("backend", "axiom_native")

            try:
                execution = await run_delegation(
                    agent_fabric,
                    agent_backend_gateway,
                    memory_store,
                    execution_store,
                    agent_id=target_agent_id,
                    task_input=task_input,
                    backend_name=backend_name,
                )
            except (AgentNotFoundError, AgentBackendNotFoundError) as exc:
                return ToolCallResult(content={"error": str(exc)}, is_error=True)

            if execution.status.value == "failed":
                return ToolCallResult(content={"error": execution.error}, is_error=True)

            return ToolCallResult(
                content={
                    "execution_id": execution.execution_id,
                    "agent_id": target_agent_id,
                    "content": execution.result.content if execution.result else None,
                    "delegation_depth": depth + 1,
                }
            )

        registry.register(
            ToolDefinition(
                name="delegate_to_agent",
                description=(
                    "Delegate a task to another registered Axiom agent. Bounded to a real "
                    f"recursion depth of {_MAX_DELEGATION_DEPTH} via `_delegation_depth`."
                ),
                input_schema={
                    "type": "object",
                    "properties": {
                        "agent_id": {"type": "string"},
                        "task_input": {"type": "string"},
                        "backend": {"type": "string"},
                        "_delegation_depth": {"type": "integer"},
                    },
                    "required": ["agent_id", "task_input"],
                },
                source="native",
                permissions=("agent.delegate",),
                risk_level="medium",
            ),
            delegate_to_agent,
        )
