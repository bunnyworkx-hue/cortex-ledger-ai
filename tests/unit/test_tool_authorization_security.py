"""Milestone 20 (Security) — Tool Authorization Tests, CLAUDE.md §96.

Two things are true about tool authorization in this build, and both need
a regression test so neither drifts silently:

1. Permission-set enforcement (``granted_permissions``) works when a
   caller supplies one — already covered by test_tool_registry.py.
2. ``ToolRegistry.execute()`` itself does NOT consult the Policy Engine —
   the propose/approve gate lives one layer up, in
   apps/api/axiom_api/routers/tools.py (which calls
   ``policy.evaluate()`` before ever calling ``registry.execute()``) and
   routers/approvals.py (which calls ``registry.execute()`` directly,
   *by design*, only after a human decision is recorded).

That second point is a real architectural boundary, not a bug: today the
only two callers of ``ToolRegistry.execute()`` are those two,
policy-aware routers, so a high-risk tool can't currently be reached
without going through the approval gate. But the registry would happily
run a "high"/"critical" risk tool with zero approval if a future caller
invoked ``execute()`` directly — see docs/security/SECURITY_AUDIT.md
§"Tool Authorization" for the full writeup. This test documents that
boundary in code: if someone later moves policy enforcement inside the
registry, they'll need to update this test; if someone accidentally adds
a bypass path, this test's docstring is the tripwire.
"""

import pytest

from axiom_core.tools import ToolCallResult, ToolDefinition, ToolRegistry


@pytest.mark.asyncio
async def test_registry_execute_has_no_built_in_risk_gate():
    registry = ToolRegistry()
    calls: list[dict] = []

    async def handler(arguments: dict) -> ToolCallResult:
        calls.append(arguments)
        return ToolCallResult(content={"executed": True})

    registry.register(
        ToolDefinition(
            name="delete_everything",
            description="A hypothetical destructive tool.",
            input_schema={"type": "object"},
            source="native",
            permissions=(),
            risk_level="critical",
            # ToolDefinition doesn't require the caller to supply
            # granted_permissions — a "critical" tool with no
            # `permissions` requirement and no policy check upstream
            # runs immediately.
        ),
        handler,
    )

    # No PolicyEngine involved at all — proves the registry is the
    # execution plane, not the control plane. Callers (API routers) are
    # responsible for gating risky actions before reaching this call.
    result = await registry.execute("delete_everything", {})

    assert result.content == {"executed": True}
    assert len(calls) == 1
