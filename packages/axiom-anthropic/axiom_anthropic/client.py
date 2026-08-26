from anthropic import AsyncAnthropic

from axiom_core.config import AxiomSettings


class AnthropicNotConfiguredError(RuntimeError):
    """Raised when an Anthropic call is attempted but AXIOM_ANTHROPIC_API_KEY
    is unset. Fails loudly rather than silently returning a fake response.
    """


def build_anthropic_client(settings: AxiomSettings) -> AsyncAnthropic:
    if not settings.anthropic_api_key:
        raise AnthropicNotConfiguredError(
            "AXIOM_ANTHROPIC_API_KEY is not set. Copy .env.example to .env "
            "and add a real Anthropic API key."
        )
    return AsyncAnthropic(api_key=settings.anthropic_api_key)
