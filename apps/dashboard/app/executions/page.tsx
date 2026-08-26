"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type ExecutionTrace } from "@/lib/api";
import { StatusPill } from "../components/StatusPill";

export default function Executions() {
  const [executions, setExecutions] = useState<ExecutionTrace[] | null>(null);
  const [selected, setSelected] = useState<ExecutionTrace | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listExecutions(30)
      .then(setExecutions)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load executions"));
  }, []);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Execution Trace</h1>
        <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
          Every Task → Backend → Result run recorded by Axiom, success or failure.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
          {error}
        </div>
      )}

      {executions?.length === 0 && <p className="text-sm text-zinc-500">No executions recorded yet.</p>}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="flex flex-col gap-2">
          {executions?.map((exec) => (
            <button
              key={exec.execution_id}
              onClick={() => setSelected(exec)}
              className={`rounded-lg border p-3 text-left transition-colors ${
                selected?.execution_id === exec.execution_id
                  ? "border-zinc-900 dark:border-zinc-50"
                  : "border-zinc-200 hover:border-zinc-400 dark:border-zinc-800 dark:hover:border-zinc-600"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-medium">{exec.agent_id}</span>
                <StatusPill value={exec.status} />
              </div>
              <div className="mt-1 flex items-center gap-2 text-xs text-zinc-500 dark:text-zinc-400">
                <span>{exec.backend_name}</span>
                {exec.duration_ms !== null && <span>· {Math.round(exec.duration_ms)}ms</span>}
                <span>· {new Date(exec.started_at).toLocaleTimeString()}</span>
              </div>
              <p className="mt-2 truncate text-sm text-zinc-600 dark:text-zinc-300">{exec.input}</p>
            </button>
          ))}
        </div>

        <div>
          {selected ? (
            <div className="rounded-lg border border-zinc-200 p-4 text-sm dark:border-zinc-800">
              <div className="mb-3 flex items-center gap-2">
                <StatusPill value={selected.status} />
                <span className="font-mono text-xs text-zinc-500">{selected.execution_id}</span>
              </div>
              <Field label="Agent" value={selected.agent_id} />
              <Field label="Backend" value={selected.backend_name} />
              <Field label="Input" value={selected.input} />
              {selected.output && <Field label="Output" value={selected.output} />}
              {selected.error && <Field label="Error" value={selected.error} />}
              <Field label="Duration" value={selected.duration_ms ? `${Math.round(selected.duration_ms)}ms` : "—"} />
              {Object.keys(selected.raw).length > 0 && (
                <div className="mt-3">
                  <div className="mb-1 text-xs font-medium uppercase tracking-wide text-zinc-500">
                    Raw usage
                  </div>
                  <pre className="overflow-x-auto rounded-md bg-zinc-100 p-2 text-xs dark:bg-zinc-900">
                    {JSON.stringify(selected.raw, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ) : (
            <p className="text-sm text-zinc-500">Select an execution to see its full trace.</p>
          )}
        </div>
      </div>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="mb-3">
      <div className="mb-0.5 text-xs font-medium uppercase tracking-wide text-zinc-500">{label}</div>
      <div className="whitespace-pre-wrap">{value}</div>
    </div>
  );
}
