"use client";

import { useState } from "react";
import { api, ApiError, type AgentRecord, type ExecutionOut } from "@/lib/api";
import { StatusPill } from "../components/StatusPill";

export default function AgentFabric() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<AgentRecord[] | null>(null);
  const [selected, setSelected] = useState<AgentRecord | null>(null);
  const [taskInput, setTaskInput] = useState("");
  const [backend, setBackend] = useState("axiom_native");
  const [execution, setExecution] = useState<ExecutionOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [delegating, setDelegating] = useState(false);

  async function runSearch(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      setResults(await api.searchAgents(query || "strategy"));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }

  async function runDelegate(e: React.FormEvent) {
    e.preventDefault();
    if (!selected || !taskInput.trim()) return;
    setError(null);
    setExecution(null);
    setDelegating(true);
    try {
      setExecution(await api.delegate(selected.agent_id, taskInput, backend));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Delegation failed");
    } finally {
      setDelegating(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Agent Fabric</h1>
        <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
          Search the curated agent cohort and delegate a real task to any of them.
        </p>
      </div>

      <form onSubmit={runSearch} className="flex gap-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. security threat modeling"
          className="flex-1 rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-900"
        >
          {loading ? "Searching…" : "Search"}
        </button>
      </form>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div className="flex flex-col gap-2">
          {results?.length === 0 && (
            <p className="text-sm text-zinc-500">No curated agents matched — try a different query.</p>
          )}
          {results?.map((agent) => (
            <button
              key={agent.agent_id}
              onClick={() => {
                setSelected(agent);
                setExecution(null);
              }}
              className={`rounded-lg border p-3 text-left transition-colors ${
                selected?.agent_id === agent.agent_id
                  ? "border-zinc-900 dark:border-zinc-50"
                  : "border-zinc-200 hover:border-zinc-400 dark:border-zinc-800 dark:hover:border-zinc-600"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-medium">{agent.name}</span>
                {agent.risk_level && <StatusPill value={agent.risk_level} />}
              </div>
              <div className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">{agent.agent_id}</div>
              <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-300">{agent.description}</p>
              {agent.capabilities && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {agent.capabilities.map((c) => (
                    <span
                      key={c}
                      className="rounded bg-zinc-100 px-1.5 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300"
                    >
                      {c}
                    </span>
                  ))}
                </div>
              )}
            </button>
          ))}
        </div>

        <div>
          {selected ? (
            <form onSubmit={runDelegate} className="flex flex-col gap-3 rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
              <div className="text-sm font-medium">
                Delegate to <span className="font-semibold">{selected.name}</span>
              </div>
              <textarea
                value={taskInput}
                onChange={(e) => setTaskInput(e.target.value)}
                placeholder="Ask this agent something…"
                rows={3}
                className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
              />
              <select
                value={backend}
                onChange={(e) => setBackend(e.target.value)}
                className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
              >
                <option value="axiom_native">axiom_native</option>
                <option value="hermes">hermes</option>
              </select>
              <button
                type="submit"
                disabled={delegating || !taskInput.trim()}
                className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-900"
              >
                {delegating ? "Running…" : "Delegate"}
              </button>

              {execution && (
                <div className="mt-2 rounded-md border border-zinc-200 bg-zinc-50 p-3 text-sm dark:border-zinc-800 dark:bg-zinc-900">
                  <div className="mb-2 flex items-center gap-2">
                    <StatusPill value={execution.status} />
                    <span className="text-xs text-zinc-500">{execution.backend_name}</span>
                  </div>
                  <p className="whitespace-pre-wrap">{execution.content}</p>
                </div>
              )}
            </form>
          ) : (
            <p className="text-sm text-zinc-500">Select an agent from the search results to delegate a task.</p>
          )}
        </div>
      </div>
    </div>
  );
}
