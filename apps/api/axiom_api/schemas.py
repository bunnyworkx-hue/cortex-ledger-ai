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


class ExecuteAgentRequest(BaseModel):
    agent_id: str
    agent_name: str
    instructions: str
    input: str
    context: str | None = None
    backend: str | None = None


class ExecutionOut(BaseModel):
    execution_id: str
    agent_id: str
    backend_name: str
    status: str
    content: str | None


class AgentRecordOut(BaseModel):
    agent_id: str
    name: str
    description: str
    division: str
    category: str
    status: str
    is_curated: bool
    capabilities: list[str] | None
    permissions: list[str] | None
    risk_level: str | None
    frontmatter_tools: list[str]


class AgentRecordDetailOut(AgentRecordOut):
    instructions: str
    source_path: str
    source_commit: str


class DelegateRequest(BaseModel):
    input: str
    context: str | None = None
    backend: str | None = None


class ToolDefinitionOut(BaseModel):
    name: str
    description: str
    input_schema: dict
    source: str
    permissions: list[str]
    risk_level: str


class ToolCallRequest(BaseModel):
    arguments: dict = {}


class ToolCallResultOut(BaseModel):
    content: dict
    is_error: bool
