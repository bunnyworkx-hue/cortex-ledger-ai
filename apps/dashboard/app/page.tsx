"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type ObservabilityMetrics } from "@/lib/api";
import { StatusPill } from "./components/StatusPill";

type Row = { label: string; value: string; detail?: string };

export default function Overview() {
  const [rows, setRows] = useState<Row[] | null>(null);
  const [metrics, setMetrics] = useState<ObservabilityMetrics | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const [health, models, knowledge, agents, fabric, tools] = await Promise.all([
          api.health(),
          api.modelBackends(),
          api.knowledgeBackends(),
          api.agentBackends(),
          api.agentFabricStatus(),
          api.listTools(),
        ]);
        if (cancelled) return;

        const backendRow = (name: string, backends: Record<string, string>) =>
          Object.entries(backends).length
            ? Object.entries(backends)
                .map(([k, v]) => `${k}: ${v}`)
                .join(", ")
            : "none registered";

        setRows([
          { label: "API", value: health.status, detail: `${health.environment} · ${health.service}` },
          { label: "Database", value: health.database },
          { label: "Model Gateway", value: backendRow("models", models.backends) },
          { label: "Knowledge Gateway", value: backendRow("knowledge", knowledge.backends) },
          { label: "Agent Backends", value: backendRow("agents", agents.backends) },
          {
            label: "Agent Fabric",
            value: fabric.configured ? "configured" : "not_configured",
            detail: fabric.configured
              ? `${fabric.total_agents} agents (${fabric.curated_agents} curated)`
              : undefined,
          },
          { label: "Tool Registry", value: `${tools.length} tools` },
        ]);

        try {
          setMetrics(await api.metrics());
        } catch {
          // execution store may not be configured — leave metrics null
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof ApiError ? err.message : "Failed to reach the Axiom API");
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Overview</h1>
        <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
          Live status of every Axiom OS subsystem, read directly from the running API.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
          {error} — the dashboard proxies API calls through{" "}
          <code>{process.env.NEXT_PUBLIC_API_URL ?? "/api"}</code>; check that{" "}
          <code>./scripts/dev/run.sh</code> is running (default{" "}
          <code>http://127.0.0.1:8000</code>).
        </div>
      )}

      {rows && (
        <div className="overflow-hidden rounded-lg border border-zinc-200 dark:border-zinc-800">
          <table className="w-full text-sm">
            <tbody>
              {rows.map((row) => (
                <tr key={row.label} className="border-b border-zinc-100 last:border-0 dark:border-zinc-800">
                  <td className="w-48 px-4 py-3 font-medium text-zinc-600 dark:text-zinc-400">{row.label}</td>
                  <td className="px-4 py-3">
                    <StatusPill value={row.value} />
                    {row.detail && (
                      <span className="ml-2 text-zinc-500 dark:text-zinc-400">{row.detail}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {metrics && (
        <div>
          <h2 className="mb-3 text-lg font-semibold tracking-tight">Execution Metrics</h2>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <MetricCard label="Total Executions" value={metrics.total_executions} />
            <MetricCard
              label="Success Rate"
              value={metrics.success_rate !== null ? `${Math.round(metrics.success_rate * 100)}%` : "—"}
            />
            <MetricCard
              label="Avg Duration"
              value={metrics.avg_duration_ms !== null ? `${Math.round(metrics.avg_duration_ms)}ms` : "—"}
            />
            <MetricCard label="Failed" value={metrics.failed} />
          </div>
        </div>
      )}
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
      <div className="text-xs font-medium uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
        {label}
      </div>
      <div className="mt-1 text-2xl font-semibold tracking-tight">{value}</div>
    </div>
  );
}
