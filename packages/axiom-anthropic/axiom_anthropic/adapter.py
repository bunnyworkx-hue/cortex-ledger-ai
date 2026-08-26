from anthropic import AnthropicError, AsyncAnthropic
from anthropic.types import MessageParam

from axiom_core.logging import get_logger
from axiom_core.models.gateway import ModelBackendError
from axiom_core.models.types import ModelRequest, ModelResponse, TokenUsage

logger = get_logger(__name__)


class AnthropicBackend:
    """Model Gateway adapter for Anthropic. Implements the axiom_core
    ModelBackend protocol structurally (see axiom_core.models.gateway) —
    everything Anthropic-specific (message-role translation, response
    shape) is contained here, per CLAUDE.md §27.
    """

    provider_name = "anthropic"

    def __init__(self, client: AsyncAnthropic) -> None:
        self._client = client

    async def is_configured(self) -> bool:
        # Local-only check — presence of a client with a non-empty key.
        # Deliberately does not call the API (that costs money and
        # latency); see ModelGatewayRegistry docstring.
        return bool(self._client.api_key)

    async def generate(self, request: ModelRequest) -> ModelResponse:
        system_parts = [request.system] if request.system else []
        messages: list[MessageParam] = []
        for message in request.messages:
            if message.role == "system":
                system_parts.append(message.content)
            else:
                messages.append({"role": message.role, "content": message.content})

        create_kwargs: dict = {
            "model": request.model,
            "max_tokens": request.max_tokens,
            "messages": messages,
        }
        if system_parts:
            create_kwargs["system"] = "\n\n".join(system_parts)
        if request.temperature is not None:
            # Verified against anthropic-sdk-python 1.0.0 (installed
            # 2026-08-26): AsyncMessages.create() has no `temperature`
            # parameter — sampling controls have moved to `output_config`
            # ("effort") / `thinking`, or been dropped from this API
            # entirely. Log rather than silently ignore, so a caller who
            # asked for a specific temperature isn't misled about why it
            # had no effect.
            logger.warning(
                "axiom.anthropic.temperature_unsupported", requested=request.temperature
            )

        try:
            response = await self._client.messages.create(**create_kwargs)
        except AnthropicError as exc:
            # Translate the provider-specific exception into the
            # provider-neutral ModelBackendError — callers above this
            # adapter (e.g. the API router) must not need to import or
            # catch anthropic's exception types, per CLAUDE.md §27.
            raise ModelBackendError(f"Anthropic request failed: {exc}") from exc

        text = "".join(block.text for block in response.content if block.type == "text")

        return ModelResponse(
            content=text,
            model=response.model,
            provider=self.provider_name,
            usage=TokenUsage(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
            ),
            stop_reason=response.stop_reason,
            raw=response.model_dump(mode="json"),
        )
