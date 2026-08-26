"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type Approval } from "@/lib/api";

// CLAUDE.md §64's Sixth Demo, live inside the world: real high-risk
// actions genuinely stop and wait for a human here — nothing in this
// panel is simulated. "Propose test action" hits the real
// modify_business_record tool (the same demo mutating tool the rest of
// Axiom OS uses to prove the gate), which the Policy Engine really does
// refuse to run until Approve is clicked below, which really does call
// POST /v1/approvals/{id}/approve and only then executes it.
export function ApprovalStation() {
  const [open, setOpen] = useState(false);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [busyIds, setBusyIds] = useState<Set<string>>(new Set());
  const [proposing, setProposing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastAction, setLastAction] = useState<string | null>(null);

  async function refresh() {
    try {
      const list = await api.listApprovals();
      setApprovals(list);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not reach the Axiom API");
    }
  }

  useEffect(() => {
    if (!open) return;
    let cancelled = false;

    async function poll() {
      try {
        const list = await api.listApprovals();
        if (!cancelled) {
          setApprovals(list);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof ApiError ? err.message : "Could not reach the Axiom API");
      }
    }

    poll();
    const id = setInterval(poll, 6000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [open]);

  async function proposeDemoAction() {
    setProposing(true);
    setLastAction(null);
    try {
      const recordId = `world-demo-${Date.now()}`;
      const result = await api.proposeDemoAction(recordId, "reviewed-in-axiom-world");
      if ("approval_id" in result) {
        setLastAction(`Proposed ${recordId} — pending approval below (risk: high, gated by real policy).`);
        await refresh();
      } else {
        // Shouldn't happen for this demo tool (it's always high-risk),
        // but handle honestly rather than assume.
        setLastAction(`Executed immediately: ${JSON.stringify(result.content)}`);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not reach the Axiom API");
    } finally {
      setProposing(false);
    }
  }

  async function decide(approval: Approval, approved: boolean) {
    setBusyIds((prev) => new Set(prev).add(approval.id));
    try {
      if (approved) {
        const result = await api.approve(approval.id, "axiom-world-operator");
        setLastAction(`Approved and executed: ${JSON.stringify(result.content)}`);
      } else {
        await api.reject(approval.id, "axiom-world-operator");
        setLastAction(`Rejected ${approval.id} — never executed.`);
      }
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not reach the Axiom API");
    } finally {
      setBusyIds((prev) => {
        const next = new Set(prev);
        next.delete(approval.id);
        return next;
      });
    }
  }

  return (
    <div className="approval-station">
      <button className="approval-toggle" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
        Human Approval {approvals.length > 0 ? `(${approvals.length})` : ""}
      </button>

      {open && (
        <div className="approval-panel">
          <div className="approval-panel-head">
            <span>Real pending approvals — nothing here executes without a click.</span>
            <button onClick={proposeDemoAction} disabled={proposing}>
              {proposing ? "Proposing…" : "Propose test action"}
            </button>
          </div>

          {error && <div className="approval-error">{error}</div>}
          {lastAction && <div className="approval-last">{lastAction}</div>}

          {approvals.length === 0 ? (
            <div className="approval-empty">No pending approvals right now.</div>
          ) : (
            <div className="approval-list">
              {approvals.map((approval) => (
                <div key={approval.id} className="approval-card">
                  <div className="approval-card-head">
                    <span className="approval-action">{approval.action}</span>
                    <span className={`approval-risk approval-risk-${approval.risk_level}`}>{approval.risk_level}</span>
                  </div>
                  <div className="approval-reason">{approval.reason}</div>
                  <div className="approval-buttons">
                    <button
                      className="approval-approve"
                      disabled={busyIds.has(approval.id)}
                      onClick={() => decide(approval, true)}
                    >
                      Approve
                    </button>
                    <button
                      className="approval-reject"
                      disabled={busyIds.has(approval.id)}
                      onClick={() => decide(approval, false)}
                    >
                      Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
