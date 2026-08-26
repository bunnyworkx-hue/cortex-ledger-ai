import pytest

from axiom_agent_fabric.gateway import AgentInvocationGateway
from axiom_agent_fabric.registry import AgentRegistry
from axiom_agent_fabric.types import AgentRecord, AgentStatus
from axiom_core.agents import AgentResult


class _StubBackend:
    backend_name = "stub"

    async def is_configured(self) -> bool:
        return True

    async def execute(self, agent, task) -> AgentResult:
        return AgentResult(content=f"[{agent.name}] handled: {task.input} (ctx={task.context})")


@pytest.fixture
def gateway():
    record = AgentRecord(
        agent_id="engineering/engineering-frontend-developer",
        name="Frontend Developer",
        description="Builds UIs.",
        division="engineering",
        category="Engineering",
        instructions="You build UIs.",
        source_path="engineering/engineering-frontend-developer.md",
        source_commit="a" * 40,
        status=AgentStatus.ACTIVE,
        capabilities=("frontend_development",),
    )
    return AgentInvocationGateway(AgentRegistry([record]))


def test_inspect_returns_the_record(gateway):
    record = gateway.inspect("engineering/engineering-frontend-developer")
    assert record.name == "Frontend Developer"


def test_load_composes_instructions_with_task(gateway):
    prompt = gateway.load("engineering/engineering-frontend-developer", task="Build a button.")
    assert prompt == "You build UIs.\n\nCurrent task:\nBuild a button."


def test_load_without_task_returns_bare_instructions(gateway):
    assert gateway.load("engineering/engineering-frontend-developer") == "You build UIs."


@pytest.mark.asyncio
async def test_delegate_runs_through_the_given_backend(gateway):
    execution = await gateway.delegate(
        "engineering/engineering-frontend-developer",
        "build a button",
        backend=_StubBackend(),
        context="dark mode",
    )

    assert execution.status.value == "succeeded"
    assert execution.result.content == "[Frontend Developer] handled: build a button (ctx=dark mode)"
    assert execution.backend_name == "stub"
