from dataclasses import dataclass, field
from typing import Literal

Role = Literal["system", "user", "assistant"]


@dataclass(frozen=True, slots=True)
class ModelMessage:
    role: Role
    content: str


@dataclass(frozen=True, slots=True)
class ModelRequest:
    """Provider-neutral request shape. Adapters translate this into
    whatever their backend's native call shape requires — nothing above
    the adapter layer should know about Anthropic (or any provider)
    specifics, per CLAUDE.md §27.
    """

    messages: list[ModelMessage]
    model: str
    max_tokens: int = 1024
    temperature: float | None = None
    system: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TokenUsage:
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass(frozen=True, slots=True)
class ModelResponse:
    content: str
    model: str
    provider: str
    usage: TokenUsage
    stop_reason: str | None = None
    raw: dict | None = None
