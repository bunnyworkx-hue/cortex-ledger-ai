"use client";

import { useCallback, useEffect, useState } from "react";
import { api, ApiError, type Approval } from "@/lib/api";
import { StatusPill } from "../components/StatusPill";

export default function Approvals() {
  const [approvals, setApprovals] = useState<Approval[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  const load = useCallback(() => {
    api
      .listApprovals()
      .then(setApprovals)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load approvals"));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function decide(id: string, action: "approve" | "reject") {
    setBusyId(id);
    setError(null);
    try {
      // Decided by the operator viewing this dashboard — a real human
      // approving a real pending high-risk action, per CLAUDE.md §37.
      await api.decideApproval(id, action, "dashboard-operator");
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Decision failed");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Approvals</h1>
        <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
          High-risk actions the Policy Engine held for human review. Approving here executes the
          original action for real.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
          {error}
        </div>
      )}

      {approvals?.length === 0 && (
        <p className="text-sm text-zinc-500">No pending approvals right now.</p>
      )}

      <div className="flex flex-col gap-3">
        {approvals?.map((approval) => (
          <div key={approval.id} className="rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-medium">{approval.action}</span>
                <StatusPill value={approval.risk_level} />
                <StatusPill value={approval.status} />
              </div>
              <span className="text-xs text-zinc-500">
                {new Date(approval.created_at).toLocaleString()}
              </span>
            </div>
            <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-300">{approval.reason}</p>
            <pre className="mt-2 overflow-x-auto rounded-md bg-zinc-100 p-2 text-xs dark:bg-zinc-900">
              {JSON.stringify(approval.payload, null, 2)}
            </pre>
            {approval.status === "pending" ? (
              <div className="mt-3 flex gap-2">
                <button
                  onClick={() => decide(approval.id, "approve")}
                  disabled={busyId === approval.id}
                  className="rounded-md bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-50"
                >
                  Approve
                </button>
                <button
                  onClick={() => decide(approval.id, "reject")}
                  disabled={busyId === approval.id}
                  className="rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-50"
                >
                  Reject
                </button>
              </div>
            ) : (
              <p className="mt-3 text-xs text-zinc-500">
                Decided by {approval.decided_by} at{" "}
                {approval.decided_at && new Date(approval.decided_at).toLocaleString()}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
