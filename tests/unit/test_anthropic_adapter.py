from dataclasses import dataclass, field

import pytest
from anthropic import AnthropicError

from axiom_anthropic.adapter import AnthropicBackend
from axiom_core.models import ModelBackendError, ModelMessage, ModelRequest


@dataclass
class _FakeTextBlock:
    text: str
    type: str = "text"


@dataclass
class _FakeUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class _FakeMessage:
    content: list[_FakeTextBlock]
    model: str
    stop_reason: str
    usage: _FakeUsage

    def model_dump(self, mode: str = "python") -> dict:
        return {"model": self.model, "stop_reason": self.stop_reason}


class _FakeMessages:
    def __init__(self, response: _FakeMessage) -> None:
        self._response = response
        self.last_call_kwargs: dict | None = None

    async def create(self, **kwargs) -> _FakeMessage:
        self.last_call_kwargs = kwargs
        return self._response


@dataclass
class _FakeAnthropicClient:
    api_key: str
    messages: _FakeMessages = field(init=False)

    def __post_init__(self) -> None:
        self.messages = _FakeMessages(
            _FakeMessage(
                content=[_FakeTextBlock(text="Hello from Claude")],
                model="claude-sonnet-5",
                stop_reason="end_turn",
                usage=_FakeUsage(input_tokens=12, output_tokens=4),
            )
        )


@pytest.mark.asyncio
async def test_is_configured_reflects_api_key_presence():
    configured = AnthropicBackend(_FakeAnthropicClient(api_key="sk-real-key"))
    unconfigured = AnthropicBackend(_FakeAnthropicClient(api_key=""))

    assert await configured.is_configured() is True
    assert await unconfigured.is_configured() is False


@pytest.mark.asyncio
async def test_generate_maps_request_and_response():
    client = _FakeAnthropicClient(api_key="sk-real-key")
    backend = AnthropicBackend(client)

    request = ModelRequest(
        messages=[
            ModelMessage(role="system", content="Be terse."),
            ModelMessage(role="user", content="Say hi."),
        ],
        model="claude-sonnet-5",
        max_tokens=100,
        system="You are Cortex Ledger AI.",
    )

    response = await backend.generate(request)

    assert response.content == "Hello from Claude"
    assert response.provider == "anthropic"
    assert response.model == "claude-sonnet-5"
    assert response.usage.input_tokens == 12
    assert response.usage.output_tokens == 4
    assert response.usage.total_tokens == 16
    assert response.stop_reason == "end_turn"

    # System-role messages must be merged into the `system` param, not
    # sent as a message (the Anthropic API rejects role="system" messages).
    call_kwargs = client.messages.last_call_kwargs
    assert call_kwargs["system"] == "You are Cortex Ledger AI.\n\nBe terse."
    assert call_kwargs["messages"] == [{"role": "user", "content": "Say hi."}]


@pytest.mark.asyncio
async def test_generate_translates_anthropic_errors_to_model_backend_error():
    client = _FakeAnthropicClient(api_key="sk-real-key")

    async def _raise(**kwargs):
        raise AnthropicError("credit balance is too low")

    client.messages.create = _raise
    backend = AnthropicBackend(client)

    request = ModelRequest(messages=[ModelMessage(role="user", content="hi")], model="claude-sonnet-5")

    # The API router must be able to catch this without importing
    # anthropic's exception types — a real provider failure (billing,
    # rate limit, outage) must never surface as an uncaught 500.
    with pytest.raises(ModelBackendError, match="credit balance is too low"):
        await backend.generate(request)
