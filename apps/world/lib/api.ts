// Same-origin by default, proxied server-side by next.config.ts — see
// apps/dashboard/lib/api.ts for the full reasoning (the same fix that
// resolved a real cross-origin fetch failure there).
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
      // not JSON — keep statusText
    }
    throw new ApiError(response.status, detail);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export type AgentFabricStatus = {
  configured: boolean;
  total_agents: number;
  curated_agents: number;
  by_division: Record<string, number>;
};

export type AgentRecord = {
  agent_id: string;
  name: string;
  description: string;
  division: string;
  category: string;
  status: string;
  is_curated: boolean;
  risk_level: string | null;
};

export type BackendStatus = { backends: Record<string, string> };

export type DelegateResult = {
  execution_id: string;
  agent_id: string;
  backend_name: string;
  status: string;
  content: string | null;
};

export const api = {
  health: () => request<{ status: string; database: string }>("/health"),
  agentFabricStatus: () => request<AgentFabricStatus>("/v1/agent-fabric"),
  // The full real roster (all 254, each with a real addressable
  // agent_id) — unlike agentFabricStatus's aggregate-only counts, this
  // is what lets the 3D scene give individual real identity to
  // individual rendered points instead of anonymous dots.
  listAgents: () => request<AgentRecord[]>("/v1/agent-fabric/agents"),
  agentFabricSearch: (q: string) =>
    request<AgentRecord[]>(`/v1/agent-fabric/search?q=${encodeURIComponent(q)}&limit=6`),
  modelBackends: () => request<BackendStatus>("/v1/models"),
  agentBackends: () => request<BackendStatus>("/v1/agents"),
  knowledgeBackends: () => request<BackendStatus>("/v1/knowledge"),
  delegate: (agentId: string, input: string) =>
    request<DelegateResult>(`/v1/agent-fabric/agents/${agentId}/delegate`, {
      method: "POST",
      body: JSON.stringify({ input }),
    }),
};
