"""Milestone 21 — the real, minimal answer to CLAUDE.md §98's "agent-to-agent
calls are controlled": a hard depth cap on the ``delegate_to_agent`` native
tool. See its handler docstring (apps/api/axiom_api/native_tools.py) for the
honest boundary — this is a cooperative control on a tool no agent's own
reasoning can invoke autonomously yet (no tool-calling loop exists), not a
live exploitable recursion path today.
"""

import pytest

from axiom_agent_fabric.gateway import AgentInvocationGateway
from axiom_core.agents import Agent, AgentBackendRegistry, AgentResult, AgentTask
from axiom_core.tools import ToolRegistry

from axiom_api.native_tools import _MAX_DELEGATION_DEPTH, register_native_tools


class _FakeAgentRegistry:
    def get(self, agent_id: str):
        from axiom_agent_fabric.types import AgentRecord

        return AgentRecord(
            agent_id=agent_id,
            name="Fake Agent",
            description="A fake agent for depth-cap testing.",
            division="testing",
            category="testing",
            instructions="Be helpful.",
            source_path="fake.md",
            source_commit="abc123",
        )


class _FakeBackend:
    backend_name = "axiom_native"

    async def execute(self, agent: Agent, task: AgentTask) -> AgentResult:
        return AgentResult(content="ok")

    async def is_configured(self) -> bool:
        return True


def _build_registry() -> ToolRegistry:
    gateway = AgentInvocationGateway(_FakeAgentRegistry())
    backend_registry = AgentBackendRegistry()
    backend_registry.register(_FakeBackend())

    tool_registry = ToolRegistry()
    register_native_tools(
        tool_registry,
        agent_fabric=gateway,
        agent_backend_gateway=backend_registry,
    )
    return tool_registry


@pytest.mark.asyncio
async def test_delegate_to_agent_succeeds_below_depth_limit():
    registry = _build_registry()

    result = await registry.execute(
        "delegate_to_agent",
        {"agent_id": "engineering/some-agent", "task_input": "do a thing", "_delegation_depth": 0},
    )

    assert result.is_error is False
    assert result.content["content"] == "ok"
    assert result.content["delegation_depth"] == 1


@pytest.mark.asyncio
async def test_delegate_to_agent_refuses_at_depth_limit():
    registry = _build_registry()

    result = await registry.execute(
        "delegate_to_agent",
        {
            "agent_id": "engineering/some-agent",
            "task_input": "do a thing",
            "_delegation_depth": _MAX_DELEGATION_DEPTH,
        },
    )

    assert result.is_error is True
    assert "depth limit" in result.content["error"]


@pytest.mark.asyncio
async def test_delegate_to_agent_defaults_depth_to_zero_when_omitted():
    registry = _build_registry()

    result = await registry.execute(
        "delegate_to_agent", {"agent_id": "engineering/some-agent", "task_input": "do a thing"}
    )

    assert result.is_error is False
    assert result.content["delegation_depth"] == 1
