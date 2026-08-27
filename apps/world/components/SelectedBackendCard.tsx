"use client";

import type { SelectedBackend } from "./ExecutionZone";

// Same real-interactivity pattern as SelectedAgentCard/SelectedNodeCard,
// closing the one zone that hadn't gotten it yet. No live action here —
// unlike agents (real delegate call) and graph nodes (real get_neighbors
// call), there's no per-backend endpoint to call; /v1/models, /v1/agents,
// and /v1/knowledge only ever return the aggregate name→status map this
// card is already built from, so this stays informational rather than
// inventing an action that doesn't exist.
export function SelectedBackendCard({ backend, onClose }: { backend: SelectedBackend; onClose: () => void }) {
  return (
    <div className="selected-backend">
      <div className="selected-backend-head">
        <div>
          <div className="selected-backend-name">{backend.name}</div>
          <div className="selected-backend-meta">{backend.group}</div>
        </div>
        <button className="selected-backend-close" onClick={onClose} aria-label="Close">
          ×
        </button>
      </div>
      <div className={`selected-backend-status ${backend.status === "configured" ? "selected-backend-status-ok" : ""}`}>
        {backend.status}
      </div>
      {backend.isHermes && (
        <div className="selected-backend-note">
          External agent runtime (packages/axiom-hermes) — routed through Cortex Ledger AI&rsquo;s own agent
          gateway rather than given direct access. Cortex Ledger AI controls access, not Hermes.
        </div>
      )}
    </div>
  );
}
