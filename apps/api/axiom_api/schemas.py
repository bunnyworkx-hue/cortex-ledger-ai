from pydantic import BaseModel, Field


class MessageIn(BaseModel):
    role: str = Field(pattern="^(system|user|assistant)$")
    content: str


class CompletionRequest(BaseModel):
    messages: list[MessageIn]
    model: str | None = None
    max_tokens: int = 1024
    temperature: float | None = None
    system: str | None = None


class UsageOut(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int


class CompletionResponse(BaseModel):
    content: str
    model: str
    provider: str
    usage: UsageOut
    stop_reason: str | None


class KnowledgeAnswerOut(BaseModel):
    text: str
