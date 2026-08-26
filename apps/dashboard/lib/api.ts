// Same-origin by default (proxied server-side to the real API by the
// rewrite in next.config.ts) — see that file's comment for why. Set
// NEXT_PUBLIC_API_URL to bypass the proxy and call the API directly
// cross-origin instead, if that's ever actually preferred.
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "/api";

export class ApiError extends Error {
  status: number;
  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "content-type": "application/json", ...(init?.headers ?? {}) },
    cache: "no-store",
  });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail ?? detail;
    } catch {
      // response wasn't JSON — keep statusText
    }
    throw new ApiError(response.status, detail);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export type BackendStatus = { backends: Record<string, string> };
export type KnowledgeStatus = { backends: Record<string, string> };
export type AgentFabricStatus = {
  configured: boolean;
  total_agents: number;
  curated_agents: number;
  by_division?: Record<string, number>;
};
export type HealthStatus = { status: string; service: string; environment: string; database: string };

export type AgentRecord = {
  agent_id: string;
  name: string;
  description: string;
  division: string;
  category: string;
  status: string;
  is_curated: boolean;
  capabilities: string[] | null;
  permissions: string[] | null;
  risk_level: string | null;
  frontmatter_tools: string[];
};

export type ExecutionOut = {
  execution_id: string;
  agent_id: string;
  backend_name: string;
  status: string;
  content: string | null;
};

export type ExecutionTrace = {
  execution_id: string;
  agent_id: string;
  backend_name: string;
  status: string;
  input: string;
  output: string | null;
  error: string | null;
  raw: Record<string, unknown>;
  started_at: string;
  completed_at: string | null;
  duration_ms: number | null;
};

export type ObservabilityMetrics = {
  total_executions: number;
  succeeded: number;
  failed: number;
  success_rate: number | null;
  avg_duration_ms: number | null;
  top_agents_by_execution_count: Record<string, number>;
};

export type ToolDefinition = {
  name: string;
  description: string;
  input_schema: Record<string, unknown>;
  source: string;
  permissions: string[];
  risk_level: string;
};

export type Approval = {
  id: string;
  action: string;
  risk_level: string;
  reason: string;
  payload: Record<string, unknown>;
  status: string;
  created_at: string;
  decided_at: string | null;
  decided_by: string | null;
};

export const api = {
  health: () => request<HealthStatus>("/health"),
  modelBackends: () => request<BackendStatus>("/v1/models"),
  knowledgeBackends: () => request<KnowledgeStatus>("/v1/knowledge"),
  agentBackends: () => request<BackendStatus>("/v1/agents"),
  agentFabricStatus: () => request<AgentFabricStatus>("/v1/agent-fabric"),
  searchAgents: (q: string, division?: string) =>
    request<AgentRecord[]>(
      `/v1/agent-fabric/search?q=${encodeURIComponent(q)}${division ? `&division=${encodeURIComponent(division)}` : ""}`
    ),
  delegate: (agentId: string, input: string, backend?: string) =>
    request<ExecutionOut>(`/v1/agent-fabric/agents/${agentId}/delegate`, {
      method: "POST",
      body: JSON.stringify({ input, backend }),
    }),
  listExecutions: (limit = 20) => request<ExecutionTrace[]>(`/v1/observability/executions?limit=${limit}`),
  metrics: () => request<ObservabilityMetrics>("/v1/observability/metrics"),
  listTools: () => request<ToolDefinition[]>("/v1/tools"),
  listApprovals: () => request<Approval[]>("/v1/approvals"),
  decideApproval: (id: string, action: "approve" | "reject", decidedBy: string) =>
    request(`/v1/approvals/${id}/${action}`, {
      method: "POST",
      body: JSON.stringify({ decided_by: decidedBy }),
    }),
};
