"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type ToolDefinition } from "@/lib/api";
import { StatusPill } from "../components/StatusPill";

export default function Tools() {
  const [tools, setTools] = useState<ToolDefinition[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listTools()
      .then(setTools)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load tools"));
  }, []);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Tool Registry</h1>
        <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
          Every tool Cortex Ledger AI has discovered or registered — auto-discovered MCP servers and native
          tools alike.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
          {error}
        </div>
      )}

      <div className="overflow-hidden rounded-lg border border-zinc-200 dark:border-zinc-800">
        <table className="w-full text-sm">
          <thead className="bg-zinc-100 text-left text-xs uppercase tracking-wide text-zinc-500 dark:bg-zinc-900 dark:text-zinc-400">
            <tr>
              <th className="px-4 py-2 font-medium">Name</th>
              <th className="px-4 py-2 font-medium">Source</th>
              <th className="px-4 py-2 font-medium">Risk</th>
              <th className="px-4 py-2 font-medium">Description</th>
            </tr>
          </thead>
          <tbody>
            {tools?.map((tool) => (
              <tr key={tool.name} className="border-t border-zinc-100 dark:border-zinc-800">
                <td className="px-4 py-2 font-mono text-xs">{tool.name}</td>
                <td className="px-4 py-2 text-zinc-500">{tool.source}</td>
                <td className="px-4 py-2">
                  <StatusPill value={tool.risk_level} />
                </td>
                <td className="px-4 py-2 text-zinc-600 dark:text-zinc-300">{tool.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
