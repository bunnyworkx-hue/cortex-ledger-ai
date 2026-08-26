import pytest

from axiom_core.agents import Agent, AgentBackendError, AgentTask, AxiomNativeBackend
from axiom_core.models import ModelBackendError, ModelResponse, TokenUsage


class _FakeModelBackend:
    provider_name = "fake"

    def __init__(self, response: ModelResponse | None = None, error: Exception | None = None) -> None:
        self._response = response
        self._error = error
        self.last_request = None

    async def is_configured(self) -> bool:
        return True

    async def generate(self, request):
        self.last_request = request
        if self._error is not None:
            raise self._error
        return self._response


@pytest.mark.asyncio
async def test_execute_builds_system_prompt_from_instructions_and_context():
    model_backend = _FakeModelBackend(
        response=ModelResponse(
            content="Hello!",
            model="claude-sonnet-5",
            provider="fake",
            usage=TokenUsage(input_tokens=10, output_tokens=2),
            stop_reason="end_turn",
        )
    )
    backend = AxiomNativeBackend(model_backend, default_model="claude-sonnet-5")
    agent = Agent(agent_id="a1", name="Test Agent", instructions="You are a test agent.")
    task = AgentTask(input="say hi", context="The user's name is Sam.")

    result = await backend.execute(agent, task)

    assert result.content == "Hello!"
    assert result.raw["model"] == "claude-sonnet-5"
    assert result.raw["usage"]["input_tokens"] == 10

    request = model_backend.last_request
    assert request.system == "You are a test agent.\n\nRelevant context:\nThe user's name is Sam."
    assert request.messages[0].content == "say hi"


@pytest.mark.asyncio
async def test_execute_translates_model_backend_error():
    model_backend = _FakeModelBackend(error=ModelBackendError("rate limited"))
    backend = AxiomNativeBackend(model_backend, default_model="claude-sonnet-5")
    agent = Agent(agent_id="a1", name="Test Agent", instructions="You are a test agent.")

    with pytest.raises(AgentBackendError, match="rate limited"):
        await backend.execute(agent, AgentTask(input="say hi"))
