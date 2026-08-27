"""Milestone 22 (Security) — Agent Authorization Tests, CLAUDE.md §96.

Real gap this closes: ``docs/security/SECURITY_AUDIT.md`` §8 named that
only tool *execution* was policy-gated, not agent *invocation* — a
caller could delegate to any of the 254 agents, including a
``risk_level="high"`` one, with zero approval. ``routers/agent_fabric.py``'s
``delegate()`` now calls ``PolicyEngine.evaluate()`` before running a
delegation, exactly like ``routers/tools.py``'s ``call_tool()`` already
did for tools; ``routers/approvals.py``'s ``approve()`` now executes an
approved ``agent:{agent_id}`` action through the real delegation path,
not just ``tool:{name}``.

Honest scope note: no agent in the real, live registry currently has
``risk_level="high"``/``"critical"`` (all 12 curated agents cap at
"medium"; the other 242 have no risk_level at all — see
``PolicyEngine.evaluate``'s docstring on how that's treated). This test
therefore injects a fake high-risk agent via FastAPI's
``dependency_overrides`` to exercise the gate for real — the same
"forward-compatible, not yet exercised by today's data" category as the
``delegate_to_agent`` depth cap (``test_delegate_to_agent_depth.py``).
"""

import httpx
import pytest

from axiom_agent_fabric.gateway import AgentInvocationGateway
from axiom_agent_fabric.types import AgentRecord
from axiom_core.agents import Agent, AgentResult, AgentTask

from axiom_api.dependencies import get_agent_backend_gateway, get_agent_fabric
from axiom_api.main import app

_FAKE_AGENT_ID = "testing/fake-high-risk-agent"


class _FakeRegistryWithHighRiskAgent:
    """Backs a real AgentInvocationGateway — so the gateway's own real
    ``delegate()`` runs (constructs a real Agent/AgentTask, calls
    ExecutionRunner for real), the same as test_delegate_to_agent_depth.py's
    ``_FakeAgentRegistry``. Only the registry lookup is fake."""

    def get(self, agent_id: str) -> AgentRecord:
        return AgentRecord(
            agent_id=agent_id,
            name="Fake High-Risk Agent",
            description="A fake agent for policy-gate testing.",
            division="testing",
            category="testing",
            instructions="Be helpful.",
            source_path="fake.md",
            source_commit="abc123",
            risk_level="high",
        )

    def list(self, *, division=None):
        return [self.get(_FAKE_AGENT_ID)]

    def search(self, query, *, division=None, limit=10):
        return []


class _FakeBackendRegistry:
    """A stand-in AgentBackendRegistry whose one backend just echoes —
    lets the approve-and-execute path be verified without a real
    Anthropic call (also sidesteps the credit-balance issue blocking
    other live probes right now)."""

    def get(self, name: str):
        return self

    backend_name = "axiom_native"

    async def is_configured(self) -> bool:
        return True

    async def execute(self, agent: Agent, task: AgentTask) -> AgentResult:
        return AgentResult(content=f"fake result for: {task.input}")


@pytest.mark.asyncio
async def test_high_risk_agent_delegation_requires_approval_then_executes_on_approve(
    api_client: httpx.AsyncClient,
):
    app.dependency_overrides[get_agent_fabric] = lambda: AgentInvocationGateway(_FakeRegistryWithHighRiskAgent())
    app.dependency_overrides[get_agent_backend_gateway] = lambda: _FakeBackendRegistry()
    try:
        propose = await api_client.post(
            f"/v1/agent-fabric/agents/{_FAKE_AGENT_ID}/delegate",
            json={"input": "do something a high-risk agent would do"},
        )
        if propose.status_code == 503:
            pytest.skip("Approval store not configured in this environment")

        assert propose.status_code == 200
        body = propose.json()
        assert "approval_id" in body, f"expected a pending approval, got: {body}"
        assert body["status"] == "pending"
        approval_id = body["approval_id"]

        # Real end-to-end proof: approving it actually runs the
        # delegation (through run_delegation, the same path a direct
        # unapproved call would have used) — not just a status flip.
        approve = await api_client.post(f"/v1/approvals/{approval_id}/approve", json={"decided_by": "pytest"})
        assert approve.status_code == 200
        result = approve.json()
        assert result["agent_id"] == _FAKE_AGENT_ID
        assert result["content"] == "fake result for: do something a high-risk agent would do"

        # Can't double-approve — the approval was consumed.
        replay = await api_client.post(f"/v1/approvals/{approval_id}/approve", json={"decided_by": "pytest"})
        assert replay.status_code == 409
    finally:
        app.dependency_overrides.pop(get_agent_fabric, None)
        app.dependency_overrides.pop(get_agent_backend_gateway, None)
