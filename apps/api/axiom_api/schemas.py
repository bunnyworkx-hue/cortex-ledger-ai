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


class PendingApprovalOut(BaseModel):
    approval_id: str
    status: str
    reason: str


class ApprovalOut(BaseModel):
    id: str
    action: str
    risk_level: str
    reason: str
    payload: dict
    status: str
    created_at: str
    decided_at: str | None
    decided_by: str | None


class DecideApprovalRequest(BaseModel):
    decided_by: str


class SaveMemoryRequest(BaseModel):
    scope: str = Field(pattern="^(task|working|long_term|business_knowledge)$")
    owner_id: str
    content: str
    source: str
    tenant_id: str | None = None
    permissions: list[str] = []
    retention_days: int | None = None


class MemoryRecordOut(BaseModel):
    id: str
    scope: str
    owner_id: str
    tenant_id: str | None
    content: str
    source: str
    permissions: list[str]
    retention_days: int | None
    created_at: str


class ExecutionTraceOut(BaseModel):
    execution_id: str
    agent_id: str
    backend_name: str
    status: str
    input: str
    output: str | None
    error: str | None
    raw: dict
    started_at: str
    completed_at: str | None
    duration_ms: float | None


class ObservabilityMetricsOut(BaseModel):
    total_executions: int
    succeeded: int
    failed: int
    success_rate: float | None
    avg_duration_ms: float | None
    top_agents_by_execution_count: dict[str, int]
