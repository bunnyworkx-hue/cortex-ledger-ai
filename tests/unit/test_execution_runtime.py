import pytest

from axiom_core.agents import (
    Agent,
    AgentBackendError,
    AgentResult,
    AgentTask,
    ExecutionRunner,
    ExecutionStatus,
)


class _SucceedingBackend:
    backend_name = "stub"

    async def is_configured(self) -> bool:
        return True

    async def execute(self, agent: Agent, task: AgentTask) -> AgentResult:
        return AgentResult(content=f"handled: {task.input}")


class _FailingBackend:
    backend_name = "stub"

    async def is_configured(self) -> bool:
        return True

    async def execute(self, agent: Agent, task: AgentTask) -> AgentResult:
        raise AgentBackendError("upstream exploded")


@pytest.mark.asyncio
async def test_run_succeeds_and_records_result():
    agent = Agent(agent_id="a1", name="Test Agent", instructions="Be helpful.")
    task = AgentTask(input="say hi")
    runner = ExecutionRunner(_SucceedingBackend())

    execution = await runner.run(agent, task)

    assert execution.status == ExecutionStatus.SUCCEEDED
    assert execution.result is not None
    assert execution.result.content == "handled: say hi"
    assert execution.error is None
    assert execution.agent_id == "a1"
    assert execution.backend_name == "axiom_native"  # from Agent's default
    assert execution.completed_at is not None
    assert execution.completed_at >= execution.started_at


@pytest.mark.asyncio
async def test_run_records_failure_without_raising():
    agent = Agent(agent_id="a1", name="Test Agent", instructions="Be helpful.")
    task = AgentTask(input="say hi")
    runner = ExecutionRunner(_FailingBackend())

    execution = await runner.run(agent, task)

    assert execution.status == ExecutionStatus.FAILED
    assert execution.result is None
    assert execution.error == "upstream exploded"
    assert execution.completed_at is not None
